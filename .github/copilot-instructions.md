# GIỚI THIỆU DỰ ÁN (PROJECT CONTEXT)
- **Tên dự án**: Hệ thống quản lý vòng đời giao dịch ngân hàng (Transaction Management System).
- **Phạm vi**: Đây là hệ thống quản lý (Intake -> AI Scoring -> Workflow Routing -> Audit -> Data Warehouse), **KHÔNG** phải Core Banking/Ledger. Các thay đổi về số dư không được hạch toán thật mà chỉ mô phỏng qua trạng thái giao dịch và đối soát.

# TECH STACK
- **Frontend**: ReactJS (Admin Dashboard, Case Management).
- **Backend**: FastAPI (Python), RESTful APIs, JWT Authentication.
- **Database (OLTP)**: Oracle DB (ưu tiên tính ACID, chuẩn hóa 3NF).
- **Data Warehouse (OLAP)**: Oracle DB (Mô hình Star Schema - Fact/Dimension).
- **AI/ML**: Python (Scikit-learn, Random Forest) dùng để chấm điểm rủi ro (Fraud/Loan Scoring).
- **Data Engineering**: Python (ETL từ file CSV mô phỏng Data Lake vào Data Warehouse).

# QUY TẮC KIẾN TRÚC & VIẾT CODE (ARCHITECTURAL RULES)

## 1. Tầng Dữ liệu & Database (Oracle)
- **Tuyệt đối không cập nhật trạng thái giao dịch tại Data Warehouse**. Mọi thao tác INSERT/UPDATE quyết định trạng thái (PENDING, APPROVED, REJECTED, MANUAL_REVIEW) chỉ diễn ra tại OLTP.
- **Quyết định nghiệp vụ (Policy Decision) được ưu tiên đặt tại Database**: Các logic chốt hạ trạng thái (ví dụ: duyệt khoản vay dựa trên AI score) PHẢI được xử lý qua Stored Procedure (PL/SQL) kết hợp Transaction (COMMIT/ROLLBACK) để đảm bảo tính ACID.
- **Luôn ghi vết (Audit/Trigger)**: Bất kỳ thay đổi trạng thái hoặc giao dịch có giá trị cao (ví dụ: > 500M) đều phải có Trigger hoặc Procedure ghi log vào bảng `AUDIT_LOGS`.

## 2. Tầng Backend (FastAPI)
- Model AI/ML chỉ đóng vai trò "tham mưu" (Scoring). FastAPI nhận payload, gọi Model lấy `fraud_score` hoặc `pd_score`, sau đó truyền xuống Stored Procedure của Oracle để ra quyết định cuối cùng.
- Áp dụng nguyên tắc **Idempotency** (Tính lũy đẳng) cho các API Submit giao dịch: Kiểm tra `idem_key` / `txn_hash` để chặn trùng lặp trước khi gọi xuống Database.
- Các API Report/Dashboard (GET) chỉ được phép query (đọc) từ Data Warehouse (Fact/Dimension), không query vào OLTP.

## 3. Lịch sử Schema Hiện Tại (Reference Schema)
- **OLTP**: `USERS`, `ROLES`, `USER_ROLES`, `CUSTOMERS`, `TRANSACTIONS_LIVE` (Lưu trạng thái giao dịch), `LOAN_APPLICATIONS`, `LOAN_RISK_SCORES`, `AUDIT_LOGS`, `REVIEW_CASES`, `TXN_IDEMPOTENCY`, `TXN_STATE`, `RECONCILIATION_JOBS`.
- **OLAP (Warehouse)**: `FACT_TRANSACTIONS`, `DIM_TIME`, `DIM_CUSTOMER`, `DIM_LOCATION`.

## 4. Quy ước Code (Coding Standards)
- **Python/FastAPI**: Sử dụng type hints (`pydantic` models) đầy đủ cho request/response. Xử lý exception rõ ràng và trả về HTTP status code chuẩn.
- **SQL/PLSQL**: Viết hoa các từ khóa SQL (SELECT, INSERT, UPDATE, PROCEDURE, TRIGGER, v.v.). Thêm comment giải thích logic policy trong Procedure.
- **React**: Tách biệt UI Components và Logic (Custom Hooks). Các component hiển thị report cần xử lý tốt các state Loading/Error.