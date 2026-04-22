from __future__ import annotations
"""
Router: Dashboard
GET /dashboard/summary       — tổng quan hệ thống (MANAGER, ANALYST)
GET /dashboard/fraud-trend   — biểu đồ trend giao dịch theo ngày (MANAGER, ANALYST)

Tất cả endpoints đều read-only, chỉ MANAGER và ANALYST mới truy cập được.
"""

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps import require_roles
from app.db.deps import DbSession
from app.schemas.auth import TokenPayload
from app.schemas.dashboard import DashboardSummary, FraudTrendResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummary,
    summary="Tổng quan hệ thống",
    description=(
        "Trả về tổng quan real-time của toàn bộ hệ thống: "
        "số lượng giao dịch theo status, tỷ lệ fraud, "
        "queue cases đang chờ, và thống kê khoản vay. "
        "Tính toán trực tiếp từ DB — không cache."
    ),
)
def get_dashboard_summary(
    db: DbSession,
    token: TokenPayload = Depends(require_roles("MANAGER", "ANALYST")),
) -> DashboardSummary:
    svc = DashboardService(db)
    return svc.get_summary()


@router.get(
    "/fraud-trend",
    response_model=FraudTrendResponse,
    summary="Biểu đồ fraud trend theo ngày",
    description=(
        "Trả về time-series phân tích giao dịch theo ngày trong N ngày gần nhất. "
        "Mỗi điểm dữ liệu gồm: total_txn, approved, rejected, manual_review, fraud_rate. "
        "Zero-fill cho những ngày không có giao dịch. "
        "Dùng cho biểu đồ line chart trên dashboard."
    ),
)
def get_fraud_trend(
    db: DbSession,
    token: TokenPayload = Depends(require_roles("MANAGER", "ANALYST")),
    days: int = Query(
        default=30,
        ge=1,
        le=90,
        description="Số ngày nhìn lại (1–90). Mặc định 30 ngày.",
    ),
) -> FraudTrendResponse:
    svc = DashboardService(db)
    return svc.get_fraud_trend(lookback_days=days)
