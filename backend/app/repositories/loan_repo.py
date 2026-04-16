from __future__ import annotations
"""
Repository: Loan
Data access layer cho bảng loans.
Chỉ chứa thao tác DB thuần — không có business logic.
"""

from typing import Optional

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session, joinedload

from app.models.loan import Loan
from app.schemas.common import LoanStatus


class LoanRepository:
    """Thao tác DB cho Loan."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, loan_id: str) -> Optional[Loan]:
        """
        Lấy khoản vay theo ID.
        Eager-load customer, submitter, reviewer để tránh N+1 khi serialize.
        """
        return (
            self._db.query(Loan)
            .options(
                joinedload(Loan.customer),
                joinedload(Loan.submitter),
                joinedload(Loan.reviewer),
            )
            .filter(Loan.loan_id == loan_id)
            .first()
        )

    def list_loans(
        self,
        customer_id: Optional[str] = None,
        submitted_by: Optional[str] = None,
        status: Optional[LoanStatus] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Loan], int]:
        """
        Danh sách khoản vay với filter và pagination.

        Returns:
            (items, total_count)
        """
        query = self._db.query(Loan)

        filters = []
        if customer_id:
            filters.append(Loan.customer_id == customer_id)
        if submitted_by:
            filters.append(Loan.submitted_by == submitted_by)
        if status:
            filters.append(Loan.status == status.value)

        if filters:
            query = query.filter(and_(*filters))

        total = query.count()
        items = (
            query.order_by(desc(Loan.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def create(self, loan: Loan) -> Loan:
        """Insert khoản vay mới và flush để lấy generated fields."""
        self._db.add(loan)
        self._db.flush()
        return loan
