from __future__ import annotations
"""
Router: Cases (Manual Review)
GET  /cases              — danh sách case (REVIEWER)
GET  /cases/{id}         — chi tiết case (REVIEWER)
POST /cases/{id}/assign  — REVIEWER tự nhận case (self-assign)
PATCH /cases/{id}/decision — quyết định (REVIEWER)
"""

import math
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps import require_roles
from app.core.exceptions import PermissionDeniedError
from app.db.deps import DbSession
from app.schemas.auth import TokenPayload
from app.schemas.case import (
    CardVelocitySnapshot,
    CaseDecideRequest,
    CaseListItem,
    CaseResponse,
    CaseRuleHit,
    CaseTransactionSummary,
    RecentTransaction,
)
from app.models.card_velocity import CardVelocityStats
from app.models.scoring import RuleHit
from app.models.user import User
from app.schemas.common import CaseStatus, PagedResponse
from app.services.case_service import CaseService

router = APIRouter(prefix="/cases", tags=["Cases"])


def _resolve_user_names(db, user_ids: list[str]) -> dict[str, str]:
    """Batch-resolve user_id → full_name."""
    if not user_ids:
        return {}
    rows = db.query(User.user_id, User.full_name).filter(User.user_id.in_(user_ids)).all()
    return {r.user_id: r.full_name for r in rows}


@router.get(
    "",
    response_model=PagedResponse[CaseListItem],
    summary="Danh sách cases",
    description="Lấy queue cases cần xử lý. REVIEWER thấy cases của mình. MANAGER thấy tất cả.",
)
def list_cases(
    db: DbSession,
    token: TokenPayload = Depends(require_roles("REVIEWER")),
    case_status: Optional[CaseStatus] = Query(None),
    assigned_to: Optional[str] = Query(None, description="Lọc theo reviewer user_id"),
    period: Optional[str] = Query(None, description="D=1 ngày, W=7 ngày, M=30 ngày"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> PagedResponse[CaseListItem]:
    svc = CaseService(db)

    is_reviewer_only = "MANAGER" not in token.roles and "ADMIN" not in token.roles

    # REVIEWER thấy: tất cả OPEN cases (queue chưa ai nhận) + cases của mình.
    if is_reviewer_only and assigned_to is not None and assigned_to != token.sub:
        raise PermissionDeniedError("Bạn không thể lọc theo reviewer khác.")

    reviewer_queue_for = token.sub if is_reviewer_only else None

    _period_days = {"D": 1, "W": 7, "M": 30}
    created_from = (
        datetime.now(timezone.utc) - timedelta(days=_period_days[period])
        if period and period in _period_days else None
    )

    items, total = svc.list_cases(
        case_status=case_status,
        assigned_to=assigned_to if not is_reviewer_only else None,
        reviewer_queue_for=reviewer_queue_for,
        created_from=created_from,
        page=page,
        page_size=limit,
    )

    assignee_ids = [c.assigned_to for c in items if c.assigned_to]
    name_map = _resolve_user_names(db, assignee_ids)

    list_data = []
    for case in items:
        txn = case.transaction
        list_data.append(CaseListItem(
            case_id=case.case_id,
            txn_id=case.txn_id,
            case_status=case.case_status,
            assigned_to=case.assigned_to,
            assigned_to_name=name_map.get(case.assigned_to) if case.assigned_to else None,
            fraud_score=float(txn.fraud_score) if txn and txn.fraud_score else None,
            amount=txn.amount if txn else None,
            txn_time=txn.txn_time if txn else None,
            created_at=case.created_at,
        ))

    return PagedResponse(
        data=list_data,
        total=total,
        page=page,
        limit=limit,
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
    token: TokenPayload = Depends(require_roles("REVIEWER")),
) -> CaseResponse:
    svc = CaseService(db)
    case = svc.get_case(case_id)

    # REVIEWER chỉ được xem case OPEN (chưa assign) hoặc case được giao cho mình.
    if case.assigned_to is not None and case.assigned_to != token.sub:
        raise PermissionDeniedError("Case này không được giao cho bạn.")

    txn_summary = None
    if case.transaction:
        from sqlalchemy import desc as _desc
        from app.models.transaction import Transaction as _Txn
        t = case.transaction

        # Card velocity stats
        card_velocity = None
        if t.card_number_hash:
            cv = db.query(CardVelocityStats).filter(
                CardVelocityStats.card_hash == t.card_number_hash
            ).first()
            if cv:
                card_velocity = CardVelocitySnapshot(
                    avg_daily_txn=float(cv.avg_daily_txn),
                    total_txn=cv.total_txn,
                    avg_amt=float(cv.avg_amt),
                    std_amt=float(cv.std_amt),
                )

        # 10 recent transactions of same customer (excluding current)
        recent_rows = (
            db.query(_Txn)
            .filter(_Txn.customer_id == t.customer_id, _Txn.txn_id != t.txn_id)
            .order_by(_desc(_Txn.txn_time))
            .limit(10)
            .all()
        )
        recent_transactions = [
            RecentTransaction(
                txn_id=r.txn_id,
                amount=r.amount,
                merchant_name=r.merchant.merchant_name if r.merchant else None,
                status=r.status,
                fraud_score=float(r.fraud_score) if r.fraud_score is not None else None,
                txn_time=r.txn_time,
            )
            for r in recent_rows
        ]

        txn_summary = CaseTransactionSummary(
            txn_id=t.txn_id,
            amount=t.amount,
            txn_time=t.txn_time,
            fraud_score=float(t.fraud_score) if t.fraud_score else None,
            merchant_name=t.merchant.merchant_name if t.merchant else None,
            merchant_category=t.merchant.merchant_category if t.merchant else None,
            merchant_risk_level=t.merchant.risk_level if t.merchant else None,
            customer_name=t.customer.full_name if t.customer else None,
            channel_name=t.channel.channel_name if t.channel else None,
            card_number_masked=t.card_number_masked,
            rule_hits=[
                CaseRuleHit(
                    rule_code=rh.rule_code,
                    rule_name=rh.rule_name,
                    hit_value=rh.hit_value,
                    severity=rh.severity,
                )
                for rh in db.query(RuleHit).filter(RuleHit.txn_id == t.txn_id).all()
            ],
            card_velocity=card_velocity,
            recent_transactions=recent_transactions,
        )

    assignee_name = None
    if case.assigned_to:
        u = db.query(User.full_name).filter(User.user_id == case.assigned_to).scalar()
        assignee_name = u

    return CaseResponse(
        case_id=case.case_id,
        txn_id=case.txn_id,
        case_status=case.case_status,
        assigned_to=case.assigned_to,
        assigned_to_name=assignee_name,
        decision=case.decision,
        decision_note=case.decision_note,
        version=case.version,
        created_at=case.created_at,
        decided_at=case.decided_at,
        transaction=txn_summary,
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
    token: TokenPayload = Depends(require_roles("REVIEWER")),
) -> CaseResponse:
    svc = CaseService(db)
    svc.decide(case_id, body, actor_user_id=token.sub, actor_roles=token.roles)
    return get_case(case_id, db, token)
