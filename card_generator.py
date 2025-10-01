"""
Card Generator - Sinh dữ liệu card dựa trên card_id từ card transaction
và phân khúc khách hàng (A, B, C, D)
"""

import random
import pandas as pd
import os
from datetime import datetime, timedelta
from typing import List, Dict, Set
from dataclasses import dataclass

from test_config import test_config

@dataclass
class Card:
    """Card data structure"""
    card_id: str
    customer_code: str
    card_number: str
    card_type: str
    product_type: str
    issue_date: datetime
    expire_date: datetime
    activation_date: datetime
    credit_limit: float
    available_credit: float
    outstanding_balance: float
    minimum_payment: float
    due_date: datetime
    interest_rate: float
    card_status: str

class CardGenerator:
    """Card Generator với phân khúc khách hàng"""
    
    def __init__(self, config: dict):
        self.config = config
        self.cards_data = []
        
        # Định nghĩa đặc điểm card theo phân khúc khách hàng
        self.segment_configs = {
            'A': {  # Khách hàng VIP - phân khúc cao
                'card_type_weights': {'CREDIT': 0.8, 'DEBIT': 0.2},
                'product_type_weights': {'QUOC_TE': 0.7, 'NOI_DIA': 0.3},
                'credit_limit_ranges': [(150_000_000, 200_000_000), (100_000_000, 150_000_000)],
                'credit_limit_weights': [0.6, 0.4],
                'interest_rate_range': (18, 25),
                'activation_probabilities': [0.8, 0.15, 0.05],  # 7 ngày, 7-30 ngày, không kích hoạt
                'status_weights': {'ACTIVE': 0.8, 'INACTIVE': 0.05, 'BLOCKED': 0.05, 'LOST': 0.02, 'EXPIRED': 0.03, 'CLOSED': 0.05}
            },
            'B': {  # Khách hàng trung bình cao
                'card_type_weights': {'CREDIT': 0.6, 'DEBIT': 0.4},
                'product_type_weights': {'QUOC_TE': 0.5, 'NOI_DIA': 0.5},
                'credit_limit_ranges': [(70_000_000, 100_000_000), (50_000_000, 70_000_000)],
                'credit_limit_weights': [0.7, 0.3],
                'interest_rate_range': (20, 28),
                'activation_probabilities': [0.7, 0.2, 0.1],
                'status_weights': {'ACTIVE': 0.75, 'INACTIVE': 0.1, 'BLOCKED': 0.05, 'LOST': 0.02, 'EXPIRED': 0.03, 'CLOSED': 0.05}
            },
            'C': {  # Khách hàng trung bình
                'card_type_weights': {'CREDIT': 0.4, 'DEBIT': 0.6},
                'product_type_weights': {'QUOC_TE': 0.3, 'NOI_DIA': 0.7},
                'credit_limit_ranges': [(50_000_000, 70_000_000)],
                'credit_limit_weights': [1.0],
                'interest_rate_range': (22, 30),
                'activation_probabilities': [0.6, 0.25, 0.15],
                'status_weights': {'ACTIVE': 0.7, 'INACTIVE': 0.15, 'BLOCKED': 0.05, 'LOST': 0.02, 'EXPIRED': 0.03, 'CLOSED': 0.05}
            },
            'D': {  # Khách hàng thấp
                'card_type_weights': {'CREDIT': 0.2, 'DEBIT': 0.8},
                'product_type_weights': {'QUOC_TE': 0.1, 'NOI_DIA': 0.9},
                'credit_limit_ranges': [(50_000_000, 70_000_000)],
                'credit_limit_weights': [1.0],
                'interest_rate_range': (25, 30),
                'activation_probabilities': [0.5, 0.3, 0.2],
                'status_weights': {'ACTIVE': 0.6, 'INACTIVE': 0.2, 'BLOCKED': 0.05, 'LOST': 0.02, 'EXPIRED': 0.03, 'CLOSED': 0.1}
            },
            'E': {  # Khách hàng thấp nhất
                'card_type_weights': {'CREDIT': 0.1, 'DEBIT': 0.9},
                'product_type_weights': {'QUOC_TE': 0.05, 'NOI_DIA': 0.95},
                'credit_limit_ranges': [(50_000_000, 70_000_000)],
                'credit_limit_weights': [1.0],
                'interest_rate_range': (28, 30),
                'activation_probabilities': [0.4, 0.3, 0.3],
                'status_weights': {'ACTIVE': 0.5, 'INACTIVE': 0.3, 'BLOCKED': 0.05, 'LOST': 0.02, 'EXPIRED': 0.03, 'CLOSED': 0.1}
            }
        }
    
    def load_card_transactions(self) -> pd.DataFrame:
        """Load dữ liệu card transactions để lấy card_id"""
        file_path = os.path.join('output', 'banking_data_card_transactions.csv')
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Không tìm thấy file {file_path}")
        
        df = pd.read_csv(file_path)
        print(f"Da load {len(df)} card transactions")
        return df
    
    def load_customers(self) -> pd.DataFrame:
        """Load dữ liệu customers để lấy phân khúc"""
        file_path = os.path.join('output', 'banking_data_customers.csv')
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Không tìm thấy file {file_path}")
        
        df = pd.read_csv(file_path)
        print(f"Da load {len(df)} customers")
        return df
    
    def get_unique_cards_from_transactions(self, card_txn_df: pd.DataFrame) -> pd.DataFrame:
        """Lấy danh sách card_id duy nhất từ card transactions"""
        unique_cards = card_txn_df[['card_id', 'customer_code', 'card_number', 'card_type']].drop_duplicates()
        print(f"Tim thay {len(unique_cards)} card_id duy nhat")
        return unique_cards
    
    def generate_card_number(self, customer_code: str, card_type: str) -> str:
        """Sinh số thẻ theo format chuẩn"""
        # Lấy 4 số cuối từ customer_code
        customer_suffix = customer_code.split('_')[-1].zfill(4)
        
        # Sinh 4 số ngẫu nhiên cho mỗi nhóm 4 số
        group1 = random.randint(1000, 9999)
        group2 = random.randint(1000, 9999)
        group3 = random.randint(1000, 9999)
        group4 = int(customer_suffix)
        
        return f"{group1}-{group2}-{group3}-{group4}"
    
    def determine_card_type(self, segment: str) -> str:
        """Xác định loại thẻ dựa trên phân khúc"""
        config = self.segment_configs[segment]
        return random.choices(
            list(config['card_type_weights'].keys()),
            weights=list(config['card_type_weights'].values())
        )[0]
    
    def determine_product_type(self, segment: str) -> str:
        """Xác định loại sản phẩm thẻ dựa trên phân khúc"""
        config = self.segment_configs[segment]
        return random.choices(
            list(config['product_type_weights'].keys()),
            weights=list(config['product_type_weights'].values())
        )[0]
    
    def calculate_credit_limit(self, segment: str, card_type: str) -> float:
        """Tính hạn mức credit dựa trên phân khúc và loại thẻ"""
        if card_type == 'DEBIT':
            return 0.0
        
        config = self.segment_configs[segment]
        range_idx = random.choices(
            range(len(config['credit_limit_ranges'])),
            weights=config['credit_limit_weights']
        )[0]
        
        min_limit, max_limit = config['credit_limit_ranges'][range_idx]
        return random.uniform(min_limit, max_limit)
    
    def calculate_outstanding_balance(self, credit_limit: float) -> float:
        """Tính dư nợ hiện tại"""
        if credit_limit == 0:
            return 0.0
        
        # Dư nợ từ 10% đến 80% hạn mức
        utilization_rate = random.uniform(0.1, 0.8)
        return credit_limit * utilization_rate
    
    def calculate_available_credit(self, credit_limit: float, outstanding_balance: float) -> float:
        """Tính hạn mức khả dụng"""
        return max(0, credit_limit - outstanding_balance)
    
    def calculate_minimum_payment(self, outstanding_balance: float) -> float:
        """Tính số tiền tối thiểu phải trả"""
        if outstanding_balance == 0:
            return 0.0
        return max(0.05 * outstanding_balance, 100_000)  # Tối thiểu 100k
    
    def generate_issue_date(self) -> datetime:
        """Sinh ngày phát hành thẻ"""
        start_date = datetime(2020, 1, 1)
        end_date = datetime(2024, 12, 31)
        return start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
    
    def generate_expire_date(self, issue_date: datetime) -> datetime:
        """Sinh ngày hết hạn thẻ (3-5 năm sau ngày phát hành)"""
        years = random.randint(3, 5)
        return issue_date + timedelta(days=years * 365)
    
    def generate_activation_date(self, issue_date: datetime, segment: str) -> datetime:
        """Sinh ngày kích hoạt thẻ dựa trên phân khúc"""
        config = self.segment_configs[segment]
        activation_type = random.choices(
            [0, 1, 2],  # 0: 7 ngày, 1: 7-30 ngày, 2: không kích hoạt
            weights=config['activation_probabilities']
        )[0]
        
        if activation_type == 0:  # Kích hoạt trong 7 ngày
            days = random.randint(1, 7)
        elif activation_type == 1:  # Kích hoạt sau 7-30 ngày
            days = random.randint(8, 30)
        else:  # Không kích hoạt
            return None
        
        return issue_date + timedelta(days=days)
    
    def generate_due_date(self, issue_date: datetime) -> datetime:
        """Sinh ngày đến hạn thanh toán (ngày 20 hàng tháng)"""
        # Lấy ngày 20 của tháng tiếp theo
        next_month = issue_date.replace(day=1) + timedelta(days=32)
        next_month = next_month.replace(day=1)
        return next_month.replace(day=20)
    
    def generate_interest_rate(self, segment: str) -> float:
        """Sinh lãi suất dựa trên phân khúc"""
        config = self.segment_configs[segment]
        min_rate, max_rate = config['interest_rate_range']
        return round(random.uniform(min_rate, max_rate), 2)
    
    def determine_card_status(self, segment: str, has_transactions: bool) -> str:
        """Xác định trạng thái thẻ dựa trên phân khúc và hoạt động"""
        config = self.segment_configs[segment]
        
        # Nếu có giao dịch thì ưu tiên ACTIVE
        if has_transactions:
            weights = config['status_weights'].copy()
            weights['ACTIVE'] = min(0.9, weights['ACTIVE'] + 0.2)  # Tăng xác suất ACTIVE
            # Giảm xác suất các trạng thái khác
            for status in weights:
                if status != 'ACTIVE':
                    weights[status] *= 0.5
        else:
            weights = config['status_weights']
        
        return random.choices(
            list(weights.keys()),
            weights=list(weights.values())
        )[0]
    
    def generate_card(self, card_id: str, customer_code: str, card_number: str, 
                     card_type: str, segment: str, has_transactions: bool) -> Card:
        """Sinh dữ liệu cho một card"""
        
        # Sinh các thuộc tính cơ bản
        issue_date = self.generate_issue_date()
        expire_date = self.generate_expire_date(issue_date)
        activation_date = self.generate_activation_date(issue_date, segment)
        
        # Xác định loại thẻ và sản phẩm dựa trên phân khúc
        final_card_type = self.determine_card_type(segment)
        product_type = self.determine_product_type(segment)
        
        # Tính hạn mức và dư nợ
        credit_limit = self.calculate_credit_limit(segment, final_card_type)
        outstanding_balance = self.calculate_outstanding_balance(credit_limit)
        available_credit = self.calculate_available_credit(credit_limit, outstanding_balance)
        minimum_payment = self.calculate_minimum_payment(outstanding_balance)
        
        # Sinh các thuộc tính khác
        due_date = self.generate_due_date(issue_date)
        interest_rate = self.generate_interest_rate(segment)
        card_status = self.determine_card_status(segment, has_transactions)
        
        return Card(
            card_id=card_id,
            customer_code=customer_code,
            card_number=card_number,
            card_type=final_card_type,
            product_type=product_type,
            issue_date=issue_date,
            expire_date=expire_date,
            activation_date=activation_date,
            credit_limit=credit_limit,
            available_credit=available_credit,
            outstanding_balance=outstanding_balance,
            minimum_payment=minimum_payment,
            due_date=due_date,
            interest_rate=interest_rate,
            card_status=card_status
        )
    
    def generate_cards(self) -> List[Card]:
        """Sinh dữ liệu cho tất cả cards"""
        print("Bat dau sinh du lieu cards...")
        
        # Load du lieu
        card_txn_df = self.load_card_transactions()
        customers_df = self.load_customers()
        
        # Tao mapping customer_code -> segment
        customer_segment_map = dict(zip(customers_df['customer_code'], customers_df['customer_segment']))
        
        # Lay danh sach card_id duy nhat
        unique_cards_df = self.get_unique_cards_from_transactions(card_txn_df)
        
        # Tao mapping card_id -> co giao dich hay khong
        cards_with_transactions = set(card_txn_df['card_id'].unique())
        
        cards = []
        for _, row in unique_cards_df.iterrows():
            card_id = row['card_id']
            customer_code = row['customer_code']
            card_number = row['card_number']
            card_type = row['card_type']
            
            # Lay phan khuc khach hang
            segment = customer_segment_map.get(customer_code, 'D')  # Mac dinh la D neu khong tim thay
            
            # Kiem tra co giao dich hay khong
            has_transactions = card_id in cards_with_transactions
            
            # Sinh du lieu card
            card = self.generate_card(card_id, customer_code, card_number, card_type, segment, has_transactions)
            cards.append(card)
        
        print(f"Da sinh {len(cards)} cards")
        return cards
    
    def save_cards_to_csv(self, cards: List[Card]):
        """Lưu dữ liệu cards vào file CSV"""
        output_dir = 'output'
        os.makedirs(output_dir, exist_ok=True)
        
        file_path = os.path.join(output_dir, 'banking_data_cards.csv')
        
        # Chuẩn bị dữ liệu
        cards_data = []
        for card in cards:
            cards_data.append({
                'card_id': card.card_id,
                'customer_code': card.customer_code,
                'card_number': card.card_number,
                'card_type': card.card_type,
                'product_type': card.product_type,
                'issue_date': card.issue_date.strftime('%Y-%m-%d'),
                'expire_date': card.expire_date.strftime('%Y-%m-%d'),
                'activation_date': card.activation_date.strftime('%Y-%m-%d') if card.activation_date else None,
                'credit_limit': card.credit_limit,
                'available_credit': card.available_credit,
                'outstanding_balance': card.outstanding_balance,
                'minimum_payment': card.minimum_payment,
                'due_date': card.due_date.strftime('%Y-%m-%d'),
                'interest_rate': card.interest_rate,
                'card_status': card.card_status
            })
        
        # Lưu vào CSV
        df = pd.DataFrame(cards_data)
        df.to_csv(file_path, index=False, encoding='utf-8')
        print(f"Da luu {len(cards_data)} cards vao {file_path}")
        
        # Thong ke theo phan khuc
        self.print_segment_statistics(df)
    
    def print_segment_statistics(self, df: pd.DataFrame):
        """In thống kê theo phân khúc"""
        print("\n=== THONG KE CARDS THEO PHAN KHUC ===")
        
        # Load customer data de mapping
        customers_df = pd.read_csv(os.path.join('output', 'banking_data_customers.csv'))
        customer_segment_map = dict(zip(customers_df['customer_code'], customers_df['customer_segment']))
        
        # Them cot segment vao df
        df['segment'] = df['customer_code'].map(customer_segment_map)
        
        for segment in ['A', 'B', 'C', 'D', 'E']:
            segment_df = df[df['segment'] == segment]
            if len(segment_df) > 0:
                print(f"\n--- Phan khuc {segment} ({len(segment_df)} cards) ---")
                print(f"Card type: {segment_df['card_type'].value_counts().to_dict()}")
                print(f"Product type: {segment_df['product_type'].value_counts().to_dict()}")
                print(f"Status: {segment_df['card_status'].value_counts().to_dict()}")
                if segment_df['credit_limit'].sum() > 0:
                    print(f"Credit limit trung binh: {segment_df['credit_limit'].mean():,.0f} VND")
                    print(f"Outstanding balance trung binh: {segment_df['outstanding_balance'].mean():,.0f} VND")
                print(f"Interest rate trung binh: {segment_df['interest_rate'].mean():.2f}%")

def main():
    """Hàm main để chạy generator"""
    print("=== CARD GENERATOR ===")
    print("Sinh du lieu cards dua tren card_id tu card transactions")
    print("va phan khuc khach hang (A, B, C, D)")
    
    # Khoi tao generator
    generator = CardGenerator(test_config)
    
    # Sinh du lieu
    cards = generator.generate_cards()
    
    # Luu vao file
    generator.save_cards_to_csv(cards)
    
    print("\n=== HOAN THANH ===")
    print(f"Da sinh thanh cong {len(cards)} cards")

if __name__ == "__main__":
    main()
