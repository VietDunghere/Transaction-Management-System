from __future__ import annotations

from app.api.v1.routes import health as health_routes


class _ConnOK:
    def __init__(self) -> None:
        self.execute_called = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, _query):
        self.execute_called = True
        return None


class _ConnFail:
    def __enter__(self):
        raise RuntimeError("db unavailable")

    def __exit__(self, exc_type, exc, tb):
        return False


def test_health_check_ok(monkeypatch) -> None:
    conn = _ConnOK()

    class FakeEngine:
        @staticmethod
        def connect():
            return conn

    class FakeScoringSvc:
        @staticmethod
        def get_instance():
            return type("Scoring", (), {"is_ready": True})()

    monkeypatch.setattr(health_routes, "engine", FakeEngine)
    monkeypatch.setattr(health_routes, "FraudScoringService", FakeScoringSvc)
    monkeypatch.setattr(health_routes, "settings", type("Cfg", (), {"app_env": "test"})())

    result = health_routes.health_check()

    assert result.status == "ok"
    assert result.environment == "test"
    assert result.checks["database"] == "ok"
    assert result.checks["fraud_model"] == "ok"
    assert conn.execute_called is True


def test_health_check_degraded_when_model_not_loaded(monkeypatch) -> None:
    conn = _ConnOK()

    class FakeEngine:
        @staticmethod
        def connect():
            return conn

    class FakeScoringSvc:
        @staticmethod
        def get_instance():
            return type("Scoring", (), {"is_ready": False})()

    monkeypatch.setattr(health_routes, "engine", FakeEngine)
    monkeypatch.setattr(health_routes, "FraudScoringService", FakeScoringSvc)
    monkeypatch.setattr(health_routes, "settings", type("Cfg", (), {"app_env": "staging"})())

    result = health_routes.health_check()

    assert result.status == "degraded"
    assert result.environment == "staging"
    assert result.checks["database"] == "ok"
    assert result.checks["fraud_model"] == "not_loaded"
    assert conn.execute_called is True


def test_health_check_down_when_database_fails(monkeypatch) -> None:
    class FakeEngine:
        @staticmethod
        def connect():
            return _ConnFail()

    class FakeScoringSvc:
        @staticmethod
        def get_instance():
            return type("Scoring", (), {"is_ready": True})()

    monkeypatch.setattr(health_routes, "engine", FakeEngine)
    monkeypatch.setattr(health_routes, "FraudScoringService", FakeScoringSvc)
    monkeypatch.setattr(health_routes, "settings", type("Cfg", (), {"app_env": "prod"})())

    result = health_routes.health_check()

    assert result.status == "down"
    assert result.environment == "prod"
    assert result.checks["fraud_model"] == "ok"
    assert result.checks["database"].startswith("error:")
