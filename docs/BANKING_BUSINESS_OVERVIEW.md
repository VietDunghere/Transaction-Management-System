# Báo cáo Nghiệp vụ Ngân hàng – Dành cho người mới bắt đầu

> Đọc tài liệu này trước khi đọc bất kỳ tài liệu thiết kế nào khác.

---

## 1. Bức tranh tổng thể — Tiền đi từ đâu đến đâu?

Khi bạn quẹt thẻ mua cà phê 50.000đ, có một chuỗi sự kiện xảy ra trong vòng chưa đến 2 giây:

```
Bạn (Chủ thẻ)
   |--- quẹt thẻ --->  Máy POS (của quán)
                           |
                           v
                     Ngân hàng của Quán (Acquiring Bank)
                           |
                           v
                   Tổ chức thẻ quốc tế (Visa / Mastercard)
                           |
                           v
                     Ngân hàng của Bạn (Issuing Bank)
                           |
                     [Hệ thống xử lý giao dịch]
                           |
                 Duyệt ✅  hoặc  Từ chối ❌
```

**Hệ thống TMS nằm ở bước cuối cùng:** Phần xử lý bên trong Ngân hàng của Bạn (Issuing Bank) — nơi quyết định có cho phép giao dịch này hay không.

---

## 2. Tại sao ngân hàng cần "xem xét" giao dịch?

Có 3 lý do chính:

### A. Phòng chống gian lận (Fraud Prevention)

Kẻ gian có thể đánh cắp thông tin thẻ và dùng nó để mua hàng online. Ngân hàng cần phát hiện trước khi tiền bị mất.

Một số dấu hiệu đáng ngờ mà hệ thống nhận diện:
- Giao dịch lúc 3 giờ sáng với số tiền lớn bất thường
- Mua hàng tại quốc gia mà chủ thẻ chưa từng đến
- 5 giao dịch nhỏ liên tiếp trong 2 phút (thử thẻ)
- Merchant có lịch sử gian lận cao

### B. Kiểm soát rủi ro tín dụng (Credit Risk)

Với các khoản vay, ngân hàng cần đánh giá khả năng người vay có trả được nợ không dựa trên:
- Thu nhập, lịch sử trả nợ, tỷ lệ nợ hiện tại
- Điểm tín dụng (Credit Score)

### C. Tuân thủ quy định (Compliance)

Ngân hàng bị kiểm tra bởi Ngân hàng Nhà nước. Họ yêu cầu:
- Phải lưu lại toàn bộ lịch sử ai đã duyệt gì, lúc nào (→ Audit Log)
- Phải đảm bảo dữ liệu khớp nhau giữa các hệ thống (→ Reconciliation)
- Phải báo cáo định kỳ về tỷ lệ gian lận, số giao dịch đáng ngờ (→ Reports)

---

## 3. Hệ thống TMS giải quyết vấn đề gì?

TMS là lớp phần mềm trung gian đứng giữa request giao dịch đến và quyết định cuối cùng.

**Không có TMS:** Mọi giao dịch cần nhân viên ngồi xem xét bằng tay → Chậm, tốn người, dễ bỏ sót.

**Có TMS:** Hệ thống tự động phân loại:

```
                      Giao dịch đến
                           |
                     AI chấm điểm
                    (0.0 → 1.0)
                           |
         +-----------------+-----------------+
         |                 |                 |
    Điểm thấp         Điểm trung         Điểm cao
    (≤ 0.3)          (0.3 - 0.7)          (> 0.7)
         |                 |                 |
    Tự động           Chuyển cho          Tự động
    DUYỆT ✅         Reviewer xem        TỪ CHỐI ❌
                      (MANUAL REVIEW)
```

Chỉ ~20-30% giao dịch cần người xem xét thật sự. 70-80% còn lại được xử lý tự động trong mili giây.

---

## 4. Các nhân vật trong hệ thống — Họ làm gì hằng ngày?

| Nhân vật | Làm gì hằng ngày |
|---|---|
| **OPERATOR** (Nhân viên vận hành) | Mô phỏng gửi giao dịch, nhập đơn vay vào hệ thống. Trong môi trường thật đây là hệ thống tự động gửi request. |
| **REVIEWER** (Nhân viên duyệt) | Sáng đến, mở màn hình, thấy danh sách ~50 case cần xử lý. Nhận từng case, đọc thông tin, quyết định duyệt hay từ chối, ghi lý do. Chiều chốt hết. |
| **MANAGER** (Quản lý) | Xem dashboard mỗi sáng: hôm qua có bao nhiêu giao dịch, bao nhiêu fraud bị chặn, bao nhiêu case tồn đọng. Xuất báo cáo tuần/tháng cho ban giám đốc. |
| **ADMIN** (Kỹ thuật) | Tạo tài khoản nhân viên mới. Chạy pipeline đêm nếu bị lỗi. Kiểm tra kết quả đối soát để phát hiện dữ liệu mất mát. |

---

## 5. Hai khái niệm kỹ thuật quan trọng nhất

### A. Idempotency — Chống trừ tiền 2 lần

**Tình huống:** Bạn bấm thanh toán 100.000đ. Mạng bị chậm, app báo lỗi. Bạn bấm lại. Hệ thống nhận được 2 request.

**Không có Idempotency:** Trừ tiền 2 lần.

**Có Idempotency:** Hệ thống nhận ra request thứ 2 là bản sao của request thứ 1 (dựa vào hash của thông tin giao dịch), trả lại kết quả cũ mà không xử lý lại.

### B. Reconciliation — Đối soát cuối ngày

**Tình huống:** Hệ thống ghi nhận 10.000 giao dịch. Kho dữ liệu thống kê chỉ thấy 9.998. Mất 2 giao dịch ở đâu?

Mỗi tối, hệ thống tự động đếm và cộng tiền từ 3 nguồn độc lập (DB nghiệp vụ, Data Lake, Data Warehouse). Nếu khớp → yên tâm. Nếu lệch → báo động để điều tra ngay.

---

## 6. Vòng đời 1 ngày làm việc của hệ thống

```
GIỜ LÀM VIỆC (8h - 17h)
   - Operator gửi giao dịch liên tục
   - AI chấm điểm và phân luồng tự động
   - Reviewer duyệt case MANUAL_REVIEW
   - Manager theo dõi dashboard realtime

CUỐI NGÀY (17h - 23h)
   - ETL Pipeline tự động chạy:
     Đọc log thô → Làm sạch → Nạp vào Warehouse
   - Reconciliation Job tự động chạy:
     So sánh 3 nguồn dữ liệu → Báo MATCH hoặc MISMATCH

ĐẦU GIỜ HÔM SAU (7h)
   - Admin kiểm tra kết quả ETL và Reconciliation
   - Manager đọc báo cáo tổng hợp hôm qua
   - Vòng mới bắt đầu
```

---

## 7. Một điều quan trọng cần nhớ

> **Mọi hành động trong hệ thống đều phải để lại dấu vết (Audit Log).**

Ngân hàng không có khái niệm "làm mà không ghi chép". Khi có tranh chấp — khách hàng tố ngân hàng duyệt nhầm, nhân viên tố bị oan — Audit Log là bằng chứng pháp lý duy nhất. Đó là lý do bảng `audit_logs` được coi là bảng quan trọng nhất và **không bao giờ được phép xóa hay chỉnh sửa**.
