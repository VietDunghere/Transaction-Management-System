from __future__ import annotations
"""
FastAPI dependency injection cho database session.
Đảm bảo session luôn được đóng sau mỗi request, kể cả khi có exception.
"""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.base import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Dependency trả về DB session cho mỗi request.
    Pattern try/finally đảm bảo session.close() luôn được gọi.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Type alias để dùng trong route handlers
# VD: def my_route(db: DbSession): ...
DbSession = Annotated[Session, Depends(get_db)]
