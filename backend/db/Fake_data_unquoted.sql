-- ============================================================
-- FAKE DATA (ERD v2 - UNQUOTED IDENTIFIERS)
-- Scope:
--   - Match schema in backend/db/ERD.sql (11 tables)
--   - Generate 100 sample rows for core business tables:
--       customers, transactions_live, loans, audit_logs
-- ============================================================

-- Optional cleanup for re-run (children -> parents)
DELETE FROM rule_hits;
DELETE FROM review_cases;
DELETE FROM audit_logs;
DELETE FROM loans;
DELETE FROM transactions_live;
DELETE FROM card_velocity_stats;
DELETE FROM model_configs;
DELETE FROM channels;
DELETE FROM merchants;
DELETE FROM customers;
DELETE FROM users;

-- ============================================================
-- 1) USERS
-- ============================================================
INSERT INTO users (user_id, username, password_hash, full_name, email, role, status, created_at) VALUES
('11111111-1111-1111-1111-111111111111', 'admin',     'hashed_admin',    'System Admin',       'admin@tms.local', 'ADMIN',    'ACTIVE', TO_TIMESTAMP('2026-01-01 08:00:00', 'YYYY-MM-DD HH24:MI:SS'));
INSERT INTO users (user_id, username, password_hash, full_name, email, role, status, created_at) VALUES
('22222222-2222-2222-2222-222222222222', 'operator1', 'hashed_operator', 'Nguyen Van Operator','op1@tms.local',   'OPERATOR', 'ACTIVE', TO_TIMESTAMP('2026-01-01 08:01:00', 'YYYY-MM-DD HH24:MI:SS'));
INSERT INTO users (user_id, username, password_hash, full_name, email, role, status, created_at) VALUES
('33333333-3333-3333-3333-333333333333', 'reviewer1', 'hashed_reviewer', 'Le Van Reviewer',    'rev1@tms.local',  'REVIEWER', 'ACTIVE', TO_TIMESTAMP('2026-01-01 08:02:00', 'YYYY-MM-DD HH24:MI:SS'));
INSERT INTO users (user_id, username, password_hash, full_name, email, role, status, created_at) VALUES
('44444444-4444-4444-4444-444444444444', 'manager1',  'hashed_manager',  'Pham Thi Manager',   'mgr1@tms.local',  'MANAGER',  'ACTIVE', TO_TIMESTAMP('2026-01-01 08:03:00', 'YYYY-MM-DD HH24:MI:SS'));
INSERT INTO users (user_id, username, password_hash, full_name, email, role, status, created_at) VALUES
('55555555-5555-5555-5555-555555555555', 'analyst1',  'hashed_analyst',  'Hoang Van Analyst',  'ana1@tms.local',  'ANALYST',  'ACTIVE', TO_TIMESTAMP('2026-01-01 08:04:00', 'YYYY-MM-DD HH24:MI:SS'));

-- ============================================================
-- 2) CHANNELS
-- ============================================================
INSERT INTO channels (channel_code, channel_name) VALUES ('POS', 'Point of Sale');
INSERT INTO channels (channel_code, channel_name) VALUES ('ATM', 'ATM');
INSERT INTO channels (channel_code, channel_name) VALUES ('ONLINE', 'Online Banking');
INSERT INTO channels (channel_code, channel_name) VALUES ('MOBILE_APP', 'Mobile App');

