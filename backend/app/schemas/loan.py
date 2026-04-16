from __future__ import annotations
"""
Pydantic schemas: Loan
Request/Response cho loan application và approval workflow.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import LoanDecision, LoanStatus


# ============================================================
# Request schemas
# ============================================================

class LoanApplyRequest(BaseModel):
    """
    Request body khi OPERATOR tạo đơn vay cho khách hàng.
    OPERATOR là nhân viên ngân hàng đại diện customer gửi đơn.
    """
    customer_id: str = Field(
        ..., description="UUID của customer trong hệ thống"
    )
    principal_amount: Decimal = Field(
        ..., gt=0, decimal_places=2,
        examples=[50000.00],
        description="Số tiền vay (dương, tối đa 2 chữ số thập phân)",
    )
    currency_code: str = Field(default="USD", max_length=10)
    interest_rate: Decimal = Field(
        ..., ge=0, le=1, decimal_places=4,
        examples=[0.1200],
        description="Lãi suất hàng năm dạng thập phân (0.0 → 1.0). VD: 0.1200 = 12%/năm.",
    )
    term_months: int = Field(
        ..., ge=1, le=360,
        examples=[24],
        description="Thời hạn vay tính bằng tháng (1 → 360)",
    )
    purpose: str = Field(
        ..., min_length=10, max_length=200,
        description="Mục đích vay — tối thiểu 10 ký tự",
    )


class LoanDecisionRequest(BaseModel):
    """
    Request body khi MANAGER phê duyệt hoặc từ chối khoản vay.
    Client phải gửi version hiện tại của loan để đảm bảo optimistic locking —
    nếu version không khớp (MANAGER khác đã sửa), server trả 409 Conflict.
    """
    decision: LoanDecision = Field(
        ..., description="APPROVE hoặc REJECT"
    )
    review_note: Optional[str] = Field(
        None, max_length=500,
        description="Ghi chú của MANAGER — bắt buộc khi REJECT (best practice)",
    )
    version: int = Field(
        ..., ge=1,
        description="Version hiện tại của loan — dùng để tránh lost update",
    )


# ============================================================
# Response schemas
# ============================================================

class LoanResponse(BaseModel):
    """Chi tiết đầy đủ một khoản vay."""
    loan_id: str
    customer_id: str
    submitted_by: str
    reviewed_by: Optional[str] = None

    principal_amount: Decimal
    currency_code: str
    interest_rate: Decimal
    term_months: int
    purpose: Optional[str] = None

    status: LoanStatus
    version: int

    # Populated khi APPROVED
    monthly_payment: Optional[Decimal] = None
    outstanding_balance: Optional[Decimal] = None
    disbursed_at: Optional[datetime] = None
    maturity_date: Optional[date] = None

    review_note: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class LoanListItem(BaseModel):
    """Summary row cho danh sách khoản vay."""
    loan_id: str
    customer_id: str
    submitted_by: str
    principal_amount: Decimal
    currency_code: str
    interest_rate: Decimal
    term_months: int
    purpose: Optional[str] = None
    status: LoanStatus
    monthly_payment: Optional[Decimal] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}
