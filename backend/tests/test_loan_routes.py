from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from app.api.v1.routes import loan as loan_routes
from app.schemas.loan import (
    LoanApplyRequest,
    LoanDecisionRequest,
    LoanResponse,
    LoanSimulationRequest,
)
from tests.conftest import DbStub, QueryStub


NOW = datetime(2026, 1, 15, 10, 30, tzinfo=timezone.utc)


def _loan_obj(make_obj, *, loan_id: str = "loan-1"):
    return make_obj(
        loan_id=loan_id,
        customer_id="cust-1",
        submitted_by="operator-1",
        reviewed_by=None,
        principal_amount=Decimal("10000.00"),
        currency_code="USD",
        interest_rate=Decimal("0.1200"),
        term_months=24,
        purpose="Home renovation budget planning",
        status="PENDING",
        version=1,
        monthly_payment=None,
        outstanding_balance=None,
        disbursed_at=None,
        maturity_date=None,
        review_note=None,
        reviewed_at=None,
        created_at=NOW,
        pd_score=0.32,
        risk_level="MEDIUM",
        person_age=35,
        person_income=70000.0,
        person_home_ownership="MORTGAGE",
        person_emp_length=8,
        loan_grade="C",
        loan_intent="HOMEIMPROVEMENT",
        cb_person_default_on_file="N",
        cb_person_cred_hist_length=10,
        customer=make_obj(
            full_name="Customer One",
            job="Engineer",
            kyc_status="VERIFIED",
            income_level="HIGH",
        ),
    )


def test_build_loan_response_enriches_customer_and_history(make_obj) -> None:
    loan_obj = _loan_obj(make_obj)
    db = DbStub(
        query_stubs=[
            QueryStub(
                all_result=[
                    make_obj(status="APPROVED"),
                    make_obj(status="REJECTED"),
                    make_obj(status="PENDING"),
                ]
            )
        ]
    )

    result = loan_routes._build_loan_response(loan_obj, db)

    assert result.loan_id == "loan-1"
    assert result.customer_name == "Customer One"
    assert result.customer_job == "Engineer"
    assert result.customer_kyc_status == "VERIFIED"
    assert result.customer_income_level == "HIGH"
    assert result.customer_loan_stats is not None
    assert result.customer_loan_stats.total_loans == 3
    assert result.customer_loan_stats.approved == 1
    assert result.customer_loan_stats.rejected == 1
    assert result.customer_loan_stats.active == 1


def test_apply_loan_forwards_actor_context(monkeypatch, db_stub: DbStub, token_operator, make_obj) -> None:
    loan_obj = _loan_obj(make_obj, loan_id="loan-2")
    observed: dict[str, object] = {}

    class FakeService:
        def __init__(self, db):
            observed["db"] = db

        def apply(self, body, submitted_by_user_id):
            observed["body"] = body
            observed["submitted_by_user_id"] = submitted_by_user_id
            return loan_obj

    monkeypatch.setattr(loan_routes, "LoanService", FakeService)

    body = LoanApplyRequest(
        customer_id="cust-1",
        principal_amount=Decimal("10000.00"),
        currency_code="USD",
        interest_rate=Decimal("0.1200"),
        term_months=24,
        purpose="Home renovation budget planning",
        person_age=35,
        person_income=70000,
        person_home_ownership="MORTGAGE",
        person_emp_length=8,
        loan_intent="HOMEIMPROVEMENT",
        loan_grade="C",
        cb_person_default_on_file="N",
        cb_person_cred_hist_length=10,
    )

    result = loan_routes.apply_loan(body=body, db=db_stub, token=token_operator)

    assert result.loan_id == "loan-2"
    assert observed["db"] is db_stub
    assert observed["body"] == body
    assert observed["submitted_by_user_id"] == token_operator.sub


