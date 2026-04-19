# Mô tả Hệ thống Quản lý Vòng đời Giao dịch bằng Ngôn ngữ Tự nhiên

---

### **Các bước thực hiện**

* Bước 1: Giới thiệu mục đích hệ thống
* Bước 2: Phạm vi hệ thống — ai được dùng phần mềm/hệ thống? Mỗi người vào hệ thống được phép thực hiện các chức năng nào?
* Bước 3: Với mỗi chức năng mà người dùng được phép thực hiện ở bước 2, mô tả chi tiết hoạt động nghiệp vụ của chức năng đó diễn ra như thế nào?
* Bước 4: Các đối tượng nào được quản lý, xử lý trong hệ thống? Mỗi đối tượng cần dùng/quản lý các thuộc tính nào?
* Bước 5: Quan hệ (số lượng) giữa các đối tượng đã nêu ở bước 4?

---

### **Áp dụng**

---

***Bước 1: Mục đích của hệ thống***: Hệ thống phần mềm **Transaction Management System (TMS)** phục vụ công tác quản lý toàn bộ vòng đời giao dịch ngân hàng — từ khi một giao dịch được nộp vào đến khi có quyết định duyệt hoặc từ chối — bao gồm: tự động chấm điểm rủi ro gian lận (Fraud Scoring) và rủi ro tín dụng (Credit Risk Scoring) bằng mô hình AI, phân luồng giao dịch sang xử lý tự động hoặc chuyển cho nhân viên xem xét thủ công, quản lý vòng đời hồ sơ tín dụng (Loan Application), lưu vết toàn bộ hành động nghiệp vụ (Audit Logging), đối soát dữ liệu giữa các lớp hệ thống (Reconciliation), vận hành pipeline nạp dữ liệu từ Data Lake vào Kho dữ liệu thống kê (ETL), và cung cấp Dashboard & Báo cáo phục vụ quản trị.

Hệ thống **không** phải Core Banking — không hạch toán số dư thật vào tài khoản — mà đóng vai trò là **lớp trung gian xử lý quyết định** đứng giữa yêu cầu giao dịch đến và kết quả phê duyệt cuối cùng. Mọi quyết định nghiệp vụ đều phải được ghi nhận, có thể truy vết, và đảm bảo tính toàn vẹn dữ liệu theo chuẩn ACID.

---

***Bước 2: Phạm vi hệ thống***: Những người được vào hệ thống và chức năng mỗi người được thực hiện khi vào hệ thống này được quy định như sau:

* **Thành viên hệ thống** (bất kỳ tài khoản nào đã được cấp):
  * Đăng nhập vào hệ thống
  * Đăng xuất khỏi hệ thống
  * Đổi mật khẩu cá nhân

* **OPERATOR** (Nhân viên vận hành):
  * Được thực hiện các chức năng như thành viên hệ thống
  * Nộp giao dịch mới vào hệ thống để chấm điểm và phân luồng
  * Xem danh sách các giao dịch do mình nộp
  * Nộp hồ sơ đề nghị vay vốn (Loan Application) vào hệ thống

* **REVIEWER** (Nhân viên duyệt hồ sơ):
  * Được thực hiện các chức năng như thành viên hệ thống
  * Xem danh sách các case đang chờ xử lý thủ công (trạng thái OPEN)
  * Nhận (Assign) một case về tên mình để xử lý
  * Đưa ra quyết định phê duyệt (Approve) hoặc từ chối (Reject) một case đã nhận, kèm ghi chú lý do

* **MANAGER** (Quản lý):
  * Được thực hiện các chức năng như thành viên hệ thống
  * Nộp giao dịch mới vào hệ thống để chấm điểm và phân luồng
  * Nộp hồ sơ đề nghị vay vốn (Loan Application) vào hệ thống
  * Phê duyệt hoặc từ chối hồ sơ vay đang chờ duyệt (ràng buộc SoD: không được phê duyệt hồ sơ do chính mình tạo)
  * Đưa ra quyết định override với case đang ở trạng thái ASSIGNED (giám sát REVIEWER)
  * Xem danh sách và chi tiết giao dịch, hồ sơ vay, case
  * Xem Dashboard tổng quan hoạt động hệ thống (số giao dịch, tỉ lệ phê duyệt, tỉ lệ gian lận, case tồn đọng)
  * Xem biểu đồ xu hướng gian lận theo ngày (Fraud Trend Chart — lookback tối đa 90 ngày)
  * Xem danh sách báo cáo giao dịch (lọc theo thời gian, trạng thái, khách hàng)
  * Xuất báo cáo giao dịch và báo cáo gian lận theo ngày ra file CSV
  * Xem Audit Log — lịch sử toàn bộ hành động nghiệp vụ trong hệ thống

