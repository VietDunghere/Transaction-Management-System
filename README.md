# Hệ thống Phân tích Rủi ro và Đánh giá Tài chính (HPTRRĐGTC)

## Tóm tắt điều hành

Hệ thống Phân tích Rủi ro và Đánh giá Tài chính (HPTRRĐGTC) là một nền tảng cấp doanh nghiệp được thiết kế để tự động hóa xử lý giao dịch, phát hiện gian lận, đánh giá tín dụng, và phân tích rủi ro tài chính cho các tổ chức ngân hàng. Hệ thống kết hợp cơ chế định tuyến thông minh dựa trên AI, quy trình kiểm duyệt có kiểm soát, và module phân tích chuyên sâu cho phép Analyst theo dõi hiệu suất mô hình, đề xuất điều chỉnh ngưỡng, và báo cáo lên cấp quản lý — tất cả với audit trail đầy đủ để tuân thủ quy định.

---

## Phát biểu vấn đề

Các tổ chức tài chính phải đối mặt với những thách thức quan trọng trong xử lý giao dịch:

**1. Hiệu quả phát hiện gian lận thấp**
Kiểm tra thủ công từng giao dịch tốn thời gian và dễ bị lỗi. Các giao dịch gian lận thường không được phát hiện, dẫn đến mất mát tài chính đáng kể.

**2. Tắc nghẽn xử lý**
Không có định tuyến thông minh, tất cả giao dịch cần xét duyệt thủ công tạo ra tình trạng quá tải hoạt động, làm chậm kết toán giao dịch.

**3. Lỗ hổng tuân thủ**
Thiếu các bản ghi kiểm tra toàn diện khiến khó khăn trong việc chứng minh tuân thủ các yêu cầu quy định và tạo ra vấn đề về trách nhiệm.

**4. Dữ liệu không nhất quán**
Dữ liệu giao dịch tồn tại ở nhiều hệ thống (cơ sở dữ liệu OLTP, nhật ký thô, kho dữ liệu phân tích) mà không có cơ chế đối soát tự động.

**5. Báo cáo thủ công**
Trí tuệ kinh doanh và báo cáo yêu cầu can thiệp thủ công, ngăn cản thông tin chi tiết theo thời gian thực về các mẫu giao dịch và xu hướng gian lận.

---

## Tổng quan giải pháp

TMS giải quyết những thách thức này thông qua một nền tảng tích hợp cung cấp:

**1. Định tuyến giao dịch tự động**
Các giao dịch được phân loại tự động dựa trên chấm điểm rủi ro gian lận, loại bỏ xét duyệt thủ công không cần thiết.

**2. Phát hiện gian lận thông minh**
Hệ thống chấm điểm dựa trên AI đánh giá các yếu tố rủi ro giao dịch và định tuyến tương ứng.

**3. Quy trình xét duyệt được quản lý**
Các trường hợp cần xét duyệt thủ công được chỉ định có hệ thống và xử lý với tài liệu bắt buộc.

**4. Bản ghi kiểm tra đầy đủ**
Tất cả hành động được ghi lại với người thực hiện, dấu thời gian, và lý do để tuân thủ và phân tích pháp y.

**5. Kỹ thuật dữ liệu tự động**
Đường dẫn ETL trích xuất, chuyển đổi và tải dữ liệu giao dịch vào kho dữ liệu phân tích để báo cáo.

**6. Xác minh tính toàn vẹn dữ liệu**
Quy trình đối soát tự động đảm bảo tính nhất quán trên các hệ thống OLTP, Data Lake và Warehouse.

---

## Các diễn viên hệ thống và trường hợp sử dụng

### Vai trò người dùng

**OPERATOR (Người gửi giao dịch)**
- Gửi giao dịch và đơn vay vào hệ thống
- Xem kết quả xử lý giao dịch
- Cung cấp dữ liệu đầu vào cho đánh giá rủi ro gian lận

**REVIEWER (Người đưa ra quyết định)**
- Xét duyệt các giao dịch được đánh dấu để kiểm tra thủ công
- Đưa ra quyết định phê duyệt hoặc từ chối
- Ghi chú lý do cho từng quyết định
- Chịu trách nhiệm cho các quyết định xét duyệt

