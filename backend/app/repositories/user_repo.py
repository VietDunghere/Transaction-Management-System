from __future__ import annotations
"""
Repository: User
Data access layer cho bảng users và roles.
Oracle-compatible: không dùng ILIKE, RETURNING, ARRAY.
"""

from typing import Optional, Tuple, List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.user import Role, User, UserRole


class UserRepository:
    """Thao tác DB cho User — chỉ query, không chứa business logic."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ---- Single lookups ----

    def get_by_id(self, user_id: str) -> Optional[User]:
        """Tìm user theo UUID."""
        return self._db.query(User).filter(User.user_id == user_id).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """Tìm user theo username (dùng khi login)."""
        return self._db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Tìm user theo email (check duplicate khi tạo)."""
        return self._db.query(User).filter(User.email == email).first()

    # ---- List with filters & pagination ----

    def list_users(
        self,
        *,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[User], int]:
        """
        Danh sách users với filter và phân trang.
        Oracle-compatible: dùng offset/limit qua SQLAlchemy (tự sinh ROWNUM/FETCH).
        Returns: (items, total_count)
        """
        query = self._db.query(User)

        # Filter by role — join user_roles + roles
        if role:
            query = (
                query.join(UserRole, User.user_id == UserRole.user_id)
                .join(Role, UserRole.role_id == Role.role_id)
                .filter(Role.role_name == role)
            )

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        total = query.count()
        items = (
            query.order_by(User.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    # ---- Mutations ----

    def create(self, user: User) -> User:
        """Thêm user mới vào DB."""
        self._db.add(user)
        return user

    def add_user_role(self, user_role: UserRole) -> None:
        """Gán role cho user."""
        self._db.add(user_role)

    def get_role_by_name(self, role_name: str) -> Optional[Role]:
        """Tìm Role entity theo tên."""
        return self._db.query(Role).filter(Role.role_name == role_name).first()

    def remove_user_roles(self, user_id: str) -> None:
        """Xoá tất cả roles của user (dùng trước khi gán role mới)."""
        self._db.query(UserRole).filter(UserRole.user_id == user_id).delete()

    def flush(self) -> None:
        """Flush pending changes (không commit)."""
        self._db.flush()
