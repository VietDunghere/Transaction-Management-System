# Giải thích chi tiết Schema Database — HPTRRĐGTC (Phiên bản v2.0 - 11 Bảng)

> Đọc một lần, hiểu toàn bộ thiết kế kiến trúc chuẩn hóa 5NF.  
> Phiên bản 2.0 đã tinh gọn từ 31 bảng xuống **11 bảng cốt lõi**, loại bỏ dư thừa nhưng vẫn giữ nguyên tính toàn vẹn.  
> Mỗi bảng: **làm gì → lưu gì → tại sao cần → FK về đâu → Index nào → ràng buộc gì**.

---

## Phần 0 — Khái niệm nền cần biết trước

Đọc phần này trước. Hiểu rồi thì đọc bảng nào cũng rõ ngay.

### Foreign Key (FK) là gì?
FK là **khoá ngoại** — một cột trong bảng này trỏ đến khoá chính (PK) của bảng khác. Đảm bảo tính nhất quán dữ liệu.
*VD: `transactions_live.customer_id` → `customers.customer_id`. Nếu ID không tồn tại trong `customers`, DB chặn lại ngay.*

### Index là gì?
Index là **mục lục**. Không có index phải quét cả triệu dòng. Có index, database nhảy thẳng đến đúng dòng trong vài mili-giây.

### CHECK Constraint là gì?
Ràng buộc giá trị ở mức Database. Chỉ cho nhập dữ liệu nằm trong tập hợp do mình định nghĩa. 
*VD: `CHECK (status IN ('PENDING', 'APPROVED'))`. Gõ sai chính tả hệ thống báo lỗi ngay.*

### Optimistic Locking là gì?
Kỹ thuật tránh **2 người cùng sửa 1 dòng cùng lúc** mà không cần khoá bảng. Sử dụng cột `version`.
1. A và B cùng đọc dòng có `version = 1`.
2. A lưu trước kèm `version = 1`. DB cho qua, cập nhật dòng thành `version = 2`.
3. B bấm lưu kèm `version = 1`. DB đối chiếu thấy version hiện tại là 2 khác 1 → Báo lỗi xung đột **(CONFLICT)**. B phải tải lại dữ liệu mới nhất.

### CLOB vs VARCHAR
- `VARCHAR(4000)`: Chứa được 4000 ký tự. Vượt quá sẽ lỗi.
- `CLOB`: Chứa được văn bản siêu dài (lên tới 4GB). Dùng để chứa JSON cấu trúc phức tạp.

---

## Nhóm 1 — Phân quyền & Hệ thống (Auth & Identity)

### 1. `users`
**Làm gì:** Lưu tài khoản và quyền của người dùng hệ thống.  
*(Lưu ý bản 2.0: Đã xóa bỏ các bảng `roles`, `user_roles` rườm rà. Quyền được gộp chung luôn vào đây vì Use Case quy định mỗi người chỉ đóng 1 vai trò).*

**Các cột quan trọng:**
| Cột | Kiểu | Ý nghĩa |
|---|---|---|
| `user_id` | varchar(36) PK | UUID — định danh duy nhất |
| `username`, `email` | varchar UNIQUE | Tên đăng nhập và email, không được trùng |
| `password_hash` | varchar(255) | Mật khẩu đã mã hóa một chiều |
| `role` | varchar(20) | Vai trò (OPERATOR, REVIEWER, ANALYST, MANAGER, ADMIN) |
| `status` | varchar(20) | Trạng thái (ACTIVE, DISABLED) |

**Tại sao thiết kế vậy:** Mọi hành động hệ thống (Ai gửi giao dịch? Ai duyệt?) đều cần truy vết về `user_id`. Gộp role vào bảng giúp tăng tốc độ truy vấn login, không cần JOIN.

---

## Nhóm 2 — Dữ liệu tham chiếu (Reference Data)

> Dữ liệu được đẩy từ hệ thống Core Banking sang. Ở hệ thống này **chỉ đọc**, không thêm sửa xóa (CRUD).

### 2. `customers`
**Làm gì:** Dữ liệu hồ sơ của Chủ thẻ/Khách hàng.

