## **CHANGELOG – Thay đổi so với phiên bản cũ**

| # | Vị trí | Cũ | Mới |
|---|---|---|---|
| 1 | UC01 – OPERATOR | Endpoint loan: `POST /api/v1/loans/submit` | `POST /api/v1/loans` |
| 2 | UC01 – AI Engine | Loan model: "Random Forest" | XGBoost (loan), Random Forest (fraud) |
| 3 | UC03 – Phân luồng fraud | `≤ 0.3 → APPROVED`, `> 0.7 → REJECTED` | `< 0.35 → APPROVED`, `≥ 0.65 → REJECTED` |
| 4 | UC04 – OPERATOR | Endpoint: `POST /api/v1/loans/submit`, body cũ có `applicant_id`, `credit_score`, `employment_type` | `POST /api/v1/loans`, body dùng `customer_id`, `person_age`, `person_income`, `loan_grade`, v.v. |
| 5 | UC04 – OPERATOR | Hệ thống trả về `risk_grade` ngay lập tức | Tạo đơn ở trạng thái **PENDING**, `pd_score` tính ngay khi nộp |
| 6 | UC04 – REVIEWER | Chỉ xem danh sách hồ sơ vay | Phê duyệt / từ chối đơn vay: `PATCH /api/v1/loans/{loan_id}/decision` |
| 7 | UC04 – Access | Tạo đơn vay: chỉ OPERATOR | Vẫn chỉ OPERATOR — MANAGER/ADMIN không tạo đơn (thiết kế 1-bank) |
| 8 | UC04 | Thiếu endpoint mô phỏng | Thêm `POST /api/v1/loans/simulate` (không lưu DB) |
| 9 | UC07 | Endpoint: `GET /transactions/{txn_id}/states` | `GET /transactions/{txn_id}/state-history` |
| 10 | UC06 – Admin | Endpoint: `POST /api/v1/etl/trigger` | `POST /api/v1/etl/run` |
| 11 | Toàn bộ | Thiếu SSE Stream | Thêm UC08 – SSE Real-time Stream |
| 12 | UC04 – SoD | Thiếu kiểm tra phân tách trách nhiệm | REVIEWER/MANAGER không được phê duyệt đơn vay do chính mình tạo (4-eyes principle) |
| 13 | UC05 – REVIEWER list | REVIEWER bị auto-filter `assigned_to=self` → không thấy OPEN cases | REVIEWER thấy tất cả OPEN cases (queue nhận việc) + cases của mình |
| 14 | UC05 – Case decide | Case OPEN có thể bị quyết định trực tiếp | Case phải ở trạng thái ASSIGNED trước khi có thể quyết định |
| 15 | UC05 – ADMIN decide | ADMIN bị chặn khi decide case không phải của mình | ADMIN bypass như MANAGER (giám sát override) |
| 16 | UC03 – State history | OPERATOR xem được state-history của mọi giao dịch | OPERATOR xem tất cả — hệ thống 1 ngân hàng duy nhất, không phân tách dữ liệu |

---

## **UC01 – TỔNG QUAN HỆ THỐNG**

### **Mô tả Actor – Hành động**

**Operator (Nhân viên Vận hành)**

* Đăng nhập hệ thống bằng tài khoản được cấp, nhận JWT token.
* Xem thông tin tài khoản cá nhân (UC-AUTH-10).
* Gửi giao dịch demo vào hệ thống qua API (`POST /api/v1/transactions/submit`) hoặc Postman với dữ liệu mô phỏng (card\_number, amount, merchant\_id...).
* Gửi đơn vay demo thông qua Loan API (`POST /api/v1/loans`). *(~~Cũ: `/loans/submit`~~)*
* Xem danh sách giao dịch và kết quả xử lý (APPROVED / REJECTED / MANUAL\_REVIEW).
* Xem danh sách đơn vay và trạng thái phê duyệt (PENDING / APPROVED / REJECTED).

