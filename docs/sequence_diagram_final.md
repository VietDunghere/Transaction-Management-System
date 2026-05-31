# 1. Xác thực và đăng nhập

Đăng nhập

1. Người dùng thực hiện đăng nhập ở giao diện LoginFRM

2. LoginFRM gọi hàm eventPerformed()

3. LoginFRM gọi lớp UserDAO

4. Lớp UserDAO gọi hàm checkLogin() để kiểm tra đầu vào 

5. Lớp UserDAO gọi lớp Users để kiểm tra tài khoản mật khẩu

6. Lớp Users tạo một đối tượng User(), 

7. Lớp User trả kết quả về UserDAO

8. Lớp UserDAO trả về thành công cho LoginFRM

9. Lớp LoginFRM gọi cho lớp HomeFRM để hiển thị

10.  HomeFRM khởi tạo 

11. Lớp HomeFRM hiển thị kết quả cho người dùng 

12.  UserDAO gọi AuditLogs DAO

Đổi mật khẩu 

1. Người dùng ở HomeFRM chọn nút đổi mật khẩu 

2. HomeFRM gọi eventPerformed()

3. HomeFRM gọi lớp ChangePasswordFRM để hiển thị

4. ChangePasswordFRM tự khởi tạo

5. ChangePasswordFRM hiển thị

6. Người dùng nhập các thông tin cần thiết và bấm xác nhận cho lớp ChangePasswordFRM

7. ChangePasswordFRM gọi eventPerformed()

8. Lớp ChangePasswordFRM gọi lớp UserDAO

9. Lớp UserDAO tự gọi hàm checkChangePassword()

10. Lớp UserDAO gọi lớp Users 

11. Lớp Users gọi setter 

12. Lớp Users trả kết quả về cho lớp UserDAO

13. Lớp UserDAO trả kết quả cho lớp ChangePasswordFRM

14. Lớp ChangePassword display kết quả cho người dùng

\



# 2. Quản lý giao dịch

Nộp giao dịch mới 

1. Tại giao TransactionFRM Operator chọn chức năng Submit Transaction

2. TransactionFRM gọi hàm eventPerformed() 

3. TransactionFRM gọi lớp AddTransactionFRM 

4. AddTransactionFRM tự khởi tạo

5. AddTransactionFRM display cho người dùng 

6. Người dùng nhập tên khách hàng vào 

7. AddTransactionFRM gọi lớp CustomerDAO()

8. Lớp CustomerDAO gọi hàm searchCostumer()

9. Lớp CustomerDAO gọi lớp Customers

10. Lớp Customers gọi getter

11.  Customers trả về cho lớp CustomerDAO

12. Lớp CustomerDAO trả kết quả tìm được về cho AddTransactionFRM 

13. AddTransactionFRM display cho người dùng 

14. Người dùng nhập tên merchant vào 

15. AddTransactionFRM gọi lớp MerchantDAO()

16. Lớp MerchantDAO gọi hàm searchMerchant()

17. Lớp MerchantDAO gọi lớp Merchants

18. Lớp Merchants gọi setter

19.  Merchants trẻ về cho lớp MerchantDAO

20. Lớp MerchantDAO trả kết quả tìm được về cho AddTransactionFRM 

21. AddTransactionFRM display cho người dùng 

22. Người dùng nhập tên channel vào 

23. AddTransactionFRM gọi lớp ChannelDAO()

24. Lớp ChannelDAO gọi hàm searchChannel()

25. Lớp ChannelDAO gọi lớp Channels

26. Lớp Channels tự gọi getter

27. Lớp Channels trả về cho ChannelDAO

28. Lớp ChannelDAO trả kết quả tìm được về cho AddTransactionFRM 

29. AddTransactionFRM display cho người dùng 

30.  Người dùng nhập CardNumber và Amount vào và ấn nút xác nhận

31. AddTransactionFRM gọi eventPerformed()

32. AddTransactionFRM gọi TransactionliveDAO

33.  TransactionliveDAO tự gọi hàm addTransaction() để lưu bản ghi giao dịch

34.  TransactionliveDAO gọi TransactionLive để ghi nhận dữ liệu

35. Transactionlive thực hiện Transactionlive() để lưu giao dịch

36.  Transactionlive trả lại về cho TransactionliveDAO

37. TransactionliveDAO gọi hàm ScoringTransaction() để chấm điểm và phân loại

38.  TransactionliveDAO gọi Transactionlive để cập nhật trạng thái giao dịch

39. Transactionlive thực hiện setter() để ghi nhận trạng thái giao dịch

40.  TransactionliveDAO gọi AuditLogDAO 

41. AuditLogDAO tự gọi hàm saveLog()

42.  AuditLogDAO gọi Users để tìm người thực hiện

43.  Users gọi getter() để tìm

44. Users gọi AuditLog để ghi lại hành động

45. AuditLog tự gọi AuditLog() để đóng gói thông tin

46. AuditLog trả về cho AuditLogDAO

47. AuditLogDAO trả về cho TransactionliveDAO

48.  TransactionliveDAO tổng hợp rồi trả về cho AddTransactionFRM

49.  AddTransactionFRM display cho người dùng 

Xem chi tiết giao dịch

1\. Tại giao diện chính, Operator chọn giao dịch để xem chi tiết.

2\. Trang TransactionFrm gọi hàm eventPerformed() để xử lý sự kiện nhập màn hình.

3\. Trang TransactionFrm gọi lớp thực thể Transactions yêu cầu lấy danh sách hồ sơ mặc định.

4\. Lớp Transactions thực hiện hàm khởi tạo Transactions() để đóng gói thông tin thực thể.

5\. Lớp Transactions trả kết quả về cho trang TransactionFrm.

6\. Trang TransactionFrm hiển thị danh sách hồ sơ cho Operator

7\. Operator thực hiện nhập thông tin bộ lọc và tiêu chí tìm kiếm (filter Transaction + sub).

8\. Trang TransactionFrm gọi hàm eventPerformed() để xử lý yêu cầu lọc.

9\. Trang TransactionFrm gọi lớp điều khiển TransactionliveDAO yêu cầu tìm kiếm theo tiêu chí.

