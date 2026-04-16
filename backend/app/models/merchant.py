from __future__ import annotations
from typing import Optional, List
"""
ORM Model: Merchant & Channel
Merchant: đơn vị chấp nhận thanh toán.
Channel: kênh giao dịch (POS, ATM, Online, Mobile).
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Merchant(Base):
    """Bảng merchants — nơi phát sinh giao dịch."""

    __tablename__ = "merchants"

    merchant_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    merchant_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    merchant_name: Mapped[str] = mapped_column(String(150), nullable=False)

    # ---- Phân loại ----
    # Khớp với Sparkov: grocery_pos, shopping_net, entertainment, ...
    merchant_category: Mapped[Optional[str]] = mapped_column(String(100))
    risk_level: Mapped[Optional[str]] = mapped_column(String(20))   # LOW | MEDIUM | HIGH
    is_blacklisted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # ---- Địa chỉ (dùng tính khoảng cách đến customer) ----
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(50))
    country: Mapped[Optional[str]] = mapped_column(String(100))

    # ---- Toạ độ địa lý ----
    latitude: Mapped[Optional[float]] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(9, 6))

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), nullable=False)

    # Relationships
    transactions: Mapped[list["Transaction"]] = relationship(  # noqa: F821
        "Transaction", back_populates="merchant"
    )


class Channel(Base):
    """Kênh giao dịch: POS | ATM | ONLINE | MOBILE_APP."""

    __tablename__ = "channels"

    channel_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    channel_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    channel_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    transactions: Mapped[list["Transaction"]] = relationship(  # noqa: F821
        "Transaction", back_populates="channel"
    )