**Các cột quan trọng:**
| Cột | Ý nghĩa |
|---|---|
| `customer_id` | UUID — PK định danh khách hàng. |
| `kyc_status` | Trạng thái xác thực danh tính. |
| `date_of_birth` | Tuổi — Đây là một Model Feature rất quan trọng cho AI. |
| `gender`, `job`, `income_level` | Các đặc trưng cá nhân dùng để đánh giá tín dụng và gửi vào AI. |
| `latitude`, `longitude` | Tọa độ nhà/vị trí khách hàng. |

**Tại sao cần:** Để AI model biết "người này 20 tuổi, thu nhập thấp, ở xa điểm giao dịch" mà tính rủi ro, thay vì chỉ nhìn vào số tiền.

### 3. `merchants`
**Làm gì:** Thông tin Cửa hàng / Đơn vị chấp nhận thanh toán.

**Các cột quan trọng:**
| Cột | Ý nghĩa |
|---|---|
| `merchant_category` | Danh mục kinh doanh (FOOD, LUXURY...). Rất quan trọng để tính điểm fraud. |
| `is_blacklisted` | Bị vào danh sách đen (Tự động chuyển giao dịch vào loại MANUAL_REVIEW). |
| `risk_level` | Mức độ rủi ro (LOW, MEDIUM, HIGH). |

### 4. `channels`
**Làm gì:** Kênh giao dịch (ATM, POS, Mobile, Online). 

**Tại sao cần:** Tách thành bảng riêng chuẩn hóa thay vì ghi text lặp đi lặp lại. Kênh Online nặc danh bao giờ cũng bị AI chấm điểm fraud cao hơn kênh thẻ từ chạm ATM vật lý.

---

## Nhóm 3 — Lõi xử lý giao dịch phân tích (Transaction Core)

### 5. `transactions_live`
**Làm gì:** Trái tim của hệ thống. Chứa mọi giao dịch thanh toán gửi đến và ghi nhận luôn quyết định của AI.  
*(Lưu ý bản 2.0: Xóa bảng `risk_scoring_results`, tích hợp luôn `fraud_score` và cập nhật trực tiếp vào đây để tăng hiệu suất. Không còn `merch_lat` vì vi phạm chuẩn 3NF).*

**Các cột quan trọng:**
| Cột | Ý nghĩa |
|---|---|
| `txn_id` | UUID — PK. |
| `amount` | Số tiền (Có ràng buộc CHECK > 0). |
| `card_number_hash` | SHA256 của số thẻ — phục vụ đối chiếu thống kê tốc độ thẻ. |
| `status` | PENDING → APPROVED / REJECTED / MANUAL_REVIEW |
| `fraud_score` | Điểm gian lận trực tiếp do AI tạo ra (0.0 đến 1.0). |
| `model_version` | Model AI Version nào đã chấm điểm cho giao dịch này. |

**FK (Khóa ngoại):** Trỏ về `customers`, `merchants`, `channels`, `users` (người tạo-submitted_by).  
**Index:** Sinh index trên `status`, `txn_time`, `customer_id`, `merchant_id` để lọc báo cáo tốc độ cao.

### 6. `rule_hits`
**Làm gì:** Lưu bằng chứng giải thích cho Model (Explainability).

**Tại sao cần:** AI từ chối một giao dịch, Reviewer mở hồ sơ ra phải biết *TẠI SAO*. Bảng này sẽ ghi lại các dòng lỗi như: "Giao dịch nửa đêm", "Khách ở HN nhưng thẻ quẹt ở TPHCM".  
**Đặc điểm:** Nhiều dòng trỏ về cùng 1 `txn_id`.

---

## Nhóm 4 — Workflow Quản lý rủi ro (Case Management)

### 7. `review_cases`
**Làm gì:** Hồ sơ Reviewer nhảy vào duyệt tay (Trường hợp AI trả ra MANUAL_REVIEW).  
*(Lưu ý bản 2.0: Đã lược bỏ `review_case_actions` vì các vết lịch sử timeline action sẽ được ném chung vào `audit_logs`).*

**Các cột quan trọng:**
| Cột | Ý nghĩa |
|---|---|
| `case_status` | Gồm 3 trạng thái gọn gàng: OPEN → ASSIGNED → CLOSED |
| `decision` | APPROVE / REJECT |
| `version` | Dùng cho Cơ chế **Optimistic Locking** đảm bảo không có 2 Reviewer cùng click xử lý 1 case. |
| `decision_note` | Ghi chú của Reviewer vì sao duyệt/từ chối. |

