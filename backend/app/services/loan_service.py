from __future__ import annotations
"""
Service: LoanService
Business logic cho loan application và approval workflow.

Flow:
  1. OPERATOR gửi đơn vay (apply) → PENDING
  2. MANAGER phê duyệt (decide APPROVE) → APPROVED, tính monthly_payment, set maturity_date
     hoặc từ chối (decide REJECT) → REJECTED
"""

import calendar
import json
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError, OptimisticLockError
from app.services.loan_scoring_service import LoanScoringService, LoanSimulationInput
from app.core.logging import get_logger
from app.models.loan import Loan
from app.models.scoring import AuditLog
from app.repositories.loan_repo import LoanRepository
from app.repositories.velocity_repo import CustomerRepository
from app.schemas.common import LoanDecision, LoanStatus
from app.schemas.loan import LoanApplyRequest, LoanDecisionRequest

logger = get_logger(__name__)

# Trạng thái cuối — không thể chuyển tiếp nữa ở Phase B
_TERMINAL_STATUSES = {LoanStatus.APPROVED.value, LoanStatus.REJECTED.value}


def _add_months(d: date, months: int) -> date:
    """
    Thêm N tháng vào ngày d — stdlib, không dùng thư viện ngoài.
    Xử lý đúng ngày cuối tháng: VD: Jan 31 + 1 month = Feb 28/29.
    """
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _calculate_monthly_payment(
    principal: Decimal, annual_rate: Decimal, term_months: int
) -> Decimal:
    """
    Tính tiền trả hàng tháng theo công thức amortisation:
        PMT = P × r × (1+r)ⁿ / ((1+r)ⁿ − 1)
    Với r = lãi suất tháng (annual_rate / 12), n = term_months.
    Nếu lãi suất = 0: PMT = P / n (không lãi).
    """
    if annual_rate == 0 or term_months == 0:
        return (principal / Decimal(term_months)).quantize(Decimal("0.01"))

    r = float(annual_rate) / 12
    n = term_months
    p = float(principal)
    pmt = p * r * (1 + r) ** n / ((1 + r) ** n - 1)
    return Decimal(str(round(pmt, 2)))


def _try_score_loan(loan: "Loan") -> None:  # noqa: F821
    """Gọi LoanScoringService nếu loan có đủ AI input features; no-op nếu thiếu."""
    if not all([
        loan.person_age, loan.person_income, loan.person_home_ownership,
        loan.person_emp_length is not None, loan.loan_grade, loan.loan_intent,
        loan.cb_person_default_on_file, loan.cb_person_cred_hist_length is not None,
    ]):
        return

    svc = LoanScoringService.get_instance()
    if not svc.is_ready:
        return

    inp = LoanSimulationInput(
        person_age=loan.person_age,
        person_income=float(loan.person_income),
        person_home_ownership=loan.person_home_ownership,
        person_emp_length=loan.person_emp_length,
        loan_intent=loan.loan_intent,
        loan_grade=loan.loan_grade,
        loan_amnt=float(loan.principal_amount),
        loan_int_rate=float(loan.interest_rate) * 100,  # model expects %, e.g. 12.0 not 0.12
        cb_person_default_on_file=loan.cb_person_default_on_file,
        cb_person_cred_hist_length=loan.cb_person_cred_hist_length,
    )
    result = svc.simulate(inp)
    loan.pd_score = result.pd_score
    loan.risk_level = result.risk_level