**ANALYST (Chuyên viên phân tích rủi ro)**
- Theo dõi và phân tích hiệu suất mô hình fraud detection & credit scoring
- Xem xét phân phối điểm và tỷ lệ false positive
- Điều chỉnh ngưỡng phân loại (reject/review threshold) khi cần
- Tạo và quản lý suppression rules cho merchant/customer đặc biệt
- Soạn báo cáo phân tích dạng Markdown và trình lên MANAGER để xem xét
- Xuất báo cáo dưới dạng PDF chuyên nghiệp

**MANAGER (Người giám sát hoạt động)**
- Theo dõi các chỉ số và KPI trên bảng điều khiển
- Phân tích các mẫu gian lận và xu hướng thông qua báo cáo
- Xét duyệt bản ghi kiểm tra để đảm bảo chất lượng
- Tạo báo cáo tuân thủ và xuất bản
- Xem xét và xác nhận báo cáo phân tích từ ANALYST

**ADMIN (Quản trị viên hệ thống)**
- Quản lý tài khoản người dùng và kiểm soát truy cập
- Thực thi các công việc đường dẫn ETL
- Khởi tạo và giám sát các quy trình đối soát
- Khắc phục các vấn đề hệ thống

---

## Chức năng cốt lõi

### 1. Xác thực và kiểm soát truy cập

Hệ thống triển khai kiểm soát truy cập dựa trên vai trò (RBAC) thông qua xác thực dựa trên JWT. Mỗi vai trò người dùng có các quyền cụ thể hạn chế quyền truy cập vào các tính năng và dữ liệu có liên quan. Ủy quyền dựa trên token đảm bảo thiết kế API không trạng thái trong khi duy trì bảo mật.

### 2. Phát hiện gian lận và định tuyến

Các giao dịch đến trải qua phân tích tự động thông qua công cụ chấm điểm gian lận. Công cụ đánh giá nhiều yếu tố rủi ro và gán một điểm được chuẩn hóa từ 0,0 đến 1,0. Dựa trên điểm số:

- Điểm dưới 0,30: Giao dịch được phê duyệt tự động
- Điểm từ 0,30 đến 0,70: Giao dịch được định tuyến để xét duyệt thủ công (tạo trường hợp)
- Điểm cao hơn 0,70: Giao dịch bị từ chối tự động
- Các giao dịch có giá trị cao (vượt quá ngưỡng được cấu hình) ghi đè để xét duyệt thủ công

### 3. Quản lý trường hợp và quy trình xét duyệt

Các giao dịch cần xét duyệt thủ công được chuyển đổi thành các trường hợp. Những người xét duyệt có thể:
- Xem các trường hợp được chỉ định với chi tiết giao dịch và lý do chấm điểm gian lận
- Chỉ định các trường hợp cho chính họ để xét duyệt
- Ghi chú quyết định phê duyệt hoặc từ chối với ghi chú bắt buộc
- Theo dõi trạng thái trường hợp cho đến khi hoàn thành

### 4. Tính idempotent và phòng chống trùng lặp

Hệ thống duy trì một khóa idempotency cho mỗi giao dịch để ngăn chặn xử lý trùng lặp. Nếu một giao dịch được gửi nhiều lần (do lỗi mạng hoặc thử lại), hệ thống sẽ trả lại kết quả được lưu trong bộ nhớ cache thay vì xử lý lại.

### 5. Ghi nhật ký kiểm tra và khả năng truy vết

Ghi nhật ký toàn diện ghi lại tất cả các hành động hệ thống:
- Tạo giao dịch và thay đổi trạng thái
- Chỉ định trường hợp, xét duyệt và quyết định
- Lý do chấm điểm gian lận
- Các hành động của người dùng với dấu thời gian
- Lý do phê duyệt/từ chối

Các nhật ký kiểm tra có thể được truy vấn, xuất bản và truy vết theo giao dịch để phân tích pháp y hoàn chỉnh.

### 6. Bảng điều khiển và báo cáo

Hệ thống cung cấp khả năng hiển thị theo thời gian thực thông qua:
- Bảng tổng quan hiển thị khối lượng giao dịch, tỷ lệ gian lận và các trường hợp đang chờ
- Biểu đồ phân phối gian lận so sánh giao dịch gian lận với giao dịch hợp pháp
- Báo cáo dựa trên kỳ (hàng ngày, hàng tuần, hàng tháng) với số lượng giao dịch và số tiền
- Phân tích trạng thái (phê duyệt, từ chối, xét duyệt thủ công) với tỷ lệ phần trăm
- Báo cáo có thể xuất được ở các định dạng chuẩn (CSV, PDF)

### 7. Đường dẫn ETL