**Reviewer (Nhân viên Duyệt)**

* Đăng nhập hệ thống.
* Xem thông tin tài khoản cá nhân (UC-AUTH-10).
* Xem danh sách case cần duyệt – các giao dịch có status = MANUAL\_REVIEW.
* Duyệt hoặc từ chối giao dịch qua Case flow, kèm ghi chú lý do quyết định.
* Xem danh sách giao dịch để theo dõi tổng quan (thấy tất cả giao dịch, không bị lọc theo submitted\_by).

**Manager (Quản lý)**

* Đăng nhập hệ thống.
* Xem thông tin tài khoản cá nhân (UC-AUTH-10).
* Xem Dashboard tổng quan: biểu đồ tỷ lệ Fraud/Legit, thống kê theo ngày/tuần.
* Xem báo cáo tổng hợp từ Data Warehouse (OLAP).
* Xem Audit Log – theo dõi ai đã làm gì, khi nào, trên entity nào.
* Truy vết giao dịch – xem toàn bộ lịch sử trạng thái của một giao dịch cụ thể.
* Xem danh sách người dùng (chỉ đọc).

**Admin (Quản trị viên)**

* Đăng nhập hệ thống.
* Xem thông tin tài khoản cá nhân (UC-AUTH-10).
* Quản lý người dùng – tạo, vô hiệu hóa, kích hoạt lại tài khoản nhân viên (không được tự vô hiệu hóa chính mình).
* Phân quyền RBAC – gán vai trò (Operator, Reviewer, Manager, Admin) cho user.
* Chạy đối soát (Reconciliation) – so khớp dữ liệu giữa OLTP, Data Lake, Warehouse.
* Xem Dashboard tổng quan.

**Hệ thống AI (AI Engine)**

* Tự động chấm điểm rủi ro giao dịch (Fraud Scoring) – nhận dữ liệu giao dịch, chạy model **Random Forest (10 cây)**, trả về fraud\_score trong tập `{0.3, 0.4, 0.5, 0.6, 0.7}`.
* Tự động chấm điểm tín dụng (PD Score) – nhận thông tin đơn vay, chạy model **XGBoost**, trả về pd\_score (0.0–1.0) và risk\_level (LOW / MEDIUM / HIGH). *(~~Cũ: "Random Forest"~~)*

**Hệ thống ETL (ETL Scheduler)**

* Tự động chạy ETL Pipeline – Extract CSV từ Data Lake, Transform (clean, enrich), Load vào Warehouse.

---

## **UC02 – XÁC THỰC VÀ PHÂN QUYỀN**

### **Mô tả Actor – Hành động**

**Operator (Nhân viên Vận hành)**

* Đăng nhập hệ thống (UC-AUTH-01): nhập username + password, hệ thống trả JWT access token + refresh token nếu hợp lệ.
* Refresh token (UC-AUTH-13): `POST /api/v1/auth/refresh` — lấy access token mới khi hết hạn mà không cần đăng nhập lại. *(Mới)*
* Đăng xuất (UC-AUTH-03): hủy phiên làm việc phía client.
* Xem thông tin cá nhân (UC-AUTH-10): `GET /api/v1/auth/me`.
* Đổi mật khẩu (UC-AUTH-04): `PATCH /api/v1/auth/change-password`.

**Reviewer (Nhân viên Duyệt)**

* Đăng nhập hệ thống (UC-AUTH-01): JWT chứa role = REVIEWER.
* Refresh token (UC-AUTH-13).
* Đăng xuất (UC-AUTH-03).
* Xem thông tin cá nhân (UC-AUTH-10).
* Đổi mật khẩu (UC-AUTH-04).

**Manager (Quản lý)**

* Đăng nhập hệ thống (UC-AUTH-01): JWT chứa role = MANAGER.
* Refresh token (UC-AUTH-13).
* Đăng xuất (UC-AUTH-03).
* Xem thông tin cá nhân (UC-AUTH-10).
* Xem danh sách người dùng (UC-AUTH-08): xem tất cả tài khoản trong hệ thống (chỉ đọc).
* Xem chi tiết người dùng (UC-AUTH-11).

