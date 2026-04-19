# API Summary – Transaction Management System

> **Base URL:** `https://api.tms.local/api/v1`

---

## CHANGELOG

| # | Old | New |
|---|---|---|
| 1 | `POST /loans/submit` | `POST /loans` |
| 2 | `GET /loans` – MANAGER, ADMIN only | OPERATOR, MANAGER, ADMIN (OPERATOR sees own only) |
| 3 | Missing `PATCH /loans/{loan_id}/decision` | Added – MANAGER, ADMIN approve/reject loans |
| 4 | Missing `POST /loans/simulate` | Added – AI simulation, no DB write |
| 5 | `GET /transactions/{txn_id}/states` | `GET /transactions/{txn_id}/state-history` |
| 6 | `POST /etl/trigger` | `POST /etl/run` |
| 7 | Missing `POST /auth/refresh` | Added – obtain new access token via refresh token |
| 8 | Missing SSE endpoints | Added `GET /stream/transactions` and `GET /stream/dashboard` |
| 9 | Transaction Submit – OPERATOR only | OPERATOR, MANAGER, ADMIN |
| 10 | Missing `GET /dashboard/fraud-trend` | Added – daily fraud trend, lookback up to 90 days |
| 11 | Missing `GET /audit-logs/entities/{entity_type}/{entity_id}` | Added – per-entity audit history |
| 12 | Missing `GET /audit-logs/{log_id}` | Added – single audit log detail |
| 13 | `GET /reports/transactions` – aggregated report only | Raw transaction list with CSV export support |
| 14 | `GET /reports/fraud` missing | Added – fraud aggregation by day with CSV export |
| 15 | Missing `POST /datalake/ingest` | Added – ingest external snapshot into Data Lake |
| 16 | `GET /datalake/structure` (non-existent path) | `GET /datalake/snapshots` |
| 17 | `GET /reconciliation/jobs` (non-existent path) | `GET /reconciliation/reports` |
| 18 | `GET /reconciliation/jobs/{job_id}` (non-existent path) | `GET /reconciliation/{run_id}` |
| 19 | Missing `PATCH /reconciliation/{run_id}/resolve` | Added – resolve all open discrepancies |
| 20 | Total 41 endpoints (claimed) | 47 endpoints (verified from code) |

---

## Health

| # | Method | Path | Roles | Description |
|---|---|---|---|---|
| 1 | `GET` | `/health` | Public | System health check – returns status, version, environment, checks (database, fraud_model) |

---

## Auth

| # | Method | Path | Roles | Description |
|---|---|---|---|---|
| 2 | `POST` | `/auth/login` | Public | Login – returns access_token, refresh_token, user info |
| 3 | `POST` | `/auth/logout` | Any authenticated | Logout – invalidate session |
| 4 | `GET` | `/auth/me` | Any authenticated | Get current user info (user_id, username, full_name, role, is_active) |
| 5 | `PATCH` | `/auth/change-password` | Any authenticated | Change own password (current_password, new_password min8, confirm_password) |
| 6 | `POST` | `/auth/refresh` | Public | Exchange refresh_token for new TokenResponse |

---

## Users

| # | Method | Path | Roles | Description |
|---|---|---|---|---|
| 7 | `GET` | `/users` | MANAGER, ADMIN | List users – query: role, is_active, page, limit |
| 8 | `GET` | `/users/{user_id}` | MANAGER, ADMIN | Get user detail |
| 9 | `POST` | `/users` | ADMIN | Create user (username min3, full_name min2, email, password min8, role) → 201 |
| 10 | `PATCH` | `/users/{user_id}/disable` | ADMIN | Disable account (SoD: cannot disable self → 403) |
| 11 | `PATCH` | `/users/{user_id}/enable` | ADMIN | Re-enable account |
| 12 | `PATCH` | `/users/{user_id}/role` | ADMIN | Change user role |

---

## Transactions

