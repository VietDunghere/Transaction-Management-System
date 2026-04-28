from __future__ import annotations

import pytest

from app.api.v1.routes import auth as auth_routes
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse
from app.schemas.user import ChangePasswordRequest
from tests.conftest import DbStub


def _token_response() -> TokenResponse:
	return TokenResponse(
		access_token="access-token",
		refresh_token="refresh-token",
		token_type="bearer",
		expires_in=3600,
		user_id="user-1",
		username="operator01",
		full_name="Operator 01",
		role="OPERATOR",
	)


def test_login_commits_and_returns_token(db_stub: DbStub) -> None:
	expected = _token_response()
	observed: dict[str, object] = {}

	class FakeAuthService:
		def login(self, username, password):
			observed["username"] = username
			observed["password"] = password
			return expected

	body = LoginRequest(username="operator01", password="secret123")

	result = auth_routes.login(body=body, db=db_stub, auth_service=FakeAuthService())

	assert result == expected
	assert observed["username"] == body.username
	assert observed["password"] == body.password
	assert db_stub.commit_calls == 1


def test_login_does_not_commit_on_service_error(db_stub: DbStub) -> None:
	class FakeAuthService:
		def login(self, username, password):
			raise RuntimeError("auth backend unavailable")

	body = LoginRequest(username="operator01", password="secret123")

	with pytest.raises(RuntimeError, match="auth backend unavailable"):
		auth_routes.login(body=body, db=db_stub, auth_service=FakeAuthService())

	assert db_stub.commit_calls == 0


def test_logout_commits_and_returns_message(db_stub: DbStub, token_admin) -> None:
	observed: dict[str, object] = {}

	class FakeAuthService:
		def logout(self, user_id):
			observed["user_id"] = user_id

	result = auth_routes.logout(token=token_admin, db=db_stub, auth_service=FakeAuthService())

	assert result.message == "Đăng xuất thành công."
	assert observed["user_id"] == token_admin.sub
	assert db_stub.commit_calls == 1


def test_me_maps_current_user_payload(make_obj) -> None:
	current_user = make_obj(
		user_id="user-1",
		username="reviewer01",
		full_name="Reviewer 01",
		roles=["REVIEWER"],
		is_active=True,
	)

	result = auth_routes.me(user=current_user)

	assert result.user_id == "user-1"
	assert result.username == "reviewer01"
	assert result.full_name == "Reviewer 01"
	assert result.role == "REVIEWER"
	assert result.is_active is True


def test_change_password_forwards_context_and_commits(db_stub: DbStub, token_admin) -> None:
	observed: dict[str, object] = {}

	class FakeAuthService:
		def change_password(self, user_id, current_password, new_password):
			observed["user_id"] = user_id
			observed["current_password"] = current_password
			observed["new_password"] = new_password

	body = ChangePasswordRequest(
		current_password="old-password-1",
		new_password="new-password-1",
		confirm_password="new-password-1",
	)

	result = auth_routes.change_password(
		body=body,
		db=db_stub,
		token=token_admin,
		auth_service=FakeAuthService(),
	)

	assert result.message == "Đổi mật khẩu thành công."
	assert observed["user_id"] == token_admin.sub
	assert observed["current_password"] == "old-password-1"
	assert observed["new_password"] == "new-password-1"
	assert db_stub.commit_calls == 1


def test_refresh_token_returns_new_token() -> None:
	expected = _token_response()
	observed: dict[str, object] = {}

	class FakeAuthService:
		def refresh(self, refresh_token):
			observed["refresh_token"] = refresh_token
			return expected

	body = RefreshRequest(refresh_token="refresh-token")

	result = auth_routes.refresh_token(body=body, auth_service=FakeAuthService())

	assert result == expected
	assert observed["refresh_token"] == "refresh-token"
