-- ============================================================================
-- TMS seed data  (docs/plan.md section 5)
-- Run AFTER db/schema.sql.
--
-- PASSWORD SCHEME:
--   util/PasswordUtil.hashPassword(plain) = SHA-256(UTF-8(plain)) as lowercase
--   hex (String.format("%02x")). No salt. verifyPassword compares hex strings.
--
--   Seed plaintext password for ALL users:  Password@123
--   SHA-256 hex hash:
--     ff7bd97b1a7789ddd2775122fd6817f3173672da9f802ceec57f284325bf589f
--
-- Realistic Vietnam city coordinates used for customers/merchants.
-- UUIDs are literal strings.
-- ============================================================================

USE tms_local;

SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE rule_hits;
TRUNCATE TABLE card_velocity_stats;
TRUNCATE TABLE audit_logs;
TRUNCATE TABLE model_configs;
TRUNCATE TABLE loans;
TRUNCATE TABLE review_cases;
TRUNCATE TABLE transactions_live;
TRUNCATE TABLE channels;
TRUNCATE TABLE merchants;
TRUNCATE TABLE customers;
TRUNCATE TABLE users;
SET FOREIGN_KEY_CHECKS = 1;

-- ----------------------------------------------------------------------------
-- users : one ACTIVE user per role. Password = Password@123
-- ----------------------------------------------------------------------------
INSERT INTO users (user_id, username, password_hash, full_name, email, role, status, is_first_login) VALUES
('u0000001-0000-0000-0000-000000000001', 'admin',    'ff7bd97b1a7789ddd2775122fd6817f3173672da9f802ceec57f284325bf589f', 'System Admin',   'admin@tms.local',    'ADMIN',    'ACTIVE', 0),
('u0000002-0000-0000-0000-000000000002', 'manager',  'ff7bd97b1a7789ddd2775122fd6817f3173672da9f802ceec57f284325bf589f', 'Risk Manager',   'manager@tms.local',  'MANAGER',  'ACTIVE', 0),
('u0000003-0000-0000-0000-000000000003', 'analyst',  'ff7bd97b1a7789ddd2775122fd6817f3173672da9f802ceec57f284325bf589f', 'Fraud Analyst',  'analyst@tms.local',  'ANALYST',  'ACTIVE', 0),
('u0000004-0000-0000-0000-000000000004', 'reviewer', 'ff7bd97b1a7789ddd2775122fd6817f3173672da9f802ceec57f284325bf589f', 'Case Reviewer',  'reviewer@tms.local', 'REVIEWER', 'ACTIVE', 0),
('u0000005-0000-0000-0000-000000000005', 'operator', 'ff7bd97b1a7789ddd2775122fd6817f3173672da9f802ceec57f284325bf589f', 'Branch Operator','operator@tms.local', 'OPERATOR', 'ACTIVE', 0);

-- ----------------------------------------------------------------------------
-- channels (4)
-- ----------------------------------------------------------------------------
INSERT INTO channels (channel_code, channel_name) VALUES
('POS',    'Point of Sale'),
('ECOM',   'E-Commerce'),
('ATM',    'ATM Withdrawal'),
('MOBILE', 'Mobile Banking');

