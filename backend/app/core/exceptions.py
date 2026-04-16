from __future__ import annotations
from typing import Optional, List, Dict, Any
"""
Định nghĩa các HTTP exception chuẩn dùng toàn ứng dụng.
Tập trung ở đây để dễ maintain — thay đổi error format 1 chỗ, áp dụng toàn bộ.
"""

from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base exception cho toàn bộ ứng dụng."""
    pass


# ============================================================
# Auth exceptions
# ============================================================

class InvalidCredentialsError(AppException):
    """Sai username hoặc password."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Thông tin đăng nhập không hợp lệ.",
            headers={"WWW-Authenticate": "Bearer"},
        )


class TokenExpiredError(AppException):
    """JWT token đã hết hạn."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token đã hết hạn. Vui lòng đăng nhập lại.",
            headers={"WWW-Authenticate": "Bearer"},
        )


class TokenInvalidError(AppException):
    """JWT token không hợp lệ (sai format hoặc chữ ký)."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ.",
            headers={"WWW-Authenticate": "Bearer"},
        )


class InactiveUserError(AppException):
    """Tài khoản đã bị vô hiệu hoá."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị vô hiệu hoá.",
        )


class PermissionDeniedError(AppException):
    """Không đủ quyền truy cập resource này."""
    def __init__(self, detail: str = "Không có quyền thực hiện thao tác này."):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


# ============================================================
# Resource exceptions
# ============================================================

class NotFoundError(AppException):
    """Resource không tồn tại."""
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} không tồn tại.",
        )


class ConflictError(AppException):
    """Xung đột dữ liệu (VD: duplicate key, optimistic lock)."""
    def __init__(self, detail: str = "Dữ liệu đã tồn tại hoặc đang được xử lý."):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class IdempotencyConflictError(AppException):
    """Request trùng lặp — đã xử lý trước đó."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Giao dịch này đã được xử lý trước đó (idempotency key trùng).",
        )


# ============================================================
# Business logic exceptions
# ============================================================

class ModelNotLoadedError(AppException):
    """Model AI chưa được load — không thể score."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model phát hiện gian lận chưa sẵn sàng. Vui lòng thử lại sau.",
        )


class CaseAlreadyDecidedError(AppException):
    """Case đã có quyết định, không thể thay đổi."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Case này đã được quyết định và không thể thay đổi.",
        )


class OptimisticLockError(AppException):
    """Phiên bản dữ liệu đã thay đổi — cần reload và thử lại."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Dữ liệu đã được cập nhật bởi người khác. Vui lòng tải lại và thử lại.",
        )
