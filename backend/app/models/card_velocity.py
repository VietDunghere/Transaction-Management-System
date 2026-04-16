from __future__ import annotations
from typing import Optional, List
"""
ORM Model: CardVelocityStats
Cache thống kê lịch sử giao dịch theo từng thẻ.
Cập nhật mỗi khi có giao dịch mới — dùng để tính features online.

Tại sao cần bảng này:
- Model cần cc_avg_daily_txn, cc_total_txn, cc_avg_amt, cc_std_amt
- Không thể scan toàn bộ lịch sử mỗi lần score (quá chậm)
- Giải pháp: maintain rolling stats, upsert mỗi giao dịch mới
"""

from datetime import datetime

from sqlalchemy import DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CardVelocityStats(Base):
    """
    Cache velocity statistics per card (SHA256 hash).
    Được cập nhật sau mỗi giao dịch bằng incremental update formula.
    """

    __tablename__ = "card_velocity_stats"

    # SHA256 hash của cc_num — không lưu số thẻ thật
    card_hash: Mapped[str] = mapped_column(String(64), primary_key=True)

    # ---- Velocity features ----
    avg_daily_txn: Mapped[float] = mapped_column(Numeric(8, 2), default=0.0)
    total_txn: Mapped[int] = mapped_column(Integer, default=0)
    avg_amt: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0)
    std_amt: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0)

    # ---- Welford's algorithm state (online mean/variance) ----
    # M2 = sum of squared deviations — dùng tính std mà không cần lưu toàn bộ history
    m2_amt: Mapped[float] = mapped_column(Numeric(20, 4), default=0.0)

    # ---- Tracking ----
    distinct_days: Mapped[int] = mapped_column(Integer, default=1)
    last_txn_date: Mapped[Optional[str]] = mapped_column(String(10))  # YYYY-MM-DD
    last_updated: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), onupdate=func.now(), nullable=False
    )
