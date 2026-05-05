"""
Demo Transaction Generator
==========================
Script tự động:
  1. Seed DB với customers, merchants, channels giả
  2. Đăng nhập API lấy JWT
  3. Gửi giao dịch fake liên tục với Faker
  4. Hiển thị kết quả realtime trên terminal (colored, tabular)

Sử dụng:
  pip install faker rich requests
  python scripts/fake_txn_generator.py

  # Tùy chọn:
  python scripts/fake_txn_generator.py --rate 2 --url http://localhost:8000
"""

from __future__ import annotations

import argparse
from collections import deque
import json
import random
import sys
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import requests
from faker import Faker
from rich import box
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# ── Thêm thư mục gốc vào path để import app
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

console = Console()
fake = Faker("en_US")
Faker.seed(42)
random.seed(42)

# Merchant categories từ Sparkov dataset
MERCHANT_CATEGORIES = [
    "grocery_pos", "gas_transport", "misc_net", "shopping_net",
    "misc_pos", "shopping_pos", "food_dining", "personal_care",
    "health_fitness", "travel", "entertainment", "kids_pets",
    "home", "education", "automotive",
]

# Tỉ lệ giao dịch theo pattern
PATTERN_WEIGHTS = {
    "normal":     60,  # Bình thường, số tiền nhỏ
    "medium":     25,  # Số tiền trung bình
    "suspicious":  10,  # Số tiền lớn, ban đêm
    "fraud_like":   5,  # Số tiền cực lớn + xa nhà
}

TARGET_TXN_RATIOS: dict[str, float] = {
    "APPROVED": 0.80,
    "MANUAL_REVIEW": 0.10,
    "REJECTED": 0.10,
}

STATUS_PATTERN_WEIGHTS: dict[str, dict[str, int]] = {
    "APPROVED": {"normal": 86, "medium": 14, "suspicious": 0, "fraud_like": 0},
    "MANUAL_REVIEW": {"normal": 12, "medium": 66, "suspicious": 22, "fraud_like": 0},
    "REJECTED": {"normal": 0, "medium": 15, "suspicious": 45, "fraud_like": 40},
}


class TxnStatusBalancer:
    """Giữ tỉ lệ trạng thái gần mục tiêu trong cửa sổ trượt 100 giao dịch."""

    def __init__(self, window_size: int = 100):
        self._window = deque(maxlen=window_size)
        self._window_size = window_size

    def choose_target(self) -> str:
        statuses = list(TARGET_TXN_RATIOS.keys())
        if len(self._window) < min(20, self._window_size):
            return random.choices(statuses, weights=[80, 10, 10], k=1)[0]

        counts = {status: self._window.count(status) for status in statuses}
        current_size = len(self._window)
        deficits = {
            status: (TARGET_TXN_RATIOS[status] * current_size) - counts[status]
            for status in statuses
        }
        best_status = max(deficits, key=deficits.get)
        if deficits[best_status] <= 0:
            return random.choices(statuses, weights=[80, 10, 10], k=1)[0]
        return best_status

    def observe(self, actual_status: str) -> None:
        if actual_status in TARGET_TXN_RATIOS:
            self._window.append(actual_status)

    def rolling_counts(self) -> dict[str, int]:
        return {
            status: self._window.count(status)
            for status in TARGET_TXN_RATIOS
        }


def choose_pattern_for_target(target_status: str) -> str:
    weights = STATUS_PATTERN_WEIGHTS.get(target_status, STATUS_PATTERN_WEIGHTS["APPROVED"])
    patterns = list(weights.keys())
    return random.choices(patterns, weights=[weights[p] for p in patterns], k=1)[0]


# ═══════════════════════════════════════════════════════════════
# Seed DB trực tiếp (vì chưa có API tạo customer/merchant)
# ═══════════════════════════════════════════════════════════════