| # | Method | Path | Roles | Description |
|---|---|---|---|---|
| 13 | `POST` | `/transactions/submit` | OPERATOR, MANAGER, ADMIN | Submit transaction for fraud scoring → 201 (or 200 on idempotency hit). Body: card_number (raw 13–19 digits), customer_id, merchant_id, channel_id, amount, currency_code, txn_time, source_ip?, idempotency_key? |
| 14 | `GET` | `/transactions` | All roles | List transactions – query: status, customer_id, merchant_id, from_date, to_date, min_amount, max_amount, page, limit. OPERATOR sees own only. |
| 15 | `GET` | `/transactions/{txn_id}` | All roles | Get transaction detail (includes fraud_detail). OPERATOR: 403 if not own. |
| 16 | `GET` | `/transactions/{txn_id}/state-history` | All roles | List state transitions for a transaction. OPERATOR: 403 if not own. |

---

## Cases

| # | Method | Path | Roles | Description |
|---|---|---|---|---|
| 17 | `GET` | `/cases` | REVIEWER, MANAGER, ADMIN | List cases – query: case_status, assigned_to, page, limit. REVIEWER sees OPEN queue + own assigned; cannot filter by other reviewer → 403. |
| 18 | `GET` | `/cases/{case_id}` | REVIEWER, MANAGER, ADMIN | Get case detail (includes transaction summary and action history). REVIEWER: 403 if not assigned to self. |
| 19 | `POST` | `/cases/{case_id}/assign` | REVIEWER | Self-assign an OPEN case (atomic WHERE assigned_to IS NULL). 409 if already assigned. |
| 20 | `PATCH` | `/cases/{case_id}/decision` | REVIEWER, MANAGER, ADMIN | Decide case (APPROVE/REJECT). Body: decision, decision_note (min10/max2000), version. Case must be ASSIGNED → 409 if OPEN. REVIEWER: own cases only. Optimistic lock on version. |

---

## Loans

| # | Method | Path | Roles | Description |
|---|---|---|---|---|
| 21 | `POST` | `/loans` | OPERATOR, MANAGER, ADMIN | Create loan application → 201 PENDING. Body: customer_id, principal_amount, currency_code, interest_rate, term_months, purpose (required) + optional AI features for PD scoring. |
| 22 | `POST` | `/loans/simulate` | OPERATOR, MANAGER, ADMIN | Simulate PD scoring without saving to DB. All AI feature fields required. Returns pd_score, risk_level, top_risk_factors, model_version. |
| 23 | `GET` | `/loans` | OPERATOR, MANAGER, ADMIN | List loans – query: customer_id, status, page, limit. OPERATOR sees own only. |
| 24 | `GET` | `/loans/{loan_id}` | OPERATOR, MANAGER, ADMIN | Get loan detail. OPERATOR: 403 if not own. |
| 25 | `PATCH` | `/loans/{loan_id}/decision` | MANAGER, ADMIN | Approve or reject a loan. Body: decision, review_note, version. SoD: submitter cannot self-approve → 403. Optimistic lock on version. |

---

## Reconciliation

| # | Method | Path | Roles | Description |
|---|---|---|---|---|
| 26 | `POST` | `/reconciliation/run` | ADMIN | Trigger reconciliation run. Body: period_start, period_end, pending_timeout_minutes (default 120). Marks stale PENDING txns as PENDING_TIMEOUT. → 201 |
| 27 | `GET` | `/reconciliation/reports` | ADMIN | List reconciliation runs – query: status, page, limit. |
| 28 | `GET` | `/reconciliation/{run_id}` | ADMIN | Get reconciliation run detail including per-item discrepancy list. |
| 29 | `PATCH` | `/reconciliation/{run_id}/resolve` | ADMIN | Resolve all OPEN discrepancies in a COMPLETED run. Body: resolution_note (min5/max500). |

---

## ETL

| # | Method | Path | Roles | Description |
|---|---|---|---|---|
| 30 | `POST` | `/etl/run` | ADMIN | Trigger ETL job. Body: target_date, job_type (default "DAILY_SUMMARY"). Idempotent per (target_date, job_type). → 201 |
| 31 | `GET` | `/etl/logs` | ADMIN | List ETL jobs – query: job_type, status, page, limit. |

---

## Datalake