* **ADMIN** (Kỹ thuật / Quản trị hệ thống):
  * Được thực hiện các chức năng như thành viên hệ thống
  * Nộp giao dịch mới vào hệ thống
  * Nộp hồ sơ đề nghị vay vốn
  * Phê duyệt hoặc từ chối hồ sơ vay (ràng buộc SoD: không được phê duyệt hồ sơ do chính mình tạo)
  * Đưa ra quyết định override với case đang ở trạng thái ASSIGNED
  * Tạo tài khoản người dùng mới, vô hiệu hóa tài khoản, kích hoạt lại tài khoản, cấp phát vai trò
  * Xem danh sách và chi tiết snapshot trong Data Lake (endpoint `/datalake/snapshots`)
  * Nạp dữ liệu thô vào Data Lake (endpoint `POST /datalake/ingest`)
  * Kích hoạt thủ công ETL Pipeline (endpoint `POST /etl/run`)
  * Xem log kết quả các lần chạy ETL
  * Kích hoạt và theo dõi Reconciliation Job (endpoint `POST /reconciliation/run`)

Những chức năng không đề cập đến thì mặc định là không thuộc phạm vi của hệ thống (ví dụ: hạch toán tài khoản, chuyển tiền thật, quản lý thẻ vật lý, v.v.).

---

***Bước 3: Hoạt động nghiệp vụ của các chức năng***: Mỗi chức năng liệt kê trong bước 2 đều được mô tả chi tiết dưới đây.

---

#### THÀNH VIÊN HỆ THỐNG

* *Đăng nhập*: Người dùng truy cập trang đăng nhập → nhập tên đăng nhập (username) và mật khẩu → hệ thống kiểm tra thông tin xác thực bằng cách đối chiếu mật khẩu đã được băm (bcrypt) với bản ghi trong cơ sở dữ liệu → nếu hợp lệ: hệ thống tạo một JWT Token có thời hạn (access token) và trả về cho client, client lưu token này để đính kèm vào các request tiếp theo → nếu không hợp lệ: hệ thống trả về lỗi 401 Unauthorized và người dùng được yêu cầu nhập lại → hệ thống ghi lại sự kiện đăng nhập (thành công hoặc thất bại) vào Audit Log.

* *Đăng xuất*: Người dùng chọn chức năng đăng xuất → hệ thống vô hiệu hóa JWT Token hiện tại của phiên làm việc (thêm token vào danh sách đen hoặc xóa khỏi session) → hệ thống xóa token khỏi bộ nhớ phía client → người dùng được chuyển về trang đăng nhập → hệ thống ghi sự kiện đăng xuất vào Audit Log.

* *Đổi mật khẩu cá nhân*: Người dùng đăng nhập vào hệ thống → chọn chức năng đổi mật khẩu → nhập mật khẩu cũ, mật khẩu mới và xác nhận mật khẩu mới → hệ thống kiểm tra mật khẩu cũ có khớp không → nếu không khớp: trả về lỗi và yêu cầu nhập lại → nếu khớp: hệ thống kiểm tra mật khẩu mới thỏa mãn chính sách độ mạnh (độ dài tối thiểu, có ký tự đặc biệt) → băm (hash) mật khẩu mới bằng bcrypt → cập nhật bản ghi trong bảng USERS → ghi sự kiện thay đổi mật khẩu vào Audit Log → thông báo thành công và tự động đăng xuất phiên hiện tại để bắt buộc đăng nhập lại với mật khẩu mới.

---

#### OPERATOR

