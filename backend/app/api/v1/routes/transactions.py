from __future__ import annotations
"""
Router: Transactions
POST /transactions/submit    — submit giao dịch mới (OPERATOR)
GET  /transactions           — danh sách giao dịch (OPERATOR, MANAGER)
GET  /transactions/{id}      — chi tiết giao dịch (OPERATOR, MANAGER)
GET  /transactions/{id}/state-history — audit trail trạng thái
"""

import json
import math
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps import require_roles
from app.db.deps import DbSession
from app.repositories.transaction_repo import TransactionRepository
from app.schemas.auth import TokenPayload
from app.schemas.common import PagedResponse, PaginationMeta, TransactionStatus
from app.schemas.transaction import (
    FraudScoreDetail,
    TransactionResponse,
    TransactionSubmitRequest,
    TransactionSubmitResponse,
    TxnStateHistoryItem,
)
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post(
    "/submit",
    response_model=TransactionSubmitResponse,
    status_code=201,
    summary="Submit giao dịch mới",
    description=(
        "Chỉ OPERATOR (= core banking system của ngân hàng) được phép gửi giao dịch. "
        "Hệ thống chấm điểm fraud ngay lập tức và trả về: APPROVED | REJECTED | MANUAL_REVIEW."
    ),
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
    description="Lấy danh sách giao dịch với filter theo status, customer, merchant, ngày.",
)
def list_transactions(
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ANALYST", "MANAGER", "ADMIN")),
    status: Optional[TransactionStatus] = Query(None),
    customer_id: Optional[str] = Query(None, description="Lọc theo customer UUID"),
    merchant_id: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None, description="Từ ngày (ISO 8601)"),
    to_date: Optional[datetime] = Query(None, description="Đến ngày (ISO 8601)"),
    min_amount: Optional[Decimal] = Query(None, ge=0),
    max_amount: Optional[Decimal] = Query(None, ge=0),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> PagedResponse[TransactionResponse]:
    svc = TransactionService(db)

    items, total = svc.list_transactions(
        status=status,
        customer_id=customer_id,
        merchant_id=merchant_id,
        submitted_by=None,
        date_from=from_date,
        date_to=to_date,
        min_amount=float(min_amount) if min_amount is not None else None,
        max_amount=float(max_amount) if max_amount is not None else None,
        page=page,
        page_size=limit,
    )
    return PagedResponse(
        data=[TransactionResponse.model_validate(t) for t in items],
        pagination=PaginationMeta(
            page=page,
            page_size=limit,
            total_items=total,
            total_pages=math.ceil(total / limit) if total > 0 else 0,
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
    token: TokenPayload = Depends(require_roles("OPERATOR", "ANALYST", "MANAGER", "ADMIN")),
) -> TransactionResponse:
    svc = TransactionService(db)
    txn = svc.get_transaction(txn_id)

    response = TransactionResponse.model_validate(txn)

    # Đính kèm fraud detail từ scoring result nếu có
    if txn.scoring_results:
        latest = txn.scoring_results[-1]
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


@router.get(
    "/{txn_id}/state-history",
    response_model=List[TxnStateHistoryItem],
    summary="Lịch sử trạng thái giao dịch",
    description=(
        "Trả về toàn bộ audit trail các lần thay đổi trạng thái của giao dịch, "
        "sắp xếp theo thời gian tăng dần. "
        "Dùng để trace vòng đời: PENDING → APPROVED / REJECTED / MANUAL_REVIEW."
    ),
)
def get_transaction_state_history(
    txn_id: str,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("MANAGER", "ADMIN")),
) -> List[TxnStateHistoryItem]:
    svc = TransactionService(db)
    txn = svc.get_transaction(txn_id)

    repo = TransactionRepository(db)
    history = repo.get_state_history(txn_id)
    return [TxnStateHistoryItem.model_validate(h) for h in history]
