Sinh theo thứ tự SAVING TRANSACTION -> SAVING ACCOUNT -> CUSTOMER 
•	SAVING TRANSACTION
Để đảm bảo RFM và CLV thì transaction phải thỏa mãn: 

-	Số lượng transaction của TRAN_AMT_ACY từ 6-8 transaction/ tháng và có giao dịch Deposit giá trị mỗi lần giao dịch trên  50 triệu và TRAN_DATE  các ngày giao dịch thuộc khoảng [active date , ngày hết hạn] và có ít nhất 1 giao dịch trong 30 ngày so với ngày hiện tại thì   chiếm X phần trăm tổng các giao dịch ( X là tham số)

Số lượng transaction của TRAN_AMT_ACY trên 3-4 transaction/ tháng và có giao dịch Deposit giá trị mỗi lần giao dịch trên 30 triệu và TRAN_DATE  các ngày giao dịch thuộc khoảng [active date , ngày hết hạn] và có ít nhất 1 giao dịch trong 2 -6 tháng  so với ngày hiện tại thì   chiếm Y phần trăm tổng các giao dịch ( Y là tham số)

Số lượng transaction của TRAN_AMT_ACY từ 2-3 transaction/tháng  và có giao dịch Deposit  giá trị mỗi lần giao dịch từ 5-20 triệu và TRAN_DATE  các ngày giao dịch thuộc khoảng [active date , ngày hết hạn] và có ít nhất 1 giao dịch  trên 6 tháng so với ngày hiện tại thì chiếm Z phần trăm tổng các giao dịch ( Z là tham số)

Trong đó, X là 50%, Y là 30%, Z là 20%. X, Y, Z biểu thị phân khúc khách hàng

Các account_id và các customer_code sẽ sẽ được định danh vào từng phân khúc nhóm khách hàng 


-	Customer thuộc phân khúc cao sẽ sở hữu nhiều account
-	Transaction_date là các ngày giao dịch thuộc khoảng [ opendate, ngày hết hạn]
-	Transaction type phụ thuộc vào transaction date: 
Gần open_date → thường là Deposit
Gần maturity_date → Withdrawal (Principal/Interest)
Trong kỳ → Là những cái khác 
-	Amount phụ thuộc vào account_id và customer_code
Dựa vào account và customer để định vị phân khúc KH và xác định range amout cho mỗi lần gdich
-	Balance mới = balance cũ +- amount
-	Currency phụ thuộc vào account_id, 1 account_id chỉ có 1 đơn vị tiền tệ duy nhất 
Bảng: Savings transactions
Các cột chính và mô tả:

1. transaction_id
   - Mô tả: ID của giao dịch

2. account_id
   - Mô tả: ID của tài khoản tiết kiệm
   - Lưu ý: Dữ liệu sinh ra sắp xếp ngẫu nhiên, không tăng tuần tự

3. customer_code
   - Mô tả: Mã CIF khách hàng

4. transaction_date
   - Mô tả: Ngày giao dịch
   - Lưu ý: Phân bổ từng ngày trong vòng 1 năm

5. transaction_type
   - Mô tả: Loại giao dịch
   - Giá trị:
       - Interest Withdrawal: rút lãi
       - Principal Withdrawal: rút gốc
       - Deposit: gửi tiền (gồm chuyển tiền từ ngân hàng khác hoặc quầy)
       - Fund Transfer: chuyển tiền từ tài khoản thanh toán sang tài khoản tiết kiệm cùng bank
       - Fee Transaction: thu phí (rất hiếm, ví dụ cấp lại sổ, sao kê chi tiết)
   - Lưu ý ràng buộc:
       - Term_saving account:
           * Principal Withdrawal chỉ được phép khi hết maturity_date (~70% giao dịch), còn lại (~30%) được rút
           * Interest Withdrawal được phép
           * Chỉ được Deposit hoặc Fund Transfer lần đầu tiên duy nhất
       - Fee Transaction hiếm, chỉ phát sinh trong trường hợp đặc biệt

6. transaction_desc
   - Mô tả: Nội dung giao dịch
   - Lưu ý: Phù hợp với transaction_type

7. amount
   - Mô tả: Số tiền giao dịch
   - Giá trị: >5trieu 


8. balance
   - Mô tả: Số dư sau giao dịch
   - Lưu ý: balance = balance cũ + amount giao dịch

9. channel_txn
   - Mô tả: Kênh phát sinh giao dịch
   - Giá trị:
       - mobile/internet
       - atm
       - branch

10. status_txn
    - Mô tả: Trạng thái giao dịch tiết kiệm
    - Giá trị:
        - Pending: ~10%
        - Posted: ~85%
        - Declined: ~5%

11. TRAN_AMT_ACY
    - Mô tả: Số tiền giao dịch theo nguyên tệ

12. TRAN_AMT_LCY
    - Mô tả: Số tiền giao dịch quy đổi
    - Lưu ý: 
        - Nếu currency = VND → giữ nguyên
        - Nếu currency = USD → *25
        - Nếu currency = EUR → *30

13. currency
    - Mô tả: Loại tiền tệ giao dịch
    - Giá trị:
        - VND: ~85%
        - USD/EUR: ~15%



