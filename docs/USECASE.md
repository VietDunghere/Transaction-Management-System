## **UC01 – TỔNG QUAN HỆ THỐNG**

### **Mô tả Actor – Hành động**

**Operator (Nhân viên Vận hành)**

* Đăng nhập hệ thống bằng tài khoản được cấp, nhận JWT token.
* Xem thông tin tài khoản cá nhân (UC-AUTH-10).
* Gửi giao dịch demo vào hệ thống qua API (`POST /api/v1/transactions/submit`) hoặc Postman với dữ liệu mô phỏng (card\_number, amount, merchant\_id...).
* Gửi đơn vay demo thông qua Loan Simulator (`POST /api/v1/loans/submit`).
* Xem danh sách giao dịch đã gửi và kết quả xử lý (APPROVED / REJECTED / MANUAL\_REVIEW).

**Reviewer (Nhân viên Duyệt)**

* Đăng nhập hệ thống.
* Xem thông tin tài khoản cá nhân (UC-AUTH-10).
* Xem danh sách case cần duyệt – các giao dịch có status = MANUAL\_REVIEW.
* Duyệt hoặc từ chối giao dịch qua Case flow, kèm ghi chú lý do quyết định.
* Xem danh sách giao dịch để theo dõi tổng quan.

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

* Tự động chấm điểm rủi ro giao dịch (Fraud Scoring) – nhận dữ liệu giao dịch, trả về fraud\_score (0.0–1.0).
* Tự động chấm điểm ML cho vay (PD Score) – nhận thông tin đơn vay, trả về pd\_score (0.0–1.0) bằng Random Forest.

**Hệ thống ETL (ETL Scheduler)**

* Tự động chạy ETL Pipeline – Extract CSV từ Data Lake, Transform (clean, enrich), Load vào Warehouse.

---

## **UC02 – XÁC THỰC VÀ PHÂN QUYỀN**

### **Mô tả Actor – Hành động**

**Operator (Nhân viên Vận hành)**

* Đăng nhập hệ thống (UC-AUTH-01): nhập username + password, hệ thống trả JWT token nếu hợp lệ.
* Đăng xuất (UC-AUTH-03): hủy phiên làm việc, JWT không còn hiệu lực.
* Xem thông tin cá nhân (UC-AUTH-10): `GET /api/v1/auth/me` — xem user\_id, username, role, is\_active.
* Đổi mật khẩu (UC-AUTH-04): `PATCH /api/v1/auth/change-password` — cập nhật mật khẩu cá nhân.

**Reviewer (Nhân viên Duyệt)**

* Đăng nhập hệ thống (UC-AUTH-01): tương tự Operator, nhưng JWT chứa role = REVIEWER.
* Đăng xuất (UC-AUTH-03).
* Xem thông tin cá nhân (UC-AUTH-10).
* Đổi mật khẩu (UC-AUTH-04).

**Manager (Quản lý)**

* Đăng nhập hệ thống (UC-AUTH-01): JWT chứa role = MANAGER.
* Đăng xuất (UC-AUTH-03).
* Xem thông tin cá nhân (UC-AUTH-10).
* Xem danh sách người dùng (UC-AUTH-08): xem tất cả tài khoản trong hệ thống (chỉ đọc).
* Xem chi tiết người dùng (UC-AUTH-11): xem thông tin cụ thể một user.

**Admin (Quản trị viên)**

