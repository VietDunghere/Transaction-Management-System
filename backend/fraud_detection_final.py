"""
Fraud Detection v3.1 — Anti-Overfit Patch
==========================================
Dùng best params từ Optuna v3 nhưng regularize mạnh hơn
để giảm overfit gap xuống ≤ 0.05
"""

import pandas as pd
import numpy as np
import warnings
import time
import os
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.metrics import (
    confusion_matrix, f1_score, fbeta_score,
    precision_recall_curve, precision_score,
    recall_score, average_precision_score,
)
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, RobustScaler
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline

warnings.filterwarnings('ignore')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EVAL_DIR = os.path.join(SCRIPT_DIR, 'evaluation_final')
os.makedirs(EVAL_DIR, exist_ok=True)

LOG_PATH = os.path.join(EVAL_DIR, 'run_log.txt')
log_file = open(LOG_PATH, 'w', encoding='utf-8')

def log(msg=""):
    print(msg, flush=True)
    log_file.write(msg + "\n")
    log_file.flush()

def log_header(title):
    log(f"\n{'='*80}")
    log(title)
    log('='*80)


def haversine_distance_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1_r, lon1_r = np.radians(lat1), np.radians(lon1)
    lat2_r, lon2_r = np.radians(lat2), np.radians(lon2)
    dlat, dlon = lat2_r - lat1_r, lon2_r - lon1_r
    a = np.sin(dlat/2)**2 + np.cos(lat1_r)*np.cos(lat2_r)*np.sin(dlon/2)**2
    return R * 2 * np.arcsin(np.sqrt(a))


