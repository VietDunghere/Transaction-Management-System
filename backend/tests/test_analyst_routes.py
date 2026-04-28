from __future__ import annotations

from app.api.v1.routes import analyst as analyst_routes
from app.schemas.analyst import (
    FraudModelPerformanceResponse,
    FraudScoreDistribution,
    LoanModelPerformanceResponse,
    LoanRiskDistribution,
    ThresholdItem,
    ThresholdListResponse,
    ThresholdUpdateRequest,
)
from tests.conftest import DbStub


def _threshold_response() -> ThresholdListResponse:
    return ThresholdListResponse(
        fraud=[
            ThresholdItem(
                model_name="fraud",
                param_name="reject_threshold",
                param_value=0.65,
                description="reject",
                updated_by="admin-1",
                updated_at="2026-01-15T10:30:00Z",
                version=2,
            )
        ],
        loan=[
            ThresholdItem(
                model_name="loan",
                param_name="high_risk_threshold",
                param_value=0.5,
                description="high risk",
                updated_by="admin-1",
                updated_at="2026-01-15T10:30:00Z",
                version=3,
            )
        ],
    )


def test_get_thresholds_returns_service_payload(monkeypatch, db_stub: DbStub, token_admin) -> None:
    expected = _threshold_response()

    class FakeService:
        def __init__(self, db):
            self.db = db

        def get_thresholds(self):
            return expected

    monkeypatch.setattr(analyst_routes, "AnalystService", FakeService)

    result = analyst_routes.get_thresholds(db=db_stub, token=token_admin)

    assert result == expected


def test_update_thresholds_forwards_actor_context(monkeypatch, db_stub: DbStub, token_admin) -> None:
    expected = _threshold_response()
    observed: dict[str, object] = {}

    class FakeService:
        def __init__(self, db):
            observed["db"] = db

        def update_thresholds(self, body, actor_user_id):
            observed["body"] = body
            observed["actor_user_id"] = actor_user_id
            return expected

    monkeypatch.setattr(analyst_routes, "AnalystService", FakeService)

    body = ThresholdUpdateRequest.model_validate(
        {
            "updates": [
                {
                    "model_name": "fraud",
                    "param_name": "review_threshold",
                    "param_value": 0.35,
                }
            ]
        }
    )

    result = analyst_routes.update_thresholds(body=body, db=db_stub, token=token_admin)

    assert result == expected
    assert observed["db"] is db_stub
    assert observed["body"] == body
    assert observed["actor_user_id"] == token_admin.sub


def test_fraud_model_performance_forwards_days(monkeypatch, db_stub: DbStub, token_admin) -> None:
    expected = FraudModelPerformanceResponse(
        period_days=14,
        score_distribution=FraudScoreDistribution(
            approved_count=5,
            review_count=2,
            rejected_count=1,
            total=8,
            approved_rate=0.625,
            review_rate=0.25,
            rejected_rate=0.125,
            false_positive_count=0,
            false_positive_rate=0.0,
        ),
        current_thresholds={"reject_threshold": 0.65, "review_threshold": 0.35},
    )
    observed: dict[str, object] = {}

    class FakeService:
        def __init__(self, db):
            observed["db"] = db

        def get_fraud_performance(self, days):
            observed["days"] = days
            return expected

    monkeypatch.setattr(analyst_routes, "AnalystService", FakeService)

    result = analyst_routes.fraud_model_performance(db=db_stub, token=token_admin, days=14)

    assert result == expected
    assert observed["db"] is db_stub
    assert observed["days"] == 14


def test_loan_model_performance_forwards_days(monkeypatch, db_stub: DbStub, token_admin) -> None:
    expected = LoanModelPerformanceResponse(
        period_days=30,
        risk_distribution=LoanRiskDistribution(
            low_risk_count=4,
            medium_risk_count=3,
            high_risk_count=1,
            total=8,
            low_risk_rate=0.5,
            medium_risk_rate=0.375,
            high_risk_rate=0.125,
            approved_count=5,
            rejected_count=1,
            pending_count=2,
        ),
        current_thresholds={"high_risk_threshold": 0.5, "medium_risk_threshold": 0.2},
    )
    observed: dict[str, object] = {}

    class FakeService:
        def __init__(self, db):
            observed["db"] = db

        def get_loan_performance(self, days):
            observed["days"] = days
            return expected

    monkeypatch.setattr(analyst_routes, "AnalystService", FakeService)

    result = analyst_routes.loan_model_performance(db=db_stub, token=token_admin, days=30)

    assert result == expected
    assert observed["db"] is db_stub
    assert observed["days"] == 30
