# Phân tích & Đánh giá API Design — Transaction Management System

> Bản audit đầy đủ đối chiếu API Design với Use Case. Mỗi vấn đề có: **vấn đề gì → tại sao sai → fix thế nào**.

---

## 🔴 Critical — Phải fix trước khi code

---

### 1. OPERATOR xem được giao dịch của người khác

**Vấn đề:** `GET /transactions` trả về **toàn bộ** giao dịch trong hệ thống. OPERATOR A có thể đọc giao dịch của OPERATOR B.

**Tại sao sai:** USECASE viết rõ OPERATOR chỉ *"xem danh sách giao dịch đã gửi"* — tức là của chính họ.

**Fix:** Tầng service tự động thêm filter `submitted_by = current_user_id` khi role = OPERATOR. Client không được tự truyền param này.

---

### 2. Optimistic Locking không hoạt động

**Vấn đề:** USECASE có UC-STATE-03 nói về Optimistic Locking để tránh race condition. Nhưng request body của `PATCH /transactions/{txn_id}/status` **không có field `version`**:

```json
// Hiện tại — THIẾU version
{ "status": "APPROVED", "note": "Xác nhận hợp lệ" }

// Đúng phải là
{ "status": "APPROVED", "note": "Xác nhận hợp lệ", "version": 2 }
```

**Tại sao sai:** Nếu không có `version`, hai Reviewer cùng duyệt một giao dịch lúc 14:00:00 — cả hai gọi API thành công, bản ghi cuối cùng là của ai ghi sau. Không phát hiện được conflict.

**Fix:** Request phải gửi `version` hiện tại. Server so sánh với DB — nếu lệch → trả `409 CONFLICT`.

---

### 3. Endpoint thừa phá vỡ audit trail

**Vấn đề:** Tồn tại song song hai cách duyệt giao dịch:
- `PATCH /transactions/{txn_id}/status` — Reviewer update thẳng
- `POST /cases/{case_id}/approve` — đi qua case flow

**Tại sao sai:** USECASE quy định rõ luồng phải là: **nhận case → xem xét → quyết định**. Nếu Reviewer gọi thẳng endpoint đầu tiên, toàn bộ bước "ai nhận case, lúc nào, case nào" bị bỏ qua — audit trail mất dấu.

**Fix:** Xóa `PATCH /transactions/{txn_id}/status`. Chỉ dùng `POST /cases/{case_id}/approve` và `POST /cases/{case_id}/reject`.

---

### 4. State machine không có giới hạn cuối

**Vấn đề:** Không có tài liệu nào định nghĩa transition nào hợp lệ. Theo thiết kế hiện tại, Reviewer có thể gọi API để chuyển `APPROVED → REJECTED` hoặc `REJECTED → APPROVED` vì server không chặn.

**Tại sao sai:** `APPROVED` và `REJECTED` là **trạng thái kết thúc** — không thể đảo ngược. Cho phép điều này là lỗ hổng nghiệp vụ nghiêm trọng.

**Bảng transition hợp lệ — cần document và enforce:**

| Từ trạng thái | Được phép chuyển sang |
|---|---|
| `PENDING` | `APPROVED`, `REJECTED`, `MANUAL_REVIEW` |
| `MANUAL_REVIEW` | `APPROVED`, `REJECTED` |
| `APPROVED` | ❌ Không đi đâu được |
| `REJECTED` | ❌ Không đi đâu được |

**Fix:** Service layer kiểm tra: nếu status hiện tại là terminal → trả `409 INVALID_STATE_TRANSITION`.

---

### 5. Admin có thể tự vô hiệu hóa mình

**Vấn đề:** `PATCH /users/{user_id}/disable` không có guard nào ngăn Admin gọi với `user_id` của chính mình.

**Tại sao sai:** Nếu Admin duy nhất tự disable → hệ thống không còn ai có quyền admin, không có recovery path.

**Fix:** Service kiểm tra `user_id != current_user_id` → nếu trùng trả `403 SELF_DISABLE_FORBIDDEN`.

---

## 🟡 High — Ảnh hưởng đến tính đúng đắn của hệ thống

---

### 6. Idempotency key hash những field nào?

**Vấn đề:** USECASE viết *"SHA256(payload)"* nhưng payload gồm cả `txn_time` (timestamp). Nếu client gửi lại giao dịch lỗi 30 giây sau → `txn_time` khác → hash khác → **idempotency key khác** → hệ thống xử lý lại như giao dịch mới.

**Fix:** Phải document rõ chỉ hash các field định danh nghiệp vụ, ví dụ: `card_number + amount + merchant_id`. Bỏ `txn_time`, `metadata` khỏi hash input.

---

### 7. Ai làm masking `card_number`?

**Vấn đề:** API doc ghi request nhận `"card_number": "string (masked, e.g. 4111********1111)"` — tức là client tự mask trước khi gửi.

**Tại sao sai:** Nếu client tự mask, server nhận chuỗi `4111********1111` — không có cách validate đây có phải số thẻ hợp lệ không. Ai gửi `xxxx` hay `abcd` cũng lọt qua.

**Fix:** Client gửi số thẻ thật (qua HTTPS). Server validate, sau đó **tự mask** trước khi lưu DB và trả response. Document rõ điều này.

---

