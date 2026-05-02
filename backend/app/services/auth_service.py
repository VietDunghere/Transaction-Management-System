from __future__ import annotations
"""
Service: AuthService (ERD v2)
user.status instead of user.is_active, user.role instead of user.roles.
"""

import json
import uuid
from typing import Optional

from jose import JWTError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    TokenExpiredError,
    TokenInvalidError,
    NotFoundError,
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
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.auth import TokenPayload, TokenResponse

logger = get_logger(__name__)


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


class AuthService:

    def __init__(self, user_repo: UserRepository, db: Optional[Session] = None) -> None:
        self._user_repo = user_repo
        self._db = db or user_repo._db

    def login(self, username: str, password: str) -> TokenResponse:
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

    def change_password(
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

    def _issue_tokens(self, user: User) -> TokenResponse:
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
