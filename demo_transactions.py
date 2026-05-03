"""
Demo script: gửi transaction và loan liên tục lên backend FastAPI.
Chạy: python demo_transactions.py

Script này bám theo API hiện tại:
- POST /auth/login
- GET  /lookup/customers
- GET  /lookup/merchants
- GET  /lookup/channels
- POST /transactions/submit
- POST /loans
"""

from __future__ import annotations

import argparse
import random
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import requests

LOAN_INTENTS = ["PERSONAL", "EDUCATION", "MEDICAL", "VENTURE", "HOMEIMPROVEMENT", "DEBTCONSOLIDATION"]
LOAN_GRADES = ["A", "B", "C", "D", "E", "F", "G"]
HOME_OWNERSHIPS = ["RENT", "MORTGAGE", "OWN", "OTHER"]
LOAN_PURPOSES = [
    "Personal loan for home renovation project",
    "Education loan for university tuition fees",
    "Medical expense loan for surgery procedure",
    "Business venture startup capital funding",
    "Home improvement renovation and upgrade",
    "Debt consolidation to reduce monthly payments",
]


def _random_card_number() -> str:
    return "4" + "".join(str(random.randint(0, 9)) for _ in range(15))


@dataclass(frozen=True)
class DemoContext:
    customer_ids: list[str]
    merchant_ids: list[str]
    channel_ids: list[int]


class TokenManager:
    """Quản lý JWT token, tự login lại khi cần."""

    def __init__(self, base_url: str, username: str, password: str):
        self._base_url = base_url.rstrip("/")
        self._username = username
        self._password = password
        self._token: str | None = None
        self._expires_at = datetime.min.replace(tzinfo=timezone.utc)

    def get(self) -> str:
        if self._token is None or datetime.now(timezone.utc) >= self._expires_at:
            self._login()
        return self._token or ""

    def invalidate(self) -> None:
        self._token = None
        self._expires_at = datetime.min.replace(tzinfo=timezone.utc)

    def _login(self) -> None:
        resp = requests.post(
            f"{self._base_url}/auth/login",
            json={"username": self._username, "password": self._password},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        access_token = data.get("access_token")
        if not access_token:
            raise RuntimeError("Login không trả access_token hợp lệ.")
        self._token = str(access_token)
        expires_in = max(60, int(data.get("expires_in", 3600)))
        self._expires_at = datetime.now(timezone.utc) + timedelta(seconds=max(30, expires_in - 300))


class ApiClient:
    def __init__(self, base_url: str, token_manager: TokenManager):
        self._base_url = base_url.rstrip("/")
        self._token_manager = token_manager

    def request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        timeout: int = 10,
        retry_on_401: bool = True,
    ) -> requests.Response:
        url = f"{self._base_url}{path}"
        headers = {"Authorization": f"Bearer {self._token_manager.get()}"}
        resp = requests.request(method=method, url=url, json=json, params=params, headers=headers, timeout=timeout)

        if resp.status_code == 401 and retry_on_401:
            self._token_manager.invalidate()
            headers = {"Authorization": f"Bearer {self._token_manager.get()}"}
            resp = requests.request(method=method, url=url, json=json, params=params, headers=headers, timeout=timeout)

        if resp.status_code >= 400:
            raise RuntimeError(f"{method.upper()} {path} failed ({resp.status_code}): {_error_message(resp)}")
        return resp

    def get(self, path: str, *, params: dict[str, Any] | None = None, timeout: int = 10) -> requests.Response:
        return self.request("GET", path, params=params, timeout=timeout)

    def post(self, path: str, *, json: dict[str, Any], timeout: int = 10) -> requests.Response:
        return self.request("POST", path, json=json, timeout=timeout)


def _error_message(resp: requests.Response) -> str:
    try:
        body = resp.json()
    except ValueError:
        return resp.text.strip()[:120] or "unknown error"
    if isinstance(body, dict):
        if isinstance(body.get("message"), str):
            return body["message"][:120]
        if isinstance(body.get("detail"), str):
            return body["detail"][:120]
    return str(body)[:120]


def load_demo_context(
    client: ApiClient,
    *,
    customer_query: str = "cu",
    merchant_query: str = "mc",
) -> DemoContext:
    customers = client.get("/lookup/customers", params={"q": customer_query, "limit": 50}).json()
    merchants = client.get("/lookup/merchants", params={"q": merchant_query, "limit": 50}).json()
    channels = client.get("/lookup/channels").json()

    customer_ids = [item["customer_id"] for item in customers if isinstance(item, dict) and item.get("customer_id")]
    merchant_ids = [item["merchant_id"] for item in merchants if isinstance(item, dict) and item.get("merchant_id")]
    channel_ids = [item["channel_id"] for item in channels if isinstance(item, dict) and item.get("channel_id") is not None]

    if not customer_ids:
        raise RuntimeError("Không lấy được customer_id từ /lookup/customers.")
    if not merchant_ids:
        raise RuntimeError("Không lấy được merchant_id từ /lookup/merchants.")
    if not channel_ids:
        raise RuntimeError("Không lấy được channel_id từ /lookup/channels.")

    return DemoContext(customer_ids=customer_ids, merchant_ids=merchant_ids, channel_ids=channel_ids)


def build_transaction(ctx: DemoContext) -> dict[str, Any]:
    txn_time = datetime.now(timezone.utc) - timedelta(minutes=random.randint(0, 60 * 24))
    amount = round(random.uniform(3000, 8000), 2) if random.random() < 0.20 else round(random.uniform(10, 500), 2)
    return {
        "card_number": _random_card_number(),
        "customer_id": random.choice(ctx.customer_ids),
        "merchant_id": random.choice(ctx.merchant_ids),
        "channel_id": random.choice(ctx.channel_ids),
        "amount": amount,
        "txn_time": txn_time.isoformat(),
        "idempotency_key": str(uuid.uuid4()),
    }