•	SAVING ACCOUNT
Khách hàng thuộc phân khúc nào qua những transction đã được xác định bởi customer_code và account_id. Bâyh sẽ gen dữ liệu saving_account như sau:
-	Account_id: 
-	Customer_code:
-	Open_date: là ngày trước ngày activate_date. Ngày bắt đầu và ngày kết thúc phải khớp với đúng kì hạn của term_month.
-	Maturity_date: là ngày cuối cùng của hoạt động transaction. Ngày bắt đầu và ngày kết thúc phải khớp với đúng kì hạn của term_month.
-	Term_month là sẽ là 1 tháng, 3 tháng. Ngày bắt đầu và ngày kết thúc phải khớp với đúng kì hạn của term_month.
-	Interest_rate: sẽ theo lãi của từng term_month
-	Status: phụ thuộc vào account_id, nếu account nào có hoạt động txn thì để là active
-	Product_type: Những khách hàng loyal thì nên có cả những tài khoản term saving/ demand saving. Còn những khách hàng khác thì có tk demand saving. 


Bảng: Savings accounts

Các cột chính và mô tả:

1. account_id
   - Mô tả: ID tài khoản
   - Lưu ý: Sinh dữ liệu tăng tiến

2. customer_code
   - Mô tả: Mã khách hàng
   - Lưu ý: Dữ liệu phải trùng với dữ liệu của bảng Customers

3. product_type
   - Mô tả: Loại sản phẩm tiết kiệm
   - Giá trị:
       - demand_saving (không kỳ hạn)
       - term_saving (có kỳ hạn)

4. open_date
   - Mô tả: Ngày mở tài khoản tiết kiệm
   - Lưu ý: Trải dài các ngày trong vòng 1 năm sinh dữ liệu

5. maturity_date
   - Mô tả: Ngày đáo hạn
   - Lưu ý: Điền kỳ hạn hoặc null nếu không có

6. term_months
   - Mô tả: Số tháng kỳ hạn
   - Giá trị:
       - 0 (nếu product_type = demand_saving)
       - 1, 3, 6, 9, 12, 24, 36 tháng (nếu term_saving)

7. interest_rate
   - Mô tả: Lãi suất/năm
   - Giá trị:
       - Demand (không kỳ hạn): 0.01% – 0.5%
       - Kỳ ngắn (1–6 tháng): ~3.0% – 4.0%
       - Kỳ trung (6–12 tháng): ~4.5% – 5.5%
       - Kỳ dài (12–24 tháng): ~4.8% – 6.0%
       - Kỳ rất dài (>24 tháng): ~6.5% – 7.0%

8. status
   - Mô tả: Trạng thái tài khoản
   - Giá trị và lưu ý:
       - active: 80–85% (có giao dịch gần đây trong 30 ngày, hoặc rollover)
       - closed: 10–15% (maturity_date đã qua và tất toán)
       - suspend: 2–5% (lâu không có giao dịch >6 tháng)

9. channel_opened
   - Mô tả: Kênh gửi tiền
   - Giá trị:
       - mobile/internet: giao dịch online
       - atm: rút/nộp tiền mặt qua ATM
       - branch: tới trực tiếp quầy ngân hàng

Ràng buộc giữa các trường:
- Nếu product_type = demand_saving → term_months = 0
- status phụ thuộc vào maturity_date, giao dịch gần đây và rollover
- customer_code phải tồn tại trong bảng Customers






•	CUSTOMER
Khách hàng thuộc phân khúc nào qua những transction đã được xác định bởi customer_code và account_id. Bâyh sẽ gen dữ liệu customer như sau:
-	Customer_code: 
-	Full_name:
-	Gender: 
-	DOB:
-	City: phụ thuộc vào chanel_txn, ở các thành phố lớn thì chuyển khoản, qr code sẽ nhiều hơn
-	Martial_status: 
-	Nationality: 98% người VN 
-	Occupation phụ thuộc theo saving account_id. Nhóm loyal thì có nghề nghiệp thuộc top thu nhập cao
-	source_of_income
-	Income_range: phụ thuộc vào account_id và amount của transaction_id hoặc là balance trong account_id. Nếu thuộc nhóm cao cấp sẽ là 50-200tr

Bảng: Customers
Số dòng: 5000

Các cột chính và mô tả:

1. customer_code
   - Mô tả: Mã CIF Khách hàng

2. full_name
   - Mô tả: Họ tên khách hàng

3. gender
   - Mô tả: Giới tính
   - Giá trị: Nam, Nữ

4. DOB
   - Mô tả: Ngày sinh
   - Nhóm tuổi:
       <25 tuổi
       25–40 tuổi
       40–55 tuổi
       >55 tuổi

5. city
   - Mô tả: Thành phố

6. marital_status
   - Mô tả: Tình trạng hôn nhân
   - Giá trị: Độc thân, Kết hôn

7. nationality
   - Mô tả: Quốc tịch
   - Giá trị: Việt Nam, Nước ngoài

8. occupation
   - Mô tả: Nghề nghiệp
   - Giá trị:
       Nhân viên văn phòng
       Kinh doanh cá thể
       Công nhân / lao động phổ thông
       Quản lý / chuyên gia
       Khác (sinh viên, nội trợ…)

9. income_range
   - Mô tả: Thu nhập (VND)
   - Giá trị:
       <10 triệu
       10–20 triệu
       20–50 triệu
       >50 triệu

10. income_currency
    - Mô tả: Loại tiền
    - Giá trị: VND, USD

11. source_of_income
    - Mô tả: Nguồn thu nhập
    - Giá trị: Lương, Kinh doanh, Đầu tư, Khác

12. status
    - Mô tả: Trạng thái khách hàng
    - Giá trị và tỷ lệ:
        Active: ~80%
        Inactive: ~15%
        Closed: ~5%

	



