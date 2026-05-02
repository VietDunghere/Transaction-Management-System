from __future__ import annotations
"""
Pydantic schemas: Case (ERD v2)
Removed: CaseActionResponse, currency_code, source_ip from transaction summaries.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.common import CaseDecision, CaseStatus


class CaseAssignRequest(BaseModel):
    reviewer_user_id: str = Field(..., description="user_id của REVIEWER được giao case")


class CaseDecideRequest(BaseModel):
    decision: CaseDecision
    decision_note: str = Field(..., min_length=10, max_length=2000)
    version: int = Field(..., ge=1)


class CaseListFilter(BaseModel):
    case_status: Optional[CaseStatus] = None
    assigned_to: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class CaseRuleHit(BaseModel):
    rule_code: str
    rule_name: Optional[str]
    hit_value: Optional[str]
    severity: Optional[str]

    model_config = {"from_attributes": True}


class CardVelocitySnapshot(BaseModel):
    avg_daily_txn: float
    total_txn: int
    avg_amt: float
    std_amt: float


class RecentTransaction(BaseModel):
    txn_id: str
    amount: Decimal
    merchant_name: Optional[str]
    status: str
    fraud_score: Optional[float]
    txn_time: datetime


class CaseTransactionSummary(BaseModel):
    txn_id: str
    amount: Decimal
    txn_time: datetime
    fraud_score: Optional[float]
    merchant_name: Optional[str]
    merchant_category: Optional[str]
    merchant_risk_level: Optional[str]
    customer_name: Optional[str]
    channel_name: Optional[str]
    card_number_masked: Optional[str]
    rule_hits: list[CaseRuleHit] = []
    card_velocity: Optional[CardVelocitySnapshot] = None
    recent_transactions: list[RecentTransaction] = []

    model_config = {"from_attributes": True}


class CaseResponse(BaseModel):
    case_id: str
    txn_id: str
    case_status: CaseStatus
    assigned_to: Optional[str]
    assigned_to_name: Optional[str] = None
    decision: Optional[str]
    decision_note: Optional[str]
    version: int
    created_at: datetime
    decided_at: Optional[datetime]
    transaction: Optional[CaseTransactionSummary] = None

    model_config = {"from_attributes": True}


class CaseListItem(BaseModel):
    case_id: str
    txn_id: str
    case_status: CaseStatus
    assigned_to: Optional[str]
    assigned_to_name: Optional[str] = None
    fraud_score: Optional[float]
    amount: Optional[Decimal]
    txn_time: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}
