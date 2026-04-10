# API Summary – Transaction Management System

> **Base URL:** `https://api.tms.local/api`

---

## UC02 – Xác thực & Phân quyền

| # | Phương thức | URL | Input | Output | Tác dụng |
|---|---|---|---|---|---|
| 1 | `POST` | `/auth/login` | `username`, `password` | `access_token`, `role`, `user_id` | Đăng nhập, nhận JWT token |
| 2 | `POST` | `/auth/logout` | _(Bearer Token)_ | `message` | Đăng xuất, hủy phiên |
| 3 | `PUT` | `/auth/change-password` | `current_password`, `new_password`, `confirm_password` | `message` | Đổi mật khẩu cá nhân |
| 4 | `GET` | `/users` | Query: `page`, `limit`, `role`, `is_active` | Danh sách user (phân trang) | Xem danh sách tài khoản _(MANAGER, ADMIN)_ |
| 5 | `POST` | `/users` | `username`, `full_name`, `email`, `password`, `role` | `user_id`, `role`, `created_at` | Tạo tài khoản nhân viên mới _(ADMIN)_ |
| 6 | `PATCH` | `/users/{user_id}/disable` | _(user_id trên URL)_ | `is_active: false` | Vô hiệu hóa tài khoản _(ADMIN)_ |
| 7 | `PATCH` | `/users/{user_id}/role` | `role` | `user_id`, `role`, `updated_at` | Gán/thay đổi vai trò người dùng _(ADMIN)_ |

---

## UC03 – Quản lý Giao dịch

| # | Phương thức | URL | Input | Output | Tác dụng |
|---|---|---|---|---|---|
| 8 | `POST` | `/transaction/submit` | `card_number`, `amount`, `merchant_id`, `txn_time`, `currency`, `metadata` | `txn_id`, `idem_key`, `status`, `fraud_score`, `reason_code` | Gửi giao dịch demo; tự động validate, kiểm tra idempotency, chấm điểm AI, phân luồng _(OPERATOR)_ |
| 9 | `GET` | `/transaction` | Query: `page`, `limit`, `status`, `from_date`, `to_date`, `merchant_id`, `min_amount`, `max_amount` | Danh sách giao dịch (phân trang) | Xem danh sách giao dịch với bộ lọc _(Tất cả roles)_ |
| 10 | `GET` | `/transaction/{txn_id}` | `txn_id` trên URL | Chi tiết giao dịch + `state_history` | Xem chi tiết một giao dịch cụ thể _(Tất cả roles)_ |
| 11 | `PATCH` | `/transaction/{txn_id}/status` | `status` (`APPROVED`/`REJECTED`), `note` (bắt buộc) | `txn_id`, `status`, `updated_by`, `updated_at` | Cập nhật trạng thái giao dịch sau khi reviewer duyệt _(REVIEWER)_ |

---

## UC05 – Case Management & Audit

| # | Phương thức | URL | Input | Output | Tác dụng |
|---|---|---|---|---|---|
| 12 | `GET` | `/cases` | Query: `page`, `limit`, `status`, `assigned_to`, `from_date`, `to_date` | Danh sách case (phân trang) | Xem danh sách case MANUAL_REVIEW cần xử lý _(REVIEWER, MANAGER, ADMIN)_ |
| 13 | `POST` | `/cases/{case_id}/assign` | `case_id` trên URL | `case_id`, `status: ASSIGNED`, `assigned_to`, `assigned_at` | Nhận case về xử lý (Assign to me), ghi audit log _(REVIEWER)_ |
| 14 | `GET` | `/cases/{case_id}` | `case_id` trên URL | Chi tiết case + thông tin giao dịch + `state_history` | Xem chi tiết case để đánh giá _(REVIEWER, MANAGER, ADMIN)_ |
| 15 | `POST` | `/cases/{case_id}/approve` | `note` (bắt buộc) | `case_id`, `status: APPROVED`, `txn_status: APPROVED` | Duyệt case; cập nhật trạng thái giao dịch, ghi audit log _(REVIEWER)_ |
| 16 | `POST` | `/cases/{case_id}/reject` | `note` (bắt buộc) | `case_id`, `status: REJECTED`, `txn_status: REJECTED` | Từ chối case; cập nhật trạng thái giao dịch, ghi audit log _(REVIEWER)_ |
| 17 | `GET` | `/audit-logs` | Query: `page`, `limit`, `entity_type`, `entity_id`, `actor_id`, `event_type`, `from_date`, `to_date` | Danh sách audit events (phân trang) | Xem toàn bộ Audit Log hệ thống _(MANAGER, ADMIN)_ |
| 18 | `GET` | `/audit-logs/transaction/{txn_id}/trace` | `txn_id` trên URL | Timeline đầy đủ sự kiện của giao dịch | Truy vết toàn bộ lịch sử một giao dịch từ lúc tạo đến hiện tại _(MANAGER, ADMIN)_ |
| 19 | `GET` | `/audit-logs/export` | Query: `format` (`csv`/`pdf`), `from_date`, `to_date`, `entity_type` | File download (CSV/PDF) | Xuất báo cáo Audit Log ra file _(MANAGER, ADMIN)_ |

