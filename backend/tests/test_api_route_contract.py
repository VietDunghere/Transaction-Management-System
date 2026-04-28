from __future__ import annotations

from fastapi.routing import APIRoute

from main import app


EXPECTED_ENDPOINTS = {
    ("GET", "/api/v1/analyst/thresholds"),
    ("PATCH", "/api/v1/analyst/thresholds"),
    ("GET", "/api/v1/analyst/model-performance/fraud"),
    ("GET", "/api/v1/analyst/model-performance/loan"),
    ("POST", "/api/v1/auth/login"),
    ("POST", "/api/v1/auth/logout"),
    ("GET", "/api/v1/auth/me"),
    ("PATCH", "/api/v1/auth/change-password"),
    ("POST", "/api/v1/auth/refresh"),
    ("GET", "/api/v1/users"),
    ("GET", "/api/v1/users/{user_id}"),
    ("POST", "/api/v1/users"),
    ("PATCH", "/api/v1/users/{user_id}/disable"),
    ("PATCH", "/api/v1/users/{user_id}/enable"),
    ("PATCH", "/api/v1/users/{user_id}/role"),
    ("POST", "/api/v1/transactions/submit"),
    ("GET", "/api/v1/transactions"),
    ("GET", "/api/v1/transactions/{txn_id}"),
    ("GET", "/api/v1/transactions/{txn_id}/state-history"),
    ("GET", "/api/v1/cases"),
    ("GET", "/api/v1/cases/{case_id}"),
    ("POST", "/api/v1/cases/{case_id}/assign"),
    ("PATCH", "/api/v1/cases/{case_id}/decision"),
    ("POST", "/api/v1/loans"),
    ("GET", "/api/v1/loans"),
    ("POST", "/api/v1/loans/simulate"),
    ("GET", "/api/v1/loans/{loan_id}"),
    ("PATCH", "/api/v1/loans/{loan_id}/decision"),
    ("GET", "/api/v1/audit-logs"),
    ("GET", "/api/v1/audit-logs/entities/{entity_type}/{entity_id}"),
    ("GET", "/api/v1/audit-logs/{log_id}"),
    ("GET", "/api/v1/dashboard/summary"),
    ("GET", "/api/v1/dashboard/fraud-trend"),
    ("POST", "/api/v1/demo/start"),
    ("POST", "/api/v1/demo/stop"),
    ("GET", "/api/v1/demo/status"),
    ("GET", "/api/v1/reports/transactions"),
    ("GET", "/api/v1/reports/fraud"),
    ("GET", "/api/v1/health"),
}


def test_all_api_v1_routes_are_covered_by_contract() -> None:
    actual: set[tuple[str, str]] = set()
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        if not route.path.startswith("/api/v1/"):
            continue
        for method in route.methods:
            if method in {"HEAD", "OPTIONS"}:
                continue
            actual.add((method, route.path))

    assert actual == EXPECTED_ENDPOINTS
    assert len(actual) == 39
