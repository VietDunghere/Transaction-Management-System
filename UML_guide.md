Mô tả hệ thống bằng UML: use case
Các bước thực hiện
Tóm tắt các bước thực hiện để vẽ biểu đồ use case tổng quan:

Bước 1: Đề xuất các actor. Với mỗi người dùng, đề xuất thành một actor tương ứng. Nếu các actor có đặc điểm gì chung, có thể đề xuất actor trừu tượng thành actor cha của các actor tương ứng. Ngoài ra, cần xem xét cần có các actor gián tiếp tác động vào để thực hiện các chức năng hay không.
Bước 2: Đề xuất use case. Với mỗi chức năng, đề xuất thành một use case tương ứng
Bước 3: Mịn hóa các use case. Nếu có ít nhất 2 use case trùng nhau, cần xem xét gộp lại thành 1. Nếu gộp lại gây hiểu nhầm về số các actor tác động vào, thì có thể dùng use case trừu tượng cho các use case giống nhau, mỗi use case con liên quan đến nhóm các actor tương ứng mà thôi.
Tóm tắt các bước thực hiện để vẽ biểu đồ use case chi tiết:

Bước 1: Trích phần use case của chức năng tương ứng từ biểu đồ use case tổng quan.
Bước 2: Phân rã use case chính thành các use case con: mỗi giao diện (hoặc một số giao diện) tương tác với người dùng có thể đề xuất thành một use case con.
Bước 3: Xác định quan hệ của use case con với use case chính: generalization, include, hay extend.
Bước 4: Gộp các use case con tương tự nhau bằng cách dùng các use case trừu tượng tổng quát hơn.
Lưu ý tránh sai sót trong biểu đồ use case:

Tên use case phải là động từ chỉ hành động của actor. Không nên là động từ chỉ hành động của hệ thống. Cũng không nên là danh từ, tính từ…
Mỗi use case phải có tương tác với ít nhất một actor, có thể là trực tiếp hoặc gián tiếp: phải tồn tại ít nhất một đường đi từ một actor nào đó đến use case theo hướng: quan hệ include thì theo chiều mũi tên, quan hệ extend thì ngược chiều mũi tên, quan hệ kế thừa thì gộp lại.
Áp dụng
a. Biểu đồ use case tổng quan

Ta có thể đề xuất được các actor của hệ thống: sinh viên, giảng viên, quản lí, giáo vụ, và khảo thí. Tất cả đều có chức năng giống thành viên nên kế thừa từ thành viên. Riêng giảng viên, quản lí, giáo vụ, khảo thí còn kế thừa từ actor nhân viên của trường. Nhân viên kế thừa trực tiếp từ thành viên.

Các chức năng tương ứng với từng actor:

Thành viên: đăng nhập, đổi mật khẩu
Sinh viên: đăng kí học, xem lịch học, xem điểm. Ngoài ra có thể tham gia gián tiếp vào các chức năng: quản lí thông tin sinh viên, xuất bảng điểm cho sinh viên.
Giảng viên: đăng kí dạy, xem lịch dạy, nhập điểm, xem thống kê cá nhân. Ngoài ra có thể tham gia gián tiếp vào chức năng quản lí thông tin giảng viên.
Giáo vụ: quản lí thông tin sinh viên theo yêu cầu sinh viên, quản lí môn học, lớp học phần.
Khảo thí: xuất bảng điểm theo yêu cầu sinh viên.
Quản lí: quản lí thông tin chung, quản lí thông tin giảng viên theo yêu cầu giảng viên, xem các loại báo cáo thống kê..

Trong số các chức năng này, việc xem lịch học của sinh viên là tương tự chức năng xem lịch dạy của giảng viên. Nên hai use case này được cho kế thừa từ use case xem TKB. Như vậy, biểu đồ use case tổng quan của hệ thống được trình bày như Hình 3.1, với mô tả các use case như sau:

