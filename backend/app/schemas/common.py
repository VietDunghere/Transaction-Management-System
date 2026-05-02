from __future__ import annotations
"""
Pydantic schemas: Common
Các schema dùng chung toàn ứng dụng: pagination, response wrapper, enums.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


# ============================================================
# Enums — dùng cả trong schema lẫn service
# ============================================================

class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MANUAL_REVIEW = "MANUAL_REVIEW"


class CaseStatus(str, Enum):
    OPEN = "OPEN"
    ASSIGNED = "ASSIGNED"
    CLOSED = "CLOSED"


class CaseDecision(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"


class LoanStatus(str, Enum):
    """Vòng đời khoản vay."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DISBURSED = "DISBURSED"
    CLOSED = "CLOSED"
    DEFAULTED = "DEFAULTED"


class LoanDecision(str, Enum):
    """Quyết định phê duyệt khoản vay."""
    APPROVE = "APPROVE"
    REJECT = "REJECT"


# ============================================================
# Response wrappers
# ============================================================

class PagedResponse(BaseModel, Generic[T]):
    """Generic response cho list APIs — flat format."""
    data: List[T]
    total: int
    page: int
    limit: int


class ErrorDetail(BaseModel):
    """Format lỗi chuẩn — đồng nhất toàn API."""
    code: str
    message: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
