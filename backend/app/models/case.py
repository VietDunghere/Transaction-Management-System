from __future__ import annotations
"""
ORM Model: ReviewCase
ERD v2: ReviewCaseAction dropped (audit_logs replaces).
case_status: OPEN | ASSIGNED | CLOSED (decision is separate column).
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ReviewCase(Base):
    """Bảng review_cases — tạo tự động khi txn.status = MANUAL_REVIEW (ERD v2)."""

    __tablename__ = "review_cases"

    case_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    txn_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("transactions_live.txn_id"), unique=True, nullable=False
    )
    # OPEN | ASSIGNED | CLOSED
    case_status: Mapped[str] = mapped_column(String(20), nullable=False, default="OPEN", index=True)
    assigned_to: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.user_id")
    )
    decision: Mapped[Optional[str]] = mapped_column(String(20))       # APPROVE | REJECT
    decision_note: Mapped[Optional[str]] = mapped_column(String(2000))
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), nullable=False)
    decided_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relationships
    transaction: Mapped["Transaction"] = relationship(  # noqa: F821
        "Transaction", back_populates="review_case"
    )
    reviewer: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_to])  # noqa: F821