def build_loan(ctx: DemoContext) -> dict[str, Any]:
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

    return {
        "customer_id": random.choice(ctx.customer_ids),
        "principal_amount": loan_amnt,
        "interest_rate": int_rate_dec,
        "term_months": random.choice([12, 24, 36, 48, 60]),
        "purpose": random.choice(LOAN_PURPOSES),
        "person_age": age,
        "person_income": income,
        "person_home_ownership": ownership,
        "person_emp_length": emp_length,
        "loan_intent": random.choice(LOAN_INTENTS),
        "loan_grade": grade,
        "cb_person_default_on_file": default_file,
        "cb_person_cred_hist_length": random.randint(1, 30),
    }


def send_loop(client: ApiClient, ctx: DemoContext, rate: float, count: int | None, loan_pct: int) -> None:
    delay = 1.0 / rate
    sent = 0
    stats: dict[str, int] = {
        "TXN_APPROVED": 0,
        "TXN_REJECTED": 0,
        "TXN_MANUAL_REVIEW": 0,
        "LOAN_PENDING": 0,
        "ERROR": 0,
    }

    color = {
        "APPROVED": "\033[32m",
        "REJECTED": "\033[31m",
        "MANUAL_REVIEW": "\033[33m",
        "LOAN_PENDING": "\033[36m",
        "ERROR": "\033[31m",
    }
    reset = "\033[0m"

    print(f"\n{'-' * 70}")
    print(f"  TMS Demo  |  {rate} req/s  |  {loan_pct}% loan  |  target: {'∞' if count is None else count}")
    print(f"{'-' * 70}")
    print(f"{'#':>5}  {'Type':<6}  {'Result':<15}  {'Score/PD':>8}  {'Amount':>10}  Info")
    print(f"{'-' * 70}")

    try:
        while count is None or sent < count:
            is_loan = random.randint(1, 100) <= loan_pct
            seq = sent + 1

            try:
                if is_loan:
                    payload = build_loan(ctx)
                    data = client.post("/loans", json=payload).json()
                    pd_score = float(data.get("pd_score") or 0.0)
                    risk = str(data.get("risk_level") or "-")
                    grade = str(payload.get("loan_grade") or "?")
                    amount = float(payload["principal_amount"])
                    stats["LOAN_PENDING"] += 1
                    print(
                        f"{seq:>5}  {'LOAN':<6}  {color['LOAN_PENDING']}{'PENDING':<15}{reset}  "
                        f"{pd_score:>8.4f}  {amount:>10.2f}  {grade} | {risk}"
                    )
                else:
                    payload = build_transaction(ctx)
                    data = client.post("/transactions/submit", json=payload).json()
                    status = str(data.get("status") or "?")
                    decision = str(data.get("decision") or "?")
                    fraud_score = float(data.get("fraud_score") or 0.0)
                    amount = float(payload["amount"])
                    key = f"TXN_{status}"
                    stats[key] = stats.get(key, 0) + 1
                    c = color.get(status, "")
                    print(
                        f"{seq:>5}  {'TXN':<6}  {c}{status:<15}{reset}  "
                        f"{fraud_score:>8.4f}  {amount:>10.2f}  {decision}"
                    )
            except (requests.RequestException, RuntimeError) as exc:
                stats["ERROR"] += 1
                kind = "LOAN" if is_loan else "TXN"
                print(f"{seq:>5}  {kind:<6}  {color['ERROR']}{'ERROR':<15}{reset}  {'-':>8}  {'-':>10}  {str(exc)[:60]}")

            sent += 1
            time.sleep(delay)
    except KeyboardInterrupt:
        pass

    print(f"\n{'-' * 70}")
    print(f"  Tong: {sent} requests")
    for key, value in stats.items():
        if value:
            pct = value / max(sent, 1) * 100
            print(f"    {key:<20} {value:>4}  ({pct:.1f}%)")
    print(f"{'-' * 70}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="TMS demo data sender")
    parser.add_argument("--url", default="http://localhost:8000/api/v1")
    parser.add_argument("--username", default="operator1")
    parser.add_argument("--password", default="Operator@123")
    parser.add_argument("--rate", type=float, default=1.0, help="So request/giay (default: 1)")
    parser.add_argument("--count", type=int, default=None, help="Tong so request; bo trong = chay mai")
    parser.add_argument("--loans", type=int, default=20, help="Ti le % request la loan (0-100)")
    parser.add_argument("--customer-query", default="cu", help="Tu khoa tim customer qua /lookup/customers (>=2 ky tu)")
    parser.add_argument("--merchant-query", default="mc", help="Tu khoa tim merchant qua /lookup/merchants (>=2 ky tu)")
    args = parser.parse_args()

    rate = max(0.1, float(args.rate))
    loan_pct = max(0, min(100, int(args.loans)))

    print(f"Dang nhap {args.username}@{args.url}...")
    token_manager = TokenManager(args.url, args.username, args.password)
    token_manager.get()
    client = ApiClient(args.url, token_manager)
    context = load_demo_context(client, customer_query=args.customer_query, merchant_query=args.merchant_query)
    print(
        f"Login OK. Loaded lookup: customers={len(context.customer_ids)}, "
        f"merchants={len(context.merchant_ids)}, channels={len(context.channel_ids)}."
    )

    send_loop(client, context, rate=rate, count=args.count, loan_pct=loan_pct)


if __name__ == "__main__":
    main()