**Admin (Quản trị viên)**

* Đăng nhập hệ thống (UC-AUTH-01): JWT chứa role = ADMIN – quyền cao nhất.
* Refresh token (UC-AUTH-13).
* Đăng xuất (UC-AUTH-03).
* Xem thông tin cá nhân (UC-AUTH-10).
* Tạo tài khoản người dùng (UC-AUTH-05).
* Vô hiệu hóa tài khoản (UC-AUTH-06). **Ràng buộc: không được tự vô hiệu hóa chính mình.**
* Kích hoạt lại tài khoản (UC-AUTH-12): `PATCH /api/v1/users/{user_id}/enable`.
* Gán vai trò (UC-AUTH-07): thay đổi role của user.
* Xem danh sách người dùng (UC-AUTH-08).
* Xem chi tiết người dùng (UC-AUTH-11).

**Quan hệ include/extend**

* Đăng nhập → include → Xác thực JWT Token (UC-AUTH-02): tạo JWT access token (ngắn hạn) + refresh token (dài hạn).
* Đăng nhập → extend → Ghi Audit Log đăng nhập (UC-AUTH-09).
* Tạo tài khoản → include → Gán vai trò.

---

## **UC03 – QUẢN LÝ GIAO DỊCH**

### **Mô tả Actor – Hành động**

**Operator (Nhân viên Vận hành)**

* Gửi giao dịch demo (UC-TXN-01): gọi API `POST /api/v1/transactions/submit` với dữ liệu giao dịch mô phỏng (card\_number raw, amount, merchant\_id, txn\_time). Server tự mask và hash card\_number. Hệ thống tự động xác thực, kiểm tra trùng, chấm điểm AI, phân luồng.
* Xem danh sách giao dịch (UC-TXN-07): xem toàn bộ giao dịch trong hệ thống.
* Xem chi tiết giao dịch (UC-TXN-08): xem fraud\_score, status, reason\_code, thời gian xử lý.
* Xem lịch sử trạng thái (UC-STATE-05): `GET /api/v1/transactions/{txn_id}/state-history`.

**Reviewer (Nhân viên Duyệt)**

* Xem danh sách giao dịch (UC-TXN-07): thấy tất cả giao dịch (không bị lọc theo submitted\_by).
* Xem chi tiết giao dịch (UC-TXN-08).
* Lọc giao dịch theo trạng thái, ngày, số tiền, merchant.

> ~~Cập nhật trạng thái giao dịch trực tiếp (UC-TXN-10)~~ — **Đã xóa**. Mọi việc duyệt/từ chối phải đi qua Case flow.

**Hệ thống AI (AI Engine)**

* Chấm điểm rủi ro (UC-TXN-04): chạy model Random Forest (10 cây), trả về fraud\_score ∈ `{0.3, 0.4, 0.5, 0.6, 0.7}`.

**Quan hệ include/extend**

* Gửi giao dịch → include → Xác thực dữ liệu đầu vào (UC-TXN-02).
* Gửi giao dịch → include → Kiểm tra Idempotency (UC-TXN-03): check idempotency\_key. Nếu trùng → trả response cũ.
* Gửi giao dịch → include → Chấm điểm rủi ro (UC-TXN-04).
* Chấm điểm rủi ro → include → Phân luồng giao dịch (UC-TXN-05):
  * fraud\_score **< 0.35** → **APPROVED** *(~~Cũ: ≤ 0.3~~)*
  * **0.35 ≤** score **< 0.65** → **MANUAL\_REVIEW** *(~~Cũ: dải 0.3–0.7~~)*
  * fraud\_score **≥ 0.65** → **REJECTED** *(~~Cũ: > 0.7~~)*