* Đăng nhập hệ thống (UC-AUTH-01): JWT chứa role = ADMIN – quyền cao nhất.
* Đăng xuất (UC-AUTH-03).
* Xem thông tin cá nhân (UC-AUTH-10).
* Tạo tài khoản người dùng (UC-AUTH-05): tạo user mới cho nhân viên, tự động gán role mặc định.
* Vô hiệu hóa tài khoản (UC-AUTH-06): khóa tài khoản nhân viên khi nghỉ việc/vi phạm. **Ràng buộc: không được tự vô hiệu hóa chính mình.**
* Kích hoạt lại tài khoản (UC-AUTH-12): `PATCH /api/v1/users/{user_id}/enable` — mở lại tài khoản đã bị khóa.
* Gán vai trò (UC-AUTH-07): thay đổi role của user (Operator, Reviewer, Manager).
* Xem danh sách người dùng (UC-AUTH-08): xem và quản lý tất cả user.
* Xem chi tiết người dùng (UC-AUTH-11): xem thông tin cụ thể một user.

**Quan hệ include/extend**

* Đăng nhập → include → Xác thực JWT Token (UC-AUTH-02): mỗi lần login thành công, hệ thống tạo JWT chứa user\_id, role, thời hạn.
* Đăng nhập → extend → Ghi Audit Log đăng nhập (UC-AUTH-09): ghi log mọi lần login (thành công lẫn thất bại).
* Tạo tài khoản → include → Gán vai trò: khi tạo user mới, bắt buộc gán role mặc định.

---

## **UC03 – QUẢN LÝ GIAO DỊCH**

### **Mô tả Actor – Hành động**

**Operator (Nhân viên Vận hành)**

* Gửi giao dịch demo (UC-TXN-01): gọi API `POST /api/v1/transactions/submit` với dữ liệu giao dịch mô phỏng (card\_number raw, amount, merchant\_id, txn\_time). Server tự mask và hash card\_number. Hệ thống tự động xác thực, kiểm tra trùng, chấm điểm AI, phân luồng.
* Xem danh sách giao dịch (UC-TXN-07): xem bảng tất cả giao dịch đã gửi. **Chỉ thấy giao dịch do chính mình gửi** (filter ngầm submitted\_by).
* Xem chi tiết giao dịch (UC-TXN-08): xem fraud\_score, status, reason\_code, thời gian xử lý.
* Xem lịch sử trạng thái (UC-STATE-05): xem timeline trạng thái của một giao dịch.

**Reviewer (Nhân viên Duyệt)**

* Xem danh sách giao dịch (UC-TXN-07): xem tổng quan giao dịch.
* Xem chi tiết giao dịch (UC-TXN-08): xem chi tiết để đánh giá.
* Lọc giao dịch theo trạng thái (UC-TXN-09): lọc PENDING / APPROVED / REJECTED / MANUAL\_REVIEW.

> ~~Cập nhật trạng thái giao dịch trực tiếp (UC-TXN-10)~~ — **Đã xóa**. Mọi việc duyệt/từ chối phải đi qua Case flow (`PATCH /api/v1/cases/{case_id}/decision`) để đảm bảo Audit Trail toàn vẹn.

**Hệ thống AI (AI Engine)**

* Chấm điểm rủi ro (UC-TXN-04): nhận dữ liệu giao dịch từ Backend, chạy model Random Forest, trả về fraud\_score (0.0–1.0).

**Quan hệ include/extend**

* Gửi giao dịch → include → Xác thực dữ liệu đầu vào (UC-TXN-02): validate card\_number, amount > 0, merchant\_id hợp lệ.
* Gửi giao dịch → include → Kiểm tra Idempotency (UC-TXN-03): hash payload, check trong TXN\_IDEMPOTENCY. Nếu trùng → trả response cũ, không xử lý lại.
* Gửi giao dịch → include → Chấm điểm rủi ro (UC-TXN-04): gọi AI scoring.
* Chấm điểm rủi ro → include → Phân luồng giao dịch (UC-TXN-05):
  * fraud\_score <= 0.3 → APPROVED
  * 0.3 < score <= 0.7 → MANUAL\_REVIEW
  * fraud\_score > 0.7 → REJECTED
* Gửi giao dịch → extend → Phát hiện giao dịch giá trị cao (UC-TXN-06): amount > 500,000,000 → override MANUAL\_REVIEW + ghi audit.
* Mọi thay đổi trạng thái → include → Ghi Audit Log (UC-TXN-11).

