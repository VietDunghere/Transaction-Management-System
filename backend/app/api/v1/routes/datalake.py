from __future__ import annotations
"""
Router: DataLake
POST /datalake/ingest     — ingest batch dữ liệu ngoài (ADMIN)
GET  /datalake/snapshots  — danh sách snapshots (ADMIN)
"""

import math
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps import require_roles
from app.db.deps import DbSession
from app.schemas.auth import TokenPayload
from app.schemas.common import PagedResponse, PaginationMeta
from app.schemas.etl import DataLakeIngestRequest, DataLakeSnapshotResponse
from app.services.etl_service import EtlService

router = APIRouter(prefix="/datalake", tags=["DataLake"])


@router.post(
    "/ingest",
    response_model=DataLakeSnapshotResponse,
    status_code=201,
    summary="Ingest dữ liệu ngoài vào DataLake",
    description=(
        "Nhận batch records từ nguồn ngoài (bank statement, POS gateway, v.v.) "
        "và lưu vào DataLake dưới dạng snapshot EXTERNAL_INGEST. "
        "Tối đa 10.000 records mỗi lần. "
        "Chỉ ADMIN được phép."
    ),
)
def ingest(
    body: DataLakeIngestRequest,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ADMIN")),
) -> DataLakeSnapshotResponse:
    svc = EtlService(db)
    snapshot = svc.ingest(body, triggered_by=token.sub)
    return DataLakeSnapshotResponse.model_validate(snapshot)


@router.get(
    "/snapshots",
    response_model=PagedResponse[DataLakeSnapshotResponse],
    summary="Danh sách DataLake snapshots",
    description=(
        "Lấy danh sách snapshots với filter tùy chọn. "
        "Hỗ trợ lọc theo loại snapshot, ngày, và trạng thái. "
        "Chỉ ADMIN được phép."
    ),
)
def list_snapshots(
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ADMIN")),
    snapshot_type: Optional[str] = Query(
        None,
        description="Lọc theo loại: DAILY_TXN_SUMMARY | EXTERNAL_INGEST",
    ),
    snapshot_date: Optional[date] = Query(
        None,
        description="Lọc theo ngày snapshot (yyyy-mm-dd)",
    ),
    status: Optional[str] = Query(
        None,
        description="Lọc theo status: ACTIVE | ARCHIVED",
    ),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100, alias="limit"),
) -> PagedResponse[DataLakeSnapshotResponse]:
    svc = EtlService(db)
    items, total = svc.list_snapshots(
        snapshot_type=snapshot_type,
        snapshot_date=snapshot_date,
        status=status,
        page=page,
        page_size=limit,
    )
    return PagedResponse(
        data=[DataLakeSnapshotResponse.model_validate(s) for s in items],
        pagination=PaginationMeta(
            page=page,
            page_size=limit,
            total_items=total,
            total_pages=math.ceil(total / limit) if total > 0 else 0,
        ),
    )
