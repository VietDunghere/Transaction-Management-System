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