| # | Method | Path | Roles | Description |
|---|---|---|---|---|
| 32 | `POST` | `/datalake/ingest` | ADMIN | Ingest external data snapshot. Body: snapshot_date, source_label, records (1–10000 items). → 201 |
| 33 | `GET` | `/datalake/snapshots` | ADMIN | List datalake snapshots – query: snapshot_type, snapshot_date, status, page, limit. |

---

## Dashboard

| # | Method | Path | Roles | Description |
|---|---|---|---|---|
| 34 | `GET` | `/dashboard/summary` | MANAGER, ADMIN | Dashboard summary: transaction counts (total, approved, rejected, manual_review, pending, today, this_week), fraud stats, case queue, loan stats, as_of timestamp. |
| 35 | `GET` | `/dashboard/fraud-trend` | MANAGER, ADMIN | Daily fraud trend. Query: days (1–90, default 30). Returns per-day breakdown: total_txn, approved, rejected, manual_review, fraud_rate. |

---

## Audit Logs

| # | Method | Path | Roles | Description |
|---|---|---|---|---|
| 36 | `GET` | `/audit-logs` | MANAGER, ADMIN | List audit log events – query: event_type, entity_type, actor_user_id, from_date, to_date, page, limit. Sorted DESC. |
| 37 | `GET` | `/audit-logs/entities/{entity_type}/{entity_id}` | MANAGER, ADMIN | Full audit history for a specific entity. Query: page, limit (max 200). Sorted ASC. |
| 38 | `GET` | `/audit-logs/{log_id}` | MANAGER, ADMIN | Get single audit log entry with detail field. |

---

## Reports

| # | Method | Path | Roles | Description |
|---|---|---|---|---|
| 39 | `GET` | `/reports/transactions` | MANAGER, ADMIN | Export transaction list. Query: format (json/csv), status, from_date, to_date. Max 5000 rows. CSV returns text/csv with UTF-8 BOM. |
| 40 | `GET` | `/reports/fraud` | MANAGER, ADMIN | Export fraud aggregation by day. Query: format (json/csv), from_date, to_date. Columns: date, total_txn, approved, rejected, manual_review, pending, fraud_rate, avg_fraud_score. |

---

## SSE Stream

> Auth: Bearer token in Authorization header (not URL). No query-string token.

| # | Method | Path | Roles | Description |
|---|---|---|---|---|
| 41 | `GET` | `/stream/transactions` | Any authenticated | SSE live feed of new transactions. Polls DB every 2s (created_at >= last_checked). Emits: txn_id, status, fraud_score, amount, created_at. Sends `: ping` when idle. |
| 42 | `GET` | `/stream/dashboard` | Any authenticated | SSE live dashboard metrics. Polls DashboardService every 5s. Emits: total, fraud_rate, etc. |

---

## Quick Reference – Roles per Module

| Module | OPERATOR | REVIEWER | MANAGER | ADMIN |
|---|:---:|:---:|:---:|:---:|
| Health | ✓ | ✓ | ✓ | ✓ |
| Auth (all 5 endpoints) | ✓ | ✓ | ✓ | ✓ |
| User Management | – | – | Read only | Full |
| Transaction Submit | ✓ | – | ✓ | ✓ |
| Transaction List/Detail | Own only | ✓ | ✓ | ✓ |
| Transaction State-History | Own only | ✓ | ✓ | ✓ |
| Cases | – | Full | Read + Decide | Read + Decide |
| Loans – Create/Simulate | ✓ | – | ✓ | ✓ |
| Loans – List/Detail | Own only | – | ✓ | ✓ |
| Loans – Decision | – | – | ✓ (SoD) | ✓ (SoD) |
| Dashboard / Reports | – | – | ✓ | ✓ |
| Audit Logs | – | – | ✓ | ✓ |
| ETL / Datalake | – | – | – | ✓ |
| Reconciliation | – | – | – | ✓ |
| SSE Stream (transactions) | ✓ | ✓ | ✓ | ✓ |
| SSE Stream (dashboard) | ✓ | ✓ | ✓ | ✓ |
