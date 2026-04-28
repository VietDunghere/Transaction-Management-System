from __future__ import annotations

from datetime import datetime, timezone

from app.api.v1.routes import audit_logs as audit_routes
from tests.conftest import DbStub


NOW = datetime(2026, 1, 15, 10, 30, tzinfo=timezone.utc)


def _audit_obj(make_obj, *, log_id: str = "log-1"):
	return make_obj(
		log_id=log_id,
		event_type="CASE_APPROVED",
		entity_type="ReviewCase",
		entity_id="case-1",
		actor_user_id="reviewer-1",
		actor_name="Reviewer One",
		event_ts=NOW,
		detail_json='{"decision": "APPROVE"}',
	)


def test_list_audit_logs_returns_paged_items(monkeypatch, db_stub: DbStub, token_admin, make_obj) -> None:
	observed: dict[str, object] = {}
	items = [_audit_obj(make_obj, log_id="log-11")]

	class FakeService:
		def __init__(self, db):
			observed["db"] = db

		def list_logs(self, **kwargs):
			observed["kwargs"] = kwargs
			return items, 1

	monkeypatch.setattr(audit_routes, "AuditService", FakeService)

	result = audit_routes.list_audit_logs(
		db=db_stub,
		token=token_admin,
		event_type="CASE_APPROVED",
		entity_type="ReviewCase",
		actor_user_id="reviewer-1",
		from_date=NOW,
		to_date=NOW,
		page=2,
		limit=10,
	)

	assert observed["db"] is db_stub
	assert observed["kwargs"]["event_type"] == "CASE_APPROVED"
	assert observed["kwargs"]["entity_type"] == "ReviewCase"
	assert observed["kwargs"]["actor_user_id"] == "reviewer-1"
	assert observed["kwargs"]["page"] == 2
	assert observed["kwargs"]["page_size"] == 10
	assert result.total == 1
	assert result.data[0].log_id == "log-11"


def test_list_entity_audit_logs_returns_paged_audit_trail(monkeypatch, db_stub: DbStub, token_admin, make_obj) -> None:
	observed: dict[str, object] = {}
	items = [_audit_obj(make_obj, log_id="log-21")]

	class FakeService:
		def __init__(self, db):
			observed["db"] = db

		def list_by_entity(self, entity_type, entity_id, page, page_size):
			observed["entity_type"] = entity_type
			observed["entity_id"] = entity_id
			observed["page"] = page
			observed["page_size"] = page_size
			return items, 1

	monkeypatch.setattr(audit_routes, "AuditService", FakeService)

	result = audit_routes.list_entity_audit_logs(
		entity_type="ReviewCase",
		entity_id="case-22",
		db=db_stub,
		token=token_admin,
		page=3,
		limit=50,
	)

	assert observed["db"] is db_stub
	assert observed["entity_type"] == "ReviewCase"
	assert observed["entity_id"] == "case-22"
	assert observed["page"] == 3
	assert observed["page_size"] == 50
	assert result.total == 1
	assert result.data[0].log_id == "log-21"
	assert result.data[0].detail == {"decision": "APPROVE"}


def test_get_audit_log_returns_detail_payload(monkeypatch, db_stub: DbStub, token_admin, make_obj) -> None:
	observed: dict[str, object] = {}
	item = _audit_obj(make_obj, log_id="log-31")

	class FakeService:
		def __init__(self, db):
			observed["db"] = db

		def get_log(self, log_id):
			observed["log_id"] = log_id
			return item

	monkeypatch.setattr(audit_routes, "AuditService", FakeService)

	result = audit_routes.get_audit_log(log_id="log-31", db=db_stub, token=token_admin)

	assert observed["db"] is db_stub
	assert observed["log_id"] == "log-31"
	assert result.log_id == "log-31"
	assert result.detail == {"decision": "APPROVE"}
