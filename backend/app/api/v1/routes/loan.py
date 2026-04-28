from __future__ import annotations
"""
Router: Loans
POST   /loans                    — tạo đơn vay (OPERATOR)
GET    /loans                    — danh sách khoản vay (OPERATOR, REVIEWER)
POST   /loans/simulate           — AI PD Score simulation (OPERATOR, REVIEWER)
GET    /loans/{loan_id}          — chi tiết khoản vay (OPERATOR, REVIEWER)
PATCH  /loans/{loan_id}/decision — phê duyệt / từ chối (REVIEWER)
"""

import math
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps import require_roles
from app.db.deps import DbSession
from app.schemas.auth import TokenPayload
from app.schemas.common import LoanStatus, PagedResponse
from app.models.loan import Loan
from app.schemas.loan import (
    CustomerLoanStats,
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


def _build_loan_response(loan, db) -> LoanResponse:
    """Build LoanResponse enriched with customer info and loan history stats."""
    resp = LoanResponse.model_validate(loan)

    if loan.customer:
        c = loan.customer
        resp.customer_name = c.full_name
        resp.customer_job = c.job
        resp.customer_kyc_status = c.kyc_status
        resp.customer_income_level = c.income_level

    if loan.reviewer:
        resp.reviewer_name = loan.reviewer.full_name

    # Loan history for this customer (exclude current loan)
    all_loans = (
        db.query(Loan.status)
        .filter(Loan.customer_id == loan.customer_id, Loan.loan_id != loan.loan_id)
        .all()
    )
    stats = CustomerLoanStats(
        total_loans=len(all_loans),
        approved=sum(1 for r in all_loans if r.status == "APPROVED"),
        rejected=sum(1 for r in all_loans if r.status == "REJECTED"),
        active=sum(1 for r in all_loans if r.status in ("PENDING", "SCORING", "MANUAL_REVIEW")),
    )
    resp.customer_loan_stats = stats

    return resp


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
    description="Lấy danh sách khoản vay với filter theo customer, trạng thái.",
)
def list_loans(
    db: DbSession,
    token: TokenPayload = Depends(require_roles("OPERATOR", "REVIEWER")),
    customer_id: Optional[str] = Query(None, description="Lọc theo customer UUID"),
    status: Optional[LoanStatus] = Query(None, description="Lọc theo trạng thái"),
    period: Optional[str] = Query(None, description="D=1 ngày, W=7 ngày, M=30 ngày"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100, alias="limit"),
) -> PagedResponse[LoanListItem]:
    svc = LoanService(db)

    _period_days = {"D": 1, "W": 7, "M": 30}
    created_from = (
        datetime.now(timezone.utc) - timedelta(days=_period_days[period])
        if period and period in _period_days else None
    )

    items, total = svc.list_loans(
        customer_id=customer_id,
        submitted_by=None,
        status=status,
        created_from=created_from,
        page=page,
        page_size=limit,
    )
    list_data = []
    for loan in items:
        item = LoanListItem.model_validate(loan)
        item.customer_name = loan.customer.full_name if loan.customer else None
        list_data.append(item)

    return PagedResponse(
        data=list_data,
        total=total,
        page=page,
        limit=limit,
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
    token: TokenPayload = Depends(require_roles("OPERATOR", "REVIEWER")),
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
    token: TokenPayload = Depends(require_roles("OPERATOR", "REVIEWER")),
) -> LoanResponse:
    svc = LoanService(db)
    loan = svc.get_loan(loan_id)

    return _build_loan_response(loan, db)


@router.patch(
    "/{loan_id}/decision",
    response_model=LoanResponse,
    summary="Phê duyệt / Từ chối khoản vay",
    description=(
        "REVIEWER đưa ra quyết định APPROVE hoặc REJECT cho khoản vay. "
        "Yêu cầu cung cấp version hiện tại để tránh lost update (optimistic locking). "
        "Khi APPROVE: hệ thống tự tính monthly_payment, outstanding_balance và maturity_date."
    ),
)
def decide_loan(
    loan_id: str,
    body: LoanDecisionRequest,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("REVIEWER")),
) -> LoanResponse:
    svc = LoanService(db)
    loan = svc.decide(loan_id, body, actor_user_id=token.sub)
    return _build_loan_response(loan, db)
