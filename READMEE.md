#  Banking Data Generator

**Banking Data Generator** là một công cụ sinh dữ liệu ngân hàng giả lập phục vụ cho việc phân tích RFM (Recency, Frequency, Monetary) và các nghiên cứu về hành vi khách hàng ngân hàng. Tool này tạo ra dữ liệu thực tế và có tính nhất quán cao cho 5 phân khúc khách hàng khác nhau.


## Usage Flow

1. **Configure Parameters**: Chọn số lượng khách hàng, khoảng thời gian, phân bố phân khúc
2. **Generate Data**: Chạy tool để sinh dữ liệu theo flow CUSTOMER → ACCOUNT → TRANSACTION → CARD → CARD_TRANSACTION
3. **Preview & Analyze**: Xem trước dữ liệu và phân tích phân bố RFM
4. **Export**: Tải xuống CSV files hoặc sử dụng RFM Visualizer để phân tích chi tiết

## Prerequisites

- Python 3.8+
- pandas, numpy, faker libraries
- 4GB+ RAM cho dataset lớn (>10,000 khách hàng)

## Quick Start

### 1. Setup

```bash
pip install pandas numpy faker
```

### 2. Generate Data

```bash
# Generate 1000 customers with default settings
python main_generator.py
```

### 3. Customize

Edit `main_generator.py` line 313:

```python
# Change customer count
dataset = generator.generate_balanced_dataset(1000)  # 5000 customers
```

### 4. Analyze

```bash
# Run RFM analysis
python rfm_terminal_visualizer.py
```

## Getting Started

### 1. Clone và Setup

```bash
git clone <your-repo-url>
cd banking-data-generator
pip install -r requirements.txt
```

### 2. Chạy tool cơ bản

```bash
# Chạy với cấu hình mặc định (1000 khách hàng)
python main_generator.py
```

### 3. Tùy chỉnh số lượng khách hàng

Mở file `main_generator.py` và sửa dòng 313:

```python
# Thay đổi số lượng khách hàng
dataset = generator.generate_balanced_dataset(5000)  # 5000 khách hàng
```

## Architecture

### Data Generation Flow:
```
CUSTOMER → ACCOUNT → TRANSACTION → CARD → CARD_TRANSACTION
```

### RFM Customer Segments:
- **A (Champions/VIPs)**: 10% - Khách hàng VIP, tiêu nhiều tiền
- **B (Potential Loyalists)**: 15% - Khách hàng tiềm năng
- **C (At-Risk High Value)**: 5% - Khách hàng có nguy cơ rời bỏ
- **D (Stable Savers)**: 20% - Khách hàng tiết kiệm ổn định
- **E (New/Occasional Users)**: 30% - Khách hàng mới/thỉnh thoảng

## Project Structure

```
banking-data-generator/
├── main_generator.py              # Main entry point
├── customer_generator.py          # Customer data generation
├── account_generator.py           # Account data generation  
├── transaction_generator.py       # Transaction data generation
├── card_generator.py              # Card data generation
├── card_transaction_generator.py  # Card transaction generation
├── test_config.py                 # System configuration
├── rfm_terminal_visualizer.py     # RFM analysis tool
└── output/                        # Generated data output
    ├── banking_data_customers.csv
    ├── banking_data_accounts.csv
    ├── banking_data_transactions.csv
    ├── banking_data_card_transactions.csv
    └── banking_data_cards_from_txn.csv
```

## Advanced Usage

### Chạy từng module riêng lẻ

#### Sinh dữ liệu khách hàng:
```python
from customer_generator import NewCustomerGenerator
from test_config import test_config

config = test_config()
generator = NewCustomerGenerator(config)
customers = generator.generate_customers_by_count(1000)
```

