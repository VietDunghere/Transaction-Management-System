from __future__ import annotations
"""
ORM Model: Loan
Vòng đời khoản vay: PENDING → APPROVED | REJECTED
Sau khi approved: DISBURSED → CLOSED | DEFAULTED (Phase E)
"""

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Loan(Base):
    """
    Bảng loans — khoản vay của khách hàng.
    OPERATOR tạo đơn vay (submitted_by), MANAGER phê duyệt (reviewed_by).
    Sử dụng optimistic locking (version) để tránh race condition khi 2 MANAGER
    cùng phê duyệt 1 khoản vay.
    """

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
    currency_code: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    # Lãi suất hàng năm dạng thập phân, VD: 0.1200 = 12%/năm
    interest_rate: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False)
    term_months: Mapped[int] = mapped_column(Integer, nullable=False)
    purpose: Mapped[Optional[str]] = mapped_column(String(200))

    # ---- Trạng thái ----
    # PENDING | APPROVED | REJECTED | DISBURSED | CLOSED | DEFAULTED
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="PENDING", index=True
    )
    # Optimistic locking — tăng mỗi lần cập nhật trạng thái
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # ---- Kết quả phê duyệt ----
    review_note: Mapped[Optional[str]] = mapped_column(String(500))
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # ---- Thông tin giải ngân (điền khi APPROVED) ----
    # Tiền trả hàng tháng theo công thức amortisation
    monthly_payment: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    # Dư nợ còn lại — khởi tạo = principal_amount
    outstanding_balance: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    disbursed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    maturity_date: Mapped[Optional[date]] = mapped_column(Date)

    # ---- Loan AI input features (snapshot tại thời điểm nộp đơn) ----
    # Khớp với feature contract của train_loan_model.py v6:
    # loan_amnt = principal_amount, loan_int_rate = interest_rate × 100,
    # loan_percent_income = principal_amount / person_income — tính lúc scoring
    person_age: Mapped[Optional[int]] = mapped_column(Integer)
    person_income: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    person_home_ownership: Mapped[Optional[str]] = mapped_column(String(20))   # RENT|MORTGAGE|OWN|OTHER
    person_emp_length: Mapped[Optional[int]] = mapped_column(Integer)
    loan_grade: Mapped[Optional[str]] = mapped_column(String(2))               # A-G
    loan_intent: Mapped[Optional[str]] = mapped_column(String(30))             # PERSONAL|EDUCATION|MEDICAL|VENTURE|HOMEIMPROVEMENT|DEBTCONSOLIDATION
    cb_person_default_on_file: Mapped[Optional[str]] = mapped_column(String(1)) # Y|N
    cb_person_cred_hist_length: Mapped[Optional[int]] = mapped_column(Integer)

    # ---- Kết quả AI (điền bởi LoanScoringService khi APPROVE) ----
    # Xác suất vỡ nợ: 0.0 – 1.0
    pd_score: Mapped[Optional[float]] = mapped_column(Numeric(6, 4))
    # LOW RISK | MEDIUM RISK | HIGH RISK
    risk_level: Mapped[Optional[str]] = mapped_column(String(20))

    # ---- Metadata ----
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())

    # ---- Relationships ----
    customer: Mapped["Customer"] = relationship(  # noqa: F821
        "Customer", foreign_keys=[customer_id]
    )
    submitter: Mapped["User"] = relationship(  # noqa: F821
        "User", foreign_keys=[submitted_by]
    )
    reviewer: Mapped[Optional["User"]] = relationship(  # noqa: F821
        "User", foreign_keys=[reviewed_by]
    )
