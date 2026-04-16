from __future__ import annotations
"""
Pydantic schemas: User Management
Request/Response cho CRUD tài khoản và phân quyền.
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field


# ============================================================
# Enums
# ============================================================

VALID_ROLES = {"OPERATOR", "REVIEWER", "MANAGER", "ADMIN"}


# ============================================================
# Request schemas
# ============================================================

class CreateUserRequest(BaseModel):
    """ADMIN tạo tài khoản nhân viên mới."""
    username: str = Field(..., min_length=3, max_length=100, examples=["operator02"])
    full_name: str = Field(..., min_length=2, max_length=150, examples=["Nguyen Van A"])
    email: str = Field(..., max_length=150, examples=["operator02@tms.local"])
    password: str = Field(..., min_length=8, max_length=128)
    role: str = Field(..., examples=["OPERATOR"])

    def model_post_init(self, __context) -> None:
        if self.role not in VALID_ROLES:
            raise ValueError(f"role phải là một trong: {VALID_ROLES}")


class ChangePasswordRequest(BaseModel):
    """Đổi mật khẩu cá nhân."""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)

    def model_post_init(self, __context) -> None:
        if self.new_password != self.confirm_password:
            raise ValueError("new_password và confirm_password không khớp.")
        if self.current_password == self.new_password:
            raise ValueError("Mật khẩu mới phải khác mật khẩu hiện tại.")


class UserRoleUpdateRequest(BaseModel):
    """ADMIN gán/thay đổi role cho user."""
    role: str = Field(..., examples=["REVIEWER"])

    def model_post_init(self, __context) -> None:
        if self.role not in VALID_ROLES:
            raise ValueError(f"role phải là một trong: {VALID_ROLES}")


# ============================================================
# Response schemas
# ============================================================

class UserResponse(BaseModel):
    """Response chi tiết 1 user."""
    user_id: str
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: str = Field(description="Role chính của user")
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserListItem(BaseModel):
    """Item tóm tắt trong danh sách users."""
    user_id: str
    username: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CreateUserResponse(BaseModel):
    """Response sau khi tạo user thành công."""
    user_id: str
    username: str
    role: str
    created_at: datetime


class UserRoleUpdateResponse(BaseModel):
    """Response sau khi thay đổi role."""
    user_id: str
    role: str
    updated_at: datetime


class MeResponse(BaseModel):
    """Response GET /auth/me — thông tin tài khoản đang đăng nhập."""
    user_id: str
    username: str
    full_name: Optional[str] = None
    role: str
    is_active: bool


class MessageResponse(BaseModel):
    """Response đơn giản chỉ có message."""
    message: str
