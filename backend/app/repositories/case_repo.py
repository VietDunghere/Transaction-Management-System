from __future__ import annotations
"""
Repository: Case
Data access layer cho review_cases và review_case_actions.
"""

from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.models.case import ReviewCase, ReviewCaseAction
from app.models.transaction import Transaction
from app.schemas.common import CaseStatus


class CaseRepository:
    """Thao tác DB cho ReviewCase."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, case_id: str) -> Optional[ReviewCase]:
        """Lấy case kèm transaction, reviewer và actions."""
        return (
            self._db.query(ReviewCase)
            .options(
                joinedload(ReviewCase.transaction).joinedload(Transaction.merchant),
                joinedload(ReviewCase.transaction).joinedload(Transaction.customer),
                joinedload(ReviewCase.reviewer),
                joinedload(ReviewCase.actions),
            )
            .filter(ReviewCase.case_id == case_id)
            .first()
        )

    def list_cases(
        self,
        case_status: Optional[CaseStatus] = None,
        assigned_to: Optional[str] = None,
        reviewer_queue_for: Optional[str] = None,
        created_from: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[ReviewCase], int]:
        """
        Danh sách cases với filter.

        Args:
            reviewer_queue_for: Khi set (user_id của REVIEWER), trả về
                (case OPEN chưa ai nhận) OR (case được assign cho reviewer đó).
                Dùng thay cho assigned_to khi hiển thị queue REVIEWER.

        Returns:
            (items, total_count)
        """
        query = (
            self._db.query(ReviewCase)
            .options(joinedload(ReviewCase.transaction))
        )

        if case_status:
            query = query.filter(ReviewCase.case_status == case_status.value)

        if reviewer_queue_for:
            # Compound: OPEN (unassigned) hoặc assigned cho reviewer này
            query = query.filter(
                or_(
                    ReviewCase.assigned_to.is_(None),
                    ReviewCase.assigned_to == reviewer_queue_for,
                )
            )
        elif assigned_to:
            query = query.filter(ReviewCase.assigned_to == assigned_to)

        if created_from:
            query = query.filter(ReviewCase.created_at >= created_from)

        total = query.count()
        items = (
            query.order_by(ReviewCase.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total
