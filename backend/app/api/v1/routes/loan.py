from __future__ import annotations
"""
Router: Loans
POST   /loans                    — tạo đơn vay (OPERATOR)
GET    /loans                    — danh sách khoản vay (role-based)
POST   /loans/simulate           — AI PD Score simulation (any role)
GET    /loans/{loan_id}          — chi tiết khoản vay
PATCH  /loans/{loan_id}/decision — phê duyệt / từ chối (MANAGER, ADMIN)
"""

import math
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps import require_roles
from app.core.exceptions import PermissionDeniedError
from app.db.deps import DbSession
from app.schemas.auth import TokenPayload
from app.schemas.common import LoanStatus, PagedResponse, PaginationMeta
from app.schemas.loan import (
    LoanApplyRequest,
    LoanDecisionRequest,
    LoanListItem,
    LoanResponse,
    LoanSimulationRequest,
    LoanSimulationResponse,
)
from app.services.loan_service import LoanService
from app.services.loan_scoring_service import LoanScoringService, LoanSimulationInput

router = APIRouter(prefix="/loans", tags=["Loans"])


@router.post(
    "",
    response_model=LoanResponse,
    status_code=201,
    summary="Tạo đơn vay mới",
    description=(
        "Chỉ OPERATOR (= core banking system của ngân hàng) được phép tạo đơn vay. "
        "Khoản vay được tạo ở trạng thái PENDING — chờ MANAGER phê duyệt. "
        "Customer phải tồn tại trong hệ thống."
    ),
)
def apply_loan(
    body: LoanApplyRequest,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("OPERATOR")),
) -> LoanResponse:
    svc = LoanService(db)
    loan = svc.apply(body, submitted_by_user_id=token.sub)
    return LoanResponse.model_validate(loan)


@router.get(
    "",
    response_model=PagedResponse[LoanListItem],
    summary="Danh sách khoản vay",
    description=(
        "Lấy danh sách khoản vay với filter. "
        "OPERATOR chỉ thấy khoản vay do mình tạo. "
        "MANAGER và ADMIN thấy tất cả."
    ),
)
def list_loans(
    db: DbSession,
    token: TokenPayload = Depends(require_roles("OPERATOR", "MANAGER", "ADMIN", "ANALYST")),
    customer_id: Optional[str] = Query(None, description="Lọc theo customer UUID"),
    status: Optional[LoanStatus] = Query(None, description="Lọc theo trạng thái"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100, alias="limit"),
) -> PagedResponse[LoanListItem]:
    svc = LoanService(db)

    # OPERATOR chỉ thấy khoản vay do mình submit
    submitted_by: Optional[str] = None
    if "OPERATOR" in token.roles and "MANAGER" not in token.roles and "ADMIN" not in token.roles:
        submitted_by = token.sub

    items, total = svc.list_loans(
        customer_id=customer_id,
        submitted_by=submitted_by,
        status=status,
        page=page,
        page_size=limit,
    )
    return PagedResponse(
        data=[LoanListItem.model_validate(loan) for loan in items],
        pagination=PaginationMeta(
            page=page,
            page_size=limit,
            total_items=total,
            total_pages=math.ceil(total / limit) if total > 0 else 0,
        ),
    )


# ── /simulate MUST be before /{loan_id} to avoid FastAPI treating
#    "simulate" as a loan_id path parameter ──
@router.post(
    "/simulate",
    response_model=LoanSimulationResponse,
    summary="Mô phỏng Duyệt khoản vay (PD Score AI)",
    description=(
        "Chạy AI Model (XGBoost, Kaggle Dataset) để trả về Xác suất vỡ nợ (PD Score) "
        "và Phân loại rủi ro (Risk Level) trước khi thực sự quyết định khoản vay."
    ),
)
def simulate_loan(
    body: LoanSimulationRequest,
    token: TokenPayload = Depends(require_roles("OPERATOR", "MANAGER", "ADMIN", "ANALYST")),
) -> LoanSimulationResponse:
    scoring_svc = LoanScoringService.get_instance()

    inp = LoanSimulationInput(
        person_age=body.person_age,
        person_income=body.person_income,
        person_home_ownership=body.person_home_ownership,
        person_emp_length=body.person_emp_length,
        loan_intent=body.loan_intent,
        loan_grade=body.loan_grade,
        loan_amnt=body.loan_amnt,
        loan_int_rate=body.loan_int_rate,
        cb_person_default_on_file=body.cb_person_default_on_file,
        cb_person_cred_hist_length=body.cb_person_cred_hist_length,
    )

    out = scoring_svc.simulate(inp)

    return LoanSimulationResponse(
        pd_score=out.pd_score,
        risk_level=out.risk_level,
        top_risk_factors=out.top_risk_factors,
        model_version=out.model_version,
    )


@router.get(
    "/{loan_id}",
    response_model=LoanResponse,
    summary="Chi tiết khoản vay",
    description="Lấy thông tin đầy đủ một khoản vay theo ID.",
)
def get_loan(
    loan_id: str,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("OPERATOR", "MANAGER", "ADMIN", "ANALYST")),
) -> LoanResponse:
    svc = LoanService(db)
    loan = svc.get_loan(loan_id)

    # OPERATOR chỉ được xem khoản vay do mình tạo
    if "OPERATOR" in token.roles and "MANAGER" not in token.roles and "ADMIN" not in token.roles:
        if loan.submitted_by != token.sub:
            raise PermissionDeniedError("Bạn không có quyền xem khoản vay này.")

    return LoanResponse.model_validate(loan)


@router.patch(
    "/{loan_id}/decision",
    response_model=LoanResponse,
    summary="Phê duyệt / Từ chối khoản vay",
    description=(
        "MANAGER hoặc ADMIN đưa ra quyết định APPROVE hoặc REJECT cho khoản vay. "
        "Yêu cầu cung cấp version hiện tại để tránh lost update (optimistic locking). "
        "Khi APPROVE: hệ thống tự tính monthly_payment, outstanding_balance và maturity_date."
    ),
)
def decide_loan(
    loan_id: str,
    body: LoanDecisionRequest,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("MANAGER", "ADMIN")),
) -> LoanResponse:
    svc = LoanService(db)
    loan = svc.decide(loan_id, body, actor_user_id=token.sub)
    return LoanResponse.model_validate(loan)
