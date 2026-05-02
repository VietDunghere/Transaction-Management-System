from __future__ import annotations
"""
ORM Model: RuleHit, AuditLog
ERD v2: RiskScoringResult dropped (gộp vào transactions_live).
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RuleHit(Base):
    """Bảng rule_hits — kết quả rule-based checks (ERD v2)."""

    __tablename__ = "rule_hits"

    rule_hit_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    txn_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("transactions_live.txn_id"), nullable=False, index=True
    )
    rule_code: Mapped[str] = mapped_column(String(50), nullable=False)
    rule_name: Mapped[Optional[str]] = mapped_column(String(150))
    hit_value: Mapped[Optional[str]] = mapped_column(String(255))
    severity: Mapped[Optional[str]] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), nullable=False)


class AuditLog(Base):
    """Bảng audit_logs — nhật ký kiểm toán toàn hệ thống (ERD v2)."""

    __tablename__ = "audit_logs"

    log_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    actor_user_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.user_id")
    )
    actor_name: Mapped[Optional[str]] = mapped_column(String(150))
    event_ts: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), nullable=False)
    detail_json: Mapped[Optional[str]] = mapped_column(Text)
