from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.api.v1.routes import cases as case_routes
from app.core.exceptions import PermissionDeniedError
from app.schemas.case import CaseDecideRequest, CaseResponse
from tests.conftest import DbStub, QueryStub


NOW = datetime(2026, 1, 15, 10, 30, tzinfo=timezone.utc)


def test_list_cases_blocks_reviewer_filtering_other_assignee(monkeypatch, db_stub: DbStub, token_reviewer) -> None:
	class FakeService:
		def __init__(self, db):
			self.db = db

	monkeypatch.setattr(case_routes, "CaseService", FakeService)

	with pytest.raises(PermissionDeniedError):
		case_routes.list_cases(
			db=db_stub,
			token=token_reviewer,
			case_status=None,
			assigned_to="someone-else",
			period=None,
			page=1,
			limit=20,
		)


def test_list_cases_maps_summary_with_assignee_name(monkeypatch, token_manager, make_obj) -> None:
	case_obj = make_obj(
		case_id="case-1",
		txn_id="txn-1",
		case_status="ASSIGNED",
		assigned_to="reviewer-1",
		created_at=NOW,
		transaction=make_obj(
			fraud_score=0.77,
			amount=Decimal("350.00"),
			txn_time=NOW,
		),
	)
	db = DbStub(
		query_stubs=[
			QueryStub(all_result=[make_obj(user_id="reviewer-1", full_name="Reviewer One")])
		]
	)
	observed: dict[str, object] = {}

	class FakeService:
		def __init__(self, db_session):
			observed["db"] = db_session

		def list_cases(self, **kwargs):
			observed["kwargs"] = kwargs
			return [case_obj], 1

	monkeypatch.setattr(case_routes, "CaseService", FakeService)

	result = case_routes.list_cases(
		db=db,
		token=token_manager,
		case_status=None,
		assigned_to=None,
		period="D",
		page=2,
		limit=5,
	)

	assert observed["db"] is db
	assert observed["kwargs"]["page"] == 2
	assert observed["kwargs"]["page_size"] == 5
	assert observed["kwargs"]["reviewer_queue_for"] is None
	assert observed["kwargs"]["created_from"] is not None
	assert result.total == 1
	assert result.data[0].assigned_to_name == "Reviewer One"
	assert result.data[0].fraud_score == 0.77


def test_get_case_blocks_reviewer_on_other_assignment(monkeypatch, db_stub: DbStub, token_reviewer, make_obj) -> None:
	case_obj = make_obj(
		case_id="case-2",
		txn_id="txn-2",
		case_status="ASSIGNED",
		assigned_to="reviewer-2",
		decision=None,
		decision_note=None,
		version=1,
		created_at=NOW,
		decided_at=None,
		transaction=None,
		actions=[],
	)

	class FakeService:
		def __init__(self, db):
			self.db = db

		def get_case(self, case_id):
			assert case_id == "case-2"
			return case_obj

	monkeypatch.setattr(case_routes, "CaseService", FakeService)

	with pytest.raises(PermissionDeniedError):
		case_routes.get_case(case_id="case-2", db=db_stub, token=token_reviewer)


def test_get_case_enriches_transaction_details(monkeypatch, token_manager, make_obj) -> None:
	txn_obj = make_obj(
		txn_id="txn-9",
		customer_id="cust-1",
		card_number_hash="card-hash-1",
		amount=Decimal("420.00"),
		currency_code="USD",
		txn_time=NOW,
		fraud_score=0.66,
		merchant=make_obj(merchant_name="Shop", merchant_category="ELECTRONICS", risk_level="HIGH"),
		customer=make_obj(full_name="Customer 1"),
		channel=make_obj(channel_name="POS"),
		source_ip="10.0.0.9",
		card_number_masked="4111********1111",
	)
	case_obj = make_obj(
		case_id="case-9",
		txn_id="txn-9",
		case_status="ASSIGNED",
		assigned_to="reviewer-1",
		decision=None,
		decision_note=None,
		version=3,
		created_at=NOW,
		decided_at=None,
		transaction=txn_obj,
		actions=[
			make_obj(
				action_id="act-1",
				action_type="ASSIGN",
				actor_user_id="manager-1",
				action_note="Assigned",
				created_at=NOW,
			)
		],
	)

	db = DbStub(
		query_stubs=[
			QueryStub(first_result=make_obj(avg_daily_txn=3.2, total_txn=40, avg_amt=120.5, std_amt=20.1)),
			QueryStub(
				all_result=[
					make_obj(
						txn_id="txn-old-1",
						amount=Decimal("100.00"),
						currency_code="USD",
						merchant=make_obj(merchant_name="Cafe"),
						status="APPROVED",
						fraud_score=0.1,
						txn_time=NOW,
					)
				]
			),
			QueryStub(
				all_result=[
					make_obj(rule_code="R001", rule_name="High Amount", hit_value="420", severity="HIGH")
				]
			),
			QueryStub(scalar_result="Reviewer One"),
		]
	)

	class FakeService:
		def __init__(self, db_session):
			self.db = db_session

		def get_case(self, case_id):
			assert case_id == "case-9"
			return case_obj

	monkeypatch.setattr(case_routes, "CaseService", FakeService)

	result = case_routes.get_case(case_id="case-9", db=db, token=token_manager)

	assert result.case_id == "case-9"
	assert result.assigned_to_name == "Reviewer One"
	assert result.transaction is not None
	assert result.transaction.card_velocity is not None
	assert result.transaction.card_velocity.total_txn == 40
	assert len(result.transaction.rule_hits) == 1
	assert result.transaction.rule_hits[0].rule_code == "R001"
	assert len(result.transaction.recent_transactions) == 1
	assert len(result.actions) == 1


