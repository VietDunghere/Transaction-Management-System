"""
Demo script: gửi giao dịch và đơn vay liên tục lên API bằng dữ liệu Faker.
Chạy: python demo_transactions.py

Tuỳ chỉnh:
  --url      Base URL của API       (default: http://localhost:8000/api/v1)
  --rate     Số giao dịch/giây      (default: 1)
  --count    Tổng số request        (default: chạy mãi)
  --loans    Tỉ lệ loan request %   (default: 20 — 20% là loan, 80% là transaction)

Yêu cầu: pip install requests faker
"""

import argparse
import random
import time
import uuid
from datetime import datetime, timedelta

import requests
from faker import Faker

# ── Seeded IDs (khớp với seed.py) ─────────────────────────────────────────────
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

LOAN_INTENTS     = ["PERSONAL", "EDUCATION", "MEDICAL", "VENTURE", "HOMEIMPROVEMENT", "DEBTCONSOLIDATION"]
LOAN_GRADES      = ["A", "B", "C", "D", "E", "F", "G"]
HOME_OWNERSHIPS  = ["RENT", "MORTGAGE", "OWN", "OTHER"]
LOAN_PURPOSES    = [
    "Personal loan for home renovation project",
    "Education loan for university tuition fees",
    "Medical expense loan for surgery procedure",
    "Business venture startup capital funding",
    "Home improvement renovation and upgrade",
    "Debt consolidation to reduce monthly payments",
]

# ── Faker setup ────────────────────────────────────────────────────────────────
fake = Faker()
Faker.seed(None)  # random mỗi lần chạy

# ── Auth helper ────────────────────────────────────────────────────────────────

