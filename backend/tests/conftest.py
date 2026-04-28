from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

import pytest

from app.schemas.auth import TokenPayload


class QueryStub:
    """Minimal SQLAlchemy-like query stub for route-level unit tests."""

    def __init__(
        self,
        *,
        all_result: list[Any] | None = None,
        first_result: Any = None,
        scalar_result: Any = None,
    ) -> None:
        self._all_result = list(all_result or [])
        self._first_result = first_result
        self._scalar_result = scalar_result
        self.filter_calls: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
        self.order_by_calls: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
        self.limit_calls: list[int] = []

    def filter(self, *args: Any, **kwargs: Any) -> "QueryStub":
        self.filter_calls.append((args, kwargs))
        return self

    def order_by(self, *args: Any, **kwargs: Any) -> "QueryStub":
        self.order_by_calls.append((args, kwargs))
        return self

    def limit(self, value: int) -> "QueryStub":
        self.limit_calls.append(value)
        return self

    def all(self) -> list[Any]:
        return self._all_result

    def first(self) -> Any:
        return self._first_result

    def scalar(self) -> Any:
        return self._scalar_result


class DbStub:
    """Small DB stub with sequential query return support."""

    def __init__(self, query_stubs: list[QueryStub] | None = None, *, strict: bool = True) -> None:
        self._query_stubs = list(query_stubs or [])
        self._strict = strict
        self.query_calls: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
        self.commit_calls = 0

    def query(self, *args: Any, **kwargs: Any) -> QueryStub:
        self.query_calls.append((args, kwargs))
        if self._query_stubs:
            return self._query_stubs.pop(0)
        if self._strict:
            raise AssertionError(f"Unexpected DB query call: args={args}, kwargs={kwargs}")
        return QueryStub()

    def commit(self) -> None:
        self.commit_calls += 1


@pytest.fixture
def make_obj():
    def _make_obj(**kwargs: Any) -> SimpleNamespace:
        return SimpleNamespace(**kwargs)

    return _make_obj


@pytest.fixture
def now_utc() -> datetime:
    return datetime(2026, 1, 15, 10, 30, tzinfo=timezone.utc)


@pytest.fixture
def token_admin() -> TokenPayload:
    return TokenPayload(
        sub="admin-1",
        type="access",
        roles=["ADMIN", "MANAGER", "ANALYST", "REVIEWER", "OPERATOR"],
        full_name="Admin User",
    )


@pytest.fixture
def token_manager() -> TokenPayload:
    return TokenPayload(
        sub="manager-1",
        type="access",
        roles=["MANAGER"],
        full_name="Manager User",
    )


@pytest.fixture
def token_reviewer() -> TokenPayload:
    return TokenPayload(
        sub="reviewer-1",
        type="access",
        roles=["REVIEWER"],
        full_name="Reviewer User",
    )


@pytest.fixture
def token_operator() -> TokenPayload:
    return TokenPayload(
        sub="operator-1",
        type="access",
        roles=["OPERATOR"],
        full_name="Operator User",
    )


@pytest.fixture
def db_stub() -> DbStub:
    return DbStub()
