from __future__ import annotations
"""
Pydantic schemas: Loan (ERD v2)
Removed: currency_code.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.common import LoanDecision, LoanStatus


class LoanApplyRequest(BaseModel):
    customer_id: str = Field(..., description="UUID của customer trong hệ thống")
    principal_amount: Decimal = Field(..., gt=0, decimal_places=2, examples=[50000.00])
    interest_rate: Decimal = Field(
        ..., ge=0, le=1, decimal_places=4, examples=[0.1200],
        description="Lãi suất hàng năm dạng thập phân (0.0 → 1.0)",
    )
    term_months: int = Field(..., ge=1, le=360, examples=[24])
    purpose: str = Field(..., min_length=10, max_length=200)

    # AI input features
    person_age: Optional[int] = Field(None, ge=18, le=100)
    person_income: Optional[float] = Field(None, ge=1_000, le=10_000_000)
    person_home_ownership: Optional[Literal["RENT", "MORTGAGE", "OWN", "OTHER"]] = None
    person_emp_length: Optional[int] = Field(None, ge=0, le=60)
    loan_intent: Optional[Literal["PERSONAL", "EDUCATION", "MEDICAL", "VENTURE", "HOMEIMPROVEMENT", "DEBTCONSOLIDATION"]] = None
    loan_grade: Optional[Literal["A", "B", "C", "D", "E", "F", "G"]] = None
    cb_person_default_on_file: Optional[Literal["Y", "N"]] = None
    cb_person_cred_hist_length: Optional[int] = Field(None, ge=0, le=60)


class LoanDecisionRequest(BaseModel):
    decision: LoanDecision
    review_note: Optional[str] = Field(None, max_length=500)
    version: int = Field(..., ge=1)


class CustomerLoanStats(BaseModel):
    total_loans: int = 0
    approved: int = 0
    rejected: int = 0
    active: int = 0


class LoanResponse(BaseModel):
    loan_id: str
    customer_id: str
    customer_name: Optional[str] = None
    customer_job: Optional[str] = None
    customer_kyc_status: Optional[str] = None
    customer_income_level: Optional[str] = None
    submitted_by: str
    reviewed_by: Optional[str] = None
    reviewer_name: Optional[str] = None

    principal_amount: Decimal
    interest_rate: Decimal
    term_months: int
    purpose: Optional[str] = None

    status: LoanStatus
    version: int

    monthly_payment: Optional[Decimal] = None
    outstanding_balance: Optional[Decimal] = None
    disbursed_at: Optional[datetime] = None
    maturity_date: Optional[date] = None

    review_note: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime

    pd_score: Optional[float] = None
    risk_level: Optional[str] = None

    person_age: Optional[int] = None
    person_income: Optional[float] = None
    person_home_ownership: Optional[str] = None
    person_emp_length: Optional[int] = None
    loan_grade: Optional[str] = None
    loan_intent: Optional[str] = None
    cb_person_default_on_file: Optional[str] = None
    cb_person_cred_hist_length: Optional[int] = None

    customer_loan_stats: Optional[CustomerLoanStats] = None

    model_config = {"from_attributes": True}


class LoanListItem(BaseModel):
    loan_id: str
    customer_id: str
    customer_name: Optional[str] = None
    submitted_by: str
    principal_amount: Decimal
    interest_rate: Decimal
    term_months: int
    purpose: Optional[str] = None
    status: LoanStatus
    monthly_payment: Optional[Decimal] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    pd_score: Optional[float] = None
    risk_level: Optional[str] = None

    model_config = {"from_attributes": True}


class LoanSimulationRequest(BaseModel):
    person_age: int = Field(..., ge=18, le=100)
    person_income: float = Field(..., ge=1_000, le=10_000_000)
    person_home_ownership: Literal["RENT", "MORTGAGE", "OWN", "OTHER"]
    person_emp_length: int = Field(..., ge=0, le=60)
    loan_intent: Literal["PERSONAL", "EDUCATION", "MEDICAL", "VENTURE", "HOMEIMPROVEMENT", "DEBTCONSOLIDATION"]
    loan_grade: Literal["A", "B", "C", "D", "E", "F", "G"]
    loan_amnt: float = Field(..., gt=100, le=50_000)
    loan_int_rate: float = Field(..., ge=0, le=30)
    cb_person_default_on_file: Literal["Y", "N"]
    cb_person_cred_hist_length: int = Field(..., ge=0, le=60)


class LoanSimulationResponse(BaseModel):
    pd_score: float
    risk_level: str
    top_risk_factors: list[str]
    model_version: str