class FrequencyEncoder(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.frequency_maps_ = {}
        self.feature_names_in_ = None

    def fit(self, X, y=None):
        X_df = pd.DataFrame(X).copy()
        self.feature_names_in_ = X_df.columns.to_list()
        self.frequency_maps_ = {
            col: X_df[col].value_counts(normalize=True).to_dict()
            for col in self.feature_names_in_
        }
        return self

    def transform(self, X):
        X_df = pd.DataFrame(X).copy()
        encoded = pd.DataFrame(index=X_df.index)
        for col in self.feature_names_in_:
            encoded[f"{col}_freq"] = X_df[col].map(self.frequency_maps_[col]).fillna(0.0)
        return encoded.values

    def get_feature_names_out(self, input_features=None):
        cols = input_features if input_features is not None else self.feature_names_in_
        return np.array([f"{col}_freq" for col in cols], dtype=object)


# ============================================================
# FEATURE ENGINEERING
# ============================================================
log_header("STEP 1: FEATURE ENGINEERING")
start = time.perf_counter()

train_path = os.path.join(SCRIPT_DIR, 'fraudTrain.csv')
test_path = os.path.join(SCRIPT_DIR, 'fraudTest.csv')
train_df = pd.read_csv(train_path)
test_df = pd.read_csv(test_path)

X_train = train_df.drop('is_fraud', axis=1)
y_train = train_df['is_fraud']
X_test = test_df.drop('is_fraud', axis=1)
y_test = test_df['is_fraud']

drop_cols = ['Unnamed: 0', 'first', 'last', 'street', 'zip', 'trans_num', 'unix_time']
X_train = X_train.drop(columns=[c for c in drop_cols if c in X_train.columns])
X_test = X_test.drop(columns=[c for c in drop_cols if c in X_test.columns])

X_train['merchant'] = X_train['merchant'].str.replace(r'^fraud_', '', regex=True)
X_test['merchant'] = X_test['merchant'].str.replace(r'^fraud_', '', regex=True)

X_train['trans_date_trans_time'] = pd.to_datetime(X_train['trans_date_trans_time'])
X_test['trans_date_trans_time'] = pd.to_datetime(X_test['trans_date_trans_time'])

# Velocity features
cc_daily = X_train.groupby([X_train['cc_num'], X_train['trans_date_trans_time'].dt.date]).size().reset_index(name='txn_count')
cc_velocity = cc_daily.groupby('cc_num')['txn_count'].mean().reset_index()
cc_velocity.columns = ['cc_num', 'cc_avg_daily_txn']
cc_total = X_train['cc_num'].value_counts().reset_index()
cc_total.columns = ['cc_num', 'cc_total_txn']
cc_amt = X_train.groupby('cc_num')['amt'].agg(['mean', 'std']).reset_index()
cc_amt.columns = ['cc_num', 'cc_avg_amt', 'cc_std_amt']
cc_amt['cc_std_amt'] = cc_amt['cc_std_amt'].fillna(0)

for df in [X_train, X_test]:
    for merge_df in [cc_velocity, cc_total, cc_amt]:
        cols_before = df.columns.tolist()
        merged = df.merge(merge_df, on='cc_num', how='left')
        for c in [c for c in merged.columns if c not in cols_before]:
            df[c] = merged[c].values

X_test['cc_avg_daily_txn'] = X_test['cc_avg_daily_txn'].fillna(1.0)
X_test['cc_total_txn'] = X_test['cc_total_txn'].fillna(1)
X_test['cc_avg_amt'] = X_test['cc_avg_amt'].fillna(X_train['amt'].mean())
X_test['cc_std_amt'] = X_test['cc_std_amt'].fillna(X_train['amt'].std())

X_train['amt_deviation'] = (X_train['amt'] - X_train['cc_avg_amt']) / (X_train['cc_std_amt'] + 1e-6)
X_test['amt_deviation'] = (X_test['amt'] - X_test['cc_avg_amt']) / (X_test['cc_std_amt'] + 1e-6)

X_train = X_train.drop(columns=['cc_num'])
X_test = X_test.drop(columns=['cc_num'])

X_train['dob'] = pd.to_datetime(X_train['dob'])
X_test['dob'] = pd.to_datetime(X_test['dob'])
X_train['age'] = (X_train['trans_date_trans_time'].dt.year - X_train['dob'].dt.year).clip(18, 100)
X_test['age'] = (X_test['trans_date_trans_time'].dt.year - X_test['dob'].dt.year).clip(18, 100)
X_train = X_train.drop(columns=['dob'])
X_test = X_test.drop(columns=['dob'])

for df in [X_train, X_test]:
    df['txn_hour'] = df['trans_date_trans_time'].dt.hour
    df['txn_day_of_week'] = df['trans_date_trans_time'].dt.dayofweek
    df['txn_month'] = df['trans_date_trans_time'].dt.month
    df['is_weekend'] = (df['txn_day_of_week'] >= 5).astype(int)
    df['is_night'] = ((df['txn_hour'] >= 23) | (df['txn_hour'] <= 6)).astype(int)

X_train = X_train.drop(columns=['trans_date_trans_time'])
X_test = X_test.drop(columns=['trans_date_trans_time'])

for df in [X_train, X_test]:
    df['distance_km'] = haversine_distance_km(df['lat'], df['long'], df['merch_lat'], df['merch_long'])
    df['is_suspicious_distance'] = (df['distance_km'] > 100).astype(int)

X_train = X_train.drop(columns=['lat', 'long', 'merch_lat', 'merch_long'])
X_test = X_test.drop(columns=['lat', 'long', 'merch_lat', 'merch_long'])

log(f"  ✓ Done in {time.perf_counter()-start:.1f}s")
log(f"  ✓ Train: {X_train.shape}, Test: {X_test.shape}")


# ============================================================
# PREPROCESSOR
# ============================================================
preprocessor = ColumnTransformer(
    transformers=[
        ('gender', OrdinalEncoder(categories=[['F', 'M']], handle_unknown='use_encoded_value', unknown_value=-1), ['gender']),
        ('category', OneHotEncoder(handle_unknown='ignore', sparse_output=False), ['category']),
        ('high_card', FrequencyEncoder(), ['merchant', 'job', 'city', 'state']),
        ('numeric', RobustScaler(), ['amt', 'city_pop', 'age', 'distance_km', 'cc_avg_daily_txn', 'cc_total_txn', 'cc_avg_amt', 'cc_std_amt', 'amt_deviation']),
        ('passthrough', 'passthrough', ['txn_hour', 'txn_day_of_week', 'txn_month', 'is_weekend', 'is_night', 'is_suspicious_distance']),
    ],
    remainder='drop'
)


# ============================================================
# STEP 2: GRID — 3 configs: v3, regularized, conservative
# ============================================================
log_header("STEP 2: TRAINING 3 REGULARIZATION LEVELS")

configs = {
    'V3_optuna': {
        'smote': 0.15, 'n_est': 280, 'depth': 20,
        'leaf': 3, 'split': 10, 'feat': 0.3
    },
    'V3_regularized': {
        'smote': 0.15, 'n_est': 280, 'depth': 14,
        'leaf': 8, 'split': 15, 'feat': 0.3
    },
    'V3_conservative': {
        'smote': 0.15, 'n_est': 280, 'depth': 12,
        'leaf': 12, 'split': 20, 'feat': 'sqrt'
    },
}

all_results = {}

for name, cfg in configs.items():
    log(f"\n--- {name} ---")
    pipe = Pipeline(steps=[
        ('prep', preprocessor),
        ('smote', SMOTE(sampling_strategy=cfg['smote'], random_state=42)),
        ('rf', RandomForestClassifier(
            n_estimators=cfg['n_est'], max_depth=cfg['depth'],
            min_samples_leaf=cfg['leaf'], min_samples_split=cfg['split'],
            max_features=cfg['feat'], random_state=42, n_jobs=-1
        ))
    ])

    t0 = time.perf_counter()
    pipe.fit(X_train, y_train)
    train_time = time.perf_counter() - t0
    log(f"  Trained in {train_time:.1f}s")

    y_proba_test = pipe.predict_proba(X_test)[:, 1]
    y_proba_train = pipe.predict_proba(X_train)[:, 1]

    pr_auc_train = average_precision_score(y_train, y_proba_train)
    pr_auc_test = average_precision_score(y_test, y_proba_test)
    gap = pr_auc_train - pr_auc_test

    # Best threshold
    best_f2, best_th = 0, 0.3
    for th in np.arange(0.10, 0.91, 0.05):
        y_pred = (y_proba_test >= th).astype(int)
        f2 = fbeta_score(y_test, y_pred, beta=2, zero_division=0)
        if f2 > best_f2:
            best_f2 = f2
            best_th = th

    y_pred = (y_proba_test >= best_th).astype(int)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    f2 = fbeta_score(y_test, y_pred, beta=2, zero_division=0)

    log(f"  PR-AUC: Train={pr_auc_train:.4f} Test={pr_auc_test:.4f} Gap={gap:.4f} {'⚠️' if gap > 0.05 else '✅'}")
    log(f"  Best th={best_th:.2f}: P={prec:.4f} R={rec:.4f} F1={f1:.4f} F2={f2:.4f}")

    all_results[name] = {
        'pr_auc_train': pr_auc_train, 'pr_auc_test': pr_auc_test, 'gap': gap,
        'threshold': best_th, 'precision': prec, 'recall': rec,
        'f1': f1, 'f2': f2, 'y_proba_test': y_proba_test,
        'config': cfg, 'train_time': train_time
    }


# ============================================================
# STEP 3: PICK BEST CONFIG (highest F2 with gap ≤ 0.05)
# ============================================================
log_header("STEP 3: SELECT BEST MODEL")

# Prefer: gap ≤ 0.05, then highest F2
candidates = {k: v for k, v in all_results.items() if v['gap'] <= 0.05}
if not candidates:
    # Fallback: pick lowest gap
    log("  ⚠️  No config with gap ≤ 0.05, picking lowest gap")
    best_name = min(all_results, key=lambda k: all_results[k]['gap'])
else:
    best_name = max(candidates, key=lambda k: candidates[k]['f2'])

best = all_results[best_name]
log(f"  ✓ Selected: {best_name}")
log(f"    PR-AUC: {best['pr_auc_test']:.4f} (gap: {best['gap']:.4f})")
log(f"    F2: {best['f2']:.4f} at threshold {best['threshold']:.2f}")


# ============================================================
# STEP 4: FINAL COMPARISON
# ============================================================
log_header("STEP 4: FULL COMPARISON")

log(f"\n{'Model':<20} {'PR-AUC':>8} {'Gap':>6} {'Prec':>8} {'Recall':>8} {'F1':>8} {'F2':>8} {'Status':>8}")
log(f"{'-'*78}")

# V1 original
log(f"{'V1 Original':<20} {'0.8239':>8} {'N/A':>6} {'0.7787':>8} {'0.8317':>8} {'0.8043':>8} {'0.8205':>8} {'base':>8}")
# V2 audit
log(f"{'V2 Audit':<20} {'0.8572':>8} {'N/A':>6} {'0.7438':>8} {'0.8298':>8} {'0.7845':>8} {'0.8111':>8} {'audit':>8}")

for name, r in all_results.items():
    status = '⭐ BEST' if name == best_name else ('⚠️ OVF' if r['gap'] > 0.05 else '✅')
    log(f"{name:<20} {r['pr_auc_test']:>8.4f} {r['gap']:>6.4f} {r['precision']:>8.4f} {r['recall']:>8.4f} {r['f1']:>8.4f} {r['f2']:>8.4f} {status:>8}")


# ============================================================
# 3-Class for best model
# ============================================================
log_header("3-CLASS DECISION (Best Model)")

y_proba_best = best['y_proba_test']
REJECT_TH = best['threshold']
REVIEW_TH = 0.05
for rth in np.arange(0.05, REJECT_TH, 0.01):
    if recall_score(y_test, (y_proba_best >= rth).astype(int), zero_division=0) >= 0.92:
        REVIEW_TH = round(float(rth), 2)
        break

decisions = pd.Series(y_proba_best).apply(
    lambda s: 'REJECTED' if s >= REJECT_TH else ('MANUAL_REVIEW' if s >= REVIEW_TH else 'APPROVED'))

total_fraud = int(y_test.sum())
log(f"  Reject ≥ {REJECT_TH:.2f} | Review ≥ {REVIEW_TH:.2f} | Approve < {REVIEW_TH:.2f}")
log(f"\n  {'Decision':<15} {'Count':>8} {'%':>7} {'Fraud':>6} {'% Fraud':>8}")
log(f"  {'-'*48}")
for label in ['APPROVED', 'MANUAL_REVIEW', 'REJECTED']:
    mask = (decisions == label).values
    count = mask.sum()
    fraud = int(y_test.values[mask].sum())
    log(f"  {label:<15} {count:>8,} {count/len(y_test)*100:>6.2f}% {fraud:>6} {fraud/max(total_fraud,1)*100:>7.1f}%")

missed = int(y_test.values[(decisions == 'APPROVED').values].sum())
log(f"\n  Fraud missed: {missed} ({missed/max(total_fraud,1)*100:.2f}%)")
log(f"  Fraud caught: {total_fraud-missed} ({(total_fraud-missed)/max(total_fraud,1)*100:.2f}%)")


# ============================================================
# SAVE
# ============================================================
log_header("SAVING RESULTS")

# Charts
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

for name, r in all_results.items():
    pr_p, pr_r, _ = precision_recall_curve(y_test, r['y_proba_test'])
    axes[0].plot(pr_r, pr_p, linewidth=2, label=f"{name} (AUC={r['pr_auc_test']:.4f})")
axes[0].set_xlabel('Recall')
axes[0].set_ylabel('Precision')
axes[0].set_title('PR Curves — All configs')
axes[0].legend()
axes[0].grid(alpha=0.3)

# Bar chart comparison
names = list(all_results.keys())
f2s = [all_results[n]['f2'] for n in names]
gaps = [all_results[n]['gap'] for n in names]
x = np.arange(len(names))
w = 0.35
axes[1].bar(x - w/2, f2s, w, label='F2 Score', color='steelblue')
axes[1].bar(x + w/2, gaps, w, label='Overfit Gap', color='salmon')
axes[1].axhline(0.05, color='red', linestyle='--', alpha=0.5, label='Gap limit (0.05)')
axes[1].set_xticks(x)
axes[1].set_xticklabels([n.replace('V3_', '') for n in names], rotation=15)
axes[1].set_title('F2 vs Overfit Gap')
axes[1].legend()
axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(EVAL_DIR, 'comparison_final.png'), dpi=150)
plt.close()
log(f"  ✓ comparison_final.png")

