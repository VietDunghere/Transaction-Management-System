# UML Use Case – Transaction Management System (TMS)

> Tài liệu này mô tả biểu đồ use case **tổng quan** và **chi tiết** cho hệ thống TMS, xây dựng theo phương pháp luận UML chuẩn: xác định actor → xác định use case → mịn hóa → phân rã chi tiết.

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
   - [UC03 – Hỗ trợ Quyết định Cho vay](#uc03--hỗ-trợ-quyết-định-cho-vay)
   - [UC04 – Xét duyệt Thủ công](#uc04--xét-duyệt-thủ-công)
   - [UC05 – Giám sát & Báo cáo](#uc05--giám-sát--báo-cáo)
   - [UC06 – Quản trị Hệ thống](#uc06--quản-trị-hệ-thống)
   - [UC07 – Data Engineering & Đối soát](#uc07--data-engineering--đối-soát-dữ-liệu)
3. [Ghi chú Tổng quát](#3-ghi-chú-tổng-quát)

---

## 1. Biểu đồ Use Case Tổng quan

### 1.1 Xác định Actor

Dựa trên phạm vi hệ thống TMS, các actor được xác định như sau:

**Actor trừu tượng (Abstract Actor):**

- **Thành viên hệ thống**: Bất kỳ tài khoản nào đã được cấp quyền vào hệ thống TMS. Đây là actor cha trừu tượng vì mọi nhóm người dùng đều chia sẻ các chức năng xác thực chung (đăng nhập, đăng xuất, đổi mật khẩu).

**Actor cụ thể (kế thừa từ Thành viên hệ thống):**

- **OPERATOR** (Nhân viên vận hành): Nhân viên chịu trách nhiệm nhập liệu — nộp giao dịch mới và hồ sơ đề nghị vay vốn vào hệ thống.
- **REVIEWER** (Nhân viên duyệt hồ sơ): Nhân viên tiếp nhận và xét duyệt thủ công các case giao dịch đáng ngờ do hệ thống chuyển sang.
- **MANAGER** (Quản lý): Người giám sát hoạt động hệ thống, theo dõi dashboard, báo cáo, audit log và kết quả đối soát dữ liệu.
- **ADMIN** (Quản trị hệ thống): Kỹ thuật viên quản trị tài khoản người dùng, vận hành ETL pipeline và theo dõi tính nhất quán dữ liệu.

**Quan hệ kế thừa giữa actor:**

OPERATOR, REVIEWER, MANAGER, ADMIN đều **kế thừa (generalization)** từ **Thành viên hệ thống**, vì tất cả đều được thực hiện ba chức năng chung: Đăng nhập, Đăng xuất, Đổi mật khẩu cá nhân.

```
        ┌──────────────────────────┐
        │   Thành viên hệ thống    │  ← Actor trừu tượng
        └──────────────────────────┘
               ▲    ▲    ▲    ▲
               │    │    │    │  (generalization)
        ┌──────┘  ┌─┘  ┌─┘  └──────┐
        │         │    │            │
   OPERATOR  REVIEWER MANAGER    ADMIN
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
| UC02.2 | Xem danh sách giao dịch | OPERATOR, REVIEWER, MANAGER, ADMIN |
| UC02.3 | Xem chi tiết giao dịch | OPERATOR, REVIEWER, MANAGER, ADMIN |
| UC03.1 | Nộp hồ sơ đề nghị vay vốn | OPERATOR |
| UC03.2 | Xem danh sách hồ sơ vay | MANAGER, ADMIN |
| UC03.3 | Xem chi tiết hồ sơ vay | MANAGER, ADMIN |
| UC04.1 | Xem danh sách case chờ xử lý | REVIEWER, MANAGER, ADMIN |
| UC04.2 | Nhận case (Assign) | REVIEWER |
| UC04.3 | Xem chi tiết case | REVIEWER, MANAGER, ADMIN |
| UC04.4 | Ra quyết định Phê duyệt / Từ chối | REVIEWER |
| UC05.1 | Xem Dashboard tổng quan | MANAGER, ADMIN |
| UC05.2 | Xem biểu đồ phân bố Fraud Score | MANAGER, ADMIN |
| UC05.3 | Xem báo cáo giao dịch | MANAGER, ADMIN |
| UC05.4 | Xuất báo cáo (CSV / PDF) | MANAGER, ADMIN |
| UC05.5 | Xem Audit Log hệ thống | MANAGER, ADMIN |
| UC05.6 | Truy vết lịch sử một giao dịch cụ thể | MANAGER, ADMIN |
| UC05.7 | Xem kết quả đối soát (Reconciliation) | MANAGER, ADMIN |
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
| UC07.6 | Xem danh sách Reconciliation Jobs | ADMIN, MANAGER |
| UC07.7 | Xem chi tiết Reconciliation Job | ADMIN, MANAGER |

---

### 1.3 Mịn hóa Use Case

> Theo phương pháp luận: nếu có ít nhất 2 use case **thao tác giống nhau**, xem xét gộp lại thành 1. Nếu gộp gây nhầm lẫn về actor (vì mỗi UC liên quan đến nhóm actor khác nhau), dùng **UC trừu tượng làm cha** và các UC cụ thể kế thừa từ đó.

---

#### Nhóm 1 — Cặp "Xem danh sách" và "Xem chi tiết" (6 cặp)

Trong hệ thống TMS, 6 cặp UC sau đây có **thao tác giống nhau**: người dùng browse danh sách → tùy chọn click một dòng để xem chi tiết.

| Cặp | "Xem danh sách" | "Xem chi tiết" |
|-----|-----------------|----------------|
| 1 | UC02.2 – Xem danh sách giao dịch | UC02.3 – Xem chi tiết giao dịch |
| 2 | UC03.2 – Xem danh sách hồ sơ vay | UC03.3 – Xem chi tiết hồ sơ vay |
| 3 | UC04.1 – Xem danh sách case chờ xử lý | UC04.3 – Xem chi tiết case |
| 4 | UC06.5 – Xem danh sách người dùng | UC06.6 – Xem chi tiết thông tin người dùng |
| 5 | UC07.3 – Xem ETL Logs | UC07.4 – Xem chi tiết một ETL Job |
| 6 | UC07.6 – Xem danh sách Reconciliation Jobs | UC07.7 – Xem chi tiết Reconciliation Job |

**Phân tích — có thể gộp không?**

Xét gộp nhóm "Xem danh sách": 6 UC này trông giống nhau về thao tác (duyệt danh sách, phân trang), nhưng **actor khác nhau** (UC02.2 có 4 actor; UC07.3 chỉ có ADMIN), và **đối tượng dữ liệu khác nhau** hoàn toàn (giao dịch ≠ hồ sơ vay ≠ case ≠ người dùng ≠ ETL Job ≠ Recon Job). Nếu gộp thành một UC trừu tượng chung sẽ không phản ánh đúng ngữ nghĩa nghiệp vụ và gây nhầm lẫn về phạm vi quyền truy cập.

Xét gộp nhóm "Xem chi tiết": Tương tự — đối tượng khác nhau, actor khác nhau, màn hình hiển thị khác nhau.

**Quyết định: Giữ nguyên 12 UC riêng biệt.** Xác định quan hệ giữa từng cặp là **<<extend>>**: mỗi "Xem chi tiết" là mở rộng **có điều kiện** từ "Xem danh sách" tương ứng — chỉ xảy ra khi người dùng chủ động click vào một dòng cụ thể trong danh sách.

**Quan hệ sau mịn hóa (tất cả 6 cặp):**

| UC con (<<extend>>) | Extend từ | Điều kiện kích hoạt |
|---------------------|-----------|---------------------|
| UC02.3 Xem chi tiết giao dịch | UC02.2 Xem danh sách giao dịch | Người dùng click vào một dòng giao dịch |
| UC03.3 Xem chi tiết hồ sơ vay | UC03.2 Xem danh sách hồ sơ vay | Người dùng click vào một dòng hồ sơ vay |
| UC04.3 Xem chi tiết case | UC04.1 Xem danh sách case | Người dùng click vào một dòng case |
| UC06.6 Xem chi tiết thông tin người dùng | UC06.5 Xem danh sách người dùng | Người dùng click vào tên một tài khoản |
| UC07.4 Xem chi tiết một ETL Job | UC07.3 Xem ETL Logs | ADMIN click vào một dòng kết quả ETL |
| UC07.7 Xem chi tiết Reconciliation Job | UC07.6 Xem danh sách Reconciliation Jobs | ADMIN/MANAGER click vào một dòng kết quả đối soát |

---

#### Nhóm 2 — "Xem danh sách" có thao tác "Lọc" đi kèm

Ở mỗi màn hình danh sách, người dùng **có thể** áp dụng bộ lọc — nhưng không bắt buộc. Đây là thao tác tùy chọn, áp dụng cho 5 màn hình danh sách:

| "Xem danh sách" | Thao tác "Lọc" tương ứng |
|-----------------|--------------------------|
| UC02.2 Xem danh sách giao dịch | Lọc theo trạng thái, kênh, khoảng fraud_score, thời gian |
| UC03.2 Xem danh sách hồ sơ vay | Lọc theo mức rủi ro (LOW/MEDIUM/HIGH), thời gian |
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
- Reconciliation: so sánh số liệu 3 chiều (OLTP / Lake / Warehouse)

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

Cả hai UC cùng actor OPERATOR, cùng thao tác tổng quát là "điền form → xác nhận → nhận kết quả AI".

**Phân tích:** Dù quy trình bề ngoài giống nhau, hai UC này:
- Có **đối tượng dữ liệu khác nhau** hoàn toàn (transaction vs loan application)
- Có **output khác nhau** (fraud_score + APPROVED/REJECTED/MANUAL_REVIEW vs PD Score + LOW/MEDIUM/HIGH)
- Dẫn đến **luồng nghiệp vụ khác nhau** (fraud routing vs loan advisory)

Tạo UC trừu tượng "Nộp dữ liệu vào hệ thống" sẽ không có giá trị ngữ nghĩa và gây hiểu nhầm.

**Quyết định: Giữ nguyên 2 UC riêng biệt.**

---

#### Tổng hợp sau mịn hóa — Bảng toàn bộ quan hệ UC trong sơ đồ tổng quan

| UC | Tên Use Case | Actor | Quan hệ với UC khác |
|----|-------------|-------|---------------------|
| UC01.1 | Đăng nhập | Thành viên hệ thống | — |
| UC01.2 | Đăng xuất | Thành viên hệ thống | — |
| UC01.3 | Đổi mật khẩu cá nhân | Thành viên hệ thống | — |
| UC02.1 | Nộp giao dịch mới | OPERATOR | — |
| UC02.2 | Xem danh sách giao dịch | OPERATOR, REVIEWER, MANAGER, ADMIN | UC02.3 <<extend>> UC02.2 |
| UC02.3 | Xem chi tiết giao dịch | OPERATOR, REVIEWER, MANAGER, ADMIN | <<extend>> UC02.2 |
| UC03.1 | Nộp hồ sơ đề nghị vay vốn | OPERATOR | — |
| UC03.2 | Xem danh sách hồ sơ vay | MANAGER, ADMIN | UC03.3 <<extend>> UC03.2 |
| UC03.3 | Xem chi tiết hồ sơ vay | MANAGER, ADMIN | <<extend>> UC03.2 |
| UC04.1 | Xem danh sách case chờ xử lý | REVIEWER, MANAGER, ADMIN | UC04.3 <<extend>> UC04.1 |
| UC04.2 | Nhận case (Assign) | REVIEWER | — |
| UC04.3 | Xem chi tiết case | REVIEWER, MANAGER, ADMIN | <<extend>> UC04.1 |
| UC04.4 | Ra quyết định Phê duyệt / Từ chối | REVIEWER | — |
| UC05.1 | Xem Dashboard tổng quan | MANAGER, ADMIN | UC05.2 <<extend>> UC05.1 |
| UC05.2 | Xem biểu đồ phân bố Fraud Score | MANAGER, ADMIN | <<extend>> UC05.1 |
| UC05.3 | Xem báo cáo giao dịch | MANAGER, ADMIN | UC05.4 <<include>> UC05.3 |
| UC05.4 | Xuất báo cáo (CSV / PDF) | MANAGER, ADMIN | <<include>> UC05.3 |
| UC05.5 | Xem Audit Log hệ thống | MANAGER, ADMIN | UC05.6 <<extend>> UC05.5 |
| UC05.6 | Truy vết lịch sử một giao dịch cụ thể | MANAGER, ADMIN | <<extend>> UC05.5 |
| UC05.7 | Xem kết quả đối soát (Reconciliation) | MANAGER, ADMIN | — |
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
| UC07.6 | Xem danh sách Reconciliation Jobs | ADMIN, MANAGER | UC07.7 <<extend>> UC07.6 |
| UC07.7 | Xem chi tiết Reconciliation Job | ADMIN, MANAGER | <<extend>> UC07.6 |

> **Lưu ý đọc bảng quan hệ:**
> - `UC_X <<extend>> UC_Y` → UC_X **mở rộng** UC_Y (xảy ra có điều kiện, tùy chọn, kích hoạt từ UC_Y)
> - `UC_X <<include>> UC_Y` → UC_X **bao gồm bắt buộc** UC_Y (mỗi lần UC_X thực thi đều gọi UC_Y)
> - `UC_X generalization → UC_Y` → UC_X là **dạng chuyên biệt hóa** của UC_Y trừu tượng
> - Chiều mũi tên trong UML: `<<extend>>` hướng **từ UC con về UC cha** (ngược chiều gọi); `<<include>>` hướng **từ UC cha đến UC con** (cùng chiều gọi)

**Kết quả:** 33 UC nghiệp vụ + 1 UC trừu tượng (UC06.A), tổ chức thành **7 nhóm UC**, liên kết với **5 actor** (1 trừu tượng + 4 cụ thể), 8 cặp quan hệ <<extend>>, 1 quan hệ <<include>>, 1 cặp generalization UC.

---

### 1.4 Mô tả Actor và Use Case

#### Mô tả Actor

| Actor | Loại | Kế thừa từ | Mô tả |
|-------|------|-----------|-------|
| Thành viên hệ thống | Trừu tượng | — | Bất kỳ người dùng có tài khoản hợp lệ trong TMS |
| OPERATOR | Cụ thể | Thành viên hệ thống | Nhân viên nhập liệu giao dịch và hồ sơ vay |
| REVIEWER | Cụ thể | Thành viên hệ thống | Nhân viên xét duyệt case thủ công |
| MANAGER | Cụ thể | Thành viên hệ thống | Quản lý theo dõi hoạt động và báo cáo |
| ADMIN | Cụ thể | Thành viên hệ thống | Quản trị viên kỹ thuật toàn hệ thống |

---

#### Mô tả Use Case theo nhóm

**UC01 – Xác thực & Quản lý Phiên làm việc**

| Mã UC | Use Case | Actor | Mô tả |
|-------|----------|-------|-------|
| UC01.1 | Đăng nhập | Thành viên hệ thống | UC này cho phép người dùng đăng nhập vào TMS bằng username và password để nhận JWT token truy cập hệ thống |
| UC01.2 | Đăng xuất | Thành viên hệ thống | UC này cho phép người dùng kết thúc phiên làm việc và vô hiệu hóa JWT token hiện tại |
| UC01.3 | Đổi mật khẩu cá nhân | Thành viên hệ thống | UC này cho phép người dùng thay đổi mật khẩu cá nhân sau khi xác minh mật khẩu cũ và đáp ứng chính sách độ mạnh |

---

**UC02 – Quản lý Giao dịch**

| Mã UC | Use Case | Actor | Mô tả |
|-------|----------|-------|-------|
| UC02.1 | Nộp giao dịch mới | OPERATOR | UC này cho phép OPERATOR nhập và gửi một giao dịch ngân hàng vào hệ thống để chấm điểm gian lận và phân luồng tự động |
| UC02.2 | Xem danh sách giao dịch | OPERATOR, REVIEWER, MANAGER, ADMIN | UC này cho phép người dùng xem danh sách giao dịch trong hệ thống (OPERATOR chỉ thấy giao dịch do chính mình nộp) |
| UC02.3 | Xem chi tiết giao dịch | OPERATOR, REVIEWER, MANAGER, ADMIN | UC này cho phép người dùng xem toàn bộ thông tin của một giao dịch: fraud_score, trạng thái, lý do phân loại, và mã case liên quan nếu có |

---

**UC03 – Hỗ trợ Quyết định Cho vay (Loan Simulator)**

| Mã UC | Use Case | Actor | Mô tả |
|-------|----------|-------|-------|
| UC03.1 | Nộp hồ sơ đề nghị vay vốn | OPERATOR | UC này cho phép OPERATOR nhập thông tin tín dụng của khách hàng để hệ thống tính PD Score và phân loại mức rủi ro (LOW / MEDIUM / HIGH) |
| UC03.2 | Xem danh sách hồ sơ vay | MANAGER, ADMIN | UC này cho phép MANAGER và ADMIN xem danh sách các hồ sơ vay đã được nộp, lọc theo trạng thái và mức rủi ro |
| UC03.3 | Xem chi tiết hồ sơ vay | MANAGER, ADMIN | UC này cho phép xem toàn bộ thông tin hồ sơ vay kèm kết quả PD Score và phân loại rủi ro từ mô hình AI |

---

**UC04 – Xét duyệt Thủ công (Manual Case Management)**

| Mã UC | Use Case | Actor | Mô tả |
|-------|----------|-------|-------|
| UC04.1 | Xem danh sách case chờ xử lý | REVIEWER, MANAGER, ADMIN | UC này cho phép xem danh sách các case đang ở trạng thái OPEN (chưa ai nhận) hoặc ASSIGNED (đã nhận nhưng chưa quyết định) |
| UC04.2 | Nhận case (Assign) | REVIEWER | UC này cho phép REVIEWER chọn một case chưa có người xử lý và nhận về tên mình để tiến hành xét duyệt |
| UC04.3 | Xem chi tiết case | REVIEWER, MANAGER, ADMIN | UC này cho phép xem toàn bộ thông tin của một case: thông tin giao dịch liên quan, fraud_score, lịch sử trạng thái và người phụ trách |
| UC04.4 | Ra quyết định Phê duyệt / Từ chối | REVIEWER | UC này cho phép REVIEWER đưa ra quyết định cuối cùng (APPROVED / REJECTED) cho case đã nhận, kèm ghi chú lý do bắt buộc |

---

**UC05 – Giám sát & Báo cáo**

| Mã UC | Use Case | Actor | Mô tả |
|-------|----------|-------|-------|
| UC05.1 | Xem Dashboard tổng quan | MANAGER, ADMIN | UC này cho phép xem tổng hợp số liệu KPI hoạt động hệ thống (tổng giao dịch, tỉ lệ phê duyệt, tỉ lệ gian lận, case tồn đọng) theo khoảng thời gian, dữ liệu từ Data Warehouse |
| UC05.2 | Xem biểu đồ phân bố Fraud Score | MANAGER, ADMIN | UC này cho phép xem biểu đồ histogram phân bố fraud_score của các giao dịch theo dải điểm, để đánh giá hiệu quả mô hình AI |
| UC05.3 | Xem báo cáo giao dịch | MANAGER, ADMIN | UC này cho phép tra cứu danh sách giao dịch từ Data Warehouse với các điều kiện lọc: khoảng thời gian, trạng thái, kênh, ngưỡng fraud_score |
| UC05.4 | Xuất báo cáo (CSV / PDF) | MANAGER, ADMIN | UC này cho phép xuất toàn bộ dữ liệu báo cáo đang xem ra file CSV hoặc PDF để lưu trữ và báo cáo kiểm toán |
| UC05.5 | Xem Audit Log hệ thống | MANAGER, ADMIN | UC này cho phép xem toàn bộ nhật ký hành động nghiệp vụ trong hệ thống (actor, hành động, đối tượng bị tác động, giá trị trước/sau) |
| UC05.6 | Truy vết lịch sử một giao dịch cụ thể | MANAGER, ADMIN | UC này cho phép xem toàn bộ timeline trạng thái của một giao dịch: khi nào tạo, ai xét duyệt, lý do quyết định, trạng thái thay đổi như thế nào |
| UC05.7 | Xem kết quả đối soát (Reconciliation) | MANAGER, ADMIN | UC này cho phép xem danh sách và chi tiết kết quả các lần đối soát dữ liệu 3 chiều (OLTP / Data Lake / Warehouse) |

---

**UC06 – Quản trị Hệ thống (User Management)**

| Mã UC | Use Case | Actor | Mô tả |
|-------|----------|-------|-------|
| UC06.1 | Tạo tài khoản người dùng mới | ADMIN | UC này cho phép ADMIN tạo tài khoản mới cho nhân viên với thông tin cơ bản (họ tên, email, username, mật khẩu tạm, vai trò) |
| UC06.2 | Vô hiệu hóa tài khoản | ADMIN | UC này cho phép ADMIN khóa tài khoản nhân viên (is_active = FALSE), ngăn đăng nhập mới và thu hồi phiên đang chạy |
| UC06.3 | Kích hoạt lại tài khoản | ADMIN | UC này cho phép ADMIN mở lại tài khoản đã bị vô hiệu hóa (is_active = TRUE) |
| UC06.4 | Gán / Thay đổi vai trò người dùng | ADMIN | UC này cho phép ADMIN gán hoặc thay đổi vai trò (OPERATOR / REVIEWER / MANAGER / ADMIN) của một người dùng |
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
| UC07.5 | Kích hoạt Reconciliation Job | ADMIN | UC này cho phép ADMIN khởi chạy thủ công job đối soát 3 chiều (OLTP / Data Lake / Warehouse) cho một ngày cụ thể |
| UC07.6 | Xem danh sách Reconciliation Jobs | ADMIN, MANAGER | UC này cho phép xem danh sách kết quả các lần đối soát: ngày chạy, trạng thái (MATCH / MISMATCH / FAILED), số liệu 3 nguồn |
| UC07.7 | Xem chi tiết Reconciliation Job | ADMIN, MANAGER | UC này cho phép xem chi tiết một lần đối soát: so sánh COUNT và SUM từ 3 nguồn, thông tin chênh lệch nếu MISMATCH |

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

Đây là use case cốt lõi của hệ thống. Người dùng tương tác qua các màn hình:
1. Form nhập giao dịch → điền thông tin
2. Xem lại và xác nhận gửi
3. Nhận kết quả phân loại tức thì
4. Tùy chọn: click "Xem chi tiết" để xem bản ghi đã tạo

**Quan hệ use case con:**
- **Nộp giao dịch mới** `<<include>>` **Điền thông tin giao dịch**
- **Nộp giao dịch mới** `<<include>>` **Xác nhận và gửi giao dịch**
- **Nộp giao dịch mới** `<<include>>` **Xem kết quả phân loại giao dịch**
- **Nộp giao dịch mới** `<<extend>>` **Xem chi tiết giao dịch** (chỉ khi người dùng click "Xem thêm")

| Use Case con | Actor | Quan hệ | Mô tả |
|---|---|---|---|
| Điền thông tin giao dịch | OPERATOR | `<<include>>` từ Nộp giao dịch mới | UC này cho phép OPERATOR nhập các trường bắt buộc: mã khách hàng, số tiền, loại tiền tệ, tên merchant, kênh giao dịch (ATM / POS / ONLINE) |
| Xác nhận và gửi giao dịch | OPERATOR | `<<include>>` từ Nộp giao dịch mới | UC này cho phép OPERATOR xem lại tóm tắt thông tin đã nhập và xác nhận gửi chính thức vào hệ thống |
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
| Lọc danh sách giao dịch | OPERATOR, REVIEWER, MANAGER, ADMIN | `<<extend>>` từ Xem danh sách giao dịch | UC này cho phép người dùng thu hẹp kết quả theo: khoảng thời gian, trạng thái, kênh giao dịch (ATM / POS / ONLINE), ngưỡng fraud_score |

---

### UC03 – Hỗ trợ Quyết định Cho vay

#### Chi tiết: Nộp hồ sơ đề nghị vay vốn (OPERATOR)

Người dùng tương tác qua các màn hình:
1. Form nhập hồ sơ vay → điền thông tin tín dụng
2. Xác nhận gửi
3. Nhận kết quả PD Score và phân loại rủi ro

**Quan hệ use case con:**
- **Nộp hồ sơ đề nghị vay vốn** `<<include>>` **Điền thông tin tín dụng khách hàng**
- **Nộp hồ sơ đề nghị vay vốn** `<<include>>` **Xác nhận và gửi hồ sơ vay**
- **Nộp hồ sơ đề nghị vay vốn** `<<include>>` **Xem kết quả chấm điểm rủi ro vay**

| Use Case con | Actor | Quan hệ | Mô tả |
|---|---|---|---|
| Điền thông tin tín dụng khách hàng | OPERATOR | `<<include>>` từ Nộp hồ sơ đề nghị vay vốn | UC này cho phép OPERATOR nhập: mã khách hàng, số tiền đề nghị vay, mục đích vay, thu nhập hàng tháng, tỉ lệ nợ (DTI), điểm tín dụng lịch sử |
| Xác nhận và gửi hồ sơ vay | OPERATOR | `<<include>>` từ Nộp hồ sơ đề nghị vay vốn | UC này cho phép OPERATOR xem lại thông tin và xác nhận gửi hồ sơ vào hệ thống để chấm điểm |
| Xem kết quả chấm điểm rủi ro vay | OPERATOR | `<<include>>` từ Nộp hồ sơ đề nghị vay vốn | UC này cho phép OPERATOR nhận ngay kết quả: PD Score (0.0–1.0) và mức độ rủi ro LOW / MEDIUM / HIGH từ mô hình AI |

---

#### Chi tiết: Xem danh sách hồ sơ vay

**Quan hệ use case con:**
- **Xem danh sách hồ sơ vay** `<<extend>>` **Lọc danh sách hồ sơ vay**
- **Xem danh sách hồ sơ vay** `<<extend>>` **Xem chi tiết hồ sơ vay** (UC03.3)

| Use Case con | Actor | Quan hệ | Mô tả |
|---|---|---|---|
| Lọc danh sách hồ sơ vay | MANAGER, ADMIN | `<<extend>>` từ Xem danh sách hồ sơ vay | UC này cho phép người dùng lọc hồ sơ vay theo trạng thái, mức rủi ro (LOW / MEDIUM / HIGH), khoảng thời gian nộp |

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

#### Chi tiết: Ra quyết định Phê duyệt / Từ chối (REVIEWER)

Người dùng tương tác qua các màn hình:
1. Danh sách case đã ASSIGNED (của mình)
2. Màn hình chi tiết case — đọc đầy đủ thông tin
3. Form quyết định — chọn APPROVE / REJECT + nhập ghi chú lý do
4. Xác nhận gửi quyết định
5. Tùy chọn (khi version conflict): màn hình cảnh báo và tải lại

**Quan hệ use case con:**
- **Ra quyết định Phê duyệt / Từ chối** `<<include>>` **Xem chi tiết case** (UC04.3) — phải đọc trước khi quyết định
- **Ra quyết định Phê duyệt / Từ chối** `<<include>>` **Nhập quyết định và ghi chú lý do**
- **Ra quyết định Phê duyệt / Từ chối** `<<include>>` **Xác nhận quyết định**
- **Ra quyết định Phê duyệt / Từ chối** `<<extend>>` **Tải lại thông tin case mới nhất** (chỉ khi hệ thống báo version conflict — 409 Conflict)

| Use Case con | Actor | Quan hệ | Mô tả |
|---|---|---|---|
| Nhập quyết định và ghi chú lý do | REVIEWER | `<<include>>` từ Ra quyết định | UC này cho phép REVIEWER chọn APPROVE hoặc REJECT và nhập ghi chú lý do nghiệp vụ (bắt buộc, tối thiểu 10 ký tự) |
| Xác nhận quyết định | REVIEWER | `<<include>>` từ Ra quyết định | UC này cho phép REVIEWER xác nhận gửi quyết định kèm version hiện tại của case (phục vụ Optimistic Locking — chống ghi đè đồng thời) |
| Tải lại thông tin case mới nhất | REVIEWER | `<<extend>>` từ Ra quyết định | UC này cho phép REVIEWER tải lại dữ liệu case khi hệ thống trả lỗi 409 Conflict do version không khớp — có người khác thay đổi case trước |

---

### UC05 – Giám sát & Báo cáo

#### Chi tiết: Xem Dashboard tổng quan (MANAGER, ADMIN)

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
| Xem KPI Cards và biểu đồ xu hướng | MANAGER, ADMIN | `<<include>>` từ Xem Dashboard | UC này cho phép người dùng xem các chỉ số: tổng giao dịch, tỉ lệ APPROVED / REJECTED / MANUAL_REVIEW, số case tồn đọng, tỉ lệ gian lận bị chặn |
| Lọc Dashboard theo thời gian | MANAGER, ADMIN | `<<extend>>` từ Xem Dashboard | UC này cho phép người dùng chọn khoảng thời gian (hôm nay / tuần này / tháng này) để cập nhật toàn bộ số liệu Dashboard |
| Xem chi tiết một KPI cụ thể | MANAGER, ADMIN | `<<extend>>` từ Xem Dashboard | UC này cho phép người dùng click vào một chỉ số KPI để xem số liệu chi tiết theo từng ngày trong khoảng đã chọn |

---

#### Chi tiết: Xem báo cáo giao dịch + Xuất báo cáo (MANAGER, ADMIN)

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
| Nhập điều kiện lọc báo cáo | MANAGER, ADMIN | `<<include>>` từ Xem báo cáo | UC này cho phép người dùng nhập điều kiện lọc: khoảng thời gian, trạng thái, kênh giao dịch, ngưỡng fraud_score |
| Xem chi tiết giao dịch trong báo cáo | MANAGER, ADMIN | `<<extend>>` từ Xem báo cáo | UC này cho phép người dùng click vào một dòng để xem thông tin chi tiết đầy đủ của giao dịch đó |
| Chọn định dạng và tải file | MANAGER, ADMIN | `<<include>>` từ Xuất báo cáo | UC này cho phép người dùng chọn định dạng (CSV hoặc PDF) và tải file xuống máy — file chứa toàn bộ dữ liệu theo điều kiện lọc hiện tại, không giới hạn phân trang |

---

#### Chi tiết: Xem Audit Log hệ thống (MANAGER, ADMIN)

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
| Lọc Audit Log | MANAGER, ADMIN | `<<extend>>` từ Xem Audit Log | UC này cho phép lọc log theo khoảng thời gian, actor, loại hành động (action), đối tượng bị tác động (entity type) |
| Xuất Audit Log | MANAGER, ADMIN | `<<extend>>` từ Xem Audit Log | UC này cho phép xuất danh sách audit events đang lọc ra file để phục vụ kiểm toán nội bộ hoặc báo cáo cơ quan giám sát |

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
| Chọn vai trò mới | ADMIN | `<<include>>` từ Gán / Thay đổi vai trò | UC này cho phép ADMIN chọn một vai trò mới (OPERATOR / REVIEWER / MANAGER / ADMIN) từ danh sách |
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
| Chọn ngày đối soát | ADMIN | `<<include>>` từ Kích hoạt Reconciliation Job | UC này cho phép ADMIN nhập ngày cụ thể cần đối soát 3 chiều giữa OLTP / Data Lake / Warehouse |
| Xác nhận chạy đối soát | ADMIN | `<<include>>` từ Kích hoạt Reconciliation Job | UC này cho phép ADMIN xác nhận khởi chạy job — hệ thống thu thập COUNT và SUM(amount) từ 3 nguồn rồi so sánh |

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
| Tên use case là động từ chỉ hành động của actor | ✅ Đăng nhập, Nộp, Xem, Xuất, Lọc, Nhận, Xác nhận, Truy vết, Kích hoạt... |
| Mọi use case có ít nhất một actor liên kết | ✅ Trực tiếp qua Association hoặc gián tiếp qua UC có actor dùng `<<include>>`/`<<extend>>` |
| Không liệt kê xử lý tự động của hệ thống là use case | ✅ Chấm điểm AI, ghi Audit Log, phân luồng, DB Locking, JWT creation... → không xuất hiện trong biểu đồ |
| Actor trừu tượng "Thành viên hệ thống" đúng vai trò | ✅ Chỉ dùng làm cha để chia sẻ 3 UC xác thực, không có use case riêng ngoài 3 UC đó |
| UC con của include/extend đều có actor (trực tiếp hoặc gián tiếp) | ✅ Mọi UC con đều có thể trace ngược lên một actor qua chuỗi quan hệ |
