# API Design – Hệ thống Phân tích Rủi ro và Đánh giá Tài chính (HPTRRĐGTC)

> **Base URL:** `https://api.hptrrđgtc.local/api/v1`
> **Auth:** JWT Bearer Token (trừ endpoint `/auth/login` và `/auth/refresh`)
> **Content-Type:** `application/json`

---

## CHANGELOG – Thay đổi so với phiên bản cũ

| # | Cũ | Mới |
|---|---|---|
| 1 | `POST /loans/submit` (body: `applicant_id`, `credit_score`, `employment_type`) | `POST /loans` (body: `customer_id`, `person_age`, `person_income`, `loan_grade`, v.v.) |
| 2 | Thiếu `PATCH /loans/{loan_id}/decision` | Thêm — MANAGER/ADMIN phê duyệt/từ chối |
| 3 | Thiếu `POST /loans/simulate` | Thêm — AI scoring không lưu DB |
| 4 | `GET /loans` — chỉ MANAGER, ADMIN | Thêm OPERATOR (chỉ thấy đơn của mình) |
| 5 | Thiếu `POST /auth/refresh` | Thêm |
| 6 | `GET /transactions/{txn_id}/states` | `GET /transactions/{txn_id}/state-history` |
| 7 | `POST /etl/trigger` | `POST /etl/run` |
| 8 | Fraud threshold: `≤0.30 → APPROVED`, `>0.70 → REJECTED` | `<0.35 → APPROVED`, `≥0.65 → REJECTED` |
| 9 | Duplicate `GET /users/{user_id}` section | Removed duplicate |
| 10 | `POST /transactions/submit` — chỉ OPERATOR | OPERATOR, MANAGER, ADMIN |
| 11 | Thiếu UC08 SSE Stream section | Thêm |
| 12 | Permissions table: Loan Submit chỉ OPERATOR; Transaction States chỉ OPERATOR/ADMIN | Cập nhật đúng |
| 13 | Loan decision: không có SoD check | Thêm: submitter != approver (4-eyes) → 403 |
| 14 | Case decide: OPEN case có thể bị quyết định trực tiếp | Case phải ASSIGNED trước → 409 nếu OPEN |
| 15 | Case decide: ADMIN bị chặn như REVIEWER | ADMIN bypass giống MANAGER |
| 16 | REVIEWER list cases: thấy tất cả hoặc chỉ của mình (sai cả hai) | Thấy OPEN queue + cases của mình (compound OR query) |
| 17 | Transaction state-history: OPERATOR xem được của ai cũng được | OPERATOR chỉ xem giao dịch do mình submit |
| 18 | `CaseDecideRequest` body field: `note` | `decision_note` (khớp với Pydantic schema thực tế) |
| 19 | `TransactionSubmitResponse`: thiếu `amount`, `currency_code`, `message`, `case_id` | Thêm đủ fields |
| 20 | Thiếu role ANALYST | Thêm role ANALYST với module phân tích riêng (UC09) |
| 21 | Tên hệ thống: "Transaction Management System" | Đổi tên thành "Hệ thống Phân tích Rủi ro và Đánh giá Tài chính" |
| 22 | Thiếu SoD check trong PATCH /cases/{id}/decision | Thêm: reviewer không quyết định case cho giao dịch do mình submit → 403 |
| 23 | Thiếu AuditLog trong reconciliation resolve và ETL run | Thêm đầy đủ |
| 24 | `txn_time` không validate future date | Thêm validator: từ chối txn_time > now + 5 phút |
| 25 | CORS allow_methods/allow_headers quá rộng trên production | Tighten cho production env |

---

## Mục lục