* *Nộp giao dịch mới*: OPERATOR đăng nhập vào hệ thống → chọn chức năng nộp giao dịch → nhập thông tin giao dịch (mã khách hàng, số tiền, loại tiền tệ, tên đơn vị thụ hưởng/merchant, kênh giao dịch: ATM/POS/ONLINE) → hệ thống tính toán một chuỗi băm (txn_hash) từ các trường dữ liệu tĩnh của giao dịch để tạo Idempotency Key → hệ thống kiểm tra Idempotency Key này đã tồn tại trong bảng TXN_IDEMPOTENCY chưa:
  * Nếu **đã tồn tại** (request trùng lặp): hệ thống trả lại kết quả của lần xử lý trước đó, không xử lý lại, không trừ tiền hai lần.
  * Nếu **chưa tồn tại**: tiếp tục xử lý.

  Hệ thống che/mask số thẻ (nếu có) trước khi lưu vào DB để bảo vệ dữ liệu nhạy cảm → hệ thống gọi mô hình AI Random Forest (Fraud Scoring Model) để chấm điểm gian lận, nhận về một giá trị `fraud_score` từ 0.0 đến 1.0 → hệ thống phân luồng dựa trên ngưỡng điểm:
  * Nếu **fraud_score < 0.35**: giao dịch được **tự động phê duyệt** (APPROVED).
  * Nếu **0.35 ≤ fraud_score < 0.65** hoặc số tiền vượt ngưỡng quy định: giao dịch chuyển sang trạng thái **MANUAL_REVIEW** và hệ thống tự động tạo một **REVIEW_CASE** để Reviewer xem xét thủ công.
  * Nếu **fraud_score ≥ 0.65**: giao dịch bị **tự động từ chối** (REJECTED).

  Kết quả được ghi vào bảng TRANSACTIONS_LIVE → trạng thái ghi vào TXN_STATE → Idempotency Key ghi vào TXN_IDEMPOTENCY → hệ thống **tự động kích hoạt Trigger** ghi một bản ghi vào bảng AUDIT_LOGS (ghi nhận ai nộp giao dịch, lúc nào, kết quả là gì) → OPERATOR nhận phản hồi với kết quả phân loại và `fraud_score`.

* *Xem danh sách giao dịch cá nhân*: OPERATOR đăng nhập → chọn chức năng xem giao dịch → hệ thống hiển thị danh sách các giao dịch do OPERATOR này nộp (lọc theo `submitted_by = current_user_id`), được phân trang, gồm thông tin: mã giao dịch, thời gian, số tiền, tên merchant, kênh, điểm gian lận, trạng thái hiện tại → OPERATOR có thể lọc thêm theo khoảng thời gian, trạng thái, kênh → OPERATOR click vào một giao dịch cụ thể để xem chi tiết đầy đủ (bao gồm lý do từ chối nếu có, mã case liên quan nếu có).

* *Nộp hồ sơ đề nghị vay vốn*: OPERATOR đăng nhập → chọn chức năng nộp hồ sơ vay → nhập thông tin tín dụng của khách hàng (mã khách hàng, số tiền đề nghị vay, mục đích vay, thu nhập hàng tháng, tỉ lệ nợ hiện tại / Debt-to-Income Ratio, lịch sử tín dụng) → hệ thống gọi mô hình AI Loan Risk Model để tính **PD Score** (Probability of Default — xác suất khách hàng không trả được nợ), nhận về giá trị từ 0.0 đến 1.0 → hệ thống phân loại mức độ rủi ro:
  * **LOW RISK**: PD Score thấp — khả năng trả nợ tốt.
  * **MEDIUM RISK**: PD Score trung bình — cần xem xét thêm điều kiện.
  * **HIGH RISK**: PD Score cao — rủi ro không trả được nợ lớn.

  Hồ sơ vay được lưu vào bảng LOAN_APPLICATIONS cùng điểm PD → điểm chi tiết ghi vào LOAN_RISK_SCORES kèm phiên bản mô hình đã dùng → hệ thống ghi Audit Log → OPERATOR nhận kết quả phân loại rủi ro.

---

#### REVIEWER

* *Xem danh sách case chờ xử lý*: REVIEWER đăng nhập → chọn chức năng quản lý case → hệ thống hiển thị danh sách các REVIEW_CASE đang có trạng thái OPEN (chưa được nhận bởi ai), gồm: mã case, mã giao dịch liên quan, số tiền giao dịch, điểm gian lận, thời gian tạo case, thời gian chờ (SLA) → REVIEWER có thể sắp xếp theo thời gian chờ (lâu nhất lên trước) hoặc lọc theo khoảng fraud_score → REVIEWER cũng thấy danh sách các case đang ASSIGNED cho mình (đã nhận nhưng chưa quyết định).

* *Nhận case (Assign)*: REVIEWER xem danh sách case → chọn một case muốn xử lý → gọi endpoint `POST /cases/{id}/assign` → hệ thống thực hiện **Database Locking** bằng câu lệnh `UPDATE ... WHERE assigned_to IS NULL` để đảm bảo chỉ một Reviewer nhận được case tại một thời điểm (tránh hai người cùng nhận một case) → nếu thành công: trạng thái case chuyển từ OPEN sang ASSIGNED, `assigned_to` được gán bằng ID của REVIEWER hiện tại, số phiên bản (`version`) của case được tăng lên 1 → hệ thống ghi Audit Log → REVIEWER nhận phản hồi xác nhận case đã được gán cho mình → nếu case đã được người khác nhận trước: hệ thống trả về thông báo lỗi, REVIEWER được yêu cầu chọn case khác.

