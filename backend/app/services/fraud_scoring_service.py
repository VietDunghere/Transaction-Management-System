from __future__ import annotations
from typing import Optional, List, Dict, Any
"""
Service: FraudScoringService
Core ML integration — load model, build features, predict fraud score.

Pipeline features (khớp với training trong fraud_detection_final.py):
  Categorical → FrequencyEncoder: merchant, job, city, state
  Categorical → OneHotEncoder:    category
  Ordinal:                         gender (F=0, M=1)
  Numerical → RobustScaler:       amt, city_pop, age, dist_km,
                                   cc_avg_daily, cc_total, cc_avg_amt, cc_std_amt, amt_dev
  Passthrough:                     txn_hour, txn_dow, txn_month, is_weekend, is_night, is_sus_dist
"""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np

from app.core.config import get_settings
from app.core.exceptions import ModelNotLoadedError
from app.core.logging import get_logger
from app.utils.haversine import haversine_km

settings = get_settings()
logger = get_logger(__name__)


@dataclass
class FraudScoringInput:
    """
    Tất cả thông tin cần thiết để tính fraud score.
    Services layer cung cấp object này sau khi load đủ dữ liệu từ DB.
    """
    # Transaction
    amount: float
    txn_time: datetime
    category: str              # merchant category (VD: grocery_pos)
    merchant_name: str         # tên merchant (không có prefix fraud_)

    # Customer
    gender: str                # F | M
    job: str
    city: str
    state: str
    city_population: int
    date_of_birth: datetime
    customer_lat: float
    customer_lon: float

    # Merchant
    merchant_lat: float
    merchant_lon: float

    # Card velocity (từ card_velocity_stats)
    cc_avg_daily_txn: float
    cc_total_txn: int
    cc_avg_amt: float
    cc_std_amt: float


@dataclass
class FraudScoringOutput:
    """Kết quả trả về sau khi chạy model."""
    fraud_score: float                     # 0.0 → 1.0
    decision: str                          # APPROVED | MANUAL_REVIEW | REJECTED
    reject_threshold: float
    review_threshold: float
    model_version: str
    feature_snapshot: dict                 # Feature vector đã dùng (cho audit)
    top_risk_factors: List[str]            # Tên features có importance cao nhất


