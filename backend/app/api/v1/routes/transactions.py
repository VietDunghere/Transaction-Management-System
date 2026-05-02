from __future__ import annotations
"""
Router: Transactions (ERD v2)
Removed: state-history endpoint (replaced by audit_logs), scoring_results references.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps import require_roles
from app.db.deps import DbSession
from app.schemas.auth import TokenPayload
from app.schemas.common import PagedResponse, TransactionStatus
from app.schemas.transaction import (
    TransactionResponse,
    TransactionSubmitRequest,
    TransactionSubmitResponse,
)
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post(
    "/submit",
    response_model=TransactionSubmitResponse,
    status_code=201,
    summary="Submit giao dịch mới",
)
def submit_transaction(
    body: TransactionSubmitRequest,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("OPERATOR")),
) -> TransactionSubmitResponse:
    svc = TransactionService(db)
    return svc.submit(body, submitted_by_user_id=token.sub)


@router.get(
    "",
    response_model=PagedResponse[TransactionResponse],
    summary="Danh sách giao dịch",
)
def list_transactions(
    db: DbSession,
    token: TokenPayload = Depends(require_roles("OPERATOR", "ANALYST", "MANAGER")),
    status: Optional[TransactionStatus] = Query(None),
    customer_id: Optional[str] = Query(None),
    merchant_id: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    min_amount: Optional[Decimal] = Query(None, ge=0),
    max_amount: Optional[Decimal] = Query(None, ge=0),
    period: Optional[str] = Query(None, description="D=1 ngày, W=7 ngày, M=30 ngày"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> PagedResponse[TransactionResponse]:
    svc = TransactionService(db)

    _period_days = {"D": 1, "W": 7, "M": 30}
    effective_from = (
        datetime.now(timezone.utc) - timedelta(days=_period_days[period])
        if period and period in _period_days else from_date
    )

    items, total = svc.list_transactions(
        status=status,
        customer_id=customer_id,
        merchant_id=merchant_id,
        submitted_by=None,
        date_from=effective_from,
        date_to=to_date,
        min_amount=float(min_amount) if min_amount is not None else None,
        max_amount=float(max_amount) if max_amount is not None else None,
        page=page,
        page_size=limit,
    )
    return PagedResponse(
        data=[TransactionResponse.model_validate(t) for t in items],
        total=total,
        page=page,
        limit=limit,
    )


@router.get(
    "/{txn_id}",
    response_model=TransactionResponse,
    summary="Chi tiết giao dịch",
)
def get_transaction(
    txn_id: str,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("OPERATOR", "ANALYST", "MANAGER")),
) -> TransactionResponse:
    svc = TransactionService(db)
    txn = svc.get_transaction(txn_id)

    response = TransactionResponse.model_validate(txn)
    if txn.customer:
        response.customer_name = txn.customer.full_name
    if txn.merchant:
        response.merchant_name = txn.merchant.merchant_name

    return response
