# Giải thích toàn bộ Schema Database — HPTRRĐGTC

> Đọc một lần, hiểu toàn bộ thiết kế.  
> Mỗi bảng: **làm gì → lưu gì → tại sao cần → FK về đâu → Index nào → ràng buộc gì**.

---

## Phần 0 — Khái niệm nền cần biết trước

Đọc phần này trước. Hiểu rồi thì đọc bảng nào cũng rõ ngay.

---

### Foreign Key (FK) là gì?

FK là **khoá ngoại** — một cột trong bảng này trỏ đến khoá chính (PK) của bảng khác.

**Ví dụ thực tế:**
```
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

Dùng CLOB khi nội dung có thể rất dài: JSON phân tích AI, nội dung báo cáo Markdown, lý do chi tiết.

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

## Nhóm 1 — Phân quyền (Auth & Roles)

---

### `users`
**Làm gì:** Lưu tài khoản người dùng hệ thống.

**Các cột quan trọng:**
| Cột | Kiểu | Ý nghĩa |
|---|---|---|
| `user_id` | varchar(36) PK | UUID — định danh duy nhất |
| `username` | varchar(100) UNIQUE | Tên đăng nhập, không được trùng |
| `password_hash` | varchar(255) | Mật khẩu đã hash (bcrypt) — không lưu mật khẩu thật |
| `is_active` | number(1) | 1 = tài khoản hoạt động, 0 = đã khoá |
| `updated_at` | timestamp | Theo dõi lần cuối đổi mật khẩu hoặc role |

**Tại sao cần:** Mọi hành động trong hệ thống đều gắn với một `user_id`. Không có bảng này thì không biết ai làm gì.

---

### `roles`
**Làm gì:** Danh mục các vai trò trong hệ thống.

**Các giá trị thực tế:**
`OPERATOR`, `REVIEWER`, `ANALYST`, `MANAGER`, `ADMIN`

**Tại sao cần:** Tách role ra bảng riêng thay vì hardcode trong `users` → dễ thêm role mới mà không phải sửa cấu trúc bảng `users`.

---

### `user_roles`
**Làm gì:** Bảng trung gian nối `users` ↔ `roles` — một người có thể có nhiều role.

**FK:**
- `user_id` → `users.user_id` — user phải tồn tại
- `role_id` → `roles.role_id` — role phải tồn tại

**Tại sao cần:** Quan hệ nhiều-nhiều (Many-to-Many). Một ADMIN có thể đồng thời có role MANAGER. Không thể lưu nhiều role vào một cột trong `users` → phải dùng bảng trung gian.

---

---

## Nhóm 2 — Dữ liệu tham chiếu (Master / Reference Data)

> Các bảng này do **Core Banking của ngân hàng đối tác** cung cấp qua ETL.  
> Hệ thống HPTRRĐGTC **chỉ đọc**, không tạo mới hay xoá customer/merchant.

---

### `customers`
**Làm gì:** Hồ sơ khách hàng chủ thẻ — nguồn gốc từ Core Banking.

**Các cột quan trọng:**
| Cột | Ý nghĩa |
|---|---|
| `customer_id` | UUID — định danh duy nhất |
| `customer_code` | Mã nội bộ ngân hàng (CUST00001...) |
| `kyc_status` | PENDING / VERIFIED / REJECTED — kết quả xác thực danh tính |
| `date_of_birth` | Tuổi — feature quan trọng cho ML (khách trẻ = rủi ro khác khách lớn tuổi) |
| `gender`, `job` | Features ML — tần suất encoding |
| `latitude`, `longitude` | Toạ độ nhà khách hàng — tính khoảng cách đến merchant khi chấm điểm |
| `city_population` | Dân số thành phố — feature ML theo Sparkov dataset |
| `income_level` | LOW / MEDIUM / HIGH — ảnh hưởng ngưỡng xét duyệt khoản vay |

**FK:** Không có FK ra ngoài — đây là bảng gốc.

**Tại sao cần:** ML model cần biết "người này sống ở đâu, làm gì, bao nhiêu tuổi" để tính xác suất gian lận. Thiếu bảng này, model chỉ nhìn được số tiền giao dịch — kém chính xác hơn nhiều.

---

### `merchants`
**Làm gì:** Danh sách đơn vị chấp nhận thanh toán — nguồn từ Core Banking.

**Các cột quan trọng:**
| Cột | Ý nghĩa |
|---|---|
| `merchant_category` | Ngành nghề: FOOD / RETAIL / ENTERTAINMENT... — feature ML quan trọng |
| `latitude`, `longitude` | Toạ độ merchant — tính khoảng cách đến nhà khách hàng |
| `risk_level` | LOW / MEDIUM / HIGH — pre-labeled bởi bộ phận risk |
| `is_blacklisted` | 1 = merchant trong danh sách đen → giao dịch tự động MANUAL_REVIEW |

**Tại sao cần:** Giao dịch tại merchant rủi ro cao = cần ngưỡng fraud thấp hơn. Không có bảng này, model AI không phân biệt được "mua cà phê ở Highlands" vs "giao dịch tại casino nước ngoài".

---

### `channels`
**Làm gì:** Bảng tra cứu kênh giao dịch — POS / ATM / ONLINE / MOBILE_APP.

**Tại sao cần:** Lưu riêng thay vì ghi chuỗi thẳng vào `transactions_live` để tránh lặp dữ liệu và dễ thêm kênh mới. Kênh online luôn rủi ro hơn kênh có chip thẻ vật lý — cần phân biệt rõ.

---

---

## Nhóm 3 — Lõi xử lý giao dịch (Transaction Core)

---

### `transactions_live`
**Làm gì:** Bảng **trung tâm của toàn hệ thống** — lưu mọi giao dịch OLTP đang hoạt động.

**Các cột quan trọng:**
| Cột | Ý nghĩa |
|---|---|
| `txn_id` | UUID — PK |
| `submitted_by` | FK → `users.user_id` — OPERATOR nào gửi giao dịch này |
| `card_number_masked` | Số thẻ đã che (4111 \*\*\*\* \*\*\*\* 1111) — chỉ để hiển thị |
| `card_number_hash` | SHA256 của số thẻ thật — dùng tra cứu velocity stats và suppression rules mà không lưu số thẻ raw |
| `currency_code` | ISO 4217, mặc định USD |
| `status` | PENDING → APPROVED / REJECTED / MANUAL_REVIEW |
| `fraud_score` | 0.0–1.0 — điểm gian lận từ model AI |
| `override_reason` | Lý do hệ thống ghi đè quyết định AI (VD: HIGH_VALUE, BLACKLISTED_MERCHANT) |
| `merch_lat`, `merch_long`, `unix_time` | Snapshot toạ độ merchant và epoch time tại lúc giao dịch — dùng cho training data pipeline |

**FK:**
- `customer_id` → `customers` — giao dịch phải thuộc về customer có thật
- `merchant_id` → `merchants` — giao dịch phải tại merchant có thật
- `channel_id` → `channels` — kênh phải hợp lệ
- `submitted_by` → `users` — phải biết ai gửi

**Index:**
| Index | Cột | Lý do |
|---|---|---|
| `idx_transactions_status` | `status` | Lọc PENDING / MANUAL_REVIEW — query rất phổ biến |
| `idx_txn_live_time` | `txn_time` | Tìm giao dịch trong khoảng ngày giờ |
| `idx_txn_live_cust` | `customer_id` | Xem lịch sử giao dịch của 1 khách hàng |
| `idx_txn_live_merch` | `merchant_id` | Xem giao dịch tại 1 merchant |
| `idx_txn_live_card_hash` | `card_number_hash` | Tra cứu suppression rules theo thẻ |
| `idx_txn_live_submitted` | `submitted_by` | OPERATOR chỉ thấy giao dịch do mình gửi — lọc theo cột này |

**CHECK constraints:**
- `amount > 0` — không cho phép giao dịch âm hoặc bằng 0
- `fraud_score BETWEEN 0 AND 1` — điểm AI phải trong khoảng hợp lệ
- `status IN (...)` — chỉ nhận 4 giá trị hợp lệ

---

### `risk_scoring_results`
**Làm gì:** Lưu **bằng chứng chấm điểm** của mỗi lần AI/Rule engine phân tích một giao dịch.

**Các cột quan trọng:**
| Cột | Ý nghĩa |
|---|---|
| `model_version` | Phiên bản model AI đã dùng — quan trọng khi model upgrade |
| `fraud_score` | Điểm 0.0–1.0 |
| `decision_suggested` | AI đề xuất: APPROVED / REJECTED / MANUAL_REVIEW |
| `reason_json` | CLOB — JSON giải thích top features ảnh hưởng điểm (VD: `{"top_features": [{"name": "distance", "value": 850}]}`) |
| `reject_threshold` | Ngưỡng REJECT **tại thời điểm chấm điểm** — snapshot từ `model_configs` |
| `review_threshold` | Ngưỡng MANUAL_REVIEW tại thời điểm chấm điểm |
| `feature_snapshot_json` | CLOB — toàn bộ feature vector đã đưa vào model — dùng để tái tạo lại kết quả khi audit |

**FK:** `txn_id` → `transactions_live` — kết quả chấm điểm phải gắn với giao dịch có thật.

**Tại sao cần:** Khi khách hàng khiếu nại "tại sao giao dịch của tôi bị từ chối?", cần biết chính xác model nào chấm, điểm bao nhiêu, ngưỡng lúc đó là bao nhiêu, vì lý do gì. Nếu không lưu bảng này, câu trả lời sẽ mãi là "không rõ".  

Lý do lưu `reject_threshold` tại đây: ngưỡng có thể được ANALYST điều chỉnh. Sau này nếu ngưỡng thay đổi, vẫn biết lúc giao dịch xảy ra ngưỡng là bao nhiêu.

---

### `rule_hits`
**Làm gì:** Ghi lại từng rule nghiệp vụ nào đã bị kích hoạt trong một giao dịch.

**Ví dụ thực tế:**  
Giao dịch `TXN-001` trigger 3 rule cùng lúc → 3 dòng trong `rule_hits`:
1. `BLACKLISTED_MERCHANT` — severity HIGH
2. `NIGHT_TRANSACTION` — severity MEDIUM  
3. `AMOUNT_OVER_THRESHOLD` — severity HIGH

**FK:** `txn_id` → `transactions_live`

**Index:** `idx_rule_hits_code` trên `rule_code` — ANALYST hay hỏi "rule X này hit bao nhiêu lần trong tháng?" → không có index là full scan toàn bảng.

**Tại sao tách khỏi `risk_scoring_results`:** Một giao dịch kích hoạt nhiều rule → cần nhiều dòng. Không thể nhét tất cả rule hits vào 1 cột JSON trong bảng scoring — sẽ rất khó query và phân tích từng rule riêng lẻ.

---

---

## Nhóm 4 — Quản lý Case (Case Management)

---

### `review_cases`
**Làm gì:** Mỗi giao dịch bị đẩy vào `MANUAL_REVIEW` sẽ tự động tạo ra 1 "hồ sơ" ở đây.

**Các cột quan trọng:**
| Cột | Ý nghĩa |
|---|---|
| `case_status` | OPEN → ASSIGNED → APPROVED / REJECTED → CLOSED |
| `assigned_to` | FK → `users` — Reviewer nào đang xử lý case này |
| `decision` | APPROVE / REJECT — quyết định cuối |
| `decision_note` | varchar(2000) — Reviewer giải thích lý do quyết định |
| `version` | Optimistic Locking — tránh 2 Reviewer cùng duyệt 1 case |

**FK:**
- `txn_id` → `transactions_live` — case phải gắn với giao dịch có thật (UNIQUE — 1 giao dịch chỉ có 1 case)
- `assigned_to` → `users` — Reviewer phải là user hợp lệ

**Index:**
| Index | Lý do |
|---|---|
| `idx_case_status` | Reviewer dashboard lọc OPEN/ASSIGNED — query chạy liên tục |
| `idx_case_assigned` | Reviewer xem "case nào đang được giao cho tôi" |

**CHECK:** `case_status IN ('OPEN','ASSIGNED','APPROVED','REJECTED','CLOSED')`

**Tại sao tách khỏi `transactions_live`:** Giao dịch và case là 2 vòng đời khác nhau. Giao dịch có thể APPROVED mà không qua case. Reviewer làm việc trên case, không được phép sửa thẳng giao dịch — tách bảng để enforce quyền này.

---

### `review_case_actions`
**Làm gì:** Timeline lịch sử **từng hành động** trên một case — ai làm gì lúc mấy giờ.

**Ví dụ timeline:**
```
09:00 — ASSIGN  — Manager Hùng giao case cho Reviewer An
09:45 — COMMENT — Reviewer An: "Đang liên hệ xác minh với khách hàng"
10:30 — APPROVE — Reviewer An: "Khách xác nhận hợp lệ"
```

**FK:**
- `case_id` → `review_cases` — action phải thuộc về case có thật
- `actor_user_id` → `users` — phải biết ai thực hiện

**CHECK:** `action_type IN ('ASSIGN','COMMENT','APPROVE','REJECT','REOPEN')`

**Tại sao cần:** `review_cases` chỉ lưu trạng thái *hiện tại*. Nếu có tranh chấp về quy trình xét duyệt ("Ai duyệt case này? Lúc mấy giờ?"), bảng này là bằng chứng. Yêu cầu bắt buộc của compliance tài chính.

---

---

## Nhóm 5 — Idempotency & State Machine

---

### `txn_idempotency`
**Làm gì:** Bộ nhớ chống xử lý giao dịch trùng lặp.

**Vấn đề cần giải quyết:**  
Ngân hàng gửi giao dịch → mạng timeout → ngân hàng gửi lại (retry) → hệ thống xử lý lần 2 → **trừ tiền 2 lần**.

**Cách hoạt động:**
1. OPERATOR gửi giao dịch kèm `idempotency_key` (hash từ các trường cố định của giao dịch)
2. Hệ thống kiểm tra key này đã tồn tại chưa
3. Đã tồn tại → trả lại kết quả cũ, **không xử lý lại**
4. Chưa tồn tại → xử lý bình thường, lưu key + kết quả vào bảng này

**Các cột quan trọng:**
| Cột | Ý nghĩa |
|---|---|
| `idempotency_key` | PK — hash duy nhất của request |
| `txn_hash` | Hash toàn bộ payload — phát hiện nếu cùng key nhưng khác data |
| `response_snapshot_json` | Kết quả lần đầu xử lý — trả lại nguyên khi có retry |
| `status` | IN_PROGRESS / SUCCESS / FAILED |

**CHECK:** `status IN ('IN_PROGRESS','SUCCESS','FAILED')`

---

### `txn_state`
**Làm gì:** Lưu trạng thái **hiện tại** của giao dịch với cơ chế Optimistic Locking.

**Tại sao tách khỏi `transactions_live`?**  
Optimistic Locking cần lock đúng dòng cần cập nhật, không ảnh hưởng performance của bảng giao dịch chính. `transactions_live` có hàng triệu dòng và nhiều cột — lock dòng trong đó tốn kém. `txn_state` chỉ có `txn_id` + `status` + `version` → lock nhanh hơn, gọn hơn.

**Các cột quan trọng:**
| Cột | Ý nghĩa |
|---|---|
| `version` | Số nguyên tăng dần — trung tâm của Optimistic Locking |
| `retry_count` | Bao nhiêu lần đã retry xử lý (dùng cho circuit breaker) |
| `last_error_code` | Mã lỗi gần nhất — debug khi giao dịch bị stuck |
| `last_update` | DEFAULT SYSTIMESTAMP — tự điền thời gian hiện tại |

**FK:** `txn_id` → `transactions_live` (1-1 relationship)

**CHECK:** `status IN ('PENDING','APPROVED','REJECTED','MANUAL_REVIEW')`

---

### `txn_state_history`
**Làm gì:** Timeline toàn bộ lịch sử thay đổi trạng thái của một giao dịch.

**Ví dụ:**
```
PENDING → MANUAL_REVIEW  (fraud_score=0.55, lúc 14:00)
MANUAL_REVIEW → APPROVED  (Reviewer An duyệt lúc 14:30)
```

**Cách tạo ra:** Trigger `TRG_LOG_STATUS_CHANGE` tự động INSERT dòng mới mỗi khi `transactions_live.status` thay đổi — không cần code application gọi thêm.

**FK:**
- `txn_id` → `transactions_live`
- `changed_by_user_id` → `users` — ai thay đổi (NULL nếu do hệ thống tự động)

**Dùng cho:** API `GET /transactions/{id}/state-history` — trả về audit trail trạng thái cho client.

---

---

## Nhóm 6 — Chống Gian lận nâng cao

---

### `card_velocity_stats`
**Làm gì:** Cache thống kê lịch sử giao dịch theo từng số thẻ — **cập nhật sau mỗi giao dịch mới**.

**Vấn đề cần giải quyết:**  
Model AI cần biết "thẻ này trung bình giao dịch bao nhiêu lần/ngày, số tiền trung bình bao nhiêu" — đây là feature quan trọng nhất để phát hiện velocity attack (đánh cắp thẻ và liên tục giao dịch nhỏ).  
Không thể `SELECT AVG(amount) FROM transactions_live WHERE card_hash = ?` mỗi lần → quét hàng triệu dòng, quá chậm.

**Giải pháp:** Dùng **Welford's online algorithm** — cập nhật mean và variance incremental mà không cần lưu toàn bộ lịch sử.

**Các cột quan trọng:**
| Cột | Ý nghĩa |
|---|---|
| `card_hash` | SHA256 của số thẻ — PK. Không lưu số thẻ thật |
| `avg_daily_txn` | Trung bình số giao dịch/ngày |
| `total_txn` | Tổng số giao dịch từ trước đến nay |
| `avg_amt` | Trung bình số tiền mỗi giao dịch |
| `std_amt` | Độ lệch chuẩn — phát hiện giao dịch bất thường (outlier) |
| `m2_amt` | Biến trung gian của Welford algorithm — dùng tính `std_amt` mà không lưu toàn bộ lịch sử |
| `last_updated` | DEFAULT SYSTIMESTAMP — tự điền |

**Tại sao PK là `card_hash` (không phải auto-increment)?**  
Vì mỗi thẻ chỉ có 1 dòng. Khi có giao dịch mới: `UPSERT card_hash = ?` → cập nhật stats. Lookup bằng `card_hash` là O(1).

---

### `suppression_rules`
**Làm gì:** Whitelist — bypass fraud scoring cho merchant/customer/thẻ cụ thể đã được ANALYST xác nhận an toàn.

**Ví dụ thực tế:**  
Merchant A là đối tác lớn của ngân hàng, giao dịch luôn cao nhưng không phải fraud. ANALYST tạo suppression rule `rule_type=MERCHANT, entity_id=merchant-A-id` → tất cả giao dịch tại merchant A bỏ qua fraud scoring, tự động APPROVED.

**Các cột quan trọng:**
| Cột | Ý nghĩa |
|---|---|
| `rule_type` | MERCHANT / CUSTOMER / CARD_HASH — loại entity được bypass |
| `entity_id` | ID cụ thể của entity đó |
| `expires_at` | Thời gian hết hạn. NULL = không hết hạn |
| `is_active` | 1 = đang áp dụng, 0 = đã vô hiệu hoá |

**FK:** `created_by` → `users` — chỉ ANALYST được tạo rule, phải ghi lại ai tạo.

**Index:**
| Index | Lý do |
|---|---|
| `idx_suppression_active` | Mỗi giao dịch check `WHERE is_active = 1` — rất hot |
| `idx_suppression_type_eid` | Compound index: `(rule_type, entity_id)` — query exact match theo loại và ID |
| `idx_supp_expires` | Check `expires_at IS NULL OR expires_at > SYSDATE` — cần index để không full scan |

**CHECK:** `rule_type IN ('MERCHANT','CUSTOMER','CARD_HASH')`

---

---

## Nhóm 7 — Idempotency & State Machine (đã giải thích ở Nhóm 5)

---

## Nhóm 8 — Đối soát (Reconciliation)

---

### `reconciliation_runs`
**Làm gì:** Mỗi lần chạy đối soát tạo ra 1 "phiên đối soát" tại đây.

**Vấn đề cần giải quyết:**  
Giao dịch có thể bị stuck ở trạng thái PENDING mãi mãi do lỗi hệ thống (mạng đứt, DB timeout...). Cần job chạy định kỳ phát hiện những giao dịch này.

**Các cột quan trọng:**
| Cột | Ý nghĩa |
|---|---|
| `period_start`, `period_end` | Khoảng thời gian đối soát |
| `pending_timeout_minutes` | Ngưỡng: giao dịch PENDING quá X phút là bất thường (mặc định 120 phút) |
| `matched_count` | Số giao dịch bình thường |
| `discrepancy_count` | Số giao dịch bất thường (stuck PENDING) |
| `status` | RUNNING / COMPLETED / FAILED |

**FK:** `triggered_by` → `users` — ai kích hoạt đối soát (NULL nếu chạy tự động theo lịch)

**CHECK:** `status IN ('RUNNING','COMPLETED','FAILED')`

---

### `reconciliation_items`
**Làm gì:** Liệt kê từng giao dịch bất thường phát hiện trong một phiên đối soát.

**Các cột quan trọng:**
| Cột | Ý nghĩa |
|---|---|
| `run_id` | FK → `reconciliation_runs` — thuộc phiên đối soát nào |
| `txn_id` | FK → `transactions_live` — giao dịch nào bị bất thường |
| `item_type` | `PENDING_TIMEOUT` — loại bất thường |
| `minutes_pending` | Đã ở PENDING bao nhiêu phút |
| `status` | OPEN / RESOLVED — đã xử lý chưa |
| `resolved_by` | FK → `users` — ai đã xử lý |
| `resolution_note` | Ghi chú xử lý |

**FK:**
- `run_id` → `reconciliation_runs`
- `txn_id` → `transactions_live`
- `resolved_by` → `users`

**CHECK:** `status IN ('OPEN','RESOLVED')`

---

---

## Nhóm 9 — Data Engineering (ETL & Data Lake)

---

### `etl_logs`
**Làm gì:** Ghi lại lịch sử mỗi lần chạy ETL job (Extract giao dịch → Transform → Load vào Data Lake).

**Các cột quan trọng:**
| Cột | Ý nghĩa |
|---|---|
| `job_type` | Hiện tại: `DAILY_SUMMARY` — tổng hợp giao dịch theo ngày |
| `target_date` | Ngày dữ liệu đang được xử lý |
| `records_in` | Số dòng đọc từ `transactions_live` |
| `records_out` | Số snapshot ghi ra `datalake_snapshots` |
| `started_at` | DEFAULT SYSTIMESTAMP — tự điền khi INSERT |
| `status` | RUNNING / SUCCESS / FAILED |

**FK:** `triggered_by` → `users`

**Index:** `idx_etl_logs_date` trên `target_date` — ADMIN xem "ETL ngày X chạy thế nào?" — query phổ biến.

**CHECK:** `status IN ('RUNNING','SUCCESS','FAILED')`

---

### `datalake_snapshots`
**Làm gì:** Lưu dữ liệu tổng hợp sau khi ETL xử lý xong — đây là "Data Lake" của hệ thống.

**Hai loại snapshot:**
1. `DAILY_TXN_SUMMARY` — tạo tự động bởi ETL job hàng ngày, có `job_id`
2. `EXTERNAL_INGEST` — ingest thủ công từ nguồn ngoài (file Excel ngân hàng đối tác...), không có `job_id`

**Các cột quan trọng:**
| Cột | Ý nghĩa |
|---|---|
| `snapshot_type` | Loại snapshot (xem trên) |
| `snapshot_date` | Ngày dữ liệu trong snapshot |
| `job_id` | FK → `etl_logs` — snapshot này được tạo bởi ETL job nào. NULL nếu EXTERNAL_INGEST |
| `data_json` | CLOB — nội dung tổng hợp dạng JSON |
| `status` | ACTIVE / ARCHIVED |

**CHECK:** `status IN ('ACTIVE','ARCHIVED')`

---

### Bộ Dimension Tables (DWH)
`dim_time`, `dim_customer`, `dim_merchant`, `dim_channel`, `dim_location`

**Làm gì:** Các bảng chiều (Dimension) trong Star Schema của Data Warehouse.

**Tại sao cần Star Schema thay vì query thẳng OLTP?**

Query OLAP kiểu:  
> "Tháng trước, nhóm khách hàng HIGH RISK giao dịch qua kênh ONLINE tổng bao nhiêu tiền, tại thành phố nào?"

Nếu query thẳng `transactions_live` → phải JOIN 3-4 bảng OLTP → khoá dữ liệu production → làm chậm giao dịch thật.

Star Schema giải quyết: Copy dữ liệu ra DWH riêng, dùng khoá số nguyên (`_key`) thay vì UUID → JOIN nhanh hơn gấp nhiều lần.

**Dim tables lưu "phiên bản đóng băng" của dữ liệu** tại thời điểm ETL chạy — ngay cả khi sau này khách hàng đổi thành phố, dữ liệu DWH vẫn phản ánh đúng lúc giao dịch xảy ra.

---

### `fact_transactions`
**Làm gì:** Bảng sự kiện trung tâm của DWH — mỗi giao dịch được ETL xử lý có 1 dòng tại đây.

**Cấu trúc:** Chỉ lưu khoá (`_key`) trỏ đến dim tables + các số đo (amount, fraud_score, processing_time_ms).

**FK về dim tables:**
- `time_id` → `dim_time` — giao dịch thuộc ngày nào
- `customer_key` → `dim_customer` — khách hàng phân khúc nào
- `merchant_key` → `dim_merchant` — merchant loại gì
- `channel_key` → `dim_channel` — kênh giao dịch nào
- `location_key` → `dim_location` — IP từ đâu

**Tại sao không FK về OLTP trực tiếp?**  
DWH và OLTP chạy tách biệt — DWH có thể ở server khác. FK cross-server không thực tế.  
`txn_id` vẫn được lưu để có thể trace ngược về OLTP khi cần.

---

### `fact_loans`
**Làm gì:** Tương tự `fact_transactions` nhưng cho dữ liệu khoản vay.

**FK đặc biệt:** `loan_id` → `loans.loan_id` — trỏ về bảng OLTP loans (thay vì bảng cũ `loan_applications` đã bị xoá trong v1.3).

---

---

## Nhóm 10 — Kiểm toán (Audit)

---

### `audit_logs`
**Làm gì:** "Hộp đen" của toàn hệ thống — ghi lại mọi sự kiện quan trọng theo thứ tự thời gian tuyệt đối.

**Ví dụ sự kiện được ghi:**
- ANALYST thay đổi ngưỡng fraud từ 0.45 lên 0.50
- MANAGER acknowledge báo cáo R-001
- ADMIN khoá tài khoản user U-005
- REVIEWER duyệt case C-012

**Các cột quan trọng:**
| Cột | Ý nghĩa |
|---|---|
| `event_type` | Loại sự kiện: THRESHOLD_UPDATED / CASE_DECIDED / USER_LOCKED... |
| `entity_type` | Đối tượng bị tác động: TRANSACTION / CASE / USER / LOAN / MODEL_CONFIG |
| `entity_id` | ID cụ thể của đối tượng |
| `actor_user_id` | Ai thực hiện (FK → users) |
| `detail_json` | **CLOB** — chi tiết đầy đủ của sự kiện (giá trị trước và sau khi thay đổi) |

**Index:**
| Index | Lý do |
|---|---|
| `idx_audit_event_type` | Lọc tất cả sự kiện loại X: "Ai thay đổi ngưỡng trong tuần qua?" |
| `idx_audit_entity_id` | Trace toàn bộ lịch sử của 1 entity: "Giao dịch TXN-001 có gì xảy ra?" |
| `idx_audit_event_ts` | Query theo khoảng thời gian: "Hôm nay có bao nhiêu sự kiện?" |

**Tại sao `detail_json` phải là CLOB (không phải varchar)?**  
Audit payload có thể chứa toàn bộ JSON object trước và sau khi thay đổi. Với bảng có nhiều cột (loans, model_configs), JSON này dễ vượt 4000 ký tự → phải dùng CLOB.

**Quy tắc bất biến:** Bảng này **không bao giờ được phép UPDATE hay DELETE**. Chỉ INSERT. Bất kỳ sửa đổi nào trong audit log đều là vi phạm pháp lý.

---

---

## Nhóm 11 — ANALYST Module (v1.3)

---

### `loans`
**Làm gì:** Bảng OLTP lưu hồ sơ xin vay — OPERATOR nộp đơn, MANAGER phê duyệt.

**Thiết kế đặc biệt — features ML được lưu thẳng trong bảng:**
Thay vì bảng riêng `loan_feature_snapshots` (như thiết kế cũ), toàn bộ features của XGBoost model (`person_age`, `person_income`, `person_home_ownership`...) được lưu thẳng vào `loans`. Lý do: đơn giản hoá schema, 1 query là có đủ thông tin, không cần JOIN thêm bảng.

**Các cột quan trọng:**
| Cột | Ý nghĩa |
|---|---|
| `principal_amount` | Số tiền vay |
| `interest_rate` | Lãi suất năm dạng thập phân (0.1200 = 12%) |
| `pd_score` | Probability of Default — xác suất vỡ nợ 0.0–1.0 |
| `risk_level` | LOW RISK / MEDIUM RISK / HIGH RISK |
| `version` | Optimistic Locking |
| `monthly_payment` | Tự tính khi APPROVE: `P * r(1+r)^n / ((1+r)^n - 1)` |

**FK:**
- `customer_id` → `customers`
- `submitted_by` → `users` (OPERATOR)
- `reviewed_by` → `users` (MANAGER/ADMIN)

**CHECK constraints:**
- `principal_amount > 0`
- `interest_rate > 0 AND interest_rate < 100`
- `pd_score BETWEEN 0 AND 1`
- `status IN ('PENDING','APPROVED','REJECTED','DISBURSED','CLOSED','DEFAULTED')`

---

### `model_configs`
**Làm gì:** Lưu **ngưỡng phân loại** của model AI — ANALYST điều chỉnh qua API, không cần deploy lại code.

**Ví dụ các config thực tế:**

| model_name | param_name | param_value | Ý nghĩa |
|---|---|---|---|
| fraud | reject_threshold | 0.450000 | Điểm fraud ≥ 0.45 → REJECTED |
| fraud | review_threshold | 0.050000 | Điểm fraud ≥ 0.05 → MANUAL_REVIEW |
| loan | risk_high_threshold | 0.600000 | PD ≥ 0.60 → HIGH RISK |
| loan | risk_medium_threshold | 0.300000 | PD ≥ 0.30 → MEDIUM RISK |

**Tại sao không hardcode trong code?**  
Thực tế thị trường thay đổi: mùa dịch fraud tăng → cần hạ ngưỡng REJECT để chặt hơn. Nếu hardcode, phải deploy lại toàn bộ hệ thống mỗi lần điều chỉnh. Với bảng này, ANALYST chỉ cần gọi 1 API, thay đổi có hiệu lực ngay.

**UNIQUE constraint:** `(model_name, param_name)` — mỗi tham số chỉ có 1 giá trị hiện hành.

**`updated_at` DEFAULT SYSTIMESTAMP:** Tự điền khi INSERT, tránh lỗi ORA-01400 nếu code không truyền giá trị.

---

### `suppression_rules`
*(Đã giải thích chi tiết ở Nhóm 6 — Chống Gian lận nâng cao)*

---

### `analyst_reports`
**Làm gì:** Kênh giao tiếp chính thức từ ANALYST → MANAGER — báo cáo phân tích và đề xuất.

**Workflow:**
```
ANALYST tạo báo cáo (status=PENDING_REVIEW)
    ↓
