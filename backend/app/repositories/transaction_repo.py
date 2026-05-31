from __future__ import annotations
"""
Repository: Transaction (ERD v2)
Dropped: TxnState, TxnStateHistory, TxnIdempotency.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session, joinedload

from app.models.transaction import TransactionLive
from app.schemas.common import TransactionStatus


class TransactionRepository:

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, txn_id: str) -> Optional[TransactionLive]:
        return (
            self._db.query(TransactionLive)
            .options(
                joinedload(TransactionLive.customer),
                joinedload(TransactionLive.merchant),
                joinedload(TransactionLive.channel),
            )
            .filter(TransactionLive.txn_id == txn_id)
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
    ) -> tuple[list[TransactionLive], int]:
        query = self._db.query(TransactionLive)

        filters = []
        if status:
            filters.append(TransactionLive.status == status.value)
        if customer_id:
            filters.append(TransactionLive.customer_id == customer_id)
        if merchant_id:
            filters.append(TransactionLive.merchant_id == merchant_id)
        if submitted_by:
            filters.append(TransactionLive.submitted_by == submitted_by)
        if date_from:
            filters.append(TransactionLive.txn_time >= date_from)
        if date_to:
            filters.append(TransactionLive.txn_time <= date_to)
        if min_amount is not None:
            filters.append(TransactionLive.amount >= min_amount)
        if max_amount is not None:
            filters.append(TransactionLive.amount <= max_amount)
        if created_after is not None:
            filters.append(TransactionLive.created_at >= created_after)

        if filters:
            query = query.filter(and_(*filters))

        total = query.count()
        items = (
            query.order_by(desc(TransactionLive.txn_time))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def create(self, txn: TransactionLive) -> TransactionLive:
        self._db.add(txn)
        self._db.flush()
        return txn

    def update_status(self, txn_id: str, status: str, fraud_score: Optional[float] = None) -> None:
        self._db.query(TransactionLive).filter(TransactionLive.txn_id == txn_id).update({
            "status": status,
            "fraud_score": fraud_score,
        })
