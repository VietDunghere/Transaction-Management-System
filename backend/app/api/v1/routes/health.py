from __future__ import annotations
"""
Router: Health Check
GET /health — kiểm tra trạng thái hệ thống cho load balancer và monitoring.
"""

from datetime import datetime, timezone
from typing import Dict

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text

from app.core.config import get_settings
from app.db.base import engine
from app.services.fraud_scoring_service import FraudScoringService

router = APIRouter(prefix="/health", tags=["System"])
settings = get_settings()


class HealthResponse(BaseModel):
    status: str                        # ok | degraded | down
    version: str = "1.0.0"
    environment: str
    timestamp: datetime
    checks: Dict[str, str]


@router.get(
    "",
    response_model=HealthResponse,
    summary="Health check",
    description="Kiểm tra trạng thái DB và ML model. Dùng cho load balancer liveness/readiness probe.",
)
def health_check() -> HealthResponse:
    """
    Kiểm tra:
    - DB connection
    - ML model loaded
    """
    checks: Dict[str, str] = {}

    # ---- DB check ----
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:
        checks["database"] = f"error: {exc}"

    # ---- Model check ----
    scoring_svc = FraudScoringService.get_instance()
    checks["fraud_model"] = "ok" if scoring_svc.is_ready else "not_loaded"

    # ---- Overall status ----
    all_ok = all(v == "ok" for v in checks.values())
    db_ok = checks.get("database") == "ok"
    status = "ok" if all_ok else ("degraded" if db_ok else "down")

    return HealthResponse(
        status=status,
        environment=settings.app_env,
        timestamp=datetime.now(timezone.utc),
        checks=checks,
    )