10\. Lớp TransactionliveDAO thực hiện hàm filterTransaction() để lọc danh sách hồ sơ từ cơ sở dữ liệu.

11\. Hàm filterTransaction() gọi lớp thực thể Transactions để truy xuất dữ liệu phù hợp.

12\. Lớp Transactions thực hiện hàm Transactions() để đóng gói danh sách thực thể đã lọc.

13\. Lớp Transactions trả kết quả về cho hàm filterTransaction() của lớp TransactionliveDAO.

14\. Lớp TransactionliveDAO trả kết quả danh sách đã lọc về cho trang TransactionFrm.

15\. Trang TransactionFrm hiển thị danh sách kết quả mới cho Transaction Staff.

16\. Transaction Staff click chọn xem chi tiết một hồ sơ vay cụ thể (click Transaction detail).

17\. Trang TransactionFrm gọi hàm eventPerformed() để xử lý sự kiện chọn bản ghi.

18\. Trang TransactionFrm gọi giao diện chi tiết TransactionDetailFrm.

19\. Giao diện TransactionDetailFrm thực hiện hàm khởi tạo TransactionDetailFrm() để chuẩn bị khung hiển thị.

20\. Giao diện TransactionDetailFrm gọi lớp TransactionliveDAO yêu cầu truy xuất thông tin chi tiết toàn diện.

21\. Lớp TransactionliveDAO thực hiện hàm viewTransactionDetail() để tập hợp dữ liệu hồ sơ và đánh giá rủi ro.

22\. Hàm viewTransactionDetail() gọi lớp thực thể Transactions để lấy thông tin khoản vay.

23\. Lớp Transactions thực hiện hàm Transactions() để đóng gói thông tin thực thể khoản vay.

24\. Lớp thực thể Transactions gọi tiếp lớp thực thể Customer để lấy thông tin định danh chủ hồ sơ.

25\. Lớp Customer thực hiện hàm Customers() để đóng gói thông tin thực thể khách hàng.

26\. Lớp Customer trả kết quả thông tin khách hàng về cho lớp Transactions.

27\. Lớp Transactions trả toàn bộ thông tin hồ sơ đã đóng gói về cho hàm viewTransactionDetail() của TransactionliveDAO.

28\. Lớp TransactionliveDAO trả kết quả tổng hợp về cho giao diện TransactionDetailFrm.

29\. Giao diện TransactionDetailFrm hiển thị chi tiết hồ sơ vay và thông tin khách hàng cho Operator


# 3. Hỗ trợ quyết định cho vay

_Nộp hồ sơ đề nghị vay vốn_

1\. Tại giao diện chính, nhân viên vận hành (Operator) chọn chức năng quản lý khoản vay.

2\. Trang LoanFrm gọi hàm eventPerformed() để xử lý sự kiện vào màn hình.

3\. Trang LoanFrm gọi lớp thực thể Loans yêu cầu lấy thông tin danh sách nền tảng.

4\. Lớp thực thể Loans thực hiện hàm khởi tạo Loans() để tự đóng gói thông tin thực thể.

5\. Lớp thực thể Loans trả kết quả lại cho trang LoanFrm.

6\. Trang LoanFrm hiển thị trạng thái danh sách khoản vay cho Operator.

7\. Operator click chọn chức năng thêm mới hồ sơ đề nghị vay vốn (click add loan).

8\. Trang LoanFrm gọi hàm eventPerformed() để xử lý sự kiện.

9\. Trang LoanFrm gọi trang AddLoanFrm để chuyển sang màn hình nhập liệu hồ sơ.

10\. Trang AddLoanFrm thực hiện hàm khởi tạo AddLoanFrm() để thiết lập form dữ liệu.

11\. Trang AddLoanFrm hiển thị form nhập hồ sơ cho Operator.

12\. Operator thực hiện nhập thông tin định danh của khách hàng (enter customer info).

13\. Trang AddLoanFrm gọi hàm eventPerformed() để xử lý sự kiện nhập liệu.

14\. Trang AddLoanFrm gọi lớp điều khiển CustomerDAO yêu cầu tìm kiếm khách hàng.

15\. Lớp điều khiển CustomerDAO thực hiện hàm searchCustomerLoan() để truy vấn dữ liệu tín dụng.

16\. Hàm searchCustomerLoan() gọi lớp thực thể Customers để lấy thông tin chi tiết.

17\. Lớp thực thể Customers thực hiện hàm Customers() để đóng gói thông tin khách hàng.

18\. Lớp thực thể Customers trả kết quả về cho hàm searchCustomerLoan().

19\. Hàm searchCustomerLoan() trả kết quả về cho trang AddLoanFrm.

20\. Trang AddLoanFrm hiển thị thông tin hồ sơ khách hàng hiện tại để xác nhận.

21\. Operator nhập thông tin khoản vay đề xuất và đính kèm hồ sơ tài chính (enter loan info + sub).

22\. Trang AddLoanFrm gọi hàm eventPerformed() để xử lý lệnh nộp hồ sơ.

23\. Trang AddLoanFrm gọi lớp điều khiển LoanDAO yêu cầu khởi tạo khoản vay mới.

24\. Lớp điều khiển LoanDAO thực hiện hàm addLoan() để lưu bản ghi hồ sơ.

25\. Hàm addLoan() gọi lớp thực thể Loans để ghi nhận dữ liệu.

26\. Lớp thực thể Loans thực hiện hàm setter() để đóng gói thông tin hồ sơ vay.

27\. Lớp thực thể Loans trả kết quả về cho hàm addLoan().

28\. Hàm addLoan() trả kết quả lưu trữ tạm thời về cho trang AddLoanFrm.

29\. Trang AddLoanFrm gọi lớp điều khiển LoanDAO yêu cầu chấm điểm rủi ro cho hồ sơ.

30\. Lớp điều khiển LoanDAO thực hiện hàm scoreLoan() để chạy thuật toán đánh giá tài chính.

31\. Hàm scoreLoan() gọi lớp thực thể Loans để cập nhật điểm số và trạng thái trung gian.

32\. Lớp thực thể Loans thực hiện hàm setter() để lưu kết quả đánh giá vào thực thể.

33\. Lớp thực thể Loans trả kết quả cập nhật về cho hàm scoreLoan().