* *Đưa ra quyết định phê duyệt/từ chối*: REVIEWER đã nhận case → đọc toàn bộ thông tin: thông tin khách hàng, chi tiết giao dịch, điểm gian lận, lịch sử giao dịch trước của khách hàng, lý do hệ thống tạo case → phân tích và đưa ra quyết định → gọi endpoint `PATCH /cases/{id}/decision` kèm: quyết định (APPROVED / REJECTED), ghi chú lý do nghiệp vụ (bắt buộc), và **số phiên bản case hiện tại** (version) → hệ thống thực hiện **Optimistic Locking**: kiểm tra `version` trong request có khớp với `version` trong DB không:
  * Nếu **khớp**: tiến hành xử lý → cập nhật case (case_status = APPROVED hoặc REJECTED) → cập nhật trạng thái giao dịch tương ứng sang APPROVED hoặc REJECTED trong bảng TRANSACTIONS_LIVE → toàn bộ thay đổi được thực thi trong một **Database Transaction (COMMIT)** duy nhất để đảm bảo tính ACID → hệ thống ghi Audit Log gồm: ai quyết định, quyết định gì, lúc nào, ghi chú gì.
  * Nếu **không khớp** (có người khác thay đổi case trong lúc REVIEWER đang đọc): hệ thống trả về lỗi 409 Conflict, không thực hiện ghi đè, yêu cầu REVIEWER tải lại thông tin case mới nhất.

---

#### MANAGER

* *Xem Dashboard tổng quan*: MANAGER đăng nhập → chọn chức năng Dashboard → hệ thống truy vấn **Kho dữ liệu (Data Warehouse / OLAP)** để lấy số liệu tổng hợp theo ngày hiện tại hoặc ngày được chọn: tổng số giao dịch, tổng giá trị giao dịch, số giao dịch APPROVED / REJECTED / PENDING, số case MANUAL_REVIEW đang tồn đọng, tỉ lệ gian lận bị chặn, tỉ lệ tự động hóa (% giao dịch không cần người xem xét) → hệ thống hiển thị dữ liệu dạng thẻ số liệu (KPI Cards) và biểu đồ cột/đường theo thời gian → MANAGER có thể chọn khoảng thời gian (hôm nay, tuần này, tháng này) để lọc lại Dashboard. Lưu ý: toàn bộ dữ liệu Dashboard **chỉ đọc từ Warehouse**, không bao giờ query vào DB OLTP để tránh ảnh hưởng hiệu năng xử lý giao dịch.

* *Xem biểu đồ phân bố điểm gian lận*: MANAGER chọn chức năng Fraud Chart → hệ thống truy vấn FACT_TRANSACTIONS trong Warehouse → tổng hợp phân bố `fraud_score` theo dải giá trị (0.0–0.1, 0.1–0.2, …, 0.9–1.0) trong khoảng thời gian được chọn → hệ thống hiển thị biểu đồ histogram cho thấy bao nhiêu giao dịch rơi vào mỗi dải điểm → MANAGER dùng thông tin này để đánh giá hiệu quả mô hình AI (nếu quá nhiều giao dịch rơi vào vùng 0.3–0.7 thì mô hình đang không phân loại rõ ràng, cần tái huấn luyện).

* *Xem báo cáo giao dịch*: MANAGER chọn chức năng Reports → chọn loại báo cáo: Danh sách giao dịch → nhập điều kiện lọc: khoảng thời gian, trạng thái, kênh giao dịch (ATM/POS/ONLINE), mức fraud_score → hệ thống truy vấn Warehouse → hiển thị danh sách giao dịch thỏa điều kiện, phân trang, gồm: mã giao dịch, thời gian, khách hàng, số tiền, kênh, điểm gian lận, trạng thái → MANAGER có thể click vào từng giao dịch để xem chi tiết.

* *Xuất báo cáo (Export)*: MANAGER đang xem danh sách báo cáo → click nút "Xuất file" → chọn định dạng xuất (CSV hoặc PDF) → hệ thống gọi module `report_exporter` để sinh file với toàn bộ dữ liệu đang lọc (không giới hạn phân trang) → file được tải xuống trình duyệt của MANAGER → hệ thống ghi Audit Log ghi nhận sự kiện xuất báo cáo (ai, lúc nào, điều kiện lọc gì).

