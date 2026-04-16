# API Summary – Transaction Management System

> **Base URL:** `https://api.tms.local/api/v1`

---

## Hệ thống & Health

| # | Phương thức | URL | Input | Output | Tác dụng |
|---|---|---|---|---|---|
| 1 | `GET` | `/health` | _(không có)_ | `status`, `version`, `timestamp` | Kiểm tra trạng thái hệ thống, phục vụ load balancer & health probes |

---

## UC02 – Xác thực & Phân quyền

| # | Phương thức | URL | Input | Output | Tác dụng |
|---|---|---|---|---|---|
| 2 | `POST` | `/auth/login` | `username`, `password` | `access_token`, `role`, `user_id` | Đăng nhập, nhận JWT token |
| 3 | `POST` | `/auth/logout` | _(Bearer Token)_ | `message` | Đăng xuất, hủy phiên |
| 4 | `GET` | `/auth/me` | _(Bearer Token)_ | `user_id`, `username`, `role`, `is_active` | Xem thông tin tài khoản đang xác thực _(Tất cả roles)_ |
| 5 | `PATCH` | `/auth/change-password` | `current_password`, `new_password`, `confirm_password` | `message` | Đổi mật khẩu cá nhân |
| 6 | `GET` | `/users` | Query: `page`, `limit`, `role`, `is_active` | Danh sách user (phân trang) | Xem danh sách tài khoản _(MANAGER, ADMIN)_ |
| 7 | `GET` | `/users/{user_id}` | `user_id` trên URL | `user_id`, `username`, `role`, `is_active`, `created_at` | Xem chi tiết thông tin một người dùng cụ thể _(MANAGER, ADMIN)_ |
| 8 | `POST` | `/users` | `username`, `full_name`, `email`, `password`, `role` | `user_id`, `role`, `created_at` | Tạo tài khoản nhân viên mới _(ADMIN)_ |
| 9 | `PATCH` | `/users/{user_id}/disable` | _(user_id trên URL)_ | `is_active: false` | Vô hiệu hóa tài khoản (không được tự disable chính mình) _(ADMIN)_ |
| 10 | `PATCH` | `/users/{user_id}/enable` | _(user_id trên URL)_ | `is_active: true` | Kích hoạt lại tài khoản đã bị vô hiệu hóa _(ADMIN)_ |
| 11 | `PATCH` | `/users/{user_id}/role` | `role` | `user_id`, `role`, `updated_at` | Gán/thay đổi vai trò người dùng _(ADMIN)_ |

---

## UC03 – Quản lý Giao dịch

| # | Phương thức | URL | Input | Output | Tác dụng |
|---|---|---|---|---|---|
| 12 | `POST` | `/transactions/submit` | `card_number` (dạng raw, server tự mask), `amount`, `merchant_id`, `currency`, `metadata` | `txn_id`, `idempotency_key`, `status`, `fraud_score`, `override_reason` | Gửi giao dịch; Server định tuyến, lấy các field tĩnh hash thành `idempotency_key`, tránh xử lý lặp _(OPERATOR)_ |
| 13 | `GET` | `/transactions` | Query: `page`, `limit`, `status`, `from_date`, `to_date`, `merchant_id`, `min_amount`, `max_amount` | Danh sách giao dịch (phân trang) | Liệt kê giao dịch. **Lưu ý:** Filter ngầm `submitted_by` được tự động gán nếu role là OPERATOR _(Tất cả roles)_ |
| 14 | `GET` | `/transactions/{txn_id}` | `txn_id` trên URL | Chi tiết giao dịch + `state_history` | Xem chi tiết một giao dịch cụ thể _(Tất cả roles)_ |

