# Backend Changes Report — ERD v1 to v2 Migration

**Date:** 2026-05-03
**Author:** Senior Backend / DBA
**Scope:** Full backend realignment from ERD v1 (31 tables) to ERD v2 (11 tables), Oracle compatibility fixes, and runtime bug resolution.

---

## 1. Schema Migration (v1 → v2)

### 1.1 Dropped Entities (20 tables removed)

| Removed Table | Reason |
|---|---|
| `roles`, `user_roles` | Merged into `users.role` (single role per user per UC06.3) |
| `risk_scoring_results` | Merged into `transactions_live.fraud_score` + `model_version` |
| `review_case_actions` | Replaced by `audit_logs` (unified audit trail) |
| `txn_idempotency` | No longer required (simplified transaction flow) |
| `txn_state`, `txn_state_history` | Replaced by `audit_logs` + `TRG_AUDIT_TXN_STATUS` trigger |
| `suppression_rules` | Dropped (not in v2 UC scope) |
| `analyst_reports` | Dropped |
| `reconciliation_runs`, `reconciliation_items` | Dropped (no reconciliation UC in v2) |
| `datalake_snapshots`, `etl_logs` | Dropped (out of scope) |
| `dim_time`, `dim_customer`, `dim_merchant`, `dim_channel`, `dim_location`, `fact_transactions`, `fact_loans` | Dropped (star schema not in v2) |

### 1.2 Column Changes on Surviving Tables

| Table | Removed Columns | Added Columns |
|---|---|---|
| `users` | `is_active` | `role` (varchar 20), `status` (varchar 20, DEFAULT 'ACTIVE') |
| `customers` | `state`, `zip_code`, `city_population` | `address`, `identity_card` |
| `transactions_live` | `currency_code`, `source_ip`, `reason_code`, `override_reason`, `unix_time` | `fraud_score`, `model_version` (merged from `risk_scoring_results`) |
| `review_cases` | — | `decision` (APPROVE/REJECT), `decision_note`; `case_status` simplified to OPEN/ASSIGNED/CLOSED |
| `loans` | `currency_code` | `model_version` |

---

## 2. Oracle Compatibility Fixes

### 2.1 Identifier Casing (Critical)

**Problem:** ERD.sql used double-quoted lowercase identifiers (`"users"`, `"model_configs"`). Oracle stores quoted identifiers case-sensitively as lowercase. SQLAlchemy generates unquoted SQL, which Oracle uppercases (`FROM USERS`). Result: `ORA-00942: table or view does not exist` for any table whose uppercase name doesn't match the lowercase stored name.

**Diagnosis:** After running ERD.sql, `user_tables` showed lowercase names (`model_configs`). SQLAlchemy queries resolved to uppercase (`MODEL_CONFIGS`). Additionally, a previous `create_tables()` call from SQLAlchemy had created **duplicate uppercase tables** for some entities (USERS, CUSTOMERS, etc.) but failed on `MODEL_CONFIGS` due to constraint name collision — leaving a partial set of uppercase tables alongside the full set of lowercase tables. This caused inconsistent behavior: some tables worked (happened to have uppercase duplicates), others didn't.

**Fix:** Removed all double-quote wrapping from identifiers in ERD.sql via regex transformation. Oracle now stores all identifiers as UPPERCASE (its default for unquoted identifiers), matching SQLAlchemy's generated SQL.

**Files changed:** `db/ERD.sql`

### 2.2 Missing DEFAULT on `created_at` Columns

**Problem:** ERD.sql defined `created_at timestamp NOT NULL` without a DEFAULT clause. SQLAlchemy models declared `server_default=func.current_timestamp()`, which tells SQLAlchemy the server handles the default — but no server-side default existed. Result: `ORA-01400: cannot insert NULL into CREATED_AT`.

**Fix:** Added `DEFAULT SYSTIMESTAMP` to all `created_at` and `event_ts` columns across 8 tables in ERD.sql.

**Tables affected:** `users`, `customers`, `merchants`, `transactions_live`, `review_cases`, `loans`, `audit_logs`, `rule_hits`

### 2.3 Model Registration (`models/__init__.py`)

**Problem:** `__init__.py` was empty. When seed.py ran without `create_tables()`, SQLAlchemy had not imported all model classes. String-based relationship references like `"Transaction"` in `Merchant.transactions` resolved to `sqlalchemy.engine.base.Transaction` instead of `app.models.transaction.Transaction`. Result: `UnmappedClassError`.

**Fix:** Populated `models/__init__.py` with explicit imports of all 9 model classes, ensuring they register with SQLAlchemy's mapper before any query execution.

**File changed:** `app/models/__init__.py`

---

## 3. Runtime Bug Fixes

### 3.1 Duplicate ReviewCase Creation (ORA-00001)

**Problem:** When a transaction scored as `MANUAL_REVIEW`, two actors tried to insert into `review_cases` for the same `txn_id`:
1. Oracle trigger `TRG_AUTO_CREATE_CASE` (fires `AFTER INSERT ON transactions_live`)
2. Python code in `TransactionService.submit()` (lines 128-138)

Since `review_cases.txn_id` has a UNIQUE constraint, the second insert failed with `ORA-00001: unique constraint violated`. This caused ~70% of demo runner transactions to error out (all non-REJECTED ones).

**Fix:** Removed Python-side ReviewCase creation from `TransactionService.submit()`. The Oracle trigger is the sole owner of review case creation. Comment left in code explaining the delegation.

**File changed:** `app/services/transaction_service.py`

### 3.2 Enum Repr Leaking into API Response

