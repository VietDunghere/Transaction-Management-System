from __future__ import annotations
"""
ORM Model: Customer
Thông tin khách hàng — nạp sẵn từ core banking (ERD v2).
"""

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Customer(Base):
    """Bảng customers — khách hàng/chủ thẻ (ERD v2)."""

    __tablename__ = "customers"

    customer_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    customer_code: Mapped[Optional[str]] = mapped_column(String(50), unique=True, index=True)

    # ---- Thông tin cá nhân ----
    full_name: Mapped[Optional[str]] = mapped_column(String(150))
    identity_card: Mapped[Optional[str]] = mapped_column(String(50), unique=True)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date)
    gender: Mapped[Optional[str]] = mapped_column(String(10))
    address: Mapped[Optional[str]] = mapped_column(String(255))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(10))
    job: Mapped[Optional[str]] = mapped_column(String(150))

    # ---- Toạ độ địa lý ----
    latitude: Mapped[Optional[float]] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(9, 6))

    # ---- Quản lý rủi ro ----
    income_level: Mapped[Optional[str]] = mapped_column(String(50))
    kyc_status: Mapped[Optional[str]] = mapped_column(String(20))

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), nullable=False)

    # Relationships
    transactions: Mapped[list["Transaction"]] = relationship(  # noqa: F821
        "Transaction", back_populates="customer"
    )
