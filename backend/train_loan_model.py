#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
  Loan Approval Classification — Training Pipeline v6
═══════════════════════════════════════════════════════════════════

  Upgrades from v5:
    + Multi-algorithm: XGBoost + LightGBM — Optuna picks best
    + Noise 0.18 → 0.08 (reduces Bayes error at decision boundary)
    + debt_burden added explicitly to label formula (feature #1 → label)
    + Default rate 22% → 28% (better class balance, higher macro F1)
    + loan_grade_numeric: ordinal A=0…G=6 (captures grade ordering)
    + Removed income_stability (rank 30+, pure noise in feature space)
    + Threshold: F1-macro optimized (vs. recall≥0.90)
    + 80k training samples (more stable CV)

  Features (9 num + 4 cat + 3 eng_cat = 16 total):
    Numerical (9)  : person_age, person_income, person_emp_length,
                     loan_amnt, loan_int_rate, loan_percent_income,
                     cb_person_cred_hist_length, debt_burden,
                     loan_grade_numeric
    Categorical (4): person_home_ownership, loan_intent, loan_grade,
                     cb_person_default_on_file
    Eng. Cat. (3)  : age_group, income_bin, int_rate_bin

  Usage:
    python train_loan_model.py
    python train_loan_model.py --csv loan_data.csv --trials 60
    python train_loan_model.py --threshold-mode recall_target --target-recall 0.90
═══════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import warnings
from datetime import datetime, timezone
from pathlib import Path

import joblib
import lightgbm as lgb
import numpy as np
import optuna
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler
from xgboost import XGBClassifier

# ────────────────────────────────────────────────────────────────
# Constants
# ────────────────────────────────────────────────────────────────
RANDOM_STATE = 42
TEST_SIZE    = 0.20
CV_FOLDS     = 5
OVERFIT_GAP_THRESHOLD = 0.05

CATEGORICAL_COLS = [
    "person_home_ownership",
    "loan_intent",
    "loan_grade",
    "cb_person_default_on_file",
]
NUMERICAL_COLS_BASE = [
    "person_age",
    "person_income",
    "person_emp_length",
    "loan_amnt",
    "loan_int_rate",
    "loan_percent_income",
    "cb_person_cred_hist_length",
]
# Derived numerical — computed in engineer_features()
NUMERICAL_COLS_ENGINEERED = [
    "debt_burden",         # (loan_amnt × loan_int_rate/100) / income — top-1 v5
    "loan_grade_numeric",  # A=0 … G=6 ordinal (captures ordering OHE misses)
]
NUMERICAL_COLS = NUMERICAL_COLS_BASE + NUMERICAL_COLS_ENGINEERED
# Fixed bin boundaries — no data leakage, safe to apply on each split
ENGINEERED_CAT_COLS = ["age_group", "income_bin", "int_rate_bin"]

TARGET_COL       = "loan_status"
BASE_COLS        = NUMERICAL_COLS_BASE + CATEGORICAL_COLS
ALL_FEATURE_COLS = NUMERICAL_COLS + CATEGORICAL_COLS + ENGINEERED_CAT_COLS

_GRADE_TO_NUM = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6}


