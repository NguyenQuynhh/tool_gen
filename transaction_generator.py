"""
Module sinh dữ liệu bảng Savings transactions
Tuân thủ quy tắc RFM và phân khúc khách hàng theo README
"""

import random
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import numpy as np

class TransactionGenerator:
    def __init__(self, seed: int = 42):
        random.seed(seed)
        np.random.seed(seed)
        
        # Các loại giao dịch
        self.transaction_types = [
            "Interest Withdrawal", "Principal Withdrawal", "Deposit", 
            "Fund Transfer", "Fee Transaction"
        ]
        
        # Kênh giao dịch
        self.channels = ["mobile/internet", "atm", "branch"]
        
        # Trạng thái giao dịch
        self.status_txn = ["Pending", "Posted", "Declined"]
        self.status_weights = [0.10, 0.85, 0.05]  # 10%, 85%, 5%
        
        # Loại tiền tệ
        self.currencies = ["VND", "USD", "EUR"]
        self.currency_weights = [0.85, 0.10, 0.05]  # 85%, 10%, 5%
        
        # Tỷ giá quy đổi
        self.exchange_rates = {"VND": 1, "USD": 25, "EUR": 30}
        
        # Quy tắc phân khúc theo README
        self.segment_rules = {
            "premium": {
                "txn_per_month": (6, 8),
                "deposit_min": 50000000,  # 50 triệu
                "recent_days": 30,
                "percentage": 0.50
            },
            "standard": {
                "txn_per_month": (3, 4), 
                "deposit_min": 30000000,  # 30 triệu
                "recent_days": (60, 180),  # 2-6 tháng
                "percentage": 0.30
            },
            "basic": {
                "txn_per_month": (2, 3),
                "deposit_min": (5000000, 20000000),  # 5-20 triệu
                "recent_days": 180,  # >6 tháng
                "percentage": 0.20
            }
        }
    
    def get_transaction_type_for_account(self, account: Dict, txn_date: datetime) -> str:
        """Xác định loại giao dịch dựa trên loại tài khoản và thời gian"""
        product_type = account['product_type']
        open_date = pd.to_datetime(account['open_date'])
        maturity_date = pd.to_datetime(account['maturity_date']) if pd.notna(account['maturity_date']) else None
        
        if product_type == "demand_saving":
            # Tài khoản không kỳ hạn: chủ yếu Deposit và Fund Transfer
            if random.random() < 0.7:
                return random.choice(["Deposit", "Fund Transfer"])
            else:
                return random.choice(["Interest Withdrawal", "Principal Withdrawal"])
        else:
            # Tài khoản có kỳ hạn
            days_since_open = (txn_date - open_date).days
            days_to_maturity = (maturity_date - txn_date).days if maturity_date else float('inf')
            
            if days_since_open < 30:
                # Gần ngày mở: chủ yếu Deposit
                return "Deposit"
            elif days_to_maturity < 30:
                # Gần đáo hạn: chủ yếu Withdrawal
                return random.choice(["Interest Withdrawal", "Principal Withdrawal"])
            else:
                # Trong kỳ: đa dạng
                return random.choice(self.transaction_types)
    
    def calculate_amount_for_segment(self, segment: str, txn_type: str, 
                                   account: Dict) -> float:
        """Tính số tiền giao dịch dựa trên phân khúc và loại giao dịch"""
        rules = self.segment_rules[segment]
        
        if txn_type == "Deposit":
            if segment == "premium":
                # Cao cấp: 50-200 triệu
                return random.uniform(50000000, 200000000)
            elif segment == "standard":
                # Tiêu chuẩn: 30-100 triệu
                return random.uniform(30000000, 100000000)
            else:
                # Cơ bản: 5-50 triệu
                return random.uniform(5000000, 50000000)
        elif txn_type in ["Interest Withdrawal", "Principal Withdrawal"]:
            # Rút tiền: 10-80% số tiền gửi
            deposit_amount = random.uniform(10000000, 100000000)
            return random.uniform(0.1, 0.8) * deposit_amount
        elif txn_type == "Fund Transfer":
            # Chuyển khoản: 5-50 triệu
            return random.uniform(5000000, 50000000)
        else:  # Fee Transaction
            # Phí: 10,000 - 100,000 VND
            return random.uniform(10000, 100000)
    
    def generate_transaction_dates(self, account: Dict, segment: str) -> List[datetime]:
        """Sinh danh sách ngày giao dịch cho tài khoản"""
        open_date = pd.to_datetime(account['open_date'])
        maturity_date = pd.to_datetime(account['maturity_date']) if pd.notna(account['maturity_date']) else None
        
        # Xác định ngày kết thúc
        if maturity_date:
            end_date = min(maturity_date, datetime.now())
        else:
            end_date = datetime.now()
        
        # Số tháng hoạt động
        months_active = max(1, (end_date - open_date).days // 30)
        
        # Số giao dịch theo phân khúc
        rules = self.segment_rules[segment]
        min_txn_per_month, max_txn_per_month = rules['txn_per_month']
        
        # Tổng số giao dịch
        total_txn = random.randint(
            min_txn_per_month * months_active,
            max_txn_per_month * months_active
        )
        
        # Sinh ngày giao dịch
        txn_dates = []
        for _ in range(total_txn):
            # Ngày ngẫu nhiên trong khoảng hoạt động
            random_days = random.randint(0, (end_date - open_date).days)
            txn_date = open_date + timedelta(days=random_days)
            txn_dates.append(txn_date)
        
        # Sắp xếp theo thời gian
        txn_dates.sort()
        return txn_dates
    
    def calculate_balance(self, current_balance: float, amount: float, 
                         txn_type: str) -> float:
        """Tính số dư sau giao dịch"""
        if txn_type in ["Deposit", "Fund Transfer"]:
            return current_balance + amount
        elif txn_type in ["Interest Withdrawal", "Principal Withdrawal"]:
            return max(0, current_balance - amount)  # Không âm
        else:  # Fee Transaction
            return max(0, current_balance - amount)
    
    def generate_transactions_for_account(self, account: Dict, 
                                        segment: str) -> List[Dict]:
        """Sinh giao dịch cho một tài khoản"""
        transactions = []
        txn_dates = self.generate_transaction_dates(account, segment)
        
        balance = 0  # Số dư ban đầu
        transaction_id = 1
        
        for txn_date in txn_dates:
            # Loại giao dịch
            txn_type = self.get_transaction_type_for_account(account, txn_date)
            
            # Số tiền
            amount = self.calculate_amount_for_segment(segment, txn_type, account)
            
            # Cập nhật số dư
            balance = self.calculate_balance(balance, amount, txn_type)
            
            # Loại tiền tệ
            currency = random.choices(self.currencies, weights=self.currency_weights)[0]
            
            # Số tiền theo nguyên tệ và quy đổi
            tran_amt_acy = amount
            tran_amt_lcy = amount * self.exchange_rates[currency]
            
            # Kênh giao dịch
            channel_txn = random.choice(self.channels)
            
            # Trạng thái giao dịch
            status_txn = random.choices(self.status_txn, weights=self.status_weights)[0]
            
            # Mô tả giao dịch
            txn_desc = self.generate_transaction_description(txn_type, amount, currency)
            
            transaction = {
                "transaction_id": f"TXN{transaction_id:08d}",
                "account_id": account['account_id'],
                "customer_code": account['customer_code'],
                "transaction_date": txn_date.strftime("%Y-%m-%d"),
                "transaction_type": txn_type,
                "transaction_desc": txn_desc,
                "amount": round(amount, 2),
                "balance": round(balance, 2),
                "channel_txn": channel_txn,
                "status_txn": status_txn,
                "TRAN_AMT_ACY": round(tran_amt_acy, 2),
                "TRAN_AMT_LCY": round(tran_amt_lcy, 2),
                "currency": currency
            }
            
            transactions.append(transaction)
            transaction_id += 1
        
        return transactions
    
    def generate_transaction_description(self, txn_type: str, amount: float, 
                                       currency: str) -> str:
        """Sinh mô tả giao dịch"""
        descriptions = {
            "Deposit": [
                f"Gửi tiền tiết kiệm {amount:,.0f} {currency}",
                f"Chuyển khoản vào tài khoản tiết kiệm {amount:,.0f} {currency}",
                f"Nộp tiền mặt tại quầy {amount:,.0f} {currency}"
            ],
            "Interest Withdrawal": [
                f"Rút lãi tiết kiệm {amount:,.0f} {currency}",
                f"Chi trả lãi định kỳ {amount:,.0f} {currency}"
            ],
            "Principal Withdrawal": [
                f"Rút gốc tiết kiệm {amount:,.0f} {currency}",
                f"Tất toán tài khoản tiết kiệm {amount:,.0f} {currency}"
            ],
            "Fund Transfer": [
                f"Chuyển tiền từ tài khoản thanh toán {amount:,.0f} {currency}",
                f"Chuyển khoản nội bộ {amount:,.0f} {currency}"
            ],
            "Fee Transaction": [
                f"Phí dịch vụ {amount:,.0f} {currency}",
                f"Phí sao kê {amount:,.0f} {currency}",
                f"Phí cấp lại sổ tiết kiệm {amount:,.0f} {currency}"
            ]
        }
        
        return random.choice(descriptions[txn_type])
    
    def generate_all_transactions(self, accounts_df: pd.DataFrame) -> pd.DataFrame:
        """Sinh tất cả giao dịch cho tất cả tài khoản"""
        all_transactions = []
        
        for _, account in accounts_df.iterrows():
            segment = account['segment']
            account_transactions = self.generate_transactions_for_account(account, segment)
            all_transactions.extend(account_transactions)
        
        transactions_df = pd.DataFrame(all_transactions)
        
        # Lưu dữ liệu ra file CSV
        import os
        os.makedirs('output', exist_ok=True)
        output_file = 'output/savings_transactions.csv'
        transactions_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"Đã lưu {len(transactions_df)} giao dịch vào file: {output_file}")
        
        return transactions_df
    
    def validate_rfm_segments(self, transactions_df: pd.DataFrame, 
                            accounts_df: pd.DataFrame) -> Dict[str, Any]:
        """Kiểm tra và báo cáo phân khúc RFM"""
        # Nhóm theo customer_code và account_id
        customer_stats = transactions_df.groupby(['customer_code', 'account_id']).agg({
            'transaction_date': ['count', 'max'],
            'amount': ['sum', 'mean'],
            'transaction_type': lambda x: (x == 'Deposit').sum()
        }).reset_index()
        
        customer_stats.columns = ['customer_code', 'account_id', 'txn_count', 'last_txn_date', 
                                'total_amount', 'avg_amount', 'deposit_count']
        
        # Thêm thông tin phân khúc
        customer_stats = customer_stats.merge(
            accounts_df[['account_id', 'segment']], 
            on='account_id'
        )
        
        # Tính toán RFM
        current_date = datetime.now()
        customer_stats['days_since_last_txn'] = (
            current_date - pd.to_datetime(customer_stats['last_txn_date'])
        ).dt.days
        
        # Phân loại theo quy tắc README
        premium_customers = customer_stats[
            (customer_stats['txn_count'] >= 6) & 
            (customer_stats['txn_count'] <= 8) &
            (customer_stats['deposit_count'] > 0) &
            (customer_stats['avg_amount'] >= 50000000) &
            (customer_stats['days_since_last_txn'] <= 30)
        ]
        
        standard_customers = customer_stats[
            (customer_stats['txn_count'] >= 3) & 
            (customer_stats['txn_count'] <= 4) &
            (customer_stats['deposit_count'] > 0) &
            (customer_stats['avg_amount'] >= 30000000) &
            (customer_stats['days_since_last_txn'] >= 60) &
            (customer_stats['days_since_last_txn'] <= 180)
        ]
        
        basic_customers = customer_stats[
            (customer_stats['txn_count'] >= 2) & 
            (customer_stats['txn_count'] <= 3) &
            (customer_stats['deposit_count'] > 0) &
            (customer_stats['avg_amount'] >= 5000000) &
            (customer_stats['avg_amount'] <= 20000000) &
            (customer_stats['days_since_last_txn'] > 180)
        ]
        
        total_customers = len(customer_stats)
        
        return {
            "total_customers": total_customers,
            "premium_count": len(premium_customers),
            "premium_percentage": len(premium_customers) / total_customers * 100,
            "standard_count": len(standard_customers), 
            "standard_percentage": len(standard_customers) / total_customers * 100,
            "basic_count": len(basic_customers),
            "basic_percentage": len(basic_customers) / total_customers * 100
        }

