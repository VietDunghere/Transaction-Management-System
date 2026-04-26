# Use Case Tổng quan — Hệ thống HPTRRĐGTC (Sau tinh gọn)

> **Phiên bản tinh gọn:** Giảm từ 41 UC → 20 UC, từ 8 nhóm → 7 nhóm.
> Đã gộp các UC trùng lặp và cắt bỏ các UC không thuộc nghiệp vụ lõi.

## Actor

| Actor | Loại | Kế thừa từ |
|-------|------|-----------|
| Thành viên hệ thống | Trừu tượng | — |
| OPERATOR | Cụ thể | Thành viên hệ thống |
| REVIEWER | Cụ thể | Thành viên hệ thống |
| ANALYST | Cụ thể | Thành viên hệ thống |
| MANAGER | Cụ thể | Thành viên hệ thống |
| ADMIN | Cụ thể | Thành viên hệ thống |

---

## UC Tổng quan và UC Chi tiết

### UC01 — Xác thực & Quản lý Phiên làm việc

**Actor:** Thành viên hệ thống

| UC chi tiết | Actor |
|---|---|
| UC01.1 Đăng nhập | Thành viên hệ thống |
| UC01.2 Đăng xuất | Thành viên hệ thống |
| UC01.3 Đổi mật khẩu cá nhân | Thành viên hệ thống |

---

### UC02 — Quản lý Giao dịch

**Actor:** OPERATOR, ANALYST, MANAGER

| UC chi tiết | Actor |
|---|---|
| UC02.1 Nộp giao dịch mới | OPERATOR |
| UC02.2 Xem giao dịch | ANALYST, MANAGER |

---

### UC03 — Hỗ trợ Quyết định Cho vay

**Actor:** OPERATOR, REVIEWER

| UC chi tiết | Actor |
|---|---|
| UC03.1 Nộp hồ sơ đề nghị vay vốn | OPERATOR |
| UC03.2 Xem hồ sơ vay | OPERATOR, REVIEWER |
| UC03.3 Phê duyệt / Từ chối hồ sơ vay | REVIEWER |

---

### UC04 — Xét duyệt Thủ công

**Actor:** REVIEWER

| UC chi tiết | Actor |
|---|---|
| UC04.1 Xem case | REVIEWER |
| UC04.2 Nhận case (Assign) | REVIEWER |
| UC04.3 Ra quyết định Phê duyệt / Từ chối | REVIEWER |

---

### UC05 — Giám sát & Báo cáo

**Actor:** ANALYST, MANAGER, ADMIN

| UC chi tiết | Actor |
|---|---|
| UC05.1 Xem Dashboard tổng quan | ANALYST, MANAGER |
| UC05.2 Xem Audit Log hệ thống (bao gồm truy vết giao dịch) | MANAGER, ADMIN |

---

### UC06 — Quản trị Hệ thống

**Actor:** ADMIN, MANAGER (chỉ xem)

| UC chi tiết | Actor |
|---|---|
| UC06.1 Tạo tài khoản người dùng mới | ADMIN |
| UC06.2 Thay đổi trạng thái tài khoản | ADMIN |
| UC06.3 Gán / Thay đổi vai trò người dùng | ADMIN |
| UC06.4 Xem người dùng | MANAGER, ADMIN |

---

### UC07 — Phân tích Rủi ro (Analyst Module)

**Actor:** ANALYST

| UC chi tiết | Actor |
|---|---|
| UC07.1 Xem ngưỡng phân loại hiện hành | ANALYST |
| UC07.2 Cập nhật ngưỡng phân loại | ANALYST |
| UC07.3 Xem hiệu suất mô hình | ANALYST |