* Gửi giao dịch → extend → Phát hiện giao dịch giá trị cao (UC-TXN-06): amount > 500,000,000 → override MANUAL\_REVIEW + ghi audit.
* Mọi thay đổi trạng thái → include → Ghi Audit Log (UC-TXN-11).

---

## **UC04 – QUẢN LÝ ĐƠN VAY (LOAN MANAGEMENT)**

*(~~Cũ: "Hỗ trợ Quyết định Cho vay (Loan Simulator)"~~ — đã mở rộng thành quy trình phê duyệt đầy đủ)*

### **Mô tả Actor – Hành động**

**Operator (Nhân viên Vận hành)**

* Nộp đơn vay mới (UC-LOAN-01): gọi API `POST /api/v1/loans` với thông tin người vay và khoản vay. *(~~Cũ: `POST /api/v1/loans/submit`~~)*
  * Body bao gồm: `customer_id`, `principal_amount`, `currency_code`, `interest_rate`, `term_months`, `purpose`
  * AI features (tùy chọn, dùng để tính PD Score): `person_age`, `person_income`, `person_home_ownership`, `person_emp_length`, `loan_intent`, `loan_grade`, `cb_person_default_on_file`, `cb_person_cred_hist_length` *(~~Cũ: `applicant_id`, `credit_score`, `employment_type`~~)*
  * Đơn được tạo ở trạng thái **PENDING**. PD Score và risk\_level được tính ngay khi nộp (nếu đủ AI features). *(~~Cũ: trả kết quả ngay, không có trạng thái~~)*
* Mô phỏng khoản vay (UC-LOAN-SIM): `POST /api/v1/loans/simulate` — chạy AI model trả về pd\_score và risk\_level mà **không lưu DB**. *(Mới)*
* Xem danh sách đơn vay (UC-LOAN-02): `GET /api/v1/loans` — xem toàn bộ đơn vay.
* Xem chi tiết đơn vay (UC-LOAN-03): `GET /api/v1/loans/{loan_id}` — xem pd\_score, risk\_level, trạng thái phê duyệt.

**Reviewer (Nhân viên Duyệt)**

* Xem danh sách hồ sơ vay (UC-LOAN-02): `GET /api/v1/loans`.
* Xem chi tiết hồ sơ vay (UC-LOAN-03).
* **Phê duyệt hoặc từ chối đơn vay (UC-LOAN-04)**: `PATCH /api/v1/loans/{loan_id}/decision`
  * `decision`: `APPROVE` hoặc `REJECT`
  * `review_note`: bắt buộc
  * `version`: Optimistic Locking
  * Khi APPROVE: hệ thống tính `monthly_payment`, `outstanding_balance`, `maturity_date`.
  * **Ràng buộc SoD**: người phê duyệt **không được là người đã tạo đơn** (`submitted_by != actor_user_id`). Nếu vi phạm → 403.

**Manager (Quản lý)**

* Xem danh sách và chi tiết hồ sơ vay (UC-LOAN-02, UC-LOAN-03): giám sát tổng thể, chỉ đọc.

**Quan hệ include/extend**

* Nộp đơn → include → Kiểm tra Customer tồn tại.
* Nộp đơn → include → Chấm điểm PD Score: gọi ML model (XGBoost), trả về pd\_score (0.0–1.0).
* Chấm điểm → include → Phân loại risk\_level: *(~~Cũ: risk\_grade~~)*
  * pd\_score **< 0.20** → **LOW** *(~~Cũ ngưỡng: < 0.3~~)*
  * **0.20 ≤** pd < **0.50** → **MEDIUM** *(~~Cũ: 0.3–0.6~~)*
  * pd\_score **≥ 0.50** → **HIGH** *(~~Cũ: > 0.6~~)*
