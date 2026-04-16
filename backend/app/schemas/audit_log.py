from __future__ import annotations
"""
Pydantic schemas: AuditLog
Response cho audit trail API — KHÔNG có write schema vì audit log là immutable.
Audit log chỉ được tạo bởi các service nội bộ, không qua API trực tiếp.
"""

import json
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, model_validator


def _safe_json_parse(raw: Optional[str]) -> Optional[dict]:
    """Parse JSON string thành dict — trả None nếu null hoặc parse lỗi."""
    if not raw:
        return None
    try:
        result = json.loads(raw)
        return result if isinstance(result, dict) else None
    except (json.JSONDecodeError, TypeError):
        return None


# ============================================================
# Response schemas
# ============================================================

class AuditLogListItem(BaseModel):
    """
    Summary row cho danh sách audit log.
    Không kèm detail để giữ response nhẹ — dùng GET /{log_id} để lấy đầy đủ.
    """
    log_id: str
    event_type: str
    entity_type: str
    entity_id: str
    actor_user_id: Optional[str] = None
    actor_name: Optional[str] = None
    event_ts: datetime

    model_config = {"from_attributes": True}


class AuditLogResponse(BaseModel):
    """
    Chi tiết đầy đủ một audit log event, kèm detail dạng dict.
    detail_json (Text column) được parse thành dict trước khi trả về client —
    client không cần double-parse JSON string.
    """
    log_id: str
    event_type: str
    entity_type: str
    entity_id: str
    actor_user_id: Optional[str] = None
    actor_name: Optional[str] = None
    event_ts: datetime
    detail: Optional[dict] = None

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def _coerce_orm_object(cls, data: Any) -> Any:
        """
        Khi input là ORM object (AuditLog), chuyển sang dict và parse detail_json.
        Khi input đã là dict, giữ nguyên.
        """
        if isinstance(data, dict):
            return data

        # ORM object — extract từng field tường minh để tránh phụ thuộc vào
        # from_attributes khi có model_validator override
        return {
            "log_id": data.log_id,
            "event_type": data.event_type,
            "entity_type": data.entity_type,
            "entity_id": data.entity_id,
            "actor_user_id": getattr(data, "actor_user_id", None),
            "actor_name": getattr(data, "actor_name", None),
            "event_ts": data.event_ts,
            "detail": _safe_json_parse(getattr(data, "detail_json", None)),
        }