34\. Sau khi chấm điểm, LoanDAO gọi AuditLogDAO yêu cầu lưu vết toàn bộ thao tác.

35\. Lớp AuditLogDAO thực hiện hàm saveLog() để bắt đầu quy trình ghi nhật ký kiểm toán.

36\. Hàm saveLog() gọi lớp thực thể Users để định danh tác nhân thực hiện.

37\. Lớp thực thể Users thực hiện hàm Users() để đóng gói thông tin nhân viên vận hành.

38\. Hàm saveLog() gọi tiếp lớp thực thể AuditLogs để đóng gói bằng chứng giao dịch.

39\. Lớp thực thể AuditLogs thực hiện hàm setter() để lưu vết hành động, nội dung và thời gian.

40\. Lớp thực thể AuditLogs trả kết quả lưu trữ thành công về cho hàm saveLog().

41\. Lớp AuditLogDAO trả kết quả phản hồi về cho lớp điều khiển LoanDAO.

42\. Lớp điều khiển LoanDAO trả kết quả tổng hợp cuối cùng về cho trang AddLoanFrm.

43\. Trang AddLoanFrm hiển thị thông báo kết quả nộp hồ sơ và điểm rủi ro cho Operator.

_Xem hồ sơ vay_

1\. Tại giao diện chính, nhân viên quản lý khoản vay (Loan Staff) thực hiện truy cập chức năng.

2\. Trang LoanFrm gọi hàm eventPerformed() để xử lý sự kiện nhập màn hình.

3\. Trang LoanFrm gọi lớp thực thể Loans yêu cầu lấy danh sách hồ sơ mặc định.

4\. Lớp Loans thực hiện hàm khởi tạo Loans() để đóng gói thông tin thực thể.

5\. Lớp Loans trả kết quả về cho trang LoanFrm.

6\. Trang LoanFrm hiển thị danh sách hồ sơ cho Loan Staff.

7\. Loan Staff thực hiện nhập thông tin bộ lọc và tiêu chí tìm kiếm (filter loan + sub).

8\. Trang LoanFrm gọi hàm eventPerformed() để xử lý yêu cầu lọc.

9\. Trang LoanFrm gọi lớp điều khiển LoanDAO yêu cầu tìm kiếm theo tiêu chí.

10\. Lớp LoanDAO thực hiện hàm filterLoan() để lọc danh sách hồ sơ từ cơ sở dữ liệu.

11\. Hàm filterLoan() gọi lớp thực thể Loans để truy xuất dữ liệu phù hợp.

12\. Lớp Loans thực hiện hàm Loans() để đóng gói danh sách thực thể đã lọc.

13\. Lớp Loans trả kết quả về cho hàm filterLoan() của lớp LoanDAO.

14\. Lớp LoanDAO trả kết quả danh sách đã lọc về cho trang LoanFrm.

15\. Trang LoanFrm hiển thị danh sách kết quả mới cho Loan Staff.

16\. Loan Staff click chọn xem chi tiết một hồ sơ vay cụ thể (click loan detail).

17\. Trang LoanFrm gọi hàm eventPerformed() để xử lý sự kiện chọn bản ghi.

18\. Trang LoanFrm gọi giao diện chi tiết LoanDetailFrm.

19\. Giao diện LoanDetailFrm thực hiện hàm khởi tạo LoanDetailFrm() để chuẩn bị khung hiển thị.

20\. Giao diện LoanDetailFrm gọi lớp LoanDAO yêu cầu truy xuất thông tin chi tiết toàn diện.

21\. Lớp LoanDAO thực hiện hàm viewLoanDetail() để tập hợp dữ liệu hồ sơ và đánh giá rủi ro.

22\. Hàm viewLoanDetail() gọi lớp thực thể Loans để lấy thông tin khoản vay.

23\. Lớp Loans thực hiện hàm Loans() để đóng gói thông tin thực thể khoản vay.

24\. Lớp thực thể Loans gọi tiếp lớp thực thể Customer để lấy thông tin định danh chủ hồ sơ.

25\. Lớp Customer thực hiện hàm Customers() để đóng gói thông tin thực thể khách hàng.

26\. Lớp Customer trả kết quả thông tin khách hàng về cho lớp Loans.

27\. Lớp Loans trả toàn bộ thông tin hồ sơ đã đóng gói về cho hàm viewLoanDetail() của LoanDAO.

28\. Lớp LoanDAO trả kết quả tổng hợp về cho giao diện LoanDetailFrm.

29\. Giao diện LoanDetailFrm hiển thị chi tiết hồ sơ vay và thông tin khách hàng cho Loan Staff.

_Phê duyệt / Từ chối hồ sơ vay_

1\. Tại giao diện chính, người thẩm định (Reviewer) thực hiện truy cập chức năng.

2\. Trang LoanFrm gọi hàm eventPerformed() để xử lý sự kiện vào màn hình.

3\. Trang LoanFrm gọi lớp thực thể Loans yêu cầu lấy danh sách hồ sơ cần thẩm định.

4\. Lớp Loans thực hiện hàm khởi tạo Loans() để đóng gói thông tin thực thể danh sách.

5\. Lớp Loans trả kết quả về cho trang LoanFrm.

6\. Trang LoanFrm hiển thị danh sách hồ sơ chờ duyệt cho Reviewer.

7\. Reviewer click chọn một hồ sơ vay cụ thể để xem chi tiết (click loan detail).

8\. Trang LoanFrm gọi hàm eventPerformed() để xử lý sự kiện chọn hồ sơ.

9\. Trang LoanFrm gọi trang LoanDetailFrm.

10\. Trang LoanDetailFrm thực hiện hàm khởi tạo LoanDetailFrm() để thiết lập giao diện chi tiết.

11\. Trang LoanDetailFrm gọi lớp điều khiển LoanDAO yêu cầu truy xuất dữ liệu hồ sơ.

12\. Lớp LoanDAO thực hiện hàm viewLoanDetail() để tập hợp thông tin.

13\. Hàm viewLoanDetail() gọi lớp thực thể Loans để lấy thông tin khoản vay.

14\. Lớp Loans thực hiện hàm Loans() để đóng gói thông tin thực thể khoản vay.

