# Giải thích toàn bộ Schema Database — HPTRRĐGTC (Phiên bản 2.0 Tinh Gọn)

> Đọc một lần, hiểu toàn bộ thiết kế.  
> Mỗi bảng: **làm gì → lưu gì → tại sao cần → FK về đâu → Index nào → ràng buộc gì**.

---

Đọc phần này trước. Hiểu rồi thì đọc bảng nào cũng rõ ngay.

---

### Foreign Key (FK) là gì?

FK là **khoá ngoại** — một cột trong bảng này trỏ đến khoá chính (PK) của bảng khác.

**Ví dụ thực tế:**
```text
transactions_live.customer_id  →  customers.customer_id
```
Nghĩa là: cột `customer_id` trong bảng giao dịch **phải tồn tại** trong bảng `customers`.  
Nếu bạn INSERT một giao dịch với `customer_id = 'abc'` mà `customers` không có dòng `customer_id = 'abc'` → DB sẽ **báo lỗi ngay**, không cho phép ghi vào.

**Tại sao cần FK?**
- Đảm bảo tính nhất quán dữ liệu — không bao giờ có giao dịch "mồ côi" không biết của ai
- Khi JOIN 2 bảng, DB optimizer biết đây là quan hệ hợp lệ → chạy nhanh hơn
- Tài liệu sống: nhìn vào FK là hiểu ngay bảng nào liên quan bảng nào

---

### Index là gì?

Index là **mục lục** — giống như mục lục cuối sách giáo khoa. Không có mục lục, muốn tìm "trang nói về quang hợp" phải lật từng trang. Có mục lục, mở thẳng trang đó luôn.

**Ví dụ không có index:**
```sql
SELECT * FROM transactions_live WHERE customer_id = 'abc-123';
```
DB phải đọc **toàn bộ bảng** từ đầu đến cuối để tìm (gọi là Full Table Scan).  
Với 10 triệu giao dịch → có thể mất **vài giây** hoặc **timeout**.

**Ví dụ có index trên `customer_id`:**
DB dùng cấu trúc B-Tree đã được sắp xếp sẵn → nhảy thẳng đến đúng vị trí.  
Query đó chạy trong **vài milliseconds**.

**Index có nhược điểm không?**  
Có — mỗi lần INSERT/UPDATE, DB phải cập nhật cả index → INSERT chậm hơn một chút.  
Vì vậy không index tất cả mọi cột — chỉ index cột **thường xuyên xuất hiện trong WHERE, ORDER BY, JOIN**.

---

### CHECK Constraint là gì?

CHECK là **ràng buộc giá trị** — chỉ cho phép ghi giá trị nằm trong tập hợp đã định.

**Ví dụ:**
```sql
CONSTRAINT chk_txn_status CHECK ("status" IN ('PENDING','APPROVED','REJECTED','MANUAL_REVIEW'))
```
Nếu code ghi `status = 'TYPO'` hoặc `status = 'approved'` (chữ thường) → DB báo lỗi ngay.  
Không có CHECK, lỗi typo trong code sẽ âm thầm ghi dữ liệu sai vào DB → rất khó debug.

---

### Optimistic Locking là gì?

Là kỹ thuật tránh **2 người cùng sửa 1 dòng cùng lúc** mà không cần khoá (lock) bảng.

**Cách hoạt động** — mỗi dòng có cột `version` (số nguyên, bắt đầu từ 1):
1. User A đọc dòng → thấy `version = 3`
2. User B đọc dòng đó cùng lúc → cũng thấy `version = 3`
3. User A gửi UPDATE kèm `version = 3` → DB tăng lên `version = 4` → thành công
4. User B gửi UPDATE kèm `version = 3` → DB kiểm tra: version hiện tại là 4, không phải 3 → **trả lỗi 409 CONFLICT**

User B biết có người sửa trước → phải đọc lại dữ liệu mới nhất rồi mới sửa.  
Không ai mất dữ liệu, không ai ghi đè không biết.

---

### CLOB vs VARCHAR là gì?

- `VARCHAR(4000)` — lưu tối đa 4000 ký tự. Quá giới hạn → lỗi hoặc bị cắt bớt
- `CLOB` (Character Large Object) — lưu được đến **4 GB** văn bản

Dùng CLOB khi nội dung có thể rất dài: JSON báo cáo, lịch sử dữ liệu chi tiết.

---

### Server DEFAULT là gì?