### 8. `PUT /auth/change-password` sai HTTP method

**Vấn đề:** Dùng `PUT` để đổi mật khẩu.

**Tại sao sai:** `PUT` có nghĩa là *thay thế toàn bộ resource*. Đổi mật khẩu chỉ cập nhật một phần → phải dùng `PATCH`.

**Fix:** `PATCH /auth/change-password`.

---

### 9. `POST /cases/{case_id}/approve|reject` sai HTTP method

**Vấn đề:** Dùng `POST` để thay đổi trạng thái một resource đang tồn tại.

**Tại sao sai:** `POST` dùng để *tạo resource mới*. Approve/reject là cập nhật → dùng `PATCH`.

**Fix:** Gộp thành một endpoint: `PATCH /cases/{case_id}/decision` với body `{ "decision": "APPROVED|REJECTED", "note": "..." }`. Gọn hơn, đúng semantic hơn.

---

### 10. Race condition khi assign case

**Vấn đề:** `POST /cases/{case_id}/assign` không có locking — hai Reviewer cùng assign một case lúc 10:00:00 → cả hai thành công → case có hai `assigned_to`.

**Fix:** Dùng `UPDATE ... WHERE assigned_to IS NULL` — nếu không update được row nào → trả `409 CASE_ALREADY_ASSIGNED`.

---

### 11. Thiếu `FAILED` status trong Reconciliation

**Vấn đề:** `GET /reconciliation/jobs` chỉ có status `MATCH | MISMATCH | RUNNING`. Nếu job crash giữa chừng (DB timeout, hết memory) → không có status đại diện.

**Fix:** Thêm `FAILED` + field `error_message` vào response.

---

### 12. `GET /dashboard/fraud-chart` có conflict params

**Vấn đề:** Endpoint nhận cả `period=weekly` (relative) lẫn `from_date/to_date` (absolute). Nếu client truyền cả hai, không biết cái nào được dùng.

**Fix:** Dùng `from_date/to_date` làm primary. `period` chỉ là shortcut (`period=this_week` = server tự tính `from_date/to_date`). Document rõ thứ tự ưu tiên: nếu có `from_date/to_date` thì bỏ qua `period`.

---

## 🟢 Medium — Không sai nhưng cần bổ sung

---

### 13. Thiếu `GET /auth/me`

OPERATOR và REVIEWER không có endpoint nào để xem thông tin của chính mình — `GET /users` chỉ MANAGER+ mới dùng được. Nếu muốn biết mình đang đăng nhập với role gì, họ phải decode JWT client-side.

**Fix:** Thêm `GET /auth/me` → trả `user_id, username, role, is_active`. Mọi role đều dùng được.

---

### 14. Không có `PATCH /users/{user_id}/enable`

Có disable nhưng không có re-enable. Nếu Admin disable nhầm → bế tắc hoàn toàn.

---

### 15. Thiếu `GET /etl/logs/{job_id}`

`POST /etl/trigger` trả `job_id` nhưng không có endpoint để poll trạng thái job đó. Client phải lọc trong `GET /etl/logs` (list tất cả) để tìm — không thực tế.

---

### 16. `GET /dashboard/summary` — trend granularity mơ hồ

Response trả `"date": "2026-04-01"` trong trend array. Nhưng nếu `period=today` → trend theo giờ thì format ngày không hợp lệ.

**Fix:** Document rõ: `period=today` → granularity hourly, `period=this_week` → daily, `period=this_month` → daily. Thêm field `granularity` vào response.

---

### 17. `GET /datalake/structure` không có pagination

Sau 1 năm = 365 thư mục, sau 3 năm = 1000+. Response trả all-at-once không scale.

---

### 18. Thiếu `GET /health`

Cần cho Docker health check, Kubernetes readiness probe, load balancer. Thiếu là thiếu chuẩn production cơ bản.

```json
// GET /health → 200
{ "status": "ok", "version": "1.0.0", "timestamp": "ISO8601" }
```

---

### 19. Thiếu các endpoint CRUD còn thiếu

| Thiếu | Cần cho |
|---|---|
| `GET /users/{user_id}` | Xem chi tiết 1 user |
| `GET /loans` | List loan applications |
| `GET /loans/{loan_id}` | Chi tiết loan |

---

### 20. Naming không nhất quán

| Field hiện tại | Vấn đề | Đề xuất |
|---|---|---|
| `idem_key` | Viết tắt, không rõ nghĩa | `idempotency_key` |
| `reason_code: "HIGH_VALUE"` | HIGH_VALUE là trigger condition, không phải risk reason | Tách thành field riêng `override_reason: "HIGH_VALUE"` |
| `/transaction` (số ít) | REST convention dùng số nhiều | `/transactions` |
| `processed_at` / `created_at` / `reviewed_at` | Timestamp đặt tên khác nhau mỗi resource | Thống nhất: `created_at`, `updated_at` |
| Base URL `api/` | Không có version, breaking change sẽ ảnh hưởng toàn bộ client | `api/v1/` |

---

## Tổng kết

| Mức độ | Số vấn đề | Hành động |
|---|---|---|
| 🔴 Critical | 5 | Fix trước khi bắt đầu code |
| 🟡 High | 7 | Fix trong sprint đầu |
| 🟢 Medium | 8 | Fix trước khi deploy |
