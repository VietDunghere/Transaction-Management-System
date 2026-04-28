from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.api.v1.routes import transactions as txn_routes
from app.schemas.common import TransactionStatus
from app.schemas.transaction import TransactionSubmitRequest, TransactionSubmitResponse
from tests.conftest import DbStub


NOW = datetime(2026, 1, 15, 10, 30, tzinfo=timezone.utc)


def _txn_obj(make_obj, *, with_scoring: bool):
	scoring_results = []
	if with_scoring:
		scoring_results = [
			make_obj(
				reason_json='{"top_features": ["high_amount", "new_merchant"]}',
				fraud_score=0.81,
				decision_suggested="REJECTED",
				reject_threshold=0.65,
				review_threshold=0.35,
				model_version="rf_v3",
			)
		]

	return make_obj(
		txn_id="txn-1",
		customer_id="cust-1",
		merchant_id="mcht-1",
		channel_id=1,
		submitted_by="operator-1",
		card_number_masked="4111********1111",
		amount=Decimal("120.50"),
		currency_code="USD",
		txn_time=NOW,
		status=TransactionStatus.APPROVED,
		fraud_score=0.12,
		reason_code=None,
		override_reason=None,
		created_at=NOW,
		scoring_results=scoring_results,
	)


def test_submit_transaction_forwards_payload_and_actor(monkeypatch, db_stub: DbStub, token_operator) -> None:
	expected = TransactionSubmitResponse(
		txn_id="txn-1",
		status=TransactionStatus.APPROVED,
		fraud_score=0.1,
		decision="APPROVED",
		amount=Decimal("100.00"),
		currency_code="USD",
		created_at=NOW,
		message="ok",
		case_id=None,
	)
	observed: dict[str, object] = {}

	class FakeService:
		def __init__(self, db):
			observed["db"] = db

		def submit(self, body, submitted_by_user_id):
			observed["body"] = body
			observed["submitted_by_user_id"] = submitted_by_user_id
			return expected

	monkeypatch.setattr(txn_routes, "TransactionService", FakeService)

	body = TransactionSubmitRequest(
		card_number="4111111111111111",
		customer_id="cust-1",
		merchant_id="mcht-1",
		channel_id=1,
		amount=Decimal("100.00"),
		currency_code="USD",
		txn_time=NOW - timedelta(minutes=1),
		source_ip="10.0.0.1",
		idempotency_key="idem-1",
	)

	result = txn_routes.submit_transaction(body=body, db=db_stub, token=token_operator)

	assert result == expected
	assert observed["db"] is db_stub
	assert observed["body"] == body
	assert observed["submitted_by_user_id"] == token_operator.sub


def test_list_transactions_applies_period_and_pagination(monkeypatch, db_stub: DbStub, token_admin, make_obj) -> None:
	observed: dict[str, object] = {}
	items = [_txn_obj(make_obj, with_scoring=False)]

	class FakeService:
		def __init__(self, db):
			observed["db"] = db

		def list_transactions(self, **kwargs):
			observed["kwargs"] = kwargs
			return items, 1

	monkeypatch.setattr(txn_routes, "TransactionService", FakeService)

	result = txn_routes.list_transactions(
		db=db_stub,
		token=token_admin,
		status=TransactionStatus.APPROVED,
		customer_id="cust-1",
		merchant_id="mcht-1",
		from_date=None,
		to_date=None,
		min_amount=Decimal("10"),
		max_amount=Decimal("500"),
		period="W",
		page=3,
		limit=5,
	)

	assert observed["db"] is db_stub
	assert observed["kwargs"]["status"] == TransactionStatus.APPROVED
	assert observed["kwargs"]["customer_id"] == "cust-1"
	assert observed["kwargs"]["merchant_id"] == "mcht-1"
	assert observed["kwargs"]["page"] == 3
	assert observed["kwargs"]["page_size"] == 5
	assert observed["kwargs"]["min_amount"] == 10.0
	assert observed["kwargs"]["max_amount"] == 500.0
	assert observed["kwargs"]["date_from"] is not None
	assert result.total == 1
	assert len(result.data) == 1


def test_get_transaction_enriches_fraud_detail(monkeypatch, db_stub: DbStub, token_admin, make_obj) -> None:
	txn_obj = _txn_obj(make_obj, with_scoring=True)

	class FakeService:
		def __init__(self, db):
			self.db = db

		def get_transaction(self, txn_id):
			assert txn_id == "txn-1"
			return txn_obj

	monkeypatch.setattr(txn_routes, "TransactionService", FakeService)

	result = txn_routes.get_transaction(txn_id="txn-1", db=db_stub, token=token_admin)

	assert result.txn_id == "txn-1"
	assert result.fraud_detail is not None
	assert result.fraud_detail.fraud_score == 0.81
	assert result.fraud_detail.decision == "REJECTED"
	assert result.fraud_detail.top_risk_factors == ["high_amount", "new_merchant"]


def test_get_transaction_without_scoring_keeps_fraud_detail_none(monkeypatch, db_stub: DbStub, token_admin, make_obj) -> None:
	txn_obj = _txn_obj(make_obj, with_scoring=False)
	txn_obj.txn_id = "txn-plain"

	class FakeService:
		def __init__(self, db):
			self.db = db

		def get_transaction(self, txn_id):
			assert txn_id == "txn-plain"
			return txn_obj

	monkeypatch.setattr(txn_routes, "TransactionService", FakeService)

	result = txn_routes.get_transaction(txn_id="txn-plain", db=db_stub, token=token_admin)

	assert result.txn_id == "txn-plain"
	assert result.fraud_detail is None


def test_get_transaction_state_history_reads_repo(monkeypatch, db_stub: DbStub, token_admin, make_obj) -> None:
	observed: dict[str, object] = {}

	class FakeService:
		def __init__(self, db):
			observed["service_db"] = db

		def get_transaction(self, txn_id):
			observed["service_txn_id"] = txn_id
			return make_obj(txn_id=txn_id)

	class FakeRepo:
		def __init__(self, db):
			observed["repo_db"] = db

		def get_state_history(self, txn_id):
			observed["repo_txn_id"] = txn_id
			return [
				make_obj(
					state_hist_id="hist-1",
					txn_id=txn_id,
					old_status="PENDING",
					new_status="APPROVED",
					changed_by_user_id="reviewer-1",
					changed_at=NOW,
					change_reason="Validated",
				)
			]

	monkeypatch.setattr(txn_routes, "TransactionService", FakeService)
	monkeypatch.setattr(txn_routes, "TransactionRepository", FakeRepo)

	result = txn_routes.get_transaction_state_history(txn_id="txn-2", db=db_stub, token=token_admin)

	assert observed["service_db"] is db_stub
	assert observed["repo_db"] is db_stub
	assert observed["service_txn_id"] == "txn-2"
	assert observed["repo_txn_id"] == "txn-2"
	assert len(result) == 1
	assert result[0].state_hist_id == "hist-1"
	assert result[0].new_status == "APPROVED"
