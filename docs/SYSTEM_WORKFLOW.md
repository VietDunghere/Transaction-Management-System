# Luồng Hoạt động Hệ thống (System Workflow)

Tài liệu này mô tả chi tiết các luồng nghiệp vụ cốt lõi bên trong **Transaction Management System (TMS)**.

---

## CHANGELOG – Thay đổi so với phiên bản cũ

| # | Section | Cũ | Mới |
|---|---|---|---|
| 1 | Luồng 1 – Fraud thresholds | `≤ 0.3 → APPROVED`, `> 0.7 → REJECTED` | `< 0.35 → APPROVED`, `≥ 0.65 → REJECTED` |
| 2 | Luồng 1 – MANUAL_REVIEW label | `PENDING (Mở Case MANUAL_REVIEW)` | `MANUAL_REVIEW (Mở Case)` |
| 3 | Luồng 5 – Endpoint loan | `POST /loans/submit` | `POST /loans` |
| 4 | Luồng 5 – Loan flow | Chỉ là Simulator, trả kết quả ngay | PENDING → MANAGER review → APPROVED/REJECTED |
| 5 | Luồng 5 – pd_score timing | Tính khi model chạy (demo only) | Tính ngay khi nộp đơn (tại apply), không cần chờ APPROVE |
| 6 | Toàn bộ | Thiếu SSE Stream | Thêm Luồng 6 – SSE Real-time Demo |
| 7 | Luồng 2 – Case decide | Không kiểm tra case status | Case phải ASSIGNED trước khi quyết định (OPEN → 409) |
| 8 | Luồng 2 – Case decide | ADMIN bị chặn như REVIEWER | ADMIN bypass ownership check giống MANAGER |
| 9 | Luồng 5 – Loan decide | Không có SoD check | Người tạo đơn không được tự phê duyệt → 403 |
| 10 | Luồng 2 – REVIEWER queue | REVIEWER không thấy OPEN cases | REVIEWER thấy OPEN queue + cases của mình |
| 11 | Luồng 1/7 – State history | OPERATOR xem state-history của mọi giao dịch | Chỉ xem giao dịch do mình submit |

---

## 1. Luồng Nhận & Xử lý Giao dịch (Transaction Processing)

Đây là luồng chính phục vụ với tần suất cao (High Throughput).

```text
[ OPERATOR ] 
     |
     v (1. Submit Giao Dịch)
[ API Endpoint /transactions/submit ]
     |
     v (2. Kiểm tra Idempotency Key)
{ Key đã tồn tại? } -----> [ CÓ ] -----> (Trả response cũ – chống lặp)
     |
     v [ KHÔNG ]
[ Mask & Hash số thẻ ]
     |
     v
[ Gọi Model Random Forest (10 cây) ]
     |
     v (3. Phân luồng theo Fraud Score)
     |
   +-+-------------------+-------------------+
   |                     |                   |
(score < 0.35)    (0.35 ≤ s < 0.65)     (score ≥ 0.65)
   |               Hoặc amount > 500M        |
   v                     v                   v
[ APPROVED ]      [ MANUAL_REVIEW ]      [ REJECTED ]
                  (Mở Case, chờ Reviewer)
   |                     |                   |
   +---------------------+-------------------+
                         |
                         v
            [ DB: TRANSACTIONS_LIVE ]
                         |
                         v
              ( Ghi Audit Log tự động )
```

> **Lưu ý thay đổi ngưỡng:** *(~~Cũ: ≤ 0.3 → APPROVED, > 0.7 → REJECTED~~)*
> Model Random Forest có 10 cây, cho ra score ∈ `{0.3, 0.4, 0.5, 0.6, 0.7}`.
> Ngưỡng được calibrate theo dải thực tế: ~30% APPROVED / ~40% MANUAL_REVIEW / ~30% REJECTED.

---

## 2. Luồng Xử lý Giao dịch Bị cảnh báo (Manual Case Management)

