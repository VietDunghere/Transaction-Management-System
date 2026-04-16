from __future__ import annotations
from typing import Optional, List, Dict, Any
"""
Pydantic schemas: Transaction
Request/Response cho submit và query giao dịch.
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import TransactionStatus


# ============================================================
# Request schemas
# ============================================================

class TransactionSubmitRequest(BaseModel):
    """
    Request body khi OPERATOR gửi giao dịch mới.
    Các trường này là thông tin thô từ terminal POS/gateway.
    """
    # Số thẻ — chỉ nhận, sẽ hash trước khi lưu
    card_number: str = Field(..., min_length=13, max_length=19, examples=["4111111111111111"])
    customer_id: str = Field(..., description="UUID của customer trong hệ thống")
    merchant_id: str = Field(..., description="UUID của merchant trong hệ thống")
    channel_id: int = Field(..., description="ID kênh giao dịch (POS, ATM, Online)")
    amount: Decimal = Field(..., gt=0, decimal_places=2, examples=[150.50])
    currency_code: str = Field(default="USD", max_length=10)
    txn_time: datetime = Field(..., description="Thời gian giao dịch theo local timezone")
    source_ip: Optional[str] = Field(None, max_length=64)
    # Idempotency key — client tự tạo (UUID), phòng retry trùng
    idempotency_key: Optional[str] = Field(None, max_length=100)

    @field_validator("card_number")
    @classmethod
    def validate_card_number(cls, v: str) -> str:
        """Chỉ cho phép số — loại bỏ khoảng trắng và dấu gạch."""
        cleaned = v.replace(" ", "").replace("-", "")
        if not cleaned.isdigit():
            raise ValueError("Số thẻ chỉ được chứa chữ số.")
        return cleaned


class TransactionListFilter(BaseModel):
    """Query params cho list transactions."""
    status: Optional[TransactionStatus] = None
    customer_id: Optional[str] = None
    merchant_id: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


# ============================================================
# Response schemas
# ============================================================

class FraudScoreDetail(BaseModel):
    """Chi tiết kết quả chấm điểm fraud detection."""
    fraud_score: float = Field(description="Xác suất gian lận (0.0 → 1.0)")
    decision: str = Field(description="APPROVED | MANUAL_REVIEW | REJECTED")
    reject_threshold: float
    review_threshold: float
    model_version: str
    top_risk_factors: List[str] = Field(default=[], description="Features ảnh hưởng nhiều nhất")


class TransactionResponse(BaseModel):
    """Response chi tiết 1 giao dịch."""
    txn_id: str
    customer_id: str
    merchant_id: str
    channel_id: int
    card_number_masked: Optional[str]
    amount: Decimal
    currency_code: str
    txn_time: datetime
    status: TransactionStatus
    fraud_score: Optional[float]
    reason_code: Optional[str]
    created_at: datetime
    # Đính kèm fraud detail khi có
    fraud_detail: Optional[FraudScoreDetail] = None

    model_config = {"from_attributes": True}


class TransactionSubmitResponse(BaseModel):
    """Response sau khi submit giao dịch — trả ngay kết quả AI."""
    txn_id: str
    status: TransactionStatus
    fraud_score: Optional[float]
    decision: str
    message: str
    case_id: Optional[str] = Field(None, description="Không null nếu MANUAL_REVIEW")


class TxnStateHistoryItem(BaseModel):
    """Một bước thay đổi trạng thái trong audit trail của giao dịch."""
    state_hist_id: str
    txn_id: str
    old_status: Optional[str] = None
    new_status: str
    changed_by_user_id: Optional[str] = None
    changed_at: datetime
    change_reason: Optional[str] = None

    model_config = {"from_attributes": True}
