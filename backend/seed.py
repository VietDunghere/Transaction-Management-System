"""
Seed dữ liệu khởi tạo cho Hệ thống Phân tích Rủi ro và Đánh giá Tài chính.
Chạy: python seed.py
Yêu cầu: DB đã tạo bảng (SQLAlchemy create_tables hoặc Alembic migrate xong).
Matches ERD v2 schema.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import date, datetime
import uuid

from sqlalchemy.orm import Session

from app.db.base import SessionLocal, create_tables
from app.core.security import hash_password
from app.models.user import User
from app.models.customer import Customer
from app.models.merchant import Merchant, Channel
from app.models.loan import Loan
from app.models.analyst import ModelConfig


def seed(db: Session) -> None:
    # ── Users (ERD v2: role + status inline) ───────────────────
    users_data = [
        {"username": "admin",    "password": "Admin@123",    "full_name": "System Admin",      "email": "admin@tms.local",    "role": "ADMIN"},
        {"username": "operator1","password": "Operator@123", "full_name": "Nguyễn Văn Operator","email": "op1@tms.local",     "role": "OPERATOR"},
        {"username": "operator2","password": "Operator@123", "full_name": "Trần Thị Operator",  "email": "op2@tms.local",     "role": "OPERATOR"},
        {"username": "reviewer1","password": "Reviewer@123", "full_name": "Lê Văn Reviewer",    "email": "rev1@tms.local",    "role": "REVIEWER"},
        {"username": "manager1",  "password": "Manager@123",  "full_name": "Phạm Thị Manager",   "email": "mgr1@tms.local",    "role": "MANAGER"},
        {"username": "analyst1",  "password": "Analyst@123",  "full_name": "Hoàng Văn Analyst",  "email": "ana1@tms.local",    "role": "ANALYST"},
    ]

    for u_data in users_data:
        existing = db.query(User).filter(User.username == u_data["username"]).first()
        if existing:
            print(f"[users] skip {u_data['username']} (exists)")
            continue

        user = User(
            user_id=str(uuid.uuid4()),
            username=u_data["username"],
            password_hash=hash_password(u_data["password"]),
            full_name=u_data["full_name"],
            email=u_data["email"],
            role=u_data["role"],
            status="ACTIVE",
        )
        db.add(user)
        db.flush()
        print(f"[users] created {user.username} ({u_data['role']})")

    # ── Channels ────────────────────────────────────────────
    channels_data = [
        {"channel_code": "POS",        "channel_name": "Point of Sale"},
        {"channel_code": "ATM",        "channel_name": "ATM"},
        {"channel_code": "ONLINE",     "channel_name": "Online Banking"},
        {"channel_code": "MOBILE_APP", "channel_name": "Mobile App"},
    ]

    for c_data in channels_data:
        existing = db.query(Channel).filter(Channel.channel_code == c_data["channel_code"]).first()
        if not existing:
            db.add(Channel(**c_data))
            print(f"[channels] created {c_data['channel_code']}")
        else:
            print(f"[channels] skip {c_data['channel_code']} (exists)")

    # ── Customers (ERD v2: no state, zip_code, city_population) ─
    customers_data = [
        {
            "customer_id": "cust-0001-0000-0000-000000000001",
            "customer_code": "CUST001",
            "full_name": "Nguyễn Văn An",
            "date_of_birth": date(1990, 5, 15),
            "gender": "M",
            "job": "engineer",
            "city": "Ho Chi Minh City",
            "latitude": 10.7769,
            "longitude": 106.7009,
            "kyc_status": "VERIFIED",
            "income_level": "MEDIUM",
        },
        {
            "customer_id": "cust-0002-0000-0000-000000000002",
            "customer_code": "CUST002",
            "full_name": "Trần Thị Bình",
            "date_of_birth": date(1985, 8, 22),
            "gender": "F",
            "job": "teacher",
            "city": "Hanoi",
            "latitude": 21.0245,
            "longitude": 105.8412,
            "kyc_status": "VERIFIED",
            "income_level": "LOW",
        },
        {
            "customer_id": "cust-0003-0000-0000-000000000003",
            "customer_code": "CUST003",
            "full_name": "Lê Minh Cường",
            "date_of_birth": date(1978, 3, 10),
            "gender": "M",
            "job": "manager",
            "city": "Da Nang",
            "latitude": 16.0544,
            "longitude": 108.2022,
            "kyc_status": "VERIFIED",
            "income_level": "HIGH",
        },
    ]

    for c_data in customers_data:
        existing = db.query(Customer).filter(Customer.customer_id == c_data["customer_id"]).first()
        if not existing:
            db.add(Customer(**c_data))
            print(f"[customers] created {c_data['customer_code']}")
        else:
            print(f"[customers] skip {c_data['customer_code']} (exists)")

    # ── Merchants ───────────────────────────────────────────
    merchants_data = [
        {
            "merchant_id": "mcht-0001-0000-0000-000000000001",
            "merchant_code": "MCHT001",
            "merchant_name": "Vinmart",
            "merchant_category": "grocery_pos",
            "city": "Ho Chi Minh City",
            "state": "HCM",
            "country": "VN",
            "risk_level": "LOW",
            "is_blacklisted": False,
            "latitude": 10.7800,
            "longitude": 106.6950,
        },
        {
            "merchant_id": "mcht-0002-0000-0000-000000000002",
            "merchant_code": "MCHT002",
            "merchant_name": "Shopee Online",
            "merchant_category": "shopping_net",
            "city": "Ho Chi Minh City",
            "state": "HCM",
            "country": "VN",
            "risk_level": "LOW",
            "is_blacklisted": False,
            "latitude": 10.7880,
            "longitude": 106.7040,
        },
        {
            "merchant_id": "mcht-0003-0000-0000-000000000003",
            "merchant_code": "MCHT003",
            "merchant_name": "CGV Cinema",
            "merchant_category": "entertainment",
            "city": "Hanoi",
            "state": "HN",
            "country": "VN",
            "risk_level": "LOW",
            "is_blacklisted": False,
            "latitude": 21.0300,
            "longitude": 105.8500,
        },
        {
            "merchant_id": "mcht-0004-0000-0000-000000000004",
            "merchant_code": "MCHT004",
            "merchant_name": "Unknown Online Store",
            "merchant_category": "misc_net",
            "city": "Unknown",
            "state": "XX",
            "country": "VN",
            "risk_level": "HIGH",
            "is_blacklisted": False,
            "latitude": 0.0,
            "longitude": 0.0,
        },
    ]

    for m_data in merchants_data:
        existing = db.query(Merchant).filter(Merchant.merchant_id == m_data["merchant_id"]).first()
        if not existing:
            db.add(Merchant(**m_data))
            print(f"[merchants] created {m_data['merchant_code']}")
        else:
            print(f"[merchants] skip {m_data['merchant_code']} (exists)")

    # ── Loans (ERD v2: no currency_code, added model_version) ──
    db.flush()
    op_user = db.query(User).filter(User.username == "operator1").first()
    mgr_user = db.query(User).filter(User.username == "manager1").first()

    if not op_user:
        print("[loans] skip — operator1 user not found")
    else:
        loans_data = [
            {
                "loan_id": "loan-0001-0000-0000-000000000001",
                "customer_id": "cust-0003-0000-0000-000000000003",
                "submitted_by": op_user.user_id,
                "principal_amount": 15000.00,
                "interest_rate": 0.0750,
                "term_months": 36,
                "purpose": "Home improvement loan",
                "status": "APPROVED",
                "reviewed_by": mgr_user.user_id if mgr_user else None,
                "review_note": "AI low risk — approved",
                "reviewed_at": datetime(2026, 4, 15, 10, 0, 0),
                "person_age": 48,
                "person_income": 150000.00,
                "person_home_ownership": "OWN",
                "person_emp_length": 20,
                "loan_grade": "A",
                "loan_intent": "HOMEIMPROVEMENT",
                "cb_person_default_on_file": "N",
                "cb_person_cred_hist_length": 22,
                "pd_score": 0.0523,
                "risk_level": "LOW RISK",
            },
            {
                "loan_id": "loan-0002-0000-0000-000000000002",
                "customer_id": "cust-0001-0000-0000-000000000001",
                "submitted_by": op_user.user_id,
                "principal_amount": 20000.00,
                "interest_rate": 0.1350,
                "term_months": 48,
                "purpose": "Personal loan for renovation",
                "status": "PENDING",
                "person_age": 36,
                "person_income": 65000.00,
                "person_home_ownership": "MORTGAGE",
                "person_emp_length": 8,
                "loan_grade": "C",
                "loan_intent": "PERSONAL",
                "cb_person_default_on_file": "N",
                "cb_person_cred_hist_length": 10,
                "pd_score": 0.2814,
                "risk_level": "MEDIUM RISK",
            },
            {
                "loan_id": "loan-0003-0000-0000-000000000003",
                "customer_id": "cust-0002-0000-0000-000000000002",
                "submitted_by": op_user.user_id,
                "principal_amount": 25000.00,
                "interest_rate": 0.1980,
                "term_months": 60,
                "purpose": "Education loan for MBA program",
                "status": "REJECTED",
                "reviewed_by": mgr_user.user_id if mgr_user else None,
                "review_note": "AI high risk — PD score exceeds threshold",
                "reviewed_at": datetime(2026, 4, 16, 14, 30, 0),
                "person_age": 24,
                "person_income": 28000.00,
                "person_home_ownership": "RENT",
                "person_emp_length": 2,
                "loan_grade": "E",
                "loan_intent": "EDUCATION",
                "cb_person_default_on_file": "Y",
                "cb_person_cred_hist_length": 3,
                "pd_score": 0.8721,
                "risk_level": "HIGH RISK",
            },
            {
                "loan_id": "loan-0004-0000-0000-000000000004",
                "customer_id": "cust-0001-0000-0000-000000000001",
                "submitted_by": op_user.user_id,
                "principal_amount": 30000.00,
                "interest_rate": 0.1650,
                "term_months": 24,
                "purpose": "Startup venture capital",
                "status": "PENDING",
                "person_age": 36,
                "person_income": 65000.00,
                "person_home_ownership": "MORTGAGE",
                "person_emp_length": 8,
                "loan_grade": "D",
                "loan_intent": "VENTURE",
                "cb_person_default_on_file": "N",
                "cb_person_cred_hist_length": 10,
                "pd_score": 0.4256,
                "risk_level": "MEDIUM RISK",
            },
            {
                "loan_id": "loan-0005-0000-0000-000000000005",
                "customer_id": "cust-0003-0000-0000-000000000003",
                "submitted_by": op_user.user_id,
                "principal_amount": 8000.00,
                "interest_rate": 0.0920,
                "term_months": 12,
                "purpose": "Medical procedure expenses",
                "status": "APPROVED",
                "reviewed_by": mgr_user.user_id if mgr_user else None,
                "review_note": "Low risk profile — approved promptly",
                "reviewed_at": datetime(2026, 4, 14, 9, 15, 0),
                "person_age": 48,
                "person_income": 150000.00,
                "person_home_ownership": "OWN",
                "person_emp_length": 20,
                "loan_grade": "B",
                "loan_intent": "MEDICAL",
                "cb_person_default_on_file": "N",
                "cb_person_cred_hist_length": 22,
                "pd_score": 0.0891,
                "risk_level": "LOW RISK",
            },
        ]

        for l_data in loans_data:
            existing = db.query(Loan).filter(Loan.loan_id == l_data["loan_id"]).first()
            if not existing:
                db.add(Loan(**l_data))
                print(f"[loans] created {l_data['loan_id'][:18]}... ({l_data['status']}, {l_data['risk_level']})")
            else:
                print(f"[loans] skip {l_data['loan_id'][:18]}... (exists)")

    # ── ModelConfig defaults ────────────────────────────────
    model_configs_data = [
        {"model_name": "fraud", "param_name": "reject_threshold",       "param_value": 0.65,  "description": "Ngưỡng từ chối tự động (fraud_score >= threshold → REJECTED)"},
        {"model_name": "fraud", "param_name": "review_threshold",       "param_value": 0.35,  "description": "Ngưỡng chuyển MANUAL_REVIEW (fraud_score >= threshold → MANUAL_REVIEW)"},
        {"model_name": "loan",  "param_name": "high_risk_threshold",    "param_value": 0.50,  "description": "Ngưỡng HIGH RISK (pd_score >= threshold → HIGH RISK)"},
        {"model_name": "loan",  "param_name": "medium_risk_threshold",  "param_value": 0.20,  "description": "Ngưỡng MEDIUM RISK (pd_score >= threshold → MEDIUM RISK)"},
    ]

    for cfg in model_configs_data:
        existing = db.query(ModelConfig).filter(
            ModelConfig.model_name == cfg["model_name"],
            ModelConfig.param_name == cfg["param_name"],
        ).first()
        if not existing:
            db.add(ModelConfig(**cfg))
            print(f"[model_configs] created {cfg['model_name']}.{cfg['param_name']} = {cfg['param_value']}")
        else:
            print(f"[model_configs] skip {cfg['model_name']}.{cfg['param_name']} (exists)")

    db.commit()
    print("\n[seed] Done.")
    print("\nTest accounts:")
    print("  admin     / Admin@123    (ADMIN)")
    print("  operator1 / Operator@123 (OPERATOR)")
    print("  reviewer1 / Reviewer@123 (REVIEWER)")
    print("  manager1  / Manager@123  (MANAGER)")
    print("  analyst1  / Analyst@123  (ANALYST)")


if __name__ == "__main__":
    print("[seed] Creating tables if not exists...")
    create_tables()

    db = SessionLocal()
    try:
        seed(db)
    except Exception as e:
        db.rollback()
        print(f"[seed] ERROR: {e}")
        raise
    finally:
        db.close()
