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
-- 1. ROLE: OPERATOR (Nhân viên Vận hành / Kênh giao dịch)
-- ============================================================
CREATE ROLE OPERATOR;
GRANT CONNECT TO OPERATOR;

-- Quyền Nhóm bảng Giao dịch: Thêm và Xem
GRANT SELECT, INSERT ON "transactions_live" TO OPERATOR;
GRANT SELECT, INSERT ON "txn_idempotency" TO OPERATOR;
GRANT SELECT, INSERT ON "txn_state" TO OPERATOR;
GRANT SELECT, INSERT ON "txn_state_history" TO OPERATOR;

-- Quyền Nhóm bảng Thông tin: Chỉ Xem
GRANT SELECT ON "customers" TO OPERATOR;
GRANT SELECT ON "merchants" TO OPERATOR;
GRANT SELECT ON "channels" TO OPERATOR;

-- Quyền Nhóm bảng AI: Chỉ Xem
GRANT SELECT ON "risk_scoring_results" TO OPERATOR;
GRANT SELECT ON "rule_hits" TO OPERATOR;

-- Cấp quyền gọi Procedure Submit (quan trọng để chạy luồng tạo mới)
GRANT EXECUTE ON PROC_SUBMIT_TRANSACTION TO OPERATOR;

-- ============================================================
-- 2. ROLE: REVIEWER (Nhân viên Duyệt / Thẩm định viên)
-- ============================================================
CREATE ROLE REVIEWER;
GRANT CONNECT TO REVIEWER;

-- Quyền Nhóm bảng Duyệt tay: Xem, Thêm, Sửa
GRANT SELECT, UPDATE ON "review_cases" TO REVIEWER;
GRANT SELECT, INSERT, UPDATE ON "review_case_actions" TO REVIEWER;

-- Quyền Nhóm bảng Giao dịch: Xem, Sửa
GRANT SELECT, UPDATE ON "transactions_live" TO REVIEWER;
GRANT SELECT, UPDATE ON "txn_state" TO REVIEWER;
GRANT SELECT, INSERT ON "txn_state_history" TO REVIEWER; -- INSERT cho trigger/log nếu cần thiết ở mức user

-- Quyền Nhóm bảng AI & Master Data: Chỉ Xem
GRANT SELECT ON "customers" TO REVIEWER;
GRANT SELECT ON "merchants" TO REVIEWER;
GRANT SELECT ON "risk_scoring_results" TO REVIEWER;

-- Cấp quyền gọi Procedure xử lý case
GRANT EXECUTE ON PROC_PROCESS_REVIEW_CASE TO REVIEWER;

-- ============================================================
-- 3. ROLE: MANAGER (Quản lý / Giám đốc Vận hành)
-- ============================================================
CREATE ROLE MANAGER;
GRANT CONNECT TO MANAGER;

-- Quyền Báo cáo OLAP: Chỉ xem
GRANT SELECT ON "fact_transactions" TO MANAGER;
GRANT SELECT ON "fact_loans" TO MANAGER;
GRANT SELECT ON "dim_time" TO MANAGER;
GRANT SELECT ON "dim_customer" TO MANAGER;
GRANT SELECT ON "dim_merchant" TO MANAGER;
GRANT SELECT ON "dim_channel" TO MANAGER;
GRANT SELECT ON "dim_location" TO MANAGER;

-- Quyền Giao dịch & Case Dashboard KPI: Chỉ xem
GRANT SELECT ON "transactions_live" TO MANAGER;
GRANT SELECT ON "review_cases" TO MANAGER;
GRANT SELECT ON "review_case_actions" TO MANAGER;

-- Quyền Audit & Đối soát tiến độ dòng tiền: Chỉ xem
GRANT SELECT ON "audit_logs" TO MANAGER;
GRANT SELECT ON "reconciliation_jobs" TO MANAGER;
GRANT SELECT ON "reconciliation_items" TO MANAGER;

-- ============================================================
-- 4. ROLE: IT_ADMIN (Quản trị viên Hệ thống / IT Support)
-- (Tách biệt với PROJECT_ADMIN, chuyên phục vụ nghiệp vụ IT)
-- ============================================================
CREATE ROLE IT_ADMIN;
GRANT CONNECT TO IT_ADMIN;

-- Nhóm bảng Phân quyền: Toàn quyền CRUD
GRANT SELECT, INSERT, UPDATE, DELETE ON "users" TO IT_ADMIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON "roles" TO IT_ADMIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON "user_roles" TO IT_ADMIN;

-- Nhóm bảng Master Data: Toàn quyền CRUD (quản lý, khóa merchant vi phạm...)
GRANT SELECT, INSERT, UPDATE, DELETE ON "customers" TO IT_ADMIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON "merchants" TO IT_ADMIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON "channels" TO IT_ADMIN;

-- Nhóm bảng Vận hành Data (Batch Jobs/ETL/Đối soát): Xem & Thêm
GRANT SELECT, INSERT ON "raw_ingest_batches" TO IT_ADMIN;
GRANT SELECT, INSERT ON "reconciliation_jobs" TO IT_ADMIN;
GRANT SELECT, INSERT ON "reconciliation_items" TO IT_ADMIN;

-- Cấp thêm quyền chạy Procedure đối soát phòng khi Job lỗi cần kích hoạt lại (Retry)
GRANT EXECUTE ON PROC_EXECUTE_RECONCILIATION TO IT_ADMIN;

-- Nhóm bảng Ghi vết (Audit): Chỉ xem log hệ thống/truy vết
GRANT SELECT ON "audit_logs" TO IT_ADMIN;



-- ============================================================
-- ANALYST MODULE — ROLE & PERMISSION ADDITIONS (v1.3 — 2026-04-19)
-- ============================================================

