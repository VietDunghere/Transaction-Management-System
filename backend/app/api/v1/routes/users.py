from __future__ import annotations
"""
Router: Users (ERD v2)
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps import require_roles
from app.db.deps import DbSession
from app.schemas.auth import TokenPayload
from app.schemas.common import PagedResponse
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
)
def list_users(
    db: DbSession,
    token: TokenPayload = Depends(require_roles("MANAGER", "ADMIN")),
    role: Optional[str] = Query(None, description="Lọc theo role"),
    status: Optional[str] = Query(None, description="Lọc theo status: ACTIVE, DISABLED"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100, alias="limit"),
) -> PagedResponse[UserListItem]:
    svc = UserService(db)
    items, total = svc.list_users(role=role, status=status, page=page, page_size=limit)

    data = [
        UserListItem(
            user_id=u.user_id,
            username=u.username,
            full_name=u.full_name,
            role=u.role,
            status=u.status,
            created_at=u.created_at,
        )
        for u in items
    ]

    return PagedResponse(data=data, total=total, page=page, limit=limit)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Chi tiết tài khoản",
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
        role=user.role,
        status=user.status,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.post(
    "",
    response_model=CreateUserResponse,
    status_code=201,
    summary="Tạo tài khoản",
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
)
def update_role(
    user_id: str,
    body: UserRoleUpdateRequest,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ADMIN")),
) -> UserRoleUpdateResponse:
    svc = UserService(db)
    return svc.update_role(user_id, body, actor_user_id=token.sub)
