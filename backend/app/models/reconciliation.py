from __future__ import annotations
from typing import Optional, List
"""
ORM Models: ReconciliationRun, ReconciliationItem
Đối soát giao dịch — phát hiện và xử lý bất thường.

ReconciliationRun  — một phiên đối soát cho 1 khoảng thời gian.
ReconciliationItem — mỗi giao dịch bất thường phát hiện trong phiên.
"""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ReconciliationRun(Base):
    """
    Bảng reconciliation_runs — mỗi lần chạy đối soát cho 1 khoảng thời gian.
    Kết quả: matched_count (giao dịch đã hoàn thành) và
             discrepancy_count (giao dịch cần xử lý thêm).
    """

    __tablename__ = "reconciliation_runs"

    run_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # Khoảng thời gian đối soát
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # RUNNING | COMPLETED | FAILED
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="RUNNING", index=True)

    # Kết quả đối soát
    total_txn_count: Mapped[Optional[int]] = mapped_column(Integer)
    matched_count: Mapped[Optional[int]] = mapped_column(Integer)
    discrepancy_count: Mapped[Optional[int]] = mapped_column(Integer)
    total_amount: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))

    # Cấu hình chạy
    # Thời gian tối đa một giao dịch được phép ở trạng thái PENDING (phút)
    pending_timeout_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=120)

    # Thông tin lỗi khi FAILED
    error_message: Mapped[Optional[str]] = mapped_column(String(500))

    # Actor + thời gian
    triggered_by: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.user_id")
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False
    )

    # Relationships
    triggered_by_user: Mapped[Optional["User"]] = relationship(  # noqa: F821
        "User", foreign_keys=[triggered_by]
    )
    items: Mapped[List["ReconciliationItem"]] = relationship(
        "ReconciliationItem",
        back_populates="run",
        order_by="ReconciliationItem.created_at",
    )


class ReconciliationItem(Base):
    """
    Bảng reconciliation_items — mỗi giao dịch bất thường trong 1 phiên đối soát.

    item_type hiện tại:
      PENDING_TIMEOUT — giao dịch vẫn còn PENDING sau khi vượt quá pending_timeout_minutes.
                        Cần điều tra: có thể do lỗi hệ thống, mạng, hoặc cần xử lý thủ công.
    """

    __tablename__ = "reconciliation_items"

    item_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("reconciliation_runs.run_id"), nullable=False, index=True
    )
    txn_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("transactions_live.txn_id"), index=True
    )

    # PENDING_TIMEOUT (extendable in future phases)
    item_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Snapshot trạng thái giao dịch lúc đối soát
    txn_status: Mapped[Optional[str]] = mapped_column(String(20))
    txn_amount: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    txn_created_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    # Số phút giao dịch đã ở trạng thái PENDING
    minutes_pending: Mapped[Optional[int]] = mapped_column(Integer)

    # Trạng thái xử lý discrepancy
    # OPEN | RESOLVED
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="OPEN", index=True)
    resolution_note: Mapped[Optional[str]] = mapped_column(String(500))
    resolved_by: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.user_id")
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False
    )

    # Relationships
    run: Mapped["ReconciliationRun"] = relationship(
        "ReconciliationRun", back_populates="items"
    )
    transaction: Mapped[Optional["Transaction"]] = relationship(  # noqa: F821
        "Transaction", foreign_keys=[txn_id]
    )
    resolver: Mapped[Optional["User"]] = relationship(  # noqa: F821
        "User", foreign_keys=[resolved_by]
    )