* *Xem Audit Log*: MANAGER chọn chức năng Audit Log → hệ thống hiển thị toàn bộ lịch sử hành động trong hệ thống được lưu trong bảng AUDIT_LOGS, gồm: thời gian, người thực hiện (actor), vai trò, hành động (action), đối tượng bị tác động (bảng nào, bản ghi nào), giá trị cũ và giá trị mới → MANAGER có thể lọc theo khoảng thời gian, theo actor, theo loại hành động, theo đối tượng bị tác động → MANAGER có thể xuất Audit Log ra file để phục vụ kiểm toán nội bộ hoặc báo cáo lên Ngân hàng Nhà nước.

* *Xem kết quả đối soát (Reconciliation)*: MANAGER chọn chức năng Reconciliation → hệ thống hiển thị danh sách các RECONCILIATION_JOB đã chạy, gồm: ngày chạy, trạng thái (MATCH / MISMATCH / FAILED), số lượng giao dịch đếm được từ 3 nguồn (OLTP / Data Lake / Warehouse), tổng giá trị từ 3 nguồn → MANAGER click vào một job để xem chi tiết: nếu MISMATCH, hệ thống hiển thị cụ thể nguồn nào lệch, lệch bao nhiêu bản ghi, lệch bao nhiêu giá trị → MANAGER chuyển thông tin này cho ADMIN để điều tra nguyên nhân.

---

#### ADMIN

* *Tạo tài khoản người dùng mới*: ADMIN đăng nhập → chọn chức năng Quản lý User → chọn Tạo mới → nhập thông tin người dùng mới: họ tên, email, tên đăng nhập, mật khẩu tạm thời, vai trò (OPERATOR / REVIEWER / MANAGER / ADMIN) → hệ thống kiểm tra tên đăng nhập chưa bị trùng → băm mật khẩu và lưu vào bảng USERS → gán vai trò vào bảng USER_ROLES → ghi Audit Log → thông báo thành công → người dùng mới có thể đăng nhập và được yêu cầu đổi mật khẩu ngay lần đầu.

* *Vô hiệu hóa tài khoản*: ADMIN chọn một tài khoản từ danh sách → click Vô hiệu hóa → hệ thống cập nhật trường `is_active = FALSE` trong bảng USERS → tài khoản không thể đăng nhập mới; các phiên đang chạy bị thu hồi token → hệ thống ghi Audit Log.

* *Xem danh sách snapshot Data Lake*: ADMIN chọn chức năng Data Lake → hệ thống gọi endpoint `GET /datalake/snapshots` → trả về danh sách các snapshot đã được nạp vào: ngày snapshot, loại (DAILY_TXN_SUMMARY / EXTERNAL_INGEST), số lượng bản ghi, tổng giá trị, trạng thái (ACTIVE / ARCHIVED) → ADMIN dùng thông tin này để xác nhận Data Lake đang có đủ dữ liệu trước khi kích hoạt ETL. ADMIN cũng có thể nạp thêm dữ liệu thô từ bên ngoài qua `POST /datalake/ingest`.

* *Kích hoạt ETL Pipeline*: ADMIN chọn chức năng ETL → nhập ngày mục tiêu cần xử lý (ví dụ: 2025-01-15) và loại job (mặc định: DAILY_SUMMARY) → click Kích hoạt → hệ thống gọi endpoint `POST /etl/run` → **Idempotency guard**: mỗi cặp (target_date, job_type) chỉ được chạy thành công 1 lần — nếu đã SUCCESS thì trả về 409 Conflict → ETL Pipeline bắt đầu chạy ngầm theo 3 giai đoạn:
  1. **Extract**: Đọc các file CSV/JSON thô từ Data Lake theo khoảng ngày đã chỉ định.
  2. **Transform**: Làm sạch dữ liệu (loại bỏ bản ghi thiếu trường quan trọng), chuẩn hóa định dạng, làm giàu dữ liệu (map tọa độ IP sang thông tin địa lý qua GeoIP), dựng cấu trúc Star Schema (phân tách thành Fact và các Dimension).
  3. **Load**: Chèn dữ liệu đã biến đổi vào Kho dữ liệu (FACT_TRANSACTIONS, cập nhật DIM_TIME, DIM_CUSTOMER, DIM_LOCATION nếu có bản ghi mới).

  Kết quả của job được ghi vào bảng ETL_JOB_LOGS (bao gồm: số bản ghi đọc được, số bản ghi nạp thành công, số bản ghi lỗi, thời gian bắt đầu/kết thúc, trạng thái) → ADMIN nhận thông báo hoàn thành.

