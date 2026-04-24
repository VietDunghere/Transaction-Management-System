from __future__ import annotations
"""
Router: Analyst
GET  /analyst/thresholds                      — xem tất cả threshold hiện tại (ANALYST, MANAGER, ADMIN)
PATCH /analyst/thresholds                     — cập nhật threshold (ANALYST, ADMIN)
GET  /analyst/model-performance/fraud         — thống kê fraud model (ANALYST, MANAGER, ADMIN)
GET  /analyst/model-performance/loan          — thống kê loan model (ANALYST, MANAGER, ADMIN)
"""

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps import require_roles
from app.db.deps import DbSession
from app.schemas.analyst import (
    FraudModelPerformanceResponse,
    LoanModelPerformanceResponse,
    ThresholdListResponse,
    ThresholdUpdateRequest,
)
from app.schemas.auth import TokenPayload
from app.services.analyst_service import AnalystService

router = APIRouter(prefix="/analyst", tags=["Analyst"])


@router.get(
    "/thresholds",
    response_model=ThresholdListResponse,
    summary="Xem threshold hiện tại của fraud & loan model",
)
def get_thresholds(
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ANALYST", "MANAGER", "ADMIN")),
) -> ThresholdListResponse:
    return AnalystService(db).get_thresholds()


@router.patch(
    "/thresholds",
    response_model=ThresholdListResponse,
    summary="Cập nhật threshold fraud / loan model",
    description="ANALYST hoặc ADMIN có thể điều chỉnh ngưỡng phân loại. Thay đổi ghi vào audit log.",
)
def update_thresholds(
    body: ThresholdUpdateRequest,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ANALYST", "ADMIN")),
) -> ThresholdListResponse:
    return AnalystService(db).update_thresholds(body, actor_user_id=token.sub)


@router.get(
    "/model-performance/fraud",
    response_model=FraudModelPerformanceResponse,
    summary="Thống kê hiệu suất fraud model",
)
def fraud_model_performance(
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ANALYST", "MANAGER", "ADMIN")),
    days: int = Query(default=30, ge=1, le=365, description="Số ngày nhìn lại"),
) -> FraudModelPerformanceResponse:
    return AnalystService(db).get_fraud_performance(days=days)


@router.get(
    "/model-performance/loan",
    response_model=LoanModelPerformanceResponse,
    summary="Thống kê hiệu suất loan model",
)
def loan_model_performance(
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ANALYST", "MANAGER", "ADMIN")),
    days: int = Query(default=30, ge=1, le=365, description="Số ngày nhìn lại"),
) -> LoanModelPerformanceResponse:
    return AnalystService(db).get_loan_performance(days=days)
