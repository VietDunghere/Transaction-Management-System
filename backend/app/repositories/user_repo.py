from __future__ import annotations
"""
Repository: User (ERD v2)
Direct role column — no Role/UserRole tables.
"""

from typing import Optional, Tuple, List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self._db.query(User).filter(User.user_id == user_id).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self._db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self._db.query(User).filter(User.email == email).first()

    def list_users(
        self,
        *,
        role: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[User], int]:
        query = self._db.query(User)

        if role:
            query = query.filter(User.role == role)

        if status:
            query = query.filter(User.status == status)

        total = query.count()
        items = (
            query.order_by(User.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def create(self, user: User) -> User:
        self._db.add(user)
        return user

    def flush(self) -> None:
        self._db.flush()
