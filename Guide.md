# **Mô tả hệ thống bằng ngôn ngữ tự nhiên**

### **Các bước thực hiện**

* Bước 1: Giới thiệu mục đích hệ thống  
* Bước 2: Phạm vi hệ thống: ai được dùng phần mềm/hệ thống? Mỗi người vào vào hệ thống được phép thực hiện các chức năng nào?  
* Bước 3: Với mỗi chức năng mà người dùng được phép thực hiện ở bước 2, mô tả chi tiết hoạt động nghiệp vụ của chức năng đấy diễn ra như thế nào?  
* Bước 4: Các đối tượng nào được quản lí, xử lí trong hệ thống? Mỗi đối tượng cần dùng/quản lí các thuộc tính nào?  
* Bước 5: Quan hệ (số lượng) giữa các đối tượng đã nêu ở bước 4?

### **Áp dụng**

***Bước 1: Mục đích của hệ thống***: Hệ thống trang web phục vụ công tác quản lí đăng kí tín chỉ của sinh viên, đăng kí giảng dạy của giảng viên, quản lí điểm các môn học của một trường đại học.

***Bước 2: Phạm vi hệ thống***: Những người được vào hệ thống và chức năng mỗi người được thực hiện khi vào hệ thống này được quy định như sau:

* Thành viên hệ thống:  
  * Đăng nhập  
  * Đăng xuất  
  * Đổi mật khẩu cá nhân  
* Sinh viên:  
  * Được thực hiện các chức năng như thành viên  
  * Đăng kí học, sửa thông tin đăng kí của mình  
  * Xem lịch học của mình  
  * Xem điểm của mình  
* Giảng viên:  
  * Đăng kí dạy, sửa thông tin đăng kí dạy  
  * Nhập, sửa điểm các lớp mình dạy  
  * Xem lịch dạy của mình  
  * Xem thống kê liên quan đến các lớp mình dạy  
* Nhân viên giáo vụ:  
  * Quản lí thông tin sinh viên: thêm, xóa, sửa theo yêu cầu từ sinh viên  
  * Quản lí thông tin giảng viên theo yêu cầu từ giảng viên  
  * Quản lí thông tin môn học  
  * Quản lí thông tin lớp học phần  
* Nhân viên quản lí:  
  * Xem các loại thống kê  
* Nhân viên khảo thí:  
  * Xuất bảng điểm theo yêu cầu của sinh viên

Những chức năng không đề cập đến thì mặc định là không thuộc phạm vi của hệ thống.

***Bước 3: Hoạt động nghiệp vụ của các chức năng***: Theo nguyên tắc, mỗi chức năng liệt kê trong bước 2 đều phải mô tả chi tiết. Tuy nhiên, trong phạm vi tài liệu này, chỉ có ba chức năng được mô tả chi tiết vì đây là các chức năng được dùng để minh họa cho các bước phân tích, thiết kế từ đầu đến cuối. Các chức năng còn lại coi như bài tập cho người học.