**FK:** Trỏ ngược về `transactions_live` (`txn_id` dạng UNIQUE). Chỉ 1 giao dịch sinh đúng 1 case.

---

## Nhóm 5 — Phân tích Tín dụng (Loans)

### 8. `loans`
**Làm gì:** Hệ thống cấp nợ/Khoản vay cho Khách Hàng. AI chấm điểm vỡ nợ.

**Chuẩn hóa 5NF Siêu việt:** 
Toàn bộ thông tin cá nhân khách hàng *tại lúc nộp hồ sơ vay* (Tuổi - `person_age`, Thu nhập - `person_income`, Nhà ở - `person_home_ownership`) được copy lưu thành SNAPSHOT thẳng vào bảng `loans`.  
**Tại sao không tham chiếu FK về bảng `customers` cho những cột này?** Vì 3 năm sau khách hàng già đi, thu nhập thay đổi. Nếu ta join sang, hồ sơ rủi ro quá khứ bị biến dạng. Thiết kế lưu snapshot này đảm bảo 100% vẹn toàn quá khứ (Tuân thủ mô hình sự kiện tài chính).

**Các cột quan trọng:**
| Cột | Ý nghĩa |
|---|---|
| `principal_amount` | Số tiền vay. |
| `interest_rate` | Lãi suất vay (0.1 = 10%). |
| `pd_score` | AI chấm điểm: Xác suất vỡ nợ (Probability of Default 0-1). |
| `status` | PENDING / APPROVED / REJECTED / DISBURSED... |
| `version` | Optimistic Locking. |

---

## Nhóm 6 — Cấu hình Machine Learning

### 9. `model_configs`
**Làm gì:** Thông số Threshold cấu hình Model do DATA ANALYST chỉnh sửa. (Thay vì Hardcode trong Code).

**Tại sao cần:** Mùa dịch, rủi ro cao, Analyst muốn siết chặt quy định (chuyển ngưỡng từ chối Fraud từ `>= 0.8` xuống `>= 0.6`). Họ chỉ cần vào DB sửa bảng này, không cần DevOps phải đem code ra deploy lại toàn server.

**Các cột quan trọng:**
| Cột | Ý nghĩa |
|---|---|
| `model_name` | fraud / loan |
| `param_name`, `param_value` | Ví dụ: `reject_threshold` = `0.6` |

### 10. `card_velocity_stats`
**Làm gì:** Khối AI cần biết "Chiếc thẻ này đang quẹt bao nhiêu lần/giây." Nếu dùng hàm `SUM/AVG` quét trên hàng triệu `transactions_live` thì server sập ngay.

**Cách hoạt động:** Dùng công thức chuẩn toán học Welford. Bảng cache lại mỗi thẻ 1 dòng. Khi thẻ đó quẹt, trigger sẽ cập nhật incremental vào `m2_amt`, `avg_amt`. Cực kỳ nhẹ và siêu nhanh.

---

## Nhóm 7 — Kiểm toán hệ thống tuyệt đối (Audit Module)

### 11. `audit_logs`
**Làm gì:** "Chiếc hộp đen phi cơ" chép lại toàn bộ Timeline.  
*(Lưu ý bản 2.0: Bảng này gom tất cả `txn_state_history`, `etl_logs`, `review_actions` lỉnh kỉnh hồi xưa vào 1 đầu mối).*

**Luật giang hồ:** Code ứng dụng **KHÔNG ĐƯỢC PHÉP `UPDATE` hay `DELETE`** bảng này. Nó là bằng chứng pháp lý (SOX Compliance). Chỉ được `INSERT`.

**Các cột quan trọng:**
| Cột | Ý nghĩa |
|---|---|
| `event_type` | Loại sự kiện (TXN_STATUS_CHANGED, CASE_ASSIGNED, SYS_CONFIG_UPDATE...) |
| `entity_type`, `entity_id` | Sự kiện đánh vào bảng nào, khóa là gì (VD: TRANSACTION, 'uuid-123') |
| `actor_user_id` | Ai bấm nút sinh ra sự kiện này. |
| `detail_json` | **CLOB**. Chứa 1 đoạn JSON DIFF báo rõ: Cột `status` bị đổi từ `PENDING` thành `APPROVED`. |

