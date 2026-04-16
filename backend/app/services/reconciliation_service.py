from __future__ import annotations
"""
Service: ReconciliationService
Đối soát giao dịch — phát hiện PENDING_TIMEOUT, bulk resolve discrepancies.

ReconciliationService.run():
  1. Tạo ReconciliationRun(RUNNING), commit
  2. Đếm tổng giao dịch trong period
  3. Tìm PENDING transactions vượt quá pending_timeout_minutes
  4. Tạo ReconciliationItem(PENDING_TIMEOUT) cho mỗi giao dịch bị kẹt
  5. Cập nhật run → COMPLETED với thống kê
  6. Commit và return

ReconciliationService.resolve():
  Bulk-resolve tất cả items OPEN trong 1 run.
  Yêu cầu run đã COMPLETED (không resolve run đang RUNNING/FAILED).
"""

import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import AppException, ConflictError, NotFoundError
from app.core.logging import get_logger
from app.models.reconciliation import ReconciliationItem, ReconciliationRun
from app.models.transaction import Transaction
from app.repositories.reconciliation_repo import ReconciliationRepository
from app.schemas.reconciliation import ReconciliationRunRequest, ResolveRequest
from fastapi import status as http_status

logger = get_logger(__name__)


def _ensure_aware(dt: datetime) -> datetime:
    """
    Đảm bảo datetime có tzinfo=UTC.
    Nếu naive (không có timezone) → giả sử UTC.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class ReconciliationService:
    """Đối soát giao dịch — ADMIN only."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = ReconciliationRepository(db)

    # ============================================================
    # Run reconciliation
    # ============================================================

    def run(
        self,
        request: ReconciliationRunRequest,
        triggered_by: str,
    ) -> ReconciliationRun:
        """
        Trigger một phiên đối soát mới.

        - Tìm giao dịch PENDING trong period đã vượt quá pending_timeout_minutes.
        - Tạo ReconciliationItem(PENDING_TIMEOUT) cho mỗi giao dịch bị kẹt.
        - Cập nhật run → COMPLETED khi thành công, FAILED khi lỗi.

        Raises:
            AppException(500): Nếu quá trình đối soát thất bại.
        """
        run = ReconciliationRun(
            run_id=str(uuid.uuid4()),
            period_start=request.period_start,
            period_end=request.period_end,
            pending_timeout_minutes=request.pending_timeout_minutes,
            status="RUNNING",
            triggered_by=triggered_by,
        )
        self._repo.create_run(run)
        self._db.commit()

        try:
            self._do_reconciliation(run, request)
            run.status = "COMPLETED"
            run.completed_at = datetime.now(timezone.utc)
            self._db.commit()

            logger.info(
                "reconciliation_completed",
                run_id=run.run_id,
                discrepancy_count=run.discrepancy_count,
                total_txn_count=run.total_txn_count,
            )
        except Exception as exc:
            run.status = "FAILED"
            run.error_message = str(exc)[:500]
            run.completed_at = datetime.now(timezone.utc)
            self._db.commit()
            logger.error("reconciliation_failed", run_id=run.run_id, error=str(exc))
            raise AppException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Reconciliation thất bại: {str(exc)[:200]}",
            )

        return run

    def _do_reconciliation(
        self,
        run: ReconciliationRun,
        request: ReconciliationRunRequest,
    ) -> None:
        """
        Logic đối soát:
          - Đếm tổng giao dịch trong period và số đã xử lý xong (terminal state)
          - Tìm giao dịch PENDING vượt quá timeout → tạo ReconciliationItem
          - Ghi thống kê lên run object (flush trước khi caller commit)
        """
        now = datetime.now(timezone.utc)
        period_start = _ensure_aware(request.period_start)
        period_end = _ensure_aware(request.period_end)
        timeout_cutoff = now - timedelta(minutes=request.pending_timeout_minutes)

        # ---- Tổng số giao dịch trong period ----
        total_count: int = (
            self._db.query(func.count(Transaction.txn_id))
            .filter(
                Transaction.txn_time >= period_start,
                Transaction.txn_time < period_end,
            )
            .scalar()
        ) or 0

        # ---- Số giao dịch đã hoàn thành (terminal state) ----
        matched_count: int = (
            self._db.query(func.count(Transaction.txn_id))
            .filter(
                Transaction.txn_time >= period_start,
                Transaction.txn_time < period_end,
                Transaction.status.in_(["APPROVED", "REJECTED"]),
            )
            .scalar()
        ) or 0

        # ---- Giao dịch PENDING đã vượt quá timeout — discrepancies ----
        stuck_txns: list[Transaction] = (
            self._db.query(Transaction)
            .filter(
                Transaction.txn_time >= period_start,
                Transaction.txn_time < period_end,
                Transaction.status == "PENDING",
                Transaction.txn_time <= timeout_cutoff,
            )
            .all()
        )

        # ---- Tạo ReconciliationItem cho mỗi giao dịch bị kẹt ----
        total_disc_amount = Decimal("0")
        for txn in stuck_txns:
            txn_time_aware = _ensure_aware(txn.txn_time)
            minutes_pending = int((now - txn_time_aware).total_seconds() / 60)

            item = ReconciliationItem(
                item_id=str(uuid.uuid4()),
                run_id=run.run_id,
                txn_id=txn.txn_id,
                item_type="PENDING_TIMEOUT",
                txn_status=txn.status,
                txn_amount=float(txn.amount) if txn.amount is not None else None,
                txn_created_at=txn.txn_time,
                minutes_pending=minutes_pending,
                status="OPEN",
            )
            self._repo.create_item(item)

            if txn.amount is not None:
                total_disc_amount += Decimal(str(txn.amount))

        self._db.flush()

        # ---- Ghi thống kê lên run ----
        run.total_txn_count = total_count
        run.matched_count = matched_count
        run.discrepancy_count = len(stuck_txns)
        run.total_amount = float(total_disc_amount) if stuck_txns else None

    # ============================================================
    # Query
    # ============================================================

    def get_run(self, run_id: str) -> ReconciliationRun:
        """
        Lấy chi tiết một phiên đối soát kèm items (eager-load).

        Raises:
            NotFoundError: Nếu run_id không tồn tại.
        """
        run = self._repo.get_run_by_id(run_id)
        if run is None:
            raise NotFoundError("ReconciliationRun")
        return run

    def list_runs(
        self,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ReconciliationRun], int]:
        return self._repo.list_runs(status=status, page=page, page_size=page_size)

    # ============================================================
    # Resolve
    # ============================================================

    def resolve(
        self,
        run_id: str,
        request: ResolveRequest,
        actor_user_id: str,
    ) -> ReconciliationRun:
        """
        Bulk-resolve tất cả discrepancy items OPEN trong 1 phiên đối soát.

        - Chỉ resolve phiên đã COMPLETED (không cho resolve RUNNING/FAILED).
        - resolution_note bắt buộc để đảm bảo audit trail.
        - Trả về run đã được refresh với items mới nhất.

        Raises:
            NotFoundError:      Phiên không tồn tại.
            AppException(409):  Phiên chưa COMPLETED.
            ConflictError:      Không còn item OPEN nào để resolve.
        """
        run = self._repo.get_run_by_id(run_id)
        if run is None:
            raise NotFoundError("ReconciliationRun")

        if run.status != "COMPLETED":
            raise AppException(
                status_code=http_status.HTTP_409_CONFLICT,
                detail=(
                    f"Chỉ có thể resolve phiên đã COMPLETED. "
                    f"Phiên hiện tại đang ở trạng thái: {run.status}."
                ),
            )

        open_items = self._repo.get_open_items(run_id)
        if not open_items:
            raise ConflictError(
                "Không còn discrepancy nào đang OPEN — phiên đã được resolve hoàn toàn."
            )

        now = datetime.now(timezone.utc)
        for item in open_items:
            item.status = "RESOLVED"
            item.resolution_note = request.resolution_note
            item.resolved_by = actor_user_id
            item.resolved_at = now

        self._db.flush()
        self._db.commit()

        logger.info(
            "reconciliation_resolved",
            run_id=run_id,
            resolved_count=len(open_items),
            actor=actor_user_id,
        )

        return self._repo.get_run_by_id(run_id)
