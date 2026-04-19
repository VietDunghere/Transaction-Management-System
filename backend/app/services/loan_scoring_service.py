from __future__ import annotations
"""
Service: LoanScoringService
Load trained loan-approval model (Optuna-optimised RandomForest pipeline),
build features, predict Probability-of-Default (PD Score).

Feature contract (must match train_loan_model.py):
  Numerical   : person_age, person_income, person_emp_length,
                loan_amnt, loan_int_rate, loan_percent_income,
                cb_person_cred_hist_length
  Categorical : person_home_ownership, loan_intent, loan_grade,
                cb_person_default_on_file
"""

import json
from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from app.core.config import get_settings
from app.core.exceptions import ModelNotLoadedError
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


# ────────────────────────────────────────────────────────────────
# Data contracts
# ────────────────────────────────────────────────────────────────
@dataclass
class LoanSimulationInput:
    person_age: int
    person_income: float
    person_home_ownership: str
    person_emp_length: int
    loan_intent: str
    loan_grade: str
    loan_amnt: float
    loan_int_rate: float
    cb_person_default_on_file: str
    cb_person_cred_hist_length: int


@dataclass
class LoanSimulationOutput:
    pd_score: float
    risk_level: str
    top_risk_factors: list[str]
    model_version: str


# ────────────────────────────────────────────────────────────────
# Service
# ────────────────────────────────────────────────────────────────
class LoanScoringService:
    """
    Singleton service — load loan model 1 lần khi startup, score từng request.
    Thread-safe: sklearn predict là stateless sau khi fit.
    """

    _instance: "LoanScoringService | None" = None
    _preprocessor = None
    _classifier = None
    _decision_threshold = 0.50
    _feature_names: list[str] = []
    _feature_importances: np.ndarray | None = None

    @classmethod
    def get_instance(cls) -> "LoanScoringService":
        """Singleton accessor — khởi tạo instance nếu chưa có."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        self._is_loaded = False
        self._metadata: dict = {}
        self._load_model()

    def _load_model(self) -> None:
        """
        Load artifact model từ file .pkl.
        Hỗ trợ cả 2 format: dict artifact (mới) và sklearn Pipeline (cũ).
        """
        model_path = Path(settings.loan_model_path)
        meta_path = model_path.parent / "loan_model_metadata.json"

        if not model_path.exists():
            logger.warning(
                "loan_model_not_found",
                path=str(model_path),
                hint="Chạy train_loan_model.py để tạo model.",
            )
            return

        try:
            artifact = joblib.load(model_path)

            # Định dạng dict artifact (mới) — có key "classifier"
            if isinstance(artifact, dict) and "classifier" in artifact:
                self._preprocessor = artifact.get("preprocessor")
                self._classifier = artifact.get("classifier")
                self._decision_threshold = artifact.get("threshold", 0.50)
            else:
                # Fallback sang Pipeline cũ nếu load model version trước
                self._preprocessor = artifact.named_steps.get("preprocessor")
                self._classifier = artifact.named_steps.get("classifier")
                self._decision_threshold = 0.50

            self._is_loaded = True

            # Load metadata nếu file tồn tại
            if meta_path.exists():
                with open(meta_path, "r") as f:
                    self._metadata = json.load(f)

            # Lấy feature importances từ classifier
            clf = self._classifier
            if hasattr(clf, "feature_importances_"):
                self._feature_importances = clf.feature_importances_
            elif hasattr(clf, "coef_"):
                self._feature_importances = np.abs(clf.coef_[0])

            # Lấy tên features sau khi transform
            if self._preprocessor is not None:
                try:
                    self._feature_names = list(self._preprocessor.get_feature_names_out())
                except Exception:
                    self._feature_names = []

            logger.info(
                "loan_model_loaded",
                path=str(model_path),
                version=self._metadata.get("model_version", settings.loan_model_version),
                n_features=len(self._feature_names),
                threshold=self._decision_threshold,
            )
        except Exception as exc:
            logger.error("loan_model_load_failed", error=str(exc))

    @property
    def is_ready(self) -> bool:
        """Kiểm tra model đã load xong và sẵn sàng score."""
        return self._is_loaded and self._classifier is not None and self._preprocessor is not None

    def simulate(
        self,
        inp: LoanSimulationInput,
        high_risk_threshold: float | None = None,
        medium_risk_threshold: float | None = None,
    ) -> LoanSimulationOutput:
        """
        Chạy ML inference để dự báo xác suất vỡ nợ (PD Score).
        Fallback sang heuristic nếu model chưa sẵn sàng.
        """
        if not self.is_ready:
            logger.warning("loan_model_not_loaded_fallback")
            return self._fallback_heuristic(inp)

        features = self._build_features(inp)
        df = pd.DataFrame([features])

        # Bước 1: Preprocess để lấy feature vector đã transform
        X_trans = self._preprocessor.transform(df)

        # Bước 2: Dự báo xác suất class 1 (vỡ nợ)
        pd_score = float(self._classifier.predict_proba(X_trans)[:, 1][0])

        # Bước 3: Phân loại mức rủi ro (DB override nếu có, fallback về settings)
        high_th = high_risk_threshold if high_risk_threshold is not None else settings.loan_high_risk_threshold
        medium_th = medium_risk_threshold if medium_risk_threshold is not None else settings.loan_medium_risk_threshold
        if pd_score >= high_th:
            risk_level = "HIGH RISK"
        elif pd_score >= medium_th:
            risk_level = "MEDIUM RISK"
        else:
            risk_level = "LOW RISK"

        top_factors = self._get_top_risk_factors(features)

        return LoanSimulationOutput(
            pd_score=round(pd_score, 4),
            risk_level=risk_level,
            top_risk_factors=top_factors,
            model_version=self._metadata.get("model_version", settings.loan_model_version),
        )

    def _build_features(self, inp: LoanSimulationInput) -> dict:
        """
        Xây dựng feature dict từ input. Tên cột phải khớp với ALL_FEATURE_COLS trong training pipeline.
        Bao gồm các engineered features bổ sung từ v4.
        """
        age = inp.person_age
        income = inp.person_income
        rate = inp.loan_int_rate

        # Age group binning
        if age <= 25:
            age_group = "young"
        elif age <= 35:
            age_group = "adult"
        elif age <= 50:
            age_group = "middle"
        else:
            age_group = "senior"

        # Income binning
        if income <= 30_000:
            income_bin = "low"
        elif income <= 60_000:
            income_bin = "mid"
        elif income <= 120_000:
            income_bin = "high"
        else:
            income_bin = "very_high"

        # Interest rate binning
        if rate <= 10.0:
            int_rate_bin = "low"
        elif rate <= 15.0:
            int_rate_bin = "mid"
        else:
            int_rate_bin = "high"

        grade_to_num = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6}

        return {
            # Numerical — cơ bản
            "person_age": age,
            "person_income": income,
            "person_emp_length": inp.person_emp_length,
            "loan_amnt": inp.loan_amnt,
            "loan_int_rate": rate,
            "loan_percent_income": inp.loan_amnt / max(income, 1),
            "cb_person_cred_hist_length": inp.cb_person_cred_hist_length,
            # Numerical — engineered v6 (phải khớp với engineer_features trong train_loan_model.py)
            "debt_burden": (inp.loan_amnt * rate / 100.0) / max(income, 1),
            "loan_grade_numeric": float(grade_to_num.get(inp.loan_grade.upper(), 3)),
            # Categorical — normalize uppercase để khớp dữ liệu training
            # Normalize uppercase để khớp với dữ liệu training
            "person_home_ownership": inp.person_home_ownership.upper(),
            "loan_intent": inp.loan_intent.upper(),
            "loan_grade": inp.loan_grade.upper(),
            "cb_person_default_on_file": inp.cb_person_default_on_file.upper(),
            # Engineered categorical — bin boundaries cố định
            "age_group": age_group,
            "income_bin": income_bin,
            "int_rate_bin": int_rate_bin,
        }

    def _get_top_risk_factors(self, features: dict, n: int = 5) -> list[str]:
        """
        Ánh xạ feature importances sau transform về tên cột gốc.
        Gộp các features OneHot-expanded lại theo cột gốc.
        """
        if self._feature_importances is None or not self._feature_names:
            # Fallback dùng metadata từ lúc training nếu có
            raw_keys = list(
                self._metadata.get(
                    "feature_importances_top10",
                    {"loan_percent_income": 0, "loan_int_rate": 0, "loan_grade": 0},
                ).keys()
            )
            # Bỏ prefix transformer (num__, cat__, eng__) để dễ đọc
            clean_keys = [
                k.split("__", 1)[-1] if "__" in k else k for k in raw_keys
            ]
            return clean_keys[:n]

        # Tên sau transform dạng: "num__person_age", "cat__loan_grade_A", v.v.
        original_importance: dict[str, float] = {}
        for fname, imp in zip(self._feature_names, self._feature_importances):
            clean = fname.split("__", 1)[-1] if "__" in fname else fname
            # OneHot: "loan_grade_A" → "loan_grade"
            original_col = clean
            for col in list(features.keys()):
                if clean.startswith(col):
                    original_col = col
                    break
            original_importance[original_col] = original_importance.get(original_col, 0.0) + imp

        sorted_features = sorted(original_importance.items(), key=lambda x: x[1], reverse=True)
        return [name for name, _ in sorted_features[:n]]

    def _fallback_heuristic(self, inp: LoanSimulationInput) -> LoanSimulationOutput:
        """Chấm điểm bằng rule đơn giản khi ML model chưa sẵn sàng."""
        income = max(inp.person_income, 1)
        percent = inp.loan_amnt / income

        grade_risk = {"A": 0, "B": 0.1, "C": 0.2, "D": 0.35, "E": 0.5, "F": 0.65, "G": 0.8}
        score = (
            0.4 * min(percent / 0.5, 1.0)
            + 0.3 * grade_risk.get(inp.loan_grade, 0.5)
            + 0.2 * (inp.loan_int_rate / 23.0)
            + 0.1 * (1 if inp.cb_person_default_on_file == "Y" else 0)
        )
        pd_score = min(max(score, 0.01), 0.99)

        if pd_score >= 0.50:
            risk_level = "HIGH RISK"
        elif pd_score >= 0.20:
            risk_level = "MEDIUM RISK"
        else:
            risk_level = "LOW RISK"

        return LoanSimulationOutput(
            pd_score=round(pd_score, 4),
            risk_level=risk_level,
            top_risk_factors=["loan_percent_income", "loan_grade", "loan_int_rate"],
            model_version="heuristic_fallback",
        )
