from __future__ import annotations
"""
Service: UserService
Business logic cho quản lý tài khoản (CRUD, disable/enable, role).
Commit tại service layer — repo chỉ flush.
"""

import math
import uuid
from datetime import datetime, timezone
from typing import Optional, Tuple, List

from sqlalchemy.orm import Session

from app.core.exceptions import (
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
)
from app.core.logging import get_logger
from app.core.security import hash_password
from app.models.user import Role, User, UserRole
from app.repositories.user_repo import UserRepository
from app.schemas.user import (
    CreateUserRequest,
    CreateUserResponse,
    UserRoleUpdateRequest,
    UserRoleUpdateResponse,
)

logger = get_logger(__name__)


class UserService:
    """Quản lý tài khoản nhân viên — ADMIN only (trừ list cho MANAGER)."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = UserRepository(db)

    # ---- List ----

    def list_users(
        self,
        *,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[User], int]:
        """Danh sách users (MANAGER, ADMIN)."""
        return self._repo.list_users(
            role=role, is_active=is_active, page=page, page_size=page_size
        )

    # ---- Get by ID ----

    def get_user(self, user_id: str) -> User:
        """Lấy chi tiết 1 user. Raises NotFoundError."""
        user = self._repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User")
        return user

    # ---- Create ----

    def create_user(self, req: CreateUserRequest) -> CreateUserResponse:
        """
        Tạo tài khoản nhân viên mới (ADMIN only).
        Raises: ConflictError nếu username/email trùng.
        """
        # Check duplicate username
        if self._repo.get_by_username(req.username):
            raise ConflictError(f"Username '{req.username}' đã tồn tại.")

        # Check duplicate email
        if self._repo.get_by_email(req.email):
            raise ConflictError(f"Email '{req.email}' đã được sử dụng.")

        # Verify role exists
        role_entity = self._repo.get_role_by_name(req.role)
        if role_entity is None:
            raise NotFoundError(f"Role '{req.role}'")

        # Create user
        user = User(
            user_id=str(uuid.uuid4()),
            username=req.username,
            full_name=req.full_name,
            email=req.email,
            password_hash=hash_password(req.password),
            is_active=True,
        )
        self._repo.create(user)
        self._repo.flush()  # flush to get user_id in session

        # Assign role
        user_role = UserRole(user_id=user.user_id, role_id=role_entity.role_id)
        self._repo.add_user_role(user_role)

        self._db.commit()
        self._db.refresh(user)

        logger.info("user_created", user_id=user.user_id, username=req.username, role=req.role)

        return CreateUserResponse(
            user_id=user.user_id,
            username=user.username,
            role=req.role,
            created_at=user.created_at,
        )

    # ---- Disable / Enable ----

    def disable_user(self, user_id: str, actor_user_id: str) -> User:
        """
        Vô hiệu hoá tài khoản (ADMIN only).
        Không cho phép tự disable chính mình.
        """
        if user_id == actor_user_id:
            raise PermissionDeniedError("Không thể vô hiệu hoá tài khoản của chính mình.")

        user = self._repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User")

        user.is_active = False
        self._db.commit()
        self._db.refresh(user)

        logger.info("user_disabled", user_id=user_id, actor=actor_user_id)
        return user

    def enable_user(self, user_id: str, actor_user_id: str) -> User:
        """Kích hoạt lại tài khoản đã bị vô hiệu hoá (ADMIN only)."""
        user = self._repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User")

        user.is_active = True
        self._db.commit()
        self._db.refresh(user)

        logger.info("user_enabled", user_id=user_id, actor=actor_user_id)
        return user

    # ---- Role ----

    def update_role(
        self, user_id: str, req: UserRoleUpdateRequest, actor_user_id: str
    ) -> UserRoleUpdateResponse:
        """
        Gán/thay đổi role cho user (ADMIN only).
        Xoá role cũ → gán role mới (single-role model theo API design).
        Không cho ADMIN tự hạ role chính mình.
        """
        if user_id == actor_user_id:
            raise PermissionDeniedError("Không thể thay đổi role của chính mình.")

        user = self._repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User")

        role_entity = self._repo.get_role_by_name(req.role)
        if role_entity is None:
            raise NotFoundError(f"Role '{req.role}'")

        # Remove old roles, assign new
        self._repo.remove_user_roles(user_id)
        self._repo.flush()

        user_role = UserRole(user_id=user_id, role_id=role_entity.role_id)
        self._repo.add_user_role(user_role)

        self._db.commit()
        self._db.refresh(user)

        logger.info("user_role_changed", user_id=user_id, new_role=req.role, actor=actor_user_id)

        return UserRoleUpdateResponse(
            user_id=user_id,
            role=req.role,
            updated_at=user.updated_at or datetime.now(timezone.utc),
        )