---

## Phần Tổng Kết — Sơ đồ & Dấu Khóa Quan Hệ Các Bảng (Relationships)

Để dễ hình dung hệ thống khi nối bảng (JOIN), dưới đây là mô tả chi tiết cách 11 bảng móc nối với nhau thông qua **Các mối quan hệ (Relational Mapping)**:

### 1. Quan hệ 1-Nhiều (1:N) - Luồng Dữ liệu chính
Đây là các quan hệ phổ biến nhất, khi 1 dòng ở bảng Cốt lõi/Tham chiếu sinh ra rất nhiều dòng ở bảng Giao dịch.

*   `customers` (1) ─◄ `transactions_live` (N): Một **Khách hàng** có thể thực hiện hàng ngàn **Giao dịch**. FK: `customer_id`.
*   `merchants` (1) ─◄ `transactions_live` (N): Một **Cửa hàng** có thể tiếp nhận hàng triệu **Giao dịch**. FK: `merchant_id`.
*   `channels` (1)  ─◄ `transactions_live` (N): Một **Kênh thanh toán** (VD: POS) xử lý rất nhiều **Giao dịch**. FK: `channel_id`.
*   `users` (1)     ─◄ `transactions_live` (N): Một **Nhân viên (Operator)** có thể nộp nhiều **Giao dịch**. FK: `submitted_by`.
*   `users` (1)     ─◄ `review_cases` (N): Một **Reviewer** có thể được assign nhiều **Hồ sơ xét duyệt (Case)**. FK: `assigned_to`.
*   `transactions_live` (1) ─◄ `rule_hits` (N): Một **Giao dịch vi phạm** có thể dính nhiều **Luật rủi ro (Rule)** cùng lúc (VD: Vừa ở nước ngoài, vừa quẹt nửa đêm). FK: `txn_id`.
*   `customers` (1) ─◄ `loans` (N): Một **Khách hàng** có thể nộp nhiều **Đơn vay vốn**. FK: `customer_id`.

### 2. Quan hệ 1-1 (1:1) - Luồng Mở rộng trực tiếp
*   `transactions_live` (1) ── `review_cases` (1): Nếu giao dịch bị nghi ngờ gian lận (MANUAL_REVIEW), nó sinh ra **đúng 1 hồ sơ xét duyệt** trong bảng `review_cases`. Phía `review_cases` dùng trường `txn_id` dạng `UNIQUE` để khóa cứng ràng buộc này.

### 3. Phụ thuộc Mềm và Dấu Vết (Audit/Config)
*   **Bảng `audit_logs` (Nhật ký Hệ thống):** Liên kết về `users` (1:N) thông qua khóa ngoại `actor_user_id` để biết ai là người vừa thực hiện Update/Insert. Đối với Entity bị chỉnh sửa (như *Transaction*, *Loan*, *Case*), bảng Audit **không dùng Foreign Key cứng** mà dùng cặp `(entity_type, entity_id)` để giữ tính chất Generic (để lỡ sau này có xóa bỏ Entity cũng không bị lỗi Ràng buộc toàn vẹn lịch sử).
*   **Bảng `card_velocity_stats`:** Khóa chính là `card_hash` - trùng khớp với `card_number_hash` trong `transactions_live`. AI hoặc DB Trigger sẽ lookup matching string thay vì Join Foreign Key truyền thống để đảm bảo tốc độ cực đại (O(1)).

### Sơ đồ Luồng Hoạt Động Điển Hình
```text
[1. THAM CHIẾU NGUỒN]
    customers   merchants   channels   users(OPERATOR)
        │           │           │          │
        └───────────┼───────────┼──────────┘
                    ▼
[2. CORE GIAO DỊCH] 
          transactions_live  ───────────► rule_hits (Ai bắt lỗi gì?)
              │ (Nếu status = MANUAL_REVIEW)
              ▼
[3. XỬ LÝ NHÂN CÔNG]
          review_cases ◄──────── users(REVIEWER)
              │
[TẤT CẢ MODULE] ─── (Trigger / Diff JSON) ───►  [4. HỘP ĐEN KIỂM TOÁN]
                                                      audit_logs
```