1. [Hệ thống & Health](#hệ-thống--health)
2. [UC02 – Xác thực & Phân quyền](#uc02--xác-thực--phân-quyền)
3. [UC03 – Quản lý Giao dịch](#uc03--quản-lý-giao-dịch)
4. [UC04 – Quản lý Đơn Vay](#uc04--quản-lý-đơn-vay)
5. [UC05 – Case Management & Audit](#uc05--case-management--audit)
6. [UC06 – Data Engineering & Báo cáo](#uc06--data-engineering--báo-cáo)
7. [UC07 – Idempotency, State & Reconciliation](#uc07--idempotency-state--reconciliation)
8. [UC08 – Real-time Stream (SSE)](#uc08--real-time-stream-sse)
9. [UC09 – Analyst Module](#uc09--analyst-module)
10. [Quy ước chung](#quy-ước-chung)

---

## Hệ thống & Health

### GET /health
Kiểm tra trạng thái hệ thống, phục vụ load balancer & health probes.

| | |
|---|---|
| **Auth** | Không yêu cầu |
| **Roles** | Tất cả |

**Response 200**
```json
{
  "status": "ok | degraded | down",
  "version": "1.0.0",
  "environment": "production | staging | development",
  "timestamp": "ISO8601",
  "checks": {
    "database": "ok | degraded | down",
    "fraud_model": "ok | degraded | down"
  }
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
  "refresh_token": "string (JWT)",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user_id": "uuid",
  "username": "string",
  "full_name": "string",
  "role": "OPERATOR | REVIEWER | MANAGER | ADMIN"
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
**UC-AUTH-10** – Xem thông tin tài khoản đang đăng nhập.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | Tất cả |

**Response 200**
```json
{
  "user_id": "uuid",
  "username": "string",
  "full_name": "string",
  "role": "OPERATOR | REVIEWER | MANAGER | ADMIN",
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
  "new_password": "string (min 8 ký tự)",
  "confirm_password": "string (phải khớp new_password)"
}
```

**Response 200**
```json
{ "message": "Đổi mật khẩu thành công." }
```

---

### POST /auth/refresh *(Mới – ~~Cũ: thiếu~~)*
**UC-AUTH-13** – Lấy access token mới bằng refresh token.

| | |
|---|---|
| **Auth** | Không yêu cầu Bearer |
| **Roles** | Tất cả |

**Request Body**
```json
{ "refresh_token": "string (JWT refresh token)" }
```

**Response 200**
```json
{
  "access_token": "string (JWT)",
  "refresh_token": "string (JWT – rotated)",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**Response 401**
```json
{ "error": "INVALID_TOKEN", "message": "Refresh token không hợp lệ hoặc đã hết hạn." }
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

### GET /users/{user_id}
**UC-AUTH-11** – Xem chi tiết thông tin một người dùng.

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
  "role": "OPERATOR",
  "is_active": true,
  "created_at": "ISO8601"
}
```

**Response 404**
```json
{ "error": "NOT_FOUND", "message": "Người dùng không tồn tại." }
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

> ⚠️ ADMIN không được tự vô hiệu hóa chính mình (Issue #5 – Audit).

**Response 200**
```json
{ "user_id": "uuid", "is_active": false, "message": "Tài khoản đã bị vô hiệu hóa." }
```

**Response 403**
```json
{ "error": "FORBIDDEN", "message": "Không thể tự vô hiệu hóa tài khoản của chính mình." }
```

---

### PATCH /users/{user_id}/enable
**UC-AUTH-12** – Kích hoạt lại tài khoản đã bị vô hiệu hóa.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ADMIN |

**Response 200**
```json
{ "user_id": "uuid", "is_active": true, "message": "Tài khoản đã được kích hoạt." }
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

## UC03 – Quản lý Giao dịch

### POST /transactions/submit
**UC-TXN-01** – Gửi giao dịch vào hệ thống.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | OPERATOR |

> **OPERATOR = core banking system của ngân hàng** — không phải internal staff.
> Server tự mask `card_number` — client gửi raw, không được gửi số thẻ đã mask sẵn.

**Request Body**
```json
{
  "card_number": "string (raw — server tự mask và hash)",
  "customer_id": "uuid",
  "merchant_id": "uuid",
  "channel_id": "integer",
  "amount": 1500.50,
  "currency_code": "USD",
  "txn_time": "ISO8601",
  "source_ip": "string",
  "idempotency_key": "uuid (client tự tạo để dedup)"
}
```

**Response 201 – Tạo mới**
```json
{
  "txn_id": "uuid",
  "status": "APPROVED | REJECTED | MANUAL_REVIEW",
  "fraud_score": 0.40,
  "decision": "APPROVED | REJECTED | MANUAL_REVIEW",
  "amount": 1500.50,
  "currency_code": "USD",
  "created_at": "ISO8601",
  "message": "string",
  "case_id": "uuid | null"
}
```

**Response 200 – Idempotent (đã xử lý trước đó)**
```json
{
  "txn_id": "uuid",
  "status": "APPROVED",
  "fraud_score": 0.30,
  "message": "Giao dịch đã được xử lý trước đó. Trả về kết quả cũ."
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
> *include* → UC-TXN-03 (Kiểm tra Idempotency Key)
> *include* → UC-TXN-04 (AI Fraud Scoring – Random Forest 10 cây)
> *include* → UC-TXN-05 (Phân luồng: **score < 0.35 → APPROVED**, **0.35–0.65 → MANUAL_REVIEW**, **≥ 0.65 → REJECTED**) *(~~Cũ: ≤0.3 / ≤0.7 / >0.7~~)*
> *extend* → UC-TXN-06 (amount > 500,000,000 → override MANUAL_REVIEW)
> *extend* → UC-TXN-11 (Ghi Audit Log)

---

### GET /transactions
**UC-TXN-07** – Xem danh sách giao dịch.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | OPERATOR, REVIEWER, MANAGER, ADMIN |

> ⚠️ OPERATOR chỉ thấy giao dịch do chính mình gửi (`submitted_by` tự động filter).
> REVIEWER thấy tất cả giao dịch (không bị lọc).

**Query Params**

| Param | Type | Mô tả |
|---|---|---|
| `page` | int | Số trang |
| `limit` | int | Số bản ghi/trang |
| `status` | string | `APPROVED`, `REJECTED`, `MANUAL_REVIEW` |
| `customer_id` | uuid | Lọc theo customer |
| `merchant_id` | uuid | Lọc theo merchant |
| `from_date` | ISO8601 | Từ ngày (txn_time) |
| `to_date` | ISO8601 | Đến ngày (txn_time) |
| `min_amount` | number | Lọc theo số tiền tối thiểu |
| `max_amount` | number | Lọc theo số tiền tối đa |

**Response 200**
```json
{
  "total": 1500,
  "page": 1,
  "limit": 20,
  "data": [
    {
      "txn_id": "uuid",
      "customer_id": "uuid",
      "merchant_id": "uuid",
      "channel_id": 1,
      "submitted_by": "uuid",
      "card_number_masked": "4111********1111",
      "amount": 1500.50,
      "currency_code": "USD",
      "txn_time": "ISO8601",
      "status": "APPROVED",
      "fraud_score": 0.30,
      "reason_code": "HIGH_FRAUD_SCORE | null",
      "override_reason": "string | null",
      "created_at": "ISO8601",
      "fraud_detail": null
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

> ⚠️ **OPERATOR** chỉ xem được giao dịch do **chính mình submit**. Truy cập giao dịch của người khác → 403.

**Response 200**
```json
{
  "txn_id": "uuid",
  "customer_id": "uuid",
  "merchant_id": "uuid",
  "channel_id": 1,
  "submitted_by": "uuid",
  "card_number_masked": "4111********1111",
  "amount": 1500.50,
  "currency_code": "USD",
  "txn_time": "ISO8601",
  "status": "MANUAL_REVIEW",
  "fraud_score": 0.50,
  "reason_code": "HIGH_FRAUD_SCORE | null",
  "override_reason": "string | null",
  "created_at": "ISO8601",
  "fraud_detail": {
    "fraud_score": 0.50,
    "decision": "MANUAL_REVIEW",
    "reject_threshold": 0.65,
    "review_threshold": 0.35,
    "model_version": "rf_v1",
    "top_risk_factors": ["amt_z_score", "geo_distance"]
  }
}
```

> ~~`PATCH /transactions/{txn_id}/status`~~ — **Đã gỡ bỏ** theo Audit Issue #3. Mọi việc duyệt/từ chối phải đi qua Case flow (`PATCH /cases/{case_id}/decision`) để đảm bảo Audit Trail.

---

## UC04 – Quản lý Đơn Vay *(~~Cũ: "Hỗ trợ Quyết định Cho vay (Loan Simulator)"~~)*

### POST /loans *(~~Cũ: POST /loans/submit~~)*
**UC-LOAN-01** – Tạo đơn vay mới, trả về trạng thái PENDING kèm PD Score.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | OPERATOR |

> **OPERATOR = core banking system của ngân hàng** — không phải internal staff.
> OPERATOR chỉ thấy đơn do mình tạo khi gọi `GET /loans`.
> Body cũ (`applicant_id`, `credit_score`, `employment_type`) đã bị thay thế hoàn toàn.

**Request Body**
```json
{
  "customer_id": "uuid",
  "principal_amount": 25000.00,
  "currency_code": "USD",
  "interest_rate": 0.12,
  "term_months": 36,
  "purpose": "string",
  "person_age": 30,
  "person_income": 75000.00,
  "person_home_ownership": "RENT | MORTGAGE | OWN | OTHER",
  "person_emp_length": 5,
  "loan_intent": "PERSONAL | EDUCATION | MEDICAL | VENTURE | HOMEIMPROVEMENT | DEBTCONSOLIDATION",
  "loan_grade": "A | B | C | D | E | F | G",
  "cb_person_default_on_file": "Y | N",
  "cb_person_cred_hist_length": 10
}
```

> Các field AI (`person_age` trở đi) là tùy chọn. Nếu đủ → PD Score được tính ngay.
> *(~~Cũ: `applicant_id`, `credit_score`, `employment_type`~~)*

**Response 201**
```json
{
  "loan_id": "uuid",
  "customer_id": "uuid",
  "status": "PENDING",
  "principal_amount": 25000.00,
  "currency_code": "USD",
  "interest_rate": 0.12,
  "term_months": 36,
  "purpose": "string",
  "pd_score": 0.18,
  "risk_level": "LOW | MEDIUM | HIGH",
  "submitted_by": "uuid",
  "created_at": "ISO8601",
  "version": 1
}
```

> *include* → Kiểm tra `customer_id` tồn tại trong hệ thống
> *include* → Tính PD Score nếu đủ AI features (XGBoost model)
> *extend* → Ghi Audit Log: LOAN_APPLIED

---

### POST /loans/simulate *(Mới)*
**UC-LOAN-SIM** – Mô phỏng AI Scoring mà **không tạo đơn vay thực**.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | OPERATOR, MANAGER, ADMIN |

**Request Body**
```json
{
  "person_age": 30,
  "person_income": 75000.00,
  "person_home_ownership": "RENT",
  "person_emp_length": 5,
  "loan_intent": "PERSONAL",
  "loan_grade": "C",
  "loan_amnt": 25000.00,
  "loan_int_rate": 12.0,
  "cb_person_default_on_file": "N",
  "cb_person_cred_hist_length": 10
}
```

> `loan_int_rate` là % (ví dụ: `12.0` tương đương 12%), khác với `interest_rate` trong `POST /loans` (decimal `0.12`).

**Response 200**
```json
{
  "pd_score": 0.28,
  "risk_level": "MEDIUM",
  "top_risk_factors": [
    { "feature": "debt_burden", "importance": 0.26 },
    { "feature": "loan_percent_income", "importance": 0.12 }
  ],
  "model_version": "loan_v6"
}
```

---

### GET /loans
**UC-LOAN-02** – Xem danh sách hồ sơ vay.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | OPERATOR, MANAGER, ADMIN *(~~Cũ: chỉ MANAGER, ADMIN~~)* |

> OPERATOR chỉ thấy đơn do mình tạo (`submitted_by` tự động filter).

**Query Params**

| Param | Type | Mô tả |
|---|---|---|
| `page` | int | Số trang |
| `limit` | int | Số bản ghi/trang |
| `status` | string | `PENDING`, `APPROVED`, `REJECTED` |
| `customer_id` | uuid | Lọc theo khách hàng |

**Response 200**
```json
{
  "data": [
    {
      "loan_id": "uuid",
      "customer_id": "uuid",
      "principal_amount": 25000.00,
      "status": "PENDING",
      "pd_score": 0.18,
      "risk_level": "LOW",
      "submitted_by": "uuid",
      "created_at": "ISO8601"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 120,
    "total_pages": 6
  }
}
```

---

### GET /loans/{loan_id}
**UC-LOAN-03** – Xem chi tiết hồ sơ vay.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | OPERATOR (chỉ đơn của mình), MANAGER, ADMIN |

**Response 200**
```json
{
  "loan_id": "uuid",
  "customer_id": "uuid",
  "principal_amount": 25000.00,
  "currency_code": "USD",
  "interest_rate": 0.12,
  "term_months": 36,
  "purpose": "string",
  "status": "APPROVED",
  "pd_score": 0.18,
  "risk_level": "LOW",
  "monthly_payment": 830.05,
  "outstanding_balance": 25000.00,
  "maturity_date": "2029-04-19",
  "disbursed_at": "ISO8601",
  "reviewed_by": "uuid",
  "reviewed_at": "ISO8601",
  "review_note": "string",
  "submitted_by": "uuid",
  "created_at": "ISO8601",
  "version": 2
}
```

---

### PATCH /loans/{loan_id}/decision *(Mới)*
**UC-LOAN-04** – MANAGER/ADMIN phê duyệt hoặc từ chối đơn vay.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | MANAGER, ADMIN |

> `version` bắt buộc để kích hoạt **Optimistic Locking** — tránh hai người ghi đè nhau.
> Khi APPROVE: hệ thống tự tính `monthly_payment`, `outstanding_balance`, `maturity_date`.
> **SoD (4-eyes principle):** Người phê duyệt không được là người đã tạo đơn. Vi phạm → 403. *(Mới – ~~Cũ: không có check~~)*

**Request Body**
```json
{
  "decision": "APPROVE | REJECT",
  "review_note": "string (bắt buộc)",
  "version": 1
}
```

**Response 200**
```json
{
  "loan_id": "uuid",
  "status": "APPROVED | REJECTED",
  "monthly_payment": 830.05,
  "maturity_date": "2029-04-19",
  "reviewed_by": "uuid",
  "reviewed_at": "ISO8601",
  "version": 2
}
```

**Response 403 – SoD vi phạm**
```json
{ "error": "FORBIDDEN", "message": "Không thể phê duyệt khoản vay do chính mình tạo ra (nguyên tắc phân tách trách nhiệm – 4-eyes principle)." }
```

**Response 409 – Loan không ở PENDING**
```json
{ "error": "CONFLICT", "message": "Khoản vay đang ở trạng thái 'APPROVED', không thể thay đổi." }
```

**Response 409 – Optimistic Lock conflict**
```json
{ "error": "OPTIMISTIC_LOCK_ERROR", "message": "Dữ liệu đã được cập nhật bởi người khác. Vui lòng tải lại." }
```

> *include* → **Kiểm tra SoD**: `submitted_by != actor_user_id` → 403 nếu vi phạm
> *include* → Optimistic Locking: so sánh `version` request với DB
> *include* → Tính monthly_payment khi APPROVE (công thức amortisation PMT)
> *extend* → Ghi Audit Log: LOAN_APPROVED / LOAN_REJECTED

---

## UC05 – Case Management & Audit

### GET /cases
**UC-CASE-01** – Xem danh sách case.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | REVIEWER, MANAGER, ADMIN |

> **REVIEWER** thấy: tất cả OPEN cases (queue chưa ai nhận) + cases được giao cho mình. Compound query: `(assigned_to IS NULL) OR (assigned_to = reviewer_id)`. *(~~Cũ: chỉ thấy cases của mình → không thể nhận việc mới~~)*
> MANAGER/ADMIN thấy tất cả. Nếu REVIEWER truyền `assigned_to` của reviewer khác → 403.

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

> ⚠️ Dùng `WHERE assigned_to IS NULL` để chặn race condition (Issue #9 – Audit).

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
**UC-CASE-04/05** – Duyệt hoặc từ chối case (Approve/Reject gộp chung).

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | REVIEWER, MANAGER, ADMIN *(~~Cũ: REVIEWER, MANAGER — ADMIN bị bỏ sót~~)* |

> Gộp `approve` và `reject` thành một endpoint. Dùng `PATCH` (partial update).
> Tham số `version` bắt buộc để kích hoạt **Optimistic Locking** — tránh hai reviewer ghi đè nhau.
> **Case phải ở trạng thái ASSIGNED** trước khi quyết định. Case OPEN → 409. *(Mới – ~~Cũ: không check~~)*
> REVIEWER: chỉ quyết định case được giao cho mình. MANAGER/ADMIN: override bất kỳ case ASSIGNED nào.
> **SoD (4-eyes principle):** REVIEWER không được quyết định case cho giao dịch do chính mình submit. Vi phạm → 403. MANAGER/ADMIN được phép override.

**Request Body**
```json
{
  "decision": "APPROVE | REJECT",
  "decision_note": "string (bắt buộc – tối thiểu 10 ký tự)",
  "version": 1
}
```

**Response 200**
```json
{
  "case_id": "uuid",
  "status": "APPROVED | REJECTED",
  "txn_id": "uuid",
  "txn_status": "APPROVED | REJECTED",
  "reviewed_by": "uuid",
  "reviewed_at": "ISO8601",
  "version": 2
}
```

**Response 409 – Case chưa được assign**
```json
{ "error": "CONFLICT", "message": "Case chưa được nhận (status = OPEN). Hãy assign case trước khi đưa ra quyết định." }
```

**Response 409 – Optimistic Lock conflict**
```json
{ "error": "OPTIMISTIC_LOCK_ERROR", "message": "Case đã được cập nhật bởi người khác. Vui lòng tải lại và thử lại." }
```

**Response 403 – REVIEWER quyết định case không phải của mình**
```json
{ "error": "FORBIDDEN", "message": "Case này không được giao cho bạn." }
```

> *include* → UC-CASE-06 (Ghi chú lý do bắt buộc)
> *include* → UC-CASE-07 (Cập nhật transactions_live.status)
> *include* → UC-AUDIT-01 (Ghi Audit Log tự động)

---

### GET /audit-logs
**UC-AUDIT-02** – Xem Audit Log toàn hệ thống.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | MANAGER, ADMIN |

> Sorted DESC by event_ts.

**Query Params**

| Param | Type | Mô tả |
|---|---|---|
| `page` | int | Số trang |
| `limit` | int | Số bản ghi/trang |
| `entity_type` | string | `TRANSACTION`, `LOAN`, `USER`, `CASE` |
| `actor_user_id` | uuid | Ai thực hiện *(~~Cũ: actor_id~~)* |
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
      "actor_user_id": "uuid",
      "actor_name": "string",
      "event_ts": "ISO8601"
    }
  ]
}
```

---

### GET /audit-logs/entities/{entity_type}/{entity_id} *(Mới – ~~Cũ: /audit-logs/transactions/{txn_id}/trace không tồn tại~~)*
**UC-AUDIT-03** – Lịch sử audit đầy đủ cho một entity cụ thể (transaction, loan, case, user...).

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | MANAGER, ADMIN |

> Sorted ASC by event_ts.

**Path Params**

| Param | Type | Mô tả |
|---|---|---|
| `entity_type` | string | `TRANSACTION`, `LOAN`, `CASE`, `USER` |
| `entity_id` | uuid | ID của entity |

**Query Params**

| Param | Type | Mô tả |
|---|---|---|
| `page` | int | Số trang (default: 1) |
| `limit` | int | Số bản ghi/trang (default: 50, max: 200) |

**Response 200**
```json
{
  "total": 4,
  "page": 1,
  "limit": 50,
  "data": [
    {
      "log_id": "uuid",
      "event_type": "TXN_CREATED",
      "entity_type": "TRANSACTION",
      "entity_id": "uuid",
      "actor_user_id": "uuid",
      "actor_name": "system",
      "event_ts": "ISO8601",
      "detail": {}
    }
  ]
}
```

---

### GET /audit-logs/{log_id} *(Mới)*
**UC-AUDIT-04** – Xem chi tiết một audit log entry.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | MANAGER, ADMIN |

**Response 200**
```json
{
  "log_id": "uuid",
  "event_type": "CASE_APPROVED",
  "entity_type": "TRANSACTION",
  "entity_id": "uuid",
  "actor_user_id": "uuid",
  "actor_name": "string",
  "event_ts": "ISO8601",
  "detail": {}
}
```

**Response 404**
```json
{ "error": "NOT_FOUND", "message": "Audit log entry không tồn tại." }
```

---

## UC06 – Data Engineering & Báo cáo

### GET /dashboard/summary
**UC-BI-01** – Dashboard tổng quan.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | MANAGER, ADMIN |

> No query params. Returns current snapshot as of the moment of request.

**Response 200**
```json
{
  "transactions": {
    "total": 15042,
    "approved": 10530,
    "rejected": 4512,
    "manual_review": 0,
    "pending": 0,
    "today": 320,
    "this_week": 2100
  },
  "fraud": {
    "avg_fraud_score": 0.42,
    "rejection_rate": 0.30,
    "manual_review_rate": 0.40
  },
  "cases": {
    "total_open": 23,
    "total_assigned": 7,
    "decided_today": 5
  },
  "loans": {
    "total_pending": 12,
    "total_approved": 80,
    "total_rejected": 8
  },
  "as_of": "ISO8601"
}
```

---

### GET /dashboard/fraud-trend *(~~Cũ: /dashboard/fraud-chart — không tồn tại trong code~~)*
**UC-BI-02** – Xu hướng Fraud theo ngày.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | MANAGER, ADMIN |

**Query Params**

| Param | Type | Mô tả |
|---|---|---|
| `days` | int | Số ngày nhìn lại (1–90, default: 30) |

**Response 200**
```json
{
  "period": "daily",
  "lookback_days": 30,
  "data": [
    {
      "period_label": "2026-04-01",
      "period_start": "ISO8601",
      "total_txn": 320,
      "approved": 224,
      "rejected": 64,
      "manual_review": 32,
      "fraud_rate": 0.30
    }
  ],
  "as_of": "ISO8601"
}
```

---

### GET /reports/transactions *(~~Cũ: aggregated rows only — replaced with raw transaction export~~)*
**UC-BI-03** – Xuất danh sách giao dịch thô (JSON hoặc CSV).

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | MANAGER, ADMIN |

> Max 5000 rows. CSV returns `Content-Type: text/csv` with UTF-8 BOM.

**Query Params**

| Param | Type | Mô tả |
|---|---|---|
| `format` | string | `json` (default) hoặc `csv` |
| `status` | string | Lọc theo trạng thái |
| `from_date` | ISO8601 | Từ ngày |
| `to_date` | ISO8601 | Đến ngày |

**CSV columns:** `txn_id`, `customer_id`, `merchant_id`, `channel_id`, `card_number_masked`, `amount`, `currency_code`, `txn_time`, `status`, `fraud_score`, `reason_code`, `created_at`

**Response 200 (JSON)**
```json
[
  {
    "txn_id": "uuid",
    "customer_id": "uuid",
    "merchant_id": "uuid",
    "channel_id": 1,
    "card_number_masked": "411111******1111",
    "amount": 1500.50,
    "currency_code": "USD",
    "txn_time": "ISO8601",
    "status": "APPROVED",
    "fraud_score": 0.30,
    "reason_code": null,
    "created_at": "ISO8601"
  }
]
```

---

### GET /reports/fraud *(Mới)*
**UC-BI-04** – Xuất tổng hợp Fraud theo ngày (JSON hoặc CSV).

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | MANAGER, ADMIN |

**Query Params**

| Param | Type | Mô tả |
|---|---|---|
| `format` | string | `json` (default) hoặc `csv` |
| `from_date` | ISO8601 | Từ ngày |
| `to_date` | ISO8601 | Đến ngày |

**CSV columns:** `date`, `total_txn`, `approved`, `rejected`, `manual_review`, `pending`, `fraud_rate`, `avg_fraud_score`

**Response 200 (JSON)**
```json
[
  {
    "date": "2026-04-01",
    "total_txn": 320,
    "approved": 224,
    "rejected": 64,
    "manual_review": 32,
    "pending": 0,
    "fraud_rate": 0.30,
    "avg_fraud_score": 0.45
  }
]
```

---

### POST /datalake/ingest *(Mới – ~~Cũ: GET /datalake/structure không tồn tại trong code~~)*
**UC-DATA-02** – Ingest external data snapshot vào Data Lake.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ADMIN |

**Request Body**
```json
{
  "snapshot_date": "2026-04-01",
  "source_label": "string (min2, max100)",
  "records": [ {} ]
}
```

> `records`: 1–10,000 items.

**Response 201**
```json
{
  "snapshot_id": "uuid",
  "snapshot_type": "EXTERNAL_INGEST",
  "snapshot_date": "2026-04-01",
  "job_id": null,
  "source_label": "string",
  "record_count": 500,
  "total_amount": 125000.00,
  "status": "ACTIVE | ARCHIVED",
  "created_at": "ISO8601",
  "data_summary": {}
}
```

---

### GET /datalake/snapshots *(Mới)*
**UC-DATA-03** – Xem danh sách datalake snapshots.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ADMIN |

**Query Params**

| Param | Type | Mô tả |
|---|---|---|
| `snapshot_type` | string | `DAILY_TXN_SUMMARY` hoặc `EXTERNAL_INGEST` |
| `snapshot_date` | date | Lọc theo ngày |
| `status` | string | `ACTIVE` hoặc `ARCHIVED` |
| `page` | int | Số trang (default: 1) |
| `limit` | int | Số bản ghi/trang (default: 20) |

**Response 200**
```json
{
  "total": 30,
  "page": 1,
  "limit": 20,
  "data": [
    {
      "snapshot_id": "uuid",
      "snapshot_type": "DAILY_TXN_SUMMARY",
      "snapshot_date": "2026-04-01",
      "job_id": "uuid",
      "source_label": null,
      "record_count": 1540,
      "total_amount": 980000.00,
      "status": "ACTIVE",
      "created_at": "ISO8601",
      "data_summary": {}
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
| `job_type` | string | Lọc theo job type (e.g. `DAILY_SUMMARY`) |
| `status` | string | `RUNNING`, `SUCCESS`, `FAILED` |

**Response 200**
```json
{
  "total": 120,
  "page": 1,
  "limit": 20,
  "data": [
    {
      "job_id": "uuid",
      "job_type": "DAILY_SUMMARY",
      "target_date": "2026-04-01",
      "status": "SUCCESS",
      "records_in": 1540,
      "records_out": 1538,
      "error_message": null,
      "triggered_by": "uuid",
      "started_at": "ISO8601",
      "completed_at": "ISO8601",
      "created_at": "ISO8601"
    }
  ]
}
```

---

### POST /etl/run *(~~Cũ: POST /etl/trigger~~)*
**UC-DATA-03/04/05** – Trigger ETL Pipeline thủ công.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ADMIN |

> Idempotency guard: mỗi `(target_date, job_type)` chỉ SUCCESS 1 lần. Nếu đã thành công → 409.

**Request Body**
```json
{
  "target_date": "2026-04-02",
  "job_type": "DAILY_SUMMARY"
}
```

**Response 201**
```json
{
  "job_id": "uuid",
  "job_type": "DAILY_SUMMARY",
  "target_date": "2026-04-02",
  "status": "RUNNING | SUCCESS | FAILED",
  "records_in": null,
  "records_out": null,
  "error_message": null,
  "triggered_by": "uuid",
  "started_at": "ISO8601",
  "completed_at": null,
  "created_at": "ISO8601"
}
```

> *include* → UC-DATA-04 (Transform: dedup, fill missing, GeoIP enrich, map Star Schema)
> *include* → UC-DATA-05 (Load vào FACT_TRANSACTIONS + DIM tables)
> *include* → UC-DATA-06 (Ghi log ETL)

---

## UC07 – Idempotency, State & Reconciliation

### GET /transactions/{txn_id}/state-history *(~~Cũ: /states~~)*
**UC-STATE-05** – Xem lịch sử trạng thái của giao dịch.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | OPERATOR, REVIEWER, MANAGER, ADMIN *(~~Cũ: chỉ OPERATOR, ADMIN~~)* |

> ⚠️ **OPERATOR** chỉ xem được state-history của giao dịch do **chính mình submit**. Truy cập giao dịch của người khác → 403. *(~~Cũ: không có check, xem được của tất cả~~)*

**Response 200** – Array các state transitions
```json
[
  { "status": "PENDING",       "version": 1, "changed_at": "ISO8601", "actor": "system" },
  { "status": "MANUAL_REVIEW", "version": 2, "changed_at": "ISO8601", "actor": "AI_ENGINE" },
  { "status": "APPROVED",      "version": 3, "changed_at": "ISO8601", "actor": "reviewer_01" }
]
```

> Reflection của UC-STATE-01 (khởi PENDING v1), UC-STATE-02 (chuyển trạng thái), UC-STATE-03 (Optimistic Locking version++)

---

### POST /reconciliation/run
**UC-RECON-01** – Trigger chạy đối soát.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ADMIN |

> Tìm tất cả giao dịch PENDING quá `pending_timeout_minutes` và đánh dấu `PENDING_TIMEOUT`.

**Request Body**
```json
{
  "period_start": "ISO8601",
  "period_end": "ISO8601",
  "pending_timeout_minutes": 120
}
```

> `pending_timeout_minutes`: 1–10080 (default: 120).

**Response 201**
```json
{
  "run_id": "uuid",
  "period_start": "ISO8601",
  "period_end": "ISO8601",
  "pending_timeout_minutes": 120,
  "status": "RUNNING | COMPLETED | FAILED",
  "total_txn_count": null,
  "matched_count": null,
  "discrepancy_count": null,
  "total_amount": null,
  "error_message": null,
  "triggered_by": "uuid",
  "completed_at": null,
  "created_at": "ISO8601"
}
```

> *include* → UC-RECON-02 (Tìm PENDING txns quá timeout, mark PENDING_TIMEOUT)
> *extend* → UC-RECON-03 (Ghi discrepancy items cho các giao dịch bất thường)

---

### GET /reconciliation/reports *(~~Cũ: GET /reconciliation/jobs — path không tồn tại~~)*
**UC-DATA-09** – Xem danh sách các lần chạy đối soát.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ADMIN |

**Query Params**

| Param | Type | Mô tả |
|---|---|---|
| `page` | int | Số trang |
| `limit` | int | Số bản ghi |
| `status` | string | `RUNNING`, `COMPLETED`, `FAILED` |

**Response 200**
```json
{
  "total": 30,
  "page": 1,
  "limit": 20,
  "data": [
    {
      "run_id": "uuid",
      "period_start": "ISO8601",
      "period_end": "ISO8601",
      "pending_timeout_minutes": 120,
      "status": "COMPLETED",
      "total_txn_count": 1540,
      "matched_count": 1535,
      "discrepancy_count": 5,
      "total_amount": 980000.00,
      "error_message": null,
      "triggered_by": "uuid",
      "completed_at": "ISO8601",
      "created_at": "ISO8601"
    }
  ]
}
```

---

### GET /reconciliation/{run_id} *(~~Cũ: GET /reconciliation/jobs/{job_id} — path không tồn tại~~)*
**UC-RECON-03** – Xem chi tiết lần chạy đối soát kèm danh sách discrepancy items.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ADMIN |

**Response 200**
```json
{
  "run_id": "uuid",
  "period_start": "ISO8601",
  "period_end": "ISO8601",
  "pending_timeout_minutes": 120,
  "status": "COMPLETED",
  "total_txn_count": 1540,
  "matched_count": 1535,
  "discrepancy_count": 5,
  "total_amount": 980000.00,
  "error_message": null,
  "triggered_by": "uuid",
  "completed_at": "ISO8601",
  "created_at": "ISO8601",
  "items": [
    {
      "item_id": "uuid",
      "run_id": "uuid",
      "txn_id": "uuid",
      "item_type": "string",
      "txn_status": "PENDING",
      "txn_amount": 1500.00,
      "txn_created_at": "ISO8601",
      "minutes_pending": 180,
      "status": "OPEN | RESOLVED",
      "resolution_note": null,
      "resolved_by": null,
      "resolved_at": null,
      "created_at": "ISO8601"
    }
  ]
}
```

---

### PATCH /reconciliation/{run_id}/resolve *(Mới)*
**UC-RECON-04** – Tandánh dấu tất cả discrepancy items OPEN là RESOLVED.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ADMIN |

> Chỉ hoạt động với run ở trạng thái COMPLETED. Run chưa COMPLETED → 409.

**Request Body**
```json
{
  "resolution_note": "string (min5, max500)"
}
```

**Response 200**
> Trả về `ReconciliationDetailResponse` (cùng schema với GET /reconciliation/{run_id}) với tất cả items đã cập nhật sang RESOLVED.

---

## UC08 – Real-time Stream (SSE) *(Mới)*

### GET /stream/transactions
**UC-STREAM-01** – Server-Sent Events: live feed giao dịch mới.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | OPERATOR, REVIEWER, MANAGER, ADMIN |

> Dùng trong demo: Faker POST liên tục → SSE đẩy từng giao dịch mới về frontend ngay lập tức.
> Filter dùng `created_at >= last_checked` (không phải `txn_time`) để bắt tất cả bản ghi mới insert.

**Query Params**

| Param | Type | Mô tả |
|---|---|---|
| `interval` | float | Poll interval (0.5–10s, default: 2.0s) |

**Response** – `Content-Type: text/event-stream`
```
: heartbeat

data: {"txn_id":"uuid","customer_id":"uuid","merchant_id":"uuid","amount":350.50,"currency_code":"USD","status":"APPROVED","fraud_score":0.30,"txn_time":"ISO8601","created_at":"ISO8601"}

data: {"txn_id":"uuid",...,"status":"MANUAL_REVIEW","fraud_score":0.50,...}

: ping
```

> `: ping` được gửi khi không có giao dịch mới trong interval.
> Headers: `Cache-Control: no-cache`, `X-Accel-Buffering: no`.

---

### GET /stream/dashboard
**UC-STREAM-02** – Server-Sent Events: live dashboard metrics.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | MANAGER, ADMIN |

**Query Params**

| Param | Type | Mô tả |
|---|---|---|
| `interval` | float | Poll interval (1–30s, default: 5.0s) |

**Response** – `Content-Type: text/event-stream`
```
: heartbeat

data: {"total_transactions":1540,"fraud_rate":0.08,"cases_pending":12,"cases_assigned":3,"loan_pending":5,...}

data: {...updated metrics...}
```

---

## UC09 – Analyst Module

> **Prefix:** `/analyst`
> **Roles:** ANALYST (write), MANAGER (read + acknowledge), ADMIN (read + write)

---

### GET /analyst/thresholds
**UC-ANALYST-01** – Xem ngưỡng phân loại hiện tại của fraud model và credit model.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ANALYST, MANAGER, ADMIN |

**Response 200**
```json
{
  "fraud": [
    { "model_name": "fraud", "param_name": "reject_threshold", "param_value": 0.65, "updated_at": "ISO8601", "updated_by": "uuid" },
    { "model_name": "fraud", "param_name": "review_threshold", "param_value": 0.35, "updated_at": "ISO8601", "updated_by": "uuid" }
  ],
  "loan": [
    { "model_name": "loan", "param_name": "high_risk_threshold", "param_value": 0.50, "updated_at": "ISO8601", "updated_by": "uuid" },
    { "model_name": "loan", "param_name": "medium_risk_threshold", "param_value": 0.20, "updated_at": "ISO8601", "updated_by": "uuid" }
  ]
}
```

---

### PATCH /analyst/thresholds
**UC-ANALYST-02** – Cập nhật ngưỡng phân loại (batch update).

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ANALYST, ADMIN |

> Cross-validation: `review_threshold < reject_threshold` và `medium_risk_threshold < high_risk_threshold`. Vi phạm → 422.
> Mọi thay đổi ghi `AuditLog(THRESHOLD_UPDATED)`.

**Request Body**
```json
{
  "updates": [
    { "model_name": "fraud", "param_name": "reject_threshold", "param_value": 0.70 }
  ]
}
```

**Response 200** — cùng schema với GET /analyst/thresholds

**Response 422 – Cross-validation failed**
```json
{ "code": "BusinessValidationError", "message": "review_threshold (0.40) phải nhỏ hơn reject_threshold (0.35)" }
```

---

### GET /analyst/model-performance/fraud
**UC-ANALYST-03** – Thống kê hiệu suất fraud detection model.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ANALYST, MANAGER, ADMIN |

**Query Params**

| Param | Type | Mô tả |
|---|---|---|
| `days` | int | Số ngày nhìn lại (1–365, default: 30) |

**Response 200**
```json
{
  "period_days": 30,
  "score_distribution": {
    "approved_count": 4800,
    "review_count": 6200,
    "rejected_count": 5000,
    "total": 16000,
    "approved_rate": 0.30,
    "review_rate": 0.3875,
    "rejected_rate": 0.3125,
    "false_positive_count": 124,
    "false_positive_rate": 0.02
  },
  "current_thresholds": {
    "reject_threshold": 0.65,
    "review_threshold": 0.35
  }
}
```

---

### GET /analyst/model-performance/loan
**UC-ANALYST-04** – Thống kê hiệu suất credit scoring model.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ANALYST, MANAGER, ADMIN |

**Query Params**

| Param | Type | Mô tả |
|---|---|---|
| `days` | int | Số ngày nhìn lại (1–365, default: 30) |

**Response 200**
```json
{
  "period_days": 30,
  "risk_distribution": {
    "low_risk_count": 320,
    "medium_risk_count": 180,
    "high_risk_count": 100,
    "total": 600,
    "low_risk_rate": 0.5333,
    "medium_risk_rate": 0.30,
    "high_risk_rate": 0.1667,
    "approved_count": 480,
    "rejected_count": 80,
    "pending_count": 40
  },
  "current_thresholds": {
    "high_risk_threshold": 0.50,
    "medium_risk_threshold": 0.20
  }
}
```

---

### GET /analyst/suppression-rules
**UC-ANALYST-05** – Danh sách suppression rules (whitelist bypass fraud scoring).

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ANALYST, ADMIN |

**Query Params**

| Param | Type | Mô tả |
|---|---|---|
| `include_inactive` | boolean | Bao gồm rules đã vô hiệu hóa (default: false) |

**Response 200** — Array
```json
[
  {
    "rule_id": "uuid",
    "rule_type": "MERCHANT | CUSTOMER | CARD",
    "entity_id": "string",
    "reason": "string",
    "is_active": true,
    "created_by": "uuid",
    "created_at": "ISO8601",
    "expires_at": "ISO8601 | null"
  }
]
```

---

### POST /analyst/suppression-rules
**UC-ANALYST-06** – Tạo suppression rule mới.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ANALYST |

> Ghi `AuditLog(SUPPRESSION_RULE_CREATED)`.

**Request Body**
```json
{
  "rule_type": "MERCHANT | CUSTOMER | CARD",
  "entity_id": "string (ID của merchant/customer/card)",
  "reason": "string (lý do bypass, bắt buộc)",
  "expires_at": "ISO8601 | null"
}
```

**Response 201** — cùng schema với item trong GET /analyst/suppression-rules

---

### PATCH /analyst/suppression-rules/{rule_id}
**UC-ANALYST-07** – Vô hiệu hóa suppression rule.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ANALYST, ADMIN |

> Ghi `AuditLog(SUPPRESSION_RULE_DEACTIVATED)`.

**Response 200** — rule với `is_active: false`

**Response 404**
```json
{ "code": "NotFoundError", "message": "SuppressionRule không tồn tại." }
```

---

### POST /analyst/reports
**UC-ANALYST-08** – ANALYST soạn và submit báo cáo phân tích lên MANAGER.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ANALYST |

> Báo cáo dạng **Markdown** — hỗ trợ bảng, heading, danh sách.
> `content_md` tối thiểu 30 ký tự. Ghi `AuditLog(ANALYST_REPORT_SUBMITTED)`.

**Request Body**
```json
{
  "title": "string",
  "report_type": "FRAUD_ANALYSIS | LOAN_ANALYSIS | THRESHOLD_RECOMMENDATION | SUPPRESSION_REVIEW | GENERAL",
  "content_md": "string (Markdown)"
}
```

**Response 201**
```json
{
  "report_id": "uuid",
  "title": "string",
  "report_type": "THRESHOLD_RECOMMENDATION",
  "content_md": "string",
  "status": "PENDING_REVIEW",
  "submitted_by": "uuid",
  "submitted_at": "ISO8601",
  "acknowledged_by": null,
  "acknowledged_at": null,
  "note": null,
  "submitter": { "user_id": "uuid", "username": "string", "full_name": "string" },
  "acknowledger": null
}
```

**Response 422 – Invalid report_type**
```json
{ "code": "ValidationError", "message": "report_type không hợp lệ." }
```

---

### GET /analyst/reports
**UC-ANALYST-09** – Danh sách báo cáo (không bao gồm `content_md` để giảm payload).

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ANALYST, MANAGER, ADMIN |

**Query Params**

| Param | Type | Mô tả |
|---|---|---|
| `status` | string | `PENDING_REVIEW \| ACKNOWLEDGED \| ARCHIVED` |
| `report_type` | string | Lọc theo loại báo cáo |
| `submitted_by` | uuid | Lọc theo analyst |
| `limit` | int | Số bản ghi/trang (1–100, default: 20) |
| `offset` | int | Skip N bản ghi (default: 0) |

**Response 200**
```json
{
  "total": 12,
  "limit": 20,
  "offset": 0,
  "items": [
    {
      "report_id": "uuid",
      "title": "string",
      "report_type": "FRAUD_ANALYSIS",
      "status": "PENDING_REVIEW",
      "submitted_by": "uuid",
      "submitted_at": "ISO8601",
      "acknowledged_by": null,
      "acknowledged_at": null
    }
  ]
}
```

> ⚠️ Items **không có `content_md`** (dùng GET /analyst/reports/{id} để lấy nội dung đầy đủ).

---

### GET /analyst/reports/{report_id}
**UC-ANALYST-10** – Chi tiết báo cáo kèm nội dung Markdown đầy đủ.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ANALYST, MANAGER, ADMIN |

**Response 200** — cùng schema với POST /analyst/reports Response 201 (có `content_md`)

**Response 404**
```json
{ "code": "NotFoundError", "message": "AnalystReport không tồn tại." }
```

---

### GET /analyst/reports/{report_id}/pdf
**UC-ANALYST-11** – Tải báo cáo dưới dạng PDF chuyên nghiệp.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ANALYST, MANAGER, ADMIN |

> Render Markdown → PDF bằng fpdf2. Hỗ trợ tiếng Việt Unicode đầy đủ (Arial Unicode TTF).
> Header: navy bar + light-blue title band + meta row (ngày gửi, người gửi, trạng thái).
> Footer: tên hệ thống + số trang.
> Nếu báo cáo đã ACKNOWLEDGED: hiển thị khối xác nhận màu xanh với tên MANAGER và ghi chú.

**Response 200**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="analyst_report_<id8>.pdf"
```

---

### PATCH /analyst/reports/{report_id}/acknowledge
**UC-ANALYST-12** – MANAGER xác nhận đã đọc và xử lý báo cáo.

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | MANAGER, ADMIN |

> Chuyển status `PENDING_REVIEW → ACKNOWLEDGED`. Double-acknowledge → 422.
> Ghi `AuditLog(ANALYST_REPORT_ACKNOWLEDGED)`.

**Request Body**
```json
{
  "note": "string (tùy chọn — ghi chú phản hồi cho analyst)"
}
```

**Response 200** — cùng schema với POST /analyst/reports Response 201

**Response 422 – Đã xác nhận trước đó**
```json
{ "code": "BusinessValidationError", "message": "Báo cáo này đã được xác nhận trước đó." }
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

| Module | OPERATOR | REVIEWER | ANALYST | MANAGER | ADMIN |
|---|:---:|:---:|:---:|:---:|:---:|
| Health | ✓ | ✓ | ✓ | ✓ | ✓ |
| Auth (login/logout/refresh/change-pw/me) | ✓ | ✓ | ✓ | ✓ | ✓ |
| User Management | – | – | – | Chỉ đọc | Full |
| Transaction Submit | ✓ | – | – | – | – |
| Transaction View | Chỉ của mình | ✓ | – | ✓ | ✓ |
| Transaction State-History | ✓ | ✓ | – | ✓ | ✓ |
| Case Management | – | Full | – | Chỉ đọc | Chỉ đọc |
| Audit Log | – | – | – | ✓ | ✓ |
| Dashboard / BI | – | – | – | ✓ | ✓ |
| Loan Create | ✓ | – | – | – | – |
| Loan Simulate | ✓ | – | – | ✓ | ✓ |
| Loan View | Chỉ của mình | – | – | ✓ | ✓ |
| Loan Decision (Approve/Reject) | – | – | – | ✓ | ✓ |
| ETL / Data Lake | – | – | – | – | ✓ |
| Reconciliation | – | – | – | Chỉ đọc | Full |
| SSE Stream (transactions) | ✓ | ✓ | – | ✓ | ✓ |
| SSE Stream (dashboard) | – | – | – | ✓ | ✓ |
| Analyst Thresholds (view) | – | – | ✓ | ✓ | ✓ |
| Analyst Thresholds (update) | – | – | ✓ | – | ✓ |
| Analyst Model Performance | – | – | ✓ | ✓ | ✓ |
| Analyst Suppression Rules (view) | – | – | ✓ | – | ✓ |
| Analyst Suppression Rules (create/deactivate) | – | – | ✓ | – | ✓ |
| Analyst Reports (create) | – | – | ✓ | – | – |
| Analyst Reports (view/PDF) | – | – | ✓ | ✓ | ✓ |
| Analyst Reports (acknowledge) | – | – | – | ✓ | ✓ |

### Phân luồng Fraud Score (UC-TXN-05)

*(~~Cũ: ≤ 0.30 → APPROVED, > 0.70 → REJECTED~~)*
> Model Random Forest 10 cây → score ∈ `{0.3, 0.4, 0.5, 0.6, 0.7}`. Ngưỡng calibrate theo dải thực tế.

| `fraud_score` | Kết quả |
|---|---|
| `< 0.35` | `APPROVED` (~30% giao dịch) |
| `0.35 ≤ score < 0.65` | `MANUAL_REVIEW` (~40% giao dịch) |
| `≥ 0.65` | `REJECTED` (~30% giao dịch) |
| Bất kỳ, `amount > 500,000,000` | Override → `MANUAL_REVIEW` |

### Phân loại Risk Level – Loan (UC-LOAN)

*(~~Cũ: risk_grade, ngưỡng < 0.3 / 0.3–0.6 / > 0.6~~)*

| `pd_score` | `risk_level` |
|---|---|
| `< 0.20` | `LOW` |
| `0.20 ≤ pd < 0.50` | `MEDIUM` |
| `≥ 0.50` | `HIGH` |
