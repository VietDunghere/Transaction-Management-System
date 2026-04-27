from __future__ import annotations
"""
Pydantic schemas: Demo Runner
Request/Response cho demo data generation endpoints.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DemoStartRequest(BaseModel):
    """Config for starting the demo runner."""
    rate: float = Field(
        default=1.0, ge=0.1, le=10.0,
        description="Requests per second (0.1 - 10)",
    )
    count: Optional[int] = Field(
        default=None, ge=1, le=10000,
        description="Total requests to send. null = run until stopped.",
    )
    loan_pct: int = Field(
        default=20, ge=0, le=100,
        description="Percentage of requests that are loan applications (0-100)",
    )


class DemoEvent(BaseModel):
    """Single event from the demo runner."""
    seq: int
    type: str          # "TXN" or "LOAN"
    result: str        # "APPROVED", "REJECTED", "MANUAL_REVIEW", "PENDING", "ERROR"
    score: Optional[float] = None
    amount: float
    info: str          # short description
    timestamp: datetime


class DemoStatusResponse(BaseModel):
    """Snapshot of the demo runner state."""
    running: bool
    started_by: Optional[str] = None
    started_at: Optional[datetime] = None
    config: Optional[DemoStartRequest] = None
    sent: int = 0
    stats: dict[str, int] = Field(default_factory=dict)
    recent_events: list[DemoEvent] = Field(default_factory=list)
