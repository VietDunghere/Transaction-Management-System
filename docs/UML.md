# UML Use Case – Hệ thống Phân tích Rủi ro và Đánh giá Tài chính (HPTRRĐGTC)

> Tài liệu này mô tả biểu đồ use case **tổng quan** và **chi tiết** cho hệ thống HPTRRĐGTC, xây dựng theo phương pháp luận UML chuẩn: xác định actor → xác định use case → mịn hóa → phân rã chi tiết.

---

## Mục lục

1. [Biểu đồ Use Case Tổng quan](#1-biểu-đồ-use-case-tổng-quan)
   - [1.1 Xác định Actor](#11-xác-định-actor)
   - [1.2 Xác định Use Case](#12-xác-định-use-case)
   - [1.3 Mịn hóa Use Case](#13-mịn-hóa-use-case)
   - [1.4 Mô tả Actor và Use Case](#14-mô-tả-actor-và-use-case)
2. [Biểu đồ Use Case Chi tiết](#2-biểu-đồ-use-case-chi-tiết)
   - [UC01 – Xác thực & Quản lý Phiên](#uc01--xác-thực--quản-lý-phiên-làm-việc)
   - [UC02 – Quản lý Giao dịch](#uc02--quản-lý-giao-dịch)
   - [UC03 – Hỗ trợ Quyết định Cho vay](#uc03--quản-lý-đơn-vay)
   - [UC04 – Xét duyệt Thủ công](#uc04--xét-duyệt-thủ-công)
   - [UC05 – Giám sát & Báo cáo](#uc05--giám-sát--báo-cáo)
   - [UC06 – Quản trị Hệ thống](#uc06--quản-trị-hệ-thống)
   - [UC07 – Data Engineering & Đối soát](#uc07--data-engineering--đối-soát-dữ-liệu)
   - [UC08 – Analyst Module](#uc08--analyst-module)
3. [Ghi chú Tổng quát](#3-ghi-chú-tổng-quát)

---

## 1. Biểu đồ Use Case Tổng quan

### 1.1 Xác định Actor

Dựa trên phạm vi hệ thống HPTRRĐGTC, các actor được xác định như sau:

**Actor trừu tượng (Abstract Actor):**

- **Thành viên hệ thống**: Bất kỳ tài khoản nào đã được cấp quyền vào hệ thống HPTRRĐGTC. Đây là actor cha trừu tượng vì mọi nhóm người dùng đều chia sẻ các chức năng xác thực chung (đăng nhập, đăng xuất, đổi mật khẩu).

**Actor cụ thể (kế thừa từ Thành viên hệ thống):**

- **OPERATOR** (Core Banking System của Ngân hàng đối tác): Hệ thống tự động của ngân hàng đối tác — nộp giao dịch và đơn vay vào HPTRRĐGTC qua API. Không phải nhân viên con người; không có quyền truy cập giao diện quản trị.
- **REVIEWER** (Nhân viên duyệt hồ sơ): Nhân viên tiếp nhận và xét duyệt thủ công các case giao dịch đáng ngờ do hệ thống chuyển sang.
- **ANALYST** (Chuyên viên phân tích rủi ro): Chuyên gia vận hành mô hình AI — điều chỉnh ngưỡng phân loại, phân tích hiệu suất mô hình Fraud/PD Score, quản lý suppression rules và tạo báo cáo phân tích chuyên sâu.
- **MANAGER** (Quản lý): Người giám sát hoạt động hệ thống, theo dõi dashboard, báo cáo, audit log và phê duyệt / từ chối hồ sơ vay.
- **ADMIN** (Quản trị hệ thống): Kỹ thuật viên quản trị tài khoản người dùng, vận hành ETL pipeline và theo dõi tính nhất quán dữ liệu.

**Quan hệ kế thừa giữa actor:**

OPERATOR, REVIEWER, ANALYST, MANAGER, ADMIN đều **kế thừa (generalization)** từ **Thành viên hệ thống**, vì tất cả đều được thực hiện ba chức năng chung: Đăng nhập, Đăng xuất, Đổi mật khẩu cá nhân.

```
        ┌──────────────────────────┐
        │   Thành viên hệ thống    │  ← Actor trừu tượng
        └──────────────────────────┘
          ▲    ▲    ▲      ▲    ▲
          │    │    │      │    │  (generalization)
     ┌────┘  ┌─┘  ┌─┘    ┌┘   └──────┐
     │       │    │      │            │
 OPERATOR REVIEWER ANALYST MANAGER  ADMIN
```

---

### 1.2 Xác định Use Case

Với mỗi chức năng người dùng **trực tiếp thao tác**, đề xuất một use case tương ứng. Các xử lý tự động của hệ thống (chấm điểm AI, ghi Audit Log, phân luồng...) không phải use case.

| STT | Use Case | Actor |
|-----|----------|-------|
| UC01.1 | Đăng nhập | Thành viên hệ thống |
| UC01.2 | Đăng xuất | Thành viên hệ thống |
| UC01.3 | Đổi mật khẩu cá nhân | Thành viên hệ thống |
| UC02.1 | Nộp giao dịch mới | OPERATOR |
| UC02.2 | Xem danh sách giao dịch | REVIEWER, ANALYST |
| UC02.3 | Xem chi tiết giao dịch | REVIEWER, ANALYST |
| UC03.1 | Nộp hồ sơ đề nghị vay vốn | OPERATOR |
| UC03.2 | Mô phỏng chấm điểm rủi ro vay (Simulate) | OPERATOR, REVIEWER |
| UC03.3 | Xem danh sách hồ sơ vay | OPERATOR, REVIEWER |
| UC03.4 | Xem chi tiết hồ sơ vay | OPERATOR, REVIEWER |
| UC03.5 | Phê duyệt / Từ chối hồ sơ vay | REVIEWER |
| UC04.1 | Xem danh sách case chờ xử lý | REVIEWER, MANAGER |
| UC04.2 | Nhận case (Assign) | REVIEWER |
| UC04.3 | Xem chi tiết case | REVIEWER, MANAGER |
| UC04.4 | Ra quyết định Phê duyệt / Từ chối | REVIEWER, MANAGER |
| UC05.1 | Xem Dashboard tổng quan | MANAGER |
| UC05.2 | Xem biểu đồ phân bố Fraud Score | ANALYST, MANAGER |
| UC05.3 | Xem báo cáo giao dịch | MANAGER |
| UC05.4 | Xuất báo cáo (CSV / PDF) | MANAGER |
| UC05.5 | Xem Audit Log hệ thống | MANAGER, ADMIN |
| UC05.6 | Truy vết lịch sử một giao dịch cụ thể | MANAGER, ADMIN |
| UC05.7 | Xem kết quả đối soát (Reconciliation) | ANALYST, ADMIN |
| UC06.1 | Tạo tài khoản người dùng mới | ADMIN |
| UC06.2 | Vô hiệu hóa tài khoản | ADMIN |
| UC06.3 | Kích hoạt lại tài khoản | ADMIN |
| UC06.4 | Gán / Thay đổi vai trò người dùng | ADMIN |
| UC06.5 | Xem danh sách người dùng | MANAGER, ADMIN |
| UC06.6 | Xem chi tiết thông tin người dùng | MANAGER, ADMIN |
| UC07.1 | Xem cấu trúc Data Lake | ADMIN |
| UC07.2 | Kích hoạt ETL Pipeline | ADMIN |
| UC07.3 | Xem ETL Logs | ADMIN |
| UC07.4 | Xem chi tiết một ETL Job | ADMIN |
| UC07.5 | Kích hoạt Reconciliation Job | ADMIN |
| UC07.6 | Xem danh sách Reconciliation Jobs | ANALYST, ADMIN |
| UC07.7 | Xem chi tiết Reconciliation Job | ANALYST, ADMIN |
| UC08.1 | Xem ngưỡng phân loại hiện hành | ANALYST |
| UC08.2 | Cập nhật ngưỡng Fraud Score | ANALYST |
| UC08.3 | Cập nhật ngưỡng PD Score | ANALYST |
| UC08.4 | Xem hiệu suất mô hình Fraud | ANALYST |
| UC08.5 | Xem hiệu suất mô hình PD Score | ANALYST |
| UC08.6 | Xem danh sách Suppression Rules | ANALYST |
| UC08.7 | Tạo Suppression Rule mới | ANALYST |
| UC08.8 | Vô hiệu hóa Suppression Rule | ANALYST |
| UC08.9 | Tạo báo cáo phân tích | ANALYST |
| UC08.10 | Xem danh sách báo cáo phân tích | ANALYST, MANAGER |
| UC08.11 | Xem chi tiết và tải PDF báo cáo | ANALYST, MANAGER |
| UC08.12 | Xác nhận (Acknowledge) báo cáo | MANAGER |
| UC08.13 | Xuất dữ liệu phân tích (Export for Analysis) | ANALYST |

---

### 1.3 Mịn hóa Use Case

> Theo phương pháp luận: nếu có ít nhất 2 use case **thao tác giống nhau**, xem xét gộp lại thành 1. Nếu gộp gây nhầm lẫn về actor (vì mỗi UC liên quan đến nhóm actor khác nhau), dùng **UC trừu tượng làm cha** và các UC cụ thể kế thừa từ đó.

---

#### Nhóm 1 — Cặp "Xem danh sách" và "Xem chi tiết" (6 cặp)

Trong hệ thống HPTRRĐGTC, 6 cặp UC sau đây có **thao tác giống nhau**: người dùng browse danh sách → tùy chọn click một dòng để xem chi tiết.

| Cặp | "Xem danh sách" | "Xem chi tiết" |
|-----|-----------------|----------------|
| 1 | UC02.2 – Xem danh sách giao dịch | UC02.3 – Xem chi tiết giao dịch |
| 2 | UC03.3 – Xem danh sách hồ sơ vay | UC03.4 – Xem chi tiết hồ sơ vay |
| 3 | UC04.1 – Xem danh sách case chờ xử lý | UC04.3 – Xem chi tiết case |
| 4 | UC06.5 – Xem danh sách người dùng | UC06.6 – Xem chi tiết thông tin người dùng |
| 5 | UC07.3 – Xem ETL Logs | UC07.4 – Xem chi tiết một ETL Job |
| 6 | UC07.6 – Xem danh sách Reconciliation Jobs | UC07.7 – Xem chi tiết Reconciliation Job |

**Phân tích — có thể gộp không?**

Xét gộp nhóm "Xem danh sách": 6 UC này trông giống nhau về thao tác (duyệt danh sách, phân trang), nhưng **actor khác nhau** (UC02.2 có 5 actor; UC07.3 chỉ có ADMIN), và **đối tượng dữ liệu khác nhau** hoàn toàn (giao dịch ≠ hồ sơ vay ≠ case ≠ người dùng ≠ ETL Job ≠ Recon Job). Nếu gộp thành một UC trừu tượng chung sẽ không phản ánh đúng ngữ nghĩa nghiệp vụ và gây nhầm lẫn về phạm vi quyền truy cập.

Xét gộp nhóm "Xem chi tiết": Tương tự — đối tượng khác nhau, actor khác nhau, màn hình hiển thị khác nhau.

**Quyết định: Giữ nguyên 12 UC riêng biệt.** Xác định quan hệ giữa từng cặp là **<<extend>>**: mỗi "Xem chi tiết" là mở rộng **có điều kiện** từ "Xem danh sách" tương ứng — chỉ xảy ra khi người dùng chủ động click vào một dòng cụ thể trong danh sách.

**Quan hệ sau mịn hóa (tất cả 6 cặp):**

| UC con (<<extend>>) | Extend từ | Điều kiện kích hoạt |
|---------------------|-----------|---------------------|
| UC02.3 Xem chi tiết giao dịch | UC02.2 Xem danh sách giao dịch | Người dùng click vào một dòng giao dịch |
| UC03.4 Xem chi tiết hồ sơ vay | UC03.3 Xem danh sách hồ sơ vay | Người dùng click vào một dòng hồ sơ vay |
| UC04.3 Xem chi tiết case | UC04.1 Xem danh sách case | Người dùng click vào một dòng case |
| UC06.6 Xem chi tiết thông tin người dùng | UC06.5 Xem danh sách người dùng | Người dùng click vào tên một tài khoản |
| UC07.4 Xem chi tiết một ETL Job | UC07.3 Xem ETL Logs | ADMIN click vào một dòng kết quả ETL |
| UC07.7 Xem chi tiết Reconciliation Job | UC07.6 Xem danh sách Reconciliation Jobs | ADMIN click vào một dòng kết quả đối soát |

---

#### Nhóm 2 — "Xem danh sách" có thao tác "Lọc" đi kèm

Ở mỗi màn hình danh sách, người dùng **có thể** áp dụng bộ lọc — nhưng không bắt buộc. Đây là thao tác tùy chọn, áp dụng cho 5 màn hình danh sách:

| "Xem danh sách" | Thao tác "Lọc" tương ứng |
|-----------------|--------------------------|
| UC02.2 Xem danh sách giao dịch | Lọc theo trạng thái, kênh, khoảng fraud_score, thời gian |
| UC03.3 Xem danh sách hồ sơ vay | Lọc theo trạng thái, mức rủi ro (LOW/MEDIUM/HIGH), thời gian |
| UC04.1 Xem danh sách case | Lọc theo khoảng fraud_score, sắp xếp theo thời gian chờ |
| UC06.5 Xem danh sách người dùng | Lọc theo vai trò, trạng thái tài khoản |
| UC05.5 Xem Audit Log hệ thống | Lọc theo actor, loại hành động, thời gian |

**Phân tích — có thể gộp không?**

Thao tác "Lọc" của mỗi màn hình có **tiêu chí lọc khác nhau** (fraud_score vs mức rủi ro vs vai trò vs loại hành động). Tạo một UC trừu tượng "Lọc danh sách" chung sẽ quá mờ nhạt và không phản ánh điều kiện lọc cụ thể.

**Quyết định: Không tạo UC trừu tượng chung.** Mỗi thao tác "Lọc" là UC con riêng trong sơ đồ chi tiết của nhóm UC tương ứng, với quan hệ **<<extend>>** từ "Xem danh sách" cha. Không xuất hiện ở sơ đồ tổng quan.

---

#### Nhóm 3 — UC06.2 "Vô hiệu hóa tài khoản" và UC06.3 "Kích hoạt lại tài khoản"

Cả hai UC cùng: actor ADMIN, cùng đối tượng (tài khoản người dùng), cùng thay đổi một trường duy nhất (`is_active`), chỉ khác hướng (FALSE ↔ TRUE).

**Phân tích:** Đây là hai dạng cụ thể của cùng một thao tác nghiệp vụ. Chúng **thực sự trùng nhau** ở mức thao tác (chọn tài khoản → xác nhận thay đổi trạng thái). Actor giống nhau hoàn toàn (ADMIN) nên không cần dùng UC trừu tượng để phân biệt actor — nhưng vẫn nên dùng UC trừu tượng để mô hình hóa điểm chung và làm rõ cấu trúc.

**Quyết định: Tạo UC trừu tượng "Thay đổi trạng thái tài khoản"** làm cha chung. UC06.2 và UC06.3 kế thừa từ cha này qua quan hệ **generalization** (chuyên biệt hóa).

```
              ┌─────────────────────────────────┐
              │  Thay đổi trạng thái tài khoản  │  ← UC trừu tượng
              └─────────────────────────────────┘
                       ▲              ▲
                       │              │  (generalization)
         ┌─────────────┘              └──────────────┐
         │                                           │
  UC06.2 Vô hiệu hóa tài khoản    UC06.3 Kích hoạt lại tài khoản
  (is_active = FALSE)              (is_active = TRUE)
```

**Quan hệ đầy đủ:**
- ADMIN — Association → **Thay đổi trạng thái tài khoản** (UC trừu tượng)
- **Vô hiệu hóa tài khoản** — generalization → Thay đổi trạng thái tài khoản
- **Kích hoạt lại tài khoản** — generalization → Thay đổi trạng thái tài khoản

---

#### Nhóm 4 — UC07.2 "Kích hoạt ETL Pipeline" và UC07.5 "Kích hoạt Reconciliation Job"

Cả hai UC cùng: actor ADMIN, cùng thao tác (chọn khoảng ngày → xác nhận → hệ thống chạy job ngầm).

**Phân tích:** Quy trình tương tác giống nhau, nhưng **ngữ nghĩa nghiệp vụ khác nhau hoàn toàn**:
- ETL: đọc Data Lake → biến đổi → nạp vào Warehouse
- Reconciliation: tìm giao dịch PENDING vượt quá timeout → đánh dấu PENDING_TIMEOUT → ghi discrepancy items

Ngoài ra, actor xem kết quả khác nhau: ETL Logs chỉ ADMIN xem; Reconciliation Jobs cả ADMIN và MANAGER xem. Nếu gộp thành UC trừu tượng chung, sẽ nhầm lẫn về phạm vi kết quả và gây hiểu sai về quyền truy cập.

**Quyết định: Giữ nguyên 2 UC riêng biệt.** Ghi nhận sự tương đồng về luồng thao tác nhưng không gộp vì ngữ nghĩa nghiệp vụ và kết quả khác nhau.

---

#### Nhóm 5 — UC05.4 "Xuất báo cáo" phụ thuộc bắt buộc vào UC05.3 "Xem báo cáo giao dịch"

**Phân tích:** Người dùng **phải đang ở màn hình báo cáo** (UC05.3) thì nút "Xuất file" mới xuất hiện và có thể bấm. Không thể xuất báo cáo nếu chưa tra cứu và hiển thị dữ liệu báo cáo. Đây là quan hệ **bắt buộc, không có ngoại lệ**.

**Quyết định: UC05.4 Xuất báo cáo `<<include>>` UC05.3 Xem báo cáo giao dịch.**

---

#### Nhóm 6 — UC05.2 "Xem biểu đồ phân bố Fraud Score" trong mối quan hệ với UC05.1 "Xem Dashboard"

**Phân tích:** Biểu đồ phân bố Fraud Score là một panel phân tích chuyên sâu, không phải KPI card mặc định của Dashboard. Người dùng phải vào đúng tab/màn hình "Fraud Analysis" mới thấy — không phải lúc nào vào Dashboard cũng nhìn thấy biểu đồ này. Đây là tùy chọn người dùng chủ động chọn.

**Quyết định: UC05.2 `<<extend>>` UC05.1** — biểu đồ phân bố fraud score là mở rộng có điều kiện từ trang Dashboard tổng quan, chỉ tải khi người dùng chuyển sang tab phân tích.

---

#### Nhóm 7 — UC02.1 "Nộp giao dịch mới" và UC03.1 "Nộp hồ sơ đề nghị vay vốn"

Cả hai UC cùng thao tác tổng quát là "điền form → xác nhận → nhận kết quả AI". Actor của cả hai UC02.1 và UC03.1 đều là **OPERATOR** (Core Banking System của ngân hàng đối tác).

**Phân tích:** Dù quy trình bề ngoài giống nhau, hai UC này:
- Có **đối tượng dữ liệu khác nhau** hoàn toàn (transaction vs loan application)
- Có **output khác nhau** (fraud_score + APPROVED/REJECTED/MANUAL_REVIEW vs PD Score + PENDING chờ duyệt)
- Dẫn đến **luồng nghiệp vụ khác nhau** (fraud routing tức thì vs loan workflow PENDING → MANAGER review)

Tạo UC trừu tượng "Nộp dữ liệu vào hệ thống" sẽ không có giá trị ngữ nghĩa và gây hiểu nhầm.

**Quyết định: Giữ nguyên 2 UC riêng biệt.**

---

#### Nhóm 8 — UC03.5 "Phê duyệt / Từ chối hồ sơ vay" và UC04.4 "Ra quyết định Phê duyệt / Từ chối" (case)

Cả hai UC cùng thao tác "chọn APPROVE/REJECT → nhập ghi chú → xác nhận", cùng actor MANAGER, ADMIN.

**Phân tích:**
- **Đối tượng khác nhau**: UC03.5 tác động lên Loan Application; UC04.4 tác động lên ReviewCase + Transaction
- **Ràng buộc khác nhau**: UC03.5 có SoD check (submitter ≠ approver); UC04.4 có ASSIGNED status check + ownership check cho REVIEWER
- **Optimistic lock**: cả hai đều dùng `version` nhưng trên object khác nhau

Gộp thành UC trừu tượng chung sẽ che giấu ràng buộc nghiệp vụ quan trọng của từng UC.

**Quyết định: Giữ nguyên 2 UC riêng biệt.**

---

#### Nhóm 9 — UC08 Analyst Module: Ngưỡng và Hiệu suất Mô hình

Trong UC08, có hai nhóm UC có thao tác "Xem + Cập nhật" trên cùng loại đối tượng:
- UC08.1 / UC08.2 / UC08.3 (ngưỡng Fraud và PD Score)
- UC08.4 / UC08.5 (hiệu suất mô hình Fraud và PD Score)

**Phân tích nhóm ngưỡng (UC08.1–08.3):** UC08.1 là UC xem chung cho cả hai loại ngưỡng, UC08.2/08.3 là các UC cập nhật chuyên biệt. Actor của UC08.1 rộng hơn (ANALYST) so với UC08.2/08.3 (chỉ ANALYST). Không gộp vì ngữ nghĩa khác nhau: xem là read-only cho nhiều role; cập nhật là write chỉ dành cho chuyên viên.

**Quyết định cho UC08.2/08.3:** UC08.2 `<<include>>` UC08.1 và UC08.3 `<<include>>` UC08.1 — bắt buộc xem giá trị hiện tại trước khi cập nhật.

**Phân tích nhóm hiệu suất (UC08.4–08.5):** Hai UC này cùng thao tác (xem metrics), actor như nhau, nhưng đối tượng dữ liệu hoàn toàn khác (Fraud model vs Loan PD model). Không gộp để tránh nhầm lẫn về scope metric.

**Quyết định: Giữ nguyên cấu trúc 12 UC trong UC08.**

---

#### Tổng hợp sau mịn hóa — Bảng toàn bộ quan hệ UC trong sơ đồ tổng quan

| UC | Tên Use Case | Actor | Quan hệ với UC khác |
|----|-------------|-------|---------------------|
| UC01.1 | Đăng nhập | Thành viên hệ thống | — |
| UC01.2 | Đăng xuất | Thành viên hệ thống | — |
| UC01.3 | Đổi mật khẩu cá nhân | Thành viên hệ thống | — |
| UC02.1 | Nộp giao dịch mới | OPERATOR | — |
| UC02.2 | Xem danh sách giao dịch | REVIEWER, ANALYST | UC02.3 <<extend>> UC02.2 |
| UC02.3 | Xem chi tiết giao dịch | REVIEWER, ANALYST | <<extend>> UC02.2 |
| UC03.1 | Nộp hồ sơ đề nghị vay vốn | OPERATOR | — |
| UC03.2 | Mô phỏng chấm điểm rủi ro vay (Simulate) | OPERATOR, REVIEWER | — |
| UC03.3 | Xem danh sách hồ sơ vay | OPERATOR, REVIEWER | UC03.4 <<extend>> UC03.3 |
| UC03.4 | Xem chi tiết hồ sơ vay | OPERATOR, REVIEWER | <<extend>> UC03.3 |
| UC03.5 | Phê duyệt / Từ chối hồ sơ vay | REVIEWER | — |
| UC04.1 | Xem danh sách case chờ xử lý | REVIEWER, MANAGER | UC04.3 <<extend>> UC04.1 |
| UC04.2 | Nhận case (Assign) | REVIEWER | — |
| UC04.3 | Xem chi tiết case | REVIEWER, MANAGER | <<extend>> UC04.1 |
| UC04.4 | Ra quyết định Phê duyệt / Từ chối | REVIEWER, MANAGER | — |
| UC05.1 | Xem Dashboard tổng quan | ANALYST, MANAGER | UC05.2 <<extend>> UC05.1 |
| UC05.2 | Xem biểu đồ xu hướng Fraud (fraud-trend) | ANALYST, MANAGER | <<extend>> UC05.1 |
| UC05.3 | Xem báo cáo giao dịch | MANAGER | UC05.4 <<include>> UC05.3 |
| UC05.4 | Xuất báo cáo (CSV / JSON) | MANAGER | <<include>> UC05.3 |
| UC05.5 | Xem Audit Log hệ thống | MANAGER, ADMIN | UC05.6 <<extend>> UC05.5 |
| UC05.6 | Truy vết lịch sử một giao dịch cụ thể | MANAGER, ADMIN | <<extend>> UC05.5 |
| UC05.7 | Xem kết quả đối soát (Reconciliation) | ANALYST, ADMIN | — |

| UC06.1 | Tạo tài khoản người dùng mới | ADMIN | — |
| UC06.A | Thay đổi trạng thái tài khoản *(trừu tượng)* | ADMIN | UC06.2, UC06.3 generalization → UC06.A |
| UC06.2 | Vô hiệu hóa tài khoản | ADMIN | generalization → UC06.A |
| UC06.3 | Kích hoạt lại tài khoản | ADMIN | generalization → UC06.A |
| UC06.4 | Gán / Thay đổi vai trò người dùng | ADMIN | — |
| UC06.5 | Xem danh sách người dùng | MANAGER, ADMIN | UC06.6 <<extend>> UC06.5 |
| UC06.6 | Xem chi tiết thông tin người dùng | MANAGER, ADMIN | <<extend>> UC06.5 |
| UC07.1 | Xem cấu trúc Data Lake | ADMIN | — |
| UC07.2 | Kích hoạt ETL Pipeline | ADMIN | — |
| UC07.3 | Xem ETL Logs | ADMIN | UC07.4 <<extend>> UC07.3 |
| UC07.4 | Xem chi tiết một ETL Job | ADMIN | <<extend>> UC07.3 |
| UC07.5 | Kích hoạt Reconciliation Job | ADMIN | — |
| UC07.6 | Xem danh sách Reconciliation Jobs | ANALYST, ADMIN | UC07.7 <<extend>> UC07.6 |
| UC07.7 | Xem chi tiết Reconciliation Job | ANALYST, ADMIN | <<extend>> UC07.6 |

| UC08.1 | Xem ngưỡng phân loại hiện hành | ANALYST | UC08.2 <<include>> UC08.1; UC08.3 <<include>> UC08.1 |
| UC08.2 | Cập nhật ngưỡng Fraud Score | ANALYST | <<include>> UC08.1 |
| UC08.3 | Cập nhật ngưỡng PD Score | ANALYST | <<include>> UC08.1 |
| UC08.4 | Xem hiệu suất mô hình Fraud | ANALYST | — |
| UC08.5 | Xem hiệu suất mô hình PD Score | ANALYST | — |
| UC08.6 | Xem danh sách Suppression Rules | ANALYST | — |
| UC08.7 | Tạo Suppression Rule mới | ANALYST | — |
| UC08.8 | Vô hiệu hóa Suppression Rule | ANALYST | — |
| UC08.9 | Tạo báo cáo phân tích | ANALYST | — |
| UC08.10 | Xem danh sách báo cáo phân tích | ANALYST, MANAGER | UC08.11 <<extend>> UC08.10 |
| UC08.11 | Xem chi tiết và tải PDF báo cáo | ANALYST, MANAGER | <<extend>> UC08.10 |
| UC08.12 | Xác nhận (Acknowledge) báo cáo | MANAGER | — |
| UC08.13 | Xuất dữ liệu phân tích (Export for Analysis) | ANALYST | — |

> **Lưu ý đọc bảng quan hệ:**
> - `UC_X <<extend>> UC_Y` → UC_X **mở rộng** UC_Y (xảy ra có điều kiện, tùy chọn, kích hoạt từ UC_Y)
> - `UC_X <<include>> UC_Y` → UC_X **bao gồm bắt buộc** UC_Y (mỗi lần UC_X thực thi đều gọi UC_Y)
> - `UC_X generalization → UC_Y` → UC_X là **dạng chuyên biệt hóa** của UC_Y trừu tượng
> - Chiều mũi tên trong UML: `<<extend>>` hướng **từ UC con về UC cha** (ngược chiều gọi); `<<include>>` hướng **từ UC cha đến UC con** (cùng chiều gọi)

**Kết quả:** 49 UC nghiệp vụ + 1 UC trừu tượng (UC06.A), tổ chức thành **8 nhóm UC**, liên kết với **6 actor** (1 trừu tượng + 5 cụ thể), 10 cặp quan hệ <<extend>>, 3 quan hệ <<include>>, 1 cặp generalization UC.

---

### 1.4 Mô tả Actor và Use Case

#### Mô tả Actor

| Actor | Loại | Kế thừa từ | Mô tả |
|-------|------|-----------|-------|
| Thành viên hệ thống | Trừu tượng | — | Bất kỳ người dùng / hệ thống có tài khoản hợp lệ trong HPTRRĐGTC |
| OPERATOR | Cụ thể | Thành viên hệ thống | Core Banking System của Ngân hàng đối tác — hệ thống tự động nộp giao dịch và đơn vay qua API. Không phải nhân viên con người |
| REVIEWER | Cụ thể | Thành viên hệ thống | Nhân viên tín dụng — tiếp nhận và ra quyết định các giao dịch MANUAL_REVIEW, đồng thời xét duyệt phê duyệt / từ chối hồ sơ vay |
| ANALYST | Cụ thể | Thành viên hệ thống | Chuyên viên phân tích rủi ro — vận hành mô hình AI, điều chỉnh ngưỡng, quản lý suppression rules, tạo báo cáo phân tích chuyên sâu |
| MANAGER | Cụ thể | Thành viên hệ thống | Quản lý giám sát hoạt động hệ thống, xem báo cáo, dashboard, audit log và xác nhận báo cáo phân tích. Có thể override quyết định của REVIEWER trong trường hợp leo thang |
| ADMIN | Cụ thể | Thành viên hệ thống | Quản trị viên kỹ thuật toàn hệ thống — quản lý tài khoản, ETL, đối soát |

---

#### Mô tả Use Case theo nhóm

**UC01 – Xác thực & Quản lý Phiên làm việc**

| Mã UC | Use Case | Actor | Mô tả |
|-------|----------|-------|-------|
| UC01.1 | Đăng nhập | Thành viên hệ thống | UC này cho phép người dùng đăng nhập vào HPTRRĐGTC bằng username và password để nhận JWT token truy cập hệ thống |
| UC01.2 | Đăng xuất | Thành viên hệ thống | UC này cho phép người dùng kết thúc phiên làm việc và vô hiệu hóa JWT token hiện tại |
| UC01.3 | Đổi mật khẩu cá nhân | Thành viên hệ thống | UC này cho phép người dùng thay đổi mật khẩu cá nhân sau khi xác minh mật khẩu cũ và đáp ứng chính sách độ mạnh |

---

**UC02 – Quản lý Giao dịch**

| Mã UC | Use Case | Actor | Mô tả |
|-------|----------|-------|-------|
| UC02.1 | Nộp giao dịch mới | OPERATOR | UC này cho phép Core Banking System của ngân hàng đối tác gửi một giao dịch vào HPTRRĐGTC để chấm điểm gian lận và phân luồng tự động. Chỉ OPERATOR mới được nộp — không có role nội bộ nào được phép |
| UC02.2 | Xem danh sách giao dịch | REVIEWER, ANALYST | UC này cho phép người dùng xem danh sách toàn bộ giao dịch trong hệ thống với filter theo status, ngày, merchant, số tiền |
| UC02.3 | Xem chi tiết giao dịch | REVIEWER, ANALYST | UC này cho phép người dùng xem toàn bộ thông tin của một giao dịch: fraud_score, trạng thái, lý do phân loại, và mã case liên quan nếu có |

---

**UC03 – Quản lý Đơn Vay (Loan Management)**

| Mã UC | Use Case | Actor | Mô tả |
|-------|----------|-------|-------|
| UC03.1 | Nộp hồ sơ đề nghị vay vốn | OPERATOR | UC này cho phép Core Banking System của ngân hàng đối tác nộp đơn vay của khách hàng vào HPTRRĐGTC. Hệ thống tính PD Score và phân loại mức rủi ro (LOW/MEDIUM/HIGH). Đơn được lưu với trạng thái PENDING chờ MANAGER/ADMIN duyệt. Chỉ OPERATOR mới được nộp |
| UC03.2 | Mô phỏng chấm điểm rủi ro vay (Simulate) | OPERATOR, REVIEWER | UC này cho phép người dùng nhập các trường AI để nhận PD Score và phân loại rủi ro tức thì mà không lưu vào DB — dùng để kiểm tra trước khi nộp đơn chính thức |
| UC03.3 | Xem danh sách hồ sơ vay | OPERATOR, REVIEWER | UC này cho phép xem danh sách toàn bộ hồ sơ vay, filter theo trạng thái và customer |
| UC03.4 | Xem chi tiết hồ sơ vay | OPERATOR, REVIEWER | UC này cho phép xem toàn bộ thông tin hồ sơ vay kèm kết quả PD Score, phân loại rủi ro, và trạng thái xét duyệt |
| UC03.5 | Phê duyệt / Từ chối hồ sơ vay | REVIEWER | UC này cho phép REVIEWER đưa ra quyết định APPROVE hoặc REJECT cho đơn vay đang PENDING. Ràng buộc SoD: người phê duyệt không được là người đã tạo đơn (4-eyes principle) |

---

**UC04 – Xét duyệt Thủ công (Manual Case Management)**

| Mã UC | Use Case | Actor | Mô tả |
|-------|----------|-------|-------|
| UC04.1 | Xem danh sách case chờ xử lý | REVIEWER, MANAGER | UC này cho phép xem danh sách các case đang ở trạng thái OPEN (chưa ai nhận) hoặc ASSIGNED (đã nhận nhưng chưa quyết định) |
| UC04.2 | Nhận case (Assign) | REVIEWER | UC này cho phép REVIEWER chọn một case chưa có người xử lý và nhận về tên mình để tiến hành xét duyệt |
| UC04.3 | Xem chi tiết case | REVIEWER, MANAGER | UC này cho phép xem toàn bộ thông tin của một case: thông tin giao dịch liên quan, fraud_score, lịch sử trạng thái và người phụ trách |
| UC04.4 | Ra quyết định Phê duyệt / Từ chối | REVIEWER, MANAGER | UC này cho phép đưa ra quyết định cuối cùng (APPROVED / REJECTED) cho case. REVIEWER chỉ quyết định được case đã nhận về mình; MANAGER/ADMIN có thể quyết định bất kỳ case ASSIGNED nào (override/giám sát). Case phải ở trạng thái ASSIGNED, không thể quyết định case OPEN trực tiếp |

---

**UC05 – Giám sát & Báo cáo**

| Mã UC | Use Case | Actor | Mô tả |
|-------|----------|-------|-------|
| UC05.1 | Xem Dashboard tổng quan | MANAGER | UC này cho phép xem tổng hợp số liệu KPI hoạt động hệ thống (tổng giao dịch, tỉ lệ phê duyệt, tỉ lệ gian lận, case tồn đọng) theo khoảng thời gian |
| UC05.2 | Xem biểu đồ phân bố Fraud Score | ANALYST, MANAGER | UC này cho phép xem biểu đồ histogram phân bố fraud_score của các giao dịch theo dải điểm, để đánh giá hiệu quả mô hình AI |
| UC05.3 | Xem báo cáo giao dịch | MANAGER | UC này cho phép tra cứu danh sách giao dịch với các điều kiện lọc: khoảng thời gian, trạng thái, kênh, ngưỡng fraud_score |
| UC05.4 | Xuất báo cáo (CSV / PDF) | MANAGER | UC này cho phép xuất toàn bộ dữ liệu báo cáo đang xem ra file CSV hoặc PDF để lưu trữ và báo cáo kiểm toán |
| UC05.5 | Xem Audit Log hệ thống | MANAGER, ADMIN | UC này cho phép xem toàn bộ nhật ký hành động nghiệp vụ trong hệ thống (actor, hành động, đối tượng bị tác động, giá trị trước/sau) |
| UC05.6 | Truy vết lịch sử một giao dịch cụ thể | MANAGER, ADMIN | UC này cho phép xem toàn bộ timeline trạng thái của một giao dịch: khi nào tạo, ai xét duyệt, lý do quyết định, trạng thái thay đổi như thế nào |
| UC05.7 | Xem kết quả đối soát (Reconciliation) | ANALYST, ADMIN | UC này cho phép xem danh sách và chi tiết kết quả các phiên đối soát: giao dịch PENDING_TIMEOUT, discrepancy items và trạng thái resolve |

---

**UC06 – Quản trị Hệ thống (User Management)**

| Mã UC | Use Case | Actor | Mô tả |
|-------|----------|-------|-------|
| UC06.1 | Tạo tài khoản người dùng mới | ADMIN | UC này cho phép ADMIN tạo tài khoản mới cho nhân viên với thông tin cơ bản (họ tên, email, username, mật khẩu tạm, vai trò) |
| UC06.2 | Vô hiệu hóa tài khoản | ADMIN | UC này cho phép ADMIN khóa tài khoản nhân viên (is_active = FALSE), ngăn đăng nhập mới và thu hồi phiên đang chạy |
| UC06.3 | Kích hoạt lại tài khoản | ADMIN | UC này cho phép ADMIN mở lại tài khoản đã bị vô hiệu hóa (is_active = TRUE) |
| UC06.4 | Gán / Thay đổi vai trò người dùng | ADMIN | UC này cho phép ADMIN gán hoặc thay đổi vai trò (OPERATOR / REVIEWER / ANALYST / MANAGER / ADMIN) của một người dùng |
| UC06.5 | Xem danh sách người dùng | MANAGER, ADMIN | UC này cho phép xem toàn bộ danh sách tài khoản người dùng trong hệ thống (MANAGER chỉ đọc, ADMIN có thể thao tác) |
| UC06.6 | Xem chi tiết thông tin người dùng | MANAGER, ADMIN | UC này cho phép xem thông tin chi tiết của một người dùng cụ thể: vai trò, trạng thái, email, thời gian tạo |

---

**UC07 – Data Engineering & Đối soát Dữ liệu**

| Mã UC | Use Case | Actor | Mô tả |
|-------|----------|-------|-------|
| UC07.1 | Xem cấu trúc Data Lake | ADMIN | UC này cho phép ADMIN xem thống kê cấu trúc thư mục Data Lake: số file, tổng dung lượng, khoảng ngày có dữ liệu — để xác nhận trước khi chạy ETL |
| UC07.2 | Kích hoạt ETL Pipeline | ADMIN | UC này cho phép ADMIN khởi chạy thủ công pipeline ETL từ Data Lake vào Data Warehouse với khoảng ngày được chỉ định |
| UC07.3 | Xem ETL Logs | ADMIN | UC này cho phép ADMIN xem danh sách kết quả các lần ETL đã chạy: trạng thái, số bản ghi, thời gian thực thi |
| UC07.4 | Xem chi tiết một ETL Job | ADMIN | UC này cho phép ADMIN xem chi tiết một lần chạy ETL cụ thể, bao gồm thông tin lỗi chi tiết nếu trạng thái PARTIAL hoặc FAILED |
| UC07.5 | Kích hoạt Reconciliation Job | ADMIN | UC này cho phép ADMIN khởi chạy thủ công job đối soát — tìm giao dịch PENDING vượt timeout → đánh dấu PENDING_TIMEOUT → tổng hợp discrepancy |
| UC07.6 | Xem danh sách Reconciliation Jobs | ANALYST, ADMIN | UC này cho phép xem danh sách kết quả các phiên đối soát: thời gian chạy, trạng thái (RUNNING / COMPLETED / FAILED), số giao dịch kiểm tra, số discrepancy |
| UC07.7 | Xem chi tiết Reconciliation Job | ANALYST, ADMIN | UC này cho phép xem chi tiết một phiên đối soát: danh sách giao dịch PENDING_TIMEOUT, resolve trạng thái discrepancy |

---

**UC08 – Analyst Module (Phân tích Rủi ro Chuyên sâu)**

| Mã UC | Use Case | Actor | Mô tả |
|-------|----------|-------|-------|
| UC08.1 | Xem ngưỡng phân loại hiện hành | ANALYST | UC này cho phép xem các ngưỡng phân loại đang áp dụng cho mô hình Fraud (reject_threshold, review_threshold) và mô hình PD Score (risk_high_threshold, risk_medium_threshold) |
| UC08.2 | Cập nhật ngưỡng Fraud Score | ANALYST | UC này cho phép ANALYST điều chỉnh reject_threshold và review_threshold của mô hình phát hiện gian lận. Thay đổi có hiệu lực ngay với transaction tiếp theo |
| UC08.3 | Cập nhật ngưỡng PD Score | ANALYST | UC này cho phép ANALYST điều chỉnh risk_high_threshold và risk_medium_threshold của mô hình PD Score vay vốn |
| UC08.4 | Xem hiệu suất mô hình Fraud | ANALYST | UC này cho phép xem các chỉ số đánh giá mô hình Fraud: precision, recall, F1-score, AUC-ROC, phân phối fraud_score theo khoảng, và trend theo thời gian |
| UC08.5 | Xem hiệu suất mô hình PD Score | ANALYST | UC này cho phép xem các chỉ số đánh giá mô hình PD Score: phân bố pd_score, tỉ lệ default theo risk_level, so sánh ngưỡng hiện hành với phân phối thực tế |
| UC08.6 | Xem danh sách Suppression Rules | ANALYST | UC này cho phép xem tất cả suppression rules (active và inactive): điều kiện lọc, ngưỡng, trạng thái, ngày tạo và người tạo |
| UC08.7 | Tạo Suppression Rule mới | ANALYST | UC này cho phép ANALYST tạo rule loại trừ giao dịch khỏi cờ fraud — ví dụ: tất cả giao dịch từ merchant_id X nhỏ hơn N VND sẽ không bị MANUAL_REVIEW |
| UC08.8 | Vô hiệu hóa Suppression Rule | ANALYST | UC này cho phép ANALYST tắt một suppression rule đang active mà không xóa khỏi hệ thống — hỗ trợ rollback và audit |
| UC08.9 | Tạo báo cáo phân tích | ANALYST | UC này cho phép ANALYST tạo báo cáo phân tích rủi ro định kỳ (tuần/tháng/quý) bằng Markdown với tự động render PDF, đính kèm biểu đồ và nhận xét |
| UC08.10 | Xem danh sách báo cáo phân tích | ANALYST, MANAGER | UC này cho phép xem danh sách các báo cáo đã tạo: tiêu đề, tác giả, kỳ báo cáo, trạng thái (DRAFT / PUBLISHED / ACKNOWLEDGED) |
| UC08.11 | Xem chi tiết và tải PDF báo cáo | ANALYST, MANAGER | UC này cho phép xem nội dung đầy đủ của báo cáo và tải file PDF để lưu trữ hoặc trình lãnh đạo |
| UC08.12 | Xác nhận (Acknowledge) báo cáo | MANAGER | UC này cho phép MANAGER/ADMIN xác nhận đã đọc và chấp thuận nội dung báo cáo phân tích, chuyển trạng thái báo cáo từ PUBLISHED sang ACKNOWLEDGED |
| UC08.13 | Xuất dữ liệu phân tích (Export for Analysis) | ANALYST | UC này cho phép ANALYST xuất raw dataset về máy cục bộ để phân tích offline: transactions (với fraud_score), case outcomes (AI decision vs reviewer decision), loan portfolio (PD score), model metrics history. Format CSV — tối đa 100.000 records/lần. Dùng cho re-training model, validation, báo cáo chuyên sâu |

---

## 2. Biểu đồ Use Case Chi tiết

> **Phương pháp:** Với mỗi use case tổng quan, phân rã thành các use case con dựa trên từng màn hình (giao diện) người dùng tương tác. Xác định quan hệ <<include>> (bắt buộc), <<extend>> (có điều kiện), hoặc generalization (chuyên biệt hóa).

---

### UC01 – Xác thực & Quản lý Phiên làm việc

#### Chi tiết: Đăng nhập

Người dùng tương tác qua các màn hình:
1. Form đăng nhập → người dùng nhập thông tin
2. Nhận phản hồi kết quả (thành công hoặc lỗi)

**Quan hệ use case con:**
- **Đăng nhập** `<<include>>` **Nhập thông tin đăng nhập** — bắt buộc, không thể bỏ qua
- **Đăng nhập** `<<include>>` **Nhận thông báo kết quả đăng nhập** — bắt buộc, luôn nhận phản hồi

| Use Case con | Actor | Quan hệ | Mô tả |
|---|---|---|---|
| Nhập thông tin đăng nhập | Thành viên hệ thống | `<<include>>` từ Đăng nhập | UC này cho phép người dùng nhập username và password trên form đăng nhập |
| Nhận thông báo kết quả đăng nhập | Thành viên hệ thống | `<<include>>` từ Đăng nhập | UC này cho phép người dùng nhận kết quả: chuyển vào hệ thống (thành công) hoặc xem thông báo lỗi 401 (thất bại) |

---

#### Chi tiết: Đổi mật khẩu cá nhân

Người dùng tương tác qua các màn hình:
1. Form đổi mật khẩu → nhập mật khẩu cũ, mới, xác nhận
2. Nhận phản hồi (thành công / lỗi xác thực / lỗi chính sách)

**Quan hệ use case con:**
- **Đổi mật khẩu cá nhân** `<<include>>` **Nhập mật khẩu cũ và mật khẩu mới**
- **Đổi mật khẩu cá nhân** `<<include>>` **Nhận thông báo kết quả đổi mật khẩu**

| Use Case con | Actor | Quan hệ | Mô tả |
|---|---|---|---|
| Nhập mật khẩu cũ và mật khẩu mới | Thành viên hệ thống | `<<include>>` từ Đổi mật khẩu cá nhân | UC này cho phép người dùng nhập mật khẩu hiện tại, mật khẩu mới và xác nhận lại mật khẩu mới |
| Nhận thông báo kết quả đổi mật khẩu | Thành viên hệ thống | `<<include>>` từ Đổi mật khẩu cá nhân | UC này cho phép người dùng nhận thông báo thành công (kèm yêu cầu đăng nhập lại) hoặc lỗi nếu mật khẩu cũ sai / không thỏa chính sách độ mạnh |

---

### UC02 – Quản lý Giao dịch

#### Chi tiết: Nộp giao dịch mới (OPERATOR)

Đây là use case cốt lõi của hệ thống. Core Banking System của ngân hàng đối tác gọi API trực tiếp — không qua giao diện web. Tương tác theo luồng:
1. Gửi POST /transactions/submit với đầy đủ trường bắt buộc
2. Nhận kết quả phân loại tức thì (APPROVED / REJECTED / MANUAL_REVIEW)
3. Tùy chọn: truy vấn chi tiết giao dịch vừa tạo

**Quan hệ use case con:**
- **Nộp giao dịch mới** `<<include>>` **Điền thông tin giao dịch**
- **Nộp giao dịch mới** `<<include>>` **Xác nhận và gửi giao dịch**
- **Nộp giao dịch mới** `<<include>>` **Xem kết quả phân loại giao dịch**
- **Nộp giao dịch mới** `<<extend>>` **Xem chi tiết giao dịch** (chỉ khi người dùng truy vấn thêm)

| Use Case con | Actor | Quan hệ | Mô tả |
|---|---|---|---|
| Điền thông tin giao dịch | OPERATOR | `<<include>>` từ Nộp giao dịch mới | UC này cho phép OPERATOR nhập các trường bắt buộc: mã khách hàng, số tiền, loại tiền tệ, tên merchant, kênh giao dịch (ATM / POS / ONLINE) |
| Xác nhận và gửi giao dịch | OPERATOR | `<<include>>` từ Nộp giao dịch mới | UC này cho phép OPERATOR xác nhận gửi chính thức vào hệ thống |
| Xem kết quả phân loại giao dịch | OPERATOR | `<<include>>` từ Nộp giao dịch mới | UC này cho phép OPERATOR nhận kết quả tức thì: fraud_score (0.0–1.0) và trạng thái phân loại (APPROVED / REJECTED / MANUAL_REVIEW) |
| Xem chi tiết giao dịch | OPERATOR | `<<extend>>` từ Nộp giao dịch mới | UC này cho phép OPERATOR xem toàn bộ thông tin bản ghi giao dịch vừa được lưu trong hệ thống, bao gồm mã case liên quan nếu có |

---

#### Chi tiết: Xem danh sách giao dịch

Người dùng tương tác qua các màn hình:
1. Danh sách giao dịch (mặc định, phân trang)
2. Tùy chọn: áp dụng bộ lọc
3. Tùy chọn: click một dòng để xem chi tiết

**Quan hệ use case con:**
- **Xem danh sách giao dịch** `<<extend>>` **Lọc danh sách giao dịch**
- **Xem danh sách giao dịch** `<<extend>>` **Xem chi tiết giao dịch** (UC02.3)

| Use Case con | Actor | Quan hệ | Mô tả |
|---|---|---|---|
| Lọc danh sách giao dịch | REVIEWER, ANALYST | `<<extend>>` từ Xem danh sách giao dịch | UC này cho phép người dùng thu hẹp kết quả theo: khoảng thời gian, trạng thái, kênh giao dịch (ATM / POS / ONLINE), ngưỡng fraud_score |

---

### UC03 – Quản lý Đơn Vay

#### Chi tiết: Nộp hồ sơ đề nghị vay vốn (OPERATOR)

Core Banking System của ngân hàng đối tác gọi API POST /loans. Tương tác theo luồng:
1. Gửi thông tin tín dụng khách hàng: principal_amount, interest_rate, term_months, purpose và tùy chọn các trường AI để nhận PD Score ngay
2. Nhận kết quả: đơn lưu PENDING + PD Score (nếu đủ trường AI)

**Quan hệ use case con:**
- **Nộp hồ sơ đề nghị vay vốn** `<<include>>` **Điền thông tin tín dụng khách hàng**
- **Nộp hồ sơ đề nghị vay vốn** `<<include>>` **Xác nhận và gửi hồ sơ vay**
- **Nộp hồ sơ đề nghị vay vốn** `<<include>>` **Xem kết quả lưu đơn và PD Score**

| Use Case con | Actor | Quan hệ | Mô tả |
|---|---|---|---|
| Điền thông tin tín dụng khách hàng | OPERATOR | `<<include>>` từ Nộp hồ sơ | UC này cho phép OPERATOR nhập: mã khách hàng, số tiền vay, lãi suất, kỳ hạn, mục đích và tùy chọn các trường AI (person_age, person_income, loan_grade, ...) |
| Xác nhận và gửi hồ sơ vay | OPERATOR | `<<include>>` từ Nộp hồ sơ | UC này cho phép OPERATOR xác nhận gửi hồ sơ vào hệ thống |
| Xem kết quả lưu đơn và PD Score | OPERATOR | `<<include>>` từ Nộp hồ sơ | UC này cho phép OPERATOR nhận kết quả: đơn lưu với status PENDING, PD Score và risk_level nếu đủ trường AI |

---

#### Chi tiết: Mô phỏng chấm điểm rủi ro vay (OPERATOR, REVIEWER)

Người dùng tương tác qua các màn hình:
1. Form mô phỏng → điền đầy đủ tất cả trường AI (bắt buộc cho simulate)
2. Nhận kết quả PD Score + risk_level + top risk factors

**Quan hệ use case con:**
- **Mô phỏng chấm điểm rủi ro vay** `<<include>>` **Điền đầy đủ thông tin mô phỏng**
- **Mô phỏng chấm điểm rủi ro vay** `<<include>>` **Xem kết quả mô phỏng PD Score**

| Use Case con | Actor | Quan hệ | Mô tả |
|---|---|---|---|
| Điền đầy đủ thông tin mô phỏng | OPERATOR, REVIEWER | `<<include>>` từ Mô phỏng | UC này cho phép người dùng nhập tất cả trường AI bắt buộc: person_age, person_income, person_home_ownership, person_emp_length, loan_intent, loan_grade, loan_amnt, loan_int_rate, cb_person_default_on_file, cb_person_cred_hist_length |
| Xem kết quả mô phỏng PD Score | OPERATOR, REVIEWER | `<<include>>` từ Mô phỏng | UC này cho phép người dùng nhận ngay: pd_score (0.0–1.0), risk_level (LOW/MEDIUM/HIGH), top_risk_factors, model_version — không lưu vào DB |

---

#### Chi tiết: Xem danh sách hồ sơ vay

**Quan hệ use case con:**
- **Xem danh sách hồ sơ vay** `<<extend>>` **Lọc danh sách hồ sơ vay**
- **Xem danh sách hồ sơ vay** `<<extend>>` **Xem chi tiết hồ sơ vay** (UC03.4)

| Use Case con | Actor | Quan hệ | Mô tả |
|---|---|---|---|
| Lọc danh sách hồ sơ vay | OPERATOR, REVIEWER | `<<extend>>` từ Xem danh sách hồ sơ vay | UC này cho phép người dùng lọc hồ sơ vay theo trạng thái, mức rủi ro (LOW / MEDIUM / HIGH), khoảng thời gian nộp |

---

#### Chi tiết: Phê duyệt / Từ chối hồ sơ vay (REVIEWER)

Người dùng tương tác qua các màn hình:
1. Danh sách đơn vay PENDING
2. Màn hình chi tiết đơn vay — đọc PD Score và thông tin khách hàng
3. Form quyết định — chọn APPROVE / REJECT + nhập ghi chú + version

**Ràng buộc SoD:** Người phê duyệt không được là người đã tạo đơn → 403 nếu vi phạm.

**Quan hệ use case con:**
- **Phê duyệt / Từ chối hồ sơ vay** `<<include>>` **Xem chi tiết hồ sơ vay** (UC03.4)
- **Phê duyệt / Từ chối hồ sơ vay** `<<include>>` **Nhập quyết định và ghi chú**
- **Phê duyệt / Từ chối hồ sơ vay** `<<include>>` **Xác nhận quyết định**
- **Phê duyệt / Từ chối hồ sơ vay** `<<extend>>` **Tải lại đơn vay** (khi version conflict — 409)

| Use Case con | Actor | Quan hệ | Mô tả |
|---|---|---|---|
| Nhập quyết định và ghi chú | REVIEWER | `<<include>>` từ Phê duyệt/Từ chối | UC này cho phép REVIEWER chọn APPROVE hoặc REJECT, nhập review_note (tùy chọn) và version hiện tại của đơn |
| Xác nhận quyết định | REVIEWER | `<<include>>` từ Phê duyệt/Từ chối | UC này cho phép REVIEWER xác nhận gửi quyết định. Nếu APPROVE: hệ thống tự tính monthly_payment, outstanding_balance, maturity_date |
| Tải lại đơn vay | REVIEWER | `<<extend>>` từ Phê duyệt/Từ chối | UC này cho phép REVIEWER tải lại dữ liệu đơn khi hệ thống trả 409 Conflict do version không khớp |

---

### UC04 – Xét duyệt Thủ công

#### Chi tiết: Nhận case (Assign) (REVIEWER)

Người dùng tương tác qua các màn hình:
1. Màn hình danh sách case OPEN
2. Tùy chọn: lọc / sắp xếp
3. Chọn một case và nhấn nút "Nhận case"
4. Nhận xác nhận kết quả (nhận thành công hoặc lỗi đã có người nhận trước)

**Quan hệ use case con:**
- **Nhận case (Assign)** `<<include>>` **Xem danh sách case chờ xử lý** (UC04.1) — phải vào danh sách trước
- **Nhận case (Assign)** `<<include>>` **Xác nhận nhận case**
- **Xem danh sách case chờ xử lý** `<<extend>>` **Lọc và sắp xếp danh sách case**

| Use Case con | Actor | Quan hệ | Mô tả |
|---|---|---|---|
| Lọc và sắp xếp danh sách case | REVIEWER | `<<extend>>` từ Xem danh sách case | UC này cho phép REVIEWER lọc case theo khoảng fraud_score, sắp xếp theo thời gian chờ (lâu nhất lên đầu) |
| Xác nhận nhận case | REVIEWER | `<<include>>` từ Nhận case (Assign) | UC này cho phép REVIEWER nhấn xác nhận nhận một case cụ thể — chỉ thành công nếu case chưa bị người khác nhận (hệ thống dùng DB Locking để đảm bảo) |

---

#### Chi tiết: Ra quyết định Phê duyệt / Từ chối (REVIEWER, MANAGER)

Người dùng tương tác qua các màn hình:
1. Danh sách case ASSIGNED
2. Màn hình chi tiết case — đọc đầy đủ thông tin giao dịch, fraud_score, action history
3. Form quyết định — chọn APPROVE / REJECT + nhập decision_note (bắt buộc, min 10 ký tự) + version
4. Xác nhận gửi quyết định
5. Tùy chọn (khi version conflict): màn hình cảnh báo và tải lại

> **Ràng buộc phân quyền:** Case phải ở trạng thái ASSIGNED (không thể quyết định case OPEN). REVIEWER chỉ quyết định được case được gán cho mình; MANAGER/ADMIN quyết định được bất kỳ case ASSIGNED nào (bypass ownership check).

**Quan hệ use case con:**
- **Ra quyết định Phê duyệt / Từ chối** `<<include>>` **Xem chi tiết case** (UC04.3) — phải đọc trước khi quyết định
- **Ra quyết định Phê duyệt / Từ chối** `<<include>>` **Nhập quyết định và ghi chú lý do**
- **Ra quyết định Phê duyệt / Từ chối** `<<include>>` **Xác nhận quyết định**
- **Ra quyết định Phê duyệt / Từ chối** `<<extend>>` **Tải lại thông tin case mới nhất** (chỉ khi hệ thống báo version conflict — 409 Conflict)

| Use Case con | Actor | Quan hệ | Mô tả |
|---|---|---|---|
| Nhập quyết định và ghi chú lý do | REVIEWER, MANAGER | `<<include>>` từ Ra quyết định | UC này cho phép người dùng chọn APPROVE hoặc REJECT và nhập decision_note (bắt buộc, tối thiểu 10 ký tự) kèm version hiện tại của case |
| Xác nhận quyết định | REVIEWER, MANAGER | `<<include>>` từ Ra quyết định | UC này cho phép người dùng xác nhận gửi quyết định — hệ thống dùng Optimistic Locking kiểm tra version trước khi ghi nhận |
| Tải lại thông tin case mới nhất | REVIEWER, MANAGER | `<<extend>>` từ Ra quyết định | UC này cho phép người dùng tải lại dữ liệu case khi hệ thống trả lỗi 409 Conflict do version không khớp |

---

### UC05 – Giám sát & Báo cáo

#### Chi tiết: Xem Dashboard tổng quan (ANALYST, MANAGER, ADMIN)

Người dùng tương tác qua các màn hình:
1. Trang Dashboard chính — xem KPI Cards và biểu đồ xu hướng
2. Tùy chọn: chọn khoảng thời gian (hôm nay / tuần này / tháng này)
3. Tùy chọn: click vào một chỉ số KPI để xem chi tiết

**Quan hệ use case con:**
- **Xem Dashboard tổng quan** `<<include>>` **Xem KPI Cards và biểu đồ xu hướng**
- **Xem Dashboard tổng quan** `<<extend>>` **Lọc Dashboard theo thời gian**
- **Xem Dashboard tổng quan** `<<extend>>` **Xem chi tiết một KPI cụ thể**

| Use Case con | Actor | Quan hệ | Mô tả |
|---|---|---|---|
| Xem KPI Cards và biểu đồ xu hướng | ANALYST, MANAGER, ADMIN | `<<include>>` từ Xem Dashboard | UC này cho phép người dùng xem các chỉ số: tổng giao dịch, tỉ lệ APPROVED / REJECTED / MANUAL_REVIEW, số case tồn đọng, tỉ lệ gian lận bị chặn |
| Lọc Dashboard theo thời gian | ANALYST, MANAGER, ADMIN | `<<extend>>` từ Xem Dashboard | UC này cho phép người dùng chọn khoảng thời gian (hôm nay / tuần này / tháng này) để cập nhật toàn bộ số liệu Dashboard |
| Xem chi tiết một KPI cụ thể | ANALYST, MANAGER, ADMIN | `<<extend>>` từ Xem Dashboard | UC này cho phép người dùng click vào một chỉ số KPI để xem số liệu chi tiết theo từng ngày trong khoảng đã chọn |

---

#### Chi tiết: Xem báo cáo giao dịch + Xuất báo cáo (ANALYST, MANAGER, ADMIN)

Người dùng tương tác qua các màn hình:
1. Trang báo cáo — nhập điều kiện lọc
2. Danh sách kết quả (phân trang)
3. Tùy chọn: click một dòng để xem chi tiết
4. Tùy chọn: click "Xuất file" → chọn định dạng → tải file

**Quan hệ use case con:**
- **Xem báo cáo giao dịch** `<<include>>` **Nhập điều kiện lọc báo cáo**
- **Xem báo cáo giao dịch** `<<extend>>` **Xem chi tiết giao dịch trong báo cáo**
- **Xuất báo cáo (CSV / PDF)** `<<include>>` **Xem báo cáo giao dịch** — phải có danh sách kết quả trước
- **Xuất báo cáo (CSV / PDF)** `<<include>>` **Chọn định dạng và tải file**

| Use Case con | Actor | Quan hệ | Mô tả |
|---|---|---|---|
| Nhập điều kiện lọc báo cáo | ANALYST, MANAGER, ADMIN | `<<include>>` từ Xem báo cáo | UC này cho phép người dùng nhập điều kiện lọc: khoảng thời gian, trạng thái, kênh giao dịch, ngưỡng fraud_score |
| Xem chi tiết giao dịch trong báo cáo | ANALYST, MANAGER, ADMIN | `<<extend>>` từ Xem báo cáo | UC này cho phép người dùng click vào một dòng để xem thông tin chi tiết đầy đủ của giao dịch đó |
| Chọn định dạng và tải file | ANALYST, MANAGER, ADMIN | `<<include>>` từ Xuất báo cáo | UC này cho phép người dùng chọn định dạng (CSV hoặc PDF) và tải file xuống máy — file chứa toàn bộ dữ liệu theo điều kiện lọc hiện tại, không giới hạn phân trang |

---

#### Chi tiết: Xem Audit Log hệ thống (ANALYST, MANAGER, ADMIN)

Người dùng tương tác qua các màn hình:
1. Trang Audit Log — danh sách log toàn hệ thống
2. Tùy chọn: áp dụng bộ lọc
3. Tùy chọn: chọn một giao dịch để truy vết timeline
4. Tùy chọn: xuất audit log ra file

**Quan hệ use case con:**
- **Xem Audit Log hệ thống** `<<extend>>` **Lọc Audit Log**
- **Xem Audit Log hệ thống** `<<extend>>` **Truy vết lịch sử một giao dịch cụ thể** (UC05.6)
- **Xem Audit Log hệ thống** `<<extend>>` **Xuất Audit Log**

| Use Case con | Actor | Quan hệ | Mô tả |
|---|---|---|---|
| Lọc Audit Log | ANALYST, MANAGER, ADMIN | `<<extend>>` từ Xem Audit Log | UC này cho phép lọc log theo khoảng thời gian, actor, loại hành động (action), đối tượng bị tác động (entity type) |
| Xuất Audit Log | ANALYST, MANAGER, ADMIN | `<<extend>>` từ Xem Audit Log | UC này cho phép xuất danh sách audit events đang lọc ra file để phục vụ kiểm toán nội bộ hoặc báo cáo cơ quan giám sát |

*Lưu ý: "Truy vết lịch sử một giao dịch cụ thể" (UC05.6) là use case độc lập trong sơ đồ tổng quan. Tại đây nó là mở rộng có điều kiện từ "Xem Audit Log" — được kích hoạt khi người dùng chọn tra cứu một giao dịch cụ thể.*

---

### UC06 – Quản trị Hệ thống

#### Chi tiết: Tạo tài khoản người dùng mới (ADMIN)

Người dùng tương tác qua các màn hình:
1. Trang danh sách người dùng → click "Tạo mới"
2. Form tạo tài khoản — nhập thông tin
3. Xác nhận tạo

**Quan hệ use case con:**
- **Tạo tài khoản người dùng mới** `<<include>>` **Điền thông tin người dùng mới**
- **Tạo tài khoản người dùng mới** `<<include>>` **Xác nhận tạo tài khoản**

| Use Case con | Actor | Quan hệ | Mô tả |
|---|---|---|---|
| Điền thông tin người dùng mới | ADMIN | `<<include>>` từ Tạo tài khoản | UC này cho phép ADMIN nhập: họ tên, email, username, mật khẩu tạm thời và vai trò ban đầu cho người dùng mới |
| Xác nhận tạo tài khoản | ADMIN | `<<include>>` từ Tạo tài khoản | UC này cho phép ADMIN xem lại thông tin và xác nhận tạo — hệ thống kiểm tra trùng username trước khi lưu |

---

#### Chi tiết: Vô hiệu hóa tài khoản & Kích hoạt lại tài khoản (ADMIN)

Hai UC này có chung quy trình gốc. Sử dụng use case trừu tượng **"Thay đổi trạng thái tài khoản"** làm cha chung:

**Quan hệ:**
- **Vô hiệu hóa tài khoản** là generalization (chuyên biệt hóa) của **Thay đổi trạng thái tài khoản**
- **Kích hoạt lại tài khoản** là generalization (chuyên biệt hóa) của **Thay đổi trạng thái tài khoản**
- **Thay đổi trạng thái tài khoản** `<<include>>` **Chọn tài khoản từ danh sách**
- **Thay đổi trạng thái tài khoản** `<<include>>` **Xác nhận thay đổi trạng thái**

| Use Case | Actor | Quan hệ | Mô tả |
|---|---|---|---|
| Thay đổi trạng thái tài khoản | ADMIN | Trừu tượng (cha chung) | UC trừu tượng mô tả quy trình chung: chọn tài khoản → xác nhận thay đổi is_active |
| Vô hiệu hóa tài khoản | ADMIN | generalization từ Thay đổi trạng thái | UC cụ thể: áp dụng trên tài khoản đang hoạt động → đặt is_active = FALSE |
| Kích hoạt lại tài khoản | ADMIN | generalization từ Thay đổi trạng thái | UC cụ thể: áp dụng trên tài khoản đang bị khóa → đặt is_active = TRUE |
| Chọn tài khoản từ danh sách | ADMIN | `<<include>>` từ Thay đổi trạng thái | UC này cho phép ADMIN chọn tài khoản mục tiêu từ danh sách người dùng |
| Xác nhận thay đổi trạng thái | ADMIN | `<<include>>` từ Thay đổi trạng thái | UC này cho phép ADMIN xác nhận hành động — hệ thống hiển thị cảnh báo nếu ADMIN đang cố vô hiệu hóa chính tài khoản mình |

---

#### Chi tiết: Gán / Thay đổi vai trò người dùng (ADMIN)

Người dùng tương tác qua các màn hình:
1. Màn hình chi tiết người dùng → click "Thay đổi vai trò"
2. Danh sách vai trò → chọn vai trò mới
3. Xác nhận

**Quan hệ use case con:**
- **Gán / Thay đổi vai trò người dùng** `<<include>>` **Chọn vai trò mới**
- **Gán / Thay đổi vai trò người dùng** `<<include>>` **Xác nhận gán vai trò**

| Use Case con | Actor | Quan hệ | Mô tả |
|---|---|---|---|
| Chọn vai trò mới | ADMIN | `<<include>>` từ Gán / Thay đổi vai trò | UC này cho phép ADMIN chọn một vai trò mới (OPERATOR / REVIEWER / ANALYST / MANAGER / ADMIN) từ danh sách |
| Xác nhận gán vai trò | ADMIN | `<<include>>` từ Gán / Thay đổi vai trò | UC này cho phép ADMIN xác nhận thay đổi — hệ thống cập nhật bảng USER_ROLES và ghi Audit Log |

---

### UC07 – Data Engineering & Đối soát Dữ liệu

#### Chi tiết: Kích hoạt ETL Pipeline (ADMIN)

Người dùng tương tác qua các màn hình:
1. Trang ETL — xem cấu trúc Data Lake để kiểm tra dữ liệu có sẵn
2. Form kích hoạt — nhập khoảng ngày cần xử lý
3. Xác nhận chạy
4. Theo dõi kết quả qua Xem ETL Logs
5. Tùy chọn: click vào một dòng log để xem chi tiết

**Quan hệ use case con:**
- **Kích hoạt ETL Pipeline** `<<include>>` **Chọn khoảng ngày ETL**
- **Kích hoạt ETL Pipeline** `<<include>>` **Xác nhận kích hoạt ETL**
- **Xem ETL Logs** `<<extend>>` **Xem chi tiết một ETL Job** (UC07.4) — chỉ khi click vào dòng log

| Use Case con | Actor | Quan hệ | Mô tả |
|---|---|---|---|
| Chọn khoảng ngày ETL | ADMIN | `<<include>>` từ Kích hoạt ETL | UC này cho phép ADMIN nhập ngày bắt đầu và ngày kết thúc của dữ liệu cần được xử lý từ Data Lake |
| Xác nhận kích hoạt ETL | ADMIN | `<<include>>` từ Kích hoạt ETL | UC này cho phép ADMIN xem lại cấu hình khoảng ngày và xác nhận chạy pipeline — hệ thống bắt đầu Extract → Transform → Load ngầm |

---

#### Chi tiết: Kích hoạt Reconciliation Job (ADMIN)

Người dùng tương tác qua các màn hình:
1. Trang Reconciliation — form nhập ngày đối soát
2. Xác nhận chạy
3. Theo dõi danh sách kết quả
4. Tùy chọn: click vào một job để xem chi tiết lệch

**Quan hệ use case con:**
- **Kích hoạt Reconciliation Job** `<<include>>` **Chọn ngày đối soát**
- **Kích hoạt Reconciliation Job** `<<include>>` **Xác nhận chạy đối soát**
- **Xem danh sách Reconciliation Jobs** `<<extend>>` **Xem chi tiết Reconciliation Job** (UC07.7) — chỉ khi click vào một job

| Use Case con | Actor | Quan hệ | Mô tả |
|---|---|---|---|
| Chọn khoảng thời gian đối soát | ADMIN | `<<include>>` từ Kích hoạt Reconciliation Job | UC này cho phép ADMIN nhập period_start và period_end để xác định phạm vi giao dịch PENDING cần kiểm tra |
| Xác nhận chạy đối soát | ADMIN | `<<include>>` từ Kích hoạt Reconciliation Job | UC này cho phép ADMIN xác nhận khởi chạy job — hệ thống đánh dấu PENDING_TIMEOUT các giao dịch vượt quá pending_timeout_minutes |

---

### UC08 – Analyst Module

#### Chi tiết: Quản lý Ngưỡng Phân loại (ANALYST)

ANALYST tương tác qua giao diện cấu hình mô hình:
1. Xem ngưỡng phân loại đang áp dụng (UC08.1) — hiển thị giá trị hiện hành của cả hai mô hình
2. Chọn loại ngưỡng cần cập nhật: Fraud (UC08.2) hoặc PD Score (UC08.3)
3. Nhập giá trị mới và xác nhận — thay đổi có hiệu lực ngay

**Ràng buộc nghiệp vụ:** Chỉ ANALYST được cập nhật; MANAGER/ADMIN chỉ xem. Mọi thay đổi ghi Audit Log.

**Quan hệ use case con:**
- **Cập nhật ngưỡng Fraud Score** `<<include>>` **Xem ngưỡng phân loại hiện hành** — phải xem giá trị hiện tại trước
- **Cập nhật ngưỡng PD Score** `<<include>>` **Xem ngưỡng phân loại hiện hành** — phải xem giá trị hiện tại trước

| Use Case con | Actor | Quan hệ | Mô tả |
|---|---|---|---|
| Xem ngưỡng phân loại hiện hành | ANALYST | UC08.1 | UC này cho phép xem reject_threshold, review_threshold (Fraud) và risk_high_threshold, risk_medium_threshold (PD Score) đang áp dụng |
| Nhập giá trị ngưỡng Fraud mới | ANALYST | `<<include>>` từ Cập nhật ngưỡng Fraud | UC này cho phép ANALYST nhập reject_threshold và review_threshold mới (0.0–1.0, reject > review) và xác nhận lưu |
| Nhập giá trị ngưỡng PD Score mới | ANALYST | `<<include>>` từ Cập nhật ngưỡng PD Score | UC này cho phép ANALYST nhập risk_high_threshold và risk_medium_threshold mới (risk_high < risk_medium) và xác nhận lưu |

---

#### Chi tiết: Xem Hiệu suất Mô hình (ANALYST, MANAGER, ADMIN)

ANALYST, MANAGER, ADMIN xem các metric đánh giá hiệu suất mô hình AI:
1. Chọn mô hình: Fraud Detection (UC08.4) hoặc PD Score (UC08.5)
2. Chọn khoảng thời gian phân tích
3. Xem biểu đồ và số liệu thống kê

**Quan hệ use case con:**
- **Xem hiệu suất mô hình Fraud** `<<extend>>` **Lọc theo khoảng thời gian**
- **Xem hiệu suất mô hình PD Score** `<<extend>>` **Lọc theo khoảng thời gian**

| Use Case con | Actor | Quan hệ | Mô tả |
|---|---|---|---|
| Xem metrics Fraud model | ANALYST | `<<include>>` từ UC08.4 | UC này cho phép xem: precision, recall, F1-score, AUC-ROC, tỉ lệ False Positive/Negative, phân phối fraud_score theo khoảng |
| Xem metrics PD Score model | ANALYST | `<<include>>` từ UC08.5 | UC này cho phép xem: phân bố pd_score, tỉ lệ default theo risk_level (LOW/MEDIUM/HIGH), Gini coefficient, so sánh với ngưỡng hiện tại |
| Lọc theo khoảng thời gian | ANALYST | `<<extend>>` từ UC08.4/UC08.5 | UC này cho phép chọn khoảng ngày phân tích (7 ngày / 30 ngày / 90 ngày / custom) |

---

#### Chi tiết: Quản lý Suppression Rules (ANALYST)

ANALYST tương tác qua giao diện quản lý suppression:
1. Xem danh sách rules hiện hành — bao gồm active và inactive (UC08.6)
2. Tùy chọn: tạo rule mới (UC08.7) → định nghĩa điều kiện lọc và ngưỡng
3. Tùy chọn: tắt rule đang active (UC08.8) — không xóa, hỗ trợ rollback

**Ràng buộc nghiệp vụ:** Mỗi suppression rule phải có `expires_at` để tự động hết hạn. Tạo và vô hiệu hóa đều ghi Audit Log.

| Use Case con | Actor | Quan hệ | Mô tả |
|---|---|---|---|
| Điền điều kiện suppression | ANALYST | `<<include>>` từ Tạo Suppression Rule | UC này cho phép ANALYST nhập: merchant_id (tùy chọn), channel (tùy chọn), max_amount, lý do suppression và ngày hết hạn |
| Xác nhận tạo rule | ANALYST | `<<include>>` từ Tạo Suppression Rule | UC này cho phép ANALYST xem lại cấu hình và xác nhận tạo — rule được kích hoạt ngay sau khi lưu |
| Xác nhận vô hiệu hóa rule | ANALYST | `<<include>>` từ Vô hiệu hóa Suppression Rule | UC này cho phép ANALYST xác nhận tắt rule — hệ thống đặt is_active = FALSE và ghi Audit Log |

---

#### Chi tiết: Quản lý Báo cáo Phân tích (ANALYST, MANAGER, ADMIN)

Luồng tạo và xét duyệt báo cáo:
1. ANALYST tạo báo cáo (UC08.9) → nhập nội dung Markdown → render PDF tự động → lưu DRAFT
2. ANALYST publish báo cáo → trạng thái PUBLISHED
3. MANAGER/ADMIN xem danh sách báo cáo PUBLISHED (UC08.10)
4. MANAGER/ADMIN xem chi tiết và tải PDF (UC08.11)
5. MANAGER/ADMIN xác nhận đã đọc (UC08.12) → trạng thái ACKNOWLEDGED

**Quan hệ use case con:**
- **Xem danh sách báo cáo** `<<extend>>` **Xem chi tiết và tải PDF báo cáo** (UC08.11)
- **Xác nhận (Acknowledge) báo cáo** `<<include>>` **Xem chi tiết và tải PDF báo cáo** — phải đọc trước khi ký nhận

| Use Case con | Actor | Quan hệ | Mô tả |
|---|---|---|---|
| Soạn nội dung Markdown | ANALYST | `<<include>>` từ Tạo báo cáo | UC này cho phép ANALYST nhập tiêu đề, kỳ báo cáo (weekly/monthly/quarterly), nội dung Markdown với bảng và biểu đồ |
| Render và lưu PDF | ANALYST | `<<include>>` từ Tạo báo cáo | UC này cho phép hệ thống tự động render Markdown thành PDF (fpdf2 + Arial Unicode) và lưu file — ANALYST xác nhận kết quả |
| Lọc danh sách báo cáo | ANALYST, MANAGER, ADMIN | `<<extend>>` từ Xem danh sách báo cáo | UC này cho phép lọc báo cáo theo trạng thái (DRAFT / PUBLISHED / ACKNOWLEDGED), kỳ báo cáo và tác giả |
| Tải file PDF báo cáo | ANALYST, MANAGER, ADMIN | `<<extend>>` từ Xem chi tiết báo cáo | UC này cho phép tải file PDF đã render về máy để lưu trữ hoặc trình lãnh đạo |
| Nhập ghi chú xác nhận | MANAGER, ADMIN | `<<include>>` từ Acknowledge báo cáo | UC này cho phép MANAGER/ADMIN nhập ghi chú xác nhận (tùy chọn) trước khi đổi trạng thái báo cáo sang ACKNOWLEDGED |

---

## 3. Ghi chú Tổng quát

### Bảng quy ước quan hệ

| Quan hệ | Ký hiệu UML | Áp dụng khi |
|---------|-------------|-------------|
| Association | `——` | Actor trực tiếp thực hiện use case |
| Generalization (Actor) | `◁——` | Actor con kế thừa toàn bộ quan hệ của actor cha |
| Generalization (UC) | `◁——` | UC con là dạng chuyên biệt hóa của UC cha trừu tượng |
| `<<include>>` | `- - >(include)` | UC cha bắt buộc gọi UC con mỗi lần thực thi |
| `<<extend>>` | `- - >(extend)` | UC con được kích hoạt có điều kiện, không bắt buộc |

### Kiểm tra tính hợp lệ

| Tiêu chí | Kết quả |
|----------|---------|
| Tên use case là động từ chỉ hành động của actor | ✅ Đăng nhập, Nộp, Xem, Xuất, Lọc, Nhận, Xác nhận, Truy vết, Kích hoạt, Cập nhật, Tạo, Vô hiệu hóa... |
| Mọi use case có ít nhất một actor liên kết | ✅ Trực tiếp qua Association hoặc gián tiếp qua UC có actor dùng `<<include>>`/`<<extend>>` |
| Không liệt kê xử lý tự động của hệ thống là use case | ✅ Chấm điểm AI, ghi Audit Log, phân luồng, DB Locking, JWT creation, PDF render... → không xuất hiện trong biểu đồ |
| Actor trừu tượng "Thành viên hệ thống" đúng vai trò | ✅ Chỉ dùng làm cha để chia sẻ 3 UC xác thực, không có use case riêng ngoài 3 UC đó |
| UC con của include/extend đều có actor (trực tiếp hoặc gián tiếp) | ✅ Mọi UC con đều có thể trace ngược lên một actor qua chuỗi quan hệ |
| OPERATOR được định nghĩa đúng là hệ thống tự động, không phải nhân viên | ✅ Chỉ có quyền nộp giao dịch và đơn vay; không có quyền phê duyệt, xem dashboard hoặc quản trị |
| ANALYST có đủ quyền truy cập dữ liệu để phân tích | ✅ Xem giao dịch, hồ sơ vay, simulate; quản lý ngưỡng, suppression rules, báo cáo; không có quyền phê duyệt hoặc quản trị tài khoản |
