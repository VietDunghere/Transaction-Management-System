# Cấu trúc dự án – Transaction Management System (FastAPI MVC)

> Dự án theo mô hình **MVC biến thể** phổ biến trong FastAPI:
> **Route (Controller) → Service (Logic) → Repository (DB) → Model (Schema DB)**

---

## Sơ đồ thư mục

```
Transaction-Management-System/
│
├── main.py                     # Điểm khởi động ứng dụng FastAPI
├── requirements.txt            # Danh sách thư viện Python cần cài
├── .env.example                # Mẫu biến môi trường (copy → .env)
├── Dockerfile                  # Build Docker image cho app
├── docker-compose.yml          # Chạy app + DB cùng lúc bằng Docker
│
├── app/                        # Toàn bộ mã nguồn chính
│   ├── api/                    # (Controller) Định nghĩa các endpoint HTTP
│   │   └── v1/
│   │       └── routes/         # Mỗi file = 1 nhóm API
│   │           ├── auth.py           # /auth/login, /auth/logout, /auth/change-password
│   │           ├── transaction.py    # /transaction/submit, GET /transaction, PATCH status
│   │           ├── cases.py          # /cases – Case Management
│   │           ├── audit_logs.py     # /audit-logs, /audit-logs/export
│   │           ├── dashboard.py      # /dashboard/summary, /dashboard/fraud-chart
│   │           ├── reports.py        # /reports/transactions, /reports/transactions/export
│   │           ├── loan.py           # /loan/submit – Loan Simulator
│   │           ├── datalake.py       # /datalake/structure
│   │           ├── etl.py            # /etl/trigger, /etl/logs
│   │           └── reconciliation.py # /reconciliation/run, /reconciliation/jobs
│   │
│   ├── core/                   # Cấu hình & bảo mật toàn cục
│   │   ├── config.py           # Đọc biến môi trường (.env): DB URL, JWT secret, v.v.
│   │   ├── security.py         # Tạo/giải mã JWT token, hash mật khẩu
│   │   └── dependencies.py     # Dependency injection: get_current_user, require_role(...)
│   │
│   ├── models/                 # (Model) Định nghĩa bảng DB qua ORM (SQLAlchemy)
│   │   ├── user.py             # Bảng USERS
│   │   ├── transaction.py      # Bảng TRANSACTIONS_LIVE
│   │   ├── case.py             # Bảng CASES
│   │   ├── audit_log.py        # Bảng AUDIT_LOGS
│   │   ├── loan.py             # Bảng LOAN_APPLICATIONS
│   │   ├── etl_log.py          # Bảng ETL_JOB_LOGS
│   │   └── reconciliation.py   # Bảng RECONCILIATION_JOBS
│   │
│   ├── schemas/                # Pydantic – Validate dữ liệu vào/ra API
│   │   ├── common.py           # Schema dùng chung: PaginatedResponse, ErrorResponse
│   │   ├── user.py             # UserCreate, UserResponse, RoleUpdate
│   │   ├── transaction.py      # TransactionSubmit, TransactionResponse
│   │   ├── case.py             # CaseResponse, CaseDecision
│   │   ├── audit_log.py        # AuditLogResponse, AuditTraceResponse
│   │   ├── loan.py             # LoanSubmit, LoanResponse
│   │   ├── etl.py              # ETLTriggerRequest, ETLLogResponse
│   │   └── reconciliation.py   # ReconRequest, ReconJobResponse
│   │
│   ├── services/               # (Service) Xử lý logic nghiệp vụ
│   │   ├── auth_service.py         # Đăng nhập, đổi mật khẩu, tạo/hủy token
│   │   ├── transaction_service.py  # Submit giao dịch, phân luồng fraud score
│   │   ├── case_service.py         # Assign/approve/reject case
│   │   ├── audit_service.py        # Ghi & truy vấn audit log
│   │   ├── fraud_service.py        # Tính fraud score (AI/rule-based)
│   │   ├── loan_service.py         # Tính PD score, phân loại rủi ro
│   │   ├── etl_service.py          # Điều phối ETL pipeline
│   │   └── reconciliation_service.py # So khớp dữ liệu OLTP/Lake/Warehouse
│   │
│   ├── repositories/           # (Repository) Truy vấn DB – tách biệt khỏi logic
│   │   ├── user_repo.py            # CRUD Users
│   │   ├── transaction_repo.py     # CRUD Transactions, lọc/phân trang
│   │   ├── case_repo.py            # CRUD Cases
│   │   ├── audit_repo.py           # Insert & query Audit Logs
│   │   ├── loan_repo.py            # CRUD Loan Applications
│   │   ├── etl_repo.py             # Ghi & đọc ETL Job Logs
│   │   └── reconciliation_repo.py  # Ghi & đọc Reconciliation Jobs
│   │
│   ├── db/                     # Kết nối cơ sở dữ liệu
│   │   ├── database.py         # Tạo engine, session, Base cho SQLAlchemy
│   │   └── migrations/         # File migration Alembic (tạo/sửa bảng DB)
│   │
│   └── utils/                  # Hàm tiện ích dùng chung
│       ├── hashing.py          # bcrypt hash & verify mật khẩu
│       ├── jwt.py              # Tạo và decode JWT token
│       ├── fraud_scorer.py     # Logic tính fraud score (mock AI hoặc rule)
│       └── report_exporter.py  # Xuất file CSV / PDF cho báo cáo
│
├── tests/                      # Unit test & integration test
│   ├── test_auth.py            # Test đăng nhập, phân quyền
│   ├── test_transaction.py     # Test submit giao dịch, idempotency
│   ├── test_cases.py           # Test assign/approve/reject case
│   └── test_audit.py           # Test ghi và truy vết audit log
│
└── db/                         # File ERD và thiết kế DB (Oracle Data Modeler)
```

