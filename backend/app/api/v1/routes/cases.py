from __future__ import annotations
"""
Router: Cases (Manual Review)
GET  /cases              — danh sách case (REVIEWER, MANAGER)
GET  /cases/{id}         — chi tiết case (REVIEWER, MANAGER)
POST /cases/{id}/assign  — REVIEWER tự nhận case (self-assign)
POST /cases/{id}/decide  — quyết định (REVIEWER, MANAGER)
"""

import math
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps import require_roles
from app.core.exceptions import PermissionDeniedError
from app.db.deps import DbSession
from app.schemas.auth import TokenPayload
from app.schemas.case import (
    CaseDecideRequest,
    CaseListItem,
    CaseResponse,
    CaseTransactionSummary,
)
from app.schemas.common import CaseStatus, PagedResponse, PaginationMeta
from app.services.case_service import CaseService

router = APIRouter(prefix="/cases", tags=["Cases"])


@router.get(
    "",
    response_model=PagedResponse[CaseListItem],
    summary="Danh sách cases",
    description="Lấy queue cases cần xử lý. REVIEWER thấy cases của mình. MANAGER thấy tất cả.",
)
def list_cases(
    db: DbSession,
    token: TokenPayload = Depends(require_roles("REVIEWER", "MANAGER")),
    case_status: Optional[CaseStatus] = Query(None),
    assigned_to: Optional[str] = Query(None, description="Lọc theo reviewer user_id"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> PagedResponse[CaseListItem]:
    svc = CaseService(db)

    # REVIEWER có thể thấy:
    #   - Tất cả OPEN cases (queue chưa ai nhận — để self-assign)
    #   - Cases được assign cho chính mình
    # Không cho phép REVIEWER lọc theo reviewer khác.
    # Chi tiết từng case bị giới hạn thêm ở get_case().
    is_reviewer_only = (
        "REVIEWER" in token.roles
        and "MANAGER" not in token.roles
    )

    if is_reviewer_only and assigned_to is not None and assigned_to != token.sub:
        raise PermissionDeniedError("Bạn không thể lọc theo reviewer khác.")

    # REVIEWER thấy: tất cả OPEN cases (queue chưa ai nhận) + cases của mình.
    # Dùng reviewer_queue_for thay vì assigned_to để repo tạo compound OR query.
    reviewer_queue_for = token.sub if is_reviewer_only else None

    items, total = svc.list_cases(
        case_status=case_status,
        assigned_to=assigned_to if not is_reviewer_only else None,
        reviewer_queue_for=reviewer_queue_for,
        page=page,
        page_size=limit,
    )

    list_data = []
    for case in items:
        txn = case.transaction
        list_data.append(CaseListItem(
            case_id=case.case_id,
            txn_id=case.txn_id,
            case_status=case.case_status,
            assigned_to=case.assigned_to,
            fraud_score=float(txn.fraud_score) if txn and txn.fraud_score else None,
            amount=txn.amount if txn else None,
            txn_time=txn.txn_time if txn else None,
            created_at=case.created_at,
        ))

    return PagedResponse(
        data=list_data,
        pagination=PaginationMeta(
            page=page,
            page_size=limit,
            total_items=total,
            total_pages=math.ceil(total / limit) if total > 0 else 0,
        ),
    )


@router.get(
    "/{case_id}",
    response_model=CaseResponse,
    summary="Chi tiết case",
    description="Lấy full thông tin case kèm giao dịch và lịch sử actions.",
)
def get_case(
    case_id: str,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("REVIEWER", "MANAGER")),
) -> CaseResponse:
    svc = CaseService(db)
    case = svc.get_case(case_id)

    # REVIEWER chỉ được xem case được giao cho mình
    is_reviewer_only = (
        "REVIEWER" in token.roles
        and "MANAGER" not in token.roles
    )
    if is_reviewer_only and case.assigned_to != token.sub:
        raise PermissionDeniedError("Case này không được giao cho bạn.")

    txn_summary = None
    if case.transaction:
        t = case.transaction
        txn_summary = CaseTransactionSummary(
            txn_id=t.txn_id,
            amount=t.amount,
            currency_code=t.currency_code,
            txn_time=t.txn_time,
            fraud_score=float(t.fraud_score) if t.fraud_score else None,
            merchant_name=t.merchant.merchant_name if t.merchant else None,
            merchant_category=t.merchant.merchant_category if t.merchant else None,
            customer_name=t.customer.full_name if t.customer else None,
        )

    return CaseResponse(
        case_id=case.case_id,
        txn_id=case.txn_id,
        case_status=case.case_status,
        assigned_to=case.assigned_to,
        decision=case.decision,
        decision_note=case.decision_note,
        version=case.version,
        created_at=case.created_at,
        decided_at=case.decided_at,
        transaction=txn_summary,
        actions=[a for a in case.actions] if case.actions else [],
    )


@router.post(
    "/{case_id}/assign",
    response_model=CaseResponse,
    summary="Nhận case về xử lý",
    description=(
        "REVIEWER tự nhận case về xử lý. "
        "Có constraint Transaction Locking (WHERE assigned_to IS NULL) để chặn race condition."
    ),
)
def assign_case(
    case_id: str,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("REVIEWER")),
) -> CaseResponse:
    svc = CaseService(db)
    svc.self_assign(case_id, reviewer_user_id=token.sub)
    return get_case(case_id, db, token)


@router.patch(
    "/{case_id}/decision",
    response_model=CaseResponse,
    summary="Duyệt/Từ chối case",
    description=(
        "REVIEWER đưa ra quyết định APPROVED/REJECTED cho case. "
        "Yêu cầu cung cấp version hiện tại để tránh lost update (optimistic locking). "
        "Gộp Approve & Reject vào 1 endpoint."
    ),
)
def decide_case(
    case_id: str,
    body: CaseDecideRequest,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("REVIEWER", "MANAGER")),
) -> CaseResponse:
    svc = CaseService(db)
    svc.decide(case_id, body, actor_user_id=token.sub, actor_roles=token.roles)
    return get_case(case_id, db, token)
