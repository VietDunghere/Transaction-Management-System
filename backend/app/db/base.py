from __future__ import annotations
from typing import Optional, List, Dict, Any
"""
SQLAlchemy engine và SessionLocal.
Target: Oracle Database 19c với python-oracledb (Thin mode).
"""

from sqlalchemy import create_engine, event, pool
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# ---- Engine ----
_url = settings.database_url

if _url.startswith("sqlite"):
    # Dev fallback — SQLite không hỗ trợ pool_size
    engine = create_engine(
        _url,
        connect_args={"check_same_thread": False},
        echo=settings.debug,
    )
else:
    # Oracle (oracle+oracledb://...) hoặc PostgreSQL
    engine = create_engine(
        _url,
        pool_pre_ping=True,    # Kiểm tra connection trước khi dùng
        pool_size=10,
        max_overflow=20,
        pool_recycle=1800,     # Recycle connection sau 30 phút (tránh Oracle timeout)
        echo=settings.debug,
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
