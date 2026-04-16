# Giải thích Schema Database – TMS

> Tài liệu giải thích mục đích từng bảng (trừ các bảng cơ bản như `users`, `roles`, `user_roles`).
> Với mỗi bảng: **làm gì, lưu gì, tại sao cần**.

---

## Nhóm 1 – Dữ liệu tham chiếu (Reference / Master Data)

---

### `customers`
**Làm gì:** Lưu hồ sơ khách hàng là chủ thẻ thực hiện giao dịch.

**Lưu gì:** Mã khách hàng, trạng thái định danh KYC (Know Your Customer), thu nhập, địa chỉ, CCCD.

**Tại sao cần:** Giúp phân tích rủi ro theo nhân khẩu học (khách hàng mới vs khách hàng quen, thu nhập thấp vs cao). Cần thiết để tra cứu khi Reviewer cần biết "người này là ai" khi duyệt case.

---

### `merchants`
**Làm gì:** Lưu danh sách các đơn vị chấp nhận thẻ (nhà hàng, siêu thị, website TMĐT...).

**Lưu gì:** Mã merchant, tên, danh mục ngành nghề, vị trí địa lý, mức rủi ro, cờ blacklist.

**Tại sao cần:** Merchant là một trong những yếu tố quan trọng nhất trong chấm điểm gian lận. Giao dịch tại merchant có `risk_level = HIGH` hoặc `is_blacklisted = 1` cần được nâng điểm fraud ngay lập tức. Không lưu bảng này thì model AI không có context merchant để phân tích.

---

### `channels`
**Làm gì:** Bảng tra cứu kênh giao dịch (ATM, POS, Online, Mobile App...).

**Lưu gì:** Mã kênh, tên kênh.

**Tại sao cần:** Kênh giao dịch ảnh hưởng trực tiếp đến ngưỡng rủi ro. Giao dịch online luôn rủi ro hơn giao dịch tại quầy có chip thẻ. Lưu riêng bảng lookup để tránh hardcode chuỗi lặp đi lặp lại trong `transactions_live`.

---

## Nhóm 2 – Lõi Xử lý Giao dịch (Transaction Core)

---

### `transactions_live`
**Làm gì:** Bảng trung tâm — lưu toàn bộ giao dịch đang tồn tại trong hệ thống nghiệp vụ (OLTP).

**Lưu gì:** Mọi thứ về một giao dịch: ai gửi (`submitted_by`), mua ở đâu (`merchant_id`), qua kênh nào (`channel_id`), bao nhiêu tiền, số thẻ đã che, kết quả gian lận (`fraud_score`), trạng thái hiện tại.

**Tại sao cần:** Đây là "sự thật hiện tại" (source of truth) cho toàn bộ vòng đời giao dịch. Mọi bảng khác đều FK về đây — case, audit, idempotency, state history đều phải tham chiếu về đúng giao dịch này.

---

### `risk_scoring_results`
**Làm gì:** Lưu lại kết quả chi tiết mỗi lần AI/Rule chấm điểm gian lận cho một giao dịch.

**Lưu gì:** Phiên bản model đã dùng (`model_version`), điểm số, quyết định đề xuất, JSON giải thích lý do chấm điểm (`reason_json`).

**Tại sao cần:** Khi một giao dịch sau này bị khiếu nại hoặc cần điều tra, cần biết "AI đã dùng model nào, điểm bao nhiêu, vì lý do gì". Không lưu bảng này thì sau khi giao dịch được duyệt/từ chối, bằng chứng phân tích rủi ro ban đầu sẽ biến mất hoàn toàn.

---

### `rule_hits`
**Làm gì:** Ghi lại từng rule nghiệp vụ nào đã được kích hoạt (hit) trong quá trình kiểm tra một giao dịch.

**Lưu gì:** Mã rule, tên rule, giá trị thực tế kích hoạt rule, mức độ nghiêm trọng.

**Tại sao cần:** Tách riêng khỏi `risk_scoring_results` vì một giao dịch có thể trigger nhiều rule cùng lúc (VD: vừa là merchant blacklist, vừa là giao dịch đêm khuya, vừa vượt ngưỡng số tiền). Cần lưu từng rule riêng để phân tích rule nào có hiệu quả nhất hay bị false positive nhiều nhất.

---

## Nhóm 3 – Quản lý Case & Quyết định (Case Management)

---

### `review_cases`
**Làm gì:** Mỗi giao dịch bị phân vào `MANUAL_REVIEW` sẽ tạo ra một bản ghi tại đây — đây là "hồ sơ cần xét duyệt".

**Lưu gì:** Trạng thái case (OPEN → ASSIGNED → APPROVED/REJECTED), ai đang xử lý (`assigned_to`), quyết định cuối cùng, ghi chú, `version` cho Optimistic Locking.

