"""
Module sinh dữ liệu bảng Savings accounts
Tạo tài khoản tiết kiệm dựa trên phân khúc khách hàng
"""

import random
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import numpy as np

class SavingsAccountGenerator:
    def __init__(self, seed: int = 42):
        random.seed(seed)
        np.random.seed(seed)
        
        # Lãi suất theo kỳ hạn
        self.interest_rates = {
            "demand": (0.01, 0.5),  # Không kỳ hạn: 0.01% - 0.5%
            "1": (3.0, 4.0),        # 1 tháng: 3.0% - 4.0%
            "3": (3.2, 4.2),        # 3 tháng: 3.2% - 4.2%
            "6": (4.5, 5.5),        # 6 tháng: 4.5% - 5.5%
            "9": (4.8, 5.8),        # 9 tháng: 4.8% - 5.8%
            "12": (4.8, 6.0),       # 12 tháng: 4.8% - 6.0%
            "24": (5.0, 6.2),       # 24 tháng: 5.0% - 6.2%
            "36": (6.5, 7.0)        # 36 tháng: 6.5% - 7.0%
        }
        
        # Kênh mở tài khoản
        self.channels = ["mobile/internet", "atm", "branch"]
        
        # Trạng thái tài khoản
        self.statuses = ["active", "closed", "suspend"]
        
    def get_term_months_for_segment(self, segment: str) -> List[int]:
        """Lấy danh sách kỳ hạn phù hợp với phân khúc khách hàng"""
        if segment == "premium":
            # Khách hàng cao cấp: có cả demand và term saving
            return [0, 1, 3, 6, 9, 12, 24, 36]
        elif segment == "standard":
            # Khách hàng tiêu chuẩn: chủ yếu demand và term ngắn
            return [0, 1, 3, 6, 12]
        else:
            # Khách hàng cơ bản: chủ yếu demand saving
            return [0, 1, 3]
    
    def select_product_type_and_term(self, segment: str) -> Tuple[str, int]:
        """Chọn loại sản phẩm và kỳ hạn dựa trên phân khúc"""
        available_terms = self.get_term_months_for_segment(segment)
        
        if segment == "premium":
            # Khách hàng cao cấp: 60% term saving, 40% demand
            if random.random() < 0.6:
                term_months = random.choice([t for t in available_terms if t > 0])
                product_type = "term_saving"
            else:
                term_months = 0
                product_type = "demand_saving"
        elif segment == "standard":
            # Khách hàng tiêu chuẩn: 40% term saving, 60% demand
            if random.random() < 0.4:
                term_months = random.choice([t for t in available_terms if t > 0])
                product_type = "term_saving"
            else:
                term_months = 0
                product_type = "demand_saving"
        else:
            # Khách hàng cơ bản: 20% term saving, 80% demand
            if random.random() < 0.2:
                term_months = random.choice([t for t in available_terms if t > 0])
                product_type = "term_saving"
            else:
                term_months = 0
                product_type = "demand_saving"
        
        return product_type, term_months
    
    def calculate_interest_rate(self, term_months: int) -> float:
        """Tính lãi suất dựa trên kỳ hạn"""
        if term_months == 0:
            # Demand saving
            min_rate, max_rate = self.interest_rates["demand"]
        else:
            # Term saving
            min_rate, max_rate = self.interest_rates[str(term_months)]
        
        return round(random.uniform(min_rate, max_rate), 2)
    
    def generate_open_date(self, term_months: int) -> datetime:
        """Sinh ngày mở tài khoản trong vòng 3 năm"""
        # Ngày bắt đầu: 3 năm trước
        start_date = datetime.now() - timedelta(days=3*365)
        # Ngày kết thúc: hiện tại
        end_date = datetime.now()
        
        # Sinh ngày ngẫu nhiên
        random_days = random.randint(0, (end_date - start_date).days)
        open_date = start_date + timedelta(days=random_days)
        
        return open_date
    
    def calculate_maturity_date(self, open_date: datetime, term_months: int) -> datetime:
        """Tính ngày đáo hạn"""
        if term_months == 0:
            # Demand saving không có đáo hạn
            return None
        else:
            # Thêm số tháng vào ngày mở
            maturity_date = open_date + timedelta(days=term_months * 30)  # Ước tính 30 ngày/tháng
            return maturity_date
    
    def determine_status(self, open_date: datetime, maturity_date: datetime, 
                        has_recent_transactions: bool = False) -> str:
        """Xác định trạng thái tài khoản"""
        current_date = datetime.now()
        
        if maturity_date and current_date > maturity_date:
            # Đã đáo hạn
            return "closed"
        elif not has_recent_transactions:
            # Không có giao dịch gần đây
            days_since_open = (current_date - open_date).days
            if days_since_open > 180:  # > 6 tháng
                return "suspend"
            else:
                return "active"
        else:
            # Có giao dịch gần đây
            return "active"
    
    def select_channel_opened(self, segment: str) -> str:
        """Chọn kênh mở tài khoản dựa trên phân khúc"""
        if segment == "premium":
            # Khách hàng cao cấp: ưu tiên mobile/internet
            weights = [0.6, 0.2, 0.2]
        elif segment == "standard":
            # Khách hàng tiêu chuẩn: cân bằng
            weights = [0.4, 0.3, 0.3]
        else:
            # Khách hàng cơ bản: ưu tiên branch và ATM
            weights = [0.2, 0.4, 0.4]
        
        return random.choices(self.channels, weights=weights)[0]
    
    def generate_accounts_for_customers(self, customers_df: pd.DataFrame, 
                                      accounts_per_customer: Dict[str, int] = None) -> pd.DataFrame:
        """
        Sinh tài khoản tiết kiệm cho khách hàng
        
        Args:
            customers_df: DataFrame chứa thông tin khách hàng
            accounts_per_customer: Dict mapping segment -> số tài khoản trung bình
        """
        if accounts_per_customer is None:
            # Mặc định: premium có nhiều tài khoản hơn
            accounts_per_customer = {
                "premium": 3,    # Trung bình 3 tài khoản
                "standard": 2,   # Trung bình 2 tài khoản  
                "basic": 1       # Trung bình 1 tài khoản
            }
        
        accounts = []
        account_id = 1
        
        for _, customer in customers_df.iterrows():
            customer_code = customer['customer_code']
            segment = customer['segment']
            
            # Số lượng tài khoản cho khách hàng này
            num_accounts = random.randint(1, accounts_per_customer[segment] + 1)
            
            for _ in range(num_accounts):
                # Chọn loại sản phẩm và kỳ hạn
                product_type, term_months = self.select_product_type_and_term(segment)
                
                # Ngày mở tài khoản
                open_date = self.generate_open_date(term_months)
                
                # Ngày đáo hạn
                maturity_date = self.calculate_maturity_date(open_date, term_months)
                
                # Lãi suất
                interest_rate = self.calculate_interest_rate(term_months)
                
                # Kênh mở tài khoản
                channel_opened = self.select_channel_opened(segment)
                
                # Trạng thái (sẽ được cập nhật sau khi có transaction)
                status = "active"  # Mặc định, sẽ cập nhật sau
                
                account = {
                    "account_id": account_id,
                    "customer_code": customer_code,
                    "product_type": product_type,
                    "open_date": open_date.strftime("%Y-%m-%d"),
                    "maturity_date": maturity_date.strftime("%Y-%m-%d") if maturity_date else None,
                    "term_months": term_months,
                    "interest_rate": interest_rate,
                    "status": status,
                    "channel_opened": channel_opened,
                    "segment": segment  # Thêm để theo dõi
                }
                
                accounts.append(account)
                account_id += 1
        
        accounts_df = pd.DataFrame(accounts)
        
        # Lưu dữ liệu ra file CSV
        import os
        os.makedirs('output', exist_ok=True)
        output_file = 'output/savings_accounts.csv'
        accounts_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"Đã lưu {len(accounts_df)} tài khoản vào file: {output_file}")
        
        return accounts_df
    
    def update_account_status(self, accounts_df: pd.DataFrame, 
                            transactions_df: pd.DataFrame) -> pd.DataFrame:
        """Cập nhật trạng thái tài khoản dựa trên giao dịch"""
        # Tạo mapping account_id -> có giao dịch gần đây không
        recent_transactions = {}
        current_date = datetime.now()
        
        for _, txn in transactions_df.iterrows():
            account_id = txn['account_id']
            txn_date = pd.to_datetime(txn['transaction_date'])
            
            # Kiểm tra giao dịch trong 30 ngày gần đây
            if (current_date - txn_date).days <= 30:
                recent_transactions[account_id] = True
        
        # Cập nhật trạng thái
        def update_status(row):
            account_id = row['account_id']
            open_date = pd.to_datetime(row['open_date'])
            maturity_date = pd.to_datetime(row['maturity_date']) if pd.notna(row['maturity_date']) else None
            has_recent_txn = recent_transactions.get(account_id, False)
            
            return self.determine_status(open_date, maturity_date, has_recent_txn)
        
        accounts_df['status'] = accounts_df.apply(update_status, axis=1)
        return accounts_df

if __name__ == "__main__":
    # Test với dữ liệu mẫu
    from customer_generator import CustomerGenerator
    
    # Sinh 100 khách hàng để test
    customer_gen = CustomerGenerator()
    customers_df = customer_gen.generate_customers(100)
    
    # Sinh tài khoản
    account_gen = SavingsAccountGenerator()
    accounts_df = account_gen.generate_accounts_for_customers(customers_df)
    
    print(f"Đã sinh {len(accounts_df)} tài khoản cho {len(customers_df)} khách hàng")
    print("\nPhân bố theo loại sản phẩm:")
    print(accounts_df['product_type'].value_counts())
    print("\nPhân bố theo kỳ hạn:")
    print(accounts_df['term_months'].value_counts())
    print("\nPhân bố theo phân khúc:")
    print(accounts_df['segment'].value_counts())
    print("\nMẫu dữ liệu:")
    print(accounts_df.head())
