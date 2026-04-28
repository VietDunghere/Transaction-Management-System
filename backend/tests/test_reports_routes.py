from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone
from decimal import Decimal

from app.api.v1.routes import reports as report_routes
from tests.conftest import DbStub


NOW = datetime(2026, 1, 15, 10, 30, tzinfo=timezone.utc)


def test_export_transactions_json_format(monkeypatch, db_stub: DbStub, token_admin, make_obj) -> None:
    observed: dict[str, object] = {}

    class FakeRepo:
        def __init__(self, db):
            observed["db"] = db

        def get_transactions_for_export(self, **kwargs):
            observed["kwargs"] = kwargs
            return [
                make_obj(
                    txn_id="txn-1",
                    customer_id="cust-1",
                    merchant_id="mcht-1",
                    channel_id=1,
                    card_number_masked="4111********1111",
                    amount=Decimal("123.45"),
                    currency_code="USD",
                    txn_time=NOW,
                    status="APPROVED",
                    fraud_score=0.12,
                    reason_code=None,
                    created_at=NOW,
                )
            ]

    monkeypatch.setattr(report_routes, "DashboardRepository", FakeRepo)

    response = report_routes.export_transactions(
        db=db_stub,
        token=token_admin,
        format="json",
        status="APPROVED",
        from_date=NOW,
        to_date=NOW,
    )

    payload = json.loads(response.body.decode("utf-8"))
    assert observed["db"] is db_stub
    assert observed["kwargs"]["status"] == "APPROVED"
    assert observed["kwargs"]["from_date"] == NOW
    assert observed["kwargs"]["to_date"] == NOW
    assert observed["kwargs"]["max_rows"] == 5000
    assert payload[0]["txn_id"] == "txn-1"
    assert payload[0]["amount"] == 123.45
    assert payload[0]["status"] == "APPROVED"


def test_export_transactions_csv_format(monkeypatch, db_stub: DbStub, token_admin, make_obj) -> None:
    class FakeRepo:
        def __init__(self, db):
            self.db = db

        def get_transactions_for_export(self, **kwargs):
            return [
                make_obj(
                    txn_id="txn-2",
                    customer_id="cust-2",
                    merchant_id="mcht-2",
                    channel_id=2,
                    card_number_masked="5555********4444",
                    amount=Decimal("200.00"),
                    currency_code="USD",
                    txn_time=NOW,
                    status="REJECTED",
                    fraud_score=0.88,
                    reason_code="HIGH_FRAUD_SCORE",
                    created_at=NOW,
                )
            ]

    monkeypatch.setattr(report_routes, "DashboardRepository", FakeRepo)

    response = report_routes.export_transactions(
        db=db_stub,
        token=token_admin,
        format="csv",
        status=None,
        from_date=None,
        to_date=None,
    )

    content = response.body.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))
    rows = list(reader)

    assert "attachment; filename=\"transactions_" in response.headers["Content-Disposition"]
    assert reader.fieldnames == [
        "txn_id",
        "customer_id",
        "merchant_id",
        "channel_id",
        "card_number_masked",
        "amount",
        "currency_code",
        "txn_time",
        "status",
        "fraud_score",
        "reason_code",
        "created_at",
    ]
    assert len(rows) == 1
    assert rows[0]["txn_id"] == "txn-2"
    assert rows[0]["customer_id"] == "cust-2"
    assert rows[0]["merchant_id"] == "mcht-2"
    assert rows[0]["status"] == "REJECTED"


def test_export_fraud_report_json_pivots_daily_status(monkeypatch, db_stub: DbStub, token_admin) -> None:
    observed: dict[str, object] = {}

    class FakeRepo:
        def __init__(self, db):
            observed["db"] = db

        def get_fraud_summary_for_export(self, from_date, to_date):
            observed["from_date"] = from_date
            observed["to_date"] = to_date
            return [
                {"day": "2026-01-10", "status": "APPROVED", "cnt": 8, "avg_score": 0.10},
                {"day": "2026-01-10", "status": "REJECTED", "cnt": 2, "avg_score": 0.80},
                {"day": "2026-01-11", "status": "MANUAL_REVIEW", "cnt": 3, "avg_score": 0.45},
            ]

    monkeypatch.setattr(report_routes, "DashboardRepository", FakeRepo)

    response = report_routes.export_fraud_report(
        db=db_stub,
        token=token_admin,
        format="json",
        from_date=NOW,
        to_date=NOW,
    )

    payload = json.loads(response.body.decode("utf-8"))
    first = payload[0]
    assert observed["db"] is db_stub
    assert observed["from_date"] == NOW
    assert observed["to_date"] == NOW
    assert first["date"] == "2026-01-10"
    assert first["total_txn"] == 10
    assert first["approved"] == 8
    assert first["rejected"] == 2
    assert first["fraud_rate"] == 0.2


def test_export_fraud_report_csv_format(monkeypatch, db_stub: DbStub, token_admin) -> None:
    class FakeRepo:
        def __init__(self, db):
            self.db = db

        def get_fraud_summary_for_export(self, from_date, to_date):
            return [
                {"day": "2026-01-12", "status": "APPROVED", "cnt": 4, "avg_score": 0.12},
                {"day": "2026-01-12", "status": "PENDING", "cnt": 1, "avg_score": 0.00},
            ]

    monkeypatch.setattr(report_routes, "DashboardRepository", FakeRepo)

    response = report_routes.export_fraud_report(
        db=db_stub,
        token=token_admin,
        format="csv",
        from_date=None,
        to_date=None,
    )

    content = response.body.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))
    rows = list(reader)

    assert "attachment; filename=\"fraud_report_" in response.headers["Content-Disposition"]
    assert reader.fieldnames == [
        "date",
        "total_txn",
        "approved",
        "rejected",
        "manual_review",
        "pending",
        "fraud_rate",
        "avg_fraud_score",
    ]
    assert len(rows) == 1
    assert rows[0]["date"] == "2026-01-12"
    assert rows[0]["total_txn"] == "5"
    assert rows[0]["approved"] == "4"
    assert rows[0]["pending"] == "1"
    assert rows[0]["fraud_rate"] == "0.0"
    assert rows[0]["avg_fraud_score"] == "0.12"
