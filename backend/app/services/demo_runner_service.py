from __future__ import annotations
"""
Service: DemoRunnerService
Singleton that runs a background asyncio task generating fake transactions
and loan applications through the existing service layer.

Only one demo can run at a time across all users.
"""

import asyncio
import random
import uuid
from collections import deque
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional

from app.core.logging import get_logger
from app.db.base import SessionLocal
from app.schemas.demo import DemoEvent, DemoStartRequest, DemoStatusResponse
from app.schemas.loan import LoanApplyRequest
from app.schemas.transaction import TransactionSubmitRequest
from app.services.loan_service import LoanService
from app.services.transaction_service import TransactionService

logger = get_logger(__name__)

# ── Seed data (same as demo_transactions.py) ─────────────────────────────────

CUSTOMERS = [
    "cust-0001-0000-0000-000000000001",
    "cust-0002-0000-0000-000000000002",
    "cust-0003-0000-0000-000000000003",
]
MERCHANTS = [
    "mcht-0001-0000-0000-000000000001",
    "mcht-0002-0000-0000-000000000002",
    "mcht-0003-0000-0000-000000000003",
    "mcht-0004-0000-0000-000000000004",
]
CHANNEL_IDS = [1, 2, 3, 4]

LOAN_INTENTS = ["PERSONAL", "EDUCATION", "MEDICAL", "VENTURE", "HOMEIMPROVEMENT", "DEBTCONSOLIDATION"]
HOME_OWNERSHIPS = ["RENT", "MORTGAGE", "OWN", "OTHER"]
LOAN_PURPOSES = [
    "Personal loan for home renovation project",
    "Education loan for university tuition fees",
    "Medical expense loan for surgery procedure",
    "Business venture startup capital funding",
    "Home improvement renovation and upgrade",
    "Debt consolidation to reduce monthly payments",
]


# ── Payload builders ──────────────────────────────────────────────────────────

def _random_card_number() -> str:
    """Generate a random 16-digit card number (Visa-like)."""
    return "4" + "".join(str(random.randint(0, 9)) for _ in range(15))


def _random_ip() -> str:
    return f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"


def _build_transaction() -> TransactionSubmitRequest:
    txn_time = datetime.now(timezone.utc) - timedelta(minutes=random.randint(0, 60 * 24))

    # 20% chance: large amount → likely triggers MANUAL_REVIEW or REJECTED
    if random.random() < 0.20:
        amount = round(random.uniform(3000, 8000), 2)
    else:
        amount = round(random.uniform(10, 500), 2)

    return TransactionSubmitRequest(
        card_number=_random_card_number(),
        customer_id=random.choice(CUSTOMERS),
        merchant_id=random.choice(MERCHANTS),
        channel_id=random.choice(CHANNEL_IDS),
        amount=Decimal(str(amount)),
        currency_code="USD",
        txn_time=txn_time,
        source_ip=_random_ip(),
        idempotency_key=str(uuid.uuid4()),
    )


def _build_loan() -> LoanApplyRequest:
    """Build loan with risk-stratified profiles (30% low / 40% med / 30% high)."""
    risk_bucket = random.choices(["low", "medium", "high"], weights=[30, 40, 30])[0]

    if risk_bucket == "low":
        grade = random.choice(["A", "B"])
        income = round(random.uniform(80_000, 200_000), 2)
        loan_amnt = round(random.uniform(2_000, 15_000), 2)
        int_rate_dec = round(random.uniform(0.05, 0.12), 4)
        default_file = random.choices(["Y", "N"], weights=[5, 95])[0]
        ownership = random.choice(["OWN", "MORTGAGE"])
        emp_length = random.randint(5, 30)
    elif risk_bucket == "medium":
        grade = random.choice(["C", "D"])
        income = round(random.uniform(35_000, 80_000), 2)
        loan_amnt = round(random.uniform(10_000, 30_000), 2)
        int_rate_dec = round(random.uniform(0.12, 0.18), 4)
        default_file = random.choices(["Y", "N"], weights=[20, 80])[0]
        ownership = random.choice(HOME_OWNERSHIPS)
        emp_length = random.randint(2, 15)
    else:
        grade = random.choice(["E", "F", "G"])
        income = round(random.uniform(20_000, 45_000), 2)
        loan_amnt = round(random.uniform(15_000, 40_000), 2)
        int_rate_dec = round(random.uniform(0.18, 0.25), 4)
        default_file = random.choices(["Y", "N"], weights=[40, 60])[0]
        ownership = random.choice(["RENT", "OTHER"])
        emp_length = random.randint(0, 8)

    age = random.randint(20, 65)
    emp_length = min(emp_length, max(0, age - 18))
    term = random.choice([12, 24, 36, 48, 60])
    cred_hist = random.randint(1, 30)

    return LoanApplyRequest(
        customer_id=random.choice(CUSTOMERS),
        principal_amount=Decimal(str(loan_amnt)),
        currency_code="USD",
        interest_rate=Decimal(str(int_rate_dec)),
        term_months=term,
        purpose=random.choice(LOAN_PURPOSES),
        person_age=age,
        person_income=income,
        person_home_ownership=ownership,
        person_emp_length=emp_length,
        loan_intent=random.choice(LOAN_INTENTS),
        loan_grade=grade,
        cb_person_default_on_file=default_file,
        cb_person_cred_hist_length=cred_hist,
    )


