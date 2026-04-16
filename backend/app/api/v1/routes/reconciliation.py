from __future__ import annotations
"""
Router: Reconciliation
POST  /reconciliation/run           — trigger phiên đối soát (ADMIN)
GET   /reconciliation/reports       — danh sách phiên đối soát (ADMIN)
GET   /reconciliation/{run_id}      — chi tiết phiên đối soát (ADMIN)
PATCH /reconciliation/{run_id}/resolve — bulk-resolve discrepancies (ADMIN)

IMPORTANT: route /reports PHẢI đứng trước /{run_id} để FastAPI không
           nhầm "reports" là run_id path param.
"""

import math
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps import require_roles
from app.db.deps import DbSession
from app.schemas.auth import TokenPayload
from app.schemas.common import PagedResponse, PaginationMeta
from app.schemas.reconciliation import (
    ReconciliationDetailResponse,
    ReconciliationRunRequest,
    ReconciliationRunResponse,
    ResolveRequest,
)
from app.services.reconciliation_service import ReconciliationService

router = APIRouter(prefix="/reconciliation", tags=["Reconciliation"])


@router.post(
    "/run",
    response_model=ReconciliationRunResponse,
    status_code=201,
    summary="Trigger phiên đối soát",
    description=(
        "Chạy đối soát cho khoảng thời gian period_start → period_end. "
        "Hệ thống tìm tất cả giao dịch PENDING đã vượt quá pending_timeout_minutes "
        "và đánh dấu là PENDING_TIMEOUT. "
        "Phiên được tạo ở trạng thái RUNNING → COMPLETED khi xong, FAILED nếu lỗi. "
        "Chỉ ADMIN được phép."
    ),
)
def run_reconciliation(
    body: ReconciliationRunRequest,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ADMIN")),
) -> ReconciliationRunResponse:
    svc = ReconciliationService(db)
    run = svc.run(body, triggered_by=token.sub)
    return ReconciliationRunResponse.model_validate(run)


@router.get(
    "/reports",
    response_model=PagedResponse[ReconciliationRunResponse],
    summary="Danh sách phiên đối soát",
    description=(
        "Lấy danh sách các phiên đối soát (không kèm items chi tiết). "
        "Hỗ trợ lọc theo status. "
        "Chỉ ADMIN được phép."
    ),
)
def list_reconciliation_runs(
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ADMIN")),
    status: Optional[str] = Query(
        None,
        description="Lọc theo status: RUNNING | COMPLETED | FAILED",
    ),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100, alias="limit"),
) -> PagedResponse[ReconciliationRunResponse]:
    svc = ReconciliationService(db)
    items, total = svc.list_runs(status=status, page=page, page_size=limit)
    return PagedResponse(
        data=[ReconciliationRunResponse.model_validate(run) for run in items],
        pagination=PaginationMeta(
            page=page,
            page_size=limit,
            total_items=total,
            total_pages=math.ceil(total / limit) if total > 0 else 0,
        ),
    )


@router.get(
    "/{run_id}",
    response_model=ReconciliationDetailResponse,
    summary="Chi tiết phiên đối soát",
    description=(
        "Lấy đầy đủ thông tin một phiên đối soát kèm danh sách discrepancy items. "
        "Chỉ ADMIN được phép."
    ),
)
def get_reconciliation_run(
    run_id: str,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ADMIN")),
) -> ReconciliationDetailResponse:
    svc = ReconciliationService(db)
    run = svc.get_run(run_id)
    return ReconciliationDetailResponse.model_validate(run)


@router.patch(
    "/{run_id}/resolve",
    response_model=ReconciliationDetailResponse,
    summary="Bulk-resolve discrepancies",
    description=(
        "Đánh dấu tất cả discrepancy items OPEN trong phiên là RESOLVED. "
        "Chỉ áp dụng cho phiên đã COMPLETED. "
        "resolution_note bắt buộc để đảm bảo audit trail. "
        "Chỉ ADMIN được phép."
    ),
)
def resolve_reconciliation(
    run_id: str,
    body: ResolveRequest,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ADMIN")),
) -> ReconciliationDetailResponse:
    svc = ReconciliationService(db)
    run = svc.resolve(run_id, body, actor_user_id=token.sub)
    return ReconciliationDetailResponse.model_validate(run)