#### Sinh dữ liệu giao dịch thẻ:
```python
from card_transaction_generator import CardTransactionGenerator
import pandas as pd

# Đọc dữ liệu khách hàng từ CSV
df_customers = pd.read_csv("output/banking_data_customers.csv")
customers = df_customers[['customer_code', 'customer_segment']].to_dict('records')

generator = CardTransactionGenerator()
cards = generator.generate_cards_for_customers(customers, start_date, end_date)
transactions = generator.generate_transactions_for_cards(cards, start_date, end_date)
```


## Configuration

### File `test_config.py`

Các tham số chính có thể tùy chỉnh:

```python
# Dataset sizes
SMALL_DATASET: int = 100
MEDIUM_DATASET: int = 1000
LARGE_DATASET: int = 10000

# RFM Segment distribution
SEGMENT_DISTRIBUTION: Dict[str, float] = {
    'A': 0.10,  # Champions/VIPs
    'B': 0.15,  # Potential Loyalists  
    'C': 0.05,  # At-Risk High Value
    'D': 0.20,  # Stable Savers
    'E': 0.30   # New/Occasional Users
}

# Date range
START_DATE: datetime = datetime(2023, 1, 1)
END_DATE: datetime = datetime(2024, 12, 31)

# Account settings
MIN_ACCOUNTS_PER_CUSTOMER: int = 1
MAX_ACCOUNTS_PER_CUSTOMER: int = 5
```

## Data Output

### Generated CSV Files

#### 1. `banking_data_customers.csv`
Customer information with columns:
- `customer_code`: Customer ID
- `full_name`: Full name
- `gender`: Gender
- `dob`: Date of birth
- `city`: City
- `marital_status`: Marital status
- `nationality`: Nationality
- `occupation`: Occupation
- `income_range`: Income range
- `customer_segment`: RFM segment (A, B, C, D, E)

#### 2. `banking_data_accounts.csv`
Savings account information:
- `account_id`: Account ID
- `customer_code`: Customer ID
- `product_type`: Product type (demand_saving, term_saving)
- `open_date`: Account opening date
- `maturity_date`: Maturity date
- `term_months`: Term in months
- `interest_rate`: Interest rate (%)
- `status`: Account status
- `balance`: Current balance

#### 3. `banking_data_transactions.csv`
Savings transactions:
- `transaction_id`: Transaction ID
- `account_id`: Account ID
- `customer_code`: Customer ID
- `transaction_date`: Transaction date
- `transaction_type`: Transaction type
- `amount`: Transaction amount
- `balance`: Balance after transaction
- `channel_txn`: Transaction channel
- `status_txn`: Transaction status

#### 4. `banking_data_card_transactions.csv`
Card transactions:
- `tran_id`: Transaction ID
- `card_id`: Card ID
- `customer_code`: Customer ID
- `tran_amt_acy`: Transaction amount (original currency)
- `tran_currency`: Currency
- `tran_date`: Transaction date
- `tran_type`: Transaction type
- `merchant_name`: Merchant name
- `tran_status`: Transaction status

## Data Analysis


### Python Analysis

```python
import pandas as pd

# Load data
customers = pd.read_csv("output/banking_data_customers.csv")
transactions = pd.read_csv("output/banking_data_transactions.csv")

# Segment analysis
segment_analysis = customers.groupby('customer_segment').agg({
    'customer_code': 'count',
    'income_range': lambda x: x.value_counts().to_dict()
})

print(segment_analysis)
```

## Key Features

### 1. Smart RFM Segmentation
- Automatic customer classification into 5 groups A, B, C, D, E
- Transaction behavior aligned with each segment
- Consistent and realistic data patterns

### 2. Logical Data Generation
- VIP customers have multiple term_saving accounts
- New customers primarily use demand_saving
- Longer terms have higher interest rates
- Major cities have more online transactions

### 3. Multi-Currency Support
- VND (85%), USD (10%), EUR (5%)
- Automatic exchange rate conversion
- Realistic multi-currency transactions