Đăng kí học: UC này cho phép sinh viên vào hệ thống đăng kí các môn học theo nguyện vọng cá nhân.
Xem lịch học: UC này cho phép sinh viên vào hệ thống xem lịch học cá nhân
Xem điểm: UC này cho phép sinh viên vào hệ thống xem kết quả các môn học của mình.
Đăng kí dạy: UC này cho phép giảng viên vào hệ thống để đăng kí lịch dạy của mình vào đầu mỗi kì học.
Xem lịch dạy: UC này cho phép giảng viên xem lịch dạy cá nhân
Nhập điểm: UC này cho phép giảng viên nhập điểm các lớp học phần do mình dạy
Xem thống kê cá nhân: UC này cho phép giảng viên xem các thống kê cá nhân
Quản lí thông tin giảng viên: UC này cho phép giáo vụ quản lí thông tin giảng viên theo yêu cầu của giảng viên tương ứng.
Quản lí thông tin sinh viên: UC này cho phép giáo vụ quản lí thông tin sinh viên theo yêu cầu từ sinh viên tương ứng.
Quản lí thông tin môn học: UC này cho phép giáo vụ quản lí thông tin các môn học
Quản lí thông tin lớp học phần: UC này cho phép giáo vụ quản lí thông tin các lớp học phần.
Xuất bảng điểm: UC này cho phép khảo thí xuất bảng điểm cho sinh viên theo yêu cầu từ sinh viên.
Xem thống kê: UC này cho phép nhân viên quản lí xem các loại báo cáo thống kê.
b. Use chi tiết của đăng kí học


Chức năng đăng kí học có các giao diện tương tác với sinh viên:

Đăng nhập -> đề xuất UC đăng nhập
Đăng kí -> đề xuất UC đăng kí
Chọn môn học -> đề xuất UC chọn môn học
Chọn lớp học phần -> đề xuất UC chọn lớp học phần
Đăng nhập, chọn môn học, chọn lớp học phần là bắt buộc mới hoàn thành được việc đăng kí, do đó UC đăng kí include các UC này.
Như vậy, biểu đồ UC chi tiết cho modul đăng kí học được trình bày trong Hình trên. Các UC được mô tả như sau:

Chọn môn học: UC này cho phép sinh viên chọn môn học để đăng kí học
Chọn lớp học phần: UC này cho phép sinh viên chọn lớp học phần để đăng kí học.
c. Use case chi tiết modul nhập điểm


Trong chức năng nhập điểm, giảng viên phải tương tác với các giao diện:

Đăng nhập -> thống nhất với UC đăng nhập
Chọn kì học + môn học -> đề xuất UC chọn môn học
Chọn lớp học phần -> đề xuất UC chọn lớp học phần
Nhập điểm chi tiết -> đề xuất UC nhập điểm chi tiết
Các UC trên đều bắt buộc thực hiện mới hoàn thành việc nhập điểm -> chúng đều bị chứa trong UC nhập điểm
Như vậy, biểu đồ UC chi tiết cho modul nhập điểm được trình bày trong hình trên. Trong đó các UC được mô tả như sau:

Chọn môn học: UC này cho phép giảng viên chọn môn học để nhập điểm
Chọn lớp học phần: UC này cho phép giảng viên chọn lớp học phần để nhập điểm
Nhập điểm chi tiết: UC cho phép giảng viên nhập/sửa điểm chi tiết từng đầu điểm thành phần của từng sinh viên trong một lớp học phần do mình dạy
d. Use case chi tiết cho modul xem thống kê loại học lực


Trong chức năng này, nhân viên quản lí có thể phải tương tác với các giao diện:

Đăng nhập -> thống nhất với UC đăng nhập
Xem thống kê loại học lực -> đề xuất UC xem TK loại học lực
Xem thống kê các sinh viên của 1 loại học lực -> đề xuất UC xem TK sinh viên của loại học lực.
Xem kết quả của một sinh viên -> đề xuất UC xem điểm các môn học của sinh viên
Xêm chi tiết một môn học của sinh viên -> đề xuất UC xem điểm chi tiết 1 môn học của sinh viên.
Các giao diện thống kê lần lượt theo dạng: giao diện sau là tùy chọn từ giao diện trước. Do đó, chúng có quan hệ mở rộng lần lượt cái sau từ cái trước.
Như vậy, biểu đồ UC chi tiết cho chức năng thống kê loại học lực được trình bày như trong hình vẽ. Trong đó, các UC chi tiết được mô tả như sau:

Xem TK loại học lực: UC này cho phép NVQL xem thống kê số lượng sinh viên trong mỗi loại học lực của một kì học
Xem TK sinh viên của một loại học lực: UC này cho phép NVQL xem TK kết quả các sinh viên của một loại học lực
Xem TK điểm của một sinh viên: UC này cho phép NVQL xem kết quả các môn học của một sinh viên trong một kì học
Xem kết quả một một học của một sinh viên: UC này cho phép NVQL xem kết quả chi tiết một môn học của một sinh viên.