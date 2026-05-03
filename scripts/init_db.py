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
  4. Seeds default admin user if no users exist
"""
from __future__ import annotations

import sys
import os

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
from app.models.merchant import Channel
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

    # ── 4. Default admin user ─────────────────────────────────
    if db.query(User).count() == 0:
        import uuid
        admin = User(
            user_id=str(uuid.uuid4()),
            username="admin",
            password_hash=_pwd.hash("Admin@1234"),
            full_name="System Administrator",
            email="admin@tms.local",
            role="ADMIN",
            status="ACTIVE",
        )
        db.add(admin)
        print("[init_db] Seeded default admin (username=admin, password=Admin@1234)")
        print("[init_db] IMPORTANT: Change admin password immediately after first login!")
    db.commit()


with SessionLocal() as db:
    _seed(db)

print("[init_db] Done.")
