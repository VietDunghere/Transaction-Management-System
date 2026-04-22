from __future__ import annotations
"""
Schemas: Analyst module
- ThresholdResponse / ThresholdUpdateRequest
- SuppressionRuleResponse / SuppressionRuleCreateRequest
- ModelPerformanceResponse (fraud + loan)
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ================================================================
# Threshold schemas
# ================================================================

class ThresholdItem(BaseModel):
    model_name: str
    param_name: str
    param_value: float
    description: Optional[str] = None
    updated_by: Optional[str] = None
    updated_at: datetime
    version: int

    model_config = {"from_attributes": True}


class ThresholdUpdateItem(BaseModel):
    model_name: str = Field(..., pattern="^(fraud|loan)$")
    param_name: str = Field(..., min_length=1)
    param_value: float = Field(..., gt=0.0, lt=1.0)

    @field_validator("param_name")
    @classmethod
    def validate_param_name(cls, v: str, info) -> str:
        valid = {
            "fraud": {"reject_threshold", "review_threshold"},
            "loan": {"high_risk_threshold", "medium_risk_threshold"},
        }
        model = info.data.get("model_name")
        if model and v not in valid.get(model, set()):
            raise ValueError(f"param_name không hợp lệ cho model '{model}'")
        return v


class ThresholdUpdateRequest(BaseModel):
    updates: list[ThresholdUpdateItem] = Field(..., min_length=1)


class ThresholdListResponse(BaseModel):
    fraud: list[ThresholdItem]
    loan: list[ThresholdItem]


# ================================================================
# Suppression rule schemas
# ================================================================

class SuppressionRuleResponse(BaseModel):
    rule_id: str
    rule_type: str
    entity_id: str
    reason: str
    created_by: str
    expires_at: Optional[datetime] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class SuppressionRuleCreateRequest(BaseModel):
    rule_type: str = Field(..., pattern="^(MERCHANT|CUSTOMER|CARD_HASH)$")
    entity_id: str = Field(..., min_length=1, max_length=255)
    reason: str = Field(..., min_length=5, max_length=1000)
    expires_at: Optional[datetime] = None


# ================================================================
# Model performance schemas
# ================================================================

class FraudScoreDistribution(BaseModel):
    approved_count: int       # fraud_score < review_threshold
    review_count: int         # review_threshold <= fraud_score < reject_threshold
    rejected_count: int       # fraud_score >= reject_threshold
    total: int
    approved_rate: float
    review_rate: float
    rejected_rate: float
    false_positive_count: int  # MANUAL_REVIEW case → reviewer quyết APPROVED (model over-flagged)
    false_positive_rate: float


class LoanRiskDistribution(BaseModel):
    low_risk_count: int
    medium_risk_count: int
    high_risk_count: int
    total: int
    low_risk_rate: float
    medium_risk_rate: float
    high_risk_rate: float
    approved_count: int
    rejected_count: int
    pending_count: int


class FraudModelPerformanceResponse(BaseModel):
    period_days: int
    score_distribution: FraudScoreDistribution
    current_thresholds: dict[str, float]


class LoanModelPerformanceResponse(BaseModel):
    period_days: int
    risk_distribution: LoanRiskDistribution
    current_thresholds: dict[str, float]


# ================================================================
# Analyst report schemas
# ================================================================

VALID_REPORT_TYPES = {
    "FRAUD_ANALYSIS",
    "LOAN_ANALYSIS",
    "THRESHOLD_RECOMMENDATION",
    "SUPPRESSION_REVIEW",
    "GENERAL",
}


class AnalystReportCreateRequest(BaseModel):
    title: str = Field(..., min_length=5, max_length=255)
    report_type: str = Field(..., description="FRAUD_ANALYSIS | LOAN_ANALYSIS | THRESHOLD_RECOMMENDATION | SUPPRESSION_REVIEW | GENERAL")
    content_md: str = Field(..., min_length=20, description="Nội dung báo cáo định dạng Markdown")

    @field_validator("report_type")
    @classmethod
    def validate_report_type(cls, v: str) -> str:
        if v not in VALID_REPORT_TYPES:
            raise ValueError(f"report_type phải là một trong: {', '.join(sorted(VALID_REPORT_TYPES))}")
        return v


class AnalystReportAcknowledgeRequest(BaseModel):
    note: Optional[str] = Field(None, max_length=1000, description="Ghi chú phản hồi của MANAGER")


class AnalystReportResponse(BaseModel):
    report_id: str
    title: str
    report_type: str
    content_md: str
    status: str
    submitted_by: str
    submitted_at: datetime
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    note: Optional[str] = None

    model_config = {"from_attributes": True}


class AnalystReportSummary(BaseModel):
    """Trả về trong list — không bao gồm content_md để tránh payload lớn."""
    report_id: str
    title: str
    report_type: str
    status: str
    submitted_by: str
    submitted_at: datetime
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
