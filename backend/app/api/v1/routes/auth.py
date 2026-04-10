from __future__ import annotations
from typing import Optional, List, Dict, Any
"""
Router: Auth
POST /auth/login  — đăng nhập, lấy JWT
POST /auth/refresh — lấy access token mới
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_auth_service
from app.db.deps import get_db
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse
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
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return auth_service.login(body.username, body.password)


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