Là giá trị **DB tự điền** nếu code không truyền giá trị vào khi INSERT.

```sql
"created_at" timestamp DEFAULT SYSTIMESTAMP NOT NULL
```
Nếu code không truyền `created_at` → Oracle tự điền thời gian hiện tại.  
Không có DEFAULT mà cột là `NOT NULL` → INSERT không truyền giá trị → **lỗi ORA-01400**.

---

---

## Nhóm 1 — Phân quyền & Người dùng (Auth & Users)

---

### 1. `users`
**Làm gì:** Lưu tài khoản nhân viên và phân quyền trong hệ thống. Ở bản 2.0, bảng roles đã được gộp thẳng vào đây để tối ưu.

**Các cột quan trọng:**
| Cột | Kiểu | Ý nghĩa |
|---|---|---|
| `user_id` | varchar(36) PK | UUID — định danh duy nhất |
| `username` | varchar(100) UNIQUE | Tên đăng nhập, không được trùng |
| `password_hash` | varchar(255) | Mật khẩu đã hash (bcrypt) — không bao giờ lưu mật khẩu thật |
| `role` | varchar(20) | Xác định quyền: OPERATOR, REVIEWER, ANALYST, MANAGER, ADMIN |
| `status` | varchar(20) | ACTIVE hoặc DISABLED |

**FK:** Không có (bảng gốc).

**Index:**
- `idx_users_role` trên `role` để liệt kê nhanh danh sách theo quyền.
- `idx_users_status` trên `status` để lọc tài khoản đang bị khoá.

**CHECK constraints:**
- `role` chỉ được phép nằm trong 5 vai trò hệ thống quy định.
- `status` chỉ nhận ACTIVE / DISABLED.

**Tại sao cần:** Bất kỳ thao tác nào tạo ra dữ liệu, duyệt giao dịch, đổi config đều phải gắn với 1 user. Thiếu bảng này hệ thống không biết ai đang thực thi hành động gì, không thể rà soát truy vết (Audit).

---

## Nhóm 2 — Dữ liệu tham chiếu (Master / Reference Data)

> Các bảng này được nạp sẵn từ hệ thống Core Banking. Ứng dụng HPTRRĐGTC **chỉ đọc**, không quản lý.

---

### 2. `customers`
**Làm gì:** Hồ sơ khách hàng chủ thẻ.

**Các cột quan trọng:**
| Cột | Ý nghĩa |
|---|---|
| `customer_id` | UUID — định danh duy nhất |
| `customer_code` | Mã nội bộ ngân hàng (VD: CUST00001) |
| `date_of_birth` | Ngày sinh — Feature quan trọng cho ML (Tuổi tác) |
| `job`, `income_level` | Feature ML về nghề nghiệp, thu nhập ảnh hưởng độ tin cậy |
| `latitude`, `longitude` | Toạ độ nhà — Dùng tính khoảng cách tới điểm giao dịch. |

**Tại sao cần:** Khi Model AI chấm điểm 1 giao dịch, nó không chỉ nhìn vào số tiền, mà còn nhìn vào "Ai đang giao dịch". Người thu nhập thấp, thẻ mở hôm qua giao dịch mua sắm 50 triệu sẽ rủi ro hơn người thu nhập cao giao dịch mua sắm 50 triệu. Không có bảng này thì AI bị mù thông tin.

---

### 3. `merchants`
**Làm gì:** Danh sách các điểm bán hàng (Đơn vị chấp nhận thẻ).

**Các cột quan trọng:**
| Cột | Ý nghĩa |
|---|---|
| `merchant_category` | Lĩnh vực kinh doanh (Nhà hàng, Điện máy, Quán Bar...) |
| `latitude`, `longitude` | Toạ độ merchant |
| `is_blacklisted` | 1 = Cửa hàng nằm trong danh sách đen lừa đảo |

**Tại sao cần:** Giao dịch ở một Quán Bar lúc 2 giờ sáng rủi ro cao hơn mua thực phẩm ở Siêu thị lúc 9 giờ sáng. Ngoài ra, trường hợp merchant bị `is_blacklisted = 1`, mọi giao dịch tự động chuyển sang MANUAL_REVIEW hoặc từ chối ngay lập tức.

---

### 4. `channels`
**Làm gì:** Bảng tra cứu kênh thực hiện giao dịch (POS, ATM, Online, Mobile_App...).

