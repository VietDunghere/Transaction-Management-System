# Transaction Management System

> Hệ thống quản lý giao dịch và kiểm soát gian lận cho ngân hàng/fintech. Xây dựng bằng **FastAPI + Oracle DB + AI Fraud Scoring**.

---

## 🎯 Tính năng chính

- ✅ **Xác thực & Phân quyền** — JWT-based, 4 roles (OPERATOR, REVIEWER, MANAGER, ADMIN)
- ✅ **Quản lý giao dịch** — Submit, phân luồng fraud, duyệt manual review
- ✅ **Case Management** — Assign → review → approve/reject với audit trail đầy đủ
- ✅ **Fraud Scoring** — AI-powered (hoặc rule-based), tự động phân luồng
- ✅ **Idempotency** — Tránh duplicate transaction khi retry
- ✅ **Audit Log & Traceability** — Ghi vết mọi hành động, truy vết giao dịch
- ✅ **Dashboard & Báo cáo** — Tổng quan, fraud ratio, export CSV/PDF
- ✅ **ETL Pipeline** — Extract từ Data Lake, transform, load vào Warehouse
- ✅ **Reconciliation** — So khớp dữ liệu OLTP ↔ Lake ↔ Warehouse
- ✅ **Loan Simulator** — PD Score, rủi ro tín dụng

---

## 📋 Yêu cầu

- **Python** 3.9+
- **Oracle Database** 18c+ (hoặc PostgreSQL dev)
- **Redis** (cho token blacklist, caching)
- **Docker** (optional, để dev dễ hơn)

---

## 🚀 Quick Start

### 1. Clone & setup environment

```bash
git clone https://github.com/VietDunghere/Transaction-Management-System.git
cd Transaction-Management-System

# Copy .env
cp .env.example .env

# Edit .env với database credentials
nano .env
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Chạy migrations (tạo bảng DB)

```bash
alembic upgrade head
```

### 4. Khởi động server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server chạy tại: `http://localhost:8000`

**API Documentation (Swagger):** `http://localhost:8000/docs`

---

## 🏗️ Cấu trúc dự án

```
Transaction-Management-System/
├── app/
│   ├── api/v1/routes/          # API endpoints (controller)
│   ├── schemas/                # Pydantic request/response models
│   ├── services/               # Business logic
│   ├── repositories/           # Database access layer
│   ├── models/                 # ORM models (SQLAlchemy)
│   ├── core/                   # Config, security, dependencies
│   ├── db/                     # Database setup, migrations
│   └── utils/                  # Helper functions
│
├── tests/                      # Unit & integration tests
├── db/                         # ER diagram, design docs
│
├── main.py                     # App entry point
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
├── Dockerfile                  # Docker build
├── docker-compose.yml          # Docker + DB stack
│
├── API_DESIGN.md               # Full API specification
├── API_SUMMARY.md              # Quick API reference (31 endpoints)
├── API_AUDIT.md                # 20 issues found + fixes
├── PROJECT_STRUCTURE.md        # Layer giải thích chi tiết
└── README.md                   # File này
```

Xem **[PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)** để hiểu cách sắp xếp từng layer.

---

## 🔐 Authentication

### Đăng nhập

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "operator1",
    "password": "password123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "user_id": "uuid",
    "username": "operator1",
    "role": "OPERATOR"
  }
}
```

### Sử dụng token

Thêm vào header tất cả request:
```bash
Authorization: Bearer <access_token>
```

---

## 📡 API Overview

**31 endpoints** chia thành 5 nhóm:

| Nhóm | Endpoints | Roles |
|---|---|---|
| **Auth** | login, logout, change-password, user management | Tất cả |
| **Transaction** | submit, list, detail, update status | OPERATOR, REVIEWER |
| **Case Management** | assign, approve, reject | REVIEWER |
| **Audit & Reports** | audit logs, export, dashboard, fraud chart | MANAGER, ADMIN |
| **Data Engineering** | ETL, reconciliation, data lake | ADMIN |

Xem **[API_DESIGN.md](./API_DESIGN.md)** để xem đầy đủ spec từng endpoint.

---

## 📊 Phân quyền (RBAC)

| Role | Quyền chính |
|---|---|
| **OPERATOR** | Submit transaction, submit loan, xem giao dịch của mình |
| **REVIEWER** | Assign case, approve/reject, xem case |
| **MANAGER** | Xem dashboard, báo cáo, audit log, reconciliation |
| **ADMIN** | Quản lý user, ETL, data lake, reconciliation |

---

## 🏭 Luồng xử lý giao dịch

```
1. OPERATOR gửi transaction → POST /api/v1/transactions/submit