* *Xem ETL Logs*: ADMIN chọn chức năng ETL Logs → hệ thống hiển thị danh sách các lần ETL đã chạy từ bảng ETL_JOB_LOGS, gồm: thời gian kích hoạt, khoảng ngày xử lý, người kích hoạt, số bản ghi extract/load/error, trạng thái (SUCCESS / PARTIAL / FAILED) → ADMIN click vào một job để xem chi tiết lỗi nếu có (ví dụ: file không đọc được, bản ghi thiếu trường bắt buộc, lỗi kết nối Warehouse).

* *Kích hoạt Reconciliation Job*: ADMIN chọn chức năng Reconciliation → nhập khoảng thời gian cần đối soát (period_start, period_end) và ngưỡng thời gian chờ (pending_timeout_minutes, mặc định 120 phút) → click Chạy đối soát → hệ thống gọi endpoint `POST /reconciliation/run` → Reconciliation Service thực hiện:
  1. Tìm tất cả giao dịch có trạng thái **PENDING** trong khoảng thời gian đã chỉ định.
  2. Kiểm tra thời gian chờ: giao dịch nào đã PENDING vượt quá `pending_timeout_minutes` → đánh dấu **PENDING_TIMEOUT** và ghi nhận vào danh sách discrepancy.
  3. Tổng hợp kết quả: số giao dịch đã kiểm tra, số giao dịch bình thường (matched), số giao dịch lệch (discrepancy).

  Kết quả ghi vào bảng RECONCILIATION_RUNS với trạng thái COMPLETED hoặc FAILED → ADMIN có thể xem chi tiết từng discrepancy item qua `GET /reconciliation/{run_id}` → ADMIN giải quyết các discrepancy bằng cách nhập ghi chú lý do qua `PATCH /reconciliation/{run_id}/resolve`.

---

***Bước 4: Thông tin các đối tượng cần xử lý, quản lý***:

**Nhóm đối tượng liên quan đến người dùng hệ thống:**

* **Tài khoản người dùng** (USER): mã người dùng (user_id), tên đăng nhập (username), mật khẩu đã băm (password_hash), họ và tên (full_name), địa chỉ email (email), trạng thái hoạt động (is_active), thời điểm tạo (created_at)
* **Vai trò** (ROLE): mã vai trò (role_id), tên vai trò (role_name) — nhận một trong các giá trị: OPERATOR, REVIEWER, MANAGER, ADMIN
* **Phân quyền người dùng – vai trò** (USER_ROLE): mã người dùng (user_id), mã vai trò (role_id) — bảng trung gian thể hiện quan hệ nhiều-nhiều

**Nhóm đối tượng liên quan đến khách hàng:**

* **Khách hàng** (CUSTOMER): mã khách hàng (customer_id), họ và tên (full_name), ngày sinh (date_of_birth), địa chỉ (address), số điện thoại (phone), địa chỉ email (email), điểm tín dụng (credit_score), thời điểm tạo hồ sơ (created_at)

**Nhóm đối tượng liên quan đến giao dịch:**

* **Giao dịch** (TRANSACTION_LIVE): mã giao dịch (txn_id), mã khách hàng (customer_id), số tiền (amount), loại tiền tệ (currency), tên đơn vị thụ hưởng (merchant_name), kênh giao dịch (channel) — ATM / POS / ONLINE, số thẻ đã che (masked_card_number), điểm gian lận (fraud_score), trạng thái (status) — PENDING / APPROVED / REJECTED / MANUAL_REVIEW, mã người nộp (submitted_by), thời điểm tạo (created_at)
* **Khóa lũy đẳng giao dịch** (TXN_IDEMPOTENCY): khóa lũy đẳng (idem_key), mã giao dịch liên kết (txn_id), bản snapshot kết quả (response_snapshot), thời điểm tạo (created_at)
* **Lịch sử trạng thái giao dịch** (TXN_STATE): mã giao dịch (txn_id), trạng thái hiện tại (current_state), trạng thái trước đó (previous_state), thời điểm thay đổi (changed_at)

**Nhóm đối tượng liên quan đến hồ sơ vay vốn:**