# ── Singleton service ─────────────────────────────────────────────────────────

class DemoRunnerService:
    """
    Singleton demo runner. One global instance, one task at a time.
    All public methods are safe to call from async FastAPI handlers.
    """

    _instance: Optional[DemoRunnerService] = None

    def __init__(self) -> None:
        self._task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
        self._running = False
        self._started_by: Optional[str] = None
        self._started_at: Optional[datetime] = None
        self._config: Optional[DemoStartRequest] = None
        self._sent = 0
        self._stats: dict[str, int] = {}
        self._events: deque[DemoEvent] = deque(maxlen=50)

    @classmethod
    def get_instance(cls) -> DemoRunnerService:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ── Public API ────────────────────────────────────────────────────────

    async def start(self, config: DemoStartRequest, user_id: str, username: str) -> DemoStatusResponse:
        async with self._lock:
            if self._running:
                raise DemoAlreadyRunningError(self._started_by)

            self._reset()
            self._config = config
            self._started_by = username
            self._started_at = datetime.now(timezone.utc)
            self._running = True
            self._task = asyncio.create_task(self._run_loop(config, user_id))
            logger.info("demo_started", user=username, rate=config.rate, count=config.count)
            return self.status()

    async def stop(self) -> DemoStatusResponse:
        async with self._lock:
            if self._task and not self._task.done():
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass
            snapshot = self.status()
            self._running = False
            self._task = None
            logger.info("demo_stopped", sent=self._sent)
            return snapshot

    def status(self) -> DemoStatusResponse:
        return DemoStatusResponse(
            running=self._running,
            started_by=self._started_by,
            started_at=self._started_at,
            config=self._config,
            sent=self._sent,
            stats=dict(self._stats),
            recent_events=list(self._events),
        )

    # ── Internal ──────────────────────────────────────────────────────────

    def _reset(self) -> None:
        self._sent = 0
        self._stats = {
            "TXN_APPROVED": 0, "TXN_REJECTED": 0, "TXN_MANUAL_REVIEW": 0,
            "LOAN_PENDING": 0, "ERROR": 0,
        }
        self._events.clear()

    async def _run_loop(self, config: DemoStartRequest, user_id: str) -> None:
        delay = 1.0 / config.rate

        try:
            while config.count is None or self._sent < config.count:
                is_loan = random.randint(1, 100) <= config.loan_pct
                try:
                    if is_loan:
                        event = await asyncio.to_thread(self._do_loan, user_id)
                    else:
                        event = await asyncio.to_thread(self._do_transaction, user_id)
                    self._events.append(event)
                except Exception as exc:
                    self._stats["ERROR"] = self._stats.get("ERROR", 0) + 1
                    self._sent += 1
                    self._events.append(DemoEvent(
                        seq=self._sent,
                        type="ERR",
                        result="ERROR",
                        score=None,
                        amount=0,
                        info=str(exc)[:80],
                        timestamp=datetime.now(timezone.utc),
                    ))
                    logger.warning("demo_iteration_error", error=str(exc))

                await asyncio.sleep(delay)

        except asyncio.CancelledError:
            pass
        finally:
            self._running = False

    def _do_transaction(self, user_id: str) -> DemoEvent:
        """Run one transaction — called in a thread to avoid blocking the loop."""
        db = SessionLocal()
        try:
            payload = _build_transaction()
            svc = TransactionService(db)
            result = svc.submit(payload, submitted_by_user_id=user_id)

            self._sent += 1
            status = result.status
            key = f"TXN_{status}"
            self._stats[key] = self._stats.get(key, 0) + 1

            return DemoEvent(
                seq=self._sent,
                type="TXN",
                result=str(status),
                score=result.fraud_score,
                amount=float(result.amount),
                info=result.decision,
                timestamp=datetime.now(timezone.utc),
            )
        finally:
            db.close()

    def _do_loan(self, user_id: str) -> DemoEvent:
        """Run one loan application — called in a thread."""
        db = SessionLocal()
        try:
            payload = _build_loan()
            svc = LoanService(db)
            loan = svc.apply(payload, submitted_by_user_id=user_id)

            self._sent += 1
            self._stats["LOAN_PENDING"] = self._stats.get("LOAN_PENDING", 0) + 1

            risk = getattr(loan, "risk_level", None) or "—"
            pd = getattr(loan, "pd_score", None)
            grade = payload.loan_grade or "?"

            return DemoEvent(
                seq=self._sent,
                type="LOAN",
                result="PENDING",
                score=pd,
                amount=float(payload.principal_amount),
                info=f"{grade} | {risk}",
                timestamp=datetime.now(timezone.utc),
            )
        finally:
            db.close()


class DemoAlreadyRunningError(Exception):
    def __init__(self, started_by: Optional[str] = None):
        self.started_by = started_by
        super().__init__(f"Demo already running (started by {started_by})")