def test_assign_case_calls_self_assign_then_returns_case(monkeypatch, db_stub: DbStub, token_reviewer) -> None:
	observed: dict[str, object] = {}
	expected = CaseResponse.model_validate(
		{
			"case_id": "case-3",
			"txn_id": "txn-3",
			"case_status": "ASSIGNED",
			"assigned_to": "reviewer-1",
			"decision": None,
			"decision_note": None,
			"version": 1,
			"created_at": NOW,
			"decided_at": None,
			"transaction": None,
			"actions": [],
		}
	)

	class FakeService:
		def __init__(self, db):
			observed["db"] = db

		def self_assign(self, case_id, reviewer_user_id):
			observed["case_id"] = case_id
			observed["reviewer_user_id"] = reviewer_user_id

	def fake_get_case(case_id, db, token):
		observed["get_case_called_with"] = (case_id, db, token.sub)
		return expected

	monkeypatch.setattr(case_routes, "CaseService", FakeService)
	monkeypatch.setattr(case_routes, "get_case", fake_get_case)

	result = case_routes.assign_case(case_id="case-3", db=db_stub, token=token_reviewer)

	assert result == expected
	assert observed["db"] is db_stub
	assert observed["case_id"] == "case-3"
	assert observed["reviewer_user_id"] == token_reviewer.sub
	assert observed["get_case_called_with"] == ("case-3", db_stub, token_reviewer.sub)


def test_decide_case_calls_service_then_returns_updated_case(monkeypatch, db_stub: DbStub, token_manager) -> None:
	observed: dict[str, object] = {}
	expected = CaseResponse.model_validate(
		{
			"case_id": "case-4",
			"txn_id": "txn-4",
			"case_status": "APPROVED",
			"assigned_to": "reviewer-1",
			"decision": "APPROVE",
			"decision_note": "Valid transaction after manual verification.",
			"version": 2,
			"created_at": NOW,
			"decided_at": NOW,
			"transaction": None,
			"actions": [],
		}
	)

	class FakeService:
		def __init__(self, db):
			observed["db"] = db

		def decide(self, case_id, body, actor_user_id, actor_roles):
			observed["case_id"] = case_id
			observed["body"] = body
			observed["actor_user_id"] = actor_user_id
			observed["actor_roles"] = actor_roles

	def fake_get_case(case_id, db, token):
		observed["get_case_called_with"] = (case_id, db, token.sub)
		return expected

	monkeypatch.setattr(case_routes, "CaseService", FakeService)
	monkeypatch.setattr(case_routes, "get_case", fake_get_case)

	body = CaseDecideRequest(
		decision="APPROVE",
		decision_note="Valid transaction after manual verification.",
		version=1,
	)

	result = case_routes.decide_case(case_id="case-4", body=body, db=db_stub, token=token_manager)

	assert result == expected
	assert observed["db"] is db_stub
	assert observed["case_id"] == "case-4"
	assert observed["body"] == body
	assert observed["actor_user_id"] == token_manager.sub
	assert observed["actor_roles"] == token_manager.roles
	assert observed["get_case_called_with"] == ("case-4", db_stub, token_manager.sub)
