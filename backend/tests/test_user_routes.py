from __future__ import annotations

from datetime import datetime, timezone

from app.api.v1.routes import users as user_routes
from app.schemas.user import (
    CreateUserRequest,
    CreateUserResponse,
    UserRoleUpdateRequest,
    UserRoleUpdateResponse,
)
from tests.conftest import DbStub


NOW = datetime(2026, 1, 15, 10, 30, tzinfo=timezone.utc)


def test_list_users_builds_paged_response(monkeypatch, db_stub: DbStub, token_admin, make_obj) -> None:
    observed: dict[str, object] = {}
    users = [
        make_obj(
            user_id="user-1",
            username="operator01",
            full_name="Operator 01",
            role="OPERATOR",
            status="ACTIVE",
            created_at=NOW,
        )
    ]

    class FakeService:
        def __init__(self, db):
            observed["db"] = db

        def list_users(self, **kwargs):
            observed["kwargs"] = kwargs
            return users, 1

    monkeypatch.setattr(user_routes, "UserService", FakeService)

    result = user_routes.list_users(
        db=db_stub,
        token=token_admin,
        role="OPERATOR",
        status="ACTIVE",
        page=2,
        limit=10,
    )

    assert observed["db"] is db_stub
    assert observed["kwargs"] == {
        "role": "OPERATOR",
        "status": "ACTIVE",
        "page": 2,
        "page_size": 10,
    }
    assert result.total == 1
    assert result.page == 2
    assert result.limit == 10
    assert len(result.data) == 1
    assert result.data[0].user_id == "user-1"
    assert result.data[0].role == "OPERATOR"


def test_get_user_maps_domain_user(monkeypatch, db_stub: DbStub, token_admin, make_obj) -> None:
    user_obj = make_obj(
        user_id="user-1",
        username="reviewer01",
        full_name="Reviewer 01",
        email="reviewer01@tms.local",
        role="REVIEWER",
        status="ACTIVE",
        created_at=NOW,
        updated_at=NOW,
    )

    class FakeService:
        def __init__(self, db):
            self.db = db

        def get_user(self, user_id):
            assert user_id == "user-1"
            return user_obj

    monkeypatch.setattr(user_routes, "UserService", FakeService)

    result = user_routes.get_user(user_id="user-1", db=db_stub, token=token_admin)

    assert result.user_id == "user-1"
    assert result.username == "reviewer01"
    assert result.role == "REVIEWER"
    assert result.email == "reviewer01@tms.local"


def test_create_user_forwards_actor_user_id(monkeypatch, db_stub: DbStub, token_admin) -> None:
    expected = CreateUserResponse(
        user_id="user-2",
        username="analyst01",
        role="ANALYST",
        created_at=NOW,
    )
    observed: dict[str, object] = {}

    class FakeService:
        def __init__(self, db):
            observed["db"] = db

        def create_user(self, body, actor_user_id):
            observed["body"] = body
            observed["actor_user_id"] = actor_user_id
            return expected

    monkeypatch.setattr(user_routes, "UserService", FakeService)

    body = CreateUserRequest(
        username="analyst01",
        full_name="Analyst 01",
        email="analyst01@tms.local",
        password="secure-pass-123",
        role="ANALYST",
    )

    result = user_routes.create_user(body=body, db=db_stub, token=token_admin)

    assert result == expected
    assert observed["db"] is db_stub
    assert observed["body"] == body
    assert observed["actor_user_id"] == token_admin.sub


def test_disable_user_calls_service_and_returns_message(monkeypatch, db_stub: DbStub, token_admin) -> None:
    observed: dict[str, object] = {}

    class FakeService:
        def __init__(self, db):
            observed["db"] = db

        def disable_user(self, user_id, actor_user_id):
            observed["user_id"] = user_id
            observed["actor_user_id"] = actor_user_id

    monkeypatch.setattr(user_routes, "UserService", FakeService)

    result = user_routes.disable_user(user_id="user-3", db=db_stub, token=token_admin)

    assert observed["db"] is db_stub
    assert observed["user_id"] == "user-3"
    assert observed["actor_user_id"] == token_admin.sub
    assert result.message == "Tài khoản user-3 đã bị vô hiệu hoá."


def test_enable_user_calls_service_and_returns_message(monkeypatch, db_stub: DbStub, token_admin) -> None:
    observed: dict[str, object] = {}

    class FakeService:
        def __init__(self, db):
            observed["db"] = db

        def enable_user(self, user_id, actor_user_id):
            observed["user_id"] = user_id
            observed["actor_user_id"] = actor_user_id

    monkeypatch.setattr(user_routes, "UserService", FakeService)

    result = user_routes.enable_user(user_id="user-4", db=db_stub, token=token_admin)

    assert observed["db"] is db_stub
    assert observed["user_id"] == "user-4"
    assert observed["actor_user_id"] == token_admin.sub
    assert result.message == "Tài khoản user-4 đã được kích hoạt lại."


def test_update_role_forwards_payload_and_actor(monkeypatch, db_stub: DbStub, token_admin) -> None:
    expected = UserRoleUpdateResponse(user_id="user-5", role="MANAGER", updated_at=NOW)
    observed: dict[str, object] = {}

    class FakeService:
        def __init__(self, db):
            observed["db"] = db

        def update_role(self, user_id, body, actor_user_id):
            observed["user_id"] = user_id
            observed["body"] = body
            observed["actor_user_id"] = actor_user_id
            return expected

    monkeypatch.setattr(user_routes, "UserService", FakeService)

    body = UserRoleUpdateRequest(role="MANAGER")

    result = user_routes.update_role(user_id="user-5", body=body, db=db_stub, token=token_admin)

    assert result == expected
    assert observed["db"] is db_stub
    assert observed["user_id"] == "user-5"
    assert observed["body"] == body
    assert observed["actor_user_id"] == token_admin.sub
