from __future__ import annotations
"""
Pydantic schemas: Dashboard & Reports
Response cho analytics endpoints — read-only, tổng hợp từ nhiều bảng.
"""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ============================================================
# Dashboard Summary
# ============================================================

class TransactionStats(BaseModel):
    """Tổng quan giao dịch — counts theo status và theo thời gian."""
    total: int          = Field(description="Tổng số giao dịch")
    approved: int       = Field(description="Số giao dịch APPROVED")
    rejected: int       = Field(description="Số giao dịch REJECTED")
    manual_review: int  = Field(description="Số giao dịch MANUAL_REVIEW")
    pending: int        = Field(description="Số giao dịch PENDING")
    today: int          = Field(description="Giao dịch tạo trong ngày hôm nay (UTC)")
    this_week: int      = Field(description="Giao dịch tạo trong tuần này (từ thứ Hai UTC)")


class FraudStats(BaseModel):
    """Thống kê fraud detection."""
    avg_fraud_score: Optional[float] = Field(
        None, description="Điểm fraud trung bình (0.0→1.0). Null nếu chưa có giao dịch."
    )
    rejection_rate: float = Field(
        description="Tỷ lệ REJECTED / tổng (0.0→1.0). 0.0 nếu chưa có giao dịch."
    )
    manual_review_rate: float = Field(
        description="Tỷ lệ MANUAL_REVIEW / tổng. 0.0 nếu chưa có giao dịch."
    )


class CaseStats(BaseModel):
    """Tổng quan manual review cases."""
    total_open: int      = Field(description="Số case chưa được nhận (OPEN)")
    total_assigned: int  = Field(description="Số case đang xử lý (ASSIGNED)")
    decided_today: int   = Field(description="Số case đã quyết định hôm nay (UTC)")


class LoanStats(BaseModel):
    """Tổng quan khoản vay."""
    total_pending: int   = Field(description="Số đơn vay chờ duyệt")
    total_approved: int  = Field(description="Số khoản vay đã duyệt")
    total_rejected: int  = Field(description="Số đơn vay bị từ chối")


class DashboardSummary(BaseModel):
    """
    Toàn bộ dashboard summary — tổng hợp từ 4 domain.
    Dành cho MANAGER/ADMIN xem tổng quan hệ thống.
    """
    transactions: TransactionStats
    fraud: FraudStats
    cases: CaseStats
    loans: LoanStats
    as_of: datetime = Field(description="Thời điểm tính toán (UTC)")


# ============================================================
# Fraud Trend
# ============================================================

class FraudTrendPoint(BaseModel):
    """Một điểm dữ liệu trong biểu đồ fraud trend."""
    period_label: str   = Field(description="Nhãn hiển thị, VD: '2024-01-15'")
    period_start: date  = Field(description="Ngày bắt đầu kỳ")
    total_txn: int
    approved: int
    rejected: int
    manual_review: int
    fraud_rate: float   = Field(
        description="Tỷ lệ giao dịch REJECTED trong kỳ (0.0→1.0). 0.0 nếu total_txn=0."
    )


class FraudTrendResponse(BaseModel):
    """
    Biểu đồ trend giao dịch theo thời gian.
    Trả về danh sách các điểm dữ liệu sắp xếp theo ngày tăng dần.
    """
    period: str         = Field(description="Độ phân giải: 'daily'")
    lookback_days: int  = Field(description="Số ngày nhìn lại")
    data: List[FraudTrendPoint]
    as_of: datetime     = Field(description="Thời điểm tính toán (UTC)")