class TokenManager:
    """Quản lý JWT token — tự động re-login khi nhận 401."""

    def __init__(self, base_url: str, username: str, password: str):
        self._base_url = base_url
        self._username = username
        self._password = password
        self._token: str | None = None
        self._expires_at: datetime = datetime.min

    def get(self) -> str:
        """Trả token hợp lệ — tự refresh nếu sắp hết hạn (< 5 phút còn lại)."""
        if self._token is None or datetime.now() >= self._expires_at:
            self._login()
        return self._token  # type: ignore[return-value]

    def invalidate(self) -> None:
        """Force re-login cho lần gọi tiếp theo (sau khi nhận 401)."""
        self._token = None

    def _login(self) -> None:
        resp = requests.post(
            f"{self._base_url}/auth/login",
            json={"username": self._username, "password": self._password},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        self._token = data["access_token"]
        # expires_in là giây — refresh trước 5 phút để tránh race
        expires_in = data.get("expires_in", 3600)
        self._expires_at = datetime.now() + timedelta(seconds=expires_in - 300)


# ── Payload builders ───────────────────────────────────────────────────────────

def build_transaction() -> dict:
    """Tạo 1 transaction payload ngẫu nhiên."""
    txn_time = datetime.now() - timedelta(minutes=random.randint(0, 60 * 24))

    # 20% chance: amount lớn bất thường → dễ trigger MANUAL_REVIEW / REJECTED
    if random.random() < 0.20:
        amount = round(random.uniform(3000, 8000), 2)
    else:
        amount = round(random.uniform(10, 500), 2)

    return {
        "card_number":     fake.credit_card_number(card_type=None),
        "customer_id":     random.choice(CUSTOMERS),
        "merchant_id":     random.choice(MERCHANTS),
        "channel_id":      random.choice(CHANNEL_IDS),
        "amount":          amount,
        "currency_code":   "USD",
        "txn_time":        txn_time.isoformat(),
        "source_ip":       fake.ipv4_private(),
        "idempotency_key": str(uuid.uuid4()),
    }


def build_loan() -> dict:
    """Tạo 1 loan application payload ngẫu nhiên với đủ AI features."""
    grade        = random.choice(LOAN_GRADES)
    intent       = random.choice(LOAN_INTENTS)
    ownership    = random.choice(HOME_OWNERSHIPS)
    age          = random.randint(20, 65)
    emp_length   = random.randint(0, min(age - 18, 30))
    income       = round(random.uniform(20_000, 200_000), 2)
    loan_amnt    = round(random.uniform(2_000, 40_000), 2)
    # interest_rate cho LoanApplyRequest: dạng thập phân 0.05–0.25
    int_rate_dec = round(random.uniform(0.05, 0.25), 4)
    term         = random.choice([12, 24, 36, 48, 60])
    cred_hist    = random.randint(1, 30)
    default_file = random.choices(["Y", "N"], weights=[15, 85])[0]

    return {
        "customer_id":              random.choice(CUSTOMERS),
        "principal_amount":         loan_amnt,
        "currency_code":            "USD",
        "interest_rate":            int_rate_dec,
        "term_months":              term,
        "purpose":                  random.choice(LOAN_PURPOSES),
        # AI features
        "person_age":               age,
        "person_income":            income,
        "person_home_ownership":    ownership,
        "person_emp_length":        emp_length,
        "loan_intent":              intent,
        "loan_grade":               grade,
        "cb_person_default_on_file": default_file,
        "cb_person_cred_hist_length": cred_hist,
    }


# ── Main send loop ─────────────────────────────────────────────────────────────

def send_loop(
    base_url: str,
    tm: TokenManager,
    rate: float,
    count: int | None,
    loan_pct: int,
) -> None:
    delay = 1.0 / rate
    sent  = 0
    stats: dict[str, int] = {
        # transaction
        "TXN_APPROVED": 0, "TXN_REJECTED": 0, "TXN_MANUAL_REVIEW": 0,
        # loan
        "LOAN_PENDING": 0,
        # errors
        "ERROR": 0,
    }

    print(f"\n{'─'*70}")
    print(f"  TMS Demo  |  {rate} req/s  |  {loan_pct}% loan  |  "
          f"target: {'∞' if count is None else count}")
    print(f"{'─'*70}")
    print(f"{'#':>5}  {'Type':<6}  {'Result':<15}  {'Score/PD':>8}  {'Amount':>10}  Info")
    print(f"{'─'*70}")

    COLOR = {
        "APPROVED":      "\033[32m",
        "TXN_APPROVED":  "\033[32m",
        "REJECTED":      "\033[31m",
        "TXN_REJECTED":  "\033[31m",
        "MANUAL_REVIEW": "\033[33m",
        "TXN_MANUAL_REVIEW": "\033[33m",
        "LOAN_PENDING":  "\033[36m",
        "ERROR":         "\033[31m",
    }
    RESET = "\033[0m"

    try:
        while count is None or sent < count:
            is_loan = random.randint(1, 100) <= loan_pct
            headers = {"Authorization": f"Bearer {tm.get()}"}

            if is_loan:
                payload = build_loan()
                try:
                    resp = requests.post(
                        f"{base_url}/loans",
                        json=payload,
                        headers=headers,
                        timeout=10,
                    )
                    # Token hết hạn → re-login và thử lại 1 lần
                    if resp.status_code == 401:
                        tm.invalidate()
                        headers = {"Authorization": f"Bearer {tm.get()}"}
                        resp = requests.post(
                            f"{base_url}/loans",
                            json=payload,
                            headers=headers,
                            timeout=10,
                        )
                    data = resp.json()
                    if resp.status_code == 201:
                        risk  = data.get("risk_level") or "—"
                        pd    = data.get("pd_score")
                        amt   = payload["principal_amount"]
                        grade = payload["loan_grade"]
                        stats["LOAN_PENDING"] += 1
                        c = COLOR.get("LOAN_PENDING", "")
                        print(
                            f"{sent+1:>5}  {'LOAN':<6}  {c}{'PENDING':<15}{RESET}  "
                            f"{pd or 0:>8.4f}  {amt:>10.2f}  {grade} | {risk}"
                        )
                    else:
                        stats["ERROR"] += 1
                        msg = data.get("message", str(data))[:50]
                        print(f"{sent+1:>5}  {'LOAN':<6}  {COLOR['ERROR']}{'ERROR':<15}{RESET}  "
                              f"{resp.status_code:>8}  {payload['principal_amount']:>10.2f}  {msg}")
                except requests.RequestException as e:
                    stats["ERROR"] += 1
                    print(f"{sent+1:>5}  {'LOAN':<6}  {COLOR['ERROR']}NETWORK ERROR{RESET}   {e}")

            else:
                payload = build_transaction()
                try:
                    resp = requests.post(
                        f"{base_url}/transactions/submit",
                        json=payload,
                        headers=headers,
                        timeout=10,
                    )
                    if resp.status_code == 401:
                        tm.invalidate()
                        headers = {"Authorization": f"Bearer {tm.get()}"}
                        resp = requests.post(
                            f"{base_url}/transactions/submit",
                            json=payload,
                            headers=headers,
                            timeout=10,
                        )
                    data = resp.json()
                    if resp.status_code == 201:
                        status   = data.get("status", "?")
                        score    = data.get("fraud_score") or 0.0
                        decision = data.get("decision", "?")
                        key      = f"TXN_{status}"
                        stats[key] = stats.get(key, 0) + 1
                        c = COLOR.get(status, "")
                        print(
                            f"{sent+1:>5}  {'TXN':<6}  {c}{status:<15}{RESET}  "
                            f"{score:>8.4f}  {payload['amount']:>10.2f}  {decision}"
                        )
                    else:
                        stats["ERROR"] += 1
                        msg = data.get("message", str(data))[:50]
                        print(f"{sent+1:>5}  {'TXN':<6}  {COLOR['ERROR']}{'ERROR':<15}{RESET}  "
                              f"{resp.status_code:>8}  {payload['amount']:>10.2f}  {msg}")
                except requests.RequestException as e:
                    stats["ERROR"] += 1
                    print(f"{sent+1:>5}  {'TXN':<6}  {COLOR['ERROR']}NETWORK ERROR{RESET}   {e}")

            sent += 1
            time.sleep(delay)

    except KeyboardInterrupt:
        pass

    print(f"\n{'─'*70}")
    print(f"  Tổng: {sent} requests")
    for k, v in stats.items():
        if v:
            pct = v / max(sent, 1) * 100
            print(f"    {k:<20} {v:>4}  ({pct:.1f}%)")
    print(f"{'─'*70}\n")


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="TMS demo data sender")
    parser.add_argument("--url",       default="http://localhost:8000/api/v1")
    parser.add_argument("--username",  default="operator1")
    parser.add_argument("--password",  default="Operator@123")
    parser.add_argument("--rate",      type=float, default=1.0,
                        help="Số request/giây (default: 1)")
    parser.add_argument("--count",     type=int,   default=None,
                        help="Tổng số request — bỏ trống = chạy mãi")
    parser.add_argument("--loans",     type=int,   default=20,
                        help="Tỉ lệ %% request là loan (0–100, default: 20)")
    args = parser.parse_args()

    loan_pct = max(0, min(100, args.loans))

    print(f"Đăng nhập {args.username}@{args.url}...")
    tm = TokenManager(args.url, args.username, args.password)
    tm.get()  # login ngay để báo lỗi sớm
    print("Login OK.")

    send_loop(args.url, tm, args.rate, args.count, loan_pct)


if __name__ == "__main__":
    main()
