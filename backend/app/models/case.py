from __future__ import annotations
from typing import Optional, List
"""
ORM Model: ReviewCase, ReviewCaseAction
Case manual review — nhân viên REVIEWER xem xét quyết định.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ReviewCase(Base):
    """
    Bảng review_cases — mỗi giao dịch MANUAL_REVIEW sẽ tạo 1 case.
    Reviewer được giao case và đưa ra quyết định cuối.
    """

    __tablename__ = "review_cases"

    case_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    txn_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("transactions_live.txn_id"), unique=True, nullable=False
    )
    # OPEN | ASSIGNED | APPROVED | REJECTED | CLOSED
    case_status: Mapped[str] = mapped_column(String(20), nullable=False, default="OPEN", index=True)
    assigned_to: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.user_id")
    )
    decision: Mapped[Optional[str]] = mapped_column(String(20))       # APPROVE | REJECT
    decision_note: Mapped[Optional[str]] = mapped_column(Text)
    # Optimistic locking — tăng mỗi lần update để tránh lost update
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    decided_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relationships
    transaction: Mapped["Transaction"] = relationship(  # noqa: F821
        "Transaction", back_populates="review_case"
    )
    reviewer: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_to])  # noqa: F821
    actions: Mapped[list["ReviewCaseAction"]] = relationship(
        "ReviewCaseAction", back_populates="case", order_by="ReviewCaseAction.created_at"
    )


class ReviewCaseAction(Base):
    """
    Audit trail chi tiết của từng case — mọi hành động đều được ghi lại.
    VD: ASSIGN, COMMENT, APPROVE, REJECT, REOPEN
    """

    __tablename__ = "review_case_actions"

    action_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("review_cases.case_id"), nullable=False, index=True
    )
    # ASSIGN | COMMENT | APPROVE | REJECT | REOPEN
    action_type: Mapped[str] = mapped_column(String(30), nullable=False)
    actor_user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.user_id"), nullable=False
    )
    action_note: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    case: Mapped["ReviewCase"] = relationship("ReviewCase", back_populates="actions")