2. Hệ thống:
   - ✓ Validate input
   - ✓ Kiểm tra idempotency (avoid duplicate)
   - ✓ Chạy AI fraud scoring → fraud_score (0.0-1.0)
   - ✓ Phân luồng:
     • fraud_score ≤ 0.30 → APPROVED (tự động)
     • 0.30 < score ≤ 0.70 → MANUAL_REVIEW (tạo case)
     • score > 0.70 → REJECTED (tự động)
   - ✓ Ghi audit log

3. Nếu MANUAL_REVIEW → tạo case, REVIEWER nhận & duyệt

4. Kết quả cuối → ghi vào Warehouse, Data Lake

5. Cuối ngày → chạy reconciliation (so khớp OLTP ↔ Lake ↔ Warehouse)
```

---

## 🧪 Testing

### Chạy unit test

```bash
pytest tests/ -v

# Test cụ thể
pytest tests/test_auth.py -v
pytest tests/test_transaction.py::test_submit_transaction -v
```

### Coverage report

```bash
pytest tests/ --cov=app --cov-report=html
```

---

## 🐳 Docker

### Dev stack (app + Oracle)

```bash
docker-compose up -d
```

Mở http://localhost:8000/docs để test API.

---

## 📝 Commit Convention

```bash
# Feature
git commit -m "feat: add fraud scoring endpoint"

# Bug fix
git commit -m "fix: optimistic lock race condition in case assign"

# Docs
git commit -m "docs: update API_AUDIT.md"

# Refactor
git commit -m "refactor: extract fraud logic to service layer"

# Test
git commit -m "test: add integration test for transaction submit"
```

---

## 🚨 Critical Issues Found

Audit đã tìm ra **20 issues**:

- **🔴 5 Critical:** Data isolation, optimistic locking, state machine, audit trail, self-disable
- **🟡 7 High:** Idempotency spec, card masking, HTTP methods, race condition
- **🟢 8 Medium:** Missing endpoints, naming inconsistency

Xem **[API_AUDIT.md](./API_AUDIT.md)** để chi tiết + cách fix từng vấn đề.

---

## 📚 Tài liệu

| File | Nội dung |
|---|---|
| **[PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)** | Chi tiết từng layer MVC, luồng request |
| **[API_DESIGN.md](./API_DESIGN.md)** | Full spec 31 endpoints + error codes |
| **[API_SUMMARY.md](./API_SUMMARY.md)** | Quick reference bảng tổng hợp |
| **[API_AUDIT.md](./API_AUDIT.md)** | 20 vấn đề tìm được + fix |
| **[USECASE.md](./USECASE.md)** | Use case diagram + actor descriptions |
| **[db/](./db/)** | ER diagram (Oracle Data Modeler) |

---

## 🤝 Contributing

1. Fork repo
2. Tạo branch: `git checkout -b feature/your-feature`
3. Commit: `git commit -m "feat: ..."`
4. Push: `git push origin feature/your-feature`
5. Tạo Pull Request

**Lưu ý:**
- Tất cả feature phải pass tests
- API changes cần update `API_DESIGN.md`
- Follow commit convention trên

---

## 📞 Support

- 📖 Tài liệu: [docs/](./docs/)
- 🐛 Report bug: [GitHub Issues](https://github.com/VietDunghere/Transaction-Management-System/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/VietDunghere/Transaction-Management-System/discussions)

---

## 📄 License

MIT License — Xem [LICENSE](./LICENSE) để chi tiết.

---

**Bắt đầu dev:** Làm theo [Quick Start](#-quick-start) → Đọc [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) → Xem [API_DESIGN.md](./API_DESIGN.md) → Code!

Happy coding! 🚀
