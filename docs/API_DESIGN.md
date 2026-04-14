# API Design – Transaction Management System

> **Base URL:** `https://api.tms.local/api/v1`  
> **Auth:** JWT Bearer Token (áp dụng trừ `/auth/login` và `/health`)  
> **Content-Type:** `application/json`

---

## Mục lục

0. [Tiện ích Hệ thống](#tiện-ích-hệ-thống)
1. [UC02 – Xác thực & Phân quyền](#uc02--xác-thực--phân-quyền)
2. [UC03 – Quản lý Giao dịch](#uc03--quản-lý-giao-dịch)
3. [UC04 – Quản lý Khoản vay](#uc04--quản-lý-khoản-vay)
4. [UC05 – Case Management & Audit](#uc05--case-management--audit)
5. [UC06 – Data Engineering & Báo cáo](#uc06--data-engineering--báo-cáo)
6. [UC07 – Idempotency, State & Reconciliation](#uc07--idempotency-state--reconciliation)
7. [Quy ước chung](#quy-ước-chung)

---

## Tiện ích Hệ thống

### GET /health
**HEALTH** – Kiểm tra trạng thái hệ thống.

| | |
|---|---|
| **Auth** | Không yêu cầu |
| **Roles** | Public |

**Response 200**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "timestamp": "2026-04-14T08:00:00Z"
}
```

---

## UC02 – Xác thực & Phân quyền

### POST /auth/login
**UC-AUTH-01** – Đăng nhập, nhận JWT token.

| | |
|---|---|
| **Auth** | Không yêu cầu |
| **Roles** | Tất cả |

**Request Body**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response 200**
```json
{
  "access_token": "string (JWT)",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "user_id": "uuid",
    "username": "string",
    "role": "OPERATOR | REVIEWER | MANAGER | ADMIN"
  }
}
```

**Response 401**
```json
{ "error": "INVALID_CREDENTIALS", "message": "Sai username hoặc mật khẩu." }
```

**Response 403**
```json
{ "error": "ACCOUNT_DISABLED", "message": "Tài khoản đã bị vô hiệu hóa." }
```

> *include* → UC-AUTH-02 (Xác thực JWT tạo ra và ký)  
> *extend* → UC-AUTH-09 (Ghi Audit Log mọi lần login, kể cả thất bại)

---

### POST /auth/logout
**UC-AUTH-03** – Đăng xuất, hủy phiên JWT.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | Tất cả |

**Response 200**
```json
{ "message": "Đăng xuất thành công." }
```

---

### GET /auth/me
**UC-AUTH-ME** – Lấy thông tin user hiện tại.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | Tất cả |

**Response 200**
```json
{
  "user_id": "uuid",
  "username": "duyhoang",
  "role": "OPERATOR",
  "is_active": true
}
```

---

### PATCH /auth/change-password
**UC-AUTH-04** – Đổi mật khẩu cá nhân.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | Tất cả |

**Request Body**
```json
{
  "current_password": "string",
  "new_password": "string",
  "confirm_password": "string"
}
```

**Response 200**
```json
{ "message": "Đổi mật khẩu thành công." }
```

**Response 400**
```json
{ "error": "PASSWORD_MISMATCH", "message": "Mật khẩu xác nhận không khớp." }
```

---

### GET /users
**UC-AUTH-08** – Xem danh sách người dùng.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | MANAGER, ADMIN |

**Query Params**

| Param | Type | Mô tả |
|---|---|---|
| `page` | int | Số trang (default: 1) |
| `limit` | int | Số bản ghi/trang (default: 20) |
| `role` | string | Lọc theo role |
| `is_active` | boolean | Lọc theo trạng thái |

**Response 200**
```json
{
  "total": 42,
  "page": 1,
  "limit": 20,
  "data": [
    {
      "user_id": "uuid",
      "username": "string",
      "full_name": "string",
      "role": "OPERATOR",
      "is_active": true,
      "created_at": "ISO8601"
    }
  ]
}
```

---

### POST /users
**UC-AUTH-05** – Tạo tài khoản người dùng mới.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ADMIN |

**Request Body**
```json
{
  "username": "string",
  "full_name": "string",
  "email": "string",
  "password": "string",
  "role": "OPERATOR | REVIEWER | MANAGER"
}
```

**Response 201**
```json
{
  "user_id": "uuid",
  "username": "string",
  "role": "OPERATOR",
  "created_at": "ISO8601"
}
```

> *include* → Gán role mặc định khi tạo

---

### PATCH /users/{user_id}/disable
**UC-AUTH-06** – Vô hiệu hóa tài khoản (Server kiểm tra `user_id != current_user_id` để tránh tự khóa).

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ADMIN |

**Response 200**
```json
{ "user_id": "uuid", "is_active": false, "message": "Tài khoản đã bị vô hiệu hóa." }
```

**Response 403**
```json
{ "error": "SELF_DISABLE_FORBIDDEN", "message": "Không thể tự vô hiệu hóa tài khoản của chính mình." }
```

---

### PATCH /users/{user_id}/enable
**UC-AUTH-ENABLE** – Khôi phục khóa tài khoản đã bị disable.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ADMIN |

**Response 200**
```json
{ "user_id": "uuid", "is_active": true, "message": "Tài khoản đã được mở khóa." }
```

---

### PATCH /users/{user_id}/role
**UC-AUTH-07** – Gán/thay đổi vai trò.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ADMIN |

**Request Body**
```json
{ "role": "OPERATOR | REVIEWER | MANAGER" }
```

**Response 200**
```json
{ "user_id": "uuid", "role": "REVIEWER", "updated_at": "ISO8601" }
```

---

### GET /users/{user_id}
**UC-AUTH-09** – Xem chi tiết 1 người dùng.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | MANAGER, ADMIN |

**Response 200**
```json
{
  "user_id": "uuid",
  "username": "string",
  "full_name": "string",
  "email": "string",
  "role": "REVIEWER",
  "is_active": true,
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

---

## UC03 – Quản lý Giao dịch

### POST /transactions/submit
**UC-TXN-01** – Gửi giao dịch demo. (Client gửi card thật qua HTTPS, Backend tự masking trước khi lưu DB. `idempotency_key` được tính bằng hash của `card_number + amount + merchant_id` thay vì toàn bộ payload).

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | OPERATOR |

**Request Body**
```json
{
  "card_number": "string (số thật chứa max digits, e.g. 4111111111111111)",
  "amount": 1500000,
  "merchant_id": "string",
  "txn_time": "ISO8601",
  "currency": "VND",
  "metadata": {
    "source_ip": "string",
    "device_id": "string"
  }
}
```

**Response 201 – Tạo mới**
```json
{
  "txn_id": "uuid",
  "idempotency_key": "string",
  "status": "APPROVED | REJECTED | MANUAL_REVIEW",
  "fraud_score": 0.25,
  "override_reason": "LOW_RISK | HIGH_RISK | MANUAL_REQUIRED | HIGH_VALUE",
  "processed_at": "ISO8601"
}
```

**Response 200 – Idempotent (đã xử lý trước đó)**
```json
{
  "txn_id": "uuid",
  "idempotency_key": "string",
  "status": "APPROVED",
  "fraud_score": 0.25,
  "message": "Giao dịch đã được xử lý trước đó. Trả về kết quả cũ.",
  "processed_at": "ISO8601"
}
```

**Response 400**
```json
{
  "error": "VALIDATION_ERROR",
  "details": [
    { "field": "amount", "message": "Amount phải lớn hơn 0." },
    { "field": "merchant_id", "message": "merchant_id không hợp lệ." }
  ]
}
```

> *include* → UC-TXN-02 (Validate input)  
> *include* → UC-TXN-03 (Kiểm tra Idempotency – SHA256 hash của card_number+amount+merchant_id)  
> *include* → UC-TXN-04 (AI Fraud Scoring)  
> *include* → UC-TXN-05 (Phân luồng: score ≤0.3 → APPROVED, ≤0.7 → MANUAL_REVIEW, >0.7 → REJECTED)  
> *extend* → UC-TXN-06 (Oracle Trigger: amount > 500,000,000 → MANUAL_REVIEW)  
> *extend* → UC-TXN-11 (Ghi Audit Log)

---

### GET /transactions
**UC-TXN-07** – Xem danh sách giao dịch. (Lọc `submitted_by` tự động cho OPERATOR)

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | OPERATOR, REVIEWER, MANAGER, ADMIN |

**Query Params**

| Param | Type | Mô tả |
|---|---|---|
| `page` | int | Số trang |
| `limit` | int | Số bản ghi/trang |
| `status` | string | `PENDING`, `APPROVED`, `REJECTED`, `MANUAL_REVIEW` |
| `from_date` | ISO8601 | Từ ngày |
| `to_date` | ISO8601 | Đến ngày |
| `merchant_id` | string | Lọc theo merchant |
| `min_amount` | number | Lọc theo số tiền |
| `max_amount` | number | Lọc theo số tiền |

**Response 200**
```json
{
  "total": 1500,
  "page": 1,
  "limit": 20,
  "data": [
    {
      "txn_id": "uuid",
      "card_number": "4111********1111",
      "amount": 1500000,
      "merchant_id": "string",
      "status": "APPROVED",
      "fraud_score": 0.12,
      "txn_time": "ISO8601",
      "processed_at": "ISO8601"
    }
  ]
}
```

---

### GET /transactions/{txn_id}
**UC-TXN-08** – Xem chi tiết một giao dịch.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | OPERATOR, REVIEWER, MANAGER, ADMIN |

**Response 200**
```json
{
  "txn_id": "uuid",
  "card_number": "4111********1111",
  "amount": 1500000,
  "currency": "VND",
  "merchant_id": "string",
  "status": "MANUAL_REVIEW",
  "fraud_score": 0.55,
  "override_reason": "MANUAL_REQUIRED",
  "idempotency_key": "sha256_hash",
  "txn_time": "ISO8601",
  "processed_at": "ISO8601",
  "metadata": {
    "source_ip": "192.168.1.1",
    "device_id": "string"
  },
  "state_history": [
    { "status": "PENDING", "changed_at": "ISO8601", "version": 1 },
    { "status": "MANUAL_REVIEW", "changed_at": "ISO8601", "version": 2 }
  ]
}
```

---

## UC04 – Quản lý Khoản vay

### POST /loans/submit
**UC-LOAN-01** – Gửi đơn vay demo tự động chấm điểm xếp hạng.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | OPERATOR |

**Request Body**
```json
{
  "customer_info": {
    "age": 30,
    "income": 20000000,
    "credit_history_length": 5
  },
  "loan_amount": 50000000,
  "term_months": 12
}
```

**Response 201**
```json
{
  "loan_id": "uuid",
  "idempotency_key": "string",
  "status": "APPROVED | REJECTED | MANUAL_REVIEW",
  "pd_score": 0.45,
  "processed_at": "ISO8601"
}
```

> *include* → UC-LOAN-03 (Validate input)  
> *include* → UC-LOAN-02 (AI PD Scoring)  
> *include* → UC-LOAN-04 (Phân luồng dựa trên `pd_score`)

---

### GET /loans
**UC-LOAN-05** – Xem danh sách đơn vay (Lọc `submitted_by` tự động cho OPERATOR).

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | Tất cả roles |

**Response 200**
```json
{
  "total": 500,
  "page": 1,
  "limit": 20,
  "data": [
    {
      "loan_id": "uuid",
      "loan_amount": 50000000,
      "status": "MANUAL_REVIEW",
      "pd_score": 0.45,
      "created_at": "ISO8601"
    }
  ]
}
```

---

### GET /loans/{loan_id}
**UC-LOAN-06** – Xem chi tiết một đơn vay.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | Tất cả roles |

**Response 200**
```json
{
  "loan_id": "uuid",
  "customer_info": {},
  "loan_amount": 50000000,
  "term_months": 12,
  "status": "MANUAL_REVIEW",
  "pd_score": 0.45,
  "created_at": "ISO8601"
}
```

---

## UC05 – Case Management & Audit

### GET /cases
**UC-CASE-01** – Xem danh sách case OPEN/ASSIGNED.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | REVIEWER, MANAGER, ADMIN |

**Query Params**

| Param | Type | Mô tả |
|---|---|---|
| `page` | int | Số trang |
| `limit` | int | Số bản ghi/trang |
| `status` | string | `OPEN`, `ASSIGNED`, `APPROVED`, `REJECTED` |
| `assigned_to` | uuid | Lọc theo reviewer |
| `from_date` | ISO8601 | Từ ngày |
| `to_date` | ISO8601 | Đến ngày |

**Response 200**
```json
{
  "total": 35,
  "page": 1,
  "limit": 20,
  "data": [
    {
      "case_id": "uuid",
      "txn_id": "uuid",
      "amount": 350000000,
      "fraud_score": 0.61,
      "status": "OPEN",
      "assigned_to": null,
      "created_at": "ISO8601"
    }
  ]
}
```

---

### POST /cases/{case_id}/assign
**UC-CASE-02** – Nhận case (Assign to me). Check Racing: `UPDATE ... WHERE assigned_to IS NULL`.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | REVIEWER |

**Response 200**
```json
{
  "case_id": "uuid",
  "status": "ASSIGNED",
  "assigned_to": "uuid",
  "assigned_at": "ISO8601"
}
```

**Response 409**
```json
{ "error": "CASE_ALREADY_ASSIGNED", "message": "Case này đã được nhận bởi người khác." }
```

> *include* → Ghi Audit Log sự kiện `CASE_ASSIGNED`

---

### GET /cases/{case_id}
**UC-CASE-03** – Xem chi tiết case.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | REVIEWER, MANAGER, ADMIN |

**Response 200**
```json
{
  "case_id": "uuid",
  "status": "ASSIGNED",
  "assigned_to": { "user_id": "uuid", "username": "string" },
  "transaction": {
    "txn_id": "uuid",
    "card_number": "4111********1111",
    "amount": 350000000,
    "merchant_id": "string",
    "fraud_score": 0.61,
    "txn_time": "ISO8601"
  },
  "state_history": [
    { "status": "OPEN", "changed_at": "ISO8601" },
    { "status": "ASSIGNED", "changed_at": "ISO8601", "actor": "string" }
  ],
  "created_at": "ISO8601"
}
```

---

### PATCH /cases/{case_id}/decision
**UC-CASE-04/05** – Cập nhật trạng thái duyệt / từ chối case. Kiểm tra trạng thái hiện tại (nếu terminal thì chặn) và Optimistic Locking (version của case hiện tại).

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | REVIEWER |

**Request Body**
```json
{
  "decision": "APPROVED | REJECTED",
  "note": "string (bắt buộc – lý do)",
  "version": 2
}
```

**Response 200**
```json
{
  "case_id": "uuid",
  "status": "APPROVED",
  "txn_id": "uuid",
  "txn_status": "APPROVED",
  "reviewed_by": "uuid",
  "reviewed_at": "ISO8601"
}
```

**Response 409**
```json
{ "error": "CONFLICT", "message": "Phiên bản dữ liệu không khớp. Case đã bị thay đổi bởi người khác." }
```

> *include* → UC-CASE-06 (Ghi chú lý do bắt buộc)  
> *include* → UC-CASE-07 (Cập nhật TRANSACTIONS_LIVE hoặc LOAN_APPLICATIONS)  
> *include* → UC-AUDIT-01 (Ghi Audit Log tự động)

---

### GET /audit-logs
**UC-AUDIT-02** – Xem Audit Log toàn hệ thống.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | MANAGER, ADMIN |

**Query Params**

| Param | Type | Mô tả |
|---|---|---|
| `page` | int | Số trang |
| `limit` | int | Số bản ghi/trang |
| `entity_type` | string | `TRANSACTION`, `LOAN`, `USER`, `CASE` |
| `entity_id` | uuid | ID của entity cụ thể |
| `actor_id` | uuid | Ai thực hiện |
| `event_type` | string | Loại sự kiện |
| `from_date` | ISO8601 | Từ ngày |
| `to_date` | ISO8601 | Đến ngày |

**Response 200**
```json
{
  "total": 3200,
  "page": 1,
  "limit": 20,
  "data": [
    {
      "log_id": "uuid",
      "event_type": "CASE_APPROVED",
      "entity_type": "TRANSACTION",
      "entity_id": "uuid",
      "actor_id": "uuid",
      "actor_name": "string",
      "detail": "string",
      "created_at": "ISO8601"
    }
  ]
}
```

---

### GET /audit-logs/transaction/{txn_id}/trace
**UC-AUDIT-03** – Truy vết toàn bộ lịch sử của một giao dịch.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | MANAGER, ADMIN |

**Response 200**
```json
{
  "txn_id": "uuid",
  "timeline": [
    {
      "event_type": "TXN_CREATED",
      "status_before": null,
      "status_after": "PENDING",
      "actor": "system",
      "detail": "Giao dịch mới nhận",
      "occurred_at": "ISO8601"
    },
    {
      "event_type": "FRAUD_SCORED",
      "fraud_score": 0.61,
      "actor": "AI_ENGINE",
      "detail": "fraud_score = 0.61 → MANUAL_REVIEW",
      "occurred_at": "ISO8601"
    },
    {
      "event_type": "CASE_ASSIGNED",
      "actor": "reviewer_01",
      "occurred_at": "ISO8601"
    },
    {
      "event_type": "CASE_APPROVED",
      "status_before": "MANUAL_REVIEW",
      "status_after": "APPROVED",
      "actor": "reviewer_01",
      "note": "Xác nhận hợp lệ sau xem xét",
      "occurred_at": "ISO8601"
    }
  ]
}
```

---

### GET /audit-logs/export
**UC-AUDIT-05** – Xuất báo cáo Audit Log ra file.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | MANAGER, ADMIN |

**Query Params**

| Param | Type | Mô tả |
|---|---|---|
| `format` | string | `csv` hoặc `pdf` |
| `from_date` | ISO8601 | Bắt buộc |
| `to_date` | ISO8601 | Bắt buộc |
| `entity_type` | string | Tùy chọn – lọc loại entity |

**Response 200**
> `Content-Type: text/csv` hoặc `application/pdf`  
> `Content-Disposition: attachment; filename="audit_log_{from}_{to}.csv"`

---

## UC06 – Data Engineering & Báo cáo

### GET /dashboard/summary
**UC-BI-01** – Dashboard tổng quan.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | MANAGER, ADMIN |

**Query Params**

| Param | Type | Mô tả |
|---|---|---|
| `from_date` | ISO8601 | Bắt buộc |
| `to_date` | ISO8601 | Bắt buộc |

**Response 200**
```json
{
  "total_transactions": 15042,
  "total_amount": 97500000000,
  "fraud_rate": 0.08,
  "cases_pending": 23,
  "cases_assigned": 7,
  "period": "custom",
  "trend": [
    { "date": "2026-04-01", "total": 320, "fraud": 25, "legit": 295 },
    { "date": "2026-04-02", "total": 415, "fraud": 31, "legit": 384 }
  ]
}
```

---

### GET /dashboard/fraud-chart
**UC-BI-02** – Biểu đồ tỷ lệ Fraud vs Legit (từ Warehouse/OLAP).

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | MANAGER, ADMIN |

**Query Params**

| Param | Type | Mô tả |
|---|---|---|
| `from_date` | ISO8601 | Bắt buộc |
| `to_date` | ISO8601 | Bắt buộc |
| `period` | string | (Tuỳ chọn) Thay đổi độ phân giải: `daily`, `weekly`, `monthly` |

**Response 200**
```json
{
  "source": "WAREHOUSE",
  "period": "daily",
  "data": {
    "fraud_count": 210,
    "fraud_amount": 8500000000,
    "legit_count": 2350,
    "legit_amount": 89000000000,
    "fraud_rate_count": 0.082,
    "fraud_rate_amount": 0.087
  },
  "breakdown": [
    { "date": "2026-04-01", "fraud": 48, "legit": 520 }
  ]
}
```

---

### GET /reports/transactions
**UC-BI-03** – Báo cáo giao dịch theo thời gian.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | MANAGER, ADMIN |

**Query Params**

| Param | Type | Mô tả |
|---|---|---|
| `from_date` | ISO8601 | Bắt buộc |
| `to_date` | ISO8601 | Bắt buộc |
| `period` | string | `daily`, `weekly`, `monthly`, `quarterly` |

**Response 200**
```json
{
  "period": "monthly",
  "rows": [
    {
      "period_label": "2026-03",
      "total_count": 8240,
      "total_amount": 45200000000,
      "approved_count": 7100,
      "rejected_count": 650,
      "manual_review_count": 490,
      "approved_rate": 0.862,
      "rejected_rate": 0.079
    }
  ]
}
```

> *extend* → UC-BI-04 (Xuất báo cáo)

---

### GET /reports/transactions/export
**UC-BI-04** – Xuất báo cáo giao dịch ra file PDF/CSV.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | MANAGER, ADMIN |

**Query Params**

| Param | Type | Mô tả |
|---|---|---|
| `format` | string | `csv` hoặc `pdf` |
| `from_date` | ISO8601 | Bắt buộc |
| `to_date` | ISO8601 | Bắt buộc |
| `period` | string | Tùy chọn gom nhóm: `daily`, `weekly`, `monthly` |

**Response 200**
> File download – `Content-Disposition: attachment`

---

### GET /datalake/structure
**UC-DATA-02** – Xem cấu trúc Data Lake.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ADMIN |

**Query Params**

| Param | Type | Mô tả |
|---|---|---|
| `page` | int | Số trang (mặc định 1) |
| `limit` | int | Số bản ghi/trang (mặc định 20) |

**Response 200**
```json
{
  "total": 1,
  "page": 1,
  "limit": 20,
  "base_path": "/datalake/raw/transaction_logs/",
  "directories": [
    {
      "date": "2026-04-01",
      "path": "/datalake/raw/transaction_logs/2026-04-01/",
      "file_count": 3,
      "total_size_mb": 12.4
    }
  ]
}
```

---

### GET /etl/logs
**UC-DATA-06** – Xem log ETL pipeline.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ADMIN |

**Query Params**

| Param | Type | Mô tả |
|---|---|---|
| `page` | int | Số trang |
| `limit` | int | Số bản ghi/trang |
| `status` | string | `SUCCESS`, `FAILED`, `RUNNING` |
| `from_date` | ISO8601 | Từ ngày |

**Response 200**
```json
{
  "total": 120,
  "data": [
    {
      "job_id": "uuid",
      "job_type": "DAILY_ETL",
      "status": "SUCCESS",
      "rows_extracted": 1540,
      "rows_loaded": 1538,
      "started_at": "ISO8601",
      "finished_at": "ISO8601",
      "error_message": null
    }
  ]
}
```

---

### GET /etl/logs/{job_id}
**UC-DATA-06** – Xem chi tiết log ETL pipeline theo ID.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ADMIN |

**Response 200**
```json
{
  "job_id": "uuid",
  "job_type": "DAILY_ETL",
  "status": "SUCCESS",
  "rows_extracted": 1540,
  "rows_loaded": 1538,
  "started_at": "ISO8601",
  "finished_at": "ISO8601",
  "error_message": null,
  "steps": [
    {
      "step_name": "EXTRACT",
      "status": "SUCCESS",
      "time_taken_ms": 1200
    },
    {
      "step_name": "TRANSFORM",
      "status": "SUCCESS",
      "time_taken_ms": 4500
    }
  ]
}
```

---

### POST /etl/trigger
**UC-DATA-03/04/05** – Trigger ETL Pipeline thủ công (Extract → Transform → Load).

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ADMIN |

**Request Body**
```json
{
  "date": "2026-04-02",
  "mode": "FULL | INCREMENTAL"
}
```

**Response 202**
```json
{
  "job_id": "uuid",
  "status": "RUNNING",
  "message": "ETL job đã được khởi động.",
  "started_at": "ISO8601"
}
```

> *include* → UC-DATA-04 (Transform: dedup, fill missing, GeoIP enrich, map Star Schema)  
> *include* → UC-DATA-05 (Load vào FACT_TRANSACTIONS + DIM tables)  
> *include* → UC-DATA-06 (Ghi log ETL)

---

## UC07 – Idempotency, State & Reconciliation

### GET /transactions/{txn_id}/states
**UC-STATE-05** – Xem lịch sử trạng thái (State History) của giao dịch.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | OPERATOR, ADMIN |

**Response 200**
```json
{
  "txn_id": "uuid",
  "current_status": "APPROVED",
  "current_version": 3,
  "history": [
    { "status": "PENDING",       "version": 1, "changed_at": "ISO8601", "actor": "system" },
    { "status": "MANUAL_REVIEW", "version": 2, "changed_at": "ISO8601", "actor": "AI_ENGINE" },
    { "status": "APPROVED",      "version": 3, "changed_at": "ISO8601", "actor": "reviewer_01" }
  ]
}
```

> Reflection của UC-STATE-01 (khởi PENDING v1), UC-STATE-02 (chuyển trạng thái), UC-STATE-03 (Optimistic Locking version++)

---

### POST /reconciliation/run
**UC-RECON-01** – Trigger chạy đối soát (Reconciliation).

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ADMIN |

**Request Body**
```json
{ "date": "2026-04-02" }
```

**Response 202**
```json
{
  "job_id": "uuid",
  "status": "RUNNING",
  "date": "2026-04-02",
  "message": "Reconciliation job đã bắt đầu.",
  "started_at": "ISO8601"
}
```

> *include* → UC-RECON-02 (So khớp COUNT(*) và SUM(amount) giữa OLTP, Data Lake, Warehouse)  
> *extend* → UC-RECON-03 (Tạo báo cáo MISMATCH nếu phát hiện chênh lệch)

---

### GET /reconciliation/jobs
**UC-DATA-09** – Xem danh sách kết quả đối soát.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ADMIN, MANAGER |

**Query Params**

| Param | Type | Mô tả |
|---|---|---|
| `page` | int | Số trang |
| `limit` | int | Số bản ghi |
| `status` | string | `MATCH`, `MISMATCH`, `RUNNING`, `FAILED` |
| `from_date` | ISO8601 | Từ ngày |

**Response 200**
```json
{
  "total": 30,
  "data": [
    {
      "job_id": "uuid",
      "date": "2026-04-02",
      "status": "MISMATCH",
      "oltp_count": 1540,
      "lake_count": 1538,
      "warehouse_count": 1535,
      "oltp_sum": 9800000000,
      "lake_sum": 9750000000,
      "warehouse_sum": 9750000000,
      "mismatch_detail": "OLTP vs Lake: delta_count=2, delta_amount=50000000",
      "error_message": null,
      "run_at": "ISO8601"
    },
    {
      "job_id": "uuid-failed",
      "date": "2026-04-03",
      "status": "FAILED",
      "error_message": "Database connection timeout timeout during extraction.",
      "run_at": "ISO8601"
    }
  ]
}
```

---

### GET /reconciliation/jobs/{job_id}
**UC-RECON-03** – Xem chi tiết báo cáo chênh lệch.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ADMIN, MANAGER |

**Response 200**
```json
{
  "job_id": "uuid",
  "date": "2026-04-02",
  "status": "MISMATCH",
  "error_message": null,
  "sources": {
    "oltp":      { "count": 1540, "sum_amount": 9800000000 },
    "datalake":  { "count": 1538, "sum_amount": 9750000000 },
    "warehouse": { "count": 1535, "sum_amount": 9750000000 }
  },
  "discrepancies": [
    {
      "type": "COUNT_MISMATCH",
      "source_a": "OLTP",
      "source_b": "DATALAKE",
      "delta": 2
    },
    {
      "type": "AMOUNT_MISMATCH",
      "source_a": "OLTP",
      "source_b": "DATALAKE",
      "delta": 50000000
    }
  ],
  "run_at": "ISO8601"
}
```

---

## Quy ước chung

### Mã lỗi chuẩn (Error Codes)

| HTTP | Error Code | Ý nghĩa |
|---|---|---|
| 400 | `VALIDATION_ERROR` | Dữ liệu đầu vào không hợp lệ |
| 401 | `UNAUTHORIZED` | Chưa đăng nhập / JWT hết hạn |
| 403 | `FORBIDDEN` | Không có quyền thực hiện |
| 404 | `NOT_FOUND` | Resource không tồn tại |
| 409 | `CONFLICT` | Trùng lặp dữ liệu / Optimistic Lock conflict |
| 422 | `UNPROCESSABLE` | Dữ liệu hợp lệ nhưng không thể xử lý |
| 429 | `RATE_LIMITED` | Vượt quá giới hạn request |
| 500 | `INTERNAL_ERROR` | Lỗi server nội bộ |

**Cấu trúc lỗi chuẩn:**
```json
{
  "error": "FORBIDDEN",
  "message": "Bạn không có quyền thực hiện hành động này.",
  "request_id": "uuid"
}
```

### Phân quyền theo Endpoint

| Module | OPERATOR | REVIEWER | MANAGER | ADMIN |
|---|:---:|:---:|:---:|:---:|
| Auth (login/logout/change-pw) | ✓ | ✓ | ✓ | ✓ |
| User Management | – | – | Chỉ đọc | Full |
| Transaction Submit | ✓ | – | – | – |
| Transaction View | ✓ | ✓ | ✓ | ✓ |
| Transaction Update Status | – | ✓ | – | – |
| Case Management | – | Full | Chỉ đọc | Chỉ đọc |
| Audit Log | – | – | ✓ | ✓ |
| Dashboard / BI | – | – | ✓ | ✓ |
| Loan Submit | ✓ | – | – | – |
| ETL / Data Lake | – | – | – | ✓ |
| Reconciliation | – | – | Chỉ đọc | Full |

### Phân luồng Fraud Score (UC-TXN-05)

| `fraud_score` | Kết quả |
|---|---|
| `≤ 0.30` | `APPROVED` (tự động) |
| `0.30 < score ≤ 0.70` | `MANUAL_REVIEW` (tạo case) |
| `> 0.70` | `REJECTED` (tự động) |
| Bất kỳ, `amount > 500,000,000` | Override → `MANUAL_REVIEW` (Oracle Trigger) |
