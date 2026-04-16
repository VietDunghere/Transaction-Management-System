from __future__ import annotations
"""
Router: ETL
POST /etl/run   — trigger ETL job (ADMIN)
GET  /etl/logs  — danh sách ETL job runs (ADMIN)
"""

import math
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps import require_roles
from app.db.deps import DbSession
from app.schemas.auth import TokenPayload
from app.schemas.common import PagedResponse, PaginationMeta
from app.schemas.etl import EtlJobResponse, EtlRunRequest
from app.services.etl_service import EtlService

router = APIRouter(prefix="/etl", tags=["ETL"])


@router.post(
    "/run",
    response_model=EtlJobResponse,
    status_code=201,
    summary="Trigger ETL job",
    description=(
        "Chạy ETL pipeline cho một ngày cụ thể. "
        "Tổng hợp tất cả giao dịch trong target_date và lưu vào DataLake. "
        "**Idempotency guard**: mỗi (target_date, job_type) chỉ được chạy thành công 1 lần — "
        "nếu đã SUCCESS sẽ trả về 409. "
        "Chỉ ADMIN được phép."
    ),
)
def run_etl(
    body: EtlRunRequest,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ADMIN")),
) -> EtlJobResponse:
    svc = EtlService(db)
    job = svc.run_etl(body, triggered_by=token.sub)
    return EtlJobResponse.model_validate(job)


@router.get(
    "/logs",
    response_model=PagedResponse[EtlJobResponse],
    summary="Danh sách ETL job runs",
    description=(
        "Lấy danh sách các ETL job runs với filter tùy chọn. "
        "Chỉ ADMIN được phép."
    ),
)
def list_etl_jobs(
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ADMIN")),
    job_type: Optional[str] = Query(None, description="Lọc theo job_type (vd: DAILY_SUMMARY)"),
    status: Optional[str] = Query(None, description="Lọc theo status: RUNNING | SUCCESS | FAILED"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100, alias="limit"),
) -> PagedResponse[EtlJobResponse]:
    svc = EtlService(db)
    items, total = svc.list_jobs(
        job_type=job_type,
        status=status,
        page=page,
        page_size=limit,
    )
    return PagedResponse(
        data=[EtlJobResponse.model_validate(job) for job in items],
        pagination=PaginationMeta(
            page=page,
            page_size=limit,
            total_items=total,
            total_pages=math.ceil(total / limit) if total > 0 else 0,
        ),
    )
