from __future__ import annotations

from datetime import datetime, timezone

from app.api.v1.routes import dashboard as dashboard_routes
from app.schemas.dashboard import DashboardSummary, FraudTrendResponse
from tests.conftest import DbStub


NOW = datetime(2026, 1, 15, 10, 30, tzinfo=timezone.utc)


def test_get_dashboard_summary_returns_service_payload(monkeypatch, db_stub: DbStub, token_admin) -> None:
    expected = DashboardSummary.model_validate(
        {
            "transactions": {
                "total": 100,
                "approved": 80,
                "rejected": 10,
                "manual_review": 5,
                "pending": 5,
                "today": 20,
                "this_week": 60,
            },
            "fraud": {
                "avg_fraud_score": 0.18,
                "rejection_rate": 0.1,
                "manual_review_rate": 0.05,
            },
            "cases": {
                "total_open": 3,
                "total_assigned": 7,
                "decided_today": 4,
            },
            "loans": {
                "total_pending": 11,
                "total_approved": 50,
                "total_rejected": 9,
            },
            "as_of": NOW,
        }
    )
    observed: dict[str, object] = {}

    class FakeService:
        def __init__(self, db):
            observed["db"] = db

        def get_summary(self):
            return expected

    monkeypatch.setattr(dashboard_routes, "DashboardService", FakeService)

    result = dashboard_routes.get_dashboard_summary(db=db_stub, token=token_admin)

    assert observed["db"] is db_stub
    assert result == expected


def test_get_fraud_trend_forwards_days(monkeypatch, db_stub: DbStub, token_admin) -> None:
    expected = FraudTrendResponse.model_validate(
        {
            "period": "daily",
            "lookback_days": 14,
            "data": [
                {
                    "period_label": "2026-01-01",
                    "period_start": "2026-01-01",
                    "total_txn": 10,
                    "approved": 8,
                    "rejected": 1,
                    "manual_review": 1,
                    "fraud_rate": 0.1,
                }
            ],
            "as_of": NOW,
        }
    )
    observed: dict[str, object] = {}

    class FakeService:
        def __init__(self, db):
            observed["db"] = db

        def get_fraud_trend(self, lookback_days):
            observed["lookback_days"] = lookback_days
            return expected

    monkeypatch.setattr(dashboard_routes, "DashboardService", FakeService)

    result = dashboard_routes.get_fraud_trend(db=db_stub, token=token_admin, days=14)

    assert observed["db"] is db_stub
    assert observed["lookback_days"] == 14
    assert result == expected