---

## **UC04 – HỖ TRỢ QUYẾT ĐỊNH CHO VAY (LOAN SIMULATOR)**

### **Mô tả Actor – Hành động**

**Operator (Nhân viên Vận hành)**

* Gửi đơn vay demo (UC-LOAN-01): gọi API `POST /api/v1/loans/submit` với thông tin người vay (applicant\_id, loan\_amount, tenure\_months, annual\_income, credit\_score, employment\_type). Hệ thống chấm điểm PD Score bằng model ML và trả về risk\_grade (LOW / MEDIUM / HIGH).

**Manager (Quản lý)**

* Xem danh sách hồ sơ vay (UC-LOAN-02): `GET /api/v1/loans` — liệt kê các đơn vay, lọc theo status.
* Xem chi tiết hồ sơ vay (UC-LOAN-03): `GET /api/v1/loans/{loan_id}` — xem đầy đủ thông tin và kết quả chấm điểm.

**Admin (Quản trị viên)**

* Xem danh sách và chi tiết hồ sơ vay (UC-LOAN-02, UC-LOAN-03): giám sát tổng thể.

**Quan hệ include/extend**

* Gửi đơn vay → include → Chấm điểm PD Score: gọi ML model, trả về pd\_score (0.0–1.0).
* Chấm điểm → include → Phân loại risk\_grade: LOW (<0.3), MEDIUM (0.3–0.6), HIGH (>0.6).
* Gửi đơn vay → extend → Ghi Audit Log.

---

## **UC05 – CASE MANAGEMENT VÀ AUDIT**

### **Mô tả Actor – Hành động**

**Reviewer (Nhân viên Duyệt)**

* Xem danh sách case OPEN (UC-CASE-01): xem tất cả case đang chờ xử lý (giao dịch bị flag MANUAL\_REVIEW).
* Nhận case – Assign to me (UC-CASE-02): chọn case chưa ai nhận, gán cho mình → status chuyển OPEN → ASSIGNED. Hệ thống dùng `WHERE assigned_to IS NULL` để tránh race condition. Ghi audit log.
* Xem chi tiết case (UC-CASE-03): xem thông tin giao dịch liên quan (amount, fraud\_score, txn\_time), lịch sử trạng thái.
* Quyết định case (UC-CASE-04/05): `PATCH /api/v1/cases/{case_id}/decision` với `decision` = APPROVE hoặc REJECT, kèm `note` bắt buộc và `version` để kích hoạt **Optimistic Locking** — tránh hai reviewer ghi đè nhau. Hệ thống cập nhật REVIEW\_CASES.status và TRANSACTIONS\_LIVE.status đồng thời, ghi audit log.

**Manager (Quản lý)**

* Xem danh sách case (UC-CASE-01): giám sát tổng quan (chỉ đọc).
* Xem chi tiết case (UC-CASE-03): xem thông tin để giám sát chất lượng duyệt.
* Xem Audit Log (UC-AUDIT-02): xem toàn bộ log sự kiện theo entity (TRANSACTION, LOAN, USER).
* Truy vết giao dịch (UC-AUDIT-03): `GET /api/v1/audit-logs/transactions/{txn_id}/trace` — xem timeline: khi nào tạo, ai duyệt, lý do gì, trạng thái thay đổi thế nào.
* Lọc Audit Log (UC-AUDIT-04): lọc theo thời gian, actor, event\_type.
* Xuất báo cáo Audit (UC-AUDIT-05): export danh sách audit events ra file CSV/PDF.

**Admin (Quản trị viên)**

* Xem Audit Log (UC-AUDIT-02): giám sát kỹ thuật.
* Truy vết giao dịch (UC-AUDIT-03): debug khi có vấn đề.
* Lọc Audit Log (UC-AUDIT-04): tìm kiếm sự kiện cụ thể.
* Xuất báo cáo Audit (UC-AUDIT-05): tạo báo cáo compliance.