Dành cho đối tượng `REVIEWER`. Bảo vệ tính nguyên vẹn dữ liệu bằng DB Locking khi nhận việc và Optimistic Locking khi ra quyết định.

```text
[ REVIEWER ]                                  [ SERVER / DB ]
      |                                              |
      |--- 1. GET /cases ---------------------------->|
      |       (thấy OPEN + cases của mình)            |-- Compound: (assigned_to IS NULL)
      |<-- Queue: OPEN cases + assigned to me --------|    OR (assigned_to = reviewer_id)
      |                                              |
      |--- 2. POST /cases/{id}/assign -------------->|
      |       (chọn 1 case OPEN)                     |-- (UPDATE WHERE assigned_to IS NULL)
      |<-- Case status = ASSIGNED ------------------|
      |                                              |
      |--- 3. GET /cases/{id} (chi tiết) ----------->|
      |       (chỉ xem case của mình)                |-- Check: assigned_to == reviewer_id
      |<-- Chi tiết case + transaction info ----------|
      |                                              |
      |--- 4. PATCH /cases/{id}/decision ----------->|
      |       { decision, note, version }            |-- Check: case status == ASSIGNED (!)
      |                                              |-- Check version (Optimistic Lock)
      |                                              |-- Update case status
      |                                              |-- Update transaction status
      |                                              |-- Ghi AUDIT_LOGS
      |<-- { case_id, status, txn_status } ----------|
```

> **Ràng buộc mới:**
> - Case phải ở **ASSIGNED** trước khi quyết định — không thể quyết định case OPEN trực tiếp. *(~~Cũ: có thể~~)*
> - REVIEWER chỉ xem chi tiết case của mình. List cho thấy OPEN queue + case của mình.
> - MANAGER/ADMIN có thể quyết định bất kỳ case ASSIGNED nào (override/giám sát). *(~~Cũ: ADMIN bị chặn~~)*

---

## 3. Luồng Quản trị Dữ liệu (ETL Pipeline)

Tiến trình chạy ngầm lấy dữ liệu từ file log thô sang Kho dữ liệu Thống kê.

```text
[ Data Lake ]
   (Raw CSV/JSON Logs chứa IP, payload)
          |
          |  <-- (Job chạy theo lịch hoặc ADMIN trigger qua POST /etl/run)
          |
[ ETL Pipeline ]
   |-- 1. Extract:    Đọc file thô theo target_date
   |-- 2. Transform:  Loại bỏ rác, map GeoIP, dựng Star Schema
   |-- 3. Load:       Chèn số liệu tóm tắt vào Warehouse
          |
          v
[ Data Warehouse ]
   (FACT_TRANSACTIONS – Phục vụ OLAP)
          |
          v
   [ Ghi Log kết quả vào ETL_JOB_LOGS ]
```

> **Lưu ý:** Idempotency guard – mỗi `(target_date, job_type)` chỉ được chạy thành công 1 lần.
> Nếu đã SUCCESS → trả 409 Conflict.

---

## 4. Luồng Đối soát So khớp (Reconciliation)

So sánh 3 nguồn dữ liệu để phát hiện thất thoát.

```text
       [ ADMIN hoặc Cronjob ]
                |
                v (POST /reconciliation/run)
                |
        ( Thu thập dữ liệu )
   +------------+------------+
   |            |            |
   v            v            v
[ OLTP ]    [Data Lake] [Warehouse]
(SQLite/    (Raw Files)   (OLAP)
 Oracle)
   |            |            |
   v            v            v
 { COUNT(*) & SUM(amount) có khớp nhau? }
                |
    +-----------+-----------+
    |           |           |
[ MATCH ]   [ MISMATCH ] [ FAILED ]
  (Khớp 100%) (Có lệch)  (DB Lỗi/Timeout)
```

---

## 5. Luồng Quản lý Đơn Vay (Loan Management)

