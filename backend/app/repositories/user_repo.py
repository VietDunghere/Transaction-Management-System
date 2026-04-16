from __future__ import annotations
"""
Repository: User
Data access layer cho bảng users và roles.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Thao tác DB cho User — chỉ query, không chứa business logic."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, user_id: str) -> Optional[User]:
        """Tìm user theo UUID."""
        return self._db.query(User).filter(User.user_id == user_id).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """Tìm user theo username (dùng khi login)."""
        return self._db.query(User).filter(User.username == username).first()
