from __future__ import annotations
"""
Repository: AuditLog
Data access layer cho bảng audit_logs.
Bảng này chỉ được đọc qua đây — mọi thao tác write đều do service nội bộ thực hiện
trực tiếp qua session.add(AuditLog(...)).
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from app.models.scoring import AuditLog
from app.models.user import User


# Danh sách entity_type hợp lệ để validate đầu vào
VALID_ENTITY_TYPES = frozenset({
    "Transaction",
    "ReviewCase",
    "Loan",
    "User",
    "Auth",
})


def _hydrate_actor_name(db: Session, logs: list[AuditLog]) -> list[AuditLog]:
    """Backfill actor_name from User table for logs that have it null."""
    missing = [log for log in logs if log.actor_name is None and log.actor_user_id]
    if not missing:
        return logs
    user_ids = list({log.actor_user_id for log in missing})
    rows = db.query(User.user_id, User.full_name).filter(User.user_id.in_(user_ids)).all()
    name_map = {r.user_id: r.full_name for r in rows}
    for log in missing:
        log.actor_name = name_map.get(log.actor_user_id)
    return logs


class AuditLogRepository:
    """Thao tác DB cho AuditLog — chỉ đọc."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, log_id: str) -> Optional[AuditLog]:
        """Lấy 1 audit log event theo primary key."""
        log = (
            self._db.query(AuditLog)
            .filter(AuditLog.log_id == log_id)
            .first()
        )
        if log:
            _hydrate_actor_name(self._db, [log])
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
        Danh sách audit log với filter đa tiêu chí và pagination.
        Kết quả sắp xếp theo event_ts giảm dần (mới nhất lên trước).

        Returns:
            (items, total_count)
        """
        query = self._db.query(AuditLog)

        filters = []
        if event_type:
            filters.append(AuditLog.event_type == event_type)
        if entity_type:
            filters.append(AuditLog.entity_type == entity_type)
        if actor_user_id:
            filters.append(AuditLog.actor_user_id == actor_user_id)
        if from_date:
            filters.append(AuditLog.event_ts >= from_date)
        if to_date:
            filters.append(AuditLog.event_ts <= to_date)

        if filters:
            query = query.filter(and_(*filters))

        total = query.count()
        items = (
            query.order_by(desc(AuditLog.event_ts))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        _hydrate_actor_name(self._db, items)
        return items, total

    def list_by_entity(
        self,
        entity_type: str,
        entity_id: str,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[AuditLog], int]:
        """
        Lấy toàn bộ audit log của một entity cụ thể.
        Sắp xếp theo event_ts tăng dần để dễ theo dõi vòng đời.
        VD: tất cả events của Transaction abc-123, Loan xyz-456.

        Returns:
            (items, total_count)
        """
        query = (
            self._db.query(AuditLog)
            .filter(
                AuditLog.entity_type == entity_type,
                AuditLog.entity_id == entity_id,
            )
        )

        total = query.count()
        items = (
            query.order_by(AuditLog.event_ts)   # tăng dần — timeline
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        _hydrate_actor_name(self._db, items)
        return items, total
