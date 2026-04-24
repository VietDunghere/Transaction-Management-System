from __future__ import annotations
"""
Router: Audit Logs
GET /audit-logs                                 — danh sách events (MANAGER, ADMIN)
GET /audit-logs/entities/{entity_type}/{id}     — audit trail của 1 entity (MANAGER, ADMIN)
GET /audit-logs/{log_id}                        — chi tiết 1 event (MANAGER, ADMIN)

Thứ tự đăng ký route QUAN TRỌNG:
  - /entities/{...} phải đứng TRƯỚC /{log_id} để FastAPI không nhầm "entities"
    là một log_id khi resolve path.

Audit log là immutable theo quy định ngân hàng — không có POST/PUT/DELETE.
Chỉ MANAGER và ADMIN mới được xem để đảm bảo tính bảo mật.
"""

import math
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps import require_roles
from app.db.deps import DbSession
from app.repositories.audit_repo import VALID_ENTITY_TYPES
from app.schemas.audit_log import AuditLogListItem, AuditLogResponse
from app.schemas.auth import TokenPayload
from app.schemas.common import PagedResponse
from app.services.audit_service import AuditService

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get(
    "",
    response_model=PagedResponse[AuditLogListItem],
    summary="Danh sách audit log",
    description=(
        "Lấy danh sách tất cả audit events với filter đa tiêu chí. "
        "Chỉ MANAGER và ADMIN mới được truy cập. "
        "Kết quả sắp xếp theo thời gian giảm dần (mới nhất trước)."
    ),
)
def list_audit_logs(
    db: DbSession,
    token: TokenPayload = Depends(require_roles("MANAGER", "ADMIN")),
    event_type: Optional[str] = Query(
        None,
        description=(
            "Lọc theo loại event. Các giá trị có thể có: "
            "TRANSACTION_SUBMITTED | "
            "CASE_ASSIGNED, CASE_APPROVED, CASE_REJECTED | "
            "LOAN_APPLIED, LOAN_APPROVED, LOAN_REJECTED | "
            "USER_CREATED, USER_DISABLED, USER_ENABLED, USER_ROLE_UPDATED"
        ),
    ),
    entity_type: Optional[str] = Query(
        None,
        description=f"Lọc theo loại entity. Các giá trị hợp lệ: {sorted(VALID_ENTITY_TYPES)}",
    ),
    actor_user_id: Optional[str] = Query(
        None, description="Lọc theo UUID của user thực hiện hành động"
    ),
    from_date: Optional[datetime] = Query(
        None, description="Từ thời điểm (ISO 8601). VD: 2024-01-01T00:00:00"
    ),
    to_date: Optional[datetime] = Query(
        None, description="Đến thời điểm (ISO 8601). VD: 2024-12-31T23:59:59"
    ),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> PagedResponse[AuditLogListItem]:
    svc = AuditService(db)
    items, total = svc.list_logs(
        event_type=event_type,
        entity_type=entity_type,
        actor_user_id=actor_user_id,
        from_date=from_date,
        to_date=to_date,
        page=page,
        page_size=limit,
    )
    return PagedResponse(
        data=[AuditLogListItem.model_validate(log) for log in items],
        total=total,
        page=page,
        limit=limit,
    )


# ⚠️  Route này phải đứng TRƯỚC /{log_id} để tránh FastAPI match "entities" như log_id
@router.get(
    "/entities/{entity_type}/{entity_id}",
    response_model=PagedResponse[AuditLogResponse],
    summary="Audit trail của một entity",
    description=(
        "Lấy toàn bộ lịch sử hành động của một entity cụ thể (Transaction, Loan, "
        "ReviewCase, User) theo thứ tự thời gian tăng dần. "
        f"entity_type hợp lệ: {sorted(VALID_ENTITY_TYPES)}. "
        "Dùng để trace vòng đời đầy đủ của một đối tượng."
    ),
)
def list_entity_audit_logs(
    entity_type: str,
    entity_id: str,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("MANAGER", "ADMIN")),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=200),
) -> PagedResponse[AuditLogResponse]:
    svc = AuditService(db)
    items, total = svc.list_by_entity(
        entity_type=entity_type,
        entity_id=entity_id,
        page=page,
        page_size=limit,
    )
    return PagedResponse(
        data=[AuditLogResponse.model_validate(log) for log in items],
        total=total,
        page=page,
        limit=limit,
    )


@router.get(
    "/{log_id}",
    response_model=AuditLogResponse,
    summary="Chi tiết một audit event",
    description=(
        "Lấy đầy đủ thông tin của một audit log event, kèm detail dạng JSON object. "
        "detail chứa context cụ thể tuỳ theo event_type."
    ),
)
def get_audit_log(
    log_id: str,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("MANAGER", "ADMIN")),
) -> AuditLogResponse:
    svc = AuditService(db)
    log = svc.get_log(log_id)
    return AuditLogResponse.model_validate(log)
