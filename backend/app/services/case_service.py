from __future__ import annotations
"""
Service: CaseService (ERD v2)
Simplified: no ReviewCaseAction, TxnState, TxnStateHistory.
case_status: OPEN → ASSIGNED → CLOSED. Decision stored in decision column.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import List

from sqlalchemy.orm import Session

from app.core.exceptions import (
    CaseAlreadyDecidedError,
    ConflictError,
    NotFoundError,
    OptimisticLockError,
    PermissionDeniedError,
)
from app.core.logging import get_logger
from app.models.case import ReviewCase
from app.models.scoring import AuditLog
from app.models.transaction import Transaction
from app.repositories.case_repo import CaseRepository
from app.schemas.case import CaseDecideRequest
from app.schemas.common import CaseStatus

logger = get_logger(__name__)


class CaseService:

    def __init__(self, db: Session) -> None:
        self._db = db
        self._case_repo = CaseRepository(db)

    def get_case(self, case_id: str) -> ReviewCase:
        case = self._case_repo.get_by_id(case_id)
        if case is None:
            raise NotFoundError("Case")
        return case

    def list_cases(
        self,
        case_status=None,
        assigned_to=None,
        reviewer_queue_for=None,
        created_from=None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ReviewCase], int]:
        return self._case_repo.list_cases(
            case_status=case_status,
            assigned_to=assigned_to,
            reviewer_queue_for=reviewer_queue_for,
            created_from=created_from,
            page=page,
            page_size=page_size,
        )

    def self_assign(self, case_id: str, reviewer_user_id: str) -> ReviewCase:
        case = self._get_open_case(case_id)

        if case.assigned_to is not None:
            raise ConflictError("Case này đã được nhận bởi reviewer khác.")

        rows_updated = (
            self._db.query(ReviewCase)
            .filter(
                ReviewCase.case_id == case_id,
                ReviewCase.assigned_to.is_(None),
            )
            .update(
                {
                    "assigned_to": reviewer_user_id,
                    "case_status": CaseStatus.ASSIGNED.value,
                },
                synchronize_session="fetch",
            )
        )

        if rows_updated == 0:
            raise ConflictError("Case này đã được nhận bởi reviewer khác.")

        self._write_audit(case_id, reviewer_user_id, "CASE_ASSIGNED", {
            "assigned_to": reviewer_user_id,
        })
        self._db.commit()

        logger.info("case_self_assigned", case_id=case_id, reviewer=reviewer_user_id)
        return self._case_repo.get_by_id(case_id)

    def decide(
        self,
        case_id: str,
        request: CaseDecideRequest,
        actor_user_id: str,
        actor_roles: List[str],
    ) -> ReviewCase:
        case = self._get_open_case(case_id)

        if case.case_status == CaseStatus.OPEN.value:
            raise ConflictError(
                "Case chưa được nhận (status = OPEN). "
                "Hãy assign case trước khi đưa ra quyết định."
            )

        is_privileged = "MANAGER" in actor_roles or "ADMIN" in actor_roles
        if not is_privileged and case.assigned_to != actor_user_id:
            raise PermissionDeniedError("Case này không được giao cho bạn.")

        if not is_privileged:
            txn = self._db.query(Transaction).filter(Transaction.txn_id == case.txn_id).first()
            if txn and txn.submitted_by == actor_user_id:
                raise PermissionDeniedError(
                    "Vi phạm nguyên tắc 4 mắt (SoD): không thể review giao dịch do chính mình tạo."
                )

        if case.version != request.version:
            raise OptimisticLockError()

        # ERD v2: case_status → CLOSED, decision stores APPROVE/REJECT
        case.case_status = CaseStatus.CLOSED.value
        case.decision = request.decision.value
        case.decision_note = request.decision_note
        case.decided_at = datetime.now(timezone.utc)
        case.version += 1

        event_type = "CASE_APPROVED" if request.decision.value == "APPROVE" else "CASE_REJECTED"
        self._write_audit(case_id, actor_user_id, event_type, {
            "decision": request.decision.value,
            "note": request.decision_note,
        })

        # Update transaction status
        txn_new_status = "APPROVED" if request.decision.value == "APPROVE" else "REJECTED"
        self._db.query(Transaction).filter(Transaction.txn_id == case.txn_id).update(
            {"status": txn_new_status}, synchronize_session="fetch"
        )

        self._db.commit()

        logger.info(
            "case_decided",
            case_id=case_id,
            decision=request.decision.value,
            actor=actor_user_id,
        )
        return self._case_repo.get_by_id(case_id)

    def _get_open_case(self, case_id: str) -> ReviewCase:
        case = self._case_repo.get_by_id(case_id)
        if case is None:
            raise NotFoundError("Case")
        if case.case_status == CaseStatus.CLOSED.value:
            raise CaseAlreadyDecidedError()
        return case

    def _write_audit(self, entity_id: str, actor: str, event_type: str, detail: dict) -> None:
        from app.models.user import User
        user = self._db.query(User.full_name).filter(User.user_id == actor).first()
        audit = AuditLog(
            log_id=str(uuid.uuid4()),
            event_type=event_type,
            entity_type="ReviewCase",
            entity_id=entity_id,
            actor_user_id=actor,
            actor_name=user.full_name if user else None,
            detail_json=json.dumps(detail),
        )
        self._db.add(audit)
