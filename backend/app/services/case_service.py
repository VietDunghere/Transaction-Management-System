from __future__ import annotations
"""
Service: CaseService
Xử lý business logic cho manual review cases.
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
from app.models.case import ReviewCase, ReviewCaseAction
from app.models.scoring import AuditLog
from app.models.transaction import Transaction, TxnState, TxnStateHistory
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

    def list_cases(
        self,
        case_status=None,
        assigned_to=None,
        reviewer_queue_for=None,
        created_from=None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ReviewCase], int]:
        """Danh sách cases với filter và pagination."""
        return self._case_repo.list_cases(
            case_status=case_status,
            assigned_to=assigned_to,
            reviewer_queue_for=reviewer_queue_for,
            created_from=created_from,
            page=page,
            page_size=page_size,
        )

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

        # Case phải ở trạng thái ASSIGNED trước khi có thể quyết định.
        # MANAGER và ADMIN có thể override nhưng case vẫn phải qua bước assign
        # để đảm bảo audit trail đầy đủ.
        if case.case_status == CaseStatus.OPEN.value:
            raise ConflictError(
                "Case chưa được nhận (status = OPEN). "
                "Hãy assign case trước khi đưa ra quyết định."
            )

        # REVIEWER chỉ quyết định được case được giao cho mình.
        # MANAGER và ADMIN có thể quyết định bất kỳ case nào (override/giám sát).
        is_privileged = "MANAGER" in actor_roles or "ADMIN" in actor_roles
        if not is_privileged and case.assigned_to != actor_user_id:
            raise PermissionDeniedError("Case này không được giao cho bạn.")

        # SoD: người submit giao dịch không được tự review (4-eyes principle).
        # MANAGER được phép override để xử lý trường hợp khẩn.
        if not is_privileged:
            txn = self._db.query(Transaction).filter(Transaction.txn_id == case.txn_id).first()
            if txn and txn.submitted_by == actor_user_id:
                raise PermissionDeniedError(
                    "Vi phạm nguyên tắc 4 mắt (SoD): không thể review giao dịch do chính mình tạo."
                )

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
        event_type = "CASE_APPROVED" if request.decision.value == "APPROVE" else "CASE_REJECTED"
        self._write_audit(case_id, actor_user_id, event_type, {
            "decision": request.decision.value,
            "note": request.decision_note,
        })

        # Sync Transaction and TxnState to final status
        txn_new_status = "APPROVED" if request.decision.value == "APPROVE" else "REJECTED"
        self._db.query(Transaction).filter(Transaction.txn_id == case.txn_id).update(
            {"status": txn_new_status}, synchronize_session="fetch"
        )
        self._db.query(TxnState).filter(TxnState.txn_id == case.txn_id).update(
            {"status": txn_new_status}, synchronize_session="fetch"
        )
        self._db.add(TxnStateHistory(
            state_hist_id=str(uuid.uuid4()),
            txn_id=case.txn_id,
            old_status="MANUAL_REVIEW",
            new_status=txn_new_status,
            changed_by_user_id=actor_user_id,
            change_reason=f"Case {case_id} decided: {request.decision.value}",
        ))
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
