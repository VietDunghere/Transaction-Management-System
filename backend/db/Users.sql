CREATE ROLE PROJECT_ADMIN;
GRANT CONNECT, RESOURCE TO PROJECT_ADMIN;
GRANT CREATE VIEW, CREATE PROCEDURE, CREATE SEQUENCE TO PROJECT_ADMIN;
GRANT CREATE USER, DROP USER, ALTER USER TO PROJECT_ADMIN;
GRANT CONNECT, RESOURCE TO PROJECT_ADMIN WITH ADMIN OPTION;
GRANT GRANT ANY PRIVILEGE TO PROJECT_ADMIN;
GRANT CREATE ROLE TO PROJECT_ADMIN;
GRANT DROP ANY ROLE TO PROJECT_ADMIN;
GRANT GRANT ANY ROLE TO PROJECT_ADMIN;


CREATE USER ADMIN IDENTIFIED BY "123456";
GRANT PROJECT_ADMIN TO ADMIN;
ALTER USER ADMIN QUOTA UNLIMITED ON USERS;

-- ============================================================
-- 1. ROLE: OPERATOR
--    Core Banking System của Ngân hàng đối tác (hệ thống tự động).
--    Chỉ được INSERT giao dịch / đơn vay — không đọc báo cáo.
-- ============================================================
CREATE ROLE OPERATOR;
GRANT CONNECT TO OPERATOR;

GRANT SELECT, INSERT ON "transactions_live"    TO OPERATOR;
GRANT SELECT, INSERT ON "txn_idempotency"      TO OPERATOR;
GRANT SELECT, INSERT ON "txn_state"            TO OPERATOR;
GRANT SELECT, INSERT ON "txn_state_history"    TO OPERATOR;
GRANT SELECT, INSERT ON "loans"                TO OPERATOR;
GRANT SELECT         ON "customers"            TO OPERATOR;
GRANT SELECT         ON "merchants"            TO OPERATOR;
GRANT SELECT         ON "channels"             TO OPERATOR;
GRANT SELECT         ON "risk_scoring_results" TO OPERATOR;
GRANT SELECT         ON "rule_hits"            TO OPERATOR;
GRANT SELECT         ON "model_configs"        TO OPERATOR;
GRANT SELECT         ON "suppression_rules"    TO OPERATOR;
GRANT SELECT, INSERT, UPDATE ON "card_velocity_stats" TO OPERATOR;

GRANT EXECUTE ON PROC_SUBMIT_TRANSACTION TO OPERATOR;

-- ============================================================
-- 2. ROLE: REVIEWER
--    Nhân viên duyệt Case thủ công.
-- ============================================================
CREATE ROLE REVIEWER;
GRANT CONNECT TO REVIEWER;

GRANT SELECT, UPDATE        ON "review_cases"        TO REVIEWER;
GRANT SELECT, INSERT, UPDATE ON "review_case_actions" TO REVIEWER;
GRANT SELECT, UPDATE        ON "transactions_live"   TO REVIEWER;
GRANT SELECT, UPDATE        ON "txn_state"           TO REVIEWER;
GRANT SELECT, INSERT        ON "txn_state_history"   TO REVIEWER;
GRANT SELECT                ON "customers"           TO REVIEWER;
GRANT SELECT                ON "merchants"           TO REVIEWER;
GRANT SELECT                ON "risk_scoring_results" TO REVIEWER;

GRANT EXECUTE ON PROC_PROCESS_REVIEW_CASE TO REVIEWER;

-- ============================================================
-- 3. ROLE: ANALYST
--    Chuyên viên Phân tích Rủi ro.
-- ============================================================
CREATE ROLE ANALYST;
GRANT CONNECT TO ANALYST;

-- Đọc dữ liệu OLTP để phân tích
GRANT SELECT ON "transactions_live"     TO ANALYST;
GRANT SELECT ON "risk_scoring_results"  TO ANALYST;
GRANT SELECT ON "rule_hits"             TO ANALYST;
GRANT SELECT ON "loans"                 TO ANALYST;
GRANT SELECT ON "review_cases"          TO ANALYST;
GRANT SELECT ON "audit_logs"            TO ANALYST;
GRANT SELECT ON "customers"             TO ANALYST;
GRANT SELECT ON "merchants"             TO ANALYST;
GRANT SELECT ON "card_velocity_stats"   TO ANALYST;
GRANT SELECT ON "reconciliation_runs"   TO ANALYST;
GRANT SELECT ON "reconciliation_items"  TO ANALYST;
GRANT SELECT ON "etl_logs"             TO ANALYST;
GRANT SELECT ON "datalake_snapshots"   TO ANALYST;

