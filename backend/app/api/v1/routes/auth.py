from __future__ import annotations
"""
Router: Auth
POST  /auth/login           — đăng nhập, lấy JWT
POST  /auth/logout          — đăng xuất (stateless — client discard token)
GET   /auth/me              — thông tin tài khoản đang đăng nhập
PATCH /auth/change-password — đổi mật khẩu cá nhân
POST  /auth/refresh         — lấy access token mới
"""

from fastapi import APIRouter, Depends

from app.api.v1.deps import CurrentToken, CurrentUser, get_auth_service
from app.db.deps import DbSession
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse
from app.schemas.user import ChangePasswordRequest, MeResponse, MessageResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Đăng nhập",
    description="Xác thực username/password và trả JWT access + refresh token.",
)
def login(
    body: LoginRequest,
    db: DbSession,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    result = auth_service.login(body.username, body.password)
    db.commit()
    return result


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Đăng xuất",
    description="Đăng xuất — JWT stateless nên client chỉ cần discard token.",
)
def logout(
    token: CurrentToken,
    db: DbSession,
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    auth_service.logout(user_id=token.sub)
    db.commit()
    return MessageResponse(message="Đăng xuất thành công.")


@router.get(
    "/me",
    response_model=MeResponse,
    summary="Thông tin tài khoản",
    description="Xem thông tin tài khoản đang xác thực. Tất cả roles đều truy cập được.",
)
def me(user: CurrentUser) -> MeResponse:
    return MeResponse(
        user_id=user.user_id,
        username=user.username,
        full_name=user.full_name,
        role=user.role,
        status=user.status,
    )


@router.patch(
    "/change-password",
    response_model=MessageResponse,
    summary="Đổi mật khẩu",
    description="Đổi mật khẩu cá nhân. Cần cung cấp mật khẩu hiện tại để xác thực.",
)
def change_password(
    body: ChangePasswordRequest,
    db: DbSession,
    token: CurrentToken,
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    auth_service.change_password(
        user_id=token.sub,
        current_password=body.current_password,
        new_password=body.new_password,
    )
    db.commit()
    return MessageResponse(message="Đổi mật khẩu thành công.")


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh token",
    description="Dùng refresh token để lấy access token mới mà không cần đăng nhập lại.",
)
def refresh_token(
    body: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return auth_service.refresh(body.refresh_token)
