from __future__ import annotations
"""
Service: AuditService
Business logic cho audit log queries.
Audit log là immutable — service này CHỈ đọc, không bao giờ write hay update.
"""

from datetime import datetime
from typing import Optional

from fastapi import status
from sqlalchemy.orm import Session

from app.core.exceptions import AppException, NotFoundError
from app.models.scoring import AuditLog
from app.repositories.audit_repo import AuditLogRepository, VALID_ENTITY_TYPES


class AuditService:
    """Query audit log — read-only."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = AuditLogRepository(db)

    def get_log(self, log_id: str) -> AuditLog:
        """
        Lấy chi tiết 1 audit event theo ID.

        Raises:
            NotFoundError: nếu log_id không tồn tại
        """
        log = self._repo.get_by_id(log_id)
        if log is None:
            raise NotFoundError("AuditLog")
        return log

    def list_logs(
        self,
        event_type: Optional[str] = None,
        entity_type: Optional[str] = None,
        actor_user_id: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[AuditLog], int]:
        """
        Danh sách audit log với filter đa tiêu chí.
        Validates entity_type nếu được cung cấp.
        """
        if entity_type and entity_type not in VALID_ENTITY_TYPES:
            raise AppException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"entity_type '{entity_type}' không hợp lệ. "
                    f"Các giá trị được phép: {sorted(VALID_ENTITY_TYPES)}"
                ),
            )

        return self._repo.list_logs(
            event_type=event_type,
            entity_type=entity_type,
            actor_user_id=actor_user_id,
            from_date=from_date,
            to_date=to_date,
            page=page,
            page_size=page_size,
        )

    def list_by_entity(
        self,
        entity_type: str,
        entity_id: str,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[AuditLog], int]:
        """
        Lấy toàn bộ audit trail của một entity cụ thể.

        Raises:
            AppException (422): nếu entity_type không hợp lệ
        """
        if entity_type not in VALID_ENTITY_TYPES:
            raise AppException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"entity_type '{entity_type}' không hợp lệ. "
                    f"Các giá trị được phép: {sorted(VALID_ENTITY_TYPES)}"
                ),
            )

        return self._repo.list_by_entity(
            entity_type=entity_type,
            entity_id=entity_id,
            page=page,
            page_size=page_size,
        )