15\. Lớp thực thể Loans gọi lớp thực thể Customers để lấy thông tin chủ hồ sơ.

16\. Lớp Customers thực hiện hàm Customers() để đóng gói thông tin thực thể khách hàng.

17\. Lớp Customers trả kết quả về cho lớp thực thể Loans.

18\. Lớp thực thể Loans trả kết quả tổng hợp về cho hàm viewLoanDetail().

19\. Lớp LoanDAO trả kết quả dữ liệu hồ sơ về cho trang LoanDetailFrm.

20\. Trang LoanDetailFrm hiển thị thông tin chi tiết hồ sơ cho Reviewer.

21\. Reviewer thực hiện thao tác tự giao hồ sơ này cho chính mình xử lý (assign case to self).

22\. Trang LoanDetailFrm gọi hàm eventPerformed() để xử lý lệnh phân công.

23\. Trang LoanDetailFrm gọi lớp điều khiển LoanDAO yêu cầu cập nhật người xử lý.

24\. Lớp LoanDAO thực hiện hàm assignLoan() để thực thi nghiệp vụ phân công.

25\. Hàm assignLoan() gọi lớp thực thể Loans để ghi nhận nhân sự phụ trách.

26\. Lớp Loans thực hiện hàm setter() để đóng gói trạng thái phân công vào thực thể.

27\. Lớp Loans trả kết quả cập nhật về cho hàm assignLoan().

28\. \[GHI LOG PHÂN CÔNG]: Lớp LoanDAO gọi lớp điều khiển dùng chung AuditLogDAO yêu cầu lưu vết.

29\. Lớp AuditLogDAO thực hiện hàm saveLog() để bắt đầu quy trình ghi nhật ký.

30\. Hàm saveLog() gọi lớp thực thể Users để xác định danh tính tác nhân thực hiện.

31\. Lớp Users thực hiện hàm Users() để đóng gói thông tin người dùng.

32\. Hàm saveLog() gọi tiếp lớp thực thể AuditLogs để đóng gói dữ liệu nhật ký.

33\. Lớp AuditLogs thực hiện hàm setter() để lưu các thuộc tính nhật ký.

34\. Lớp AuditLogs trả kết quả về cho hàm saveLog().

35\. Lớp AuditLogDAO trả kết quả lưu vết về cho hàm assignLoan().

36\. Lớp LoanDAO trả kết quả thành công về cho trang LoanDetailFrm.

37\. Trang LoanDetailFrm hiển thị trạng thái đã tiếp nhận hồ sơ cho Reviewer.

38\. Reviewer click chọn quyết định phê duyệt hoặc từ chối hồ sơ (click approve / reject loan).

39\. Trang LoanDetailFrm gọi hàm eventPerformed() để xử lý sự kiện ra quyết định.

40\. Trang LoanDetailFrm gọi trang xác nhận ConfirmReviewLoanFrm.

41\. Trang ConfirmReviewLoanFrm thực hiện hàm khởi tạo ConfirmReviewLoanFrm() để hiện pop-up xác nhận.

42\. Trang ConfirmReviewLoanFrm hiển thị cho Reviewer.

43\. Reviewer nhập ghi chú thẩm định và click xác nhận gửi kết quả (enter note + click submit).

44\. Trang ConfirmReviewLoanFrm gọi hàm eventPerformed() để xử lý lệnh nộp kết quả.

45\. Trang ConfirmReviewLoanFrm gọi lớp điều khiển LoanDAO yêu cầu lưu quyết định cuối cùng.

46\. Lớp LoanDAO thực hiện hàm reviewLoan() để thực thi nghiệp vụ phê duyệt/từ chối.

47\. Hàm reviewLoan() gọi lớp thực thể Loans để cập nhật trạng thái thẩm định.

48\. Lớp Loans thực hiện hàm setter() để đóng gói thông tin quyết định vào thực thể.

49\. Lớp Loans trả kết quả lưu trữ về cho hàm reviewLoan().

50\. \[GHI LOG QUYẾT ĐỊNH]: Sau khi cập nhật hồ sơ thành công, LoanDAO gọi AuditLogDAO yêu cầu lưu vết quyết định.

51\. Lớp AuditLogDAO thực hiện hàm saveLog() để ghi nhật ký kiểm toán bước cuối.

52\. Hàm saveLog() gọi lớp thực thể Users để xác định lại tác nhân ra quyết định.

53\. Lớp Users thực hiện hàm Users() để đóng gói thông tin Reviewer.

54\. Hàm saveLog() gọi tiếp lớp thực thể AuditLogs để đóng gói bằng chứng phê duyệt/từ chối.

55\. Lớp AuditLogs thực hiện hàm setter() để lưu vết kết quả và thời điểm thẩm định.

56\. Lớp AuditLogs trả kết quả về cho hàm saveLog().

57\. Lớp AuditLogDAO trả kết quả lưu vết thành công về cho hàm reviewLoan().

58\. Lớp LoanDAO trả kết quả kết thúc quy trình về cho trang ConfirmReviewLoanFrm.

59\. Trang ConfirmReviewLoanFrm gọi lệnh phản hồi về cho trang LoanDetailFrm.

60\. Trang LoanDetailFrm hiển thị kết quả xử lý cuối cùng cho Reviewer.

\
\
\


**4. Xét duyệt thủ công**