-- ============================================================
-- 3) CUSTOMERS (100 ROWS)
-- ============================================================
INSERT INTO customers (
  customer_id, customer_code, full_name, identity_card, date_of_birth, gender,
  address, city, job, latitude, longitude, income_level, kyc_status, created_at
)
SELECT
  'cust-' || LPAD(level, 4, '0') || '-0000-0000-000000' || LPAD(level, 6, '0'),
  'CUST' || LPAD(level, 6, '0'),
  'Khach hang ' || TO_CHAR(level),
  '001' || LPAD(level, 9, '0'),
  ADD_MONTHS(DATE '1980-01-01', MOD(level * 7, 360)),
  CASE MOD(level, 2) WHEN 0 THEN 'F' ELSE 'M' END,
  'So ' || TO_CHAR(level) || ', Ward ' || TO_CHAR(MOD(level, 30) + 1),
  CASE MOD(level, 3) WHEN 0 THEN 'Ho Chi Minh City' WHEN 1 THEN 'Hanoi' ELSE 'Da Nang' END,
  CASE MOD(level, 5) WHEN 0 THEN 'engineer' WHEN 1 THEN 'teacher' WHEN 2 THEN 'manager' WHEN 3 THEN 'accountant' ELSE 'developer' END,
  8 + MOD(level * 13, 1600) / 100,
  102 + MOD(level * 17, 700) / 100,
  CASE MOD(level, 3) WHEN 0 THEN 'LOW' WHEN 1 THEN 'MEDIUM' ELSE 'HIGH' END,
  CASE MOD(level, 4) WHEN 0 THEN 'PENDING' WHEN 1 THEN 'VERIFIED' WHEN 2 THEN 'VERIFIED' ELSE 'REJECTED' END,
  TO_TIMESTAMP('2026-01-01 09:00:00', 'YYYY-MM-DD HH24:MI:SS') + NUMTODSINTERVAL(level, 'MINUTE')
FROM dual
CONNECT BY level <= 100;

-- ============================================================
-- 4) MERCHANTS (20 ROWS)
-- ============================================================
INSERT INTO merchants (
  merchant_id, merchant_code, merchant_name, merchant_category, city, state, country,
  latitude, longitude, risk_level, is_blacklisted, created_at
)
SELECT
  'mcht-' || LPAD(level, 4, '0') || '-0000-0000-000000' || LPAD(level, 6, '0'),
  'MCHT' || LPAD(level, 6, '0'),
  'Merchant ' || TO_CHAR(level),
  CASE MOD(level, 5)
    WHEN 0 THEN 'grocery_pos'
    WHEN 1 THEN 'shopping_net'
    WHEN 2 THEN 'entertainment'
    WHEN 3 THEN 'misc_net'
    ELSE 'food_dining'
  END,
  CASE MOD(level, 3) WHEN 0 THEN 'Ho Chi Minh City' WHEN 1 THEN 'Hanoi' ELSE 'Da Nang' END,
  CASE MOD(level, 3) WHEN 0 THEN 'HCM' WHEN 1 THEN 'HN' ELSE 'DN' END,
  'VN',
  8 + MOD(level * 29, 1600) / 100,
  102 + MOD(level * 23, 700) / 100,
  CASE MOD(level, 4) WHEN 0 THEN 'HIGH' WHEN 1 THEN 'LOW' WHEN 2 THEN 'MEDIUM' ELSE 'LOW' END,
  CASE WHEN MOD(level, 20) = 0 THEN 1 ELSE 0 END,
  TO_TIMESTAMP('2026-01-01 10:00:00', 'YYYY-MM-DD HH24:MI:SS') + NUMTODSINTERVAL(level, 'MINUTE')
FROM dual
CONNECT BY level <= 20;

-- ============================================================
-- 5) MODEL_CONFIGS
-- ============================================================
INSERT INTO model_configs (model_name, param_name, param_value, description, updated_by, version) VALUES
('fraud', 'reject_threshold', 0.650000, 'Auto reject threshold for fraud', '55555555-5555-5555-5555-555555555555', 1);
INSERT INTO model_configs (model_name, param_name, param_value, description, updated_by, version) VALUES
('fraud', 'review_threshold', 0.350000, 'Manual review threshold for fraud', '55555555-5555-5555-5555-555555555555', 1);
INSERT INTO model_configs (model_name, param_name, param_value, description, updated_by, version) VALUES
('loan', 'high_risk_threshold', 0.500000, 'High risk threshold for loan PD', '55555555-5555-5555-5555-555555555555', 1);
INSERT INTO model_configs (model_name, param_name, param_value, description, updated_by, version) VALUES
('loan', 'medium_risk_threshold', 0.200000, 'Medium risk threshold for loan PD', '55555555-5555-5555-5555-555555555555', 1);

