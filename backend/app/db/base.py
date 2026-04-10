from __future__ import annotations
from typing import Optional, List, Dict, Any
"""
SQLAlchemy engine và SessionLocal.
Hỗ trợ cả PostgreSQL (production) lẫn SQLite (dev không có Docker).
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# ---- Engine ----
# SQLite cần thêm check_same_thread=False để dùng trong nhiều thread
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    # Pool size cho PostgreSQL — SQLite bỏ qua
    pool_pre_ping=True,       # Kiểm tra connection trước khi dùng
    pool_size=10,
    max_overflow=20,
    echo=settings.debug,      # Log SQL queries khi debug
)

# ---- Session factory ----
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,   # Đọc lại object sau commit không cần refresh
)


# ---- SQLAlchemy Base ----
class Base(DeclarativeBase):
    """Base class cho tất cả ORM models."""
    pass


def create_tables() -> None:
    """
    Tạo tất cả bảng từ ORM models.
    Gọi khi startup — trong production dùng Alembic migrate thay thế.
    """
    # Import tất cả models để Base biết cần tạo bảng nào
    from app.models import user, customer, merchant, transaction, scoring, case, card_velocity  # noqa: F401
    Base.metadata.create_all(bind=engine)