* **Đơn vay** (LOAN_APPLICATION): mã đơn vay (loan_id), mã khách hàng (customer_id), người nộp (submitted_by), người duyệt (reviewed_by), số tiền vay (principal_amount), loại tiền tệ (currency_code), lãi suất (interest_rate — dạng thập phân, ví dụ 0.12 = 12%), kỳ hạn tháng (term_months), mục đích vay (purpose), trạng thái (status) — PENDING / APPROVED / REJECTED / DISBURSED / CLOSED / DEFAULTED, số phiên bản chống ghi đè (version), điểm xác suất vỡ nợ (pd_score), mức độ rủi ro (risk_level) — LOW RISK / MEDIUM RISK / HIGH RISK, số tiền trả hàng tháng (monthly_payment), số dư còn lại (outstanding_balance), ngày giải ngân (disbursed_at), ngày đáo hạn (maturity_date), ghi chú duyệt (review_note), thời điểm duyệt (reviewed_at), thời điểm tạo (created_at)
  * *Tính điểm PD (Probability of Default) tại thời điểm nộp đơn* nếu đủ các trường AI: person_age, person_income, person_home_ownership, person_emp_length, loan_intent, loan_grade, cb_person_default_on_file, cb_person_cred_hist_length. Ngưỡng phân loại: pd < 0.20 → LOW RISK, 0.20 ≤ pd < 0.50 → MEDIUM RISK, pd ≥ 0.50 → HIGH RISK.

**Nhóm đối tượng liên quan đến xét duyệt thủ công:**

* **Hồ sơ xét duyệt** (REVIEW_CASE): mã case (case_id), mã giao dịch liên quan (txn_id), trạng thái case (case_status) — OPEN / ASSIGNED / APPROVED / REJECTED / CLOSED, mã Reviewer được gán (assigned_to), quyết định (decision) — APPROVE / REJECT, ghi chú quyết định (decision_note), số phiên bản chống ghi đè (version), thời điểm tạo case (created_at), thời điểm ra quyết định (decided_at)

**Nhóm đối tượng liên quan đến kiểm toán:**

* **Nhật ký kiểm toán** (AUDIT_LOG): mã log (log_id), mã người thực hiện (actor_id), vai trò người thực hiện (actor_role), loại hành động (action), bảng bị tác động (target_table), mã bản ghi bị tác động (target_id), giá trị trước thay đổi (old_value), giá trị sau thay đổi (new_value), địa chỉ IP (ip_address), thời điểm ghi log (created_at)

**Nhóm đối tượng liên quan đến ETL và Đối soát:**

* **Nhật ký ETL** (ETL_JOB_LOG): mã job (job_id), người kích hoạt (triggered_by), khoảng ngày xử lý (date_range), số bản ghi đọc được (records_extracted), số bản ghi nạp thành công (records_loaded), số bản ghi lỗi (records_failed), trạng thái (status) — SUCCESS / PARTIAL / FAILED, chi tiết lỗi (error_detail), thời điểm bắt đầu (started_at), thời điểm kết thúc (finished_at)
* **Công việc đối soát** (RECONCILIATION_JOB): mã job (job_id), ngày đối soát (run_date), số bản ghi từ OLTP (oltp_count), tổng giá trị từ OLTP (oltp_sum), số bản ghi từ Data Lake (lake_count), tổng giá trị từ Data Lake (lake_sum), số bản ghi từ Warehouse (warehouse_count), tổng giá trị từ Warehouse (warehouse_sum), trạng thái (status) — MATCH / MISMATCH / FAILED, chi tiết lệch (mismatch_detail), người kích hoạt (run_by), thời điểm chạy (created_at)

**Nhóm đối tượng OLAP — Kho dữ liệu thống kê (Data Warehouse):**

* **Bảng sự kiện giao dịch** (FACT_TRANSACTION): mã sự kiện (fact_id), mã giao dịch gốc (txn_id), khóa chiều thời gian (time_key), khóa chiều khách hàng (customer_key), khóa chiều địa lý (location_key), số tiền (amount), điểm gian lận (fraud_score), trạng thái (status), kênh giao dịch (channel)
* **Chiều thời gian** (DIM_TIME): khóa thời gian (time_key), ngày đầy đủ (full_date), năm (year), quý (quarter), tháng (month), ngày trong tháng (day), ngày trong tuần (day_of_week)
* **Chiều khách hàng** (DIM_CUSTOMER): khóa khách hàng (customer_key), mã khách hàng gốc (customer_id), họ và tên (full_name), điểm tín dụng (credit_score), phân khúc rủi ro (risk_segment)
* **Chiều địa lý** (DIM_LOCATION): khóa địa lý (location_key), quốc gia (country), thành phố (city), khu vực (region), loại merchant (merchant_category)

---

***Bước 5: Quan hệ giữa các đối tượng, thông tin***:

**Nhóm người dùng – vai trò:**

* Một USER có thể được gán **nhiều ROLE** khác nhau (quan hệ nhiều–nhiều thông qua bảng trung gian USER_ROLE). Một ROLE (OPERATOR / REVIEWER / MANAGER / ADMIN) có thể được gán cho nhiều USER khác nhau. ADMIN có thể cấp thêm hoặc thu hồi ROLE của USER bất kỳ lúc nào — thay đổi có hiệu lực ngay với token mới sau đăng nhập lại.

