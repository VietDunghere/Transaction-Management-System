from __future__ import annotations
"""
Cấu hình ứng dụng — đọc từ biến môi trường (.env)
Dùng pydantic-settings để validate kiểu dữ liệu ngay khi khởi động.
"""

from functools import lru_cache
from typing import Optional, List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ---- Application ----
    app_name: str = "Transaction Management System"
    app_env: str = "development"
    debug: bool = False

    # ---- Database ----
    # Oracle 19c: oracle+oracledb://tms_user:password@localhost:1521/?service_name=ORCLPDB1
    # SQLite (dev fallback): sqlite:///./tms.db
    database_url: str = "sqlite:///./tms.db"

    # ---- JWT ----
    jwt_secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7

    # ---- Fraud Detection Model ----
    fraud_model_path: str = "./ml_models/fraud_rf_v3.pkl"
    fraud_reject_threshold: float = 0.45
    fraud_review_threshold: float = 0.05
    fraud_model_version: str = "rf_v3_regularized"

    # ---- Loan Approval Model ----
    loan_model_path: str = "./ml_models/loan_model.pkl"
    loan_high_risk_threshold: float = 0.50
    loan_medium_risk_threshold: float = 0.20
    loan_model_version: str = "loan_v5_xgboost"

    # ---- API ----
    api_prefix: str = "/api/v1"
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    @field_validator("app_env")
    @classmethod
    def validate_env(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"app_env phải là một trong: {allowed}")
        return v

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """
    Singleton settings — chỉ đọc file .env 1 lần.
    Dùng lru_cache để cache kết quả, tránh parse lại mỗi request.
    """
    return Settings()
