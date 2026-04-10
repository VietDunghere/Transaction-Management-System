# Luồng Hoạt động Hệ thống (System Workflow)

Tài liệu này mô tả chi tiết các luồng nghiệp vụ cốt lõi bên trong **Transaction Management System (TMS)**.

---

## 1. Luồng Nhận & Xử lý Giao dịch (Transaction Processing)

Đây là luồng chính phục vụ với tần suất cao (High Throughput). Hệ thống thực hiện việc kiểm tra trùng lặp và phân luồng qua AI Engine.

1. **Gửi yêu cầu:** `OPERATOR` gọi API POST gửi thông tin giao dịch (Card Number, Amount, Merchant ID...).
2. **Tiền xử lý (Pre-processing):**
   - Server tự động **Mask** (che) số thẻ tín dụng nhằm đảm bảo an ninh dữ liệu trước khi lưu trữ (ví dụ: `4111********1111`).
   - Tự chọn các trường dữ liệu tĩnh nghiệp vụ để băm (Hash SHA256) tạo ra `idempotency_key`. Không dùng timestamp để tránh hash bị thay đổi.
3. **Kiểm tra trùng lặp (Idempotency Check):**
   - Truy vấn DB xem `idempotency_key` đã tồn tại chưa.
   - Nếu *có*, lập tức trả về snapshot kết quả xử lý của lần trước đó, dừng luồng (Chống double-charge).
   - Nếu *chưa*, tiếp tục lưu key và chuyển sang bước tiếp.
4. **Phân tích Rủi ro & Ra quyết định (AI Scoring):**
   - Gọi **AI Engine** (Random Forest) dự đoán và trả về `fraud_score` (từ 0.0 - 1.0).
   - Trigger DB tự động kích hoạt nếu số tiền lớn bất thường (ví dụ: > 500,000,000) ghi đè lý do để ép kiểm tra tay.
5. **Định tuyến luồng (Routing):**
   - Nếu `fraud_score` $\leq$ 0.3: Trạng thái `APPROVED` (Cho qua tự động).
   - Nếu 0.3 $<$ `fraud_score` $\leq$ 0.7 HOẶC chạm ngưỡng số tiền cao: Phân sang `MANUAL_REVIEW`.
   - Nếu `fraud_score` $>$ 0.7: Trạng thái `REJECTED` (Từ chối tự động).
6. **Hoàn tất:** Giao dịch được lưu vào `TRANSACTIONS_LIVE` và nhật ký hành động tự động được ghi vết vào `AUDIT_LOGS`.

---

## 2. Luồng Xử lý Giao dịch Bị cảnh báo (Manual Case Management)

Dành cho đối tượng `REVIEWER` theo dõi và giải quyết các cảnh báo trung bình. Đảm bảo triệt để tính truy vết (Audit Trail).

1. **Khởi tạo:** Với mọi giao dịch vào nhánh `MANUAL_REVIEW`, hệ thống sinh ra một bản ghi trong quản lý `CASES` với status `OPEN`.
2. **Nhận việc (Assign):** 
   - `REVIEWER` vào màn hình các khoản đợi, chọn Case và gán cho mình.
   - *Ràng buộc an toàn:* Lệnh gán đi kèm khóa Database (`UPDATE ... WHERE assigned_to IS NULL`) đảm bảo 2 Reviewer không nhận trùng việc. Case chuyển `ASSIGNED`.
3. **Thanh tra (Investigation):** `REVIEWER` đọc dữ liệu chi tiết giao dịch, phân tích lý do điểm AI báo và đưa kết luận.
4. **Ra quyết định (Approve/Reject):**
   - Gửi trạng thái quyết định bắt buộc kèm theo **Ghi chú (Note)** và tham số **`version`**.
   - *Optimistic Locking:* Hệ thống so khớp `version`. Nếu khớp, tăng version lên 1 (Tránh đụng độ sửa đổi).
   - *Thay đổi liên hoàn (Cascading):* Trạng thái Case cập nhật $\rightarrow$ Trạng thái Giao dịch cập nhật $\rightarrow$ Nhật ký Audit ghi lại toàn bộ quyết định.

---

## 3. Luồng Quản trị Dữ liệu (ETL Pipeline)

Tiến trình chạy ngầm qua cronjob hoặc xử lý thủ công từ `ADMIN`.

1. **Gắn log thô (Realtime):** Song song với quá trình nhận giao dịch, dữ liệu thô (raw JSON, time, origin IP) được sao lưu cứng thành file CSV tại đường dẫn Data Lake (`/datalake/raw/transaction_logs/YYYY-MM-DD/`).
2. **Trích xuất (Extract):** Quét phân vùng Data Lake thu thập các lô tệp theo ngày.
3. **Biến đổi (Transform):** Xử lý dọn dẹp (Data Cleansing) tẩy các dòng nhiễu, làm giàu dữ liệu GeoIP mapping và chuyển hóa cấu trúc sang Mô hình Schema hình sao (Star Schema).
4. **Tải lên kho (Load):** Nạp vào Data Warehouse (`FACT_TRANSACTIONS`) phục vụ mảng thống kê phân tích (OLAP).
5. **Ghi vết tiến trình:** Kết quả trạng thái và số dòng đọc vào được log đầy đủ sang `ETL_JOB_LOGS`.

---

## 4. Luồng Đối soát So khớp (Reconciliation)

Chạy lúc chốt phiên ngày, tự động rà quét kiểm tra độ toàn vẹn của nền tảng (Tính năng kỹ thuật cấp cao).

1. **Khởi chạy:** Tiến trình được đặt `RUNNING`.
2. **Khai thác 3 nguồn:** Thu gom COUNT(*) số lượng và SUM(amount) số tiền từ ba điểm độc lập:
   - Cơ sở dữ liệu nghiệp vụ chính (**OLTP**)
   - Các bản lưu văn bản gốc (**Data Lake**)
   - Kho lưu trữ số liệu thống kê (**Data Warehouse**)
3. **Đối chiếu:**
   - Hoàn toàn bằng nhau $\rightarrow$ Cập nhật thẻ trạng thái `MATCH`.
   - Có khác biệt $\rightarrow$ Hệ thống đánh thẻ `MISMATCH` và liệt kê rõ nguyên nhân/khác biệt (Discrepancies).
   - Nếu Database chết/Timeout $\rightarrow$ Rơi vào thẻ `FAILED`.

---

## 5. Luồng Trình giả lập Quyết định Vay vốn (Loan Simulator)

Luồng kiểm nghiệm tích hợp mô hình Machine Learning riêng biệt do `OPERATOR` sử dụng.

1. **Gửi hồ sơ dự định:** Điền một số lượng vốn, thu nhập, lịch sử tín dụng giả định.
2. **Chấm điểm Probability of Default (PD):** Trí tuệ Nhan tạo xử lý mô hình, nhả điểm số tỷ lệ rủi ro có thể vỡ nợ.
3. **Phân cấp:** Quy nó về cấu trúc cảnh báo (Rủi ro Thấp, Trung Bình, Cao) làm tư liệu ra quyết định cấp vốn.
4. **Lưu trữ:** Lưu log kết quả xuống `LOAN_APPLICATIONS` phục vụ việc truy xuất và báo cáo BI sau này.