-- ============================================================
-- 6) TRANSACTIONS_LIVE (100 ROWS)
-- ============================================================
INSERT INTO transactions_live (
  txn_id, customer_id, merchant_id, channel_id, submitted_by,
  card_number_masked, card_number_hash, amount, txn_time, status,
  fraud_score, model_version, created_at
)
SELECT
  'txn-' || LPAD(level, 4, '0') || '-0000-0000-000000' || LPAD(level, 6, '0'),
  'cust-' || LPAD(MOD(level - 1, 100) + 1, 4, '0') || '-0000-0000-000000' || LPAD(MOD(level - 1, 100) + 1, 6, '0'),
  'mcht-' || LPAD(MOD(level - 1, 20) + 1, 4, '0') || '-0000-0000-000000' || LPAD(MOD(level - 1, 20) + 1, 6, '0'),
  CASE MOD(level - 1, 4)
    WHEN 0 THEN (SELECT channel_id FROM channels WHERE channel_code = 'POS')
    WHEN 1 THEN (SELECT channel_id FROM channels WHERE channel_code = 'ATM')
    WHEN 2 THEN (SELECT channel_id FROM channels WHERE channel_code = 'ONLINE')
    ELSE (SELECT channel_id FROM channels WHERE channel_code = 'MOBILE_APP')
  END,
  '22222222-2222-2222-2222-222222222222',
  '4222********' || LPAD(MOD(level * 19, 10000), 4, '0'),
  RPAD(TO_CHAR(level, 'FM000000'), 64, '0'),
  ROUND(50 + MOD(level * 137, 900000) / 100, 2),
  TO_TIMESTAMP('2026-02-01 00:00:00', 'YYYY-MM-DD HH24:MI:SS') + NUMTODSINTERVAL(level * 15, 'MINUTE'),
  CASE MOD(level, 10)
    WHEN 0 THEN 'PENDING'
    WHEN 1 THEN 'APPROVED'
    WHEN 2 THEN 'APPROVED'
    WHEN 3 THEN 'APPROVED'
    WHEN 4 THEN 'APPROVED'
    WHEN 5 THEN 'REJECTED'
    WHEN 6 THEN 'MANUAL_REVIEW'
    WHEN 7 THEN 'MANUAL_REVIEW'
    WHEN 8 THEN 'APPROVED'
    ELSE 'REJECTED'
  END,
  ROUND(0.01 + MOD(level * 37, 95) / 100, 4),
  'rf_v3_regularized',
  TO_TIMESTAMP('2026-02-01 00:00:00', 'YYYY-MM-DD HH24:MI:SS') + NUMTODSINTERVAL(level * 15, 'MINUTE')
FROM dual
CONNECT BY level <= 100;

-- ============================================================
-- 7) REVIEW_CASES (AUTO-SCOPE FOR MANUAL_REVIEW TXNS)
-- ============================================================
INSERT INTO review_cases (
  case_id, txn_id, case_status, assigned_to, decision, decision_note, version, created_at, decided_at
)
SELECT
  'case-' || LPAD(ROW_NUMBER() OVER (ORDER BY txn_id), 4, '0') || '-0000-0000-000000' || LPAD(ROW_NUMBER() OVER (ORDER BY txn_id), 6, '0'),
  txn_id,
  CASE MOD(ROW_NUMBER() OVER (ORDER BY txn_id), 3)
    WHEN 0 THEN 'OPEN'
    WHEN 1 THEN 'ASSIGNED'
    ELSE 'CLOSED'
  END,
  '33333333-3333-3333-3333-333333333333',
  CASE WHEN MOD(ROW_NUMBER() OVER (ORDER BY txn_id), 3) = 2
       THEN CASE WHEN MOD(ROW_NUMBER() OVER (ORDER BY txn_id), 2) = 0 THEN 'APPROVE' ELSE 'REJECT' END
       ELSE NULL END,
  CASE WHEN MOD(ROW_NUMBER() OVER (ORDER BY txn_id), 3) = 2
       THEN 'Reviewed by reviewer1'
       ELSE NULL END,
  1,
  created_at + NUMTODSINTERVAL(10, 'MINUTE'),
  CASE WHEN MOD(ROW_NUMBER() OVER (ORDER BY txn_id), 3) = 2
       THEN created_at + NUMTODSINTERVAL(30, 'MINUTE')
       ELSE NULL END