class LoanService:
    """Orchestrator cho loan application và approval."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._loan_repo = LoanRepository(db)
        self._customer_repo = CustomerRepository(db)

    # ============================================================
    # Public API
    # ============================================================

    def apply(self, request: LoanApplyRequest, submitted_by_user_id: str) -> Loan:
        """
        OPERATOR tạo đơn vay mới cho khách hàng.

        Raises:
            NotFoundError: nếu customer_id không tồn tại trong hệ thống
        """
        customer = self._customer_repo.get_by_id(request.customer_id)
        if customer is None:
            raise NotFoundError("Customer")

        loan = Loan(
            loan_id=str(uuid.uuid4()),
            customer_id=request.customer_id,
            submitted_by=submitted_by_user_id,
            principal_amount=request.principal_amount,
            currency_code=request.currency_code,
            interest_rate=request.interest_rate,
            term_months=request.term_months,
            purpose=request.purpose,
            status=LoanStatus.PENDING.value,
            version=1,
        )
        self._loan_repo.create(loan)
        self._write_audit(loan.loan_id, submitted_by_user_id, "LOAN_APPLIED", {
            "principal_amount": float(request.principal_amount),
            "interest_rate": float(request.interest_rate),
            "term_months": request.term_months,
            "purpose": request.purpose,
        })
        self._db.commit()

        logger.info(
            "loan_applied",
            loan_id=loan.loan_id,
            customer_id=request.customer_id,
            submitted_by=submitted_by_user_id,
        )
        return self._loan_repo.get_by_id(loan.loan_id)

    def get_loan(self, loan_id: str) -> Loan:
        """Lấy chi tiết 1 khoản vay theo ID."""
        loan = self._loan_repo.get_by_id(loan_id)
        if loan is None:
            raise NotFoundError("Loan")
        return loan

    def list_loans(self, **kwargs) -> tuple[list[Loan], int]:
        """Danh sách khoản vay với filter và pagination."""
        return self._loan_repo.list_loans(**kwargs)

    def decide(
        self,
        loan_id: str,
        request: LoanDecisionRequest,
        actor_user_id: str,
    ) -> Loan:
        """
        MANAGER phê duyệt hoặc từ chối khoản vay.

        - Optimistic locking: client phải gửi version hiện tại.
          Nếu version không khớp → 409 OptimisticLockError.
        - Chỉ loan ở trạng thái PENDING mới được quyết định.
        - Khi APPROVE: tính monthly_payment, set outstanding_balance, disbursed_at, maturity_date.

        Raises:
            NotFoundError: loan không tồn tại
            ConflictError: loan không ở PENDING
            OptimisticLockError: version lỗi thời
        """
        loan = self._loan_repo.get_by_id(loan_id)
        if loan is None:
            raise NotFoundError("Loan")

        if loan.status != LoanStatus.PENDING.value:
            raise ConflictError(
                f"Khoản vay đang ở trạng thái '{loan.status}', không thể thay đổi."
            )

        if loan.version != request.version:
            raise OptimisticLockError()

        now = datetime.now(timezone.utc)

        if request.decision == LoanDecision.APPROVE:
            monthly_pmt = _calculate_monthly_payment(
                Decimal(str(loan.principal_amount)),
                Decimal(str(loan.interest_rate)),
                loan.term_months,
            )
            loan.status = LoanStatus.APPROVED.value
            loan.monthly_payment = monthly_pmt
            loan.outstanding_balance = loan.principal_amount
            loan.disbursed_at = now
            loan.maturity_date = _add_months(now.date(), loan.term_months)

            # Populate pd_score / risk_level nếu loan có đủ AI features
            _try_score_loan(loan)
        else:
            loan.status = LoanStatus.REJECTED.value

        loan.reviewed_by = actor_user_id
        loan.reviewed_at = now
        loan.review_note = request.review_note
        loan.version += 1

        event_type = "LOAN_APPROVED" if request.decision == LoanDecision.APPROVE else "LOAN_REJECTED"
        self._write_audit(loan_id, actor_user_id, event_type, {
            "decision": request.decision.value,
            "review_note": request.review_note,
            "new_version": loan.version,
        })
        self._db.commit()

        logger.info(
            "loan_decided",
            loan_id=loan_id,
            decision=request.decision.value,
            actor=actor_user_id,
        )
        return self._loan_repo.get_by_id(loan_id)

    # ============================================================
    # Private helpers
    # ============================================================

    def _write_audit(
        self, entity_id: str, actor: str, event_type: str, detail: dict
    ) -> None:
        """Ghi audit log — không commit, để service tự commit sau."""
        audit = AuditLog(
            log_id=str(uuid.uuid4()),
            event_type=event_type,
            entity_type="Loan",
            entity_id=entity_id,
            actor_user_id=actor,
            detail_json=json.dumps(detail),
        )
        self._db.add(audit)
