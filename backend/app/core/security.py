from __future__ import annotations
"""
Security utilities — JWT và password hashing.
Tất cả logic liên quan đến auth tập trung ở đây, không rải rác trong code.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.exc import UnknownHashError

from app.core.config import get_settings

settings = get_settings()

# Context cho bcrypt — slow hash để chống brute force
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================================
# Password utilities
# ============================================================

def hash_password(plain_password: str) -> str:
    """Hash mật khẩu bằng bcrypt trước khi lưu DB."""
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """So sánh mật khẩu nhập vào với hash đã lưu.

    Returns False (not 500) when the stored value is not a recognised hash
    format — handles rows seeded before proper bcrypt hashing was in place.
    """
    try:
        return _pwd_context.verify(plain_password, hashed_password)
    except UnknownHashError:
        return False


# ============================================================
# JWT utilities
# ============================================================

def create_access_token(subject: str, extra_claims: Optional[dict] = None) -> str:
    """
    Tạo JWT access token.

    Args:
        subject: user_id của người dùng (sub claim)
        extra_claims: Thông tin bổ sung như roles, full_name

    Returns:
        JWT string
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )
    payload = {
        "sub": subject,
        "exp": expire,
        "type": "access",
        **(extra_claims or {}),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str) -> str:
    """Tạo JWT refresh token — thời hạn dài hơn access token."""
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.jwt_refresh_token_expire_days
    )
    payload = {
        "sub": subject,
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    """
    Giải mã và validate JWT.

    Returns:
        Payload dict nếu hợp lệ.

    Raises:
        JWTError nếu token hết hạn hoặc chữ ký sai.
    """
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
