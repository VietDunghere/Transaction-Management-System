# API Design -- Frontend

> **Base URL:** `/api/v1`
> **Auth:** JWT Bearer Token (tru endpoint login va refresh)
> **Content-Type:** `application/json`

> Tai lieu nay anh xa tu UC_SUMMARY.md (UC01-UC07, 20 UC) sang API endpoint tuong ung cho frontend.
> Role assignment tuan theo UC_SUMMARY.md -- KHONG theo API_DESIGN.md cu.

---

## Muc luc

1. [UC01 -- Xac thuc & Quan ly Phien lam viec](#uc01--xac-thuc--quan-ly-phien-lam-viec)
2. [UC02 -- Quan ly Giao dich](#uc02--quan-ly-giao-dich)
3. [UC03 -- Ho tro Quyet dinh Cho vay](#uc03--ho-tro-quyet-dinh-cho-vay)
4. [UC04 -- Xet duyet Thu cong](#uc04--xet-duyet-thu-cong)
5. [UC05 -- Giam sat & Bao cao](#uc05--giam-sat--bao-cao)
6. [UC06 -- Quan tri He thong](#uc06--quan-tri-he-thong)
7. [UC07 -- Phan tich Rui ro](#uc07--phan-tich-rui-ro)
8. [Phan quyen tong hop](#phan-quyen-tong-hop)

---

## UC01 -- Xac thuc & Quan ly Phien lam viec

**Actor:** Thanh vien he thong (tat ca role)

### UC01.1 -- Dang nhap

`POST /auth/login` -- Khong can auth

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
  "role": "OPERATOR | REVIEWER | ANALYST | MANAGER | ADMIN"
}
```

**Response 401** -- `INVALID_CREDENTIALS`
**Response 403** -- `ACCOUNT_DISABLED`

---

### UC01.2 -- Dang xuat

`POST /auth/logout` -- Bearer Token -- Tat ca role

**Response 200**
```json
{ "message": "Dang xuat thanh cong." }
```

---

### UC01.3 -- Doi mat khau ca nhan

`PATCH /auth/change-password` -- Bearer Token -- Tat ca role

**Request Body**
```json
{
  "current_password": "string",
  "new_password": "string (min 8 ky tu)",
  "confirm_password": "string"
}
```

**Response 200**
```json
{ "message": "Doi mat khau thanh cong." }
```

---

### UC01.S1 -- Xem thong tin ca nhan

`GET /auth/me` -- Bearer Token -- Tat ca role

**Response 200**
```json
{
  "user_id": "uuid",
  "username": "string",
  "full_name": "string",
  "role": "OPERATOR | REVIEWER | ANALYST | MANAGER | ADMIN",
  "is_active": true
}
```

---

### UC01.S2 -- Lam moi token

`POST /auth/refresh` -- Khong can Bearer

**Request Body**
```json
{ "refresh_token": "string" }
```

**Response 200**
```json
{
  "access_token": "string (JWT)",
  "refresh_token": "string (JWT -- rotated)",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**Response 401** -- `INVALID_TOKEN`

---

## UC02 -- Quan ly Giao dich

**Actor:** OPERATOR (nop), ANALYST, MANAGER (xem)
> `POST /transactions/submit` (UC02.1 -- Nop giao dich) la OPERATOR only, khong can frontend.

### UC02.2 -- Xem giao dich

#### Danh sach

`GET /transactions` -- Bearer Token -- **ANALYST, MANAGER**

**Query Params**

| Param | Type | Mo ta |
|---|---|---|
| `page` | int | So trang (default: 1) |
| `limit` | int | So ban ghi/trang (default: 20) |
| `status` | string | `APPROVED`, `REJECTED`, `MANUAL_REVIEW` |
| `customer_id` | uuid | Loc theo customer |
| `merchant_id` | uuid | Loc theo merchant |
| `from_date` | ISO8601 | Tu ngay (txn_time) |
| `to_date` | ISO8601 | Den ngay (txn_time) |
| `min_amount` | number | So tien toi thieu |
| `max_amount` | number | So tien toi da |

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

#### Chi tiet

`GET /transactions/{txn_id}` -- Bearer Token -- **ANALYST, MANAGER**

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

---

## UC03 -- Ho tro Quyet dinh Cho vay

**Actor:** OPERATOR (nop), REVIEWER (xem + phe duyet)
> `POST /loans` (UC03.1 -- Nop ho so) la OPERATOR only, khong can frontend.

### UC03.2 -- Xem ho so vay

#### Danh sach

`GET /loans` -- Bearer Token -- **OPERATOR, REVIEWER**

**Query Params**

| Param | Type | Mo ta |
|---|---|---|
| `page` | int | So trang |
| `limit` | int | So ban ghi/trang |
| `status` | string | `PENDING`, `APPROVED`, `REJECTED` |
| `customer_id` | uuid | Loc theo khach hang |

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

#### Chi tiet

`GET /loans/{loan_id}` -- Bearer Token -- **OPERATOR, REVIEWER**

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

### UC03.3 -- Phe duyet / Tu choi ho so vay

`PATCH /loans/{loan_id}/decision` -- Bearer Token -- **REVIEWER**

> `version` bat buoc de kich hoat Optimistic Locking.

**Request Body**
```json
{
  "decision": "APPROVE | REJECT",
  "review_note": "string (bat buoc)",
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

**Response 409** -- Loan khong o PENDING hoac Optimistic Lock conflict

---

## UC04 -- Xet duyet Thu cong

**Actor:** REVIEWER

### UC04.1 -- Xem case

#### Danh sach

`GET /cases` -- Bearer Token -- **REVIEWER**

> REVIEWER thay: tat ca OPEN cases (queue chua ai nhan) + cases duoc giao cho minh.
> Compound query: `(assigned_to IS NULL) OR (assigned_to = reviewer_id)`.

**Query Params**

| Param | Type | Mo ta |
|---|---|---|
| `page` | int | So trang |
| `limit` | int | So ban ghi/trang |
| `status` | string | `OPEN`, `ASSIGNED`, `APPROVED`, `REJECTED` |
| `assigned_to` | uuid | Loc theo reviewer |
| `from_date` | ISO8601 | Tu ngay |
| `to_date` | ISO8601 | Den ngay |

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

#### Chi tiet

`GET /cases/{case_id}` -- Bearer Token -- **REVIEWER**

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

### UC04.2 -- Nhan case (Assign)

`POST /cases/{case_id}/assign` -- Bearer Token -- **REVIEWER**

> Dung `WHERE assigned_to IS NULL` de chan race condition.

**Response 200**
```json
{
  "case_id": "uuid",
  "status": "ASSIGNED",
  "assigned_to": "uuid",
  "assigned_at": "ISO8601"
}
```

**Response 409** -- `CASE_ALREADY_ASSIGNED`

---

### UC04.3 -- Ra quyet dinh Phe duyet / Tu choi

`PATCH /cases/{case_id}/decision` -- Bearer Token -- **REVIEWER**

> Case phai o trang thai **ASSIGNED** truoc khi quyet dinh. Case OPEN -> 409.
> REVIEWER chi quyet dinh case duoc giao cho minh.
> `version` bat buoc -- Optimistic Locking.

**Request Body**
```json
{
  "decision": "APPROVE | REJECT",
  "decision_note": "string (bat buoc -- toi thieu 10 ky tu)",
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

**Response 403** -- Case khong phai cua minh
**Response 409** -- Case chua assign hoac Optimistic Lock conflict

---

## UC05 -- Giam sat & Bao cao

**Actor:** ANALYST, MANAGER (dashboard); MANAGER, ADMIN (audit log)

### UC05.1 -- Xem Dashboard tong quan

#### Summary

`GET /dashboard/summary` -- Bearer Token -- **ANALYST, MANAGER**

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

#### Fraud Trend

`GET /dashboard/fraud-trend` -- Bearer Token -- **ANALYST, MANAGER**

**Query Params**

| Param | Type | Mo ta |
|---|---|---|
| `days` | int | So ngay nhin lai (1-90, default: 30) |

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

### UC05.2 -- Xem Audit Log he thong

#### Danh sach

`GET /audit-logs` -- Bearer Token -- **MANAGER, ADMIN**

> Sorted DESC by event_ts.

**Query Params**

| Param | Type | Mo ta |
|---|---|---|
| `page` | int | So trang |
| `limit` | int | So ban ghi/trang |
| `entity_type` | string | `TRANSACTION`, `LOAN`, `USER`, `CASE` |
| `actor_user_id` | uuid | Ai thuc hien |
| `event_type` | string | Loai su kien |
| `from_date` | ISO8601 | Tu ngay |
| `to_date` | ISO8601 | Den ngay |

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

#### Chi tiet

`GET /audit-logs/{log_id}` -- Bearer Token -- **MANAGER, ADMIN**

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

**Response 404** -- `NOT_FOUND`

---

## UC06 -- Quan tri He thong

**Actor:** ADMIN (full), MANAGER (chi xem)

### UC06.1 -- Tao tai khoan nguoi dung moi

`POST /users` -- Bearer Token -- **ADMIN**

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

---

### UC06.2 -- Thay doi trang thai tai khoan

`PATCH /users/{user_id}/disable` -- Bearer Token -- **ADMIN**
`PATCH /users/{user_id}/enable` -- Bearer Token -- **ADMIN**

> ADMIN khong duoc tu vo hieu hoa chinh minh.

**Response 200 (disable)**
```json
{ "user_id": "uuid", "is_active": false, "message": "Tai khoan da bi vo hieu hoa." }
```

**Response 200 (enable)**
```json
{ "user_id": "uuid", "is_active": true, "message": "Tai khoan da duoc kich hoat." }
```

**Response 403** -- Tu vo hieu hoa chinh minh

---

### UC06.3 -- Gan / Thay doi vai tro nguoi dung

`PATCH /users/{user_id}/role` -- Bearer Token -- **ADMIN**

**Request Body**
```json
{ "role": "OPERATOR | REVIEWER | MANAGER" }
```

**Response 200**
```json
{ "user_id": "uuid", "role": "REVIEWER", "updated_at": "ISO8601" }
```

---

### UC06.4 -- Xem nguoi dung

#### Danh sach

`GET /users` -- Bearer Token -- **MANAGER, ADMIN**

**Query Params**

| Param | Type | Mo ta |
|---|---|---|
| `page` | int | So trang (default: 1) |
| `limit` | int | So ban ghi/trang (default: 20) |
| `role` | string | Loc theo role |
| `is_active` | boolean | Loc theo trang thai |

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

#### Chi tiet

`GET /users/{user_id}` -- Bearer Token -- **MANAGER, ADMIN**

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

**Response 404** -- `NOT_FOUND`

---

## UC07 -- Phan tich Rui ro (Analyst Module)

**Actor:** ANALYST

### UC07.1 -- Xem nguong phan loai hien hanh

`GET /analyst/thresholds` -- Bearer Token -- **ANALYST**

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

### UC07.2 -- Cap nhat nguong phan loai

`PATCH /analyst/thresholds` -- Bearer Token -- **ANALYST**

> Cross-validation: `review_threshold < reject_threshold` va `medium_risk_threshold < high_risk_threshold`. Vi pham -> 422.

**Request Body**
```json
{
  "updates": [
    { "model_name": "fraud", "param_name": "reject_threshold", "param_value": 0.70 }
  ]
}
```

**Response 200** -- Cung schema voi GET /analyst/thresholds

**Response 422** -- Cross-validation failed

---

### UC07.3 -- Xem hieu suat mo hinh

`GET /analyst/model-performance/fraud` -- Bearer Token -- **ANALYST**
`GET /analyst/model-performance/loan` -- Bearer Token -- **ANALYST**

**Query Params**

| Param | Type | Mo ta |
|---|---|---|
| `days` | int | So ngay nhin lai (1-365, default: 30) |

**Response 200 (fraud)**
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

**Response 200 (loan)**
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

## Phan quyen tong hop

| UC | Endpoint | OPERATOR | REVIEWER | ANALYST | MANAGER | ADMIN |
|---|---|:---:|:---:|:---:|:---:|:---:|
| UC01.1 | POST /auth/login | V | V | V | V | V |
| UC01.2 | POST /auth/logout | V | V | V | V | V |
| UC01.3 | PATCH /auth/change-password | V | V | V | V | V |
| UC01.S1 | GET /auth/me | V | V | V | V | V |
| UC01.S2 | POST /auth/refresh | V | V | V | V | V |
| UC02.2 | GET /transactions | -- | -- | V | V | -- |
| UC02.2 | GET /transactions/{id} | -- | -- | V | V | -- |
| UC03.2 | GET /loans | V | V | -- | -- | -- |
| UC03.2 | GET /loans/{id} | V | V | -- | -- | -- |
| UC03.3 | PATCH /loans/{id}/decision | -- | V | -- | -- | -- |
| UC04.1 | GET /cases | -- | V | -- | -- | -- |
| UC04.1 | GET /cases/{id} | -- | V | -- | -- | -- |
| UC04.2 | POST /cases/{id}/assign | -- | V | -- | -- | -- |
| UC04.3 | PATCH /cases/{id}/decision | -- | V | -- | -- | -- |
| UC05.1 | GET /dashboard/summary | -- | -- | V | V | -- |
| UC05.1 | GET /dashboard/fraud-trend | -- | -- | V | V | -- |
| UC05.2 | GET /audit-logs | -- | -- | -- | V | V |
| UC05.2 | GET /audit-logs/{id} | -- | -- | -- | V | V |
| UC06.1 | POST /users | -- | -- | -- | -- | V |
| UC06.2 | PATCH /users/{id}/disable\|enable | -- | -- | -- | -- | V |
| UC06.3 | PATCH /users/{id}/role | -- | -- | -- | -- | V |
| UC06.4 | GET /users | -- | -- | -- | V | V |
| UC06.4 | GET /users/{id} | -- | -- | -- | V | V |
| UC07.1 | GET /analyst/thresholds | -- | -- | V | -- | -- |
| UC07.2 | PATCH /analyst/thresholds | -- | -- | V | -- | -- |
| UC07.3 | GET /analyst/model-performance/* | -- | -- | V | -- | -- |

---

## Quy uoc chung

### Ma loi chuan

| HTTP | Error Code | Y nghia |
|---|---|---|
| 400 | `VALIDATION_ERROR` | Du lieu dau vao khong hop le |
| 401 | `UNAUTHORIZED` | Chua dang nhap / JWT het han |
| 403 | `FORBIDDEN` | Khong co quyen thuc hien |
| 404 | `NOT_FOUND` | Resource khong ton tai |
| 409 | `CONFLICT` | Trung lap / Optimistic Lock conflict |
| 422 | `UNPROCESSABLE` | Du lieu hop le nhung khong the xu ly |
| 429 | `RATE_LIMITED` | Vuot qua gioi han request |
| 500 | `INTERNAL_ERROR` | Loi server noi bo |

**Cau truc loi chuan:**
```json
{
  "error": "FORBIDDEN",
  "message": "Ban khong co quyen thuc hien hanh dong nay.",
  "request_id": "uuid"
}
```
