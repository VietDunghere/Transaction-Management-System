from __future__ import annotations
"""
Router: Analyst
GET  /analyst/thresholds                  — xem tất cả threshold hiện tại (ANALYST, MANAGER, ADMIN)
PATCH /analyst/thresholds                 — cập nhật threshold (ANALYST, ADMIN)
GET  /analyst/model-performance/fraud     — thống kê fraud model (ANALYST, MANAGER, ADMIN)
GET  /analyst/model-performance/loan      — thống kê loan model (ANALYST, MANAGER, ADMIN)
GET  /analyst/suppression-rules           — danh sách suppression rules (ANALYST, ADMIN)
POST /analyst/suppression-rules           — tạo suppression rule (ANALYST)
PATCH /analyst/suppression-rules/{id}     — vô hiệu hóa rule (ANALYST, ADMIN)
"""

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps import require_roles
from app.db.deps import DbSession
from app.schemas.analyst import (
    FraudModelPerformanceResponse,
    LoanModelPerformanceResponse,
    SuppressionRuleCreateRequest,
    SuppressionRuleResponse,
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


@router.get(
    "/suppression-rules",
    response_model=list[SuppressionRuleResponse],
    summary="Danh sách suppression rules",
)
def list_suppression_rules(
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ANALYST", "ADMIN")),
    include_inactive: bool = Query(default=False, description="Bao gồm rule đã vô hiệu hóa"),
) -> list[SuppressionRuleResponse]:
    return AnalystService(db).list_suppression_rules(include_inactive=include_inactive)


@router.post(
    "/suppression-rules",
    response_model=SuppressionRuleResponse,
    status_code=201,
    summary="Tạo suppression rule mới",
    description="Tạo rule bypass fraud scoring cho merchant/customer/card cụ thể. Ghi audit log.",
)
def create_suppression_rule(
    body: SuppressionRuleCreateRequest,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ANALYST")),
) -> SuppressionRuleResponse:
    return AnalystService(db).create_suppression_rule(body, actor_user_id=token.sub)


@router.patch(
    "/suppression-rules/{rule_id}",
    response_model=SuppressionRuleResponse,
    summary="Vô hiệu hóa suppression rule",
)
def deactivate_suppression_rule(
    rule_id: str,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ANALYST", "ADMIN")),
) -> SuppressionRuleResponse:
    return AnalystService(db).deactivate_suppression_rule(rule_id, actor_user_id=token.sub)