*(~~Cũ: "Trình giả lập Quyết định Vay vốn (Loan Simulator)"~~ — đã mở rộng thành quy trình phê duyệt đầy đủ)*

```text
[ OPERATOR / MANAGER / ADMIN ]
     |
     v
[ POST /loans ] (Nộp hồ sơ tín dụng)
     |
     v (Kiểm tra customer_id hợp lệ)
[ AI Loan Model – XGBoost ]          <- Tính ngay khi nộp (không cần chờ)
     |
     v (PD Score 0.0–1.0)
{ Phân loại Risk Level }
     |
  +--+--+----+
  |     |    |
[LOW] [MED] [HIGH]       pd < 0.20 / 0.20–0.50 / ≥ 0.50
  |     |    |           (~~Cũ: < 0.3 / 0.3–0.6 / > 0.6~~)
  +--+--+----+
     |
     v
[ Lưu LOAN_APPLICATIONS — Status: PENDING ]
     |
     v
[ Ghi Audit Log: LOAN_APPLIED ]
     |
     v
[ MANAGER / ADMIN xem đơn PENDING ]
     |
     v (PATCH /loans/{loan_id}/decision)
     |   { decision: APPROVE|REJECT, review_note, version }
     |-- SoD Check: submitted_by != actor_user_id → 403 nếu vi phạm (Mới)
     |
     +--------+--------+
     |                 |
[ APPROVE ]        [ REJECT ]
     |                 |
[ Tính monthly_payment ] [ Status = REJECTED ]
[ outstanding_balance   ]
[ maturity_date         ]
[ disbursed_at          ]
[ Status = APPROVED     ]
     |                 |
     +--------+--------+
              |
     [ Ghi Audit Log: LOAN_APPROVED / LOAN_REJECTED ]
```

> **Mô phỏng (không lưu DB):** `POST /loans/simulate` — trả về pd\_score và risk\_level ngay,
> dùng để kiểm tra trước khi nộp đơn chính thức.

---

## 6. Luồng Real-time Demo Feed (SSE Stream) *(Mới)*

Dành cho màn hình demo: Faker gửi liên tục, SSE đẩy kết quả về frontend theo thời gian thực.

```text
[ FAKER / Demo Script ]        [ BACKEND ]           [ FRONTEND ]
         |                          |                      |
         |-- POST /transactions/submit ->|                  |
         |-- POST /transactions/submit ->|                  |
         |-- POST /loans          --->|                  |
         |                          |                      |
         |              [ DB: TRANSACTIONS_LIVE ]          |
         |                          |                      |
         |                          |<-- GET /stream/transactions (SSE)
         |                          |    (interval=2s, Bearer Token)
         |                          |                      |
         |                [ Poll DB mỗi 2s ]               |
         |                  created_at >= last_checked      |
         |                          |                      |
         |                          |-- data: {txn_id, status, fraud_score, ...} ->|
         |                          |-- data: {txn_id, ...} ----------------------->|
         |                          |-- : ping (nếu không có giao dịch mới) ------->|
         |                          |                      |
         |              [ GET /stream/dashboard (SSE) ]    |
         |                          |<--------------------- |
         |                [ Poll DashboardService mỗi 5s ] |
         |                          |-- data: {total, fraud_rate, ...} ------------>|
```

> **Tại sao dùng SSE thay vì WebSocket:**
> Demo chỉ cần server → client (1 chiều). SSE đơn giản hơn, không cần handshake nâng cấp.
> WebSocket cần khi client cũng gửi dữ liệu ngược lại qua cùng kết nối.
>
> **Lưu ý `created_at` vs `txn_time`:**
> Demo tạo `txn_time` ngẫu nhiên trong 24h qua → filter bằng `created_at >= last_checked`
> mới đảm bảo bắt tất cả giao dịch mới insert, bất kể thời gian giao dịch.