**Tại sao cần:** Tách case ra khỏi giao dịch giúp theo dõi riêng quy trình xét duyệt thủ công mà không ảnh hưởng đến bảng giao dịch gốc. Reviewer làm việc trên case, không được động thẳng vào `transactions_live`.

---

### `review_case_actions`
**Làm gì:** Ghi lại từng hành động cụ thể xảy ra trên một case theo thứ tự thời gian.

**Lưu gì:** Loại hành động (ASSIGN / COMMENT / APPROVE / REJECT), ai thực hiện, lúc nào, ghi chú kèm theo.

**Tại sao cần:** `review_cases` chỉ lưu trạng thái *hiện tại*. Bảng này lưu *lịch sử đầy đủ*: case này được ai nhận lúc 9h, ai comment lúc 10h, ai duyệt lúc 11h. Quan trọng cho compliance — phải chứng minh đúng người đúng việc.

---

## Nhóm 4 – Idempotency & State Machine

---

### `txn_idempotency`
**Làm gì:** Bộ nhớ chống xử lý giao dịch trùng lặp.

**Lưu gì:** `idempotency_key` (hash từ các trường tĩnh của giao dịch), snapshot JSON kết quả lần đầu xử lý, trạng thái xử lý (IN_PROGRESS / SUCCESS / FAILED).

**Tại sao cần:** Nếu client bị timeout và retry, giao dịch sẽ được gửi lại. Không có bảng này, hệ thống xử lý lại lần 2 → có thể trừ tiền 2 lần. Khi có bảng này, lần retry chỉ cần lookup key → trả lại kết quả cũ, không xử lý gì thêm.

---

### `txn_state`
**Làm gì:** Lưu trạng thái *hiện tại* của giao dịch, tách riêng khỏi `transactions_live` để phục vụ cơ chế Optimistic Locking.

**Lưu gì:** Status hiện tại, `version` (số nguyên tăng dần mỗi lần đổi status), số lần retry, mã lỗi gần nhất.

**Tại sao cần:** Khi 2 Reviewer cùng duyệt 1 giao dịch lúc 14:00:00, ai gửi request trước với `version=1` sẽ thành công và hệ thống tăng lên `version=2`. Người thứ 2 gửi `version=1` → server phát hiện không khớp → trả về lỗi 409 CONFLICT, tránh ghi đè bừa.

---

### `txn_state_history`
**Làm gì:** Timeline lịch sử mọi lần thay đổi trạng thái của một giao dịch.

**Lưu gì:** Trạng thái cũ, trạng thái mới, ai thay đổi, lúc nào, lý do.

**Tại sao cần:** `txn_state` chỉ có trạng thái hiện tại. Bảng này là cuốn lịch sử đầy đủ: "PENDING → MANUAL_REVIEW (do fraud score 0.55) → APPROVED (do Reviewer Nguyễn A duyệt lúc 14:30)". Dùng cho API `GET /transactions/{id}/states` và điều tra forensic.

---

## Nhóm 5 – Data Engineering (ETL & Warehouse)

---

### `raw_ingest_batches`
**Làm gì:** Theo dõi từng lô file CSV được đọc vào từ Data Lake (bước Extract).

**Lưu gì:** Đường dẫn file, ngày file, số bản ghi, trạng thái ingest (PENDING / SUCCESS / FAILED), thông báo lỗi.

**Tại sao cần:** Khi ETL pipeline bị lỗi giữa chừng, cần biết đã đọc được file nào rồi, file nào chưa, file nào đọc lỗi để retry đúng chỗ thay vì chạy lại toàn bộ.

---

### `etl_job_logs`
**Làm gì:** Theo dõi toàn bộ vòng đời của một lần chạy ETL Pipeline (Extract → Transform → Load).

**Lưu gì:** Ai kích hoạt, chạy chế độ gì (FULL / INCREMENTAL), ngày xử lý, số bản ghi qua từng bước, trạng thái, lý do lỗi.

**Tại sao cần:** Khác với `raw_ingest_batches` (chỉ theo dõi file đầu vào), bảng này cho biết cả quá trình Transform và Load có thành công không. ADMIN dùng API `GET /etl/logs/{job_id}` để poll tiến trình ngay sau khi bấm chạy pipeline.

---

### `dim_time` / `dim_customer` / `dim_merchant` / `dim_channel` / `dim_location`
**Làm gì:** Các bảng chiều (Dimension Tables) trong Star Schema của Data Warehouse.

**Lưu gì:** Phiên bản "đóng băng" thông tin tại thời điểm xảy ra giao dịch (không bị cập nhật sau).

**Tại sao cần:** Trong OLAP, câu hỏi thường là "Tháng trước, nhóm khách hàng rủi ro cao giao dịch ở kênh nào nhiều nhất?" — cần join nhanh qua khóa số nguyên (`_key`). Tách dim ra khỏi fact giúp query analytics chạy nhanh gấp nhiều lần so với join thẳng vào OLTP.

