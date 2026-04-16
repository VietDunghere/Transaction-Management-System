from __future__ import annotations
from typing import Optional, List, Dict, Any
"""
Service: CaseService
Xử lý business logic cho manual review cases.
"""

import json
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import (
    CaseAlreadyDecidedError,
    ConflictError,
    NotFoundError,
    OptimisticLockError,
    PermissionDeniedError,
)
from app.core.logging import get_logger
from app.models.case import ReviewCase, ReviewCaseAction
from app.models.scoring import AuditLog
from app.repositories.case_repo import CaseRepository
from app.schemas.case import CaseDecideRequest
from app.schemas.common import CaseStatus

logger = get_logger(__name__)

# Trạng thái cuối — không thể thay đổi
TERMINAL_STATUSES = {CaseStatus.APPROVED, CaseStatus.REJECTED, CaseStatus.CLOSED}


class CaseService:
    """Xử lý business logic cho REVIEWER/MANAGER."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._case_repo = CaseRepository(db)

    def get_case(self, case_id: str) -> ReviewCase:
        """Lấy chi tiết case kèm transaction và actions."""
        case = self._case_repo.get_by_id(case_id)
        if case is None:
            raise NotFoundError("Case")
        return case

    def list_cases(self, **kwargs) -> tuple[list[ReviewCase], int]:
        """Danh sách cases với filter và pagination."""
        return self._case_repo.list_cases(**kwargs)

    def self_assign(self, case_id: str, reviewer_user_id: str) -> ReviewCase:
        """
        REVIEWER tự nhận case về xử lý.
        Dùng WHERE assigned_to IS NULL để chặn race condition
        (Transaction Locking — chỉ 1 reviewer nhận được).

        Raises:
            NotFoundError, ConflictError (nếu đã có người nhận)
        """
        case = self._get_open_case(case_id)

        if case.assigned_to is not None:
            raise ConflictError("Case này đã được nhận bởi reviewer khác.")

        # Atomic update with WHERE assigned_to IS NULL
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

        # Ghi action log
        action = ReviewCaseAction(
            action_id=str(uuid.uuid4()),
            case_id=case_id,
            action_type="ASSIGN",
            actor_user_id=reviewer_user_id,
            action_note=f"Self-assigned by {reviewer_user_id}",
        )
        self._db.add(action)
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
        """
        REVIEWER đưa ra quyết định APPROVE/REJECT cho case.

        Raises:
            PermissionDeniedError: nếu case không được assign cho người này
            OptimisticLockError: nếu version không khớp (case đã bị sửa)
        """
        case = self._get_open_case(case_id)

        # Chỉ reviewer được assign mới có thể quyết định (MANAGER bypass được)
        if "MANAGER" not in actor_roles and case.assigned_to != actor_user_id:
            raise PermissionDeniedError("Case này không được giao cho bạn.")

        # Optimistic lock check
        if case.version != request.version:
            raise OptimisticLockError()

        # Cập nhật case
        final_status = CaseStatus.APPROVED if request.decision.value == "APPROVE" else CaseStatus.REJECTED
        case.case_status = final_status.value
        case.decision = request.decision.value
        case.decision_note = request.decision_note
        case.decided_at = datetime.now(timezone.utc)
        case.version += 1  # Tăng version để lock

        # Ghi action log
        action = ReviewCaseAction(
            action_id=str(uuid.uuid4()),
            case_id=case_id,
            action_type=request.decision.value,
            actor_user_id=actor_user_id,
            action_note=request.decision_note,
        )
        self._db.add(action)
        self._write_audit(case_id, actor_user_id, f"CASE_{request.decision.value}D", {
            "decision": request.decision.value,
            "note": request.decision_note,
        })
        self._db.commit()

        logger.info(
            "case_decided",
            case_id=case_id,
            decision=request.decision.value,
            actor=actor_user_id,
        )
        return self._case_repo.get_by_id(case_id)

    # ---- Private ----

    def _get_open_case(self, case_id: str) -> ReviewCase:
        """Load case và kiểm tra không ở trạng thái cuối."""
        case = self._case_repo.get_by_id(case_id)
        if case is None:
            raise NotFoundError("Case")
        if case.case_status in {s.value for s in TERMINAL_STATUSES}:
            raise CaseAlreadyDecidedError()
        return case

    def _write_audit(self, entity_id: str, actor: str, event_type: str, detail: dict) -> None:
        audit = AuditLog(
            log_id=str(uuid.uuid4()),
            event_type=event_type,
            entity_type="ReviewCase",
            entity_id=entity_id,
            actor_user_id=actor,
            detail_json=json.dumps(detail),
        )
        self._db.add(audit)
