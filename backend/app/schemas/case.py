from __future__ import annotations
from typing import Optional, List, Dict, Any
"""
Pydantic schemas: Case (Manual Review)
Request/Response cho quản lý case review.
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.common import CaseDecision, CaseStatus


# ============================================================
# Request schemas
# ============================================================

class CaseAssignRequest(BaseModel):
    """MANAGER giao case cho một REVIEWER cụ thể."""
    reviewer_user_id: str = Field(..., description="user_id của REVIEWER được giao case")


class CaseDecideRequest(BaseModel):
    """REVIEWER ra quyết định cho case."""
    decision: CaseDecision = Field(..., description="APPROVE hoặc REJECT")
    decision_note: str = Field(..., min_length=10, max_length=2000,
                               description="Ghi chú lý do quyết định (bắt buộc)")
    # Optimistic locking — client gửi lên version hiện tại, server verify
    version: int = Field(..., ge=1, description="Version hiện tại của case (optimistic lock)")


class CaseListFilter(BaseModel):
    """Query params cho list cases."""
    case_status: Optional[CaseStatus] = None
    assigned_to: Optional[str] = Field(None, description="Lọc theo reviewer user_id")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


# ============================================================
# Response schemas
# ============================================================

class CaseTransactionSummary(BaseModel):
    """Tóm tắt giao dịch đính kèm trong case — reviewer cần thấy ngay."""
    txn_id: str
    amount: Decimal
    currency_code: str
    txn_time: datetime
    fraud_score: Optional[float]
    merchant_name: Optional[str]
    merchant_category: Optional[str]
    customer_name: Optional[str]

    model_config = {"from_attributes": True}


class CaseActionResponse(BaseModel):
    """Một action trong lịch sử case."""
    action_id: str
    action_type: str
    actor_user_id: str
    action_note: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class CaseResponse(BaseModel):
    """Response chi tiết 1 case."""
    case_id: str
    txn_id: str
    case_status: CaseStatus
    assigned_to: Optional[str]
    decision: Optional[str]
    decision_note: Optional[str]
    version: int
    created_at: datetime
    decided_at: Optional[datetime]
    # Thông tin giao dịch để reviewer ra quyết định
    transaction: Optional[CaseTransactionSummary] = None
    actions: List[CaseActionResponse] = []

    model_config = {"from_attributes": True}


class CaseListItem(BaseModel):
    """Item tóm tắt trong danh sách cases — chỉ cần thông tin đủ để hiển thị hàng."""
    case_id: str
    txn_id: str
    case_status: CaseStatus
    assigned_to: Optional[str]
    fraud_score: Optional[float]
    amount: Optional[Decimal]
    txn_time: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}
