# Luồng Hoạt động Hệ thống (System Workflow)

Tài liệu này mô tả chi tiết các luồng nghiệp vụ cốt lõi bên trong **Transaction Management System (TMS)** được trực quan hóa bằng sơ đồ.

---

## 1. Luồng Nhận & Xử lý Giao dịch (Transaction Processing)

Đây là luồng chính phục vụ với tần suất cao (High Throughput). Trọng tâm là Idempotency để chống lặp và gọi Model AI chấm điểm.

```mermaid
graph TD
    Op((OPERATOR)) -->|1. Submit Endpoint| API[API Endpoint]
    API -->|2. Hash payload tĩnh| IdemCheck{Idempotency Key<br>đã tồn tại DB?}
    
    IdemCheck -->|CÓ| ReturnCached[Dừng luồng - Trả kết quả cũ<br>Chống bị trừ tiền 2 lần]
    IdemCheck -->|CHƯA| Masking[Tiền xử lý: Mask thẻ tín dụng]
    
    Masking --> AI[Gọi Model Random Forest<br>Dự đoán % gian lận]
    AI --> Logic{Fraud Score Threshold?}
    
    Logic -->|<= 0.3| Approve[Trạng thái: APPROVED]
    Logic -->|> 0.3 và <= 0.7| Manual[Chuyển PENDING<br>Mở Case: MANUAL_REVIEW]
    Logic -->|Trị giá cực lớn <br>bất chấp điểm số| Manual
    Logic -->|> 0.7| Reject[Trạng thái: REJECTED]
    
    Approve --> DB[(Oracle DB<br>TRANSACTIONS_LIVE)]
    Manual --> DB
    Reject --> DB
    
    DB -.-> AuditLog(Hệ thống tự động ghi vết Audit)
```

---

## 2. Luồng Xử lý Giao dịch Bị cảnh báo (Manual Case Management)

Dành cho đối tượng `REVIEWER` theo dõi và giải quyết các cảnh báo trung bình. Trọng tâm là dùng Locking để đảm bảo chỉ 1 người được xử lý 1 case.

```mermaid
sequenceDiagram
    participant R as REVIEWER
    participant S as Server
    participant DB as TRANSACTIONS_LIVE
    participant C as CASES
    
    R->>S: Xem danh sách Case (Lọc OPEN)
    S-->>R: Trả Danh sách Case cần xử lý
    R->>S: GET /cases/{id}/assign (Nhận Case)
    Note right of S: Dùng: UPDATE CASES ...<br>WHERE assigned_to IS NULL
    S->>C: Ghi đè người thực hiện = current user
    S-->>R: Trạng thái Case cập nhật: ASSIGNED
    R->>R: Đọc hồ sơ & Đi tìm bằng chứng
    R->>S: Gửi Quyết định (Decision) <br>kèm Note và Version khóa Optimistic
    S->>C: Check Version. Nếu khớp: Case = Đóng
    S->>DB: Status Giao dịch = Approved hoặc Rejected
    Note right of S: Sự kiện "Nhận Case", "Duyệt Case" <br>đều được ghi vào AUDIT_LOGS
```

---

## 3. Luồng Quản trị Dữ liệu (ETL Pipeline)

Tiến trình chạy ngầm làm nhiệm vụ lấy dữ liệu từ các file Log giao dịch thô sang Kho dữ liệu Thống kê phục vụ biểu đồ (Dashboard).

```mermaid
graph LR
    subgraph Data Lake
    A[Hệ thống Ghi trực tiếp Log thô<br>Dạng Raw CSV / JSON]
    end
    
    subgraph ETL Job / Pipeline
    B(Trích xuất / Extract)
    C(Làm sạch & Ánh xạ GeoIP / Transform)
    D(Nạp dữ liệu mảng Star Schema / Load)
    end
    
    subgraph Data Warehouse 
    E[(FACT_TRANSACTIONS<br>Bảng phụ trợ OLAP)]
    end
    
    A -->|Quét thư mục YYYY-MM-DD| B
    B --> C
    C --> D
    D --> E
    D -.-> Log[Ghi Log thành công/lỗi vào ETL_JOB_LOGS]
```

---

## 4. Luồng Đối soát So khớp (Reconciliation)

Chạy lúc chốt phiên ngày, so sánh đối chiếu chéo (3-way match) để xem có sự đứt gãy nào làm thất thoát số liệu hay không.

```mermaid
graph TD
    Batch((Manager / Cronjob)) -->|Lệnh Chạy| Trigger[Trigger Endpoint /reconciliation/run]
    
    Trigger --> FetchOLTP[(Lấy SUM & COUNT<br>từ SQL OLTP)]
    Trigger --> FetchLake[(Count Số lượng file<br>trong Data Lake)]
    Trigger --> FetchWH[(Lấy SUM & COUNT<br>từ Warehouse OLAP)]
    
    FetchOLTP --> Compare{Số liệu 3 nơi<br>Khớp nhau 100%?}
    FetchLake --> Compare
    FetchWH --> Compare
    
    Compare -->|Có| Match[Đánh dấu Trạng thái: MATCH]
    Compare -->|Lệch số| Mismatch[Đánh Thẻ: MISMATCH<br>Liệt kê Discrepancies vào mảng log]
    Compare -->|SQL Timeout / Lỗi Cấu hình| Failed[Đánh Thẻ: FAILED]
```

---

## 5. Luồng Trình giả lập Quyết định Vay vốn (Loan Simulator)

Dành cho module Phân tích Khoản vay với trí tuệ nhân tạo riêng lẻ.

```mermaid
graph TD
    O((OPERATOR)) -->|1. Submit hồ sơ đệ trình| API[Endpoint /loans/submit]
    API --> AI((Mô hình AI: Tính Tỷ lệ Vỡ Nợ))
    AI --> |2. Phân tích PD Score| Eval{Phân khúc Rủi ro Hệ thống}
    
    Eval -->|Điểm số thấp| L[Kết luận Rủi ro LOW]
    Eval -->|Điểm số tầm trung| M[Kết luận Rủi ro MEDIUM]
    Eval -->|Điểm số nguy hiểm| H[Kết luận Rủi ro HIGH<br>Từ chối tự động phần lớn]
    
    L --> DB[(Lưu Archive vào LOAN_APPLICATIONS)]
    M --> DB
    H --> DB
```