1\. Reviewer tương tác chức năng xem danh sách case trên giao diện boundary CaseFrm.

  2. CaseFrm tự gọi hàm eventPerformed() để xử lý sự kiện.

  3. CaseFrm call lớp control ReviewCaseDAO để yêu cầu lấy danh sách case.

  4. ReviewCaseDAO tự gọi hàm filterCase() để kích hoạt tiến trình truy vấn.

  5. ReviewCaseDAO call lớp entity ReviewCase để truy xuất dữ liệu.

  6. ReviewCase tự gọi hàm khởi tạo ReviewCase() để dựng đối tượng case từ cơ sở dữ liệu.

  7. ReviewCase return dữ liệu danh sách case về cho ReviewCaseDAO.

  8. ReviewCaseDAO return kết quả về cho CaseFrm.

  9. CaseFrm return hiển thị danh sách case cho Reviewer.

  10. Reviewer click chọn một case cụ thể trên giao diện CaseFrm.

  11. CaseFrm tự gọi hàm eventPerformed() để xử lý sự kiện.

  12. CaseFrm call giao diện boundary CaseDetailFrm để mở màn hình chi tiết.

  13. CaseDetailFrm tự gọi hàm khởi tạo CaseDetailFrm() để dựng form chi tiết.

  14. CaseDetailFrm call lớp control ReviewCaseDAO để lấy thông tin case.

  15. ReviewCaseDAO tự gọi hàm viewCaseDetail() để xử lý truy vấn.

  16. ReviewCaseDAO call lớp entity ReviewCase để truy xuất dữ liệu.

  17. ReviewCase tự gọi hàm getter() để lấy dữ liệu case.

  18. ReviewCase return dữ liệu case về cho ReviewCaseDAO.

  19. ReviewCaseDAO return kết quả về cho CaseDetailFrm.

  20. CaseDetailFrm call lớp control CustomerDAO để lấy giao dịch chính.

  21. CustomerDAO tự gọi hàm getMainTransaction() để xử lý truy vấn.

  22. CustomerDAO call lớp entity TransactionLive để truy xuất dữ liệu.

  23. TransactionLive tự gọi hàm khởi tạo TransactionLive() để dựng đối tượng giao dịch.

  24. TransactionLive return giao dịch chính về cho CustomerDAO.

  25. CustomerDAO return kết quả về cho CaseDetailFrm.

  26. CaseDetailFrm call lớp control CustomerDAO để lấy danh sách giao dịch liên quan.

  27. CustomerDAO tự gọi hàm getRelatedTransactions() để xử lý truy vấn.

  28. CustomerDAO call lớp entity TransactionLive để truy xuất dữ liệu.

  29. TransactionLive tự gọi hàm khởi tạo TransactionLive() để dựng các đối tượng giao dịch.

  30. TransactionLive return danh sách giao dịch liên quan về cho CustomerDAO.

  31. CustomerDAO return kết quả về cho CaseDetailFrm.

  32. CaseDetailFrm call lớp control CustomerDAO để lấy thông tin khách hàng.

  36. Customer return dữ liệu khách hàng về cho CustomerDAO.

  37. CustomerDAO return kết quả về cho CaseDetailFrm.

  38. CaseDetailFrm return hiển thị chi tiết case cho Reviewer.

  39. Reviewer click nút Assign to me trên giao diện CaseDetailFrm.

  40. CaseDetailFrm tự gọi hàm eventPerformed() để xử lý sự kiện.

  41. CaseDetailFrm call lớp control ReviewCaseDAO để yêu cầu gán case.

  42. ReviewCaseDAO tự gọi hàm assignCase() để xử lý gán case.

  43. ReviewCaseDAO call lớp entity ReviewCase để cập nhật trạng thái.

  44. ReviewCase tự gọi hàm setter() để cập nhật status và assignedReviewer.

  45. ReviewCase return kết quả cập nhật về cho ReviewCaseDAO.

  46. ReviewCaseDAO return kết quả về cho CaseDetailFrm.

  47. CaseDetailFrm return hiển thị giao diện đã cập nhật cho Reviewer.

  48. Reviewer click nút Approve hoặc Reject trên giao diện CaseDetailFrm.

  49. CaseDetailFrm tự gọi hàm eventPerformed() để xử lý sự kiện.

  50. CaseDetailFrm call giao diện boundary ConfirmReviewCaseFrm để mở form xác nhận.

  51. ConfirmReviewCaseFrm tự gọi hàm khởi tạo ConfirmReviewCaseFrm() để dựng form xác nhận.

  52. ConfirmReviewCaseFrm return hiển thị form nhập ghi chú cho Reviewer.

  53. Reviewer nhập ghi chú và click nút Confirm trên giao diện ConfirmReviewCaseFrm.

  54. ConfirmReviewCaseFrm tự gọi hàm eventPerformed() để xử lý sự kiện xác nhận.

  55. ConfirmReviewCaseFrm call lớp control ReviewCaseDAO để lưu quyết định.

  56. ReviewCaseDAO tự gọi hàm reviewCase() để xử lý quyết định.

  57. ReviewCaseDAO call lớp entity ReviewCase để cập nhật quyết định.

  58. ReviewCase tự gọi hàm setter() để cập nhật decision, status, decisionNote, decidedAt, decisionMaker.

  59. ReviewCase return kết quả cập nhật về cho ReviewCaseDAO.

  60. ReviewCaseDAO call lớp control AuditLogDAO để ghi log quyết định.

  61. AuditLogDAO tự gọi hàm saveLog() để xử lý lưu log.

  62. AuditLogDAO call lớp entity Users để lấy thông tin người ra quyết định.

  63. Users tự gọi hàm getter() để truy xuất thông tin user.

  64. Users call lớp entity AuditLog để lưu bản ghi log.

  65. AuditLogs tự gọi hàm setter() để gắn thông tin log (actor, action, time, target).

  66. AuditLogs return kết quả về cho Users.

  67. Users return kết quả về cho AuditLogDAO.

  68. AuditLogDAO return kết quả về cho ReviewCaseDAO.

  69. ReviewCaseDAO return kết quả về cho ConfirmReviewCaseFrm.

  70. ConfirmReviewCaseFrm return hiển thị thông báo thành công cho Reviewer.

**5. Giám sát và báo cáo**


### **I. PHÂN HỆ: XEM VÀ TƯƠNG TÁC DASHBOARD TỔNG QUAN**>

**Khởi tạo và Hiển thị Dashboard Mặc định (Hôm nay)**

1. Tại giao diện **HomeView**, Analyst hoặc Manager chọn chức năng "Xem Dashboard".

2. Lớp **HomeView** gọi hàm eventPerformed().

3. Lớp **HomeView** gọi lớp **DashboardView** để điều hướng.

4. Lớp **DashboardView** tự khởi tạo.

5. Lớp **DashboardView** gửi thông điệp yêu cầu truy xuất dữ liệu tổng quát xuống lớp thực thể **DashboardReport**.

6. Lớp thực thể **DashboardReport** thực thi hành động getDashboardData(timeRange) để truy vấn và tính toán các số liệu rủi ro.

