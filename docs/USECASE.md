# Tài liệu Đặc tả UC -- Hệ thống Phân tích Rủi ro và Đánh giá Tài chính

## Mục lục

1. [Giới thiệu](#1-giới-thiệu)
2. [Biểu đồ UC tổng quan](#2-biểu-đồ-UC-tổng-quan)
   - [2.1 Xác định tác nhân](#21-xác-định-tác-nhân)
   - [2.2 Danh sách UC tổng quan](#22-danh-sách-UC-tổng-quan)
   - [2.3 Mô tả tác nhân](#23-mô-tả-tác-nhân)
   - [2.4 Mô tả UC tổng quan](#24-mô-tả-UC-tổng-quan)
3. [Biểu đồ UC phân rã](#3-biểu-đồ-UC-phân-rã)
   - [3.1 Xác thực và quản lý phiên làm việc](#31-xác-thực-và-quản-lý-phiên-làm-việc)
   - [3.2 Quản lý giao dịch](#32-quản-lý-giao-dịch)
   - [3.3 Hỗ trợ quyết định cho vay](#33-hỗ-trợ-quyết-định-cho-vay)
   - [3.4 Xét duyệt thủ công](#34-xét-duyệt-thủ-công)
   - [3.5 Giám sát và báo cáo](#35-giám-sát-và-báo-cáo)
   - [3.6 Quản trị hệ thống](#36-quản-trị-hệ-thống)
   - [3.7 Phân tích rủi ro](#37-phân-tích-rủi-ro)

---

## 1. Giới thiệu

Tài liệu này đặc tả các UC của Hệ thống Phân tích Rủi ro và Đánh giá Tài chính, bao gồm biểu đồ UC tổng quan và biểu đồ UC phân rã cho từng gói chức năng. Tài liệu được xây dựng theo phương pháp UML chuẩn.

---

## 2. Biểu đồ UC tổng quan

### 2.1 Xác định tác nhân

Hệ thống có 1 tác nhân trừu tượng, 3 tác nhân trừu tượng trung gian và 5 tác nhân cụ thể.

**Tác nhân trừu tượng gốc:**

- **Thành viên hệ thống**: Bất kỳ tài khoản nào đã được cấp quyền vào hệ thống. Đây là tác nhân cha trừu tượng, mọi nhóm người dùng đều kế thừa từ tác nhân này.

**Tác nhân cụ thể -- kế thừa từ Thành viên hệ thống:**

| Tác nhân | Mô tả |
|----------|-------|
| Operator | Hệ thống ngân hàng đối tác -- nộp giao dịch và đơn vay vào hệ thống qua giao diện lập trình |
| Reviewer | Nhân viên duyệt hồ sơ -- tiếp nhận và xét duyệt thủ công các case giao dịch đáng ngờ |
| Analyst | Chuyên viên phân tích rủi ro -- vận hành mô hình trí tuệ nhân tạo, điều chỉnh ngưỡng, theo dõi hiệu suất |
| Manager | Quản lý -- giám sát hoạt động hệ thống, theo dõi bảng điều khiển và nhật ký |
| Admin | Quản trị viên hệ thống -- quản lý tài khoản người dùng |

**Tác nhân trừu tượng trung gian:**

Trong sơ đồ tổng quan, các tác nhân cụ thể được nhóm thông qua các tác nhân trừu tượng trung gian để thể hiện vai trò chia sẻ:

| Tác nhân trung gian | Kế thừa bởi | Vai trò |
|---------------------|-------------|---------|
| Loan Staff | Operator, Reviewer | Nhóm các tác nhân liên quan đến nghiệp vụ cho vay |
| Transaction Manager | Analyst, Manager | Nhóm các tác nhân quản lý và xem giao dịch |
| Reporter | Analyst, Manager | Nhóm các tác nhân xem giám sát và báo cáo |

**Quan hệ kế thừa:**

- Operator, Reviewer, Analyst, Manager, Admin kế thừa từ Thành viên hệ thống.
- Operator, Reviewer kế thừa từ Loan Staff.
- Analyst, Manager kế thừa từ Transaction Manager.
- Analyst, Manager kế thừa từ Reporter.

---

### 2.2 Danh sách UC tổng quan

Sơ đồ tổng quan bao gồm 7 UC mức gói, mỗi UC đại diện cho một nhóm chức năng chính của hệ thống.

| STT | UC tổng quan | Tác nhân liên kết | Điểm mở rộng |
|-----|----------------------|-------------------|---------------|
| UC01 | Xác thực và quản lý phiên làm việc | Thành viên hệ thống | Đăng nhập, Đổi mật khẩu |
| UC02 | Quản lý giao dịch | Operator, Transaction Manager | Xem danh sách giao dịch, Nộp giao dịch mới |
| UC03 | Hỗ trợ quyết định cho vay | Operator, Loan Staff | Nộp hồ sơ, Phê duyệt, Xem danh sách hồ sơ |
| UC04 | Xét duyệt thủ công | Reviewer | Xem danh sách case, Phê duyệt/từ chối, Nhận case |
| UC05 | Giám sát và báo cáo | Reporter | Xem bảng điều khiển, Xem nhật ký |
| UC06 | Quản trị hệ thống | Admin | Xem danh sách người dùng, Thay đổi vai trò, Thay đổi trạng thái tài khoản, Tạo tài khoản |
| UC07 | Phân tích rủi ro | Analyst | Cập nhật ngưỡng phân loại, Xem ngưỡng phân loại, Xem điểm mô hình |

---

### 2.3 Mô tả tác nhân

| Tác nhân | Loại | Kế thừa từ | Mô tả chi tiết |
|----------|------|-----------|-----------------|
| Thành viên hệ thống | Trừu tượng | -- | Đại diện cho mọi tài khoản hợp lệ trong hệ thống, chia sẻ các chức năng xác thực chung |
| Operator | Cụ thể | Thành viên hệ thống | Hệ thống tự động của ngân hàng đối tác, nộp giao dịch và đơn vay qua giao diện lập trình. Không phải nhân viên con người |
| Reviewer | Cụ thể | Thành viên hệ thống | Nhân viên tín dụng, tiếp nhận và ra quyết định các giao dịch cần xét duyệt thủ công, đồng thời xét duyệt hồ sơ vay |
| Analyst | Cụ thể | Thành viên hệ thống | Chuyên viên phân tích rủi ro, vận hành mô hình trí tuệ nhân tạo, điều chỉnh ngưỡng phân loại, theo dõi hiệu suất mô hình |
| Manager | Cụ thể | Thành viên hệ thống | Quản lý giám sát hoạt động hệ thống, xem bảng điều khiển tổng quan và nhật ký hệ thống |
| Admin | Cụ thể | Thành viên hệ thống | Quản trị viên kỹ thuật, quản lý tài khoản người dùng trong toàn hệ thống |
| Loan Staff | Trừu tượng trung gian | -- | Nhóm các tác nhân tham gia nghiệp vụ cho vay |
| Transaction Manager | Trừu tượng trung gian | -- | Nhóm các tác nhân quản lý giao dịch |
| Reporter | Trừu tượng trung gian | -- | Nhóm các tác nhân xem giám sát và báo cáo |

---

### 2.4 Mô tả UC tổng quan

| Mã | UC | Mô tả |
|----|-----------|-------|
| UC01 | Xác thực và quản lý phiên làm việc | Gói chức năng xác thực danh tính và quản lý phiên làm việc, bao gồm đăng nhập và đổi mật khẩu |
| UC02 | Quản lý giao dịch | Gói chức năng nộp giao dịch mới từ ngân hàng đối tác và xem danh sách giao dịch trong hệ thống |
| UC03 | Hỗ trợ quyết định cho vay | Gói chức năng nộp hồ sơ đề nghị vay vốn, xem danh sách hồ sơ và phê duyệt hồ sơ vay |
| UC04 | Xét duyệt thủ công | Gói chức năng xem, nhận và ra quyết định phê duyệt hoặc từ chối các case giao dịch đáng ngờ |
| UC05 | Giám sát và báo cáo | Gói chức năng xem bảng điều khiển tổng quan và nhật ký hoạt động hệ thống |
| UC06 | Quản trị hệ thống | Gói chức năng quản lý tài khoản người dùng: tạo, thay đổi trạng thái, thay đổi vai trò và xem danh sách người dùng |
| UC07 | Phân tích rủi ro | Gói chức năng xem và cập nhật ngưỡng phân loại, xem điểm hiệu suất mô hình trí tuệ nhân tạo |

---

## 3. Biểu đồ UC phân rã

Phần này trình bày biểu đồ phân rã cho từng UC tổng quan. Mỗi UC tổng quan được phân rã thành các UC con với các quan hệ bao gồm bắt buộc và mở rộng có điều kiện.

---

### 3.1 Xác thực và quản lý phiên làm việc

**Tác nhân:** Thành viên hệ thống

**UC cha:** Xác thực và quản lý phiên làm việc

**Điểm mở rộng:** Đăng nhập, Đổi mật khẩu

**Danh sách UC con:**

| UC con | Tác nhân | Quan hệ với UC cha | Mô tả |
|----------------|----------|---------------------------|-------|
| Đăng nhập | Thành viên hệ thống | Mở rộng từ UC cha | Cho phép người dùng nhập tên đăng nhập và mật khẩu để truy cập hệ thống |
| Đổi mật khẩu | Thành viên hệ thống | Mở rộng từ UC cha | Cho phép người dùng thay đổi mật khẩu cá nhân sau khi xác minh mật khẩu cũ |

**Quan hệ giữa các UC con:**

- Đăng nhập bao gồm bắt buộc UC cha Xác thực và quản lý phiên làm việc

---

### 3.2 Quản lý giao dịch

**Tác nhân:** Operator, Analyst, Manager

**Tác nhân trung gian:** Transaction Manager -- Analyst và Manager kế thừa từ tác nhân này

**UC cha:** Quản lý giao dịch

**Điểm mở rộng:** Xem danh sách giao dịch, Nộp giao dịch mới

**Danh sách UC con:**

| UC con | Tác nhân | Quan hệ với UC cha | Mô tả |
|----------------|----------|---------------------------|-------|
| Nộp giao dịch mới | Operator | Mở rộng từ UC cha | Cho phép hệ thống ngân hàng đối tác gửi giao dịch vào hệ thống để chấm điểm gian lận và phân luồng tự động |
| Xem danh sách giao dịch | Transaction Manager | Mở rộng từ UC cha | Cho phép xem toàn bộ danh sách giao dịch trong hệ thống |
| Xem chi tiết giao dịch | Transaction Manager | Bao gồm bắt buộc từ Xem danh sách giao dịch | Cho phép xem thông tin chi tiết của một giao dịch cụ thể |

**Quan hệ giữa các UC con:**

- Xem danh sách giao dịch bao gồm bắt buộc Xem chi tiết giao dịch

---

### 3.3 Hỗ trợ quyết định cho vay

**Tác nhân:** Operator, Reviewer

**Tác nhân trung gian:** Loan Staff -- Operator và Reviewer kế thừa từ tác nhân này

**UC cha:** Hỗ trợ quyết định cho vay

**Điểm mở rộng:** Nộp hồ sơ, Phê duyệt, Xem danh sách hồ sơ

**Danh sách UC con:**

| UC con | Tác nhân | Quan hệ với UC cha | Mô tả |
|----------------|----------|---------------------------|-------|
| Nộp hồ sơ | Operator | Mở rộng từ UC cha | Cho phép hệ thống ngân hàng đối tác nộp đơn vay của khách hàng. Hệ thống tính điểm xác suất vỡ nợ và phân loại mức rủi ro |
| Xem danh sách hồ sơ | Loan Staff | Mở rộng từ UC cha | Cho phép xem toàn bộ danh sách hồ sơ vay trong hệ thống |
| Xem chi tiết hồ sơ | Loan Staff | Bao gồm bắt buộc từ Xem danh sách hồ sơ | Cho phép xem thông tin chi tiết của một hồ sơ vay cụ thể |
| Phê duyệt | Reviewer | Mở rộng từ UC cha | Cho phép nhân viên duyệt đưa ra quyết định phê duyệt hoặc từ chối cho đơn vay đang chờ xử lý |

**Quan hệ giữa các UC con:**

- Xem danh sách hồ sơ bao gồm bắt buộc Xem chi tiết hồ sơ
- Phê duyệt bao gồm bắt buộc UC cha Hỗ trợ quyết định cho vay

---

### 3.4 Xét duyệt thủ công

**Tác nhân:** Reviewer

**UC cha:** Xét duyệt thủ công

**Điểm mở rộng:** Xem danh sách case, Phê duyệt/từ chối, Nhận case

**Danh sách UC con:**

| UC con | Tác nhân | Quan hệ với UC cha | Mô tả |
|----------------|----------|---------------------------|-------|
| Nhận case | Reviewer | Mở rộng từ UC cha | Cho phép nhân viên duyệt chọn một case chưa có người xử lý và nhận về để tiến hành xét duyệt |
| Phê duyệt/từ chối | Reviewer | Mở rộng từ UC cha | Cho phép nhân viên duyệt đưa ra quyết định cuối cùng cho case đã nhận |
| Xem danh sách case | Reviewer | Mở rộng từ UC cha | Cho phép xem danh sách các case đang chờ xử lý hoặc đã được giao |
| Xem case cụ thể | Reviewer | Bao gồm bắt buộc từ Xem danh sách case | Cho phép xem thông tin chi tiết của một case cụ thể |

**Quan hệ giữa các UC con:**

- Xem danh sách case bao gồm bắt buộc Xem case cụ thể
- Phê duyệt/từ chối bao gồm bắt buộc Nhận case

---

### 3.5 Giám sát và báo cáo

**Tác nhân:** Analyst, Manager

**Tác nhân trung gian:** Reporter -- Analyst và Manager kế thừa từ tác nhân này

**UC cha:** Giám sát và báo cáo

**Điểm mở rộng:** Xem bảng điều khiển, Xem nhật ký

**Danh sách UC con:**

| UC con | Tác nhân | Quan hệ với UC cha | Mô tả |
|----------------|----------|---------------------------|-------|
| Xem bảng điều khiển | Reporter | Mở rộng từ UC cha | Cho phép xem tổng hợp số liệu hoạt động hệ thống |
| Xem biểu đồ tổng quan | Reporter | Bao gồm bắt buộc từ Xem bảng điều khiển | Cho phép xem các biểu đồ xu hướng và chỉ số tổng hợp trên bảng điều khiển |
| Xem chỉ số cụ thể | Reporter | Bao gồm bắt buộc từ Xem bảng điều khiển | Cho phép xem chi tiết từng chỉ số hiệu suất |
| Xem nhật ký | Manager | Mở rộng từ UC cha | Cho phép xem toàn bộ nhật ký hành động nghiệp vụ trong hệ thống |
| Xem chi tiết nhật ký hệ thống | Manager | Bao gồm bắt buộc từ Xem nhật ký | Cho phép xem chi tiết một bản ghi nhật ký, bao gồm tác nhân thực hiện, hành động, đối tượng bị tác động |

**Quan hệ giữa các UC con:**

- Xem bảng điều khiển bao gồm bắt buộc Xem biểu đồ tổng quan
- Xem bảng điều khiển bao gồm bắt buộc Xem chỉ số cụ thể
- Xem nhật ký bao gồm bắt buộc Xem chi tiết nhật ký hệ thống

---

### 3.6 Quản trị hệ thống

**Tác nhân:** Admin

**UC cha:** Quản trị hệ thống

**Điểm mở rộng:** Xem danh sách người dùng, Thay đổi vai trò, Thay đổi trạng thái tài khoản, Tạo tài khoản

**Danh sách UC con:**

| UC con | Tác nhân | Quan hệ với UC cha | Mô tả |
|----------------|----------|---------------------------|-------|
| Tạo tài khoản | Admin | Mở rộng từ UC cha | Cho phép quản trị viên tạo tài khoản mới cho nhân viên với thông tin cơ bản và vai trò ban đầu |
| Thay đổi trạng thái tài khoản | Admin | Mở rộng từ UC cha | Cho phép quản trị viên vô hiệu hóa hoặc kích hoạt lại tài khoản nhân viên |
| Thay đổi vai trò | Admin | Mở rộng từ UC cha | Cho phép quản trị viên gán hoặc thay đổi vai trò của một người dùng |
| Xem danh sách người dùng | Admin | Mở rộng từ UC cha | Cho phép xem toàn bộ danh sách tài khoản người dùng trong hệ thống |
| Xem chi tiết người dùng | Admin | Bao gồm bắt buộc từ Xem danh sách người dùng | Cho phép xem thông tin chi tiết của một tài khoản người dùng |

**Quan hệ giữa các UC con:**

- Xem danh sách người dùng bao gồm bắt buộc Xem chi tiết người dùng

---

### 3.7 Phân tích rủi ro

**Tác nhân:** Analyst

**UC cha:** Phân tích rủi ro

**Điểm mở rộng:** Cập nhật ngưỡng phân loại, Xem ngưỡng phân loại, Xem điểm mô hình

**Danh sách UC con:**

| UC con | Tác nhân | Quan hệ với UC cha | Mô tả |
|----------------|----------|---------------------------|-------|
| Xem điểm mô hình | Analyst | Mở rộng từ UC cha | Cho phép xem các chỉ số đánh giá hiệu suất của các mô hình trí tuệ nhân tạo |
| Cập nhật ngưỡng phân loại | Analyst | Mở rộng từ UC cha | Cho phép chuyên viên điều chỉnh ngưỡng phân loại của các mô hình. Thay đổi có hiệu lực ngay |
| Xem ngưỡng phân loại | Analyst | Mở rộng từ UC cha | Cho phép xem các giá trị ngưỡng phân loại đang áp dụng cho các mô hình |
