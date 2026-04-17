"""
Demo script: gửi giao dịch liên tục lên API bằng dữ liệu Faker.
Chạy: python demo_transactions.py

Tuỳ chỉnh:
  --url    Base URL của API  (default: http://localhost:8000/api/v1)
  --rate   Số giao dịch/giây (default: 1)
  --count  Tổng số giao dịch  (default: chạy mãi)
"""

import argparse
import random
import time
import uuid
from datetime import datetime, timedelta

import requests
from faker import Faker

# ── Seeded IDs (khớp với seed.py) ─────────────────────────────
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

# ── Faker setup ────────────────────────────────────────────────
fake = Faker()
Faker.seed(None)  # random mỗi lần chạy


def build_transaction() -> dict:
    """Tạo 1 transaction payload ngẫu nhiên."""
    # txn_time ngẫu nhiên trong 24h qua
    txn_time = datetime.now() - timedelta(
        minutes=random.randint(0, 60 * 24)
    )

    # 20% chance: amount lớn bất thường (dễ trigger MANUAL_REVIEW / REJECTED)
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


def login(base_url: str, username: str, password: str) -> str:
    resp = requests.post(
        f"{base_url}/auth/login",
        json={"username": username, "password": password},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def send_loop(base_url: str, token: str, rate: float, count: int | None):
    headers = {"Authorization": f"Bearer {token}"}
    delay   = 1.0 / rate
    sent    = 0
    stats   = {"APPROVED": 0, "REJECTED": 0, "MANUAL_REVIEW": 0, "ERROR": 0}

    print(f"\n{'─'*60}")
    print(f"  TMS Demo — {rate} txn/s  |  target: {'∞' if count is None else count}")
    print(f"{'─'*60}")
    print(f"{'#':>5}  {'Status':<15}  {'Score':>6}  {'Amount':>8}  {'Decision'}")
    print(f"{'─'*60}")

    try:
        while count is None or sent < count:
            payload = build_transaction()
            try:
                resp = requests.post(
                    f"{base_url}/transactions/submit",
                    json=payload,
                    headers=headers,
                    timeout=10,
                )
                data = resp.json()

                if resp.status_code == 201:
                    status   = data.get("status", "?")
                    score    = data.get("fraud_score") or 0
                    decision = data.get("decision", "?")
                    stats[status] = stats.get(status, 0) + 1

                    # Màu terminal: APPROVED=green, MANUAL_REVIEW=yellow, REJECTED=red
                    color = {"APPROVED": "\033[32m", "REJECTED": "\033[31m", "MANUAL_REVIEW": "\033[33m"}.get(status, "")
                    reset = "\033[0m"
                    print(
                        f"{sent+1:>5}  {color}{status:<15}{reset}  "
                        f"{score:>6.3f}  {payload['amount']:>8.2f}  {decision}"
                    )
                else:
                    stats["ERROR"] += 1
                    msg = data.get("message", str(data))[:60]
                    print(f"{sent+1:>5}  \033[31mERROR\033[0m           {resp.status_code}  {msg}")

            except requests.RequestException as e:
                stats["ERROR"] += 1
                print(f"{sent+1:>5}  \033[31mNETWORK ERROR\033[0m  {e}")

            sent += 1
            time.sleep(delay)

    except KeyboardInterrupt:
        pass

    print(f"\n{'─'*60}")
    print(f"  Tổng: {sent} giao dịch")
    for k, v in stats.items():
        if v:
            pct = v / max(sent, 1) * 100
            print(f"    {k:<15} {v:>4}  ({pct:.1f}%)")
    print(f"{'─'*60}\n")


def main():
    parser = argparse.ArgumentParser(description="TMS demo transaction sender")
    parser.add_argument("--url",      default="http://localhost:8000/api/v1")
    parser.add_argument("--username", default="operator1")
    parser.add_argument("--password", default="Operator@123")
    parser.add_argument("--rate",     type=float, default=1.0, help="Txn/giây")
    parser.add_argument("--count",    type=int,   default=None, help="Số txn (bỏ trống = vô hạn)")
    args = parser.parse_args()

    print(f"Đăng nhập {args.username}@{args.url}...")
    token = login(args.url, args.username, args.password)
    print("Login OK.")

    send_loop(args.url, token, args.rate, args.count)


if __name__ == "__main__":
    main()