**Quan hệ include/extend**

* Quyết định case → include → Ghi chú quyết định (UC-CASE-06): bắt buộc ghi lý do (tối thiểu 10 ký tự).
* Quyết định case → include → Kiểm tra Optimistic Lock: so sánh `version` request với DB, từ chối nếu lệch.
* Quyết định case → include → Cập nhật trạng thái TRANSACTIONS\_LIVE (UC-CASE-07).
* Cập nhật trạng thái → include → Tự động ghi Audit Log (UC-AUDIT-01).
* Nhận case → include → Tự động ghi Audit Log: ghi log "CASE\_ASSIGNED".
* Truy vết giao dịch → include → Xem Audit Log: truy vết = đọc audit log theo txn\_id.

---

## **UC06 – DATA ENGINEERING VÀ BÁO CÁO**

### **Mô tả Actor – Hành động**

**Hệ thống ETL (ETL Scheduler)**

* Ghi log thô vào Data Lake (UC-DATA-01): sau mỗi giao dịch, log thô (raw\_txn\_id, raw\_timestamp, raw\_payload\_json, source\_ip) được ghi vào file CSV theo cấu trúc `/datalake/raw/transaction_logs/{YYYY-MM-DD}/`.
* Extract từ Data Lake (UC-DATA-03): đọc file CSV từ thư mục Data Lake.
* Chạy đối soát tự động cuối ngày (UC-RECON-01).

**Admin (Quản trị viên)**

* Xem cấu trúc Data Lake (UC-DATA-02): `GET /api/v1/datalake/structure` — kiểm tra thư mục, số file, kích thước. Hỗ trợ phân trang.
* Xem danh sách log ETL (UC-DATA-06): `GET /api/v1/etl/logs` — kiểm tra ETL pipeline có chạy thành công hay lỗi.
* Xem chi tiết một ETL job (UC-DATA-07): `GET /api/v1/etl/logs/{job_id}` — xem rows processed, error message, thời gian chạy.
* Trigger ETL thủ công (UC-DATA-03/04/05): `POST /api/v1/etl/trigger` — khởi chạy pipeline khi cần, chọn mode FULL hoặc INCREMENTAL.
* Chạy đối soát thủ công (UC-RECON-01): `POST /api/v1/reconciliation/run`.
* Xem kết quả đối soát (UC-DATA-09): `GET /api/v1/reconciliation/jobs` — status MATCH / MISMATCH / RUNNING / FAILED.

**Manager (Quản lý)**

* Xem Dashboard tổng quan (UC-BI-01): `GET /api/v1/dashboard/summary?period=today|this_week|this_month&granularity=day` — tổng số giao dịch, tỷ lệ fraud, số case chờ duyệt, trend.
* Xem biểu đồ Fraud/Legit (UC-BI-02): `GET /api/v1/dashboard/fraud-chart?from_date=...&to_date=...&period=weekly` — data từ Warehouse (OLAP).
* Xem báo cáo theo thời gian (UC-BI-03): `GET /api/v1/reports/transactions` — số lượng giao dịch, tổng amount, tỷ lệ APPROVED/REJECTED/MANUAL\_REVIEW theo ngày/tuần/tháng/quý.
* Xuất báo cáo PDF/CSV (UC-BI-04): `GET /api/v1/reports/transactions/export`.
* Xem kết quả đối soát (UC-DATA-09): `GET /api/v1/reconciliation/jobs` — kiểm tra độ chính xác dữ liệu.

**Quan hệ include/extend**

