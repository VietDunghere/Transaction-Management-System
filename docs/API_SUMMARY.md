# API Summary – Transaction Management System

> **Base URL:** `https://api.tms.local/api/v1`

---

## Health Check

| # | Phương thức | URL | Input | Output | Tác dụng |
|---|---|---|---|---|---|
| 0 | `GET` | `/health` | _(không có)_ | `status`, `version`, `timestamp` | Kiểm tra trạng thái hệ thống _(Public)_ |

---

## UC02 – Xác thực & Phân quyền

| # | Phương thức | URL | Input | Output | Tác dụng |
|---|---|---|---|---|---|
| 1 | `POST` | `/auth/login` | `username`, `password` | `access_token`, `role`, `user_id` | Đăng nhập, nhận JWT token |
| 2 | `GET` | `/auth/me` | _(Bearer Token)_ | `user_id`, `username`, `role` | Lấy thông tin user hiện tại _(Tất cả roles)_ |
| 3 | `POST` | `/auth/logout` | _(Bearer Token)_ | `message` | Đăng xuất, hủy phiên |
| 4 | `PATCH` | `/auth/change-password` | `current_password`, `new_password`, `confirm_password` | `message` | Đổi mật khẩu cá nhân |
| 5 | `GET` | `/users` | Query: `page`, `limit`, `role`, `is_active` | Danh sách user (phân trang) | Xem danh sách tài khoản _(MANAGER, ADMIN)_ |
| 6 | `GET` | `/users/{user_id}` | `user_id` trên URL | Chi tiết User | Xem chi tiết 1 account _(MANAGER, ADMIN)_ |
| 7 | `POST` | `/users` | `username`, `full_name`, `email`, `password`, `role` | `user_id`, `role`, `created_at` | Tạo tài khoản nhân viên mới _(ADMIN)_ |
| 8 | `PATCH` | `/users/{user_id}/disable` | _(user_id trên URL)_ | `is_active: false` | Vô hiệu hóa tài khoản (server chặn tự disable) _(ADMIN)_ |
| 9 | `PATCH` | `/users/{user_id}/enable` | _(user_id trên URL)_ | `is_active: true` | Mở khóa tài khoản _(ADMIN)_ |
| 10 | `PATCH` | `/users/{user_id}/role` | `role` | `user_id`, `role`, `updated_at` | Gán/thay đổi vai trò người dùng _(ADMIN)_ |

---

## UC03 – Quản lý Giao dịch

| # | Phương thức | URL | Input | Output | Tác dụng |
|---|---|---|---|---|---|
| 11 | `POST` | `/transactions/submit` | `card_number` (số thật), `amount`, `merchant_id`, `currency` | `txn_id`, `idem_key`, `status`, `fraud_score` | Gửi giao dịch; tự mask thẻ, tính idem_key từ amount+card+merchant, gọi AI _(OPERATOR)_ |
| 12 | `GET` | `/transactions` | Query: `page`, `limit`, `status`, `from_date`, `to_date` | Danh sách giao dịch | Xem danh sách (Operator chỉ xem của mình) _(Tất cả roles)_ |
| 13 | `GET` | `/transactions/{txn_id}` | `txn_id` trên URL | Chi tiết giao dịch | Xem chi tiết giao dịch _(Tất cả roles)_ |

---

## UC04 – Quản lý Khoản vay (Loan & Scoring)

| # | Phương thức | URL | Input | Output | Tác dụng |
|---|---|---|---|---|---|
| 14 | `POST` | `/loans/submit` | `customer_info`, `income`, `loan_amount`, `term_months` | `loan_id`, `idem_key`, `status`, `pd_score` | Gửi đơn vay demo; validate, tính idem_key, gọi AI chấm credit score _(OPERATOR)_ |
| 15 | `GET` | `/loans` | Query: `page`, `limit`, `status`, `from_date`, `to_date` | Danh sách đơn vay | Xem danh sách khoản vay (Operator chỉ xem của mình) _(Tất cả roles)_ |
| 16 | `GET` | `/loans/{loan_id}` | `loan_id` trên URL | Chi tiết khoản vay | Xem chi tiết một đơn vay _(Tất cả roles)_ |

---

## UC05 – Case Management & Audit

