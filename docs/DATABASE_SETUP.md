# Hướng dẫn Cài đặt và Thiết lập Oracle Database

Tài liệu này cung cấp các bước để thiết lập Oracle Database cho hệ thống **Transaction Management System** sau khi bạn đã cài đặt trực tiếp trên máy tính.

## 1. Yêu cầu hệ thống
- Oracle Database (phiên bản 19c - Enterprise/Standard/Express Edition) đã được cài đặt trên máy.
- Công cụ quản trị CSDL như DBeaver, SQL Developer hoặc DataGrip.
- Oracle SQL*Plus (nếu thao tác qua command line).

## 2. Thông tin Kết nối Cơ sở dữ liệu mặc định
Sau khi bạn đã cài đặt Oracle DB 19c thành công, các thông tin kết nối mặc định thường là:
- **Host**: `localhost`
- **Port**: `1521`
- **Service Name (hoặc SID)**: `orcl` 
- **Tài khoản Quản trị DB**: `SYS` hoặc `SYSTEM` (cần chọn Role là `SYSDBA`)
- **Mật khẩu**: (Mật khẩu bạn đã tạo lúc cài đặt Oracle DB)

*Lưu ý với 19c: Bạn nên ưu tiên kết nối thẳng vào Pluggable Database (PDB) như `ORCLPDB1` (hoặc `XEPDB1` với bản XE) để tạo các user và schema ứng dụng thay vì tạo trực tiếp ở container root (CDB$ROOT).*

## 3. Chạy Scripts Khởi tạo Dữ liệu (Setup)

Trình tự chạy các scripts là rất quan trọng để đảm bảo cấu trúc và phân quyền được áp dụng đúng.
Các file SQL nằm trong thư mục `backend/db/`.

1. Khởi chạy công cụ quản trị CSDL (DBeaver, SQL Developer...) và kết nối bằng tài khoản `SYS` hoặc `SYSTEM` với Role `SYSDBA` (trỏ đến PDB của bạn, ví dụ `ORCLPDB1`).
2. Mở schema hiện tại và thực thi các file theo trình tự sau:

### Bước 3.1: Tạo User và Cấp Quyền (Phân quyền Hệ thống)
Chạy file `Users.sql` đầu tiên. File này sẽ:
- Tạo role `PROJECT_ADMIN` quản lý kiến trúc.
- Tạo user `ADMIN` với password `123456` và gán schema quản lý.
- Cấp quota lưu trữ không giới hạn trên tablespace `USERS`.
- Định nghĩa các role nghiệp vụ: `OPERATOR`, `REVIEWER`, `MANAGER`, `IT_ADMIN`.

> **Chú ý quan trọng**: Từ bước này trở đi, bạn hãy **ngắt kết nối** khỏi tài khoản `SYS` và **tạo một kết nối mới bằng tài khoản `ADMIN`** (với mật khẩu `123456`) trên đúng Service Name đó để chạy các lệnh tạo bảng và dữ liệu mẫu dưới schema của `ADMIN`.

### Bước 3.2: Tạo Cấu trúc Bảng và Ràng buộc (ERD)
- Kết nối bằng user `ADMIN` (`ADMIN`/`123456`).
- Chạy file `ERD.sql` (hoặc các file DDL tương đương tạo bảng). 
- Đảm bảo thực thi tất cả các lệnh tạo `TABLE`, `PRIMARY KEY`, `FOREIGN KEY`, `SEQUENCE` báo thành công.

### Bước 3.3: Nạp Dữ liệu Mẫu (Fake Data)
- Tiếp tục ở user `ADMIN`.
- Chạy file `Fake_data.sql` để chèn các dữ liệu giả lập ban đầu cho các bảng danh mục (Master data), User test cho từng roles, và các giao dịch mẫu.

## 4. Cấu hình Kết nối ở Application (FastAPI)

Sau khi thiết lập xong DB, bạn cần cấu hình Backend để kết nối với cơ sở dữ liệu.
Trong file `backend/app/core/config.py` (hoặc file `.env`), thiết lập các biến môi trường kết nối.

```env
DB_USER=ADMIN
DB_PASSWORD=123456
DB_HOST=localhost
DB_PORT=1521
DB_SERVICE=orcl  # Cập nhật thành ORCL, XE, ORCLPDB1 hoặc XEPDB1 tùy theo cài đặt 19c của bạn
```

Chuỗi kết nối (Connection String) trong log / SQLAlchemy sẽ có dạng:
`oracle+cx_oracle://ADMIN:123456@localhost:1521/?service_name=ORCLPDB1`

## 5. Troubleshooting (Khắc phục sự cố)
- **Lỗi "ORA-65096: invalid common user or role name"**: Bạn đang kết nối vào Root Container (CDB$ROOT) thay vì PDB. Đảm bảo Service Name lúc kết nối là `ORCLPDB1` (hoặc tên PDB tương ứng) thay vì `ORCL` / `XE`.
- **Lỗi không đủ quyền (Insufficient Privileges)**: Đảm bảo script tạo bảng (`ERD.sql`) được chạy dưới user `ADMIN` chứ không phải một user chưa được cấp quyền `RESOURCE` hoặc quyền tạo bảng.
- **Lỗi không tìm thấy Service Name (ORA-12514)**: Kiểm tra lại tên Service Name của bạn, có thể chạy lệnh `lsnrctl status` trong command line Windows để xem các service đang chạy.
- **Lỗi trùng lặp dữ liệu / Constraint Violated**: Nếu cần làm lại từ đầu, hãy kết nối lại bằng `SYS` và chạy lệnh `DROP USER ADMIN CASCADE;` sau đó thực hiện lại từ Bước 3.1.