---

### `fact_transactions`
**Làm gì:** Bảng sự kiện trung tâm (Fact Table) của Data Warehouse, lưu các giao dịch đã được ETL xử lý.

**Lưu gì:** Khóa tham chiếu đến tất cả dim tables, số tiền, trạng thái cuối, nhãn gian lận, điểm fraud, thời gian xử lý (ms).

**Tại sao cần:** Đây là nguồn dữ liệu cho Dashboard và báo cáo OLAP. Queries của Manager như "Tổng giao dịch fraud tuần này theo kênh" chạy trên bảng này thay vì quét thẳng `transactions_live` (tránh làm chậm hệ thống giao dịch thật).

---

### `fact_loans`
**Làm gì:** Tương tự `fact_transactions` nhưng dành cho dữ liệu khoản vay trong Warehouse.

---

## Nhóm 6 – Đối soát (Reconciliation)

---

### `reconciliation_jobs`
**Làm gì:** Mỗi lần chạy đối soát (cuối ngày hoặc thủ công) tạo ra một bản ghi ở đây.

**Lưu gì:** Ngày nghiệp vụ, số lượng và tổng tiền kỳ vọng vs thực tế từ 3 nguồn, trạng thái kết quả (MATCHED / MISMATCH / FAILED), thông báo lỗi kỹ thuật (nếu có).

**Tại sao cần:** Bộ phận kế toán cần bằng chứng hàng ngày rằng "Số tiền trong DB nghiệp vụ = Số tiền trong kho dữ liệu = Số tiền trong file log". Nếu lệch 1 đồng cũng phải có hồ sơ để điều tra.

---

### `reconciliation_items`
**Làm gì:** Liệt kê từng điểm lệch cụ thể khi job có status = MISMATCH.

**Lưu gì:** Khóa tham chiếu bị lệch (`ref_key`), loại vấn đề (`issue_type`), giá trị kỳ vọng vs giá trị thực tế.

**Tại sao cần:** `reconciliation_jobs` chỉ cho biết "có lệch". Bảng này trả lời "lệch ở đâu, bao nhiêu, giao dịch nào" — dữ liệu cần thiết để kỹ thuật viên sửa lỗi và kế toán làm bút toán điều chỉnh.

---

## Nhóm 7 – Cho vay (Loan Simulator)

---

### `loan_applications`
**Làm gì:** Bảng chính lưu các hồ sơ xin vay vốn được OPERATOR nộp vào.

**Lưu gì:** Ai vay, vay bao nhiêu, trạng thái xét duyệt. Thêm cache `pd_score` và `risk_level` để tránh join sang bảng scoring mỗi lần tra cứu.

---

### `loan_feature_snapshots`
**Làm gì:** Chụp lại toàn bộ đặc trưng dữ liệu (features) của người xin vay tại thời điểm nộp đơn.

**Lưu gì:** Thu nhập năm, số năm đi làm, tỷ lệ nợ/thu nhập, điểm tín dụng, số lần vỡ nợ trước đây, thời hạn vay.

**Tại sao cần:** Model AI cần input cụ thể để tính PD Score. Lưu snapshot này đảm bảo có thể tái tạo lại đúng kết quả AI nếu cần kiểm toán sau này. Nếu không lưu, không ai biết "Lúc đó AI tính dựa trên thu nhập bao nhiêu?"

---

### `loan_risk_scores`
**Làm gì:** Lưu kết quả chi tiết mỗi lần model AI chấm điểm PD (Probability of Default) cho một đơn vay.

**Lưu gì:** Điểm PD, phiên bản model, lý do chấm điểm dạng JSON.

**Tại sao cần:** Tương tự `risk_scoring_results` của giao dịch — cần bằng chứng minh bạch cho quyết định tín dụng. Các ngân hàng chịu sự kiểm tra của cơ quan giám sát tài chính, phải chứng minh được "tại sao từ chối đơn vay này".

---

## Nhóm 8 – Kiểm toán (Audit)

---

### `audit_logs`
**Làm gì:** Ghi lại mọi sự kiện quan trọng xảy ra trong hệ thống theo thứ tự thời gian tuyệt đối.

**Lưu gì:** Loại sự kiện, đối tượng bị tác động (TRANSACTION / CASE / USER / LOAN), ai thực hiện, lúc nào, chi tiết dạng JSON.

**Tại sao cần:** Đây là "hộp đen" của hệ thống. Khi xảy ra tranh chấp ("Reviewer A duyệt nhầm giao dịch của tôi"), audit log là bằng chứng pháp lý duy nhất. Với các tổ chức tài chính, đây còn là yêu cầu bắt buộc từ cơ quan quản lý nhà nước (MAS, NHNN...). Bảng này **không bao giờ được phép xóa hay sửa**.
