from __future__ import annotations
from typing import Optional, List
"""
ORM Model: Customer
Thông tin khách hàng sở hữu thẻ tín dụng.
Bao gồm các trường cần thiết để model ML tính features:
  - date_of_birth → age
  - gender → feature ordinal
  - job → frequency encoded
  - lat/lon → khoảng cách đến merchant
  - city_population → frequency feature
"""

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Customer(Base):
    """Bảng customers — khách hàng/chủ thẻ."""

    __tablename__ = "customers"

    customer_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    customer_code: Mapped[Optional[str]] = mapped_column(String(50), unique=True, index=True)

    # ---- Thông tin cá nhân ----
    full_name: Mapped[Optional[str]] = mapped_column(String(150))
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date)
    gender: Mapped[Optional[str]] = mapped_column(String(1))      # F / M
    job: Mapped[Optional[str]] = mapped_column(String(150))
    identity_card: Mapped[Optional[str]] = mapped_column(String(50), unique=True)

    # ---- Địa chỉ ----
    address: Mapped[Optional[str]] = mapped_column(String(255))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(50))
    zip_code: Mapped[Optional[str]] = mapped_column(String(20))

    # ---- Toạ độ địa lý (dùng tính khoảng cách đến merchant) ----
    latitude: Mapped[Optional[float]] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(9, 6))

    # ---- Dân số thành phố (feature ML) ----
    city_population: Mapped[Optional[int]] = mapped_column(Integer)

    # ---- Quản lý rủi ro ----
    kyc_status: Mapped[Optional[str]] = mapped_column(String(20))
    income_level: Mapped[Optional[str]] = mapped_column(String(50))

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    transactions: Mapped[list["Transaction"]] = relationship(  # noqa: F821
        "Transaction", back_populates="customer"
    )