def seed_database(db_url: str, n_customers: int = 20, n_merchants: int = 15) -> tuple[list, list, list]:
    """
    Tạo dữ liệu mẫu vào DB và trả về danh sách IDs.
    Nếu đã có data rồi thì reuse, không insert thêm.
    """
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(db_url, echo=False)

    # Import models để đảm bảo bảng tồn tại
    from app.db.base import Base, create_tables
    create_tables()

    Session = sessionmaker(bind=engine)
    db = Session()

    # ---- Check đã seed chưa ----
    existing_customers = db.execute(text("SELECT customer_id FROM customers LIMIT 1")).fetchone()
    existing_merchants = db.execute(text("SELECT merchant_id FROM merchants LIMIT 1")).fetchone()

    customer_ids = []
    merchant_ids = []
    channel_ids = []

    # ---- Channels ----
    channel_rows = db.execute(text("SELECT channel_id FROM channels")).fetchall()
    if not channel_rows:
        channels_data = [
            (1, "POS", "Point of Sale"),
            (2, "ATM", "ATM Machine"),
            (3, "ONLINE", "Online Banking"),
            (4, "MOBILE", "Mobile App"),
        ]
        for cid, code, name in channels_data:
            db.execute(text(
                "INSERT INTO channels (channel_id, channel_code, channel_name) "
                "VALUES (:id, :code, :name)"
            ), {"id": cid, "code": code, "name": name})
        db.commit()
        channel_ids = [1, 2, 3, 4]
        console.print("[green]✓ Seeded 4 channels[/green]")
    else:
        channel_ids = [r[0] for r in db.execute(text("SELECT channel_id FROM channels")).fetchall()]

    # ---- Customers ----
    if not existing_customers:
        for _ in range(n_customers):
            cid = str(uuid.uuid4())
            profile = fake.simple_profile()
            gender = random.choice(["M", "F"])
            dob = fake.date_of_birth(minimum_age=21, maximum_age=75)
            jobs = ["engineer", "teacher", "nurse", "accountant", "manager",
                    "technician", "mechanic", "artist", "doctor", "writer"]
            db.execute(text("""
                INSERT INTO customers
                  (customer_id, customer_code, full_name, date_of_birth, gender, job,
                   city, state, zip_code, city_population, latitude, longitude,
                   kyc_status, created_at)
                VALUES
                  (:id, :code, :name, :dob, :gender, :job,
                   :city, :state, :zip, :pop, :lat, :lon,
                   'VERIFIED', :created)
            """), {
                "id": cid,
                "code": f"CUST-{fake.bothify('????###').upper()}",
                "name": fake.name(),
                "dob": dob.isoformat(),
                "gender": gender,
                "job": random.choice(jobs),
                "city": fake.city(),
                "state": fake.state_abbr(),
                "zip": fake.zipcode(),
                "pop": random.randint(5000, 500000),
                "lat": float(fake.latitude()),
                "lon": float(fake.longitude()),
                "created": datetime.utcnow().isoformat(),
            })
            customer_ids.append(cid)
        db.commit()
        console.print(f"[green]✓ Seeded {n_customers} customers[/green]")
    else:
        rows = db.execute(text("SELECT customer_id FROM customers")).fetchall()
        customer_ids = [r[0] for r in rows]

    # ---- Merchants ----
    if not existing_merchants:
        for _ in range(n_merchants):
            mid = str(uuid.uuid4())
            cat = random.choice(MERCHANT_CATEGORIES)
            name = fake.company().split(",")[0]
            db.execute(text("""
                INSERT INTO merchants
                  (merchant_id, merchant_code, merchant_name, merchant_category,
                   city, state, country, latitude, longitude, risk_level,
                   is_blacklisted, created_at)
                VALUES
                  (:id, :code, :name, :cat,
                   :city, :state, 'US', :lat, :lon, :risk,
                   0, :created)
            """), {
                "id": mid,
                "code": f"MERCH-{fake.bothify('???###').upper()}",
                "name": f"fraud_{name}_{cat}",
                "cat": cat,
                "city": fake.city(),
                "state": fake.state_abbr(),
                "lat": float(fake.latitude()),
                "lon": float(fake.longitude()),
                "risk": random.choice(["LOW", "LOW", "LOW", "MEDIUM", "HIGH"]),
                "created": datetime.utcnow().isoformat(),
            })
            merchant_ids.append(mid)
        db.commit()
        console.print(f"[green]✓ Seeded {n_merchants} merchants[/green]")
    else:
        rows = db.execute(text("SELECT merchant_id FROM merchants")).fetchall()
        merchant_ids = [r[0] for r in rows]

    # ---- OPERATOR user ----
    from app.core.security import hash_password
    existing_op = db.execute(text("SELECT user_id FROM users WHERE username='operator01'")).fetchone()
    if not existing_op:
        operator_id = str(uuid.uuid4())
        reviewer_id = str(uuid.uuid4())
        manager_id = str(uuid.uuid4())
        db.execute(text("""
            INSERT INTO roles (role_name) VALUES ('OPERATOR'), ('REVIEWER'), ('MANAGER'), ('ADMIN')
        """))
        for uid, uname, fname in [
            (operator_id, "operator01", "Demo Operator"),
            (reviewer_id, "reviewer01", "Demo Reviewer"),
            (manager_id,  "manager01",  "Demo Manager"),
        ]:
            db.execute(text("""
                INSERT INTO users (user_id, username, password_hash, full_name, is_active, created_at)
                VALUES (:id, :un, :ph, :fn, 1, :ca)
            """), {
                "id": uid, "un": uname,
                "ph": hash_password("demo1234"),
                "fn": fname, "ca": datetime.utcnow().isoformat()
            })
        # Gán roles
        op_role_id = db.execute(text("SELECT role_id FROM roles WHERE role_name='OPERATOR'")).scalar()
        rv_role_id = db.execute(text("SELECT role_id FROM roles WHERE role_name='REVIEWER'")).scalar()
        mg_role_id = db.execute(text("SELECT role_id FROM roles WHERE role_name='MANAGER'")).scalar()
        for (uid, rid) in [(operator_id, op_role_id), (reviewer_id, rv_role_id), (manager_id, mg_role_id)]:
            db.execute(text("""
                INSERT INTO user_roles (user_id, role_id, assigned_at) VALUES (:u, :r, :t)
            """), {"u": uid, "r": rid, "t": datetime.utcnow().isoformat()})
        db.commit()
        console.print("[green]✓ Seeded users: operator01 / reviewer01 / manager01 (pass: demo1234)[/green]")

    db.close()
    return customer_ids, merchant_ids, channel_ids