7. Lớp thực thể **DashboardReport** trả kết quả dữ liệu thống kê tổng quát về cho lớp **DashboardView**.

8. Lớp **DashboardView** display (hiển thị) các chỉ số KPIs cùng biểu đồ (outKPITotalTrans, outKPIApprovalRate...) mặc định theo mốc thời gian "Hôm nay" lên màn hình.

**Đổi mốc thời gian** 

9. Tại màn hình **DashboardView**, Analyst hoặc Manager chọn khoảng thời gian mới tại trường inoutTimeFilter. 

10. Tại màn hình **DashboardView**, người dùng kích hoạt hành động subSelectTimeFilter(). 

11. Lớp **DashboardView** display cho người dùng (tải lại dữ liệu). 

12. Lớp **DashboardView** gửi thông điệp yêu cầu truy xuất dữ liệu tổng quát xuống lớp thực thể **DashboardReport** kèm tham số thời gian mới. 

13. Lớp thực thể **DashboardReport** tính toán lại dữ liệu rủi ro và trả tập kết quả mới về cho lớp **DashboardView**. 

14. Lớp **DashboardView** display cập nhật lại toàn bộ số liệu KPIs mới tương ứng lên màn hình.

**Xem chi tiết một KPI** 

15. Tại màn hình **DashboardView**, Analyst hoặc Manager click vào một thẻ chỉ số bất kỳ. 

16. Lớp **DashboardView** gọi hàm eventPerformed(). 

17. Lớp **DashboardView** gọi lớp màn hình phụ **KPIDetailView**. 

18. Lớp màn hình phụ **KPIDetailView** tự khởi tạo (popup). 

19. Lớp màn hình phụ **KPIDetailView** display cho người dùng. 

20. Lớp màn hình phụ **KPIDetailView** gửi thông điệp gọi hành động getKPIDetail(kpiType, timeRange) xuống lớp thực thể **DashboardReport**. 

21. Lớp thực thể **DashboardReport** xử lý tổng hợp số liệu chi tiết theo từng ngày và trả tập dữ liệu về cho lớp **KPIDetailView**. 

22. Lớp màn hình phụ **KPIDetailView** display bảng số liệu chi tiết cùng biểu đồ phụ (outDetailChart, outDailyStats).

**Đóng chi tiết KPI** 

23. Tại màn hình **KPIDetailView**, Analyst hoặc Manager nhấn nút đóng popup subClose(). 

24. Giao diện **KPIDetailView** đóng lại, giải phóng bộ nhớ. 

25. Người dùng quay trở lại màn hình chính **DashboardView**.


## **II. PHÂN HỆ: TRUY VẾT VÀ TRA CỨU AUDIT LOG HỆ THỐNG** 

1. Tại menu hệ thống trên giao diện HomeView, Manager hoặc Admin chọn chức năng "Xem Audit Log".

2. Lớp HomeView gọi hàm nội bộ eventPerformed() để xử lý sự kiện kích hoạt.

3. Lớp HomeView gửi thông điệp điều hướng gọi sang lớp màn hình chính AuditLogView.

4. Lớp AuditLogView tự thực hiện kịch bản khởi tạo giao diện.

5. Lớp AuditLogView thực hiện hành động display cấu trúc trang hiển thị cho người dùng.

6. Lớp AuditLogView gửi thông điệp yêu cầu truy xuất danh sách log mặc định xuống tầng xử lý dữ liệu nâng cao **AuditLogsDAO**.

7. Lớp **AuditLogsDAO** gọi hàm hành động **filterAuditLog()** để bắt đầu quá trình kết nối và truy vấn.

8. Lớp **AuditLogsDAO** gửi thông điệp call xuống lớp thực thể **AuditLog** để quét toàn bộ dữ liệu thuộc tính hệ thống sẵn có (entityType, actorName, createdAt).

9. Lớp thực thể **AuditLog** trả tập dữ liệu kết quả danh sách bản ghi nhật ký về cho lớp **AuditLogsDAO**.

10. Lớp **AuditLogsDAO** gửi tín hiệu phản hồi (return) chuyển giao tập danh sách kết quả ngược lên cho lớp AuditLogView.

11. Lớp AuditLogView tiếp nhận dữ liệu và thực hiện hành động display đổ toàn bộ bảng danh sách log hoàn chỉnh lên thuộc tính đầu ra **outListAuditLog** cho người dùng theo dõi.

12. Tại vùng bộ lọc trên giao diện AuditLogView, Manager hoặc Admin thiết lập các giá trị nâng cao bao gồm: Loại đối tượng inLogType, Loại hành động inActionType, và Ngày thực hiện subLogDate.

13. Tại giao diện AuditLogView, người dùng nhấn nút Tìm kiếm/Lọc subFilter.

14. Lớp AuditLogView gọi hàm nội bộ eventPerformed() và thực hiện lệnh display để tải lại vùng dữ liệu giao diện.

15. Lớp AuditLogView gom toàn bộ các tiêu chí lọc vừa nhập và chuyển thông điệp gọi hành động **filterAuditLog()** với đầy đủ các tham số truyền vào xuống lớp xử lý dữ liệu **AuditLogsDAO**.

16. Lớp **AuditLogsDAO** xử lý tìm kiếm, quét các điều kiện khớp dữ liệu trực tiếp trong cơ sở dữ liệu tại lớp thực thể **AuditLog**.

17. Lớp thực thể **AuditLog** lọc thành công và trả tập danh sách log đã thỏa mãn điều kiện về cho lớp **AuditLogsDAO**.

18. Lớp **AuditLogsDAO** gửi tín hiệu phản hồi (return) đẩy tập kết quả danh sách log sạch về cho giao diện màn hình chính AuditLogView.

19. Lớp AuditLogView ghi nhận, tiến hành cập nhật dữ liệu và hiển thị (display) lại bảng danh sách log mới thông qua trường kết quả đầu ra **inoutListAuditLog**.

20. Tại bảng danh sách hiển thị trên giao diện AuditLogView, Manager hoặc Admin chọn một dòng log cụ thể.

21. Tại giao diện AuditLogView, người dùng nhấn nút xem thông tin chi tiết **subViewDetail**.

