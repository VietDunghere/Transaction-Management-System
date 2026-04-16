from __future__ import annotations
from typing import Optional, List
"""
ORM Model: RiskScoringResult, RuleHit, AuditLog
Kết quả chấm điểm fraud detection và audit trail.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RiskScoringResult(Base):
    """
    Kết quả chạy model ML cho mỗi giao dịch.
    Lưu cả feature vector để phục vụ audit và retraining.
    """

    __tablename__ = "risk_scoring_results"

    score_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    txn_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("transactions_live.txn_id"), nullable=False, index=True
    )
    model_version: Mapped[Optional[str]] = mapped_column(String(50))
    fraud_score: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False)

    # APPROVED | MANUAL_REVIEW | REJECTED
    decision_suggested: Mapped[Optional[str]] = mapped_column(String(20))

    # Threshold tại thời điểm score (có thể thay đổi theo thời gian)
    reject_threshold: Mapped[Optional[float]] = mapped_column(Numeric(6, 4))
    review_threshold: Mapped[Optional[float]] = mapped_column(Numeric(6, 4))

    # JSON string chứa feature vector đã dùng — dùng cho audit và model retraining
    feature_snapshot_json: Mapped[Optional[str]] = mapped_column(Text)

    # Reason codes dạng JSON: {"top_features": [...], "rule_hits": [...]}
    reason_json: Mapped[Optional[str]] = mapped_column(Text)

    score_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), nullable=False)

    # Relationships
    transaction: Mapped["Transaction"] = relationship(  # noqa: F821
        "Transaction", back_populates="scoring_results"
    )


class RuleHit(Base):
    """
    Bảng rule_hits — kết quả các rule-based checks chạy song song với ML.
    VD: BLACKLISTED_MERCHANT, NIGHT_TRANSACTION, AMOUNT_SPIKE
    """

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
    severity: Mapped[Optional[str]] = mapped_column(String(20))  # LOW | MEDIUM | HIGH | CRITICAL
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), nullable=False)


class AuditLog(Base):
    """
    Bảng audit_logs — lịch sử hành động của mọi user trong hệ thống.
    Bảng này KHÔNG BAO GIỜ được phép xóa hay sửa (theo quy định ngân hàng).
    """

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