Đường dẫn kỹ thuật dữ liệu tự động xử lý nhật ký giao dịch thô:
- Trích xuất: Đọc các nhật ký giao dịch thô từ lưu trữ Data Lake
- Chuyển đổi: Áp dụng các kiểm tra chất lượng dữ liệu, khử trùng lặp và làm giàu (ánh xạ GeoIP)
- Tải: Chèn dữ liệu được xử lý vào kho dữ liệu phân tích với các bảng chiều thích hợp
- Giám sát: Ghi lại trạng thái thực thi đường dẫn, số lượng bản ghi và chi tiết lỗi

### 8. Quy trình đối soát

Đối soát hàng ngày tự động xác minh tính toàn vẹn dữ liệu trên các hệ thống:
- So sánh số lượng giao dịch giữa cơ sở dữ liệu OLTP, Data Lake và Warehouse
- Xác thực các khoản tổng hợp trên các hệ thống
- Báo cáo trạng thái phù hợp (MATCH hoặc MISMATCH)
- Chi tiết sự không phù hợp khi phát hiện không nhất quán
- Cho phép phân tích nguyên nhân gốc rễ và sửa chữa dữ liệu

### 9. Hỗ trợ quyết định cho vay

Hệ thống bao gồm một trình mô phỏng phê duyệt cho vay có thể:
- Phân tích các đặc điểm của người xin vay
- Tính toán điểm Xác suất Vỡ nợ (PD Score)
- Phân loại mức rủi ro (THẤP, TRUNG BÌNH, CAO)
- Hỗ trợ phân tích giả định cho mô hình quyết định tín dụng

### 10. Module Phân tích Chuyên sâu (Analyst Module)

Module dành riêng cho ANALYST cung cấp bộ công cụ phân tích rủi ro toàn diện:

**Quản lý ngưỡng mô hình:**
- Xem và điều chỉnh các ngưỡng phân loại của fraud model (`reject_threshold`, `review_threshold`) và credit model (`high_risk_threshold`, `medium_risk_threshold`)
- Mọi thay đổi được ghi vào audit log với actor và timestamp

**Hiệu suất mô hình:**
- Thống kê phân phối điểm fraud score theo khoảng thời gian tùy chọn
- Tính tỷ lệ false positive dựa trên quyết định thực tế của reviewer
- Thống kê phân phối rủi ro tín dụng và tỷ lệ phê duyệt/từ chối

**Suppression Rules:**
- Tạo whitelist bypass fraud scoring cho merchant/customer/card VIP
- Quản lý danh sách rules (xem, vô hiệu hóa), mỗi thay đổi có audit log

**Báo cáo Analyst:**
- Soạn báo cáo phân tích dạng Markdown (hỗ trợ bảng, header, danh sách)
- Vòng đời báo cáo: `PENDING_REVIEW → ACKNOWLEDGED → ARCHIVED`
- MANAGER xác nhận báo cáo và ghi chú phản hồi
- Xuất báo cáo dưới dạng **PDF chuyên nghiệp** với header thương hiệu, bảng định dạng đầy đủ, khối xác nhận màu xanh, và hỗ trợ tiếng Việt Unicode đầy đủ

---

## Kiến trúc hệ thống

Hệ thống tuân theo mô hình kiến trúc phân tầng:

```
Tầng Trình bày
  Ứng dụng khách (Cổng thông tin Operator, Bảng điều khiển Reviewer, Bảng điều khiển Admin)
        |
Tầng API
  API HTTP RESTful với xác thực JWT
        |
Tầng Dịch vụ
  Logic nghiệp vụ (Chấm điểm gian lận, Quản lý trường hợp, Ghi nhật ký kiểm tra)
        |
Tầng Kho lưu trữ
  Trừu tượng hóa truy cập dữ liệu
        |
Tầng Dữ liệu
  Cơ sở dữ liệu OLTP (Oracle)
  Data Lake (Nhật ký thô)
  Kho dữ liệu phân tích (OLAP)
        |
Công việc nền
  Đường dẫn ETL, Quy trình đối soát
```

### Stack công nghệ

- Framework backend: FastAPI (Python)
- Cơ sở dữ liệu: Oracle 23ai Free (chính), SQLite (dev fallback)
- ORM: SQLAlchemy + Alembic (migration)
- PDF rendering: fpdf2 + Arial Unicode TTF (hỗ trợ tiếng Việt)
- Triển khai: Docker (Oracle container), sẵn sàng cho Kubernetes

---

## Quy trình hoạt động

### Quy trình xử lý giao dịch