* Extract → include → Transform (UC-DATA-04): Drop duplicates, Fill missing values, Enrich GeoIP (IP → City/Country), Map sang Star Schema.
* Transform → include → Load vào Warehouse (UC-DATA-05): INSERT vào FACT\_TRANSACTIONS + DIM tables.
* Load → include → Ghi log ETL (UC-DATA-06): ghi kết quả (thành công/lỗi, số dòng đã load).
* Đối soát → include → So khớp (UC-RECON-02): đếm COUNT(\*) và SUM(amount) giữa 3 nguồn (OLTP, Lake, Warehouse).
* So khớp → extend → Báo cáo chênh lệch (UC-RECON-03): nếu MISMATCH → tạo báo cáo chi tiết, status = FAILED nếu job lỗi.
* Dashboard → include → Biểu đồ Fraud/Legit.
* Báo cáo theo thời gian → extend → Xuất báo cáo.

---

## **UC07 – IDEMPOTENCY, STATE VÀ RECONCILIATION**

### **Mô tả Actor – Hành động**

**Operator (Nhân viên Vận hành)**

* Xem lịch sử trạng thái (UC-STATE-05): `GET /api/v1/transactions/{txn_id}/states` — xem timeline trạng thái (PENDING → APPROVED/REJECTED/MANUAL\_REVIEW → ...).

**Admin (Quản trị viên)**

* Xem lịch sử trạng thái (UC-STATE-05): debug khi có vấn đề về trạng thái giao dịch.
* Chạy đối soát (UC-RECON-01): `POST /api/v1/reconciliation/run` — trigger reconciliation, kiểm tra tính nhất quán dữ liệu.
* Xem báo cáo chênh lệch (UC-RECON-03): `GET /api/v1/reconciliation/jobs/{job_id}` — nếu có MISMATCH hoặc FAILED, xem chi tiết chênh lệch.

**Hệ thống (System Auto)**

* Tạo Idempotency Key (UC-IDEM-01): khi nhận giao dịch, hệ thống tự tạo hash = SHA256(card\_number + amount + merchant\_id + txn\_time) làm idempotency\_key.
* Kiểm tra trùng lặp (UC-IDEM-02): trước khi xử lý, check idempotency\_key trong bảng TXN\_IDEMPOTENCY:
  * Nếu đã tồn tại → trả response cũ (UC-IDEM-03), không xử lý lại.
  * Nếu chưa tồn tại → xử lý bình thường, lưu response snapshot (UC-IDEM-04).
* Khởi tạo trạng thái PENDING (UC-STATE-01): khi giao dịch mới vào hệ thống, tạo bản ghi TXN\_STATE với status = PENDING, version = 1.
* Chuyển trạng thái (UC-STATE-02): mỗi khi status thay đổi, hệ thống:
  * Kiểm tra version (Optimistic Locking – UC-STATE-03): đảm bảo không có race condition.
  * Tăng version++ sau mỗi lần chuyển trạng thái.
* Retry giao dịch lỗi (UC-STATE-04): nếu giao dịch bị lỗi giữa chừng (timeout, DB lỗi), hệ thống tự retry bằng cách chuyển trạng thái lại.
* Chạy đối soát tự động (UC-RECON-01): cuối ngày, tự động so khớp COUNT(\*) và SUM(amount) giữa OLTP, Data Lake, Warehouse. Kết quả: MATCH / MISMATCH / FAILED.

**Quan hệ include/extend**

* Kiểm tra trùng → extend → Trả response cũ (UC-IDEM-03): chỉ khi idempotency\_key đã tồn tại.
* Kiểm tra trùng → include → Lưu response snapshot (UC-IDEM-04): lần đầu xử lý → lưu lại kết quả.
* Chuyển trạng thái → include → Kiểm tra version (UC-STATE-03): bắt buộc check optimistic lock.
* Retry → include → Chuyển trạng thái: retry = thử chuyển trạng thái lại.
* Đối soát → include → So khớp OLTP vs Lake vs Warehouse (UC-RECON-02).
* So khớp → extend → Báo cáo chênh lệch (UC-RECON-03): chỉ tạo báo cáo khi MISMATCH hoặc FAILED.
