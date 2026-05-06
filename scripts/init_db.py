#!/usr/bin/env python3
"""
init_db.py — Idempotent DB initializer for Transaction Management System.

Run after each deploy:
    cd /root/Transaction-Management-System
    python scripts/init_db.py

What it does:
  1. Creates all tables via SQLAlchemy
  2. Seeds channels
  3. Seeds model_configs
  4. Seeds demo users (admin, operator1, manager1, reviewer1, analyst1)
  5. Seeds demo customers — Kaggle-realistic US profiles (city/state/lat/lon/job match training data)
  6. Seeds demo merchants  — one per Kaggle category, exact merchant names the model knows
"""
from __future__ import annotations

import sys
import os
import uuid
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
os.chdir(os.path.join(os.path.dirname(__file__), "..", "backend"))

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.db.base import Base, engine, SessionLocal
from app.models import (  # noqa: F401
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

    # ── 3. Model configs ──────────────────────────────────────
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
                model_name=model_name, param_name=param_name,
                param_value=value, description=desc, version=1,
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
                user_id=str(uuid.uuid4()), username=uname,
                password_hash=_pwd.hash(pw), full_name=fname,
                email=email, role=role, status="ACTIVE",
            ))
            print(f"[init_db] Seeded user: {uname} ({role})")
    db.flush()

    # ── 5. Demo customers — Kaggle-realistic profiles ─────────
    # city/state/lat/lon/city_pop from Kaggle fraudTrain.csv (seen by FrequencyEncoder)
    # job titles from top-frequency Kaggle jobs
    demo_customers = [
        ("cu001", "Jennifer Banks",   "F", date(1988, 3, 9),  "Psychologist, counselling",
         "Moravian Falls", "NC",  36.0788,  -81.1781,   3495),
        ("cu002", "Robert Martinez",  "M", date(1975, 6, 15), "Film/video editor",
         "Norfolk",        "VA",  36.8294,  -76.2701, 242803),
        ("cu003", "Maria Johnson",    "F", date(1992, 11, 2), "Financial adviser",
         "Azusa",          "CA",  34.1248, -117.9031,  59705),
        ("cu004", "James Wilson",     "M", date(1965, 4, 22), "Systems developer",
         "Milwaukee",      "WI",  42.9676,  -88.0434, 817312),
        ("cu005", "Patricia Davis",   "F", date(1980, 8, 30), "Materials engineer",
         "Fairhope",       "AL",  30.5012,  -87.8835,  27829),
        ("cu006", "Michael Brown",    "M", date(1958, 1, 18), "Chief Executive Officer",
         "Huntsville",     "AL",  34.7789,  -86.5438, 190178),
        ("cu007", "Linda Garcia",     "F", date(1995, 7, 5),  "IT trainer",
         "La Grande",      "OR",  45.3304, -118.0852,  16955),
        ("cu008", "David Rodriguez",  "M", date(1983, 9, 14), "Naval architect",
         "Bellmore",       "NY",  40.6729,  -73.5365,  34496),
        ("cu009", "Barbara Martinez", "F", date(1970, 3, 27), "Environmental consultant",
         "Key West",       "FL",  24.6557,  -81.3824,  32891),
        ("cu010", "William Anderson", "M", date(1948, 12, 10),"Paramedic",
         "San Diego",      "CA",  33.0067, -117.0690, 1241364),
    ]
    for cid, name, gender, dob, job, city, state, lat, lon, pop in demo_customers:
        if not db.query(Customer).filter_by(customer_id=cid).first():
            db.add(Customer(
                customer_id=cid, customer_code=cid, full_name=name,
                gender=gender, date_of_birth=dob, job=job,
                city=city, address=city, latitude=lat, longitude=lon,
                kyc_status="VERIFIED",
            ))
            print(f"[init_db] Seeded customer: {cid} ({name}, {job}, {city} {state})")
    db.flush()

    # ── 6. Demo merchants — one per Kaggle category ───────────
    # Exact merchant names from Kaggle fraudTrain.csv top merchants per category.
    # FrequencyEncoder will recognize these and produce non-zero encodings.
    demo_merchants = [
        ("mc001", "Lebsack and Sons",                   "misc_net",     37.5, -122.0),
        ("mc002", "Hackett-Lueilwitz",                  "grocery_pos",  34.1, -118.2),
        ("mc003", "Parker, Nolan and Trantow",          "entertainment",36.8,  -76.3),
        ("mc004", "Cummerata-Jones",                    "gas_transport",33.0, -117.1),
        ("mc005", "Gislason Group",                     "misc_pos",     42.9,  -88.0),
        ("mc006", "Dach-Borer",                         "grocery_net",  40.7,  -74.0),
        ("mc007", "Fisher Inc",                         "shopping_net", 34.7,  -86.5),
        ("mc008", "Stoltenberg-Beatty",                 "shopping_pos", 45.3, -118.1),
        ("mc009", "Hermiston, Russel and Price",        "food_dining",  30.5,  -87.9),
        ("mc010", "Kautzer and Sons",                   "personal_care",24.7,  -81.4),
        ("mc011", "Mueller, Gerhold and Mueller",       "health_fitness",42.2, -83.4),
        ("mc012", "Corwin-Romaguera",                   "travel",       40.7,  -73.5),
        ("mc013", "Hilpert-Conroy",                     "kids_pets",    36.6,  -78.9),
        ("mc014", "Terry Ltd",                          "home",         48.9, -118.2),
    ]
    for mid, name, cat, mlat, mlon in demo_merchants:
        if not db.query(Merchant).filter_by(merchant_id=mid).first():
            db.add(Merchant(
                merchant_id=mid, merchant_code=mid,
                merchant_name=name, merchant_category=cat,
                latitude=mlat, longitude=mlon, risk_level="LOW",
            ))
            print(f"[init_db] Seeded merchant: {mid} ({name}, {cat})")
    db.commit()


with SessionLocal() as db:
    _seed(db)

print("[init_db] Done.")
