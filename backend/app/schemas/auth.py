from __future__ import annotations
from typing import Optional, List, Dict, Any
"""
Pydantic schemas: Auth
Request/Response cho đăng nhập và refresh token.
"""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Request đăng nhập."""
    username: str = Field(..., min_length=3, max_length=100, examples=["operator01"])
    password: str = Field(..., min_length=6, examples=["secret123"])


class TokenResponse(BaseModel):
    """Response sau khi đăng nhập thành công."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Thời hạn access token (giây)")
    # User info — trả ngay sau login để frontend không cần gọi thêm /auth/me
    user_id: str
    username: str
    full_name: str
    role: str


class RefreshRequest(BaseModel):
    """Request lấy access token mới bằng refresh token."""
    refresh_token: str


class TokenPayload(BaseModel):
    """Payload đã decode từ JWT — dùng trong dependency injection."""
    sub: str             # user_id
    type: str            # access | refresh
    roles: List[str] = []
    full_name: str = ""