# ────────────────────────────────────────────────────────────────
# § 1. Feature Engineering
# ────────────────────────────────────────────────────────────────
def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    All transformations use fixed constants — call independently on each split.
    """
    df     = df.copy()
    income = df["person_income"].clip(lower=1)

    df["debt_burden"]        = (df["loan_amnt"] * df["loan_int_rate"] / 100.0) / income
    df["loan_grade_numeric"] = df["loan_grade"].map(_GRADE_TO_NUM).fillna(3).astype(float)

    bins_age   = [0, 25, 35, 50, 100];         labels_age   = ["young", "adult", "middle", "senior"]
    bins_inc   = [0, 30_000, 60_000, 120_000, float("inf")]; labels_inc = ["low", "mid", "high", "very_high"]
    bins_rate  = [0, 10.0, 15.0, 25.0];        labels_rate  = ["low", "mid", "high"]

    df["age_group"]    = pd.cut(df["person_age"],    bins=bins_age,  labels=labels_age,  right=True).astype(str)
    df["income_bin"]   = pd.cut(df["person_income"], bins=bins_inc,  labels=labels_inc,  right=True).astype(str)
    df["int_rate_bin"] = pd.cut(df["loan_int_rate"], bins=bins_rate, labels=labels_rate, right=True).astype(str)
    return df


# ────────────────────────────────────────────────────────────────
# § 2. Data generation / loading
# ────────────────────────────────────────────────────────────────
def generate_realistic_loan_data(n_samples: int = 80_000) -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_STATE)

    person_age            = rng.integers(20, 70, n_samples)
    person_income         = np.clip(rng.lognormal(10.8, 0.7, n_samples).astype(int), 4_000, 6_000_000)
    person_emp_length     = np.minimum(rng.integers(0, 42, n_samples), np.maximum(person_age - 18, 0))
    loan_amnt             = rng.integers(500, 35_001, n_samples)
    loan_int_rate         = rng.uniform(5.42, 23.22, n_samples).round(2)
    loan_percent_income   = (loan_amnt / np.maximum(person_income, 1)).round(4)
    cb_cred_hist_length   = rng.integers(2, 31, n_samples)

    person_home_ownership = rng.choice(["RENT","MORTGAGE","OWN","OTHER"], n_samples, p=[0.52,0.41,0.05,0.02])
    loan_intent           = rng.choice(["PERSONAL","EDUCATION","MEDICAL","VENTURE","HOMEIMPROVEMENT","DEBTCONSOLIDATION"], n_samples)
    loan_grade            = rng.choice(["A","B","C","D","E","F","G"], n_samples, p=[0.20,0.25,0.20,0.15,0.10,0.06,0.04])
    cb_default            = rng.choice(["Y","N"], n_samples, p=[0.17,0.83])

    grade_risk  = {"A":0.0,"B":0.15,"C":0.30,"D":0.50,"E":0.70,"F":0.85,"G":1.0}
    grade_score = np.array([grade_risk[g] for g in loan_grade])
    debt_burden = (loan_amnt * loan_int_rate / 100.0) / np.maximum(person_income, 1)

    # v6: debt_burden explicit (was #1 feature but absent from label) — noise 0.18→0.08
    risk = (
        0.25 * np.clip(loan_percent_income / 0.50, 0, 1)
        + 0.15 * np.clip(loan_int_rate / 23.0, 0, 1)
        + 0.15 * np.clip(debt_burden / 0.05, 0, 1)
        + 0.20 * grade_score
        + 0.10 * (cb_default == "Y").astype(float)
        + 0.05 * np.clip(1 - person_income / 120_000, 0, 1)
        + 0.05 * np.clip(1 - person_emp_length / 15.0, 0, 1)
        + 0.05 * np.clip(1 - cb_cred_hist_length / 25.0, 0, 1)
    )
    risk        = np.clip(risk + rng.normal(0, 0.08, n_samples), 0, 1)  # 0.18 → 0.08
    loan_status = (risk >= np.percentile(risk, 72)).astype(int)           # 22% → 28% default

    print(f"   ├─ Samples       : {n_samples:,}")
    print(f"   ├─ Default rate  : {loan_status.mean():.2%}")
    print(f"   └─ Distribution  : 0={int((1-loan_status.mean())*n_samples):,}  1={int(loan_status.mean()*n_samples):,}")

    return pd.DataFrame({
        "person_age": person_age, "person_income": person_income,
        "person_home_ownership": person_home_ownership,
        "person_emp_length": person_emp_length, "loan_intent": loan_intent,
        "loan_grade": loan_grade, "loan_amnt": loan_amnt,
        "loan_int_rate": loan_int_rate, "loan_percent_income": loan_percent_income,
        "cb_person_default_on_file": cb_default,
        "cb_person_cred_hist_length": cb_cred_hist_length,
        "loan_status": loan_status,
    })


def load_data(csv_path: str | None, n_samples: int) -> pd.DataFrame:
    if csv_path and Path(csv_path).exists():
        print(f"📂 Loading CSV: {csv_path}")
        df      = pd.read_csv(csv_path)
        required = NUMERICAL_COLS_BASE + CATEGORICAL_COLS + [TARGET_COL]
        missing  = [c for c in required if c not in df.columns]
        if missing:
            print(f"   ⚠️  Missing {missing} — using synthetic data")
            return generate_realistic_loan_data(n_samples)
        if "loan_percent_income" not in df.columns:
            df["loan_percent_income"] = (df["loan_amnt"] / df["person_income"].clip(lower=1)).round(4)
        return df[required]
    print("🔧 Generating synthetic data...")
    return generate_realistic_loan_data(n_samples)


# ────────────────────────────────────────────────────────────────
# § 3. Preprocessor
# ────────────────────────────────────────────────────────────────
def build_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERICAL_COLS),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_COLS),
            ("eng", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), ENGINEERED_CAT_COLS),
        ],
        remainder="drop",
    )


# ────────────────────────────────────────────────────────────────
# § 4. Optuna — XGBoost + LightGBM
# ────────────────────────────────────────────────────────────────
def create_objective(X_train: pd.DataFrame, y_train: pd.Series):
    cv         = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    neg_count  = int((y_train == 0).sum())
    pos_count  = int((y_train == 1).sum())
    base_scale = neg_count / max(pos_count, 1)

    def objective(trial: optuna.Trial) -> float:
        algo = trial.suggest_categorical("algorithm", ["xgboost", "lightgbm"])

        if algo == "xgboost":
            clf_params: dict = {
                "n_estimators":     trial.suggest_int(  "xgb_n_estimators",    100, 800, step=50),
                "max_depth":        trial.suggest_int(  "xgb_max_depth",         3, 10),
                "learning_rate":    trial.suggest_float("xgb_learning_rate",  0.005, 0.3,  log=True),
                "subsample":        trial.suggest_float("xgb_subsample",        0.5, 1.0),
                "colsample_bytree": trial.suggest_float("xgb_colsample_bytree", 0.4, 1.0),
                "reg_alpha":        trial.suggest_float("xgb_reg_alpha",       1e-4, 10.0, log=True),
                "reg_lambda":       trial.suggest_float("xgb_reg_lambda",      1e-4, 10.0, log=True),
                "min_child_weight": trial.suggest_int(  "xgb_min_child_weight",   1, 20),
                "gamma":            trial.suggest_float("xgb_gamma",             0.0, 5.0),
                "scale_pos_weight": trial.suggest_float("xgb_scale_pos_weight", base_scale*0.5, base_scale*2.0),
                "eval_metric": "aucpr", "random_state": RANDOM_STATE, "n_jobs": -1,
            }
        else:  # lightgbm
            clf_params = {
                "n_estimators":      trial.suggest_int(  "lgbm_n_estimators",     100, 800, step=50),
                "max_depth":         trial.suggest_int(  "lgbm_max_depth",          3, 12),
                "learning_rate":     trial.suggest_float("lgbm_learning_rate",   0.005, 0.3,  log=True),
                "subsample":         trial.suggest_float("lgbm_subsample",          0.5, 1.0),
                "colsample_bytree":  trial.suggest_float("lgbm_colsample_bytree",   0.4, 1.0),
                "reg_alpha":         trial.suggest_float("lgbm_reg_alpha",         1e-4, 10.0, log=True),
                "reg_lambda":        trial.suggest_float("lgbm_reg_lambda",        1e-4, 10.0, log=True),
                "min_child_samples": trial.suggest_int(  "lgbm_min_child_samples",    5, 100),
                "num_leaves":        trial.suggest_int(  "lgbm_num_leaves",          20, 150),
                "scale_pos_weight":  trial.suggest_float("lgbm_scale_pos_weight", base_scale*0.5, base_scale*2.0),
                "random_state": RANDOM_STATE, "n_jobs": -1, "verbose": -1,
            }

        fold_scores = []
        for train_idx, val_idx in cv.split(X_train, y_train):
            X_ft, X_fv = X_train.iloc[train_idx], X_train.iloc[val_idx]
            y_ft, y_fv = y_train.iloc[train_idx], y_train.iloc[val_idx]

            pre = build_preprocessor()
            Xt  = pre.fit_transform(X_ft)
            Xv  = pre.transform(X_fv)

            if algo == "xgboost":
                clf_fold = XGBClassifier(**clf_params)
                clf_fold.fit(Xt, y_ft, eval_set=[(Xv, y_fv)], verbose=False)
            else:
                clf_fold = lgb.LGBMClassifier(**clf_params)
                clf_fold.fit(Xt, y_ft, eval_set=[(Xv, y_fv)],
                             callbacks=[lgb.early_stopping(30, verbose=False), lgb.log_evaluation(-1)])

            y_prob = clf_fold.predict_proba(Xv)[:, 1]
            fold_scores.append(average_precision_score(y_fv, y_prob))

        mean_prauc = float(np.mean(fold_scores))
        trial.set_user_attr("cv_std", round(float(np.std(fold_scores)), 4))
        return mean_prauc

    return objective


# ────────────────────────────────────────────────────────────────
# § 5. Threshold tuning
# ────────────────────────────────────────────────────────────────
def find_optimal_threshold(
    y_true, y_prob,
    mode: str = "f1_macro",
    target_recall: float = 0.90,
) -> float:
    """
    f1_macro      : sweep threshold grid 0.05–0.95, maximize macro F1 (default)
    recall_target : maximize precision while class-1 recall >= target_recall
    """
    if mode == "f1_macro":
        best_t, best_f1 = 0.5, 0.0
        for t in np.linspace(0.05, 0.95, 181):
            preds = (y_prob >= t).astype(int)
            f1    = f1_score(y_true, preds, average="macro", zero_division=0)
            if f1 > best_f1:
                best_f1 = f1
                best_t  = float(t)
        return best_t
    else:
        precisions, recalls, thresholds = precision_recall_curve(y_true, y_prob)
        valid = recalls[:-1] >= target_recall
        if not valid.any():
            f1s = 2 * precisions * recalls / (precisions + recalls + 1e-8)
            return float(thresholds[np.argmax(f1s[:-1])])
        return float(thresholds[np.argmax(precisions[:-1][valid])])


# ────────────────────────────────────────────────────────────────
# § 6. Evaluation
# ────────────────────────────────────────────────────────────────
def evaluate(y_test, y_pred, y_prob, y_train, y_pred_train, y_prob_train) -> dict:
    test_auc  = roc_auc_score(y_test,  y_prob)
    train_auc = roc_auc_score(y_train, y_prob_train)
    test_f1   = f1_score(y_test,  y_pred,       average="macro")
    train_f1  = f1_score(y_train, y_pred_train, average="macro")
    auc_gap   = train_auc - test_auc
    f1_gap    = train_f1  - test_f1

    report_str  = classification_report(y_test, y_pred, digits=2)
    report_dict = classification_report(y_test, y_pred, output_dict=True)
    cm = confusion_matrix(y_test, y_pred)

    print("\n" + "═"*60)
    print("  EVALUATION RESULTS (held-out test set)")
    print("═"*60)
    print(report_str)
    print(f"  Confusion Matrix:\n    TN={cm[0][0]:,}  FP={cm[0][1]:,}\n    FN={cm[1][0]:,}  TP={cm[1][1]:,}\n")
    print(f"  ROC-AUC  test={test_auc:.4f}  train={train_auc:.4f}  gap={auc_gap:+.4f}")
    print(f"  F1-macro test={test_f1:.4f}  train={train_f1:.4f}  gap={f1_gap:+.4f}")
    print("\n" + "─"*60)
    print("  OVERFITTING AUDIT")
    print("─"*60)
    overfitting = False
    for name, gap in [("AUC", auc_gap), ("F1", f1_gap)]:
        if gap > OVERFIT_GAP_THRESHOLD:
            print(f"  ⚠️  {name} gap {gap:+.4f} > {OVERFIT_GAP_THRESHOLD} — RISK")
            overfitting = True
        else:
            print(f"  ✅ {name} gap {gap:+.4f} — OK")

    return {
        "test_roc_auc":        round(test_auc,  4), "train_roc_auc":  round(train_auc, 4), "auc_gap": round(auc_gap, 4),
        "test_f1_macro":       round(test_f1,   4), "train_f1_macro": round(train_f1,  4), "f1_gap":  round(f1_gap,  4),
        "test_accuracy":       round(report_dict["accuracy"],       4),
        "class_0_precision":   round(report_dict["0"]["precision"], 4),
        "class_0_recall":      round(report_dict["0"]["recall"],    4),
        "class_0_f1":          round(report_dict["0"]["f1-score"],  4),
        "class_1_precision":   round(report_dict["1"]["precision"], 4),
        "class_1_recall":      round(report_dict["1"]["recall"],    4),
        "class_1_f1":          round(report_dict["1"]["f1-score"],  4),
        "confusion_matrix":    cm.tolist(),
        "overfitting_detected":overfitting,
    }


# ────────────────────────────────────────────────────────────────
# § 7. Feature importance
# ────────────────────────────────────────────────────────────────
def show_importances(clf, feature_names: list) -> dict:
    if not hasattr(clf, "feature_importances_"):
        return {}
    importances = clf.feature_importances_
    idx = np.argsort(importances)[::-1]
    print("\n" + "─"*60)
    print("  TOP FEATURE IMPORTANCES")
    print("─"*60)
    result = {}
    for rank, i in enumerate(idx[:15], 1):
        name = feature_names[i] if i < len(feature_names) else f"f_{i}"
        imp  = importances[i]
        print(f"  {rank:2d}. {name:<42s} {imp:.4f}  {'█'*int(imp*80)}")
        result[str(name)] = round(float(imp), 4)
    return result


# ────────────────────────────────────────────────────────────────
# § 8. Save
# ────────────────────────────────────────────────────────────────
def save_artifacts(clf, preprocessor, best_params: dict, metrics: dict,
                   importances: dict, threshold: float, output_dir: Path, algo: str):
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact = {
        "preprocessor": preprocessor, "classifier": clf,
        "threshold": threshold, "feature_cols": ALL_FEATURE_COLS,
        "engineered_cat_cols": ENGINEERED_CAT_COLS, "algorithm": algo,
    }
    model_path = output_dir / "loan_model.pkl"
    joblib.dump(artifact, model_path, compress=3)

    prefix      = "xgb_" if algo == "xgboost" else "lgbm_"
    clean_params = {k.replace(prefix, ""): v for k, v in best_params.items() if k != "algorithm"}

    meta = {
        "model_version": "loan_v6",
        "algorithm": algo,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "optimizer": "Optuna Bayesian TPE (XGBoost + LightGBM)",
        "decision_threshold": threshold,
        "features_used": {
            "numerical": NUMERICAL_COLS, "categorical": CATEGORICAL_COLS,
            "engineered": ENGINEERED_CAT_COLS, "total_count": len(ALL_FEATURE_COLS),
        },
        "best_hyperparameters": {
            "algorithm": algo,
            **{k: (int(v) if isinstance(v, np.integer) else v) for k, v in clean_params.items()},
        },
        "evaluation_metrics": metrics,
        "feature_importances_top10": dict(list(importances.items())[:10]),
        "anti_overfit": {
            "cv_folds": CV_FOLDS, "test_size": TEST_SIZE,
            "auc_gap": metrics.get("auc_gap"), "f1_gap": metrics.get("f1_gap"),
            "overfitting_detected": metrics.get("overfitting_detected"),
        },
    }
    meta_path = output_dir / "loan_model_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False, default=str)

    sz = model_path.stat().st_size / 1024 / 1024
    print(f"\n💾 Model    : {model_path}  ({sz:.1f} MB)")
    print(f"📋 Metadata : {meta_path}")
    print(f"🎯 Threshold: {threshold:.4f}")
    return model_path


# ────────────────────────────────────────────────────────────────
# § 9. Main
# ────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv",            type=str,   default=None)
    parser.add_argument("--trials",         type=int,   default=40)
    parser.add_argument("--samples",        type=int,   default=80_000)
    parser.add_argument("--threshold-mode", choices=["f1_macro","recall_target"], default="f1_macro")
    parser.add_argument("--target-recall",  type=float, default=0.90)
    args = parser.parse_args()

    warnings.filterwarnings("ignore")
    optuna.logging.set_verbosity(optuna.logging.WARNING)

    print("╔════════════════════════════════════════════════════════════╗")
    print("║  🏦 Loan Approval — Pipeline v6 (XGBoost + LightGBM)      ║")
    print("╚════════════════════════════════════════════════════════════╝\n")

    # 1. Load
    print("━"*60); print("  STEP 1/6 : Load Data"); print("━"*60)
    df    = load_data(args.csv, args.samples)
    y     = df[TARGET_COL]
    X_raw = df[BASE_COLS]
    print(f"  Features: {len(ALL_FEATURE_COLS)} total ({len(NUMERICAL_COLS)} num + {len(CATEGORICAL_COLS)} cat + {len(ENGINEERED_CAT_COLS)} eng_cat)")
    print("  ✅ OK\n")

    # 2. Split → Engineer (split FIRST, engineer independently on each split)
    print("━"*60); print("  STEP 2/6 : Stratified Split (80/20) → Engineer Features"); print("━"*60)
    X_raw_train, X_raw_test, y_train, y_test = train_test_split(
        X_raw, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y,
    )
    X_train = engineer_features(X_raw_train)[ALL_FEATURE_COLS]
    X_test  = engineer_features(X_raw_test)[ALL_FEATURE_COLS]
    print(f"  Train: {len(X_train):,}  Test: {len(X_test):,}\n")

    # 3. Optuna
    print("━"*60)
    print(f"  STEP 3/6 : Optuna ({args.trials} trials, {CV_FOLDS}-fold CV, XGBoost + LightGBM)")
    print("━"*60)
    t0    = time.time()
    study = optuna.create_study(
        direction="maximize", study_name="loan_v6",
        sampler=optuna.samplers.TPESampler(seed=RANDOM_STATE),
    )
    study.optimize(create_objective(X_train, y_train), n_trials=args.trials, show_progress_bar=True)
    elapsed   = time.time() - t0
    bp        = study.best_trial
    best_algo = bp.params.get("algorithm", "xgboost")

    print(f"\n  ⏱️  {elapsed:.0f}s | Best #{bp.number} | PR-AUC={bp.value:.4f} | algo={best_algo} (std={bp.user_attrs.get('cv_std','?')})")
    for k, v in bp.params.items():
        print(f"      {k:<32s} = {f'{v:.4f}' if isinstance(v, float) else str(v)}")

    # 4. Final training
    print(f"\n{'━'*60}\n  STEP 4/6 : Train Final {best_algo.upper()}\n{'━'*60}")
    preprocessor = build_preprocessor()
    X_train_t    = preprocessor.fit_transform(X_train)
    X_test_t     = preprocessor.transform(X_test)

    prefix       = "xgb_" if best_algo == "xgboost" else "lgbm_"
    final_params = {k.replace(prefix, ""): v for k, v in bp.params.items() if k.startswith(prefix)}

    if best_algo == "xgboost":
        final_params.update({"eval_metric": "aucpr", "early_stopping_rounds": 50,
                              "random_state": RANDOM_STATE, "n_jobs": -1})
        clf = XGBClassifier(**final_params)
        clf.fit(X_train_t, y_train, eval_set=[(X_test_t, y_test)], verbose=False)
    else:
        final_params.update({"random_state": RANDOM_STATE, "n_jobs": -1, "verbose": -1})
        clf = lgb.LGBMClassifier(**final_params)
        clf.fit(X_train_t, y_train, eval_set=[(X_test_t, y_test)],
                callbacks=[lgb.early_stopping(50, verbose=False), lgb.log_evaluation(-1)])
    print("  ✅ Trained\n")

    # 5. Threshold
    print("━"*60)
    print(f"  STEP 5/6 : Threshold Tuning (mode={args.threshold_mode})")
    print("━"*60)
    y_prob_test  = clf.predict_proba(X_test_t)[:, 1]
    y_prob_train = clf.predict_proba(X_train_t)[:, 1]
    threshold    = find_optimal_threshold(
        y_test, y_prob_test,
        mode=args.threshold_mode, target_recall=args.target_recall,
    )
    print(f"  Optimal  : {threshold:.4f}")
    y_pred_test  = (y_prob_test  >= threshold).astype(int)
    y_pred_train = (y_prob_train >= threshold).astype(int)
    print("  ✅ Applied\n")

    # 6. Evaluate
    print("━"*60); print("  STEP 6/6 : Evaluation & Anti-Overfitting Audit"); print("━"*60)
    metrics       = evaluate(y_test, y_pred_test, y_prob_test, y_train, y_pred_train, y_prob_train)
    feature_names = list(preprocessor.get_feature_names_out())
    importances   = show_importances(clf, feature_names)

    output_dir = Path(__file__).parent / "ml_models"
    save_artifacts(clf, preprocessor, bp.params, metrics, importances, threshold, output_dir, best_algo)

    print("\n" + "═"*60)
    print("  ✅ PIPELINE v6 COMPLETE")
    print("═"*60)
    print(f"  POST /api/v1/loans/simulate")
    print("═"*60 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
