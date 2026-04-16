from __future__ import annotations
"""
Repository: ReconciliationRepository
Data access layer cho reconciliation_runs và reconciliation_items.
"""

from typing import Optional

from sqlalchemy import desc, func
from sqlalchemy.orm import Session, joinedload

from app.models.reconciliation import ReconciliationItem, ReconciliationRun


class ReconciliationRepository:
    """CRUD cho ReconciliationRun và ReconciliationItem."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ---- ReconciliationRun ----

    def get_run_by_id(self, run_id: str) -> Optional[ReconciliationRun]:
        """Lấy run kèm eager-load items để tránh N+1 query."""
        return (
            self._db.query(ReconciliationRun)
            .options(joinedload(ReconciliationRun.items))
            .filter(ReconciliationRun.run_id == run_id)
            .first()
        )

    def list_runs(
        self,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ReconciliationRun], int]:
        query = self._db.query(ReconciliationRun)
        if status:
            query = query.filter(ReconciliationRun.status == status)

        total = query.count()
        items = (
            query.order_by(desc(ReconciliationRun.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def create_run(self, run: ReconciliationRun) -> ReconciliationRun:
        self._db.add(run)
        self._db.flush()
        return run

    # ---- ReconciliationItem ----

    def create_item(self, item: ReconciliationItem) -> None:
        """Thêm 1 item vào session (bulk flush sau)."""
        self._db.add(item)

    def get_open_items(self, run_id: str) -> list[ReconciliationItem]:
        """Lấy tất cả items còn OPEN trong 1 run — dùng cho bulk resolve."""
        return (
            self._db.query(ReconciliationItem)
            .filter(
                ReconciliationItem.run_id == run_id,
                ReconciliationItem.status == "OPEN",
            )
            .all()
        )

    def count_open_items(self, run_id: str) -> int:
        """Đếm số items OPEN còn lại — dùng để confirm resolve hoàn tất."""
        result = (
            self._db.query(func.count(ReconciliationItem.item_id))
            .filter(
                ReconciliationItem.run_id == run_id,
                ReconciliationItem.status == "OPEN",
            )
            .scalar()
        )
        return result or 0
