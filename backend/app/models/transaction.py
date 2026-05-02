from __future__ import annotations
"""
ORM Model: Transaction
Giao dịch thời gian thực (ERD v2).
Đã gộp fraud_score + model_version vào bảng chính.
Loại bỏ: currency_code, reason_code, override_reason, source_ip,
         txn_state, txn_state_history, txn_idempotency.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Transaction(Base):
    """Bảng transactions_live (ERD v2)."""

    __tablename__ = "transactions_live"

    txn_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # ---- Liên kết thực thể ----
    customer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("customers.customer_id"), nullable=False, index=True
    )
    merchant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("merchants.merchant_id"), nullable=False, index=True
    )
    channel_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("channels.channel_id"), nullable=False, index=True
    )
    submitted_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.user_id"), nullable=False
    )

    # ---- Thông tin thẻ ----
    card_number_masked: Mapped[Optional[str]] = mapped_column(String(30))
    card_number_hash: Mapped[Optional[str]] = mapped_column(String(64), index=True)

    # ---- Thông tin giao dịch ----
    amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    txn_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    # ---- Kết quả xử lý (gộp từ risk_scoring_results) ----
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING", index=True)
    fraud_score: Mapped[Optional[float]] = mapped_column(Numeric(6, 4))
    model_version: Mapped[Optional[str]] = mapped_column(String(50))

    # ---- Metadata ----
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())

    # ---- Relationships ----
    customer: Mapped["Customer"] = relationship("Customer", back_populates="transactions")       # noqa: F821
    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="transactions")       # noqa: F821
    channel: Mapped["Channel"] = relationship("Channel", back_populates="transactions")          # noqa: F821
    review_case: Mapped[Optional["ReviewCase"]] = relationship(                                  # noqa: F821
        "ReviewCase", back_populates="transaction", uselist=False
    )