FROM transactions_live
WHERE status = 'MANUAL_REVIEW';

-- ============================================================
-- 8) LOANS (100 ROWS)
-- ============================================================
INSERT INTO loans (
  loan_id, customer_id, submitted_by, reviewed_by, principal_amount, interest_rate, term_months,
  purpose, status, version, review_note, reviewed_at, monthly_payment, outstanding_balance,
  disbursed_at, maturity_date, person_age, person_income, person_home_ownership, person_emp_length,
  loan_grade, loan_intent, cb_person_default_on_file, cb_person_cred_hist_length,
  pd_score, risk_level, model_version, created_at
)
SELECT
  'loan-' || LPAD(level, 4, '0') || '-0000-0000-000000' || LPAD(level, 6, '0'),
  'cust-' || LPAD(MOD(level - 1, 100) + 1, 4, '0') || '-0000-0000-000000' || LPAD(MOD(level - 1, 100) + 1, 6, '0'),
  '22222222-2222-2222-2222-222222222222',
  CASE WHEN MOD(level, 6) IN (0, 1, 2, 3) THEN '33333333-3333-3333-3333-333333333333' ELSE NULL END,
  ROUND(5000 + MOD(level * 211, 400000) / 10, 2),
  ROUND(0.05 + MOD(level * 7, 20) / 100, 4),
  CASE MOD(level, 5) WHEN 0 THEN 12 WHEN 1 THEN 24 WHEN 2 THEN 36 WHEN 3 THEN 48 ELSE 60 END,
  'Loan purpose #' || TO_CHAR(level),
  CASE MOD(level, 6)
    WHEN 0 THEN 'APPROVED'
    WHEN 1 THEN 'REJECTED'
    WHEN 2 THEN 'DISBURSED'
    WHEN 3 THEN 'CLOSED'
    WHEN 4 THEN 'DEFAULTED'
    ELSE 'PENDING'
  END,
  1,
  CASE WHEN MOD(level, 6) = 5 THEN NULL ELSE 'Auto review note #' || TO_CHAR(level) END,
  CASE WHEN MOD(level, 6) = 5 THEN NULL
       ELSE TO_TIMESTAMP('2026-03-01 00:00:00', 'YYYY-MM-DD HH24:MI:SS') + NUMTODSINTERVAL(level * 40, 'MINUTE')
  END,
  CASE WHEN MOD(level, 6) = 5 THEN NULL ELSE ROUND((5000 + MOD(level * 211, 400000) / 10) / 24, 2) END,
  CASE WHEN MOD(level, 6) IN (2, 3, 4) THEN ROUND(1000 + MOD(level * 97, 200000) / 10, 2) ELSE NULL END,
  CASE WHEN MOD(level, 6) IN (2, 3, 4)
       THEN TO_TIMESTAMP('2026-03-01 00:00:00', 'YYYY-MM-DD HH24:MI:SS') + NUMTODSINTERVAL(level * 40, 'MINUTE')
       ELSE NULL END,
  CASE WHEN MOD(level, 6) IN (2, 3, 4)
       THEN DATE '2026-03-01' + MOD(level, 365)
       ELSE NULL END,
  21 + MOD(level, 40),
  ROUND(15000 + MOD(level * 1234, 500000), 2),
  CASE MOD(level, 4) WHEN 0 THEN 'RENT' WHEN 1 THEN 'MORTGAGE' WHEN 2 THEN 'OWN' ELSE 'OTHER' END,
  MOD(level, 20),
  CASE MOD(level, 7) WHEN 0 THEN 'A' WHEN 1 THEN 'B' WHEN 2 THEN 'C' WHEN 3 THEN 'D' WHEN 4 THEN 'E' WHEN 5 THEN 'F' ELSE 'G' END,
  CASE MOD(level, 6)
    WHEN 0 THEN 'PERSONAL'
    WHEN 1 THEN 'EDUCATION'
    WHEN 2 THEN 'MEDICAL'
    WHEN 3 THEN 'VENTURE'
    WHEN 4 THEN 'HOMEIMPROVEMENT'
    ELSE 'DEBTCONSOLIDATION'
  END,
  CASE MOD(level, 5) WHEN 0 THEN 'Y' ELSE 'N' END,
  MOD(level, 30) + 1,
  ROUND(0.02 + MOD(level * 19, 85) / 100, 4),
  CASE
    WHEN MOD(level * 19, 100) >= 50 THEN 'HIGH RISK'
    WHEN MOD(level * 19, 100) >= 20 THEN 'MEDIUM RISK'
    ELSE 'LOW RISK'
  END,
  'loan_v6',
  TO_TIMESTAMP('2026-03-01 00:00:00', 'YYYY-MM-DD HH24:MI:SS') + NUMTODSINTERVAL(level * 25, 'MINUTE')
