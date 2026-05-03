from __future__ import annotations
"""
API Dependencies: Auth
FastAPI dependencies cho xác thực và phân quyền.
Inject vào route handlers để bảo vệ endpoints.
"""

from typing import Annotated

from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import PermissionDeniedError
from app.core.logging import get_logger
from app.db.deps import get_db
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.auth import TokenPayload
from app.services.auth_service import AuthService

logger = get_logger(__name__)

# Bearer token extractor
_bearer_scheme = HTTPBearer(auto_error=True)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Tạo AuthService với DB session hiện tại."""
    return AuthService(UserRepository(db))


def get_current_token(
    credentials: HTTPAuthorizationCredentials = Security(_bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenPayload:
    """
    Dependency: Validate Bearer token và trả TokenPayload.
    Inject vào bất kỳ route nào cần authentication.
    """
    return auth_service.get_current_user_from_token(credentials.credentials)


def get_current_user(
    token: TokenPayload = Depends(get_current_token),
    db: Session = Depends(get_db),
) -> User:
    """Dependency: Load full User object từ DB dựa vào token sub."""
    user = UserRepository(db).get_by_id(token.sub)
    if user is None:
        from app.core.exceptions import TokenInvalidError
        raise TokenInvalidError()
    return user


def require_roles(*roles: str):
    """
    Factory tạo dependency kiểm tra role.
    Dùng: Depends(require_roles("MANAGER", "ADMIN"))
    """
    def _check(token: TokenPayload = Depends(get_current_token)) -> TokenPayload:
        if "ADMIN" not in token.roles and not any(r in token.roles for r in roles):
            raise PermissionDeniedError(
                f"Yêu cầu một trong các quyền: {', '.join(roles)}"
            )
        return token
    return _check


# ---- Type aliases ----
CurrentToken = Annotated[TokenPayload, Depends(get_current_token)]
CurrentUser = Annotated[User, Depends(get_current_user)]
