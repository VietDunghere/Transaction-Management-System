# Transaction Management System (TMS)

## 🎯 Dự án này làm gì?

**Transaction Management System** là một nền tảng xử lý và quản lý giao dịch tài chính cho các ngân hàng, fintech, hoặc tổ chức tín dụng. Nó tự động phát hiện gian lận, quản lý luồng duyệt, và đảm bảo tính toàn vẹn dữ liệu qua ETL pipeline.

### Vấn đề nó giải quyết

Mỗi ngày, ngân hàng xử lý **hàng triệu giao dịch**. Nhưng không phải tất cả đều sạch:

- 🚨 **Gian lận** — Ai gửi từ IP lạ? Card bị clone? Số tiền bất thường?
- 🔍 **Duyệt chậm** — Reviewer nhân viên phải xem từng giao dịch bằng tay → tắc nghẽn, chậm chạp
- 📊 **Kiểm soát kém** — Không biết ai duyệt cái gì, lúc nào, lý do gì → không compliance được
- 💾 **Dữ liệu rối** — Data ở nhiều chỗ (OLTP DB, raw logs, warehouse) → khó so khớp, dễ mất dữ liệu
- 📈 **Báo cáo thủ công** — Quản lý phải chờ dev tạo báo cáo, chậm khi cần insight nhanh

### Giải pháp

TMS **tự động hóa toàn bộ flow** này:

1. **Tiếp nhận giao dịch** — OPERATOR gửi giao dịch via API
2. **Kiểm tra tự động** — Hệ thống AI chấm điểm rủi ro (fraud score)
3. **Phân luồng thông minh:**
   - ✅ Score thấp → **Approve tự động** (không cần duyệt)
   - ⚠️ Score trung bình → **Tạo case, gửi REVIEWER duyệt**
   - ❌ Score cao → **Reject tự động**
4. **Duyệt có quy trình** — REVIEWER nhận case → xem xét → approve/reject (với ghi chú lý do)
5. **Kiểm soát đầy đủ** — Mọi hành động đều được **ghi audit log** — ai duyệt, lúc nào, lý do gì
6. **Đảm bảo dữ liệu** — ETL tự động extract từ raw logs → transform → load vào warehouse để phân tích
7. **Kiểm tra tính nhất quán** — Cuối ngày tự động **so khớp** dữ liệu giữa OLTP, Data Lake, Warehouse

---

## 👥 Ai dùng nó?

### 1. **OPERATOR** — Nhân viên vận hành
   - Gửi giao dịch/đơn vay demo vào hệ thống
   - Xem kết quả xử lý (approved/rejected/manual review)
   - Không cần biết backend hoạt động thế nào, chỉ gửi → xem kết quả

### 2. **REVIEWER** — Nhân viên duyệt
   - Nhìn danh sách case cần duyệt (giao dịch bị flag = "cần xem xét")
   - Nhận case, xem chi tiết (amount, fraud score, metadata)
   - Quyết định: approve hay reject, bắt buộc ghi lý do
   - Hành động được ghi lại → có trách nhiệm

### 3. **MANAGER** — Quản lý
   - Xem dashboard tổng quan: bao nhiêu giao dịch, fraud rate bao nhiêu, case nào đang chờ
   - Xem biểu đồ fraud vs legitimate giao dịch theo ngày/tuần
   - Truy vết giao dịch: "Giao dịch này đã được duyệt bởi ai, khi nào, vì sao?"
   - Export báo cáo cho compliance/audit

### 4. **ADMIN** — Quản trị hệ thống
   - Quản lý user (tạo, disable tài khoản)
   - Trigger ETL pipeline thủ công nếu cần
   - Chạy đối soát (reconciliation) để kiểm tra dữ liệu đúng không
   - Xem log chi tiết nếu có vấn đề

---

## 🔑 Các tính năng chính

### 1️⃣ Xác thực & Phân quyền (Authentication & RBAC)
- Đăng nhập JWT token
- 4 roles khác nhau (OPERATOR, REVIEWER, MANAGER, ADMIN)
- Mỗi role chỉ xem/làm những gì được phép

### 2️⃣ Fraud Detection (Phát hiện gian lận)
- AI chấm điểm rủi ro (fraud_score: 0.0 → 1.0)
- Tự động phân luồng:
  - Score ≤ 0.3 → APPROVED
  - 0.3 < Score ≤ 0.7 → MANUAL_REVIEW (cần Reviewer duyệt)
  - Score > 0.7 → REJECTED
- Có thể cấu hình rule-based hoặc ML-based

### 3️⃣ Case Management (Quản lý case duyệt)
- Tự động tạo case khi giao dịch cần manual review
- Reviewer assign case cho mình
- Duyệt (approve) hay từ chối (reject) với bắt buộc ghi lý do
- Trạng thái case được track: OPEN → ASSIGNED → APPROVED/REJECTED

