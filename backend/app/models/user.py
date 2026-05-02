from __future__ import annotations
"""
ORM Model: User
Quản lý tài khoản nhân viên — role gộp trực tiếp trên bảng users (ERD v2).
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    """Bảng users — tài khoản nhân viên ngân hàng (ERD v2: role + status inline)."""

    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(150), unique=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())

    @property
    def roles(self) -> list[str]:
        """Backward-compat: trả list 1 phần tử cho code đang dùng user.roles."""
        return [self.role]

    @property
    def is_active(self) -> bool:
        """Backward-compat: status == ACTIVE."""
        return self.status == "ACTIVE"

    def has_role(self, role_name: str) -> bool:
        return self.role == role_name
