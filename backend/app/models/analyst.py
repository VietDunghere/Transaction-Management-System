from __future__ import annotations
"""
ORM Model: ModelConfig
ERD v2: SuppressionRule dropped.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Identity, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ModelConfig(Base):
    """Bảng model_configs — ngưỡng phân loại AI, ANALYST điều chỉnh (ERD v2)."""

    __tablename__ = "model_configs"
    __table_args__ = (UniqueConstraint("model_name", "param_name", name="uq_model_configs_name_param"),)

    config_id: Mapped[int] = mapped_column(Integer, Identity(start=1), primary_key=True)
    model_name: Mapped[str] = mapped_column(String(50), nullable=False)
    param_name: Mapped[str] = mapped_column(String(100), nullable=False)
    param_value: Mapped[float] = mapped_column(Numeric(10, 6), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    updated_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.user_id"))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), onupdate=func.now(), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    updater: Mapped[Optional["User"]] = relationship("User", foreign_keys=[updated_by])  # type: ignore[name-defined]
