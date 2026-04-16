from __future__ import annotations
from typing import Optional, List, Dict, Any
"""
Router: Transactions
POST /transactions       — submit giao dịch mới (OPERATOR)
GET  /transactions       — danh sách giao dịch (OPERATOR, MANAGER)
GET  /transactions/{id}  — chi tiết giao dịch (OPERATOR, MANAGER)
"""

import math
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import require_roles
from app.schemas.auth import TokenPayload
from app.db.deps import DbSession
from app.schemas.common import PagedResponse, PaginationMeta, TransactionStatus
from app.schemas.transaction import (
    FraudScoreDetail,
    TransactionListFilter,
    TransactionResponse,
    TransactionSubmitRequest,
    TransactionSubmitResponse,
)
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post(
    "",
    response_model=TransactionSubmitResponse,
    status_code=201,
    summary="Submit giao dịch mới",
    description=(
        "OPERATOR gửi giao dịch. Hệ thống sẽ chấm điểm fraud ngay lập tức "
        "và trả về kết quả: APPROVED | REJECTED | MANUAL_REVIEW."
    ),
)
def submit_transaction(
    body: TransactionSubmitRequest,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("OPERATOR", "MANAGER", "ADMIN")),
) -> TransactionSubmitResponse:
    svc = TransactionService(db)
    return svc.submit(body, submitted_by_user_id=token.sub)


@router.get(
    "",
    response_model=PagedResponse[TransactionResponse],
    summary="Danh sách giao dịch",
    description="Lấy danh sách giao dịch với filter theo status, customer, merchant, ngày.",
)
def list_transactions(
    db: DbSession,
    token: TokenPayload = Depends(require_roles("OPERATOR", "MANAGER", "ADMIN")),
    status: Optional[TransactionStatus] = Query(None),
    customer_id: Optional[str] = Query(None),
    merchant_id: Optional[str] = Query(None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> PagedResponse[TransactionResponse]:
    svc = TransactionService(db)
    items, total = svc.list_transactions(
        status=status,
        customer_id=customer_id,
        merchant_id=merchant_id,
        page=page,
        page_size=page_size,
    )
    return PagedResponse(
        data=[TransactionResponse.model_validate(t) for t in items],
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=math.ceil(total / page_size),
        ),
    )


@router.get(
    "/{txn_id}",
    response_model=TransactionResponse,
    summary="Chi tiết giao dịch",
    description="Lấy thông tin chi tiết 1 giao dịch kèm kết quả scoring.",
)
def get_transaction(
    txn_id: str,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("OPERATOR", "MANAGER", "ADMIN", "REVIEWER")),
) -> TransactionResponse:
    svc = TransactionService(db)
    txn = svc.get_transaction(txn_id)
    response = TransactionResponse.model_validate(txn)

    # Đính kèm fraud detail từ scoring result nếu có
    if txn.scoring_results:
        latest = txn.scoring_results[-1]
        import json
        reasons = json.loads(latest.reason_json or "{}") if latest.reason_json else {}
        response.fraud_detail = FraudScoreDetail(
            fraud_score=float(latest.fraud_score),
            decision=latest.decision_suggested or txn.status,
            reject_threshold=float(latest.reject_threshold or 0.45),
            review_threshold=float(latest.review_threshold or 0.05),
            model_version=latest.model_version or "unknown",
            top_risk_factors=reasons.get("top_features", []),
        )
    return response