* *Sinh viên đăng kí học*: Sinh viên đăng nhập vào hệ thống \-\> chọn chức năng đăng kí tín chỉ (đang trong thời gian mở đăng kí mới được chọn) \-\> chọn kì đăng kí \+ ngành học (có thể có sinh viên học đồng thời hai chuyên ngành) \-\> hệ thống hiện danh sách các môn học có thể đăng kí (mã, tên môn học, số tín chỉ, mô tả), các lớp học phần đã đăng kí rồi, nếu có \-\> Sinh viên chọn môn học \-\> hệ thống hiện danh sách các lớp học phần của môn học đấy (mã, tên, sĩ số tối đa, sĩ số hiện tại, phòng học, giảng viên, lịch học hàng tuần vào các ngày nào trong tuần, kíp nào trong ngày): chỉ active các nhóm mà không bị trùng lịch học với các môn đã chon trước, các nhóm bị trùng lịch thì chỉ xem, không chọn được \-\> Sinh viên chọn lớp học phần mình thích \-\> hệ thống quay lại trang bắt đầu đăng kí với lớp học phần vừa chọn được bổ sung vào danh sách các lớp học phần đã chọn. Sinh viên lặp lại các bước trên cho đến khi chọn đủ số tín chỉ trong ngưỡng cho phép \-\> nút lưu được active \-\> Sinh viên click lưu thì thông tin đăng kí mới chính thức được lưu vào hệ thống, hệ thống quay về giao diện chính của sinh viên.  
* *Giảng viên nhập điểm*: Giảng viên đăng nhập vào hệ thống \-\> chọn chức năng nhập điểm \-\> Chọn học kì đang active \-\> hệ thống hiện danh sách các môn học do giảng viên dạy của kì đã chọn (mã, tên, số tín chỉ, mô tả) \-\> Giảng viên click chọn môn học muốn nhập điểm \-\> Hệ thống hiện danh sách các lớp học phần do giảng viên dạy (mã, tên, sĩ số thực, phòng học, ngày học, kíp học) \-\> Giảng viên chọn 1 lớp học phần muốn nhập \-\> Hệ thống hiện danh sách các sinh viên đăng kí lớp học phần được chọn với điểm thành phần, nếu có: thứ tự, mã sinh viên, họ tên, các đầu điểm thành phần, điểm thi, cột trung bình môn và điểm chữ được tự tính sau khi nhập \-\> Giảng viên nhập đầu điểm muốn nhập cho tất cả sinh viên trong danh sách và click lưu \-\> hệ thống lưu điểm vào và quay về giao diện chính của giảng viên.  
* *Quản lí xem thống kê theo loại học lực*: Nhân viên quản lí đăng nhập vào hệ thống \-\> chọn chức năng xem thống kê \-\> hệ thống hiện giao diện chọn thông tin thống kê \-\> chọn thống kê loại học lực \-\> Hệ thống hiện giao diện thống kê loại học lực \-\> Quản lí chọn học kì muốn thống kê \-\> Kết quả thống kê hiện lên, mỗi loại học lực trên một dòng, xếp theo thứ tự cao nhất đến thấp nhất của loại học lực trong bảng đánh giá (Ưu tú, xuất sắc, giỏi, khá, trung bình, yếu kém): thứ tự, loại học lực, tổng số sinh viên đạt loại đó, điểm trung bình sinh viên trong nhóm đạt loại đó trong học kì đã chọn \-\> Quản lí click vào một loại học lực \-\> Hệ thống hiện danh sách các sinh viên đạt loại học lực đấy lên, xếp theo thứ tự các ngành học, đến thứ tự abc của tên sinh viên: thứ tự, mã sinh viên, họ và tên, ngành học, khóa học, tổng số tín chỉ của học kì, điểm trung bình của học kì \-\> Quản lí click vào một sinh viên danh sách \-\> Hệ thống hiện lên danh sách các môn và kết quả của sinh viên đã học trong học kì đó, xếp theo thứ tự abc của tên môn học: thứ tự, tên môn học, số tín chỉ, điểm trung bình môn đó của sinh viên. Dòng cuối là tổng số tín chỉ, điểm trung bình cả học kì của sinh viên \-\> Quản lí click vào một môn học trong danh sách \-\> Hệ thống hiện lên điểm chi tiết của môn học của sinh viên: mã môn, tên môn, tổng tín chỉ, các đầu điểm thành phần dạng bảng: tên đầu điểm thành phần, tỉ lệ % tính của đầu điểm thành phần, điểm của sinh viên. Dòng cuối là điểm trung bình môn của sinh viên trong môn học đó.

***Bước 4: Thông tin các đối tượng cần xử lí, quản lí***:

Nhóm các thông tin liên quan đến con người:

* Thành viên: tên đăng nhập, mật khẩu, họ tên, địa chỉ, ngày sinh, email, số điện thoại  
* Sinh viên: giống thành viên, có thêm: mã sinh viên. Theo mỗi ngành học còn có khóa học, ngành học  
* Nhân viên: giống thành viên, có thêm: vị trí công việc.  
* Nhân viên quản lí: giống nhân viên  
* Nhân viên giáo vụ: giống nhân viên  
* Nhân viên khảo thí: giống nhân viên  
* Giảng viên: giống nhân viên

Nhóm các thông tin liên quan đến cơ sở vật chất:

* Tòa nhà: tên, mô tả  
* Phòng học: tên, sức chứa tối đa, mô tả

Nhóm các thông tin liên quan đến đơn vị, tổ chức:

* Trường: tên, địa chỉ, mô tả  
* Khoa: tên, mô tả  
* Ngành học: tên, mô tả  
* Bộ môn: tên, mô tả

Nhóm các thông tin liên quan đến chuyên môn, vận hành:

* Năm học: tên, mô tả  
* Kì học: tên, mô tả  
* Tuần học: tên, mô tả  
* Ngày trong tuần: tên, mô tả  
* Kíp học trong ngày: tên, mô tả  
* Môn học: tên, số tín chỉ, mô tả  
* Lớp học phần: tên, mô tả, sĩ số tối đa, sĩ số hiện tại, giảng viên dạy, phòng học, tuần nào học ngày nào, kíp nào.

Nhóm thông tin liên quan đến thống kê:

* Thống kê theo loại học lực  
* Thống kê sinh viên theo kết quả học  
* Thống kê các môn học theo kết quả học  
* Thống kê giảng viên theo: số giờ dạy, kết quả học  
* Thống kê học kì theo số sinh viên

***Bước 5: Quan hệ giữa các đối tượng, thông tin***:

* Một trường có nhiều khoa  
* Một khoa có nhiều bộ môn  
* Một khoa có nhiều ngành học  
* Một bộ môn quản lí chuyên môn nhiều môn học  
* Một bộ môn có nhiều giảng viên  
* Một năm học có nhiều học kì  
* Một học kì liên quan đến nhiều năm học. Một năm học \+ một học kì tạo ra một kì học (kì học \# học kì).  
* Một kì học có nhiều môn học  
* Một môn học, vào một kì học, có nhiều lớp học phần  
* Một lớp học phần có thể học vào nhiều buổi, mỗi buổi có thể liên quan đến 1 tuần khác nhau, 1 ngày khác nhau, 1 kíp khác nhau, 1 phòng học khác nhau, 1 giảng viên khác nhau.  
* Một giảng viên có thể dạy nhiều môn học trong mỗi kì học  
* Một môn học, trong một kì học, giảng viên có thể dạy nhiều lớp học phần khác nhau, miễn sao không trùng lịch buổi nào.  
* Một lớp học phần, có thể có nhiều giảng viên dạy. Nhưng mỗi buổi học chỉ có một giảng viên dạy.  
* Một môn học có nhiều đầu điểm thành phần.  
* Mỗi đầu điểm thành phần, đối với mỗi môn học, có tỉ lệ % tính điểm nhất định.  
* Một tuần có thể có nhiều buổi dạy/học  
* Một ngày có thể có nhiều buổi học/dạy  
* Một kíp có thể có nhiều buổi học/dạy của nhiều lớp học phần khác nhau  
* Một phòng học có thể có nhiều lớp học phần vào học ở những buổi khác nhau.  
* Một sinh viên có thể đăng kí học nhiều ngành khác nhau (tối đa 2 ngành đồng thời).  
* Với mỗi ngành, sinh viên phải học một số môn nhất định, và điểm tính theo từng ngành. Các môn trùng nhau giữa các ngành thì sinh viên chỉ phải học 1 lần, qua là được.  
* Mỗi sinh viên, mỗi môn học, có một diểm trung bình môn.