**Tại sao cần:** Kênh giao dịch thanh toán không chạm qua Internet (Online) có nguy cơ gian lận cao hơn nhiều so với việc quẹt thẻ chip vật lý tại máy POS. Nó là 1 biến quan trọng cho hệ thống AI.

---

## Nhóm 3 — Lõi xử lý giao dịch (Transaction Core)

---

### 5. `transactions_live`
**Làm gì:** Bảng **trái tim của hệ thống**, lưu mọi giao dịch diễn ra theo thời gian thực (OLTP). Trong bản 2.0, kết quả chấm điểm của AI (`fraud_score`) được gộp luôn vào đây để tăng tốc đọc dữ liệu.

**Các cột quan trọng:**
| Cột | Ý nghĩa |
|---|---|
| `txn_id` | UUID — PK |
| `customer_id`, `merchant_id` | Người giao dịch và nơi giao dịch |
| `card_number_hash` | Chuỗi mã hoá của thẻ — Dùng tra cứu lịch sử thẻ mà không lộ thẻ thật. |
| `amount`, `currency_code` | Số tiền và đơn vị (USD/VND) |
| `status` | PENDING / APPROVED / REJECTED / MANUAL_REVIEW |
| `fraud_score` | Điểm do AI trả về, từ 0.00 đến 1.00 (gộp từ bảng risk scoring cũ) |

**FK:**
- Trỏ tới 4 bảng: `customers`, `merchants`, `channels`, `users` (để biết OPERATOR nào push giao dịch lên).

**Index:** Rất nhiều index để hỗ trợ truy vấn siêu tốc:
- `idx_txn_live_status` (Trích lọc các giao dịch cần duyệt nhanh)
- `idx_txn_live_time` (Truy vấn theo tháng/ngày)
- `idx_txn_live_cust`, `idx_txn_live_merch` (Tìm theo KH hoặc Cửa hàng)

**CHECK constraints:**
- `amount > 0` (Ngăn chặn việc truyền số tiền âm)
- `fraud_score BETWEEN 0 AND 1`
- `status IN ('PENDING','APPROVED','REJECTED','MANUAL_REVIEW')`

**Tại sao cần:** Thiếu bảng này hệ thống không hoạt động. Mọi thuật toán AI sinh ra đều là để đánh giá dữ liệu rơi vào bảng này.

---

## Nhóm 4 — Quản lý Xét duyệt (Case Management & Loans)

---

### 6. `review_cases`
**Làm gì:** Mỗi giao dịch bị AI gắn cờ rủi ro (`status = MANUAL_REVIEW`), một Trigger tự động sẽ tạo ra 1 "Hồ sơ xét duyệt tay" ở bảng này.

**Các cột quan trọng:**
| Cột | Ý nghĩa |
|---|---|
| `case_status` | OPEN (đang chờ) → ASSIGNED (có người nhận) → CLOSED (xong) |
| `assigned_to` | FK → `users`. REVIEWER nào đang theo dõi case này |
| `decision` | APPROVE hoặc REJECT |
| `version` | Optimistic Locking — Chống tranh giành (2 người cùng nhận 1 case) |

**FK:** `txn_id` → `transactions_live` (UNIQUE constraint, 1 giao dịch chỉ tạo 1 case)

**Tại sao cần:** Giao dịch và Case là 2 vòng đời khác nhau. Giao dịch hợp lệ không cần tạo Case. Tách riêng bảng này giúp Reviewer quản lý tiến độ xử lý độc lập mà không cần phải can thiệp trực tiếp vào bảng giao dịch đang rất nóng (live).

---

### 7. `loans`
**Làm gì:** Bảng lưu trữ hồ sơ đề nghị vay vốn tín chấp.

**Các cột quan trọng:**
| Cột | Ý nghĩa |
|---|---|
| `principal_amount` | Số tiền vay đề nghị |
| `status` | PENDING / APPROVED / REJECTED / DISBURSED / CLOSED |
| `pd_score` | Probability of Default: Điểm khả năng vỡ nợ do AI tính toán |
| `person_age`, `person_income`... | Snapshot thông tin người dùng ngay **tại thời điểm nộp đơn** |