* Nộp đơn → extend → Ghi Audit Log (LOAN\_APPLIED).
* Phê duyệt → include → **Kiểm tra SoD**: `submitted_by != actor_user_id`, từ chối nếu trùng → 403. *(Mới)*
* Phê duyệt → include → Optimistic Locking: so sánh version, từ chối nếu lệch → 409.
* Phê duyệt APPROVE → include → Tính monthly\_payment (công thức amortisation), maturity\_date.
* Phê duyệt → extend → Ghi Audit Log (LOAN\_APPROVED / LOAN\_REJECTED).

---

## **UC05 – CASE MANAGEMENT VÀ AUDIT**

### **Mô tả Actor – Hành động**

**Reviewer (Nhân viên Duyệt)**

* Xem danh sách case (UC-CASE-01): thấy **tất cả OPEN cases** (queue chưa ai nhận để self-assign) + **cases được giao cho mình**. *(~~Cũ: chỉ thấy cases của mình → không nhận được việc mới~~)*
* Nhận case – Assign to me (UC-CASE-02): `POST /api/v1/cases/{case_id}/assign` — chọn case OPEN chưa ai nhận, gán cho mình → OPEN → ASSIGNED. Dùng `WHERE assigned_to IS NULL` để tránh race condition.
* Xem chi tiết case (UC-CASE-03): **chỉ xem case được giao cho mình**.
* Quyết định case (UC-CASE-04/05): `PATCH /api/v1/cases/{case_id}/decision` — **case phải ở trạng thái ASSIGNED** (không được quyết định case OPEN). `decision` = APPROVE/REJECT, kèm `note` bắt buộc và `version` (Optimistic Locking). *(~~Cũ: có thể quyết định case OPEN~~)*

**Manager (Quản lý)**

* Xem danh sách case (UC-CASE-01): giám sát tổng quan — thấy tất cả cases.
* Xem chi tiết case (UC-CASE-03): thấy mọi case (không bị hạn chế như REVIEWER).
* Xem Audit Log (UC-AUDIT-02): `GET /api/v1/audit-logs`.
* Truy vết giao dịch (UC-AUDIT-03): `GET /api/v1/audit-logs/entities/TRANSACTION/{txn_id}`.
* Lọc Audit Log (UC-AUDIT-04).
* Xem chi tiết một audit event (UC-AUDIT-04): `GET /api/v1/audit-logs/{log_id}`.

**Admin (Quản trị viên)**

* Xem Audit Log (UC-AUDIT-02).
* Truy vết giao dịch (UC-AUDIT-03).
* Lọc và xuất Audit Log.

**Quan hệ include/extend**

* Quyết định case → include → **Kiểm tra case phải ASSIGNED** (không quyết định case OPEN) → 409 nếu vi phạm. *(Mới)*
* Quyết định case → include → Ghi chú quyết định (UC-CASE-06): bắt buộc ghi lý do.
* Quyết định case → include → Kiểm tra Optimistic Lock.
* Quyết định case → include → Cập nhật trạng thái TRANSACTIONS\_LIVE (UC-CASE-07).
* Cập nhật trạng thái → include → Tự động ghi Audit Log (UC-AUDIT-01).
* MANAGER/ADMIN decide → bypass ownership check (override/giám sát), nhưng **vẫn cần case ở ASSIGNED**. *(~~Cũ: ADMIN bị chặn như REVIEWER~~)*

---

## **UC06 – DATA ENGINEERING VÀ BÁO CÁO**

### **Mô tả Actor – Hành động**

**Hệ thống ETL (ETL Scheduler)**

* Ghi log thô vào Data Lake (UC-DATA-01): sau mỗi giao dịch, log thô ghi vào CSV theo cấu trúc `/datalake/raw/transaction_logs/{YYYY-MM-DD}/`.
* Extract từ Data Lake (UC-DATA-03): đọc file CSV.
* Chạy đối soát tự động cuối ngày (UC-RECON-01).

**Admin (Quản trị viên)**

