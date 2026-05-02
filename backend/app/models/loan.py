from __future__ import annotations
"""
ORM Model: Loan
Vòng đời khoản vay (ERD v2).
Loại bỏ currency_code. Thêm model_version.
"""

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Loan(Base):
    """Bảng loans — khoản vay (ERD v2)."""

    __tablename__ = "loans"

    loan_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # ---- Liên kết ----
    customer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("customers.customer_id"), nullable=False, index=True
    )
    submitted_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.user_id"), nullable=False
    )
    reviewed_by: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.user_id")
    )

    # ---- Điều kiện khoản vay ----
    principal_amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    interest_rate: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False)
    term_months: Mapped[int] = mapped_column(Integer, nullable=False)
    purpose: Mapped[Optional[str]] = mapped_column(String(200))

    # ---- Trạng thái ----
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="PENDING", index=True
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # ---- Kết quả phê duyệt ----
    review_note: Mapped[Optional[str]] = mapped_column(String(500))
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # ---- Thông tin giải ngân ----
    monthly_payment: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    outstanding_balance: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    disbursed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    maturity_date: Mapped[Optional[date]] = mapped_column(Date)

    # ---- Loan AI input features (snapshot) ----
    person_age: Mapped[Optional[int]] = mapped_column(Integer)
    person_income: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    person_home_ownership: Mapped[Optional[str]] = mapped_column(String(20))
    person_emp_length: Mapped[Optional[int]] = mapped_column(Integer)
    loan_grade: Mapped[Optional[str]] = mapped_column(String(2))
    loan_intent: Mapped[Optional[str]] = mapped_column(String(30))
    cb_person_default_on_file: Mapped[Optional[str]] = mapped_column(String(1))
    cb_person_cred_hist_length: Mapped[Optional[int]] = mapped_column(Integer)

    # ---- AI scoring output ----
    pd_score: Mapped[Optional[float]] = mapped_column(Numeric(6, 4))
    risk_level: Mapped[Optional[str]] = mapped_column(String(20))
    model_version: Mapped[Optional[str]] = mapped_column(String(50))

    # ---- Metadata ----
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())

    # ---- Relationships ----
    customer: Mapped["Customer"] = relationship("Customer", foreign_keys=[customer_id])        # noqa: F821
    submitter: Mapped["User"] = relationship("User", foreign_keys=[submitted_by])              # noqa: F821
    reviewer: Mapped[Optional["User"]] = relationship("User", foreign_keys=[reviewed_by])      # noqa: F821
