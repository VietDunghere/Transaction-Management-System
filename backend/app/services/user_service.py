from __future__ import annotations
"""
Service: UserService (ERD v2)
Direct role/status columns — no Role/UserRole tables.
"""

import json
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
from app.models.scoring import AuditLog
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.user import (
    CreateUserRequest,
    CreateUserResponse,
    UserRoleUpdateRequest,
    UserRoleUpdateResponse,
    VALID_ROLES,
)

logger = get_logger(__name__)


def _write_user_audit(
    db: Session,
    event_type: str,
    entity_id: str,
    actor_user_id: str,
    detail: dict,
) -> None:
    user = db.query(User.full_name).filter(User.user_id == actor_user_id).first()
    db.add(AuditLog(
        log_id=str(uuid.uuid4()),
        event_type=event_type,
        entity_type="User",
        entity_id=entity_id,
        actor_user_id=actor_user_id,
        actor_name=user.full_name if user else None,
        detail_json=json.dumps(detail),
    ))


class UserService:

    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = UserRepository(db)

    def list_users(
        self,
        *,
        role: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[User], int]:
        return self._repo.list_users(
            role=role, status=status, page=page, page_size=page_size
        )

    def get_user(self, user_id: str) -> User:
        user = self._repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User")
        return user

    def create_user(self, req: CreateUserRequest, actor_user_id: str) -> CreateUserResponse:
        if self._repo.get_by_username(req.username):
            raise ConflictError(f"Username '{req.username}' đã tồn tại.")
        if self._repo.get_by_email(req.email):
            raise ConflictError(f"Email '{req.email}' đã được sử dụng.")
        if req.role not in VALID_ROLES:
            raise NotFoundError(f"Role '{req.role}'")

        user = User(
            user_id=str(uuid.uuid4()),
            username=req.username,
            full_name=req.full_name,
            email=req.email,
            password_hash=hash_password(req.password),
            role=req.role,
            status="ACTIVE",
        )
        self._repo.create(user)
        self._repo.flush()

        _write_user_audit(self._db, "USER_CREATED", user.user_id, actor_user_id=actor_user_id, detail={
            "username": req.username,
            "email": req.email,
            "role": req.role,
        })
        self._db.commit()
        self._db.refresh(user)

        logger.info("user_created", user_id=user.user_id, username=req.username, role=req.role)

        return CreateUserResponse(
            user_id=user.user_id,
            username=user.username,
            role=req.role,
            created_at=user.created_at,
        )

    def disable_user(self, user_id: str, actor_user_id: str) -> User:
        if user_id == actor_user_id:
            raise PermissionDeniedError("Không thể vô hiệu hoá tài khoản của chính mình.")

        user = self._repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User")

        user.status = "DISABLED"
        _write_user_audit(self._db, "USER_DISABLED", user_id, actor_user_id=actor_user_id, detail={
            "username": user.username,
        })
        self._db.commit()
        self._db.refresh(user)

        logger.info("user_disabled", user_id=user_id, actor=actor_user_id)
        return user

    def enable_user(self, user_id: str, actor_user_id: str) -> User:
        user = self._repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User")

        user.status = "ACTIVE"
        _write_user_audit(self._db, "USER_ENABLED", user_id, actor_user_id=actor_user_id, detail={
            "username": user.username,
        })
        self._db.commit()
        self._db.refresh(user)

        logger.info("user_enabled", user_id=user_id, actor=actor_user_id)
        return user

    def update_role(
        self, user_id: str, req: UserRoleUpdateRequest, actor_user_id: str
    ) -> UserRoleUpdateResponse:
        if user_id == actor_user_id:
            raise PermissionDeniedError("Không thể thay đổi role của chính mình.")

        user = self._repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User")

        if req.role not in VALID_ROLES:
            raise NotFoundError(f"Role '{req.role}'")

        user.role = req.role

        _write_user_audit(self._db, "USER_ROLE_UPDATED", user_id, actor_user_id=actor_user_id, detail={
            "username": user.username,
            "new_role": req.role,
        })
        self._db.commit()
        self._db.refresh(user)

        logger.info("user_role_changed", user_id=user_id, new_role=req.role, actor=actor_user_id)

        return UserRoleUpdateResponse(
            user_id=user_id,
            role=req.role,
            updated_at=user.updated_at or datetime.now(timezone.utc),
        )
