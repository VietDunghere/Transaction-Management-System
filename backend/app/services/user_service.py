from __future__ import annotations
"""
Service: UserDAO (ERD v2)
Direct role/status columns — no Role/UserRole tables.
Merged: user management + authentication (formerly AuthService).
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Optional, Tuple, List

from jose import JWTError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    ConflictError,
    InactiveUserError,
    InvalidCredentialsError,
    NotFoundError,
    PermissionDeniedError,
    TokenExpiredError,
    TokenInvalidError,
)
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.scoring import AuditLog
from app.models.user import Users
from app.repositories.user_repo import UserRepository
from app.schemas.auth import TokenPayload, TokenResponse
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
    user = db.query(Users.full_name).filter(Users.user_id == actor_user_id).first()
    db.add(AuditLog(
        log_id=str(uuid.uuid4()),
        event_type=event_type,
        entity_type="User",
        entity_id=entity_id,
        actor_user_id=actor_user_id,
        actor_name=user.full_name if user else None,
        detail_json=json.dumps(detail),
    ))


def _write_auth_audit(
    db: Session,
    event_type: str,
    entity_id: str,
    actor_user_id: Optional[str],
    actor_name: Optional[str],
    detail: dict,
) -> None:
    db.add(AuditLog(
        log_id=str(uuid.uuid4()),
        event_type=event_type,
        entity_type="Auth",
        entity_id=entity_id,
        actor_user_id=actor_user_id,
        actor_name=actor_name,
        detail_json=json.dumps(detail),
    ))
    db.flush()


class UserDAO:

    def __init__(self, db_or_repo, db: Optional[Session] = None) -> None:
        # Reconcile the two former constructors:
        #   UserService(db)                  → build UserRepository from the Session
        #   AuthService(UserRepository(db))  → repo passed directly (+ optional db)
        if isinstance(db_or_repo, UserRepository):
            self._repo = db_or_repo
            self._db = db or db_or_repo._db
        else:
            self._db = db_or_repo
            self._repo = UserRepository(db_or_repo)
        # Auth methods reference self._user_repo; keep it as an alias of the repo.
        self._user_repo = self._repo

    # ============================================================
    # User management
    # ============================================================

    def list_users(
        self,
        *,
        role: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Users], int]:
        return self._repo.list_users(
            role=role, status=status, page=page, page_size=page_size
        )

    def get_user(self, user_id: str) -> Users:
        user = self._repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User")
        return user

    def createUser(self, req: CreateUserRequest, actor_user_id: str) -> CreateUserResponse:
        if self._repo.get_by_username(req.username):
            raise ConflictError(f"Username '{req.username}' đã tồn tại.")
        if self._repo.get_by_email(req.email):
            raise ConflictError(f"Email '{req.email}' đã được sử dụng.")
        if req.role not in VALID_ROLES:
            raise NotFoundError(f"Role '{req.role}'")

        user = Users(
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

    def disableUser(self, user_id: str, actor_user_id: str) -> Users:
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

    def reactivateUser(self, user_id: str, actor_user_id: str) -> Users:
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

    def changeUserRole(
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

    # ============================================================
    # Authentication (merged from AuthService)
    # ============================================================

    def checkLogin(self, username: str, password: str) -> TokenResponse:
        user = self._user_repo.get_by_username(username)

        if user is None or not verify_password(password, user.password_hash):
            logger.warning("login_failed", username=username)
            _write_auth_audit(
                self._db,
                event_type="LOGIN_FAILED",
                entity_id="unknown",
                actor_user_id=None,
                actor_name=None,
                detail={"username": username, "reason": "invalid_credentials"},
            )
            self._db.commit()
            raise InvalidCredentialsError()

        if user.status != "ACTIVE":
            logger.warning("login_inactive_account", user_id=user.user_id)
            raise InactiveUserError()

        tokens = self._issue_tokens(user)

        _write_auth_audit(
            self._db,
            event_type="LOGIN_SUCCESS",
            entity_id=user.user_id,
            actor_user_id=user.user_id,
            actor_name=user.full_name,
            detail={"username": username},
        )

        logger.info("login_success", user_id=user.user_id, role=user.role)
        return tokens

    def refresh(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
        except JWTError as exc:
            if "expired" in str(exc).lower():
                raise TokenExpiredError() from exc
            raise TokenInvalidError() from exc

        if payload.get("type") != "refresh":
            raise TokenInvalidError()

        user = self._user_repo.get_by_id(payload["sub"])
        if user is None or user.status != "ACTIVE":
            raise TokenInvalidError()

        return self._issue_tokens(user)

    def get_current_user_from_token(self, access_token: str) -> TokenPayload:
        try:
            payload = decode_token(access_token)
        except JWTError as exc:
            if "expired" in str(exc).lower():
                raise TokenExpiredError() from exc
            raise TokenInvalidError() from exc

        if payload.get("type") != "access":
            raise TokenInvalidError()

        return TokenPayload(
            sub=payload["sub"],
            type=payload["type"],
            roles=payload.get("roles", []),
            full_name=payload.get("full_name", ""),
        )

    def checkChangePassword(
        self, user_id: str, current_password: str, new_password: str
    ) -> None:
        user = self._user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User")

        if not verify_password(current_password, user.password_hash):
            raise InvalidCredentialsError()

        user.password_hash = hash_password(new_password)
        self._user_repo.flush()

        _write_auth_audit(
            self._db,
            event_type="PASSWORD_CHANGED",
            entity_id=user_id,
            actor_user_id=user_id,
            actor_name=user.full_name,
            detail={"username": user.username},
        )

        logger.info("password_changed", user_id=user_id)

    def logout(self, user_id: str) -> None:
        user = self._user_repo.get_by_id(user_id)
        actor_name = user.full_name if user else None

        _write_auth_audit(
            self._db,
            event_type="LOGOUT",
            entity_id=user_id,
            actor_user_id=user_id,
            actor_name=actor_name,
            detail={"username": user.username if user else "unknown"},
        )

        logger.info("logout", user_id=user_id)

    def _issue_tokens(self, user: Users) -> TokenResponse:
        from app.core.config import get_settings
        settings = get_settings()

        extra = {"roles": [user.role], "full_name": user.full_name or ""}
        access = create_access_token(subject=user.user_id, extra_claims=extra)
        refresh = create_refresh_token(subject=user.user_id)

        return TokenResponse(
            access_token=access,
            refresh_token=refresh,
            expires_in=settings.jwt_access_token_expire_minutes * 60,
            user_id=user.user_id,
            username=user.username,
            full_name=user.full_name or "",
            role=user.role,
        )
