# Luồng Hoạt động Hệ thống (System Workflow)

Tài liệu này mô tả chi tiết các luồng nghiệp vụ cốt lõi bên trong **Transaction Management System (TMS)** được thiết kế thông qua các sơ đồ ASCII.

---

## 1. Luồng Nhận & Xử lý Giao dịch (Transaction Processing)

Đây là luồng chính phục vụ với tần suất cao (High Throughput). Các bước chủ yếu nhằm kiểm tra trùng lặp và chấm điểm qua AI.

```text
[ OPERATOR ] 
     |
     v (1. Submit Giao Dịch)
[ API Endpoint ]
     |
     v (2. Băm các dữ liệu tĩnh)
{ Idempotency Key tồn tại? } -----> [ CÓ ] -----> (Trả Cũ - Chống Lặp)
     |
     v [ KHÔNG ]
[ Dấu/Mask Số Thẻ ]
     |
     v
[ Gọi Model Random Forest ]
     |
     v
{ Cắt lớp Fraud Score }
     |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                       |                       |
(<= 0.3)             (> 0.3 & <= 0.7)           (> 0.7)
   |                Hoặc số tiền quá lớn           |
   v                       v                       v
[ APPROVED ]           [ PENDING ]            [ REJECTED ]
   |               (Mở Case MANUAL_REVIEW)         |
   |                       |                       |
   +-----------------------+-----------------------+
                           |
                           v
              [ DB: TRANSACTIONS_LIVE ]
                           |
                           v
                ( Tự động ghi Audit Log )
```

---

## 2. Luồng Xử lý Giao dịch Bị cảnh báo (Manual Case Management)

Dành cho đối tượng `REVIEWER`. Bảo vệ tính nguyên vẹn dữ liệu bằng Database Locking khi nhận việc và Optimistic Locking khi đưa ra quyết định.

```text
[ REVIEWER ]                                  [ SERVER / DB ]
      |                                              |
      |--- 1. Xem DS Case (Filter OPEN) ------------>|
      |<-- Trả về danh sách chờ ---------------------|
      |                                              |
      |--- 2. GET /cases/{id}/assign --------------->|
      |                                              |-- (DB Locking: UPDATE 
      |                                              |    WHERE assigned_to IS NULL)
      |<-- Case Status = ASSIGNED -------------------|
      |                                              |
      |--- 3. Đọc số liệu & Phân tích                |
      |                                              |
      |--- 4. PATCH /cases/{id}/decision ----------->|
      |       (Approve/Reject + Note + Version)      |
      |                                              |-- (Check Version chống đè file)
      |                                              |-- (Tắt trạng thái Case)
      |                                              |-- (Sửa trạng thái Giao Dịch)
      |                                              |-- (Ghi AUDIT_LOGS)
```

---

## 3. Luồng Quản trị Dữ liệu (ETL Pipeline)

Tiến trình chạy ngầm làm nhiệm vụ lấy dữ liệu từ các file Log giao dịch thô sang Kho dữ liệu Thống kê phục vụ biểu đồ (Dashboard).

```text
[ Data Lake ]
   (Raw CSV/JSON Logs chứa IP, payload)
          |
          |  <-- (Job chạy theo lịch hoặc do ADMIN kích hoạt)
          |
[ ETL Pipeline ]
   |-- 1. Extract:    Đọc file thô theo cụm ngày YYYY-MM-DD
   |-- 2. Transform:  Loại bỏ rác, map GeoIP, dựng Star Schema
   |-- 3. Load:       Chèn số liệu tóm tắt vào Warehouse
          |
          v
[ Data Warehouse ]
   (FACT_TRANSACTIONS - Phục vụ OLAP)
          |
          v
   [ Ghi Log kết quả vào ETL_JOB_LOGS ]
```

---

## 4. Luồng Đối soát So khớp (Reconciliation)

Chạy lúc chốt phiên ngày, so sánh đối chiếu chéo (3-way match) để xem cơ sở hạ tầng có thất thoát dữ liệu hay không.

```text
       [ ADMIN hoặc Cronjob ]
                |
                v (Gọi Endpoint /reconciliation/run)
                |
        ( Thu thập dữ liệu )
   +------------+------------+
   |            |            |
   v            v            v
[ OLTP ]    [Data Lake] [Warehouse]
(Oracle)    (Raw Files)   (OLAP)
   |            |            |
   |            |            |
   v            v            v
 { Bộ 3: COUNT(*) & SUM(amount) có hoàn toàn bằng nhau? }
                |
    +-----------+-----------+
    |           |           |
[ MATCH ]   [ MISMATCH ] [ FAILED ]
  (Khớp 100%) (Có lệch)  (DB Lỗi/Timeout)
```

---

## 5. Luồng Trình giả lập Quyết định Vay vốn (Loan Simulator)

Dành cho module Phân tích Khoản vay với cơ chế AI chấm Điểm Rủi ro riêng lẻ.

```text
[ OPERATOR ]
     |
     v 
[ POST /loans/submit ] (Nộp hồ sơ tín dụng)
     |
     v
[ AI Loan Model ]
     |
     v (Phân tích chỉ số Probability of Default - PD Score)
{ Phân Cấp Rủi Ro }
     |
  +--+--+--+--+--+
  |      |       |
[LOW] [MEDIUM] [HIGH]
  |      |       |
  +------+-------+
         |
         v
[ Lưu trữ vào LOAN_APPLICATIONS ]
```
