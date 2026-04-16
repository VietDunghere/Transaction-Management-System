from __future__ import annotations
from typing import Optional, List
"""
ORM Model: Transaction, TxnState, TxnStateHistory, TxnIdempotency
Vòng đời giao dịch: PENDING → APPROVED | REJECTED | MANUAL_REVIEW
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Transaction(Base):
    """
    Bảng transactions_live — giao dịch thời gian thực.
    Mỗi row là một lần quẹt thẻ/thanh toán.
    """

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
    # Không lưu số thẻ raw — chỉ lưu hash SHA256 để lookup velocity stats
    card_number_masked: Mapped[Optional[str]] = mapped_column(String(30))   # VD: "4111 **** **** 1111"
    card_number_hash: Mapped[Optional[str]] = mapped_column(String(64), index=True)  # SHA256

    # ---- Thông tin giao dịch ----
    amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    txn_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    # ---- Kết quả xử lý ----
    # PENDING | APPROVED | REJECTED | MANUAL_REVIEW
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING", index=True)
    fraud_score: Mapped[Optional[float]] = mapped_column(Numeric(6, 4))
    reason_code: Mapped[Optional[str]] = mapped_column(String(50))      # VD: HIGH_FRAUD_SCORE
    override_reason: Mapped[Optional[str]] = mapped_column(String(50))  # VD: BLACKLISTED_MERCHANT

    # ---- Metadata ----
    source_ip: Mapped[Optional[str]] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())

    # ---- Relationships ----
    customer: Mapped["Customer"] = relationship("Customer", back_populates="transactions")       # noqa: F821
    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="transactions")       # noqa: F821
    channel: Mapped["Channel"] = relationship("Channel", back_populates="transactions")          # noqa: F821
    scoring_results: Mapped[list["RiskScoringResult"]] = relationship(                           # noqa: F821
        "RiskScoringResult", back_populates="transaction"
    )
    review_case: Mapped[Optional["ReviewCase"]] = relationship(                                     # noqa: F821
        "ReviewCase", back_populates="transaction", uselist=False
    )
    state: Mapped["TxnState | None"] = relationship(                                             # noqa: F821
        "TxnState", back_populates="transaction", uselist=False
    )


class TxnState(Base):
    """
    Bảng txn_state — trạng thái hiện tại của giao dịch.
    Tách riêng để lock optimistic khi cập nhật status.
    """

    __tablename__ = "txn_state"

    txn_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("transactions_live.txn_id"), primary_key=True
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    last_update: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())
    reason_code: Mapped[Optional[str]] = mapped_column(String(50))
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error_code: Mapped[Optional[str]] = mapped_column(String(50))
    last_error_message: Mapped[Optional[str]] = mapped_column(String(500))
    # Optimistic locking — tăng mỗi lần cập nhật
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="state")


class TxnStateHistory(Base):
    """Lịch sử thay đổi trạng thái giao dịch — dùng cho audit trail."""

    __tablename__ = "txn_state_history"

    state_hist_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    txn_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("transactions_live.txn_id"), nullable=False, index=True
    )
    old_status: Mapped[Optional[str]] = mapped_column(String(20))
    new_status: Mapped[str] = mapped_column(String(20), nullable=False)
    changed_by_user_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.user_id")
    )
    changed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), nullable=False)
    change_reason: Mapped[Optional[str]] = mapped_column(String(200))


class TxnIdempotency(Base):
    """
    Bảng idempotency — ngăn xử lý giao dịch trùng lặp.
    Khi cùng một request gửi lại (network retry), trả về kết quả cũ.
    """

    __tablename__ = "txn_idempotency"

    idempotency_key: Mapped[str] = mapped_column(String(100), primary_key=True)
    txn_hash: Mapped[Optional[str]] = mapped_column(String(128))
    txn_id: Mapped[Optional[str]] = mapped_column(String(36))
    # IN_PROGRESS | SUCCESS | FAILED
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    response_snapshot_json: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())
