from __future__ import annotations
"""
Pydantic schemas: ETL & DataLake
Request/Response cho ETL pipeline và DataLake ingest/query.
"""

import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field, model_validator


# ============================================================
# ETL — Request / Response
# ============================================================

class EtlRunRequest(BaseModel):
    """Request body để trigger ETL job."""
    target_date: date = Field(
        ..., description="Ngày cần xử lý (yyyy-mm-dd). ETL sẽ tổng hợp tất cả giao dịch trong ngày đó."
    )
    job_type: Literal["DAILY_SUMMARY"] = Field(
        default="DAILY_SUMMARY",
        description="Loại ETL job. Hiện tại chỉ hỗ trợ DAILY_SUMMARY.",
    )


class EtlJobResponse(BaseModel):
    """Chi tiết một ETL job run."""
    job_id: str
    job_type: str
    target_date: date
    status: str         # RUNNING | SUCCESS | FAILED
    records_in: Optional[int] = None
    records_out: Optional[int] = None
    error_message: Optional[str] = None
    triggered_by: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ============================================================
# DataLake — Request / Response
# ============================================================

class DataLakeIngestRequest(BaseModel):
    """
    Request body để ingest batch dữ liệu ngoài vào DataLake.
    Dùng cho các nguồn như: bank statement, POS gateway report, v.v.
    """
    snapshot_date: date = Field(
        ..., description="Ngày của dữ liệu được ingest (yyyy-mm-dd)."
    )
    source_label: str = Field(
        ..., min_length=2, max_length=100,
        examples=["BANK_STATEMENT", "POS_GATEWAY"],
        description="Nhãn nguồn dữ liệu — dùng để phân biệt các snapshot.",
    )
    records: List[dict] = Field(
        ...,
        min_length=1,
        max_length=10_000,
        description="Danh sách records thô (tối đa 10.000). Mỗi record là 1 dict tự do.",
    )


class DataLakeSnapshotResponse(BaseModel):
    """Chi tiết một DataLake snapshot."""
    snapshot_id: str
    snapshot_type: str      # DAILY_TXN_SUMMARY | EXTERNAL_INGEST
    snapshot_date: date
    job_id: Optional[str] = None
    source_label: Optional[str] = None
    record_count: int
    total_amount: Optional[Decimal] = None
    status: str             # ACTIVE | ARCHIVED
    created_at: datetime
    # Tóm tắt nội dung — parsed từ data_json (không trả full raw để tránh quá nặng)
    data_summary: Optional[dict] = None

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def _parse_data_json(cls, data: Any) -> Any:
        """Parse data_json thành dict summary khi input là ORM object."""
        if isinstance(data, dict):
            return data
        raw = getattr(data, "data_json", None)
        summary = None
        if raw:
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    # Trả toàn bộ nếu là DAILY_TXN_SUMMARY (compact)
                    # Trả chỉ metadata nếu là EXTERNAL_INGEST (có thể rất lớn)
                    snap_type = getattr(data, "snapshot_type", "")
                    if snap_type == "EXTERNAL_INGEST":
                        summary = {
                            "record_count": parsed.get("record_count", 0),
                            "source": parsed.get("source", ""),
                        }
                    else:
                        summary = parsed
            except (json.JSONDecodeError, TypeError):
                pass

        return {
            "snapshot_id":   data.snapshot_id,
            "snapshot_type": data.snapshot_type,
            "snapshot_date": data.snapshot_date,
            "job_id":        getattr(data, "job_id", None),
            "source_label":  getattr(data, "source_label", None),
            "record_count":  data.record_count,
            "total_amount":  getattr(data, "total_amount", None),
            "status":        data.status,
            "created_at":    data.created_at,
            "data_summary":  summary,
        }