# ═══════════════════════════════════════════════════════════════
# Login & Token
# ═══════════════════════════════════════════════════════════════

def login(base_url: str, username: str = "operator01", password: str = "demo1234") -> str:
    """Đăng nhập và trả về access token."""
    resp = requests.post(f"{base_url}/api/v1/auth/login", json={
        "username": username,
        "password": password,
    })
    if resp.status_code != 200:
        console.print(f"[red]✗ Login failed: {resp.text}[/red]")
        sys.exit(1)
    token = resp.json()["access_token"]
    console.print(f"[green]✓ Logged in as {username}[/green]")
    return token


# ═══════════════════════════════════════════════════════════════
# Transaction Generator
# ═══════════════════════════════════════════════════════════════

def generate_transaction(
    customer_ids: list,
    merchant_ids: list,
    channel_ids: list,
    pattern: str,
) -> dict:
    """Tạo payload giao dịch fake theo pattern."""
    customer_id = random.choice(customer_ids)
    merchant_id = random.choice(merchant_ids)
    channel_id  = random.choice(channel_ids)

    # ---- Amount theo pattern ----
    if pattern == "normal":
        amount = round(random.uniform(8.0, 180.0), 2)
    elif pattern == "medium":
        amount = round(random.uniform(250.0, 1400.0), 2)
    elif pattern == "suspicious":
        amount = round(random.uniform(1200.0, 6000.0), 2)
    else:  # fraud_like
        amount = round(random.uniform(5000.0, 25000.0), 2)

    # ---- Thời gian: fraud thường ban đêm ----
    if pattern in ("suspicious", "fraud_like"):
        hour = random.choice([0, 1, 2, 3, 23, 22])
    else:
        hour = random.choices([random.randint(8, 21), random.choice([22, 23, 0, 1])], weights=[97, 3], k=1)[0]

    txn_time = datetime.now().replace(
        hour=hour,
        minute=random.randint(0, 59),
        second=random.randint(0, 59),
    )

    # ---- Card number fake ----
    card = fake.credit_card_number(card_type="visa")

    return {
        "card_number": card,
        "customer_id": customer_id,
        "merchant_id": merchant_id,
        "channel_id": channel_id,
        "amount": amount,
        "currency_code": "USD",
        "txn_time": txn_time.isoformat(),
        "source_ip": fake.ipv4(),
        "idempotency_key": str(uuid.uuid4()),
    }


