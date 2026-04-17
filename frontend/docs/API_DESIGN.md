# API Design – Transaction Management System (v1.0.0)

> **Base URL:** `http://localhost:8000/api/v1` (dev) | `https://api.tms.local/api/v1` (prod)  
> **Auth:** JWT Bearer Token (except `POST /auth/login`, `POST /auth/refresh`)  
> **Content-Type:** `application/json`  
> **Generated from:** Running OpenAPI schema at `/docs`  
> **Last Updated:** 2026-04-17

---

## Table of Contents

1. [UC02 – Authentication & Authorization](#uc02--authentication--authorization)
2. [UC03 – Transaction Management](#uc03--transaction-management)
3. [UC04 – User Management](#uc04--user-management)
4. [UC05 – Case Management & Review](#uc05--case-management--review)
5. [UC06 – Loan Management](#uc06--loan-management)
6. [UC07 – Audit Logging](#uc07--audit-logging)
7. [UC08 – Dashboard & Reports](#uc08--dashboard--reports)
8. [UC09 – ETL Pipeline](#uc09--etl-pipeline)
9. [Common Conventions](#common-conventions)

---

## UC02 – Authentication & Authorization

### POST /auth/login
**Login with credentials, receive JWT tokens.**

| | |
|---|---|
| **Auth** | None required |
| **Roles** | All |

**Request Body**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response 200 (Success)**
```json
{
  "access_token": "eyJhbGc...(JWT)",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "user_id": "uuid",
    "username": "string",
    "full_name": "string"
  }
}
```

**Response 401 (Invalid credentials)**
```json
{
  "code": "UnauthorizedError",
  "message": "Invalid username or password"
}
```

---

### POST /auth/logout
**Logout — JWT is stateless, client just discards token.**

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | All |

**Response 200**
```json
{
  "message": "Đăng xuất thành công."
}
```

---

### GET /auth/me
**Get current authenticated user profile.**

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | All |

**Response 200**
```json
{
  "user_id": "uuid",
  "username": "string",
  "full_name": "string",
  "email": "string",
  "is_active": true,
  "created_at": "ISO8601"
}
```

---

### PATCH /auth/change-password
**Change personal password.**

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | All |

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
{
  "message": "Đổi mật khẩu thành công."
}
```

---

### POST /auth/refresh
**Use refresh token to get new access token without re-login.**

| | |
|---|---|
| **Auth** | None required |
| **Roles** | All |

**Request Body**
```json
{
  "refresh_token": "string"
}
```

**Response 200**
```json
{
  "access_token": "eyJhbGc...(JWT)",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

---

## UC04 – User Management

### GET /users
**List all users with pagination and filters.**

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | MANAGER, ADMIN |

**Query Parameters**

| Param | Type | Description |
|---|---|---|
| `role` | string | Filter by role: OPERATOR, REVIEWER, MANAGER, ADMIN |
| `is_active` | boolean | Filter by active status |
| `page` | int | Page number (default: 1) |
| `limit` | int | Records per page (default: 20, max: 100) |

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
      "email": "string",
      "role": "OPERATOR",
      "is_active": true,
      "created_at": "ISO8601"
    }
  ]
}
```

---

### POST /users
**Create new user account (ADMIN only).**

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

**Response 201 (Created)**
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

---

### GET /users/{user_id}
**Get user details.**

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

---

### PATCH /users/{user_id}/disable
**Disable user account.**

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ADMIN |

**Response 200**
```json
{
  "message": "Tài khoản đã bị vô hiệu hóa."
}
```

---

### PATCH /users/{user_id}/enable
**Re-enable disabled user account.**

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ADMIN |

**Response 200**
```json
{
  "message": "Tài khoản đã được kích hoạt."
}
```

---

### PATCH /users/{user_id}/role
**Update user role.**

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ADMIN |

**Request Body**
```json
{
  "role": "OPERATOR | REVIEWER | MANAGER"
}
```

**Response 200**
```json
{
  "user_id": "uuid",
  "role": "REVIEWER",
  "updated_at": "ISO8601"
}
```

---

## UC03 – Transaction Management

### POST /transactions/submit
**Submit new transaction for fraud scoring.**

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | OPERATOR |

**Request Body**
```json
{
  "customer_id": "uuid",
  "merchant_id": "uuid",
  "channel_id": "int",
  "card_number_masked": "4111********1111",
  "amount": 1500000,
  "currency_code": "VND",
  "txn_time": "ISO8601",
  "source_ip": "192.168.1.1"
}
```

**Response 201 (Created)**
```json
{
  "txn_id": "uuid",
  "status": "APPROVED | REJECTED | MANUAL_REVIEW",
  "fraud_score": 0.25,
  "reason_code": "LOW_RISK | HIGH_RISK | HIGH_VALUE",
  "created_at": "ISO8601"
}
```

---

### GET /transactions
**List transactions with filters.**

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | OPERATOR, REVIEWER, MANAGER, ADMIN |

**Query Parameters**

| Param | Type | Description |
|---|---|---|
| `status` | string | Filter: PENDING, APPROVED, REJECTED, MANUAL_REVIEW |
| `merchant_id` | string | Filter by merchant UUID |
| `from_date` | string | From date (ISO8601) |
| `to_date` | string | To date (ISO8601) |
| `min_amount` | number | Minimum amount |
| `max_amount` | number | Maximum amount |
| `page` | int | Page (default: 1) |
| `limit` | int | Per page (default: 20, max: 100) |

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
      "amount": 1500000,
      "currency_code": "VND",
      "status": "APPROVED",
      "fraud_score": 0.12,
      "txn_time": "ISO8601",
      "created_at": "ISO8601"
    }
  ]
}
```

---

### GET /transactions/{txn_id}
**Get transaction details with scoring results.**

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | OPERATOR, REVIEWER, MANAGER, ADMIN |

**Response 200**
```json
{
  "txn_id": "uuid",
  "customer_id": "uuid",
  "merchant_id": "uuid",
  "card_number_masked": "4111********1111",
  "amount": 1500000,
  "currency_code": "VND",
  "status": "MANUAL_REVIEW",
  "fraud_score": 0.55,
  "reason_code": "HIGH_RISK",
  "txn_time": "ISO8601",
  "source_ip": "192.168.1.1",
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

---

### GET /transactions/{txn_id}/state-history
**Get full state change history of a transaction.**

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | OPERATOR, ADMIN |

**Response 200**
```json
[
  {
    "state_hist_id": "uuid",
    "txn_id": "uuid",
    "old_status": null,
    "new_status": "PENDING",
    "changed_at": "ISO8601",
    "changed_by_user_id": null
  },
  {
    "state_hist_id": "uuid",
    "txn_id": "uuid",
    "old_status": "PENDING",
    "new_status": "MANUAL_REVIEW",
    "changed_at": "ISO8601",
    "changed_by_user_id": "uuid"
  },
  {
    "state_hist_id": "uuid",
    "txn_id": "uuid",
    "old_status": "MANUAL_REVIEW",
    "new_status": "APPROVED",
    "changed_at": "ISO8601",
    "changed_by_user_id": "uuid"
  }
]
```

---

## UC05 – Case Management & Review

### GET /cases
**List review cases for current user (REVIEWER) or all (MANAGER).**

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | REVIEWER, MANAGER, ADMIN |

**Query Parameters**

| Param | Type | Description |
|---|---|---|
| `case_status` | string | Filter: OPEN, ASSIGNED, APPROVED, REJECTED, CLOSED |
| `assigned_to` | string | Filter by reviewer user_id |
| `page` | int | Page (default: 1) |
| `limit` | int | Per page (default: 20, max: 100) |

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
      "case_status": "OPEN",
      "assigned_to": null,
      "transaction": {
        "txn_id": "uuid",
        "amount": 350000000,
        "fraud_score": 0.61,
        "merchant_id": "uuid"
      },
      "created_at": "ISO8601"
    }
  ]
}
```

---

### GET /cases/{case_id}
**Get full case details with transaction and action history.**

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | REVIEWER, MANAGER, ADMIN |

**Response 200**
```json
{
  "case_id": "uuid",
  "txn_id": "uuid",
  "case_status": "ASSIGNED",
  "assigned_to": "uuid",
  "decision": null,
  "decision_note": null,
  "version": 1,
  "transaction": {
    "txn_id": "uuid",
    "customer_id": "uuid",
    "merchant_id": "uuid",
    "amount": 350000000,
    "fraud_score": 0.61,
    "txn_time": "ISO8601"
  },
  "created_at": "ISO8601",
  "decided_at": null
}
```

---

### POST /cases/{case_id}/assign
**Reviewer claims case for review (Assign to me).**

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | REVIEWER |

**Response 200**
```json
{
  "case_id": "uuid",
  "case_status": "ASSIGNED",
  "assigned_to": "uuid",
  "created_at": "ISO8601"
}
```

---

### PATCH /cases/{case_id}/decision
**Submit approval or rejection decision (merged endpoint).**

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | REVIEWER |

**Request Body**
```json
{
  "decision": "APPROVE | REJECT",
  "decision_note": "string (required)",
  "version": 1
}
```

**Response 200**
```json
{
  "case_id": "uuid",
  "txn_id": "uuid",
  "case_status": "CLOSED",
  "decision": "APPROVE",
  "decided_at": "ISO8601",
  "version": 2
}
```

---

## UC06 – Loan Management

### POST /loans
**Create new loan application.**

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | OPERATOR |

**Request Body**
```json
{
  "customer_id": "uuid",
  "principal_amount": 50000.00,
  "currency_code": "USD",
  "interest_rate": 0.075,
  "term_months": 24,
  "purpose": "Home improvement"
}
```

**Response 201 (Created)**
```json
{
  "loan_id": "uuid",
  "customer_id": "uuid",
  "status": "PENDING",
  "principal_amount": 50000.00,
  "interest_rate": 0.075,
  "term_months": 24,
  "pd_score": null,
  "risk_level": null,
  "created_at": "ISO8601"
}
```

---

### GET /loans
**List loans with filters. OPERATOR sees own; MANAGER/ADMIN see all.**

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | OPERATOR, MANAGER, ADMIN |

**Query Parameters**

| Param | Type | Description |
|---|---|---|
| `customer_id` | string | Filter by customer UUID |
| `status` | string | Filter: PENDING, SCORING, APPROVED, REJECTED, MANUAL_REVIEW |
| `page` | int | Page (default: 1) |
| `limit` | int | Per page (default: 20, max: 100) |

**Response 200**
```json
{
  "total": 120,
  "page": 1,
  "limit": 20,
  "data": [
    {
      "loan_id": "uuid",
      "customer_id": "uuid",
      "status": "PENDING",
      "principal_amount": 50000.00,
      "currency_code": "USD",
      "interest_rate": 0.075,
      "term_months": 24,
      "pd_score": null,
      "risk_level": null,
      "created_at": "ISO8601"
    }
  ]
}
```

---

### GET /loans/{loan_id}
**Get loan details.**

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | OPERATOR, MANAGER, ADMIN |

**Response 200**
```json
{
  "loan_id": "uuid",
  "customer_id": "uuid",
  "status": "APPROVED",
  "principal_amount": 50000.00,
  "currency_code": "USD",
  "interest_rate": 0.075,
  "term_months": 24,
  "purpose": "Home improvement",
  "pd_score": 0.134,
  "risk_level": "LOW RISK",
  "monthly_payment": 2195.63,
  "maturity_date": "2028-04-17",
  "created_at": "ISO8601",
  "reviewed_by": "uuid",
  "reviewed_at": "ISO8601"
}
```

---

### POST /loans/simulate
**Run AI loan approval simulation (PD Score prediction).**

| | |
|---|---|
| **Auth** | None (public endpoint) |
| **Roles** | All |

**Request Body**
```json
{
  "person_age": 36,
  "person_income": 65000.00,
  "person_home_ownership": "MORTGAGE",
  "person_emp_length": 8,
  "loan_amount": 50000.00,
  "loan_grade": "C",
  "loan_intent": "PERSONAL",
  "cb_person_default_on_file": "N",
  "cb_person_cred_hist_length": 10,
  "requested_term_months": 24
}
```

**Response 200**
```json
{
  "pd_score": 0.2814,
  "risk_level": "MEDIUM RISK",
  "decision": "MANUAL_REVIEW",
  "confidence": 0.92
}
```

---

### PATCH /loans/{loan_id}/decision
**Approve or reject loan application (MANAGER/ADMIN only).**

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | MANAGER, ADMIN |

**Request Body**
```json
{
  "decision": "APPROVE | REJECT",
  "review_note": "string",
  "version": 1
}
```

**Response 200**
```json
{
  "loan_id": "uuid",
  "status": "APPROVED",
  "decision": "APPROVE",
  "monthly_payment": 2195.63,
  "maturity_date": "2028-04-17",
  "reviewed_at": "ISO8601",
  "version": 2
}
```

---

## UC07 – Audit Logging

### GET /audit-logs
**List all audit events (MANAGER/ADMIN only).**

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | MANAGER, ADMIN |

**Query Parameters**

| Param | Type | Description |
|---|---|---|
| `event_type` | string | Filter by event type (e.g., TRANSACTION_SUBMITTED, CASE_APPROVED) |
| `entity_type` | string | Filter by entity: Transaction, User, ReviewCase, Loan |
| `actor_user_id` | string | Filter by actor user_id |
| `from_date` | ISO8601 | Start date |
| `to_date` | ISO8601 | End date |
| `page` | int | Page (default: 1) |
| `limit` | int | Per page (default: 20, max: 100) |

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
      "entity_type": "ReviewCase",
      "entity_id": "uuid",
      "actor_user_id": "uuid",
      "actor_name": "reviewer_01",
      "event_ts": "ISO8601",
      "detail_json": "{...}"
    }
  ]
}
```

---

### GET /audit-logs/entities/{entity_type}/{entity_id}
**Get complete audit trail for a specific entity.**

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | MANAGER, ADMIN |

**Path Parameters**

- `entity_type`: Transaction | User | ReviewCase | Loan
- `entity_id`: UUID of the entity

**Query Parameters**

| Param | Type | Description |
|---|---|---|
| `page` | int | Page (default: 1) |
| `limit` | int | Per page (default: 50, max: 200) |

**Response 200**
```json
{
  "total": 8,
  "page": 1,
  "limit": 50,
  "data": [
    {
      "log_id": "uuid",
      "event_type": "TRANSACTION_SUBMITTED",
      "entity_type": "Transaction",
      "entity_id": "uuid",
      "event_ts": "ISO8601",
      "detail_json": "{...}",
      "actor_user_id": "system",
      "actor_name": "System"
    },
    {
      "log_id": "uuid",
      "event_type": "CASE_ASSIGNED",
      "entity_type": "ReviewCase",
      "entity_id": "uuid",
      "event_ts": "ISO8601",
      "detail_json": "{...}",
      "actor_user_id": "uuid",
      "actor_name": "reviewer_01"
    }
  ]
}
```

---

### GET /audit-logs/{log_id}
**Get details of a specific audit event.**

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | MANAGER, ADMIN |

**Response 200**
```json
{
  "log_id": "uuid",
  "event_type": "CASE_APPROVED",
  "entity_type": "ReviewCase",
  "entity_id": "uuid",
  "actor_user_id": "uuid",
  "actor_name": "reviewer_01",
  "event_ts": "ISO8601",
  "detail_json": {
    "case_id": "uuid",
    "txn_id": "uuid",
    "decision": "APPROVE",
    "decision_note": "Xác nhận hợp lệ"
  }
}
```

---

## UC08 – Dashboard & Reports

### GET /dashboard/summary
**Real-time system overview dashboard.**

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | MANAGER, ADMIN |

**Response 200**
```json
{
  "total_transactions": 15042,
  "total_transaction_amount": 97500000000,
  "transactions_by_status": {
    "PENDING": 12,
    "APPROVED": 14800,
    "REJECTED": 120,
    "MANUAL_REVIEW": 110
  },
  "fraud_rate": 0.0816,
  "cases_pending": 23,
  "cases_assigned": 7,
  "total_loans": 342,
  "loans_by_status": {
    "PENDING": 15,
    "APPROVED": 280,
    "REJECTED": 47
  }
}
```

---

### GET /dashboard/fraud-trend
**Time-series fraud trend (last N days).**

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | MANAGER, ADMIN |

**Query Parameters**

| Param | Type | Description |
|---|---|---|
| `days` | int | Look back period (1-90, default: 30) |

**Response 200**
```json
{
  "period_days": 30,
  "data": [
    {
      "date": "2026-04-01",
      "total_txn": 320,
      "approved": 295,
      "rejected": 12,
      "manual_review": 13,
      "fraud_rate": 0.0781
    },
    {
      "date": "2026-04-02",
      "total_txn": 415,
      "approved": 384,
      "rejected": 18,
      "manual_review": 13,
      "fraud_rate": 0.0747
    }
  ]
}
```

---

### GET /reports/transactions
**Export transactions (CSV or JSON).**

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | MANAGER, ADMIN |

**Query Parameters**

| Param | Type | Description |
|---|---|---|
| `format` | string | Output: csv or json (default: json) |
| `status` | string | Filter by status |
| `from_date` | ISO8601 | Start date |
| `to_date` | ISO8601 | End date |

**Response 200 (JSON)**
```json
[
  {
    "txn_id": "uuid",
    "customer_id": "uuid",
    "merchant_id": "uuid",
    "amount": 1500000,
    "currency_code": "VND",
    "status": "APPROVED",
    "fraud_score": 0.12,
    "txn_time": "ISO8601"
  }
]
```

**Response 200 (CSV)**
```
Content-Type: text/csv
Content-Disposition: attachment; filename="transactions_2026-04-01_2026-04-17.csv"

txn_id,customer_id,merchant_id,amount,currency_code,status,fraud_score,txn_time
...
```

---

### GET /reports/fraud
**Export fraud summary report (by day).**

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | MANAGER, ADMIN |

**Query Parameters**

| Param | Type | Description |
|---|---|---|
| `format` | string | Output: csv or json (default: json) |
| `from_date` | ISO8601 | Start date |
| `to_date` | ISO8601 | End date |

**Response 200 (JSON)**
```json
[
  {
    "date": "2026-04-01",
    "total_txn": 320,
    "approved": 295,
    "rejected": 12,
    "manual_review": 13,
    "fraud_count": 25,
    "fraud_rate": 0.0781
  }
]
```

---

## UC09 – ETL Pipeline

### POST /etl/run
**Trigger ETL job for target date (ADMIN only).**

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ADMIN |

**Request Body**
```json
{
  "target_date": "2026-04-17",
  "job_type": "DAILY_SUMMARY"
}
```

**Response 201 (Created)**
```json
{
  "job_id": "uuid",
  "target_date": "2026-04-17",
  "job_type": "DAILY_SUMMARY",
  "status": "RUNNING",
  "started_at": "ISO8601"
}
```

---

### GET /etl/logs
**List ETL job history (ADMIN only).**

| | |
|---|---|
| **Auth** | Bearer Token |
| **Roles** | ADMIN |

**Query Parameters**

| Param | Type | Description |
|---|---|---|
| `job_type` | string | Filter by job type |
| `status` | string | Filter: SUCCESS, FAILED, RUNNING |
| `from_date` | ISO8601 | Start date |
| `page` | int | Page (default: 1) |
| `limit` | int | Per page (default: 20, max: 100) |

**Response 200**
```json
{
  "total": 120,
  "page": 1,
  "limit": 20,
  "data": [
    {
      "job_id": "uuid",
      "target_date": "2026-04-17",
      "job_type": "DAILY_SUMMARY",
      "status": "SUCCESS",
      "records_extracted": 1540,
      "records_transformed": 1538,
      "records_loaded": 1538,
      "started_at": "ISO8601",
      "completed_at": "ISO8601",
      "error_message": null
    }
  ]
}
```

---

## Common Conventions

### Standard Error Response

All errors follow this format:

```json
{
  "code": "ERROR_CODE",
  "message": "Human-readable error message",
  "path": "/api/v1/endpoint"
}
```

**HTTP Status Codes & Error Codes**

| HTTP | Code | Meaning |
|---|---|---|
| 400 | ValidationError | Input validation failed |
| 401 | UnauthorizedError | Missing/invalid JWT token |
| 403 | ForbiddenError | Insufficient permissions |
| 404 | NotFoundError | Resource not found |
| 409 | ConflictError | Optimistic lock version mismatch or idempotency conflict |
| 422 | UnprocessableError | Valid data but cannot process |
| 429 | RateLimitedError | Too many requests |
| 500 | InternalServerError | Server error |

### Pagination Response Format

All list endpoints return paginated responses:

```json
{
  "total": 1500,
  "page": 1,
  "limit": 20,
  "data": [...]
}
```

### Role-Based Access Control

| Module | OPERATOR | REVIEWER | MANAGER | ADMIN |
|---|:---:|:---:|:---:|:---:|
| Auth (login/logout/change-pw) | ✓ | ✓ | ✓ | ✓ |
| Auth (me/refresh) | ✓ | ✓ | ✓ | ✓ |
| User Management | – | – | Rо | Full |
| Transaction Submit | ✓ | – | – | – |
| Transaction View | ✓ | ✓ | ✓ | ✓ |
| Case Management | – | Full | Rо | Rо |
| Loan Submit | ✓ | – | – | – |
| Loan Approve | – | – | ✓ | ✓ |
| Audit Logs | – | – | ✓ | ✓ |
| Dashboard/Reports | – | – | ✓ | ✓ |
| ETL Pipeline | – | – | – | ✓ |

Legend: ✓ = Access, Rо = Read-only, Full = Create/Read/Update/Delete, – = No access

### Fraud Scoring Decision Logic

| fraud_score | Decision | Action |
|---|---|---|
| ≤ 0.30 | APPROVED | Auto-approved, no case created |
| 0.30 < score ≤ 0.70 | MANUAL_REVIEW | Create review case for REVIEWER |
| > 0.70 | REJECTED | Auto-rejected, no case created |
| Any, amount > 500M | MANUAL_REVIEW | Oracle trigger override (hard rule) |

### Optimistic Locking

Endpoints that update mutable resources (cases, loans) require `version` field in request to prevent lost updates:

```json
{
  "decision": "APPROVE",
  "version": 1
}
```

If current version doesn't match stored version, returns 409 Conflict.

### Timestamps

All timestamps use ISO 8601 format with timezone info:
- Example: `2026-04-17T06:49:20.029845Z`
- Always UTC (Z suffix)
- Client should convert to local timezone for display

---

## Key Implementation Notes

✅ **Implemented Endpoints:** 30+  
✅ **Database Backend:** Oracle 23ai Free on FREEPDB1  
✅ **ORM:** SQLAlchemy 2.0.49  
✅ **Authentication:** JWT Bearer tokens (access + refresh)  
✅ **Audit Trail:** Full event logging for all entity changes  
✅ **Fraud Scoring:** Random Forest v3_regularized model  
✅ **Loan Scoring:** XGBoost model with PD score prediction  
✅ **Idempotency:** ETL jobs, transaction submissions  
✅ **Optimistic Locking:** Case and loan decision endpoints  
✅ **Role-Based Access:** 4 roles (OPERATOR, REVIEWER, MANAGER, ADMIN)  

---

**Generated:** 2026-04-17  
**API Server:** http://localhost:8000  
**Swagger Docs:** http://localhost:8000/docs  
**ReDoc Docs:** http://localhost:8000/redoc