class FraudScoringService:
    """
    Singleton service load model 1 lần lúc startup, score mỗi request.
    Thread-safe vì sklearn predict là stateless sau khi fit.
    """

    _instance: "FraudScoringService | None" = None
    _pipeline = None                       # sklearn Pipeline (ColumnTransformer + RF)
    _feature_names: List[str] = []
    _feature_importances: np.ndarray | None = None

    @classmethod
    def get_instance(cls) -> "FraudScoringService":
        """Singleton accessor."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        self._is_loaded = False
        self._load_model()

    def _load_model(self) -> None:
        """
        Load sklearn Pipeline từ file .pkl.
        Nếu file không tồn tại → log warning, không raise để app vẫn khởi động được.
        """
        model_path = Path(settings.fraud_model_path)
        if not model_path.exists():
            logger.warning(
                "model_not_found",
                path=str(model_path),
                hint="Serialize model trước: joblib.dump(pipeline, path)"
            )
            return

        try:
            self._pipeline = joblib.load(model_path)
            self._is_loaded = True
            # Lấy feature importances từ Random Forest cuối pipeline
            rf = self._pipeline.named_steps.get("clf") or self._pipeline.steps[-1][1]
            if hasattr(rf, "feature_importances_"):
                self._feature_importances = rf.feature_importances_
            logger.info("model_loaded", path=str(model_path), version=settings.fraud_model_version)
        except Exception as exc:
            logger.error("model_load_failed", error=str(exc))

    @property
    def is_ready(self) -> bool:
        """Kiểm tra model đã sẵn sàng chưa."""
        return self._is_loaded and self._pipeline is not None

    def score(self, inp: FraudScoringInput) -> FraudScoringOutput:
        """
        Tính fraud score cho 1 giao dịch.

        Args:
            inp: FraudScoringInput với đầy đủ thông tin

        Returns:
            FraudScoringOutput với score, decision, và feature snapshot

        Raises:
            ModelNotLoadedError: nếu model chưa được load
        """
        if not self.is_ready:
            raise ModelNotLoadedError()

        # ---- Build feature dict ----
        features = self._build_features(inp)

        # ---- Predict ----
        import pandas as pd
        df = pd.DataFrame([features])
        fraud_prob = float(self._pipeline.predict_proba(df)[:, 1][0])

        # ---- Apply thresholds ----
        reject_th = settings.fraud_reject_threshold
        review_th = settings.fraud_review_threshold

        if fraud_prob >= reject_th:
            decision = "REJECTED"
        elif fraud_prob >= review_th:
            decision = "MANUAL_REVIEW"
        else:
            decision = "APPROVED"

        # ---- Top risk factors (dựa vào feature importance) ----
        top_features = self._get_top_risk_factors(features, n=5)

        return FraudScoringOutput(
            fraud_score=round(fraud_prob, 4),
            decision=decision,
            reject_threshold=reject_th,
            review_threshold=review_th,
            model_version=settings.fraud_model_version,
            feature_snapshot=features,
            top_risk_factors=top_features,
        )

    # ============================================================
    # Private helpers
    # ============================================================

    def _build_features(self, inp: FraudScoringInput) -> dict:
        """
        Xây dựng feature dict từ FraudScoringInput.
        Thứ tự và tên field phải khớp với training pipeline.
        """
        txn = inp.txn_time
        txn_hour = txn.hour
        txn_dow = txn.weekday()    # Monday=0, Sunday=6
        txn_month = txn.month

        # Tính tuổi khách hàng (clip 18-100 như lúc train)
        age = max(18, min(100, txn.year - inp.date_of_birth.year))

        # Khoảng cách customer home → merchant (km)
        dist_km = haversine_km(
            inp.customer_lat, inp.customer_lon,
            inp.merchant_lat, inp.merchant_lon,
        )

        # Amount deviation: số std dev cách mean ([z-score biến thể])
        amt_dev = (inp.amount - inp.cc_avg_amt) / (inp.cc_std_amt + 1e-6)

        return {
            # Categorical (FreqEncoder)
            "merchant": inp.merchant_name,
            "job": inp.job,
            "city": inp.city,
            "state": inp.state,
            # Categorical (OneHot)
            "category": inp.category,
            # Ordinal
            "gender": inp.gender,
            # Numerical (RobustScaler)
            "amt": inp.amount,
            "city_pop": inp.city_population,
            "age": age,
            "dist_km": dist_km,
            "cc_avg_daily": inp.cc_avg_daily_txn,
            "cc_total": inp.cc_total_txn,
            "cc_avg_amt": inp.cc_avg_amt,
            "cc_std_amt": inp.cc_std_amt,
            "amt_dev": amt_dev,
            # Passthrough binary features
            "txn_hour": txn_hour,
            "txn_dow": txn_dow,
            "txn_month": txn_month,
            "is_weekend": int(txn_dow >= 5),
            "is_night": int(txn_hour >= 23 or txn_hour <= 6),
            "is_sus_dist": int(dist_km > 100),
        }

    def _get_top_risk_factors(self, features: dict, n: int = 5) -> list[str]:
        """
        Trả về n features có importance cao nhất trong lần predict này.
        Dùng global feature importances từ RF — không phải SHAP (nhanh hơn).
        """
        if self._feature_importances is None:
            return []
        feature_keys = list(features.keys())
        # Lấy n indices cao nhất
        top_indices = np.argsort(self._feature_importances)[::-1][:n]
        return [
            feature_keys[i] for i in top_indices if i < len(feature_keys)
        ]