MANAGER xem và acknowledge (status=ACKNOWLEDGED, ghi note)
    ↓
Có thể archive sau (status=ARCHIVED)
```

**Các cột quan trọng:**
| Cột | Ý nghĩa |
|---|---|
| `report_type` | FRAUD_ANALYSIS / LOAN_ANALYSIS / THRESHOLD_RECOMMENDATION / SUPPRESSION_REVIEW / GENERAL |
| `content_md` | **CLOB** — nội dung báo cáo định dạng Markdown (có thể render thành PDF) |
| `submitted_by` | FK → `users` (ANALYST) |
| `acknowledged_by` | FK → `users` (MANAGER) — NULL nếu chưa xem |
| `note` | MANAGER ghi chú khi acknowledge |

**CHECK:** `status IN ('PENDING_REVIEW','ACKNOWLEDGED','ARCHIVED')`

**Tại sao `content_md` là CLOB?**  
Báo cáo phân tích có thể dài hàng nghìn chữ, kèm bảng số liệu, biểu đồ ASCII — dễ vượt 4000 ký tự.

---

---

## Tổng kết — Sơ đồ quan hệ giữa các nhóm

```
[Core Banking]
    │ ETL
    ▼
customers ◄──────────────────────────────────────────────── transactions_live
merchants ◄──────────────────────────────────────────────────────│
channels  ◄──────────────────────────────────────────────────────│
                                                                  │
                                                    ┌─────────────┤
                                                    │             │
                                            risk_scoring   rule_hits
                                            _results
                                                    │
                                            review_cases ──► review_case_actions
                                                    │
                                            txn_idempotency
                                            txn_state ──────► txn_state_history
                                            card_velocity_stats
                                            suppression_rules

[ETL Pipeline]
transactions_live ──► etl_logs ──► datalake_snapshots
                              ──► dim_* ──► fact_transactions
                                           fact_loans

[ANALYST Module]
model_configs ◄── ANALYST ──► suppression_rules
                         ──► analyst_reports ──► MANAGER
loans ◄── OPERATOR ──► MANAGER (quyết định)

[Reconciliation]
transactions_live ──► reconciliation_runs ──► reconciliation_items

[Audit]
mọi sự kiện ──► audit_logs (chỉ INSERT, không bao giờ sửa/xoá)
```

---

## Checklist Enterprise — Trạng thái hiện tại

| Tiêu chí | Trạng thái |
|---|---|
| FK đầy đủ, đúng hướng | ✅ |
| Index trên mọi hot query path | ✅ |
| CHECK constraint trên mọi enum | ✅ |
| Optimistic Locking (version) | ✅ |
| Server DEFAULT trên timestamp columns | ✅ |
| CLOB thay vì varchar(4000) cho large text | ✅ |
| Không lưu sensitive data (số thẻ thật, mật khẩu) | ✅ |
| Audit log bất biến | ✅ |
| Idempotency chống trùng giao dịch | ✅ |
| Tách OLTP / DWH | ✅ |