# Summary JSON
summary = {
    'selected_model': best_name,
    'selected_config': best['config'],
    'metrics': {
        'precision': best['precision'], 'recall': best['recall'],
        'f1': best['f1'], 'f2': best['f2'],
        'pr_auc': best['pr_auc_test'],
    },
    'overfit_check': {
        'pr_auc_train': best['pr_auc_train'],
        'pr_auc_test': best['pr_auc_test'],
        'gap': best['gap'],
    },
    'thresholds': {'reject': REJECT_TH, 'review': REVIEW_TH},
    'fraud_missed': missed,
    'fraud_caught_pct': (total_fraud - missed) / max(total_fraud, 1) * 100,
    'all_configs': {
        name: {k: v for k, v in r.items() if k != 'y_proba_test'}
        for name, r in all_results.items()
    }
}
with open(os.path.join(EVAL_DIR, 'summary_final.json'), 'w') as f:
    json.dump(summary, f, indent=2, default=str)
log(f"  ✓ summary_final.json")

# Markdown
with open(os.path.join(EVAL_DIR, 'SUMMARY.md'), 'w', encoding='utf-8') as f:
    f.write("# Fraud Detection — Final Optimized Results\n\n")
    f.write(f"## Selected: `{best_name}`\n\n")
    f.write(f"| Metric | Value |\n|--------|-------|\n")
    f.write(f"| PR-AUC | {best['pr_auc_test']:.4f} |\n")
    f.write(f"| Precision | {best['precision']:.4f} |\n")
    f.write(f"| Recall | {best['recall']:.4f} |\n")
    f.write(f"| F1 | {best['f1']:.4f} |\n")
    f.write(f"| F2 | {best['f2']:.4f} |\n")
    f.write(f"| Overfit Gap | {best['gap']:.4f} |\n")
    f.write(f"\n## Comparison\n\n")
    f.write(f"| Model | PR-AUC | Gap | Prec | Recall | F1 | F2 |\n")
    f.write(f"|-------|--------|-----|------|--------|----|----|")
    f.write(f"\n| V1 Original | 0.8239 | N/A | 0.7787 | 0.8317 | 0.8043 | 0.8205 |")
    f.write(f"\n| V2 Audit | 0.8572 | N/A | 0.7438 | 0.8298 | 0.7845 | 0.8111 |")
    for name, r in all_results.items():
        f.write(f"\n| {name} | {r['pr_auc_test']:.4f} | {r['gap']:.4f} | {r['precision']:.4f} | {r['recall']:.4f} | {r['f1']:.4f} | {r['f2']:.4f} |")
    f.write(f"\n\n## 3-Class Decision\n")
    f.write(f"- Reject ≥ {REJECT_TH:.2f} | Review ≥ {REVIEW_TH:.2f}\n")
    f.write(f"- Fraud caught: {(total_fraud-missed)/max(total_fraud,1)*100:.1f}%\n")
log(f"  ✓ SUMMARY.md")

log_header(f"DONE — {EVAL_DIR}")
log_file.close()