if __name__ == "__main__":
    # Test với dữ liệu mẫu
    from customer_generator import CustomerGenerator
    from savings_account_generator import SavingsAccountGenerator
    
    # Sinh dữ liệu test
    customer_gen = CustomerGenerator()
    customers_df = customer_gen.generate_customers(100)
    
    account_gen = SavingsAccountGenerator()
    accounts_df = account_gen.generate_accounts_for_customers(customers_df)
    
    # Sinh giao dịch
    txn_gen = TransactionGenerator()
    transactions_df = txn_gen.generate_all_transactions(accounts_df)
    
    print(f"Đã sinh {len(transactions_df)} giao dịch cho {len(accounts_df)} tài khoản")
    print("\nPhân bố theo loại giao dịch:")
    print(transactions_df['transaction_type'].value_counts())
    print("\nPhân bố theo kênh:")
    print(transactions_df['channel_txn'].value_counts())
    print("\nMẫu dữ liệu:")
    print(transactions_df.head())
    
    # Kiểm tra RFM
    rfm_stats = txn_gen.validate_rfm_segments(transactions_df, accounts_df)
    print("\nThống kê RFM:")
    print(f"Premium: {rfm_stats['premium_count']} ({rfm_stats['premium_percentage']:.1f}%)")
    print(f"Standard: {rfm_stats['standard_count']} ({rfm_stats['standard_percentage']:.1f}%)")
    print(f"Basic: {rfm_stats['basic_count']} ({rfm_stats['basic_percentage']:.1f}%)")