---

## UC06 – Data Engineering & Báo cáo

| # | Phương thức | URL | Input | Output | Tác dụng |
|---|---|---|---|---|---|
| 20 | `GET` | `/dashboard/summary` | Query: `period` (`today`/`this_week`/`this_month`) | Tổng số giao dịch, fraud rate, cases pending, trend theo ngày | Xem Dashboard tổng quan _(MANAGER, ADMIN)_ |
| 21 | `GET` | `/dashboard/fraud-chart` | Query: `period`, `from_date`, `to_date` | Tỷ lệ Fraud/Legit (count + amount), breakdown theo kỳ | Xem biểu đồ Fraud vs Legit từ Warehouse (OLAP) _(MANAGER, ADMIN)_ |
| 22 | `GET` | `/reports/transactions` | Query: `period` (`daily`/`weekly`/`monthly`/`quarterly`), `from_date`, `to_date` | Báo cáo theo kỳ: count, amount, tỷ lệ APPROVED/REJECTED/MANUAL_REVIEW | Xem báo cáo giao dịch theo thời gian _(MANAGER, ADMIN)_ |
| 23 | `GET` | `/reports/transactions/export` | Query: `format`, `period`, `from_date`, `to_date` | File download (CSV/PDF) | Xuất báo cáo giao dịch ra file _(MANAGER, ADMIN)_ |
| 24 | `GET` | `/datalake/structure` | _(không có)_ | Danh sách thư mục theo ngày, số file, kích thước | Xem cấu trúc Data Lake _(ADMIN)_ |
| 25 | `GET` | `/etl/logs` | Query: `page`, `limit`, `status`, `from_date` | Danh sách ETL jobs (rows extracted/loaded, lỗi nếu có) | Xem log ETL pipeline _(ADMIN)_ |
| 26 | `POST` | `/etl/trigger` | `date`, `mode` (`FULL`/`INCREMENTAL`) | `job_id`, `status: RUNNING` | Trigger thủ công ETL Pipeline (Extract → Transform → Load) _(ADMIN)_ |

---

## UC07 – Idempotency, State & Reconciliation

| # | Phương thức | URL | Input | Output | Tác dụng |
|---|---|---|---|---|---|
| 27 | `GET` | `/transaction/{txn_id}/states` | `txn_id` trên URL | `current_status`, `current_version`, `history[]` (status + version + actor) | Xem lịch sử trạng thái & version Optimistic Locking của giao dịch _(OPERATOR, ADMIN)_ |
| 28 | `POST` | `/reconciliation/run` | `date` | `job_id`, `status: RUNNING` | Trigger đối soát: so khớp COUNT(*) và SUM(amount) giữa OLTP, Data Lake, Warehouse _(ADMIN)_ |
| 29 | `GET` | `/reconciliation/jobs` | Query: `page`, `limit`, `status` (`MATCH`/`MISMATCH`/`RUNNING`), `from_date` | Danh sách reconciliation jobs với kết quả tóm tắt | Xem danh sách kết quả đối soát theo ngày _(ADMIN, MANAGER)_ |
| 30 | `GET` | `/reconciliation/jobs/{job_id}` | `job_id` trên URL | Chi tiết 3 nguồn (OLTP/Lake/Warehouse), danh sách `discrepancies[]` | Xem chi tiết báo cáo chênh lệch khi MISMATCH _(ADMIN, MANAGER)_ |

---

## Tổng hợp nhanh

| Nhóm | Số endpoints |
|---|:---:|
| Xác thực & Phân quyền | 7 |
| Quản lý Giao dịch | 4 |
| Case Management & Audit | 8 |
| Data Engineering & Báo cáo | 7 |
| Idempotency, State & Reconciliation | 4 |
| **Tổng** | **30** |