FROM dual
CONNECT BY level <= 100;

-- ============================================================
-- 9) RULE_HITS (FOR FLAGGED TXNS)
-- ============================================================
INSERT INTO rule_hits (rule_hit_id, txn_id, rule_code, rule_name, hit_value, severity, created_at)
SELECT
  'rh-' || LPAD(ROW_NUMBER() OVER (ORDER BY txn_id), 6, '0') || '-0000-0000-000000000000',
  txn_id,
  CASE MOD(ROW_NUMBER() OVER (ORDER BY txn_id), 4)
    WHEN 0 THEN 'RULE_HIGH_AMOUNT'
    WHEN 1 THEN 'RULE_NEW_MERCHANT'
    WHEN 2 THEN 'RULE_ODD_HOUR'
    ELSE 'RULE_VELOCITY_SPIKE'
  END,
  'Auto-generated rule hit',
  TO_CHAR(ROUND(fraud_score, 4)),
  CASE
    WHEN fraud_score >= 0.75 THEN 'HIGH'
    WHEN fraud_score >= 0.40 THEN 'MEDIUM'
    ELSE 'LOW'
  END,
  created_at + NUMTODSINTERVAL(1, 'MINUTE')
FROM transactions_live
WHERE status IN ('MANUAL_REVIEW', 'REJECTED');

-- ============================================================
-- 10) CARD_VELOCITY_STATS (100 ROWS)
-- ============================================================
INSERT INTO card_velocity_stats (
  card_hash, avg_daily_txn, total_txn, avg_amt, std_amt, m2_amt, distinct_days, last_txn_date, last_updated
)
SELECT
  card_number_hash,
  ROUND(1 + MOD(ROW_NUMBER() OVER (ORDER BY txn_id), 7) * 0.75, 2),
  10 + MOD(ROW_NUMBER() OVER (ORDER BY txn_id) * 3, 400),
  ROUND(50 + MOD(ROW_NUMBER() OVER (ORDER BY txn_id) * 29, 7000), 2),
  ROUND(10 + MOD(ROW_NUMBER() OVER (ORDER BY txn_id) * 17, 1200), 2),
  ROUND(100 + MOD(ROW_NUMBER() OVER (ORDER BY txn_id) * 101, 50000), 4),
  1 + MOD(ROW_NUMBER() OVER (ORDER BY txn_id), 30),
  TO_CHAR(txn_time, 'YYYY-MM-DD'),
  created_at + NUMTODSINTERVAL(2, 'MINUTE')
FROM transactions_live;

-- ============================================================
-- 11) AUDIT_LOGS (100 ROWS)
-- ============================================================
INSERT INTO audit_logs (log_id, event_type, entity_type, entity_id, actor_user_id, actor_name, event_ts, detail_json)
SELECT
  'log-' || LPAD(level, 4, '0') || '-0000-0000-000000' || LPAD(level, 6, '0'),
  'TRANSACTION_SUBMITTED',
  'Transaction',
  'txn-' || LPAD(level, 4, '0') || '-0000-0000-000000' || LPAD(level, 6, '0'),
  '22222222-2222-2222-2222-222222222222',
  'Nguyen Van Operator',
  TO_TIMESTAMP('2026-02-01 00:00:00', 'YYYY-MM-DD HH24:MI:SS') + NUMTODSINTERVAL(level * 15 + 1, 'MINUTE'),
  '{"source":"fake_seed_v2","seq":' || TO_CHAR(level) || '}'
FROM dual
CONNECT BY level <= 100;

COMMIT;