22. Lớp AuditLogView gọi hàm nội bộ eventPerformed().

23. Lớp AuditLogView gọi sang lớp màn hình hiển thị chi tiết **AuditLogDetailView** để khởi tạo và mở màn hình điều hướng chi tiết.

24. Lớp AuditLogDetailView tự khởi tạo cấu trúc và thực hiện hành động display giao diện trống lên cho người dùng.

25. Lớp AuditLogDetailView gửi thông điệp yêu cầu truy xuất dữ liệu chi tiết của bản ghi nhật ký được chọn xuống tầng xử lý **AuditLogsDAO**.

26. Lớp **AuditLogsDAO** chuyển thông điệp truy vết trực tiếp vào lớp thực thể **AuditLog** dựa theo mã định danh của bản ghi.

27. Lớp thực thể **AuditLog** thực hiện gọi dữ liệu thuộc tính hoàn chỉnh của bản ghi đó và trả kết quả về cho lớp **AuditLogsDAO**.

28. Lớp **AuditLogsDAO** gửi tín hiệu phản hồi (return) đưa toàn bộ dữ liệu chi tiết lên cho lớp màn hình phụ AuditLogDetailView.

29. Lớp AuditLogDetailView tiếp nhận dữ liệu và thực hiện hành động display hiển thị tường tận tiến trình và nội dung thông tin lên màn hình qua các thuộc tính đầu ra: Thời gian tạo **outDate**, Người thực hiện hành động **outActor**, Loại thực thể bị tác động **outEntityType**, Loại hành động tương tác **outActionType**, và Chi tiết nội dung thay đổi **outDetailAction** cho người dùng xem.

30. Tại giao diện màn hình chi tiết AuditLogDetailView, Manager hoặc Admin nhấn nút chọn hành động quay lại (subBack).

31. Giao diện AuditLogDetailView tự động ẩn đi, giải phóng toàn bộ vùng bộ nhớ lưu trữ chi tiết tạm thời và đưa người dùng quay trở lại trạng thái hoạt động bình thường tại màn hình danh sách nhật ký chính AuditLogView.

\
\
\
\
\
\



# 6. Quản trị Hệ thống

1\. Chức năng Tạo tài khoản (Create User)

1. Admin click nút "Create User" (+subAdd) trên lớp biên UserView.

2. UserView gọi và hiển thị giao diện AddUserView.

3. Admin nhập thông tin người dùng mới (Username, Fullname, Email, Role) và click "Submit" (+subAdd).

4. AddUserView gọi hàm checkDuplicate(username, email) của lớp điều khiển UserDAO để kiểm tra dữ liệu.

5. Nếu trùng lặp, UserDAO trả về lỗi. AddUserView hiển thị thông báo yêu cầu nhập lại. (Ngăn chặn lỗi Omission).

6. Nếu hợp lệ, UserDAO gọi lớp tiện ích EmailService để tạo mật khẩu tạm thời và gửi email cho người dùng mới. Đồng thời set isFirstLogin = true.

7. UserDAO đóng gói dữ liệu vào thực thể User và thực thi lệnh INSERT lưu vào cơ sở dữ liệu.

8. UserDAO (không phải lớp thực thể) gọi hàm saveLog(actorName, actionType, entityType, targetUserID) của AuditLogDAO để lưu vết hành động.

9. UserDAO trả kết quả thành công về cho AddUserView.

10. AddUserView đóng luồng và yêu cầu UserView tải lại danh sách. Hệ thống hiển thị thông báo thành công cho Admin.

2\. Chức năng Thay đổi vai trò người dùng (Change Role)

1. Tại màn hình chi tiết, Admin bấm nút "Change Role" (+subChangeRole) trên UserView.

2. UserView hiển thị hộp thoại ChangeUserRoleView.

3. Admin chọn vai trò mới từ danh sách và click "Confirm" (+subConfirm).

4. ChangeUserRoleView gọi hàm changeUserRole(userID, newRole) của lớp điều khiển UserDAO.

5. UserDAO cập nhật vai trò mới vào CSDL.

6. Sau khi thành công, UserDAO gọi hàm saveLog(...) của AuditLogDAO để ghi lại lịch sử thay đổi.

7. UserDAO trả kết quả thành công. ChangeUserRoleView báo thành công, đóng hộp thoại và yêu cầu UserView cập nhật lại giao diện.

3\. Chức năng Vô hiệu hóa tài khoản (Disable User)

1. Admin chọn tài khoản đang Active và click nút "Disable" (+subDisable) trên lớp UserView.

2. Hệ thống hiển thị hộp thoại cảnh báo ConfirmDisableView.

3. Admin click "Confirm" (+subConfirm).

4. ConfirmDisableView gọi hàm disableUser(userID) của lớp điều khiển UserDAO.

5. UserDAO thực hiện lệnh UPDATE cập nhật trạng thái thành "Disabled" trong CSDL.

6. UserDAO gọi hệ thống tiện ích SessionManager.revokeSessions(userID) để thu hồi ngay lập tức các phiên làm việc hiện hành của tài khoản này (Đáp ứng đúng nghiệp vụ bảo mật ngân hàng).

7. UserDAO gọi hàm saveLog(...) của AuditLogDAO để lưu vết tác vụ.

8. Trả kết quả thành công về UI, hộp thoại đóng và màn hình hiển thị trạng thái "Disabled".

4\. Chức năng Kích hoạt lại tài khoản (Reactivate User)

1. Admin chọn tài khoản đang Disabled và click "Reactivate" (+subReactivate).

2. Hệ thống hiển thị hộp thoại xác nhận ConfirmReactivateView.

3. Admin click "Confirm" (+subConfirm).

4. ConfirmReactivateView gọi hàm reactivateUser(userID) của lớp điều khiển UserDAO.

5. UserDAO cập nhật trạng thái tài khoản thành "Active" trong CSDL.

6. UserDAO gọi hàm saveLog(...) của AuditLogDAO.

7. Giao diện nhận thông báo thành công, đóng hộp thoại và cập nhật lại trạng thái người dùng trên màn hình.

**7. Phân tích rủi ro**


### **1. Xem cấu hình Mô hình (Model Config)**>

