#!/usr/bin/env python3
"""
init_db.py — Idempotent DB initializer for Transaction Management System.

Run after each deploy:
    cd /root/Transaction-Management-System
    python scripts/init_db.py

What it does:
  1. Creates all tables (CREATE TABLE IF NOT EXISTS via SQLAlchemy checkfirst)
  2. Seeds channels (POS, ATM, ONLINE, MOBILE_APP) if not exist
  3. Seeds model_configs (fraud thresholds) if not exist
  4. Seeds demo users (admin, operator1, manager1, reviewer1, analyst1)
  5. Seeds demo customers (cu001–cu005)
  6. Seeds demo merchants (mc001–mc005)
"""
from __future__ import annotations

import sys
import os
import uuid

# Add backend/ to path so app.* imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
os.chdir(os.path.join(os.path.dirname(__file__), "..", "backend"))

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.db.base import Base, engine, SessionLocal
from app.models import (  # noqa: F401  — registers models with Base
    analyst, audit_log, card_velocity, case, customer,
    loan, merchant, scoring, transaction, user,
)
from app.models.merchant import Channel, Merchant
from app.models.customer import Customer
from app.models.user import User
from app.models.analyst import ModelConfig

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── 1. Create tables ─────────────────────────────────────────
print("[init_db] Creating tables...")
Base.metadata.create_all(bind=engine, checkfirst=True)
print("[init_db] Tables OK.")


def _seed(db: Session) -> None:
    # ── 2. Channels ───────────────────────────────────────────
    channels = [
        ("POS",        "Point of Sale"),
        ("ATM",        "ATM"),
        ("ONLINE",     "Online Banking"),
        ("MOBILE_APP", "Mobile App"),
    ]
    existing_codes = {c.channel_code for c in db.query(Channel).all()}
    for code, name in channels:
        if code not in existing_codes:
            db.add(Channel(channel_code=code, channel_name=name))
            print(f"[init_db] Seeded channel: {code}")
    db.flush()

    # ── 3. Model configs (fraud thresholds) ───────────────────
    model_configs = [
        ("fraud_model", "reject_threshold", 0.65, "Score >= này → REJECTED"),
        ("fraud_model", "review_threshold", 0.35, "Score >= này → MANUAL_REVIEW"),
        ("loan_model",  "decision_threshold", 0.50, "PD score >= này → REJECTED"),
    ]
    for model_name, param_name, value, desc in model_configs:
        exists = db.query(ModelConfig).filter_by(
            model_name=model_name, param_name=param_name
        ).first()
        if not exists:
            db.add(ModelConfig(
                model_name=model_name,
                param_name=param_name,
                param_value=value,
                description=desc,
                version=1,
            ))
            print(f"[init_db] Seeded model_config: {model_name}.{param_name}={value}")
    db.flush()

    # ── 4. Demo users ─────────────────────────────────────────
    demo_users = [
        ("admin",     "System Administrator", "admin@tms.local",     "ADMIN",    "Admin@1234"),
        ("operator1", "Nguyen Operator",      "operator1@tms.local", "OPERATOR", "Demo@1234"),
        ("manager1",  "Tran Manager",         "manager1@tms.local",  "MANAGER",  "Demo@1234"),
        ("reviewer1", "Le Reviewer",          "reviewer1@tms.local", "REVIEWER", "Demo@1234"),
        ("analyst1",  "Pham Analyst",         "analyst1@tms.local",  "ANALYST",  "Demo@1234"),
    ]
    for uname, fname, email, role, pw in demo_users:
        if not db.query(User).filter_by(username=uname).first():
            db.add(User(
                user_id=str(uuid.uuid4()),
                username=uname,
                password_hash=_pwd.hash(pw),
                full_name=fname,
                email=email,
                role=role,
                status="ACTIVE",
            ))
            print(f"[init_db] Seeded user: {uname} ({role})")
    db.flush()

    # ── 5. Demo customers ─────────────────────────────────────
    demo_customers = [
        ("cu001", "Nguyen Van A"), ("cu002", "Tran Thi B"), ("cu003", "Le Van C"),
        ("cu004", "Pham Thi D"),   ("cu005", "Hoang Van E"),
    ]
    for cid, name in demo_customers:
        if not db.query(Customer).filter_by(customer_id=cid).first():
            db.add(Customer(customer_id=cid, customer_code=cid,
                            full_name=name, kyc_status="VERIFIED"))
            print(f"[init_db] Seeded customer: {cid} ({name})")
    db.flush()

    # ── 6. Demo merchants ─────────────────────────────────────
    demo_merchants = [
        ("mc001", "Super Mart"),    ("mc002", "Coffee House"),
        ("mc003", "Tech Store"),    ("mc004", "Fashion Shop"),
        ("mc005", "Online Market"),
    ]
    for mid, name in demo_merchants:
        if not db.query(Merchant).filter_by(merchant_id=mid).first():
            db.add(Merchant(merchant_id=mid, merchant_code=mid,
                            merchant_name=name, risk_level="LOW"))
            print(f"[init_db] Seeded merchant: {mid} ({name})")
    db.commit()


with SessionLocal() as db:
    _seed(db)

print("[init_db] Done.")