### 4️⃣ Idempotency (Tránh xử lý lặp lại)
- Client retry giao dịch bị lỗi → hệ thống nhận ra nó lặp
- Trả lại kết quả cũ, không xử lý lại
- Tránh double-charge, double-debit

### 5️⃣ Audit Log & Traceability (Ghi vết mọi hành động)
- Mọi thay đổi đều được ghi: ai làm, khi nào, giao dịch nào, thay đổi từ gì sang gì
- Truy vết toàn bộ lịch sử giao dịch (timeline từ tạo → duyệt → kết quả)
- Xuất báo cáo audit ra file (CSV, PDF) cho compliance

### 6️⃣ Dashboard & Reports (Tổng quan & báo cáo)
- Dashboard tổng quan: số giao dịch, fraud rate, case pending
- Biểu đồ fraud vs legitimate theo ngày/tuần/tháng
- Báo cáo chi tiết: số lượng, tổng tiền, tỷ lệ approved/rejected/manual
- Export file cho phân tích thêm

### 7️⃣ ETL Pipeline (Xử lý dữ liệu lớn)
- Extract: đọc raw logs từ Data Lake (file CSV theo ngày)
- Transform: làm sạch dữ liệu, bổ sung (GeoIP enrichment, dedup)
- Load: đưa vào Warehouse (OLAP) để phân tích
- Ghi log ETL job (thành công/lỗi, bao nhiêu row xử lý)

### 8️⃣ Reconciliation (Kiểm tra tính nhất quán)
- So khớp dữ liệu giữa 3 nguồn:
  - OLTP DB (database chính)
  - Data Lake (raw logs)
  - Warehouse (OLAP)
- Kiểm tra: COUNT(*) và SUM(amount) có khớp không
- Nếu lệch → tạo báo cáo chi tiết chênh lệch

### 9️⃣ Loan Approval Simulator (Mô phỏng cho vay)
- Nhập thông tin applicant (income, credit score, job type, v.v)
- Hệ thống ML tính PD score (Probability of Default)
- Phân loại rủi ro: LOW, MEDIUM, HIGH

---

## 🏗️ Kiến trúc tổng thể

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT (Web/Mobile)                  │
│  OPERATOR / REVIEWER / MANAGER / ADMIN                  │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (TMS)                       │
│  - Routes (API endpoints)                               │
│  - Services (Business logic)                            │
│  - Repositories (Database access)                       │
│  - Models (ORM)                                         │
│  - Fraud Scoring Engine                                 │
│  - Audit Logger                                         │
│  - ETL Orchestrator                                     │
└─────────────────────────────────────────────────────────┘
                    ↓         ↓          ↓
          ┌─────────┴────┬────┴───┬─────┘
          ↓              ↓        ↓
    ┌──────────┐  ┌──────────┐  ┌─────────┐
    │ OLTP DB  │  │Data Lake │  │Warehouse│
    │(Oracle)  │  │(Raw CSV) │  │ (OLAP)  │
    └──────────┘  └──────────┘  └─────────┘
          ↑         (Extract)      (Load)
          │            ↑ ↓           ↓
          └────────────ETL────────Transform─────┘

          ┌──────────────────────────────┐
          │  Reconciliation Job (Daily)  │
          │  (So khớp 3 nguồn dữ liệu)  │
          └──────────────────────────────┘
```

---

## 📊 Ví dụ flow thực tế

### Scenario: OPERATOR gửi giao dịch

```
10:00:00 — OPERATOR submit transaction
  {
    "card_number": "4111111111111111",
    "amount": 350,000,000 VND,
    "merchant_id": "AEON_MALL_001",
    "txn_time": "2026-04-07T10:00:00Z"
  }

10:00:01 — Backend xử lý:
  ✓ Validate: card có format đúng? amount > 0? merchant tồn tại?
  ✓ Check idempotency: giao dịch này đã xử lý chưa?
  ✓ AI fraud scoring:
     - Giờ giao dịch: 10:00 (bình thường)
     - Amount: 350M (cao, nhưng có quy mô)
     - Card history: OK, không bất thường trước đó
     → fraud_score = 0.45 (trung bình)

  Phân luồng: 0.45 → MANUAL_REVIEW (cần Reviewer duyệt)

  ✓ Tạo case mới
  ✓ Ghi audit log: "TXN-001 created, AI scored 0.45 → MANUAL_REVIEW"

10:00:02 — Trả response về OPERATOR:
  {
    "txn_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "MANUAL_REVIEW",
    "fraud_score": 0.45,
    "reason_code": "MANUAL_REQUIRED",
    "processed_at": "2026-04-07T10:00:01Z"
  }