| # | Phương thức | URL | Input | Output | Tác dụng |
|---|---|---|---|---|---|
| 17 | `GET` | `/cases` | Query: `page`, `limit`, `status`, `assigned_to`, `from_date`, `to_date` | Danh sách case (phân trang) | Xem danh sách case MANUAL_REVIEW cần xử lý _(REVIEWER, MANAGER, ADMIN)_ |
| 18 | `POST` | `/cases/{case_id}/assign` | `case_id` trên URL | `case_id`, `status: ASSIGNED` | Nhận case (có xử lý Race Condition khi assigned_to is null) _(REVIEWER)_ |
| 19 | `GET` | `/cases/{case_id}` | `case_id` trên URL | Chi tiết case + thông tin gốc | Xem chi tiết case _(REVIEWER, MANAGER, ADMIN)_ |
| 20 | `PATCH` | `/cases/{case_id}/decision` | `decision`, `note`, `version` | `case_id`, `status`, `updated_at` | Approve/Reject với update có Optimistic Lock (trạng thái sẽ đi đến 1 chiều) _(REVIEWER)_ |
| 21 | `GET` | `/audit-logs` | Query: `page`, `limit`, `entity_type`, `actor_id`, vv.. | Danh sách audit events | Xem toàn bộ Audit Log _(MANAGER, ADMIN)_ |
| 22 | `GET` | `/audit-logs/transaction/{txn_id}/trace` | `txn_id` trên URL | Timeline đầy đủ sự kiện | Truy vết toàn bộ lịch sử 1 transaction/loan _(MANAGER, ADMIN)_ |
| 23 | `GET` | `/audit-logs/export` | Query: `format`, `from_date`, `to_date` | File (CSV/PDF) | Xuất báo cáo Audit Log ra file _(MANAGER, ADMIN)_ |

---

## UC06 – Data Engineering & Báo cáo

| # | Phương thức | URL | Input | Output | Tác dụng |
|---|---|---|---|---|---|
| 24 | `GET` | `/dashboard/summary` | Query: `period` (`today|week|month`) | Tổng quan + `granularity` | Xem ds chỉ số tổng quan _(MANAGER, ADMIN)_ |
| 25 | `GET` | `/dashboard/fraud-chart` | Query: `from_date`, `to_date` | Tỷ lệ Fraud/Legit | Xem biểu đồ (Ưu tiên absolute dates) _(MANAGER, ADMIN)_ |
| 26 | `GET` | `/reports/transactions` | Query: `from_date`, `to_date` | Báo cáo theo ngày tháng | Xem báo cáo GD theo thời gian _(MANAGER, ADMIN)_ |
| 27 | `GET` | `/reports/transactions/export` | Query: `format`, `from_date`, `to_date` | File download (CSV/PDF) | Xuất báo cáo giao dịch ra file _(MANAGER, ADMIN)_ |
| 28 | `GET` | `/datalake/structure` | Query: `page`, `limit` | Cấu trúc thư mục (paged) | Xem cấu trúc Data Lake có phân trang _(ADMIN)_ |
| 29 | `GET` | `/etl/logs` | Query: `page`, `limit`, `status` | Danh sách ETL jobs (paged) | Xem log tổng của ETL pipeline _(ADMIN)_ |
| 30 | `GET` | `/etl/logs/{job_id}` | `job_id` trên URL | `status`, `logs` chi tiết | Poll trạng thái cho job id cụ thể _(ADMIN)_ |
| 31 | `POST` | `/etl/trigger` | `date`, `mode` | `job_id`, `status: RUNNING` | Trigger thủ công ETL Pipeline (Extract->Transform->Load) _(ADMIN)_ |

---

## UC07 – Idempotency, State & Reconciliation

| # | Phương thức | URL | Input | Output | Tác dụng |
|---|---|---|---|---|---|
| 32 | `GET` | `/transactions/{txn_id}/states` | `txn_id` trên URL | `current_status`, `history[]` | Xem lịch sử state và version của giao dịch _(OPERATOR, ADMIN)_ |
| 33 | `POST` | `/reconciliation/run` | `date` | `job_id`, `status: RUNNING` | Trigger chạy đối soát OLTP, Data Lake, Warehouse _(ADMIN)_ |
| 34 | `GET` | `/reconciliation/jobs` | Query: `page`, `status` (`MATCH|MISMATCH|RUNNING|FAILED`) | Danh sách đối soát jobs | Xem list kết quả đối soát _(ADMIN, MANAGER)_ |
| 35 | `GET` | `/reconciliation/jobs/{job_id}` | `job_id` trên URL | `discrepancies[]`, error msg | Xem chi tiết lệch / lỗi _(ADMIN, MANAGER)_ |

---

## Tổng hợp nhanh

| Nhóm | Số endpoints |
|---|:---:|
| Health Check | 1 |
| Xác thực & Phân quyền | 10 |
| Quản lý Giao dịch | 3 |
| Quản lý Khoản vay | 3 |
| Case Management & Audit | 7 |
| Data Engineering & Báo cáo | 8 |
| Idempotency, State & Reconciliation | 4 |
| **Tổng** | **36** |
