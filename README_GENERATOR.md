# Hệ Thống Sinh Dữ Liệu Ngân Hàng

Hệ thống sinh dữ liệu mô phỏng cho ngân hàng theo quy tắc RFM và phân khúc khách hàng, tuân thủ yêu cầu trong file `readme.md`.

## 🏗️ Kiến Trúc Hệ Thống

### Thứ tự sinh dữ liệu:
1. **SAVING TRANSACTION** → 2. **SAVING ACCOUNT** → 3. **CUSTOMER**

### Các module chính:
- `customer_generator.py`: Sinh dữ liệu bảng Customers (55,000 records)
- `savings_account_generator.py`: Sinh dữ liệu bảng Savings accounts
- `transaction_generator.py`: Sinh dữ liệu bảng Savings transactions với phân khúc RFM
- `main_data_generator.py`: Điều phối việc sinh dữ liệu
- `test_generator.py`: Script test hệ thống

## 📊 Phân Khúc Khách Hàng (RFM)

### Premium (50% - X):
- 6-8 giao dịch/tháng
- Gửi tiền ≥ 50 triệu VND
- Có giao dịch trong 30 ngày gần đây
- Nghề nghiệp thu nhập cao
- Có cả tài khoản demand và term saving

### Standard (30% - Y):
- 3-4 giao dịch/tháng  
- Gửi tiền ≥ 30 triệu VND
- Có giao dịch trong 2-6 tháng gần đây
- Nghề nghiệp trung bình
- Chủ yếu tài khoản demand và term ngắn

### Basic (20% - Z):
- 2-3 giao dịch/tháng
- Gửi tiền 5-20 triệu VND
- Có giao dịch > 6 tháng gần đây
- Nghề nghiệp đa dạng
- Chủ yếu tài khoản demand saving

## 🚀 Cách Sử Dụng

### 1. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

### 2. Chạy test (1,000 khách hàng):
```bash
python test_generator.py
```

### 3. Chạy sinh dữ liệu đầy đủ:
```bash
python main_data_generator.py
```

### 4. Chạy từng module riêng lẻ:
```python
from customer_generator import CustomerGenerator
from savings_account_generator import SavingsAccountGenerator
from transaction_generator import TransactionGenerator

# Sinh khách hàng
customer_gen = CustomerGenerator()
customers_df = customer_gen.generate_customers(1000)

# Sinh tài khoản
account_gen = SavingsAccountGenerator()
accounts_df = account_gen.generate_accounts_for_customers(customers_df)

# Sinh giao dịch
txn_gen = TransactionGenerator()
transactions_df = txn_gen.generate_all_transactions(accounts_df)
```

## 📁 Output Files

Sau khi chạy, dữ liệu sẽ được lưu trong thư mục `output/`:

- `customers.csv`: Bảng khách hàng
- `savings_accounts.csv`: Bảng tài khoản tiết kiệm
- `savings_transactions.csv`: Bảng giao dịch tiết kiệm
- `data_report.json`: Báo cáo thống kê chi tiết

## 🔧 Tùy Chỉnh

### Thay đổi số lượng khách hàng:
```python
# Trong main_data_generator.py
datasets = generator.generate_full_dataset(num_customers=10000)
```

### Thay đổi seed để có dữ liệu khác:
```python
generator = DataGenerator(seed=123)
```

### Tùy chỉnh phân khúc:
Chỉnh sửa `segment_rules` trong `transaction_generator.py`:
```python
self.segment_rules = {
    "premium": {
        "txn_per_month": (6, 8),
        "deposit_min": 50000000,
        "recent_days": 30,
        "percentage": 0.50
    },
    # ...
}
```

## 📈 Tính Năng

### ✅ Đã implement:
- Sinh dữ liệu theo đúng thứ tự yêu cầu
- Tuân thủ quy tắc RFM và phân khúc khách hàng
- Validation dữ liệu và kiểm tra tính hợp lệ
- Báo cáo thống kê chi tiết
- Hỗ trợ test mode và full mode
- Lưu dữ liệu ra CSV và JSON

### 🎯 Đặc điểm nổi bật:
- **Realistic data**: Dữ liệu mô phỏng thực tế với các mối quan hệ hợp lệ
- **RFM compliance**: Tuân thủ nghiêm ngặt quy tắc phân khúc RFM
- **Scalable**: Có thể sinh từ 1,000 đến 55,000+ khách hàng
- **Configurable**: Dễ dàng tùy chỉnh các tham số
- **Validated**: Kiểm tra tính hợp lệ của dữ liệu

## 🐛 Troubleshooting

### Lỗi memory khi sinh dữ liệu lớn:
- Chạy test mode trước để kiểm tra
- Tăng RAM hoặc giảm số lượng khách hàng

### Lỗi import:
- Đảm bảo đã cài đặt pandas và numpy
- Kiểm tra Python version >= 3.7

### Dữ liệu không đúng phân khúc:
- Kiểm tra seed có giống nhau không
- Chạy lại với seed khác

## 📞 Hỗ Trợ

Nếu gặp vấn đề, vui lòng kiểm tra:
1. Log lỗi trong console
2. File `data_report.json` để xem thống kê
3. Dữ liệu mẫu trong `output/` folder
