from __future__ import annotations
"""
Pydantic schemas: Transaction (ERD v2)
Removed: currency_code, source_ip, reason_code, override_reason, TxnStateHistoryItem.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import TransactionStatus


class TransactionSubmitRequest(BaseModel):
    card_number: str = Field(..., min_length=13, max_length=19, examples=["4111111111111111"])
    customer_id: str = Field(..., description="UUID của customer trong hệ thống")
    merchant_id: str = Field(..., description="UUID của merchant trong hệ thống")
    channel_id: int = Field(..., description="ID kênh giao dịch (POS, ATM, Online)")
    amount: Decimal = Field(..., gt=0, decimal_places=2, examples=[150.50])
    txn_time: datetime = Field(..., description="Thời gian giao dịch theo local timezone")
    idempotency_key: Optional[str] = Field(None, max_length=100)

    @field_validator("card_number")
    @classmethod
    def validate_card_number(cls, v: str) -> str:
        cleaned = v.replace(" ", "").replace("-", "")
        if not cleaned.isdigit():
            raise ValueError("Số thẻ chỉ được chứa chữ số.")
        return cleaned

    @field_validator("txn_time")
    @classmethod
    def validate_txn_time(cls, v: datetime) -> datetime:
        now = datetime.now(timezone.utc)
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        from datetime import timedelta
        if v > now + timedelta(minutes=5):
            raise ValueError("txn_time không được nằm trong tương lai.")
        return v


class TransactionListFilter(BaseModel):
    status: Optional[TransactionStatus] = None
    customer_id: Optional[str] = None
    merchant_id: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class FraudScoreDetail(BaseModel):
    fraud_score: float
    decision: str
    reject_threshold: float
    review_threshold: float
    model_version: str
    top_risk_factors: List[str] = Field(default=[])


class TransactionResponse(BaseModel):
    txn_id: str
    customer_id: str
    customer_name: Optional[str] = None
    merchant_id: str
    merchant_name: Optional[str] = None
    channel_id: int
    submitted_by: str
    card_number_masked: Optional[str]
    amount: Decimal
    txn_time: datetime
    status: TransactionStatus
    fraud_score: Optional[float]
    model_version: Optional[str] = None
    created_at: datetime
    fraud_detail: Optional[FraudScoreDetail] = None

    model_config = {"from_attributes": True}


class TransactionSubmitResponse(BaseModel):
    txn_id: str
    status: TransactionStatus
    fraud_score: Optional[float]
    decision: str
    amount: Decimal
    created_at: datetime
    message: str
    case_id: Optional[str] = Field(None, description="Không null nếu MANUAL_REVIEW")
