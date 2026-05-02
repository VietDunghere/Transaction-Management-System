from __future__ import annotations
"""
Pydantic schemas: User Management (ERD v2)
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


VALID_ROLES = {"OPERATOR", "REVIEWER", "ANALYST", "MANAGER", "ADMIN"}


class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=100, examples=["operator02"])
    full_name: str = Field(..., min_length=2, max_length=150, examples=["Nguyen Van A"])
    email: str = Field(..., max_length=150, examples=["operator02@tms.local"])
    password: str = Field(..., min_length=8, max_length=128)
    role: str = Field(..., examples=["OPERATOR"])

    def model_post_init(self, __context) -> None:
        if self.role not in VALID_ROLES:
            raise ValueError(f"role phải là một trong: {VALID_ROLES}")


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)

    def model_post_init(self, __context) -> None:
        if self.new_password != self.confirm_password:
            raise ValueError("new_password và confirm_password không khớp.")
        if self.current_password == self.new_password:
            raise ValueError("Mật khẩu mới phải khác mật khẩu hiện t��i.")


class UserRoleUpdateRequest(BaseModel):
    role: str = Field(..., examples=["REVIEWER"])

    def model_post_init(self, __context) -> None:
        if self.role not in VALID_ROLES:
            raise ValueError(f"role phải là một trong: {VALID_ROLES}")


class UserResponse(BaseModel):
    user_id: str
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserListItem(BaseModel):
    user_id: str
    username: str
    full_name: Optional[str] = None
    role: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CreateUserResponse(BaseModel):
    user_id: str
    username: str
    role: str
    created_at: datetime


class UserRoleUpdateResponse(BaseModel):
    user_id: str
    role: str
    updated_at: datetime


class MeResponse(BaseModel):
    user_id: str
    username: str
    full_name: Optional[str] = None
    role: str
    status: str


class MessageResponse(BaseModel):
    message: str