* Xem danh sách snapshots Data Lake (UC-DATA-02): `GET /api/v1/datalake/snapshots`.
* Nạp dữ liệu ngoài vào Data Lake: `POST /api/v1/datalake/ingest`.
* Xem danh sách log ETL (UC-DATA-06): `GET /api/v1/etl/logs`.
* Trigger ETL thủ công (UC-DATA-03/04/05): `POST /api/v1/etl/run` *(~~Cũ: `/etl/trigger`~~)* — chọn `target_date`.
* Chạy đối soát thủ công (UC-RECON-01): `POST /api/v1/reconciliation/run`.
* Xem danh sách phiên đối soát (UC-DATA-09): `GET /api/v1/reconciliation/reports`.
* Xem chi tiết phiên đối soát (UC-RECON-03): `GET /api/v1/reconciliation/{run_id}`.
* Resolve discrepancies: `PATCH /api/v1/reconciliation/{run_id}/resolve`.

**Manager (Quản lý)**

* Xem Dashboard tổng quan (UC-BI-01): `GET /api/v1/dashboard/summary`.
* Xem biểu đồ xu hướng fraud (UC-BI-02): `GET /api/v1/dashboard/fraud-trend`. *(~~Cũ: fraud-chart~~)*
* Xem báo cáo giao dịch (UC-BI-03): `GET /api/v1/reports/transactions`.
* Xuất báo cáo fraud summary (UC-BI-04): `GET /api/v1/reports/fraud`.

---

## **UC07 – IDEMPOTENCY, STATE VÀ RECONCILIATION**

### **Mô tả Actor – Hành động**

**Operator (Nhân viên Vận hành)**

* Xem lịch sử trạng thái (UC-STATE-05): `GET /api/v1/transactions/{txn_id}/state-history`. *(~~Cũ: `/states`~~)*

**Admin (Quản trị viên)**

* Xem lịch sử trạng thái (UC-STATE-05).
* Chạy đối soát (UC-RECON-01): `POST /api/v1/reconciliation/run`.
* Xem chi tiết phiên đối soát (UC-RECON-03): `GET /api/v1/reconciliation/{run_id}`.

**Hệ thống (System Auto)**

* Tạo Idempotency Key (UC-IDEM-01): client gửi `idempotency_key` (UUID) theo request, server dùng field này để dedup.
* Kiểm tra trùng lặp (UC-IDEM-02): check trong TXN\_IDEMPOTENCY. Nếu trùng → trả response cũ.
* Khởi tạo trạng thái PENDING (UC-STATE-01).
* Chuyển trạng thái (UC-STATE-02) với Optimistic Locking (UC-STATE-03): version tăng sau mỗi lần chuyển.
* Chạy đối soát tự động (UC-RECON-01): cuối ngày so khớp COUNT(\*) và SUM(amount) giữa OLTP, Data Lake, Warehouse.

---

## **UC08 – REAL-TIME STREAM (SSE)** *(Mới)*

### **Mô tả Actor – Hành động**

**Operator / Reviewer / Manager / Admin**

* Nhận live feed giao dịch mới (UC-STREAM-01): `GET /api/v1/stream/transactions` — Server-Sent Events, đẩy từng giao dịch mới ngay khi submit. Dùng trong demo: Faker POST liên tục → SSE đẩy kết quả về frontend theo thời gian thực.
  * Tham số `interval` (0.5–10 giây, default: 2s): tần suất poll DB.
  * Server dùng `created_at >= last_checked` để bắt tất cả giao dịch mới bất kể `txn_time`.

**Manager / Admin**

* Nhận live dashboard summary (UC-STREAM-02): `GET /api/v1/stream/dashboard` — đẩy dashboard summary cập nhật mỗi N giây (transaction counts, fraud rate, case queue, loan stats).

**Quan hệ**

* SSE stream → include → Xác thực JWT (Bearer Token trên query string hoặc header).
* SSE stream → poll → DB (SessionLocal per tick, không giữ session dài hạn).
* Heartbeat comment `: ping` được gửi khi không có dữ liệu mới.