**Problem:** `TransactionSubmitResponse.status` was typed as `TransactionStatus` (enum). Pydantic serialized this as `"TransactionStatus.REJECTED"` instead of `"REJECTED"`. The demo runner's `DemoEvent.result` field inherited the same issue via `str(result.status)`. Stats keys also broke: `TXN_TransactionStatus.REJECTED` instead of `TXN_REJECTED`.

**Fix:**
- Changed `TransactionSubmitResponse.status` type from `TransactionStatus` to `str`
- Demo runner already calls `str()` on the status, which now returns the plain string

**Files changed:** `app/schemas/transaction.py`, `app/services/demo_runner_service.py`

---

## 4. Python Backend File Change Summary

### Models (9 files)
| File | Change |
|---|---|
| `models/__init__.py` | New: registers all 9 model classes |
| `models/user.py` | Rewritten: inline `role` + `status`, backward-compat properties `roles`, `is_active` |
| `models/customer.py` | Removed `state`, `zip_code`, `city_population` |
| `models/transaction.py` | Removed `currency_code`, `source_ip`, `reason_code`, `override_reason`; added `fraud_score`, `model_version`; dropped `TxnState`, `TxnStateHistory`, `TxnIdempotency` classes |
| `models/loan.py` | Removed `currency_code`; added `model_version` |
| `models/scoring.py` | Dropped `RiskScoringResult` class |
| `models/analyst.py` | Dropped `SuppressionRule` class |
| `models/case.py` | Dropped `ReviewCaseAction` class; `case_status` enum simplified |
| `models/card_velocity.py` | No schema change |
| `models/merchant.py` | No schema change |

### Schemas (5 files)
| File | Change |
|---|---|
| `schemas/common.py` | `CaseStatus` → OPEN/ASSIGNED/CLOSED only; removed `CaseActionType` |
| `schemas/user.py` | `is_active` (bool) → `status` (str) |
| `schemas/transaction.py` | Removed `currency_code`, `source_ip`; `TransactionSubmitResponse.status` → `str` |
| `schemas/loan.py` | Removed `currency_code` from all schemas |
| `schemas/case.py` | Removed `CaseActionResponse`; removed `currency_code`/`source_ip` from summaries |

### Repositories (4 files)
| File | Change |
|---|---|
| `repositories/user_repo.py` | Removed `Role`/`UserRole` joins; filter on `User.role` directly |
| `repositories/transaction_repo.py` | Dropped idempotency + state methods |
| `repositories/analyst_repo.py` | Dropped `SuppressionRepository` |
| `repositories/case_repo.py` | Removed `ReviewCaseAction` joinedload; dropped `list_actions` |

### Services (6 files)
| File | Change |
|---|---|
| `services/user_service.py` | Direct `user.role`/`user.status` instead of join tables |
| `services/auth_service.py` | `user.status != "ACTIVE"` instead of `user.is_active` |
| `services/transaction_service.py` | Removed suppression rules, idempotency, `RiskScoringResult`, `TxnState`/`TxnStateHistory` creation; removed Python-side `ReviewCase` creation (delegated to Oracle trigger) |
| `services/case_service.py` | `case_status` → CLOSED on decision; removed `ReviewCaseAction` creation |
| `services/loan_service.py` | Removed `currency_code` |
| `services/demo_runner_service.py` | Removed `currency_code`/`source_ip`; fixed enum-to-string in DemoEvent |

### Routes (5 files)
| File | Change |
|---|---|
| `routes/users.py` | Direct `user.role`/`user.status` access |
| `routes/auth.py` | `user.role`/`user.status` instead of `.roles`/`.is_active` |
| `routes/transactions.py` | Removed `/{txn_id}/state-history` endpoint |
| `routes/cases.py` | Removed action-related fields and endpoints |
| `routes/reports.py` | Removed `currency_code`/`reason_code` from export |

### Database (2 files)
| File | Change |
|---|---|
| `db/ERD.sql` | Removed double-quoted identifiers; added `DEFAULT SYSTIMESTAMP` to timestamp columns |
| `db/drop_all.sql` | New: utility script to drop all objects and recreate from ERD.sql |

### Seed (1 file)
| File | Change |
|---|---|
| `seed.py` | Rewritten: direct `role`/`status` on User; removed v1 columns from customers/loans; removed `SuppressionRule`; kept `ModelConfig` defaults |

---

## 5. Database Reset Procedure

```bash
cd backend

# 1. Drop all and recreate (sqlplus)
sqlplus ADMIN/123456@localhost:1521/FREEPDB1 @db/drop_all.sql

# 2. Seed application data (Python)
python -c "
from app.models import *
from app.db.base import SessionLocal
from seed import seed
db = SessionLocal()
try: seed(db)
except: db.rollback(); raise
finally: db.close()
"
```

> **Note:** Do NOT call `create_tables()` when the database has already been initialized via ERD.sql. SQLAlchemy's `create_all` will attempt to create duplicate uppercase tables and fail on named constraint conflicts.

---

## 6. Verification Checklist

- [x] All 11 tables created as UPPERCASE in Oracle
- [x] 6 users, 4 channels, 3 customers, 4 merchants, 5 loans, 4 model configs seeded
- [x] Login works (`POST /api/v1/auth/login`)
- [x] Transaction submission works without `ORA-00001`
- [x] `MANUAL_REVIEW` transactions: ReviewCase created by Oracle trigger only
- [x] Demo runner: status displays as `REJECTED` not `TransactionStatus.REJECTED`
- [x] All Python model/schema/repo/service/route imports pass
