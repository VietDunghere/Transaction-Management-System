from __future__ import annotations
"""
Repository: Transaction
Data access layer cho transactions_live và các bảng liên quan.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session, joinedload

from app.models.transaction import Transaction, TxnIdempotency, TxnState, TxnStateHistory
from app.schemas.common import TransactionStatus


class TransactionRepository:
    """Thao tác DB cho Transaction."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, txn_id: str) -> Optional[Transaction]:
        """Lấy giao dịch theo ID, kèm scoring results và customer/merchant."""
        return (
            self._db.query(Transaction)
            .options(
                joinedload(Transaction.customer),
                joinedload(Transaction.merchant),
                joinedload(Transaction.channel),
                joinedload(Transaction.scoring_results),
            )
            .filter(Transaction.txn_id == txn_id)
            .first()
        )

    def list_transactions(
        self,
        status: Optional[TransactionStatus] = None,
        customer_id: Optional[str] = None,
        merchant_id: Optional[str] = None,
        submitted_by: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Transaction], int]:
        """
        Danh sách giao dịch với filter và pagination.

        Returns:
            (items, total_count)
        """
        query = self._db.query(Transaction)

        # ---- Apply filters ----
        filters = []
        if status:
            filters.append(Transaction.status == status.value)
        if customer_id:
            filters.append(Transaction.customer_id == customer_id)
        if merchant_id:
            filters.append(Transaction.merchant_id == merchant_id)
        if submitted_by:
            filters.append(Transaction.submitted_by == submitted_by)
        if date_from:
            filters.append(Transaction.txn_time >= date_from)
        if date_to:
            filters.append(Transaction.txn_time <= date_to)
        if min_amount is not None:
            filters.append(Transaction.amount >= min_amount)
        if max_amount is not None:
            filters.append(Transaction.amount <= max_amount)

        if filters:
            query = query.filter(and_(*filters))

        total = query.count()
        items = (
            query.order_by(desc(Transaction.txn_time))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def create(self, txn: Transaction) -> Transaction:
        """Insert giao dịch mới và flush để lấy generated fields."""
        self._db.add(txn)
        self._db.flush()
        return txn

    def update_status(self, txn_id: str, status: str, fraud_score: Optional[float] = None,
                      reason_code: Optional[str] = None) -> None:
        """Cập nhật status và fraud_score của giao dịch."""
        self._db.query(Transaction).filter(Transaction.txn_id == txn_id).update({
            "status": status,
            "fraud_score": fraud_score,
            "reason_code": reason_code,
        })

    # ---- Idempotency ----

    def get_idempotency(self, key: str) -> Optional[TxnIdempotency]:
        """Tìm idempotency record theo key."""
        return self._db.query(TxnIdempotency).filter(
            TxnIdempotency.idempotency_key == key
        ).first()

    def create_idempotency(self, record: TxnIdempotency) -> None:
        """Tạo idempotency record (trước khi xử lý)."""
        self._db.add(record)
        self._db.flush()

    def update_idempotency(self, key: str, status: str, txn_id: Optional[str] = None,
                           response_json: Optional[str] = None) -> None:
        """Cập nhật kết quả sau khi xử lý xong."""
        self._db.query(TxnIdempotency).filter(
            TxnIdempotency.idempotency_key == key
        ).update({
            "status": status,
            "txn_id": txn_id,
            "response_snapshot_json": response_json,
        })

    # ---- State history ----

    def append_state_history(self, record: TxnStateHistory) -> None:
        """Ghi thêm 1 row vào lịch sử trạng thái."""
        self._db.add(record)

    def get_state_history(self, txn_id: str) -> list[TxnStateHistory]:
        """
        Lấy toàn bộ lịch sử trạng thái của giao dịch, sắp xếp theo thời gian tăng dần.
        Dùng cho endpoint audit trail.
        """
        return (
            self._db.query(TxnStateHistory)
            .filter(TxnStateHistory.txn_id == txn_id)
            .order_by(TxnStateHistory.changed_at)
            .all()
        )
