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
import typing
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
    Singleton service — load loan model once at startup, score per request.
    Thread-safe: sklearn predict is stateless after fit.
    """

    _instance: "LoanScoringService | None" = None
    _preprocessor = None
    _classifier = None
    _decision_threshold = 0.50
    _feature_names: list[str] = []
    _feature_importances: np.ndarray | None = None

    @classmethod
    def get_instance(cls) -> "LoanScoringService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        self._is_loaded = False
        self._metadata: dict = {}
        self._load_model()

    # ── Model loading ────────────────────────────────────────────
    def _load_model(self) -> None:
        model_path = Path(settings.loan_model_path)
        meta_path = model_path.parent / "loan_model_metadata.json"

        if not model_path.exists():
            logger.warning(
                "loan_model_not_found",
                path=str(model_path),
                hint="Run train_loan_model.py to generate model.",
            )
            return

        try:
            artifact = joblib.load(model_path)
            
            # Extract components from new Dictionary Artifact format
            if isinstance(artifact, dict) and "classifier" in artifact:
                self._preprocessor = artifact.get("preprocessor")
                self._classifier = artifact.get("classifier")
                self._decision_threshold = artifact.get("threshold", 0.50)
            else:
                # Fallback to old Pipeline architecture if old model loaded
                self._preprocessor = artifact.named_steps.get("preprocessor")
                self._classifier = artifact.named_steps.get("classifier")
                self._decision_threshold = 0.50
                
            self._is_loaded = True

            # Load metadata if available
            if meta_path.exists():
                with open(meta_path, "r") as f:
                    self._metadata = json.load(f)

            # Extract feature importances from classifier
            clf = self._classifier
            if hasattr(clf, "feature_importances_"):
                self._feature_importances = clf.feature_importances_
            elif hasattr(clf, "coef_"):
                self._feature_importances = np.abs(clf.coef_[0])

            # Extract transformed feature names from preprocessor
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
                threshold=self._decision_threshold
            )
        except Exception as exc:
            logger.error("loan_model_load_failed", error=str(exc))

    # ── Public API ───────────────────────────────────────────────
    @property
    def is_ready(self) -> bool:
        return self._is_loaded and self._classifier is not None and self._preprocessor is not None

    def simulate(self, inp: LoanSimulationInput) -> LoanSimulationOutput:
        """
        Run ML inference to predict PD Score.
        Falls back to a heuristic if model is not loaded.
        """
        if not self.is_ready:
            logger.warning("loan_model_not_loaded_fallback")
            return self._fallback_heuristic(inp)

        features = self._build_features(inp)
        df = pd.DataFrame([features])

        # Step 1: Preprocess to get transformed features
        X_trans = self._preprocessor.transform(df)
        
        # Step 2: Predict probability class 1 (Default)
        pd_score = float(self._classifier.predict_proba(X_trans)[:, 1][0])

        # Step 3: Risk classification using config thresholds
        if pd_score >= settings.loan_high_risk_threshold:
            risk_level = "HIGH RISK"
        elif pd_score >= settings.loan_medium_risk_threshold:
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

    # ── Feature building ─────────────────────────────────────────
    def _build_features(self, inp: LoanSimulationInput) -> dict:
        """
        Build feature dict from input. Column names and order MUST match
        the training pipeline's ALL_FEATURE_COLS.
        Includes engineered features added in v4.
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
            # Numerical — base
            "person_age": age,
            "person_income": income,
            "person_emp_length": inp.person_emp_length,
            "loan_amnt": inp.loan_amnt,
            "loan_int_rate": rate,
            "loan_percent_income": inp.loan_amnt / max(income, 1),
            "cb_person_cred_hist_length": inp.cb_person_cred_hist_length,
            # Numerical — v6 engineered (must match train_loan_model.py engineer_features)
            "debt_burden": (inp.loan_amnt * rate / 100.0) / max(income, 1),
            "loan_grade_numeric": float(grade_to_num.get(inp.loan_grade.upper(), 3)),
            # Categorical — normalize to uppercase to match training data
            "person_home_ownership": inp.person_home_ownership.upper(),
            "loan_intent": inp.loan_intent.upper(),
            "loan_grade": inp.loan_grade.upper(),
            "cb_person_default_on_file": inp.cb_person_default_on_file.upper(),
            # Engineered categorical (fixed bin boundaries)
            "age_group": age_group,
            "income_bin": income_bin,
            "int_rate_bin": int_rate_bin,
        }

    # ── Feature importance (proper mapping) ──────────────────────
    def _get_top_risk_factors(self, features: dict, n: int = 5) -> list[str]:
        """
        Map transformed feature importances back to original column names.
        Handles OneHot-expanded features by aggregating per original column.
        """
        if self._feature_importances is None or not self._feature_names:
            # Fallback: use metadata from training if available
            raw_keys = list(
                self._metadata.get(
                    "feature_importances_top10",
                    {"loan_percent_income": 0, "loan_int_rate": 0, "loan_grade": 0},
                ).keys()
            )
            # Strip transformer prefixes (num__, cat__, eng__) for readability
            clean_keys = [
                k.split("__", 1)[-1] if "__" in k else k for k in raw_keys
            ]
            return clean_keys[:n]

        # Aggregate importances back to original column names
        # Transformed names look like: "num__person_age", "cat__loan_grade_A", etc.
        original_importance: dict[str, float] = {}
        for fname, imp in zip(self._feature_names, self._feature_importances):
            # Strip prefix (num__, cat__)
            clean = fname.split("__", 1)[-1] if "__" in fname else fname
            # For OneHot features, map "loan_grade_A" → "loan_grade"
            original_col = clean
            for col in list(features.keys()):
                if clean.startswith(col):
                    original_col = col
                    break
            original_importance[original_col] = original_importance.get(original_col, 0.0) + imp

        # Sort descending and return top n
        sorted_features = sorted(original_importance.items(), key=lambda x: x[1], reverse=True)
        return [name for name, _ in sorted_features[:n]]

    # ── Fallback heuristic ───────────────────────────────────────
    def _fallback_heuristic(self, inp: LoanSimulationInput) -> LoanSimulationOutput:
        """Simple rule-based scoring when ML model is unavailable."""
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