-- Thêm OPERATOR, REVIEWER, ANALYST vào roles nếu chưa có
-- (Users.sql cũ chỉ có ADMIN, MANAGER, IT_ADMIN)

-- ============================================================
-- 5. ROLE: OPERATOR (Core Banking System của Ngân hàng đối tác)
-- ============================================================
-- Lưu ý: OPERATOR là hệ thống tự động của ngân hàng, không phải nhân viên.
-- Quyền ở DB level chỉ INSERT giao dịch/đơn vay, không có quyền đọc báo cáo.
CREATE ROLE OPERATOR_SYS;
GRANT CONNECT TO OPERATOR_SYS;

GRANT SELECT, INSERT ON "transactions_live"     TO OPERATOR_SYS;
GRANT SELECT, INSERT ON "txn_idempotency"       TO OPERATOR_SYS;
GRANT SELECT, INSERT ON "txn_state"             TO OPERATOR_SYS;
GRANT SELECT, INSERT ON "txn_state_history"     TO OPERATOR_SYS;
GRANT SELECT, INSERT ON "loans"                 TO OPERATOR_SYS;
GRANT SELECT         ON "customers"             TO OPERATOR_SYS;
GRANT SELECT         ON "merchants"             TO OPERATOR_SYS;
GRANT SELECT         ON "channels"              TO OPERATOR_SYS;
GRANT SELECT         ON "risk_scoring_results"  TO OPERATOR_SYS;
GRANT SELECT         ON "rule_hits"             TO OPERATOR_SYS;
GRANT SELECT         ON "model_configs"         TO OPERATOR_SYS;  -- Đọc ngưỡng để scoring
GRANT SELECT         ON "suppression_rules"     TO OPERATOR_SYS;  -- Đọc whitelist để bypass
GRANT EXECUTE ON PROC_SUBMIT_TRANSACTION        TO OPERATOR_SYS;

-- ============================================================
-- 6. ROLE: REVIEWER (Nhân viên Duyệt Case Thủ công)
-- ============================================================
-- Nâng cấp từ tên REVIEWER sang REVIEWER_ROLE để tránh conflict
CREATE ROLE REVIEWER_ROLE;
GRANT CONNECT TO REVIEWER_ROLE;

GRANT SELECT, UPDATE ON "review_cases"          TO REVIEWER_ROLE;
GRANT SELECT, INSERT, UPDATE ON "review_case_actions" TO REVIEWER_ROLE;
GRANT SELECT, UPDATE ON "transactions_live"     TO REVIEWER_ROLE;
GRANT SELECT, UPDATE ON "txn_state"             TO REVIEWER_ROLE;
GRANT SELECT, INSERT ON "txn_state_history"     TO REVIEWER_ROLE;
GRANT SELECT         ON "customers"             TO REVIEWER_ROLE;
GRANT SELECT         ON "merchants"             TO REVIEWER_ROLE;
GRANT SELECT         ON "risk_scoring_results"  TO REVIEWER_ROLE;
GRANT EXECUTE ON PROC_PROCESS_REVIEW_CASE       TO REVIEWER_ROLE;

-- ============================================================
-- 7. ROLE: ANALYST (Chuyên viên Phân tích Rủi ro)
-- ============================================================
CREATE ROLE ANALYST_ROLE;
GRANT CONNECT TO ANALYST_ROLE;

-- Đọc dữ liệu nghiệp vụ để phân tích
GRANT SELECT ON "transactions_live"     TO ANALYST_ROLE;
GRANT SELECT ON "risk_scoring_results"  TO ANALYST_ROLE;
GRANT SELECT ON "rule_hits"             TO ANALYST_ROLE;
GRANT SELECT ON "loans"                 TO ANALYST_ROLE;
GRANT SELECT ON "review_cases"          TO ANALYST_ROLE;
GRANT SELECT ON "audit_logs"            TO ANALYST_ROLE;
GRANT SELECT ON "customers"             TO ANALYST_ROLE;
GRANT SELECT ON "merchants"             TO ANALYST_ROLE;

-- DWH — đọc để phân tích xu hướng
GRANT SELECT ON "fact_transactions"     TO ANALYST_ROLE;
GRANT SELECT ON "fact_loans"            TO ANALYST_ROLE;
GRANT SELECT ON "dim_time"              TO ANALYST_ROLE;
GRANT SELECT ON "dim_customer"          TO ANALYST_ROLE;
GRANT SELECT ON "dim_merchant"          TO ANALYST_ROLE;
GRANT SELECT ON "dim_channel"           TO ANALYST_ROLE;

-- Analyst Module — toàn quyền trên 3 bảng mới
GRANT SELECT, INSERT, UPDATE ON "model_configs"     TO ANALYST_ROLE;
GRANT SELECT, INSERT, UPDATE ON "suppression_rules" TO ANALYST_ROLE;
GRANT SELECT, INSERT, UPDATE ON "analyst_reports"   TO ANALYST_ROLE;

-- ============================================================
-- Cập nhật MANAGER — thêm quyền xem 3 bảng Analyst Module
-- ============================================================
GRANT SELECT         ON "model_configs"     TO MANAGER;
GRANT SELECT         ON "suppression_rules" TO MANAGER;
GRANT SELECT, UPDATE ON "analyst_reports"   TO MANAGER;  -- UPDATE để acknowledge
GRANT SELECT         ON "loans"             TO MANAGER;

-- ============================================================
-- Cập nhật IT_ADMIN (= ADMIN trong app) — toàn quyền trên 3 bảng mới
-- ============================================================
GRANT SELECT, INSERT, UPDATE, DELETE ON "model_configs"     TO IT_ADMIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON "suppression_rules" TO IT_ADMIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON "analyst_reports"   TO IT_ADMIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON "loans"             TO IT_ADMIN;