def test_list_loans_adds_customer_name(monkeypatch, db_stub: DbStub, token_admin, make_obj) -> None:
    observed: dict[str, object] = {}
    loans = [_loan_obj(make_obj, loan_id="loan-3")]

    class FakeService:
        def __init__(self, db):
            observed["db"] = db

        def list_loans(self, **kwargs):
            observed["kwargs"] = kwargs
            return loans, 1

    monkeypatch.setattr(loan_routes, "LoanService", FakeService)

    result = loan_routes.list_loans(
        db=db_stub,
        token=token_admin,
        customer_id="cust-1",
        status=None,
        period="M",
        page=2,
        limit=5,
    )

    assert observed["db"] is db_stub
    assert observed["kwargs"]["customer_id"] == "cust-1"
    assert observed["kwargs"]["created_from"] is not None
    assert observed["kwargs"]["page"] == 2
    assert observed["kwargs"]["page_size"] == 5
    assert result.total == 1
    assert result.data[0].loan_id == "loan-3"
    assert result.data[0].customer_name == "Customer One"


def test_simulate_loan_uses_scoring_service(monkeypatch, token_admin) -> None:
    observed: dict[str, object] = {}

    class FakeScoringInstance:
        def simulate(self, payload):
            observed["payload"] = payload
            return type(
                "Out",
                (),
                {
                    "pd_score": 0.42,
                    "risk_level": "MEDIUM",
                    "top_risk_factors": ["loan_amnt", "loan_grade"],
                    "model_version": "loan_v6",
                },
            )()

    class FakeScoringService:
        @staticmethod
        def get_instance():
            return FakeScoringInstance()

    monkeypatch.setattr(loan_routes, "LoanScoringService", FakeScoringService)

    body = LoanSimulationRequest(
        person_age=30,
        person_income=60000,
        person_home_ownership="RENT",
        person_emp_length=4,
        loan_intent="PERSONAL",
        loan_grade="C",
        loan_amnt=12000,
        loan_int_rate=12.5,
        cb_person_default_on_file="N",
        cb_person_cred_hist_length=6,
    )

    result = loan_routes.simulate_loan(body=body, token=token_admin)

    payload = observed["payload"]
    assert payload.person_age == 30
    assert payload.loan_amnt == 12000
    assert result.pd_score == 0.42
    assert result.risk_level == "MEDIUM"
    assert result.model_version == "loan_v6"


def test_get_loan_delegates_to_builder(monkeypatch, db_stub: DbStub, token_admin, make_obj) -> None:
    observed: dict[str, object] = {}
    loan_obj = _loan_obj(make_obj, loan_id="loan-4")
    expected = LoanResponse.model_validate(loan_obj)

    class FakeService:
        def __init__(self, db):
            observed["db"] = db

        def get_loan(self, loan_id):
            observed["loan_id"] = loan_id
            return loan_obj

    def fake_builder(loan, db):
        observed["builder_input"] = (loan, db)
        return expected

    monkeypatch.setattr(loan_routes, "LoanService", FakeService)
    monkeypatch.setattr(loan_routes, "_build_loan_response", fake_builder)

    result = loan_routes.get_loan(loan_id="loan-4", db=db_stub, token=token_admin)

    assert result == expected
    assert observed["db"] is db_stub
    assert observed["loan_id"] == "loan-4"
    assert observed["builder_input"] == (loan_obj, db_stub)


def test_decide_loan_forwards_actor_and_delegates_builder(monkeypatch, db_stub: DbStub, token_admin, make_obj) -> None:
    observed: dict[str, object] = {}
    loan_obj = _loan_obj(make_obj, loan_id="loan-5")
    expected = LoanResponse.model_validate(loan_obj)

    class FakeService:
        def __init__(self, db):
            observed["db"] = db

        def decide(self, loan_id, body, actor_user_id):
            observed["loan_id"] = loan_id
            observed["body"] = body
            observed["actor_user_id"] = actor_user_id
            return loan_obj

    def fake_builder(loan, db):
        observed["builder_input"] = (loan, db)
        return expected

    monkeypatch.setattr(loan_routes, "LoanService", FakeService)
    monkeypatch.setattr(loan_routes, "_build_loan_response", fake_builder)

    body = LoanDecisionRequest(decision="APPROVE", review_note="Approved after checks", version=1)
    result = loan_routes.decide_loan(loan_id="loan-5", body=body, db=db_stub, token=token_admin)

    assert result == expected
    assert observed["db"] is db_stub
    assert observed["loan_id"] == "loan-5"
    assert observed["body"] == body
    assert observed["actor_user_id"] == token_admin.sub
    assert observed["builder_input"] == (loan_obj, db_stub)
