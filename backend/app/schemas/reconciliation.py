from __future__ import annotations
"""
Pydantic schemas: Reconciliation
Request/Response cho đối soát giao dịch.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


# ============================================================
# Request schemas
# ============================================================

class ReconciliationRunRequest(BaseModel):
    """
    Request body để trigger một phiên đối soát.
    Hệ thống sẽ tìm tất cả giao dịch PENDING trong khoảng thời gian
    đã vượt quá pending_timeout_minutes mà chưa được xử lý.
    """
    period_start: datetime = Field(
        ..., description="Bắt đầu khoảng thời gian đối soát (ISO 8601)."
    )
    period_end: datetime = Field(
        ..., description="Kết thúc khoảng thời gian đối soát (ISO 8601)."
    )
    pending_timeout_minutes: int = Field(
        default=120,
        ge=1,
        le=10080,
        description=(
            "Số phút tối đa một giao dịch được phép ở trạng thái PENDING. "
            "Giao dịch PENDING vượt quá ngưỡng này sẽ bị đánh dấu là PENDING_TIMEOUT. "
            "Mặc định: 120 phút (2 tiếng)."
        ),
    )


class ResolveRequest(BaseModel):
    """Request body để bulk-resolve tất cả discrepancy OPEN trong 1 phiên."""
    resolution_note: str = Field(
        ..., min_length=5, max_length=500,
        description="Ghi chú lý do xử lý — bắt buộc để đảm bảo audit trail.",
    )


# ============================================================
# Response schemas
# ============================================================

class ReconciliationItemResponse(BaseModel):
    """Chi tiết một discrepancy item."""
    item_id: str
    run_id: str
    txn_id: Optional[str] = None
    item_type: str
    txn_status: Optional[str] = None
    txn_amount: Optional[Decimal] = None
    txn_created_at: Optional[datetime] = None
    minutes_pending: Optional[int] = None
    status: str
    resolution_note: Optional[str] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReconciliationRunResponse(BaseModel):
    """Summary của một phiên đối soát — không kèm items."""
    run_id: str
    period_start: datetime
    period_end: datetime
    pending_timeout_minutes: int
    status: str
    total_txn_count: Optional[int] = None
    matched_count: Optional[int] = None
    discrepancy_count: Optional[int] = None
    total_amount: Optional[Decimal] = None
    error_message: Optional[str] = None
    triggered_by: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReconciliationDetailResponse(ReconciliationRunResponse):
    """
    Chi tiết đầy đủ một phiên đối soát, kèm danh sách discrepancy items.
    Dùng cho GET /reconciliation/{run_id}.
    """
    items: List[ReconciliationItemResponse] = Field(default=[])