def send_transaction(base_url: str, token: str, payload: dict) -> dict:
    """Gửi giao dịch đến API và trả về kết quả."""
    resp = requests.post(
        f"{base_url}/api/v1/transactions",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    if resp.status_code in (200, 201):
        return resp.json()
    raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")


# ═══════════════════════════════════════════════════════════════
# Rich display helpers
# ═══════════════════════════════════════════════════════════════

def score_color(score: float | None) -> str:
    """Màu sắc theo mức độ rủi ro."""
    if score is None:
        return "white"
    if score >= 0.45:
        return "red bold"
    if score >= 0.10:
        return "yellow"
    return "green"


def status_badge(status: str) -> str:
    badges = {
        "APPROVED": "[green]✓ APPROVED[/green]",
        "REJECTED": "[red]✗ REJECTED[/red]",
        "MANUAL_REVIEW": "[yellow]⚑ REVIEW[/yellow]",
    }
    return badges.get(status, status)


def pattern_emoji(pattern: str) -> str:
    emojis = {
        "normal": "😊",
        "medium": "😐",
        "suspicious": "🤔",
        "fraud_like": "🚨",
    }
    return emojis.get(pattern, "")


def build_stats_panel(stats: dict, total: int, elapsed: float) -> Panel:
    tps = total / max(elapsed, 1)
    content = (
        f"[bold]Giao dịch: {total}[/bold]  |  "
        f"[green]✓ {stats['APPROVED']}[/green]  "
        f"[yellow]⚑ {stats['MANUAL_REVIEW']}[/yellow]  "
        f"[red]✗ {stats['REJECTED']}[/red]  |  "
        f"[cyan]{tps:.1f} txn/s[/cyan]  |  "
        f"Lỗi: [red]{stats['errors']}[/red]"
    )
    return Panel(content, title="[bold blue]📊 TMS Demo — Live Stats[/bold blue]", box=box.ROUNDED)


# ═══════════════════════════════════════════════════════════════
# Main loop
# ═══════════════════════════════════════════════════════════════

def run(
    base_url: str,
    db_url: str,
    rate: float,
    max_txn: int | None,
):
    console.rule("[bold blue]TMS Fake Transaction Generator[/bold blue]")
    console.print(f"API: [cyan]{base_url}[/cyan]  |  Rate: [cyan]{rate} txn/s[/cyan]")
    console.print()

    # ---- Seed DB ----
    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as p:
        task = p.add_task("Seeding database...", total=None)
        customer_ids, merchant_ids, channel_ids = seed_database(db_url)
        p.update(task, description="✓ Database ready")

    console.print()

    # ---- Login ----
    token = login(base_url)
    console.print()
    console.rule()

    # ---- Build result table ----
    table = Table(
        "No.", "Pattern", "Amount (USD)", "Score", "Status", "TxnID",
        box=box.SIMPLE_HEAD,
        show_header=True,
        header_style="bold cyan",
        min_width=90,
    )

    stats = {"APPROVED": 0, "MANUAL_REVIEW": 0, "REJECTED": 0, "errors": 0}
    total = 0
    start_time = time.time()
    interval = 1.0 / rate

    balancer = TxnStatusBalancer(window_size=100)

    patterns = list(PATTERN_WEIGHTS.keys())
    weights  = list(PATTERN_WEIGHTS.values())

    # ---- Live display ----
    with Live(console=console, refresh_per_second=4, vertical_overflow="visible") as live:
        while True:
            if max_txn and total >= max_txn:
                break

            target_status = balancer.choose_target()
            if target_status in STATUS_PATTERN_WEIGHTS:
                pattern = choose_pattern_for_target(target_status)
            else:
                pattern = random.choices(patterns, weights=weights, k=1)[0]
            payload  = generate_transaction(customer_ids, merchant_ids, channel_ids, pattern)

            try:
                result = send_transaction(base_url, token, payload)
                status     = result.get("status", "?")
                fraud_score = result.get("fraud_score")
                txn_id     = result.get("txn_id", "")[:8] + "..."
                stats[status] = stats.get(status, 0) + 1
                balancer.observe(status)
            except Exception as exc:
                status      = "ERROR"
                fraud_score = None
                txn_id      = "—"
                stats["errors"] += 1
                console.print(f"[red]Lỗi: {exc}[/red]")

            total += 1
            elapsed = time.time() - start_time

            score_str = (
                f"[{score_color(fraud_score)}]{fraud_score:.4f}[/{score_color(fraud_score)}]"
                if fraud_score is not None else "[dim]n/a[/dim]"
            )

            table.add_row(
                str(total),
                f"{pattern_emoji(pattern)} {pattern}→{target_status[:1]}",
                f"${payload['amount']:>10,.2f}",
                score_str,
                status_badge(status),
                f"[dim]{txn_id}[/dim]",
            )

            # Chỉ giữ 40 rows gần nhất trong table để không tràn terminal
            if len(table.rows) > 40:
                table.rows.pop(0)

            live.update(
                Panel(
                    table,
                    title="[bold blue]📡 TMS Demo — Live Transactions[/bold blue]",
                    subtitle=str(build_stats_panel(stats, total, elapsed).renderable),
                    box=box.ROUNDED,
                )
            )

            time.sleep(max(0, interval - 0.01))


# ═══════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TMS Fake Transaction Generator")
    parser.add_argument("--url",    default="http://localhost:8000", help="Base URL của API")
    parser.add_argument("--db",     default="sqlite:///./tms.db",    help="Database URL (SQLAlchemy)")
    parser.add_argument("--rate",   type=float, default=1.0,         help="Số giao dịch mỗi giây (default: 1)")
    parser.add_argument("--max",    type=int,   default=None,        help="Số giao dịch tối đa (mặc định: vô hạn)")
    args = parser.parse_args()

    try:
        run(
            base_url=args.url,
            db_url=args.db,
            rate=args.rate,
            max_txn=args.max,
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]⏹ Dừng generator.[/yellow]")
