from __future__ import annotations
"""
Repository: Transaction (ERD v2)
Dropped: TxnState, TxnStateHistory, TxnIdempotency.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session, joinedload

from app.models.transaction import Transaction
from app.schemas.common import TransactionStatus


class TransactionRepository:

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, txn_id: str) -> Optional[Transaction]:
        return (
            self._db.query(Transaction)
            .options(
                joinedload(Transaction.customer),
                joinedload(Transaction.merchant),
                joinedload(Transaction.channel),
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
        created_after: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Transaction], int]:
        query = self._db.query(Transaction)

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
        if created_after is not None:
            filters.append(Transaction.created_at >= created_after)

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
        self._db.add(txn)
        self._db.flush()
        return txn

    def update_status(self, txn_id: str, status: str, fraud_score: Optional[float] = None) -> None:
        self._db.query(Transaction).filter(Transaction.txn_id == txn_id).update({
            "status": status,
            "fraud_score": fraud_score,
        })