**Nhóm khách hàng – giao dịch:**

* Một CUSTOMER có thể có nhiều TRANSACTION_LIVE (lịch sử giao dịch nhiều lần). Một TRANSACTION_LIVE chỉ thuộc về đúng một CUSTOMER.
* Một CUSTOMER có thể có nhiều LOAN_APPLICATION (đã nộp hồ sơ vay nhiều lần). Một LOAN_APPLICATION chỉ thuộc về đúng một CUSTOMER.

**Nhóm giao dịch – kiểm soát trùng lặp:**

* Một TRANSACTION_LIVE có đúng một TXN_IDEMPOTENCY tương ứng (quan hệ 1–1). TXN_IDEMPOTENCY sinh ra trước và được kiểm tra ngay khi nhận request; nếu đã tồn tại thì TRANSACTION_LIVE không được tạo thêm.
* Một TRANSACTION_LIVE có thể có nhiều bản ghi lịch sử trong TXN_STATE (mỗi lần đổi trạng thái thêm một bản ghi). Tuy nhiên, mỗi giao dịch chỉ có đúng một trạng thái hiện hành tại một thời điểm.

**Nhóm giao dịch – xét duyệt thủ công:**

* Một TRANSACTION_LIVE có thể tạo ra tối đa một REVIEW_CASE (chỉ xảy ra khi fraud_score nằm trong vùng 0.3–0.7 hoặc số tiền vượt ngưỡng). Giao dịch có điểm thấp (APPROVED) hoặc cao (REJECTED) không tạo case. Quan hệ 1–0..1.
* Một REVIEW_CASE tại một thời điểm được gán cho tối đa một REVIEWER (USER có role REVIEWER). Một REVIEWER có thể xử lý nhiều REVIEW_CASE theo thời gian (quan hệ nhiều-1 từ REVIEW_CASE đến USER).

**Nhóm đơn vay – điểm rủi ro:**

* Một LOAN_APPLICATION có thể có nhiều LOAN_RISK_SCORE (mỗi lần hệ thống tái chấm điểm hoặc dùng mô hình khác nhau sẽ tạo thêm một bản ghi). Tuy nhiên điểm có hiệu lực là bản ghi mới nhất. Quan hệ 1–nhiều.

**Nhóm kiểm toán:**

* Mọi thay đổi trạng thái của TRANSACTION_LIVE, REVIEW_CASE, LOAN_APPLICATION đều tạo ra một hoặc nhiều bản ghi AUDIT_LOG. Một AUDIT_LOG chỉ ghi nhận một sự kiện tại một thời điểm. Quan hệ: mọi đối tượng nghiệp vụ → nhiều AUDIT_LOG (1–nhiều, ghi bởi Trigger hoặc Service).
* Một USER (actor) có thể là tác nhân của nhiều AUDIT_LOG theo thời gian.

**Nhóm ETL – Warehouse:**

* Một lần chạy ETL (ETL_JOB_LOG) nạp nhiều bản ghi vào FACT_TRANSACTION (quan hệ 1–nhiều).
* Một FACT_TRANSACTION liên kết với đúng một DIM_TIME (thời điểm xảy ra), đúng một DIM_CUSTOMER (khách hàng liên quan), và đúng một DIM_LOCATION (địa lý/merchant liên quan). Đây là cấu trúc **Star Schema** trong Data Warehouse.
* Một DIM_TIME có thể liên kết với nhiều FACT_TRANSACTION (tất cả giao dịch trong cùng một ngày dùng chung một bản ghi DIM_TIME). Quan hệ 1–nhiều.
* Một DIM_CUSTOMER có thể liên kết với nhiều FACT_TRANSACTION (mọi giao dịch của cùng một khách hàng qua thời gian). Quan hệ 1–nhiều.
* Một DIM_LOCATION có thể liên kết với nhiều FACT_TRANSACTION (nhiều giao dịch tại cùng merchant/địa lý). Quan hệ 1–nhiều.

**Nhóm đối soát:**

* Một RECONCILIATION_JOB so sánh dữ liệu từ 3 nguồn độc lập (TRANSACTIONS_LIVE trong OLTP, file raw log trong Data Lake, FACT_TRANSACTIONS trong Warehouse) cho một ngày duy nhất. Một ngày có thể có nhiều RECONCILIATION_JOB nếu ADMIN chạy lại sau khi điều tra và sửa lỗi.