-- ----------------------------------------------------------------------------
-- customers (10) - fully populated for fraud scoring
-- gender, job, city, state, date_of_birth, latitude, longitude, income_level, kyc_status
-- ----------------------------------------------------------------------------
INSERT INTO customers (customer_id, customer_code, full_name, identity_card, date_of_birth, gender, address, city, state, job, latitude, longitude, income_level, kyc_status) VALUES
('c0000001-0000-0000-0000-000000000001', 'CUST001', 'Nguyen Van An',   'ID0000000001', '1990-03-15', 'MALE',   '12 Le Loi',        'Ho Chi Minh', 'HCM', 'Engineer',          10.762622, 106.660172, 'HIGH',   'VERIFIED'),
('c0000002-0000-0000-0000-000000000002', 'CUST002', 'Tran Thi Binh',   'ID0000000002', '1985-07-22', 'FEMALE', '45 Tran Hung Dao',  'Ha Noi',      'HN',  'Teacher',           21.028511, 105.804817, 'MEDIUM', 'VERIFIED'),
('c0000003-0000-0000-0000-000000000003', 'CUST003', 'Le Van Cuong',    'ID0000000003', '1992-11-05', 'MALE',   '7 Bach Dang',       'Da Nang',     'DN',  'Doctor',            16.054407, 108.202167, 'HIGH',   'VERIFIED'),
('c0000004-0000-0000-0000-000000000004', 'CUST004', 'Pham Thi Dung',   'ID0000000004', '1998-01-30', 'FEMALE', '88 Nguyen Hue',     'Ho Chi Minh', 'HCM', 'Accountant',        10.773374, 106.704170, 'MEDIUM', 'VERIFIED'),
('c0000005-0000-0000-0000-000000000005', 'CUST005', 'Hoang Van Em',    'ID0000000005', '1979-09-12', 'MALE',   '23 Hai Ba Trung',   'Hai Phong',   'HP',  'Manager',           20.844912, 106.688084, 'HIGH',   'VERIFIED'),
('c0000006-0000-0000-0000-000000000006', 'CUST006', 'Vo Thi Phuong',   'ID0000000006', '2000-06-18', 'FEMALE', '5 Pham Ngu Lao',    'Can Tho',     'CT',  'Student',           10.045162, 105.746857, 'LOW',    'PENDING'),
('c0000007-0000-0000-0000-000000000007', 'CUST007', 'Dang Van Giang',  'ID0000000007', '1988-04-09', 'MALE',   '19 Ly Thuong Kiet', 'Ha Noi',      'HN',  'Sales',             21.024500, 105.841171, 'MEDIUM', 'VERIFIED'),
('c0000008-0000-0000-0000-000000000008', 'CUST008', 'Bui Thi Hoa',     'ID0000000008', '1995-12-25', 'FEMALE', '31 Vo Van Tan',     'Ho Chi Minh', 'HCM', 'Nurse',             10.779783, 106.692222, 'MEDIUM', 'VERIFIED'),
('c0000009-0000-0000-0000-000000000009', 'CUST009', 'Do Van Khoa',     'ID0000000009', '1983-08-14', 'MALE',   '60 Hung Vuong',     'Hue',         'TTH', 'Lawyer',            16.463713, 107.590866, 'HIGH',   'VERIFIED'),
('c0000010-0000-0000-0000-000000000010', 'CUST010', 'Ngo Thi Lan',     'ID0000000010', '1996-02-28', 'FEMALE', '14 Quang Trung',    'Nha Trang',   'KH',  'Marketing',         12.238791, 109.196749, 'LOW',    'PENDING');

-- ----------------------------------------------------------------------------
-- merchants (10) - fully populated for fraud scoring
-- merchant_category, risk_level, latitude, longitude, city, state, country, is_blacklisted
-- ----------------------------------------------------------------------------
INSERT INTO merchants (merchant_id, merchant_code, merchant_name, merchant_category, risk_level, is_blacklisted, city, state, country, latitude, longitude) VALUES
('m0000001-0000-0000-0000-000000000001', 'MERC001', 'Saigon Coop Mart',   'grocery_pos',       'LOW',    0, 'Ho Chi Minh', 'HCM', 'Vietnam', 10.762900, 106.682200),
('m0000002-0000-0000-0000-000000000002', 'MERC002', 'Tiki Online',        'shopping_net',      'MEDIUM', 0, 'Ho Chi Minh', 'HCM', 'Vietnam', 10.801600, 106.711700),
('m0000003-0000-0000-0000-000000000003', 'MERC003', 'Highlands Coffee',   'food_dining',       'LOW',    0, 'Ha Noi',      'HN',  'Vietnam', 21.030700, 105.852300),
('m0000004-0000-0000-0000-000000000004', 'MERC004', 'PNJ Jewelry',        'misc_pos',          'MEDIUM', 0, 'Da Nang',     'DN',  'Vietnam', 16.067800, 108.220900),
('m0000005-0000-0000-0000-000000000005', 'MERC005', 'FPT Shop',           'shopping_pos',      'LOW',    0, 'Ho Chi Minh', 'HCM', 'Vietnam', 10.769900, 106.700400),
('m0000006-0000-0000-0000-000000000006', 'MERC006', 'GrabPay Wallet',     'misc_net',          'MEDIUM', 0, 'Ha Noi',      'HN',  'Vietnam', 21.005400, 105.843200),
('m0000007-0000-0000-0000-000000000007', 'MERC007', 'Vinpearl Resort',    'travel',            'MEDIUM', 0, 'Nha Trang',   'KH',  'Vietnam', 12.215300, 109.194500),
('m0000008-0000-0000-0000-000000000008', 'MERC008', 'QuickCash ATM Hub',  'cash_advance',      'HIGH',   0, 'Hai Phong',   'HP',  'Vietnam', 20.844900, 106.688100),
('m0000009-0000-0000-0000-000000000009', 'MERC009', 'OffshoreBet Ltd',    'gambling',          'HIGH',   1, 'Unknown',     'XX',  'Malta',   35.899200, 14.514700),
('m0000010-0000-0000-0000-000000000010', 'MERC010', 'CryptoX Exchange',   'crypto',            'HIGH',   1, 'Unknown',     'XX',  'Seychelles', -4.679600, 55.491900);