*(Endpoint duyệt thẳng giao dịch `PATCH /transaction/{txn_id}/status` đã bị gỡ bỏ theo khuyến nghị Audit (Issue #3) nhằm giữ Audit Trail, mọi việc duyệt phải thông qua Case flow bên dưới).*

---

## UC04 – Hỗ trợ Quyết định Cho vay (Loan Simulator)

| # | Phương thức | URL | Input | Output | Tác dụng |
|---|---|---|---|---|---|
| 15 | `POST` | `/loans/submit` | Dữ liệu khoản vay, người vay | `loan_id`, `pd_score`, `risk_level` | Gửi và chấm điểm khoản vay giả định _(OPERATOR)_ |
| 16 | `GET` | `/loans` | Query: `page`, `limit`, `status` | Danh sách khoản vay (phân trang) | Liệt kê các hồ sơ xin vay vốn _(MANAGER, ADMIN)_ |
| 17 | `GET` | `/loans/{loan_id}` | `loan_id` trên URL | Chi tiết hồ sơ vay | Kiểm tra và xem lại chi tiết vay _(MANAGER, ADMIN)_ |

---

## UC05 – Case Management & Audit

| # | Phương thức | URL | Input | Output | Tác dụng |
|---|---|---|---|---|---|
| 18 | `GET` | `/cases` | Query: `page`, `limit`, `status`, `assigned_to`, `from_date`, `to_date` | Danh sách case (phân trang) | Xem danh sách case MANUAL_REVIEW cần xử lý _(REVIEWER, MANAGER, ADMIN)_ |
| 19 | `POST` | `/cases/{case_id}/assign` | `case_id` trên URL | `case_id`, `status: ASSIGNED`, `assigned_to` | Nhận case về xử lý. *Có constraint Transaction Locking (WHERE assigned_to IS NULL)* để chặn race condition _(REVIEWER)_ |
| 20 | `GET` | `/cases/{case_id}` | `case_id` trên URL | Chi tiết case + thông tin giao dịch | Xem chi tiết case để ra quyết định _(REVIEWER, MANAGER, ADMIN)_ |
| 21 | `PATCH` | `/cases/{case_id}/decision` | `decision` (`APPROVED`/`REJECTED`), `note` (bắt buộc), **`version`** | `case_id`, `txn_status` mới | Duyệt/Từ chối case (Gộp Approve & Reject). Có `version` để kích hoạt Optimistic Locking ngừa đụng độ _(REVIEWER)_ |
| 22 | `GET` | `/audit-logs` | Query: `page`, `limit`, `entity_type`, `entity_id`, ... | Danh sách audit events (phân trang) | Xem toàn bộ Audit Log hệ thống _(MANAGER, ADMIN)_ |
| 23 | `GET` | `/audit-logs/transactions/{txn_id}/trace` | `txn_id` trên URL | Timeline đầy đủ sự kiện của giao dịch | Truy vết lịch sử một giao dịch từ lúc tạo đến hiện tại _(MANAGER, ADMIN)_ |
| 24 | `GET` | `/audit-logs/export` | Query: `format` (`csv`/`pdf`), `from_date`, `to_date`, `entity_type` | File download (CSV/PDF) | Xuất báo cáo Audit Log ra file _(MANAGER, ADMIN)_ |

---

## UC06 – Data Engineering & Báo cáo

| # | Phương thức | URL | Input | Output | Tác dụng |
|---|---|---|---|---|---|
| 25 | `GET` | `/dashboard/summary` | Query: `period` (`today`/`this_week`/`this_month`) | Tổng số giao dịch, fraud rate, trend + `granularity` | Xem Dashboard tổng quan _(MANAGER, ADMIN)_ |
| 26 | `GET` | `/dashboard/fraud-chart` | Query: `from_date`, `to_date` (chính), `period` (nhúng) | Tỷ lệ Fraud/Legit | Xem biểu đồ Fraud vs Legit từ OLAP _(MANAGER, ADMIN)_ |
| 27 | `GET` | `/reports/transactions` | Query: `period`, `from_date`, `to_date` | Báo cáo count, amount, tỷ lệ Trạng thái | Xem báo cáo phân tích tổng hợp _(MANAGER, ADMIN)_ |
| 28 | `GET` | `/reports/transactions/export`| Query: `format`, `from_date`, `to_date` | File download (CSV/PDF) | Xuất báo cáo giao dịch ra file _(MANAGER, ADMIN)_ |
| 29 | `GET` | `/datalake/structure` | Query: `page`, `limit` | Danh sách thư mục (Đã bổ sung Phân trang) | Xem cấu trúc Data Lake _(ADMIN)_ |
| 30 | `GET` | `/etl/logs` | Query: `page`, `limit`, `status`, `from_date`| Danh sách ETL jobs kết quả tóm tắt | Xem lịch sử chạy ETL pipeline _(ADMIN)_ |
| 31 | `GET` | `/etl/logs/{job_id}` | `job_id` trên URL | Chi tiết job + errors (nếu có) | Poll chi tiết trang thái một ETL job cụ thể _(ADMIN)_ |
| 32 | `POST` | `/etl/trigger` | `date`, `mode` (`FULL`/`INCREMENTAL`) | `job_id`, `status: RUNNING` | Khởi chạy thủ công ETL Pipeline _(ADMIN)_ |

---

## UC07 – Idempotency, State & Reconciliation

| # | Phương thức | URL | Input | Output | Tác dụng |
|---|---|---|---|---|---|
| 33 | `GET` | `/transactions/{txn_id}/states`| `txn_id` trên URL | `current_status`, `history[]` | Xem lịch sử Transition state của giao dịch _(OPERATOR, ADMIN)_ |
| 34 | `POST` | `/reconciliation/run` | `date` | `job_id`, `status: RUNNING` | Khởi động đối soát (Reconciliation) OLTP / Lake / WH _(ADMIN)_ |
| 35 | `GET` | `/reconciliation/jobs` | Query: `page`, `limit`, `status` (`MATCH`/`MISMATCH`/`RUNNING`/`FAILED`) | Danh sách jobs đối soát | Xem danh sách kết quả đối soát _(ADMIN, MANAGER)_ |
| 36 | `GET` | `/reconciliation/jobs/{job_id}`| `job_id` trên URL | Chi tiết discrepancies | Xem chi tiết lỗi lệch (MISMATCH/FAILED) _(ADMIN, MANAGER)_ |

---

## Tóm tắt thay đổi mới nhất (Đã Audit)

- **Chuẩn hóa URL:** Tăng version `api/v1/`, số nhiều cho `/transactions`.
- **Cải thiện Bảo mật & Audit:** 
  - Gỡ bỏ `PATCH /transaction/{txn_id}/status` cũ.
  - Reviewer dùng `PATCH /cases/{case_id}/decision` kèm theo tham số `version` chống ghi đè dữ liệu.
  - Cấm `ADMIN` tự sát (vô hiệu hóa mình), gán Filter bắt buộc vào việc xem giao dịch của `OPERATOR`.
- **Hoàn thiện thiết kế:**
  - Bổ sung `/health`, CRUD cho Loans (`UC04`) và `GET /auth/me`.
  - Phân trang cấu trúc thư mục DataLake, bổ sung log query cho ETL theo dõi chi tiết.
- **Tổng cộng:** 36 endpoints chính thức.
