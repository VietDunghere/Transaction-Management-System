from __future__ import annotations
"""
ORM Models: ModelConfig & SuppressionRule
- ModelConfig: lưu threshold của fraud/loan model động (thay vì hardcode trong settings)
- SuppressionRule: whitelist bypass fraud scoring cho merchant/customer/card cụ thể
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ModelConfig(Base):
    """Bảng model_configs — lưu threshold fraud/loan có thể chỉnh bởi ANALYST."""

    __tablename__ = "model_configs"

    config_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_name: Mapped[str] = mapped_column(String(50), nullable=False)        # "fraud" | "loan"
    param_name: Mapped[str] = mapped_column(String(100), nullable=False)       # "reject_threshold" ...
    param_value: Mapped[float] = mapped_column(Numeric(10, 6), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    updated_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.user_id"))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), onupdate=func.now(), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    updater: Mapped[Optional["User"]] = relationship("User", foreign_keys=[updated_by])  # type: ignore[name-defined]


class SuppressionRule(Base):
    """Bảng suppression_rules — whitelist bypass fraud scoring."""

    __tablename__ = "suppression_rules"

    rule_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    rule_type: Mapped[str] = mapped_column(String(20), nullable=False)         # MERCHANT | CUSTOMER | CARD_HASH
    entity_id: Mapped[str] = mapped_column(String(255), nullable=False)        # merchant_id / customer_id / card_hash
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.user_id"), nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)           # NULL = không hết hạn
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False
    )

    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])  # type: ignore[name-defined]