---

## Giải thích từng tầng (Layer)

### `app/api/v1/routes/` – Controller
> **Nhận request từ client, gọi Service, trả response.**
> Không chứa logic nghiệp vụ. Chỉ validate input (qua Schema) và điều hướng.

### `app/schemas/` – Request / Response Shape
> **Pydantic models định nghĩa dữ liệu hợp lệ vào/ra.**
> FastAPI tự động validate và sinh docs (Swagger UI) từ đây.

### `app/services/` – Business Logic
> **Nơi xử lý toàn bộ nghiệp vụ**: phân luồng fraud score, ghi audit log, orchestrate ETL.
> Gọi Repository để lấy/lưu dữ liệu, không tự truy vấn DB trực tiếp.

### `app/repositories/` – Data Access
> **Chỉ làm 1 việc: truy vấn DB.**
> Tách tầng này giúp dễ test (mock repo) và dễ đổi DB sau này.

### `app/models/` – ORM Models
> **Ánh xạ 1-1 với bảng trong Oracle DB.**
> Dùng SQLAlchemy để định nghĩa cột, kiểu dữ liệu, quan hệ khoá ngoại.

### `app/core/` – Cấu hình trung tâm
> `config.py` → đọc `.env`
> `security.py` → JWT + bcrypt
> `dependencies.py` → `get_current_user()`, `require_role("ADMIN")` dùng trong mọi route

### `app/utils/` – Tiện ích
> Các hàm độc lập, không phụ thuộc framework: hash, JWT helpers, xuất file.

### `tests/` – Kiểm thử
> Mỗi file test tương ứng 1 module. Dùng `pytest` + `httpx` để test endpoint.

---

## Luồng xử lý một request điển hình

```
Client
  │
  ▼
[Route] app/api/v1/routes/transaction.py
  │  Validate input qua TransactionSubmit schema
  ▼
[Service] app/services/transaction_service.py
  │  Kiểm tra idempotency → gọi fraud_service → phân luồng → ghi audit log
  ▼
[Repository] app/repositories/transaction_repo.py
  │  INSERT / SELECT vào Oracle DB
  ▼
[Model] app/models/transaction.py
  │  SQLAlchemy ORM ↔ bảng TRANSACTIONS_LIVE
  ▼
[Schema] TransactionResponse → JSON trả về Client
```

---

## Phân quyền nhanh

| Role | Quyền chính |
|---|---|
| `OPERATOR` | Submit giao dịch, submit loan, xem giao dịch của mình |
| `REVIEWER` | Duyệt/từ chối case MANUAL_REVIEW |
| `MANAGER` | Xem dashboard, báo cáo, audit log, reconciliation |
| `ADMIN` | Toàn quyền: quản lý user, ETL, data lake |