1. OPERATOR gửi giao dịch thông qua API với chi tiết thẻ, số tiền, ID nhà bán lẻ, dấu thời gian và siêu dữ liệu
2. Hệ thống xác thực dữ liệu đầu vào theo các quy tắc nghiệp vụ
3. Hệ thống kiểm tra khóa idempotency để ngăn chặn xử lý trùng lặp
4. Công cụ chấm điểm gian lận đánh giá các yếu tố rủi ro giao dịch
5. Hệ thống định tuyến giao dịch dựa trên điểm số:
   - Phê duyệt tự động (rủi ro thấp)
   - Tạo trường hợp để xét duyệt thủ công (rủi ro trung bình)
   - Từ chối tự động (rủi ro cao)
6. Hệ thống ghi lại tất cả các hành động với dấu thời gian và người thực hiện
7. Chỉ định trường hợp thông báo REVIEWER nếu cần xét duyệt thủ công
8. REVIEWER xét duyệt chi tiết trường hợp và đưa ra quyết định
9. REVIEWER ghi chú lý do quyết định
10. Trạng thái giao dịch được cập nhật và bản ghi nhật ký kiểm tra được ghi
11. Kết quả được trả về cho hệ thống gốc

### Các quy trình cuối ngày

1. Công việc ETL trích xuất nhật ký giao dịch thô từ Data Lake
2. Chuyển đổi dữ liệu áp dụng các kiểm tra chất lượng và làm giàu
3. Dữ liệu được xử lý được tải vào kho dữ liệu phân tích
4. Trạng thái thực thi ETL được ghi lại
5. Quy trình đối soát xác minh tính nhất quán dữ liệu
6. Sự không phù hợp được báo cáo để điều tra
7. Báo cáo được tạo để xét duyệt bởi các bên liên quan

---

## Mô hình nhất quán dữ liệu

Hệ thống duy trì tính nhất quán dữ liệu thông qua:

**1. Tính toàn vẹn giao dịch**
Các giao dịch cơ sở dữ liệu đảm bảo cập nhật nguyên tử.

**2. Khóa lạc quan**
Các trường phiên bản ngăn chặn xung đột sửa đổi đồng thời.

**3. Bản ghi kiểm tra**
Tất cả các thay đổi được ghi lại để phân tích pháp y.

**4. Đối soát**
Xác minh hàng ngày đảm bảo tính nhất quán trên các hệ thống.

**5. Quản lý trạng thái**
Xác thực chuyển trạng thái ngăn chặn các thay đổi trạng thái không hợp lệ.

---

## Bảo mật và tuân thủ

Hệ thống triển khai các biện pháp kiểm soát bảo mật bao gồm:

**1. Xác thực**
Xác thực dựa trên JWT không trạng thái.

**2. Ủy quyền**
Kiểm soát truy cập dựa trên vai trò với thực thi quyền.

**3. Bảo vệ dữ liệu**
Dữ liệu thẻ được che mặt trong quá trình truyền và lưu trữ.

**4. Ghi nhật ký kiểm tra**
Ghi nhật ký hành động hoàn chỉnh với xác định người thực hiện.

**5. Idempotency**
Ngăn chặn xử lý giao dịch trùng lặp.

**6. Xuất bản compliance**
Kiểm tra nhật ký và xuất báo cáo để gửi quy định.

---

## Đặc điểm hiệu suất

Hệ thống được thiết kế để xử lý:

- Khối lượng giao dịch cao (hàng triệu hàng ngày)
- Chấm điểm gian lận theo thời gian thực
- Xử lý dữ liệu có thể mở rộng thông qua ETL hàng loạt
- Khả năng xử lý phân tán
- Nhiều người dùng đồng thời với cách ly dựa trên vai trò

---

## Trạng thái triển khai

Triển khai hiện tại bao gồm:

- Backend hoàn chỉnh: **43+ endpoints** trên 9 module
- Cơ sở dữ liệu Oracle 23ai với đầy đủ Alembic migration
- ML models: fraud detection (Random Forest) + credit scoring (XGBoost)
- Module Analyst: thresholds, suppression rules, báo cáo Markdown + PDF
- SSE real-time stream cho giao dịch và dashboard
- Seed data đầy đủ cho mọi role (OPERATOR, REVIEWER, ANALYST, MANAGER, ADMIN)

---

## Bảo mật doanh nghiệp đã triển khai

Hệ thống đáp ứng tiêu chuẩn doanh nghiệp với các kiểm soát sau:

**Segregation of Duties (4-eyes principle)**
- Người tạo đơn vay không được tự phê duyệt → 403
- Reviewer không được quyết định case cho giao dịch do chính mình submit → 403
- MANAGER/ADMIN có thể override trong trường hợp khẩn

**Optimistic Locking**
- Mọi thao tác ghi quan trọng (loan decision, case decision) đều yêu cầu `version` field
- Conflict khi version không khớp → 409

**Audit Log toàn diện**
- Mọi thao tác ghi (tạo, cập nhật, xóa) đều ghi `AuditLog` với actor + timestamp
- Bao gồm: threshold update, suppression rule, ETL trigger, reconciliation resolve, analyst report

**Input Validation**
- `txn_time` không được nằm trong tương lai (tolerance 5 phút)
- CORS tightened cho môi trường production

**RBAC**
- 5 roles với phân quyền rõ ràng: OPERATOR, REVIEWER, ANALYST, MANAGER, ADMIN

---

## Các bước tiếp theo

1. Xem xét và ưu tiên hóa các vấn đề được xác định
2. Triển khai sửa chữa vấn đề quan trọng trước khi phát triển
3. Tinh chỉnh thiết kế API dựa trên các khuyến nghị kiểm toán
4. Thiết lập tiêu chuẩn phát triển và quy trình xét duyệt mã
5. Triển khai các bài kiểm tra đơn vị và tích hợp
6. Triển khai cho môi trường tổng thể
7. Tiến hành đánh giá bảo mật
8. Thực hiện kiểm tra tải
9. Triển khai cho sản xuất

---

## Tham chiếu tài liệu

- `docs/API_DESIGN.md`: Đặc tả API hoàn chỉnh (43+ endpoints, 9 module UC)
- `docs/API_SUMMARY.md`: Tham chiếu nhanh tổng hợp endpoint
- `docs/API_AUDIT.md`: Phân tích vấn đề doanh nghiệp với các bước khắc phục
- `docs/PROJECT_STRUCTURE.md`: Ánh xạ trách nhiệm lớp kiến trúc
- `docs/USECASE.md`: Mô tả use case chi tiết và tương tác actor
- `docs/SYSTEM_WORKFLOW.md`: Luồng xử lý giao dịch end-to-end
- `docs/DB_TABLES_EXPLAINED.md`: Giải thích từng bảng DB và quan hệ

---

## Liên hệ và hỗ trợ

Để đặt câu hỏi kỹ thuật, báo cáo lỗi hoặc yêu cầu tính năng:

- GitHub Issues: [Các vấn đề dự án](https://github.com/VietDunghere/Transaction-Management-System/issues)
- GitHub Discussions: [Thảo luận dự án](https://github.com/VietDunghere/Transaction-Management-System/discussions)

---

## Lịch sử phiên bản

| Phiên bản | Ngày | Thay đổi |
|----------|------|---------|
| 1.0 | 2026-04-07 | Thiết lập dự án ban đầu với thiết kế API và cấu trúc dự án |
| 1.1 | 2026-04-10 | Triển khai đầy đủ backend: auth, transactions, loans, cases, ETL, reconciliation, dashboard, SSE |
| 1.2 | 2026-04-15 | Thêm role ANALYST: threshold management, model performance, suppression rules |
| 1.3 | 2026-04-19 | Thêm Analyst Reports (Markdown + PDF export), đổi tên thành HPTRRĐGTC, vá SoD và AuditLog gaps |

---

## Phụ lục: Yêu cầu hệ thống

**Yêu cầu chức năng**
- Xử lý giao dịch với chấm điểm gian lận theo thời gian thực
- Hỗ trợ xét duyệt trường hợp đồng thời mà không làm hỏng dữ liệu
- Duy trì bản ghi kiểm tra đầy đủ của tất cả các giao dịch
- Cung cấp đối soát hàng ngày trên nhiều hệ thống
- Xuất báo cáo ở các định dạng chuẩn (CSV, PDF)

**Yêu cầu phi chức năng**
- Hỗ trợ hàng triệu giao dịch mỗi ngày
- Thời gian phản hồi API dưới 500ms (p95)
- Tính khả dụng 99,9% trong giờ kinh doanh
- Lưu giữ dữ liệu theo yêu cầu quy định
- Có thể mở rộng cho nhiều vùng triển khai

---

Phiên bản tài liệu: 1.3
Cập nhật lần cuối: 2026-04-19
Trạng thái: Hoạt động
