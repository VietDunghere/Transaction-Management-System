from __future__ import annotations
"""
Router: Users (User Management)
GET   /users                  — danh sách tài khoản (MANAGER, ADMIN)
GET   /users/{user_id}        — chi tiết tài khoản (MANAGER, ADMIN)
POST  /users                  — tạo tài khoản mới (ADMIN)
PATCH /users/{user_id}/disable — vô hiệu hoá tài khoản (ADMIN)
PATCH /users/{user_id}/enable  — kích hoạt lại tài khoản (ADMIN)
PATCH /users/{user_id}/role    — gán/thay đổi role (ADMIN)
"""

import math
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps import require_roles
from app.db.deps import DbSession
from app.schemas.auth import TokenPayload
from app.schemas.common import PagedResponse, PaginationMeta
from app.schemas.user import (
    CreateUserRequest,
    CreateUserResponse,
    UserListItem,
    UserResponse,
    UserRoleUpdateRequest,
    UserRoleUpdateResponse,
    MessageResponse,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "",
    response_model=PagedResponse[UserListItem],
    summary="Danh sách tài khoản",
    description="Xem danh sách tài khoản nhân viên. Filter theo role và trạng thái.",
)
def list_users(
    db: DbSession,
    token: TokenPayload = Depends(require_roles("MANAGER", "ADMIN")),
    role: Optional[str] = Query(None, description="Lọc theo role: OPERATOR, REVIEWER, MANAGER, ADMIN"),
    is_active: Optional[bool] = Query(None, description="Lọc theo trạng thái active"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100, alias="limit"),
) -> PagedResponse[UserListItem]:
    svc = UserService(db)
    items, total = svc.list_users(role=role, is_active=is_active, page=page, page_size=limit)

    data = []
    for u in items:
        data.append(UserListItem(
            user_id=u.user_id,
            username=u.username,
            full_name=u.full_name,
            role=u.roles[0] if u.roles else "UNKNOWN",
            is_active=u.is_active,
            created_at=u.created_at,
        ))

    return PagedResponse(
        data=data,
        pagination=PaginationMeta(
            page=page,
            page_size=limit,
            total_items=total,
            total_pages=math.ceil(total / limit) if total > 0 else 0,
        ),
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Chi tiết tài khoản",
    description="Xem chi tiết thông tin một người dùng cụ thể.",
)
def get_user(
    user_id: str,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("MANAGER", "ADMIN")),
) -> UserResponse:
    svc = UserService(db)
    user = svc.get_user(user_id)
    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        role=user.roles[0] if user.roles else "UNKNOWN",
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.post(
    "",
    response_model=CreateUserResponse,
    status_code=201,
    summary="Tạo tài khoản",
    description="Tạo tài khoản nhân viên mới. Chỉ ADMIN mới có quyền.",
)
def create_user(
    body: CreateUserRequest,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ADMIN")),
) -> CreateUserResponse:
    svc = UserService(db)
    return svc.create_user(body, actor_user_id=token.sub)


@router.patch(
    "/{user_id}/disable",
    response_model=MessageResponse,
    summary="Vô hiệu hoá tài khoản",
    description="Vô hiệu hoá tài khoản nhân viên. Không được tự disable chính mình.",
)
def disable_user(
    user_id: str,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ADMIN")),
) -> MessageResponse:
    svc = UserService(db)
    svc.disable_user(user_id, actor_user_id=token.sub)
    return MessageResponse(message=f"Tài khoản {user_id} đã bị vô hiệu hoá.")


@router.patch(
    "/{user_id}/enable",
    response_model=MessageResponse,
    summary="Kích hoạt lại tài khoản",
    description="Kích hoạt lại tài khoản đã bị vô hiệu hoá.",
)
def enable_user(
    user_id: str,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ADMIN")),
) -> MessageResponse:
    svc = UserService(db)
    svc.enable_user(user_id, actor_user_id=token.sub)
    return MessageResponse(message=f"Tài khoản {user_id} đã được kích hoạt lại.")


@router.patch(
    "/{user_id}/role",
    response_model=UserRoleUpdateResponse,
    summary="Gán/thay đổi role",
    description="Gán hoặc thay đổi vai trò của người dùng. Chỉ ADMIN mới có quyền.",
)
def update_role(
    user_id: str,
    body: UserRoleUpdateRequest,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ADMIN")),
) -> UserRoleUpdateResponse:
    svc = UserService(db)
    return svc.update_role(user_id, body, actor_user_id=token.sub)