1. Tại giao diện menu chính của hệ thống, Analysts chọn chức năng "Quản lý cấu hình mô hình".

2. Hệ thống ghi nhận sự kiện và gọi hàm nội bộ eventPerformed() xử lý kích hoạt.

3. Màn hình menu chính điều hướng và gọi sang lớp giao diện **ModelConfigFRM** để khởi tạo màn hình.

4. Lớp **ModelConfigFRM** gửi thông điệp yêu cầu truy xuất dữ liệu cấu hình hiện tại xuống lớp điều khiển dữ liệu **ModelConfigDAO** thông qua hàm getModelConfig(modelID).

5. Lớp **ModelConfigDAO** thực thi việc kết nối cơ sở dữ liệu và gọi dữ liệu thuộc tính từ lớp thực thể **ModelConfig**.

6. Lớp thực thể **ModelConfig** trả về các giá trị cấu hình hiện hành (mediumConfig, highConfig) cho lớp **ModelConfigDAO**.

7. Lớp **ModelConfigDAO** gửi tín hiệu phản hồi (return) đẩy đối tượng dữ liệu cấu hình ngược lên cho giao diện **ModelConfigFRM**.

8. Lớp **ModelConfigFRM** tiếp nhận dữ liệu và thực hiện hành động display (hiển thị) bảng danh sách ModelList và thông số cấu hình ModelConfig lên màn hình cho Analysts theo dõi.


### **2. Thay đổi cấu hình Mô hình (Có tự động lưu Audit Log)**>

9. Trên màn hình **ModelConfigFRM**, Analysts nhấn chọn nút bấm **btnChangeConfig**.

10. Lớp **ModelConfigFRM** điều hướng và gọi sang lớp giao diện chỉnh sửa **ChangeModelConfigFRM** để khởi tạo cửa sổ popup.

11. Lớp **ChangeModelConfigFRM** thực hiện hành động display hiển thị ô nhập liệu cấu hình cho Analysts.

12. Analysts nhập các giá trị thông số cấu hình mới vào ô nhập liệu inoutModelConfig và kích hoạt nút bấm **btnConfirm**.

13. Lớp **ChangeModelConfigFRM** gọi hàm nội bộ eventPerformed() để bắt đầu tiến trình xử lý lưu thay đổi.

14. Lớp **ChangeModelConfigFRM** gửi thông điệp gọi hàm **changeConfig(config)** xuống lớp điều khiển dữ liệu **ModelConfigDAO**.

15. Lớp **ModelConfigDAO** tác động trực tiếp xuống lớp thực thể **ModelConfig** để cập nhật các giá trị thông số mới vào cơ sở dữ liệu.

16. Ngay sau khi ghi nhận cập nhật thành công, lớp **ModelConfigDAO** gửi thông điệp call sang lớp điều khiển nhật ký **AuditLogDAO** thông qua hàm **saveLogs()** để kích hoạt luồng lưu vết tự động.

17. Lớp **AuditLogDAO** gửi thông điệp call sang lớp thực thể **User** để thu thập thông tin định danh (username, role) của Analyst đang thực hiện thao tác.

18. Lớp **AuditLogDAO** tiếp tục gửi thông điệp call xuống lớp thực thể **AuditLog** để đóng gói toàn bộ bản ghi nhật ký mới bao gồm: loại đối tượng (entityType), người thực hiện (actorName), và thời gian khởi tạo (createdAt).

19. Lớp thực thể **AuditLog** tự thực thi hàm khởi tạo dữ liệu nội bộ để gán các giá trị này vào bộ nhớ.

20. Lớp thực thể **AuditLog** trả kết quả phản hồi (return) bản ghi log hoàn chỉnh về cho lớp **AuditLogDAO** lưu trữ vào cơ sở dữ liệu.

21. Lớp **ModelConfigDAO** nhận tín hiệu hoàn thành luồng ghi log và gửi thông điệp phản hồi thành công (return: boolean) ngược về cho giao diện **ChangeModelConfigFRM**.

22. Lớp **ChangeModelConfigFRM** hiển thị thông báo cập nhật thành công, tự động đóng cửa sổ chỉnh sửa và chuyển tín hiệu làm mới dữ liệu sang lớp màn hình chính **ModelConfigFRM**.

23. Lớp **ModelConfigFRM** tiếp nhận tín hiệu, tự động tải lại dữ liệu mới và thực hiện hành động display để cập nhật hiển thị thông số hoàn chỉnh cho Analysts.


### **3. Xem hiệu suất hoạt động của Mô hình (Model Performance)**>

24. Tại giao diện **ModelConfigFRM**, Analysts bấm chọn một mô hình cụ thể và kích hoạt nút bấm **btnViewPerformance**.

25. Lớp **ModelConfigFRM** ghi nhận sự kiện, điều hướng và gọi sang lớp giao diện hiển thị báo cáo **ModelPerformanceFRM** để khởi tạo màn hình.

26. Lớp **ModelPerformanceFRM** gửi thông điệp yêu cầu cung cấp dữ liệu phân tích xuống lớp điều khiển dữ liệu **FraudStatsDAO** thông qua hàm **reportPerformance()**.

27. Lớp **FraudStatsDAO** kết nối cơ sở dữ liệu và gọi thông điệp truy vấn các thuộc tính thống kê rủi ro trực tiếp từ lớp thực thể **FraudStats**.

28. Lớp thực thể **FraudStats** thực thi tính toán và tổng hợp dữ liệu dựa trên các thông số hệ thống sẵn có (fraudRate, avgFraudScore, manualReviewCount, statID).

29. Lớp thực thể **FraudStats** phản hồi tập kết quả thống kê rủi ro hoàn chỉnh về cho lớp **FraudStatsDAO**.

30. Lớp **FraudStatsDAO** gửi tín hiệu phản hồi dữ liệu (return: FraudStats) ngược lên cho giao diện báo cáo **ModelPerformanceFRM**.

31. Lớp **ModelPerformanceFRM** tiếp nhận toàn bộ tập dữ liệu, tiến hành đổ cấu trúc dữ liệu lên giao diện và thực hiện hành động display hiển thị trực quan các kết quả báo cáo (ModelName, FraudStats, Performance) một lần duy nhất cho Analysts theo dõi.