### 4. Credit Card Data
- 2-4 cards per customer
- Credit limits based on customer segment
- Diverse card transactions (online, ATM, POS)
- Popular Vietnamese merchants

## Advanced Customization

### Change Segment Distribution

Edit `customer_generator.py`:

```python
# Modify segment distribution
SEGMENT_DISTRIBUTION = {
    'A': 0.15,  # Increase VIP to 15%
    'B': 0.20,  # Increase Potential to 20%
    'C': 0.05,  # Keep At-Risk same
    'D': 0.25,  # Increase Stable to 25%
    'E': 0.35   # Decrease New to 35%
}
```

### Change Date Range

Edit `test_config.py`:

```python
# Modify data time range
START_DATE: datetime = datetime(2022, 1, 1)
END_DATE: datetime = datetime(2023, 12, 31)
```

### Add New Transaction Types

Edit `transaction_generator.py`:

```python
# Add new transaction types
TRANSACTION_TYPES = [
    'DEPOSIT', 'WITHDRAWAL', 'INTEREST', 
    'FEE', 'TRANSFER', 'NEW_TYPE'  # Add new type
]
```

## Performance & Limits

### Data Generation Time:
- 1,000 customers: ~2 minutes
- 5,000 customers: ~8 minutes
- 10,000 customers: ~15 minutes

### File Sizes:
- 1,000 customers: ~50MB
- 5,000 customers: ~250MB
- 10,000 customers: ~500MB

### System Requirements:
- Maximum 50,000 customers for optimal performance
- Minimum 4GB RAM for large datasets
- Generation time scales linearly with customer count

## Cost & Data Generation Summary

| Action | Time Required | Memory Usage | Output Files | Data Quality |
|--------|---------------|--------------|--------------|--------------|
| Generate 1K customers | ~2 minutes | ~1GB | 6 CSV files | High realism |
| Generate 5K customers | ~8 minutes | ~2GB | 6 CSV files | High realism |
| Generate 10K customers | ~15 minutes | ~4GB | 6 CSV files | High realism |
| RFM Analysis | ~30 seconds | ~500MB | Terminal output | Comprehensive |

**Note**: All data generation is completely free and runs locally. No external API calls or cloud services required.

## Troubleshooting

### Vietnamese Encoding Issues
```python
# Add encoding when reading CSV
df = pd.read_csv("file.csv", encoding='utf-8-sig')
```

### Missing Output Directory
```python
# Create output directory before running
import os
os.makedirs("output", exist_ok=True)
```

### Memory Issues with Large Datasets
```python
# Reduce customer count or increase RAM
# Or run in smaller batches
```

## Stack

- **Python 3.8+** (Core language)
- **pandas** (Data manipulation and analysis)
- **numpy** (Numerical computing)
- **faker** (Realistic data generation)
- **datetime** (Date/time handling)
- **random** (Random data generation)

## Extending/Contributing

### Adding New Customer Segments

To add new RFM segments, edit `customer_generator.py`:

```python
# Add new segment to SEGMENT_DISTRIBUTION
SEGMENT_DISTRIBUTION = {
    'A': 0.10,  # Champions/VIPs
    'B': 0.15,  # Potential Loyalists
    'C': 0.05,  # At-Risk High Value
    'D': 0.20,  # Stable Savers
    'E': 0.30,  # New/Occasional Users
    'F': 0.20   # New segment
}
```

### Adding New Transaction Types

Edit `transaction_generator.py`:

```python
# Add new transaction types
TRANSACTION_TYPES = [
    'DEPOSIT', 'WITHDRAWAL', 'INTEREST', 
    'FEE', 'TRANSFER', 'INVESTMENT'  # New type
]
```

### Adding New Cities

Edit `test_config.py`:

```python
# Add new cities to CITIES list
CITIES = [
    'Hà Nội', 'TP.HCM', 'Đà Nẵng',
    'New City'  # Add new city
]
```