10:05:00 — REVIEWER A log in, thấy danh sách case chờ duyệt
           → Assign case TXN-001 cho mình

10:10:00 — REVIEWER A xem chi tiết case:
           - Amount: 350M (hợp lý cho AEON MALL)
           - Card history: OK
           - Fraud score: 0.45 (không quá cao)
           → Quyết định: APPROVE

           Ghi chú bắt buộc: "Lịch sử card tốt, amount hợp lý,
                             merchant tin cậy → approved"

           ✓ Ghi audit log: "CASE-001 approved by reviewer_a at 10:10:00
                              reason: Lịch sử card tốt, amount hợp lý..."

10:10:01 — Transaction status tự động cập nhật:
           MANUAL_REVIEW → APPROVED

10:11:00 — MANAGER xem dashboard:
           - Tổng hôm nay: 2,500 transactions
           - Fraud rate: 8.2%
           - Cases pending: 23 (đang chờ Reviewer)
           - Trend: fraud rate tăng nhẹ so với hôm qua

22:00:00 — ETL job chạy tự động (cuối ngày):
           ✓ Extract: đọc tất cả raw logs hôm nay từ /datalake/2026-04-07/
           ✓ Transform: dedup, clean, enrich GeoIP
           ✓ Load: insert vào FACT_TRANSACTIONS + DIM tables
           ✓ Ghi ETL log: "Job completed: 2,500 rows loaded, 2 errors"

23:00:00 — Reconciliation job chạy:
           ✓ OLTP count: 2,500 ✓ Lake count: 2,500 ✓ Warehouse: 2,500
           ✓ OLTP sum: 5.8B VND ✓ Lake: 5.8B VND ✓ Warehouse: 5.8B VND
           → Status: MATCH (tất cả đều khớp)

Sáng hôm sau — MANAGER xem báo cáo cuối ngày:
              - Tổng doanh số: 5.8B VND
              - Số giao dịch: 2,500
              - Fraud rate: 8.2% (210 giao dịch)
              - Reconciliation: ✓ MATCH (dữ liệu toàn vẹn)
              → Export báo cáo PDF gửi compliance
```

---

## 🎓 Tại sao dự án này quan trọng?

### Cho Business:
- ⚡ **Nhanh** — AI tự động approve/reject 90% giao dịch, không cần Reviewer → xử lý nhanh hơn
- 🛡️ **An toàn** — Phát hiện gian lận sớm, giảm loss
- 📊 **Minh bạch** — Audit log đầy đủ, có trách nhiệm → compliance dễ
- 💾 **Đáng tin** — Reconciliation đảm bảo dữ liệu không bị mất/sai

### Cho Dev (người học):
- 🏗️ **Kiến trúc clean** — FastAPI MVC, tách layers rõ ràng
- 🔐 **Security chuẩn** — JWT, role-based access, SQL injection prevention
- 📈 **Scale được** — ETL pipeline, Warehouse, async jobs
- 🧪 **Best practices** — Idempotency, optimistic locking, audit trail
- 📚 **Full cycle** — Từ API design → code → test → deploy

---

## 📖 Documentation

- **[API_DESIGN.md](./API_DESIGN.md)** — Spec chi tiết 31 endpoints
- **[API_SUMMARY.md](./API_SUMMARY.md)** — Quick reference bảng tóm tắt
- **[API_AUDIT.md](./API_AUDIT.md)** — 20 issues tìm được + cách fix
- **[PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)** — Cấu trúc folder, từng layer làm gì
- **[USECASE.md](./USECASE.md)** — Use case diagram, actor behavior
- **[db/](./db/)** — ER diagram (Oracle Data Modeler)

---

## 🚀 Bắt đầu

```bash
# 1. Clone repo
git clone https://github.com/VietDunghere/Transaction-Management-System.git

# 2. Setup environment
cp .env.example .env
nano .env  # Edit database credentials

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run database migrations
alembic upgrade head

# 5. Start server
uvicorn main:app --reload

# 6. Open Swagger docs
# http://localhost:8000/docs
```

---

## 📞 Questions?

- 📖 Tài liệu đầy đủ: xem mục [Documentation](#-documentation)
- 🐛 Found a bug? [GitHub Issues](https://github.com/VietDunghere/Transaction-Management-System/issues)
- 💬 Questions? [GitHub Discussions](https://github.com/VietDunghere/Transaction-Management-System/discussions)

---

**Tóm tắt:** TMS là một hệ thống **production-ready** xử lý giao dịch tài chính, tự động phát hiện gian lận, quản lý duyệt, và đảm bảo tính toàn vẹn dữ liệu. Nó kết hợp **frontend API design**, **backend architecture tốt**, và **data engineering pattern** — là một ví dụ hoàn chỉnh cho việc xây dựng hệ thống tài chính thực tế.