-- ----------------------------------------------------------------------------
-- model_configs : the 4 default thresholds (plan.md section 5)
--   fraud: reject 0.65 / review 0.35   loan: high 0.50 / medium 0.20
-- ----------------------------------------------------------------------------
INSERT INTO model_configs (model_name, param_name, param_value, description, updated_by) VALUES
('fraud', 'reject_threshold',      0.650000, 'Fraud score at/above this -> REJECTED',       'u0000001-0000-0000-0000-000000000001'),
('fraud', 'review_threshold',      0.350000, 'Fraud score at/above this -> MANUAL_REVIEW',  'u0000001-0000-0000-0000-000000000001'),
('loan',  'high_risk_threshold',   0.500000, 'PD at/above this -> HIGH RISK',               'u0000001-0000-0000-0000-000000000001'),
('loan',  'medium_risk_threshold', 0.200000, 'PD at/above this -> MEDIUM RISK',             'u0000001-0000-0000-0000-000000000001');

-- ----------------------------------------------------------------------------
-- transactions_live : varied statuses (channel_id 1=POS,2=ECOM,3=ATM,4=MOBILE)
-- ----------------------------------------------------------------------------
INSERT INTO transactions_live (txn_id, customer_id, merchant_id, channel_id, submitted_by, card_number_masked, card_number_hash, amount, txn_time, status, fraud_score, model_version) VALUES
('t0000001-0000-0000-0000-000000000001', 'c0000001-0000-0000-0000-000000000001', 'm0000001-0000-0000-0000-000000000001', 1, 'u0000005-0000-0000-0000-000000000005', '************1234', 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1', 250000.00,  '2026-05-20 09:15:00', 'APPROVED',      0.0420, 'rf_v3_regularized'),
('t0000002-0000-0000-0000-000000000002', 'c0000002-0000-0000-0000-000000000002', 'm0000002-0000-0000-0000-000000000002', 2, 'u0000005-0000-0000-0000-000000000005', '************5678', 'b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2', 1500000.00, '2026-05-21 14:30:00', 'APPROVED',      0.1180, 'rf_v3_regularized'),
('t0000003-0000-0000-0000-000000000003', 'c0000003-0000-0000-0000-000000000003', 'm0000009-0000-0000-0000-000000000009', 2, 'u0000005-0000-0000-0000-000000000005', '************9012', 'c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3', 9800000.00, '2026-05-22 23:45:00', 'MANUAL_REVIEW', 0.4710, 'rf_v3_regularized'),
('t0000004-0000-0000-0000-000000000004', 'c0000004-0000-0000-0000-000000000004', 'm0000010-0000-0000-0000-000000000010', 2, 'u0000005-0000-0000-0000-000000000005', '************3456', 'd4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4', 12000000.00,'2026-05-23 02:10:00', 'REJECTED',      0.8230, 'rf_v3_regularized'),
('t0000005-0000-0000-0000-000000000005', 'c0000005-0000-0000-0000-000000000005', 'm0000005-0000-0000-0000-000000000005', 1, 'u0000005-0000-0000-0000-000000000005', '************7890', 'e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5', 4200000.00, '2026-05-24 11:00:00', 'PENDING',       NULL,   NULL),
('t0000006-0000-0000-0000-000000000006', 'c0000006-0000-0000-0000-000000000006', 'm0000008-0000-0000-0000-000000000008', 3, 'u0000005-0000-0000-0000-000000000005', '************2468', 'f6f6f6f6f6f6f6f6f6f6f6f6f6f6f6f6f6f6f6f6f6f6f6f6f6f6f6f6f6f6f6f6', 7000000.00, '2026-05-25 03:30:00', 'MANUAL_REVIEW', 0.5550, 'rf_v3_regularized'),
('t0000007-0000-0000-0000-000000000007', 'c0000007-0000-0000-0000-000000000007', 'm0000003-0000-0000-0000-000000000003', 4, 'u0000005-0000-0000-0000-000000000005', '************1357', '0707070707070707070707070707070707070707070707070707070707070707', 85000.00,   '2026-05-26 08:20:00', 'APPROVED',      0.0310, 'rf_v3_regularized');

-- review_cases : auto-created for MANUAL_REVIEW transactions (varied statuses)
INSERT INTO review_cases (case_id, txn_id, case_status, assigned_to, decision, decision_note, decided_at) VALUES
('rc000001-0000-0000-0000-000000000001', 't0000003-0000-0000-0000-000000000003', 'OPEN',     NULL,                                    NULL,      NULL,                          NULL),
('rc000002-0000-0000-0000-000000000002', 't0000006-0000-0000-0000-000000000006', 'ASSIGNED', 'u0000004-0000-0000-0000-000000000004', NULL,      NULL,                          NULL);

-- ----------------------------------------------------------------------------
-- loans : varied statuses, AI input/output features populated
-- ----------------------------------------------------------------------------
INSERT INTO loans (loan_id, customer_id, submitted_by, reviewed_by, principal_amount, interest_rate, term_months, purpose, status, review_note, reviewed_at, monthly_payment, outstanding_balance, disbursed_at, maturity_date, person_age, person_income, person_home_ownership, person_emp_length, loan_grade, loan_intent, cb_person_default_on_file, cb_person_cred_hist_length, pd_score, risk_level, model_version) VALUES
('l0000001-0000-0000-0000-000000000001', 'c0000001-0000-0000-0000-000000000001', 'u0000005-0000-0000-0000-000000000005', NULL,                                    50000000.00, 12.5000, 24, 'PERSONAL',          'PENDING',  NULL,                  NULL,                  NULL,        NULL,        NULL,         '2026-05-28', 36, 240000000.00, 'MORTGAGE', 8, 'B', 'PERSONAL',          'N', 7, 0.1450, 'LOW RISK',    'loan_v6'),
('l0000002-0000-0000-0000-000000000002', 'c0000002-0000-0000-0000-000000000002', 'u0000005-0000-0000-0000-000000000005', 'u0000004-0000-0000-0000-000000000004', 30000000.00, 14.0000, 12, 'EDUCATION',         'APPROVED', 'Good credit history', '2026-05-26 10:00:00', 2691000.00,  30000000.00, '2026-05-27 09:00:00', '2027-05-27', 41, 180000000.00, 'RENT',     5, 'C', 'EDUCATION',         'N', 5, 0.2800, 'MEDIUM RISK', 'loan_v6'),
('l0000003-0000-0000-0000-000000000003', 'c0000006-0000-0000-0000-000000000006', 'u0000005-0000-0000-0000-000000000005', 'u0000004-0000-0000-0000-000000000004', 80000000.00, 18.5000, 36, 'DEBTCONSOLIDATION', 'REJECTED', 'High PD, thin file',  '2026-05-27 15:30:00', NULL,        NULL,        NULL,        NULL,        24, 60000000.00,  'RENT',     1, 'F', 'DEBTCONSOLIDATION', 'Y', 2, 0.6200, 'HIGH RISK',   'loan_v6'),
('l0000004-0000-0000-0000-000000000004', 'c0000009-0000-0000-0000-000000000009', 'u0000005-0000-0000-0000-000000000005', 'u0000004-0000-0000-0000-000000000004', 100000000.00,11.0000, 48, 'HOMEIMPROVEMENT',   'DISBURSED','Approved & disbursed', '2026-05-20 11:00:00', 2587000.00, 96000000.00, '2026-05-21 10:00:00', '2030-05-21', 42, 360000000.00, 'OWN',      12,'A', 'HOMEIMPROVEMENT',   'N', 15,0.0900, 'LOW RISK',    'loan_v6');