-- DWH — đọc để phân tích xu hướng
GRANT SELECT ON "fact_transactions"    TO ANALYST;
GRANT SELECT ON "fact_loans"           TO ANALYST;
GRANT SELECT ON "dim_time"             TO ANALYST;
GRANT SELECT ON "dim_customer"         TO ANALYST;
GRANT SELECT ON "dim_merchant"         TO ANALYST;
GRANT SELECT ON "dim_channel"          TO ANALYST;

-- Analyst Module — toàn quyền trên 3 bảng nghiệp vụ
GRANT SELECT, INSERT, UPDATE ON "model_configs"     TO ANALYST;
GRANT SELECT, INSERT, UPDATE ON "suppression_rules" TO ANALYST;
GRANT SELECT, INSERT, UPDATE ON "analyst_reports"   TO ANALYST;

-- ============================================================
-- 4. ROLE: MANAGER
--    Quản lý / Giám đốc Vận hành.
-- ============================================================
CREATE ROLE MANAGER;
GRANT CONNECT TO MANAGER;

-- DWH báo cáo
GRANT SELECT ON "fact_transactions"   TO MANAGER;
GRANT SELECT ON "fact_loans"          TO MANAGER;
GRANT SELECT ON "dim_time"            TO MANAGER;
GRANT SELECT ON "dim_customer"        TO MANAGER;
GRANT SELECT ON "dim_merchant"        TO MANAGER;
GRANT SELECT ON "dim_channel"         TO MANAGER;
GRANT SELECT ON "dim_location"        TO MANAGER;

-- OLTP dashboard
GRANT SELECT ON "transactions_live"    TO MANAGER;
GRANT SELECT ON "review_cases"         TO MANAGER;
GRANT SELECT ON "review_case_actions"  TO MANAGER;
GRANT SELECT ON "loans"                TO MANAGER;
GRANT SELECT ON "risk_scoring_results" TO MANAGER;
GRANT SELECT ON "customers"            TO MANAGER;
GRANT SELECT ON "merchants"            TO MANAGER;

-- Audit & Đối soát
GRANT SELECT ON "audit_logs"           TO MANAGER;
GRANT SELECT ON "reconciliation_runs"  TO MANAGER;
GRANT SELECT ON "reconciliation_items" TO MANAGER;
GRANT SELECT ON "etl_logs"            TO MANAGER;

-- Analyst Module — xem + acknowledge báo cáo
GRANT SELECT         ON "model_configs"     TO MANAGER;
GRANT SELECT         ON "suppression_rules" TO MANAGER;
GRANT SELECT, UPDATE ON "analyst_reports"   TO MANAGER;

-- ============================================================
-- 5. ROLE: IT_ADMIN
--    Quản trị viên Hệ thống — tách biệt với PROJECT_ADMIN.
-- ============================================================
CREATE ROLE IT_ADMIN;
GRANT CONNECT TO IT_ADMIN;

-- Phân quyền người dùng
GRANT SELECT, INSERT, UPDATE, DELETE ON "users"      TO IT_ADMIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON "roles"      TO IT_ADMIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON "user_roles" TO IT_ADMIN;

-- Master Data
GRANT SELECT, INSERT, UPDATE, DELETE ON "customers" TO IT_ADMIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON "merchants" TO IT_ADMIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON "channels"  TO IT_ADMIN;

-- Vận hành ETL & Đối soát
GRANT SELECT, INSERT, UPDATE, DELETE ON "etl_logs"             TO IT_ADMIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON "datalake_snapshots"   TO IT_ADMIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON "reconciliation_runs"  TO IT_ADMIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON "reconciliation_items" TO IT_ADMIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON "card_velocity_stats"  TO IT_ADMIN;

GRANT EXECUTE ON PROC_EXECUTE_RECONCILIATION TO IT_ADMIN;

-- Audit
GRANT SELECT ON "audit_logs" TO IT_ADMIN;

-- Analyst Module
GRANT SELECT, INSERT, UPDATE, DELETE ON "model_configs"     TO IT_ADMIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON "suppression_rules" TO IT_ADMIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON "analyst_reports"   TO IT_ADMIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON "loans"             TO IT_ADMIN;
