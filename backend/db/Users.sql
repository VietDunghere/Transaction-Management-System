CREATE ROLE PROJECT_ADMIN;
GRANT CONNECT, RESOURCE TO PROJECT_ADMIN;
GRANT CREATE VIEW, CREATE PROCEDURE, CREATE SEQUENCE TO PROJECT_ADMIN;
GRANT CREATE USER, DROP USER, ALTER USER TO PROJECT_ADMIN;
GRANT CONNECT, RESOURCE TO PROJECT_ADMIN WITH ADMIN OPTION;
GRANT GRANT ANY PRIVILEGE TO PROJECT_ADMIN;
GRANT CREATE ROLE TO PROJECT_ADMIN;
GRANT DROP ANY ROLE TO PROJECT_ADMIN;
GRANT GRANT ANY ROLE TO PROJECT_ADMIN;


CREATE USER PA IDENTIFIED BY "123456";
GRANT PROJECT_ADMIN TO PA;
ALTER USER PA QUOTA UNLIMITED ON USERS;

-- ============================================================
-- 1. ROLE: OPERATOR
--    Core Banking System của Ngân hàng đối tác (hệ thống tự động).
--    Chỉ được INSERT giao dịch / đơn vay — không đọc báo cáo.
-- ============================================================
CREATE ROLE OPERATOR;
GRANT CONNECT TO OPERATOR;

GRANT SELECT, INSERT ON "transactions_live"    TO OPERATOR;
GRANT SELECT, INSERT ON "loans"                TO OPERATOR;
GRANT SELECT         ON "customers"            TO OPERATOR;
GRANT SELECT         ON "merchants"            TO OPERATOR;
GRANT SELECT         ON "channels"             TO OPERATOR;
GRANT SELECT         ON "rule_hits"            TO OPERATOR;
GRANT SELECT         ON "model_configs"        TO OPERATOR;
GRANT SELECT, INSERT, UPDATE ON "card_velocity_stats" TO OPERATOR;

GRANT EXECUTE ON PROC_SUBMIT_TRANSACTION TO OPERATOR;

-- ============================================================
-- 2. ROLE: REVIEWER
--    Nhân viên duyệt Case thủ công.
-- ============================================================
CREATE ROLE REVIEWER;
GRANT CONNECT TO REVIEWER;

GRANT SELECT, UPDATE        ON "review_cases"        TO REVIEWER;
GRANT SELECT, UPDATE        ON "transactions_live"   TO REVIEWER;
GRANT SELECT                ON "customers"           TO REVIEWER;
GRANT SELECT                ON "merchants"           TO REVIEWER;
GRANT SELECT                ON "channels"            TO REVIEWER;
GRANT SELECT                ON "rule_hits"           TO REVIEWER;
GRANT SELECT                ON "audit_logs"          TO REVIEWER;

GRANT EXECUTE ON PROC_PROCESS_REVIEW_CASE TO REVIEWER;

-- ============================================================
-- 3. ROLE: ANALYST
--    Chuyên viên Phân tích Rủi ro.
-- ============================================================
CREATE ROLE ANALYST;
GRANT CONNECT TO ANALYST;

-- Đọc dữ liệu OLTP để phân tích
GRANT SELECT ON "transactions_live"     TO ANALYST;
GRANT SELECT ON "rule_hits"             TO ANALYST;
GRANT SELECT ON "loans"                 TO ANALYST;
GRANT SELECT ON "review_cases"          TO ANALYST;
GRANT SELECT ON "audit_logs"            TO ANALYST;
GRANT SELECT ON "customers"             TO ANALYST;
GRANT SELECT ON "merchants"             TO ANALYST;
GRANT SELECT ON "channels"              TO ANALYST;
GRANT SELECT ON "card_velocity_stats"   TO ANALYST;

-- Analyst Module — toàn quyền trên bảng cấu hình mô hình
GRANT SELECT, INSERT, UPDATE ON "model_configs"     TO ANALYST;

-- ============================================================
-- 4. ROLE: MANAGER
--    Quản lý / Giám đốc Vận hành.
-- ============================================================
CREATE ROLE MANAGER;
GRANT CONNECT TO MANAGER;

-- OLTP dashboard
GRANT SELECT ON "transactions_live"    TO MANAGER;
GRANT SELECT ON "review_cases"         TO MANAGER;
GRANT SELECT ON "loans"                TO MANAGER;
GRANT SELECT ON "customers"            TO MANAGER;
GRANT SELECT ON "merchants"            TO MANAGER;
GRANT SELECT ON "channels"             TO MANAGER;
GRANT SELECT ON "rule_hits"            TO MANAGER;
GRANT SELECT ON "card_velocity_stats"  TO MANAGER;

-- Audit
GRANT SELECT ON "audit_logs"           TO MANAGER;
GRANT SELECT ON "model_configs"        TO MANAGER;

-- ============================================================
-- 5. ROLE: IT_ADMIN
--    Quản trị viên Hệ thống — tách biệt với PROJECT_ADMIN.
-- ============================================================
CREATE ROLE IT_ADMIN;
GRANT CONNECT TO IT_ADMIN;

-- Phân quyền người dùng
GRANT SELECT, INSERT, UPDATE, DELETE ON "users"      TO IT_ADMIN;

-- Master Data
GRANT SELECT, INSERT, UPDATE, DELETE ON "customers" TO IT_ADMIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON "merchants" TO IT_ADMIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON "channels"  TO IT_ADMIN;

-- Vận hành hệ thống
GRANT SELECT, INSERT, UPDATE, DELETE ON "transactions_live"   TO IT_ADMIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON "review_cases"        TO IT_ADMIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON "loans"               TO IT_ADMIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON "model_configs"       TO IT_ADMIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON "audit_logs"          TO IT_ADMIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON "rule_hits"           TO IT_ADMIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON "card_velocity_stats" TO IT_ADMIN;

-- Procedure access
GRANT EXECUTE ON PROC_SUBMIT_TRANSACTION    TO IT_ADMIN;
GRANT EXECUTE ON PROC_PROCESS_REVIEW_CASE   TO IT_ADMIN;