**Tại sao cần Snapshot thông tin?**
Một người năm nay 25 tuổi, thu nhập 10 triệu nộp hồ sơ vay. 5 năm sau, họ 30 tuổi, thu nhập 50 triệu. Hệ thống Model AI đã chấm họ vào thời điểm quá khứ (25 tuổi, 10 triệu). Nếu ta JOIN với bảng `customers` hiện tại thì dữ liệu AI chấm sẽ mất logic. Việc snapshot ngay tại bảng loans giúp lưu lại "lịch sử sự thật" lúc chấm điểm.

---

## Nhóm 5 — Phân tích & AI (Analyst)

---

### 8. `model_configs`
**Làm gì:** Lưu **ngưỡng phân loại AI**. Các mức độ cảnh báo (threshold) được tách ra khỏi code.

**Các cột quan trọng:**
| Cột | Ý nghĩa |
|---|---|
| `model_name` | fraud hoặc loan |
| `param_name` | reject_threshold, review_threshold... |
| `param_value` | Mức giá trị (VD: 0.60) |

**Tại sao cần:** Các ngưỡng này thường xuyên biến động theo mùa rủi ro. Việc đưa nó vào Database giúp Analyst (Chuyên viên PT Rủi ro) thay đổi cấu hình trên giao diện Web theo thời gian thực mà không cần gọi Dev để sửa Code Backend.

---

### 9. `rule_hits`
**Làm gì:** Khi AI hoặc hệ thống phát hiện giao dịch rủi ro, nó bị đánh một loạt các mã quy tắc (Rule Code). Ví dụ: `RULE_NIGHT_TIME`, `RULE_BLACKLIST_MERCHANT`. Bảng này lưu lại các mã đó.

**Tại sao cần:** Nó mang lại tính "Giải thích được" (Explainability) cho AI. Khi REVIEWER xử lý 1 giao dịch bị chặn, họ cần biết: "Tại sao nó bị chặn?". Bảng này cung cấp các lý do rõ ràng.

---

### 10. `card_velocity_stats`
**Làm gì:** Cache bộ đếm thống kê tốc độ cà thẻ (Velocity). 

**Các cột quan trọng:**
| Cột | Ý nghĩa |
|---|---|
| `card_hash` | Chuỗi mã hoá số thẻ (PK) |
| `avg_daily_txn` | Trung bình số lần cà thẻ / ngày |
| `std_amt` | Độ lệch chuẩn số tiền giao dịch |

**Tại sao cần:** Hacker lấy cắp thẻ thường quẹt liên tục 20 lần trong 5 phút ở các cửa hàng nhỏ (Velocity attack). Việc tính toán trung bình (`AVG`), độ lệch chuẩn (`STDDEV`) trực tiếp từ bảng 10 triệu giao dịch quá lâu. Bảng `card_velocity_stats` sử dụng thuật toán Welford để lưu sẵn biến tính toán trước, giúp việc phát hiện tốc độ quẹt thẻ lạ chỉ mất ~1 millisecond.

---

## Nhóm 6 — Kiểm toán (Audit & Log)

---

### 11. `audit_logs`
**Làm gì:** "Hộp đen" của toàn bộ hệ thống. Bảng này lưu lại mọi hoạt động thay đổi mang tính cốt lõi (Ai đổi trạng thái giao dịch? Ai tạo case? Ai đổi cấu hình AI?).

**Các cột quan trọng:**
| Cột | Ý nghĩa |
|---|---|
| `event_type` | Loại hành động (CREATE_TXN, STATUS_CHANGE...) |
| `entity_type` | Loại đối tượng bị tác động (TRANSACTION, REVIEW_CASE, CONFIG) |
| `actor_user_id` | Ai gây ra sự kiện này |
| `detail_json` | **CLOB**: Chứa JSON gói gọn chi tiết giá trị từ cũ sang mới. |

**Tại sao dùng CLOB cho `detail_json`?**  
Dữ liệu lưu vết có thể bao gồm toàn bộ Payload 50 cột của 1 khoản vay. Kiểu `VARCHAR` 4000 ký tự sẽ bị tràn, nên phải dùng `CLOB` (cho phép lưu hàng GB văn bản).

**Tại sao cần Audit?**  
Trong ngành tài chính, các bảng như Giao dịch hay Cấu hình rủi ro nếu có sửa đổi mà không giải trình được ai làm, thì sẽ bị tước giấy phép. Bảng `audit_logs` có quy tắc bất di bất dịch: **Chỉ được INSERT, cấm tuyệt đối UPDATE và DELETE**. Mọi sự kiện đều trở thành bằng chứng pháp lý vững chắc.
