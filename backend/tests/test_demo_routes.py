from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from app.api.v1.routes import demo as demo_routes
from app.schemas.auth import TokenPayload
from app.schemas.demo import DemoStartRequest, DemoStatusResponse


NOW = datetime(2026, 1, 15, 10, 30, tzinfo=timezone.utc)


def _status(running: bool) -> DemoStatusResponse:
    return DemoStatusResponse.model_validate(
        {
            "running": running,
            "started_by": "operator",
            "started_at": NOW,
            "config": {"rate": 1.0, "count": 10, "loan_pct": 20},
            "sent": 3,
            "stats": {"TXN_APPROVED": 2, "ERROR": 1},
            "recent_events": [],
        }
    )


@pytest.mark.asyncio
async def test_start_demo_returns_status(monkeypatch, token_operator) -> None:
    observed: dict[str, object] = {}

    class FakeRunner:
        async def start(self, body, user_id, username):
            observed["body"] = body
            observed["user_id"] = user_id
            observed["username"] = username
            return _status(True)

    monkeypatch.setattr(demo_routes, "_get_runner", lambda: FakeRunner())

    body = DemoStartRequest(rate=1.5, count=5, loan_pct=40)

    result = await demo_routes.start_demo(body=body, token=token_operator)

    assert result.running is True
    assert observed["body"] == body
    assert observed["user_id"] == token_operator.sub
    assert observed["username"] == token_operator.full_name


@pytest.mark.asyncio
async def test_start_demo_returns_conflict_if_already_running(monkeypatch, token_operator) -> None:
    class FakeRunner:
        async def start(self, body, user_id, username):
            raise demo_routes.DemoAlreadyRunningError("demo is running")

    monkeypatch.setattr(demo_routes, "_get_runner", lambda: FakeRunner())

    body = DemoStartRequest(rate=1.0, count=10, loan_pct=20)
    response = await demo_routes.start_demo(body=body, token=token_operator)

    payload = json.loads(response.body.decode("utf-8"))
    assert response.status_code == 409
    assert payload["code"] == "DEMO_ALREADY_RUNNING"
    assert "demo is running" in payload["message"]


@pytest.mark.asyncio
async def test_start_demo_uses_fallback_username_when_full_name_empty(monkeypatch) -> None:
    observed: dict[str, object] = {}

    class FakeRunner:
        async def start(self, body, user_id, username):
            observed["username"] = username
            return _status(True)

    token_without_name = TokenPayload(sub="operator-1", type="access", roles=["OPERATOR"], full_name="")
    monkeypatch.setattr(demo_routes, "_get_runner", lambda: FakeRunner())

    body = DemoStartRequest(rate=1.0, count=1, loan_pct=0)
    await demo_routes.start_demo(body=body, token=token_without_name)

    assert observed["username"] == "operator"


@pytest.mark.asyncio
async def test_stop_demo_returns_snapshot(monkeypatch, token_operator) -> None:
    observed: dict[str, object] = {"called": False}

    class FakeRunner:
        async def stop(self):
            observed["called"] = True
            return _status(False)

    monkeypatch.setattr(demo_routes, "_get_runner", lambda: FakeRunner())

    result = await demo_routes.stop_demo(token=token_operator)

    assert observed["called"] is True
    assert result.running is False


@pytest.mark.asyncio
async def test_demo_status_returns_current_state(monkeypatch, token_operator) -> None:
    observed: dict[str, object] = {"called": False}

    class FakeRunner:
        def status(self):
            observed["called"] = True
            return _status(True)

    monkeypatch.setattr(demo_routes, "_get_runner", lambda: FakeRunner())

    result = await demo_routes.demo_status(token=token_operator)

    assert observed["called"] is True
    assert result.running is True
