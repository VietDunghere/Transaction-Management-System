from __future__ import annotations
from typing import Optional
"""
ORM Models: EtlLog, DataLakeSnapshot
ETL pipeline — xử lý và lưu trữ dữ liệu tổng hợp.

EtlLog     — lịch sử mỗi lần chạy ETL (DAILY_SUMMARY).
DataLakeSnapshot — điểm dữ liệu tổng hợp hoặc ingest thô từ nguồn ngoài.
"""

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EtlLog(Base):
    """
    Bảng etl_logs — ghi nhận mỗi lần chạy ETL job.
    Mỗi job đọc transactions của một ngày cụ thể (target_date),
    tổng hợp và ghi vào DataLakeSnapshot.
    """

    __tablename__ = "etl_logs"

    job_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # Loại job: DAILY_SUMMARY
    job_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Ngày dữ liệu được xử lý
    target_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    # RUNNING | SUCCESS | FAILED
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="RUNNING", index=True)

    # Thống kê xử lý
    records_in: Mapped[Optional[int]] = mapped_column(Integer)   # rows đọc từ transactions_live
    records_out: Mapped[Optional[int]] = mapped_column(Integer)  # snapshots ghi ra

    # Thời gian
    started_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Thông tin lỗi khi FAILED
    error_message: Mapped[Optional[str]] = mapped_column(String(500))

    # Actor
    triggered_by: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.user_id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False
    )

    # Relationships
    triggered_by_user: Mapped[Optional["User"]] = relationship(  # noqa: F821
        "User", foreign_keys=[triggered_by]
    )
    snapshot: Mapped[Optional["DataLakeSnapshot"]] = relationship(
        "DataLakeSnapshot", back_populates="etl_job", uselist=False
    )


class DataLakeSnapshot(Base):
    """
    Bảng datalake_snapshots — lưu điểm dữ liệu tổng hợp.

    Có 2 loại snapshot:
    - DAILY_TXN_SUMMARY: tạo tự động bởi ETL job (có job_id)
    - EXTERNAL_INGEST: ingest thủ công từ nguồn ngoài (không có job_id)
    """

    __tablename__ = "datalake_snapshots"

    snapshot_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # DAILY_TXN_SUMMARY | EXTERNAL_INGEST
    snapshot_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Ngày dữ liệu trong snapshot
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    # FK tới ETL job đã tạo snapshot này (null nếu EXTERNAL_INGEST)
    job_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("etl_logs.job_id")
    )
    # Nguồn dữ liệu (dùng cho EXTERNAL_INGEST: BANK_STATEMENT, POS_GATEWAY, v.v.)
    source_label: Mapped[Optional[str]] = mapped_column(String(100))

    # Metadata
    record_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_amount: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))

    # Nội dung JSON (aggregated hoặc raw batch)
    data_json: Mapped[Optional[str]] = mapped_column(Text)

    # ACTIVE | ARCHIVED
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE", index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False
    )

    # Relationships
    etl_job: Mapped[Optional["EtlLog"]] = relationship(
        "EtlLog", back_populates="snapshot"
    )
