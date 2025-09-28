"""
Balanced Data Generator
Generator với tất cả fixes để cân đối dữ liệu theo segment requirements
"""

import pandas as pd
import random
from datetime import datetime, timedelta
from typing import List, Dict
import os

from test_config import test_config
from customer_segment_generator import CustomerSegmentGenerator, CustomerSegment
from enhanced_transaction_generator import EnhancedTransactionGenerator, EnhancedTransaction
from phase2_account_generator import Phase2AccountGenerator, Phase2Account
from phase3_customer_generator import Phase3CustomerGenerator, Phase3Customer

class BalancedDataGenerator:
    """Balanced Data Generator với tất cả fixes"""
    
    def __init__(self, config: test_config = None):
        self.config = config or test_config()
        self.customer_segment_generator = CustomerSegmentGenerator(self.config)
        self.transaction_generator = EnhancedTransactionGenerator(self.config)
        self.account_generator = Phase2AccountGenerator(self.config)
        self.customer_generator = Phase3CustomerGenerator(self.config)

    def generate_balanced_dataset(self, num_customers: int) -> Dict[str, pd.DataFrame]:
        """Generate balanced dataset với tất cả fixes"""
        
        print(f"🚀 Bắt đầu generate BALANCED dataset với {num_customers} customers")
        print(f"📅 Thời gian: {self.config.START_DATE.strftime('%Y-%m-%d')} đến {self.config.END_DATE.strftime('%Y-%m-%d')}")
        print(f"🎯 Target segments: X({self.config.SEGMENT_DISTRIBUTION['VIP']*100:.0f}%), Y({self.config.SEGMENT_DISTRIBUTION['MEDIUM']*100:.0f}%), Z({self.config.SEGMENT_DISTRIBUTION['LOW']*100:.0f}%)")

        # 1. Generate customer segments
        print("\n1️⃣ Generating customer segments...")
        customer_segments = self.customer_segment_generator.generate_customers_by_count(num_customers)
        
        # Map segments to X, Y, Z format
        segment_mapping = {
            'VIP': 'X',
            'MEDIUM': 'Y', 
            'LOW': 'Z'
        }
        for segment in customer_segments:
            segment.segment = segment_mapping.get(segment.segment, segment.segment)
            # Update customer_code to X_, Y_, Z_ format
            if segment.customer_code.startswith('VIP_'):
                segment.customer_code = segment.customer_code.replace('VIP_', 'X_')
            elif segment.customer_code.startswith('MED_'):
                segment.customer_code = segment.customer_code.replace('MED_', 'Y_')
            elif segment.customer_code.startswith('LOW_'):
                segment.customer_code = segment.customer_code.replace('LOW_', 'Z_')
        
        print(f"   ✅ Generated {len(customer_segments)} customer segments")

        all_accounts: List[Phase2Account] = []
        all_transactions: List[EnhancedTransaction] = []
        customer_accounts_map: Dict[str, List[Phase2Account]] = {}

        # 2. Generate accounts using Balanced Account Generator
        print("\n2️⃣ Generating accounts with Balanced Account Generator...")
        for segment_info in customer_segments:
            customer_code = segment_info.customer_code
            customer_segment = segment_info.segment
            
            # Generate accounts for this customer
            accounts_for_customer = self._generate_balanced_accounts_for_customer(
                customer_code, customer_segment, self.config.START_DATE, self.config.END_DATE
            )
            all_accounts.extend(accounts_for_customer)
            customer_accounts_map[customer_code] = accounts_for_customer
        print(f"   ✅ Generated {len(all_accounts)} accounts")

        # 3. Generate transactions with balanced amounts
        print("\n3️⃣ Generating transactions with balanced amounts...")
        for account in all_accounts:
            # Determine segment
            if account.customer_code.startswith('X_'):
                segment = 'X'
            elif account.customer_code.startswith('Y_'):
                segment = 'Y'
            else:
                segment = 'Z'
            
            # Generate transactions with balanced amounts
            transactions_for_account = self._generate_balanced_transactions_for_account(
                account, segment, self.config.START_DATE, self.config.END_DATE
            )
            all_transactions.extend(transactions_for_account)
        print(f"   ✅ Generated {len(all_transactions)} transactions")

        # 4. Update account balances
        print("\n4️⃣ Updating account balances...")
        for account in all_accounts:
            account_transactions = [t for t in all_transactions if t.account_id == account.account_id]
            # Sort transactions by date
            account_transactions.sort(key=lambda x: x.transaction_date)
            
            # Calculate balance correctly
            current_balance = 0
            for transaction in account_transactions:
                if transaction.transaction_type in ['Deposit', 'Fund Transfer']:
                    current_balance += transaction.amount
                elif transaction.transaction_type in ['Principal Withdrawal', 'Interest Withdrawal', 'Fee Transaction']:
                    current_balance -= transaction.amount
                # Update transaction balance
                transaction.balance = current_balance
            
            # Update account balance
            account.current_balance = current_balance
        print(f"   ✅ Updated {len(all_accounts)} account balances")

        # 5. Generate customers using Balanced Customer Generator
        print("\n5️⃣ Generating customers with Balanced Customer Generator...")
        customers = self._generate_balanced_customers_from_data(
            [{'customer_code': acc.customer_code, 'account_id': acc.account_id} for acc in all_accounts],
            [{'customer_code': t.customer_code, 'account_id': t.account_id, 'amount': t.amount} for t in all_transactions]
        )
        print(f"   ✅ Generated {len(customers)} customers")

        # Convert to DataFrames
        transactions_df = pd.DataFrame([t.__dict__ for t in all_transactions])
        accounts_df = pd.DataFrame([a.__dict__ for a in all_accounts])
        customers_df = pd.DataFrame([c.__dict__ for c in customers])

        return {
            'transactions': transactions_df,
            'accounts': accounts_df,
            'customers': customers_df
        }

    def _generate_balanced_accounts_for_customer(self, customer_code: str, segment: str, start_date: datetime, end_date: datetime) -> List[Phase2Account]:
        """Generate balanced accounts for customer based on segment"""
        
        # Segment-based account preferences
        if segment == 'X':  # VIP
            min_accounts, max_accounts = 2, 5
            term_saving_ratio = 0.7  # 70% term_saving
            # Term months: 70% long-term (12, 24, 36), 30% medium-term (3, 6, 9)
            term_months_distribution = {
                12: 0.3, 24: 0.3, 36: 0.1,  # Long-term: 70%
                3: 0.1, 6: 0.1, 9: 0.1      # Medium-term: 30%
            }
            # Interest rates: 60% low (3-5%), 40% medium (5-7%)
            interest_rate_ranges = {
                'low': (0.03, 0.05, 0.6),
                'medium': (0.05, 0.07, 0.4)
            }
        elif segment == 'Y':  # MEDIUM
            min_accounts, max_accounts = 1, 3
            term_saving_ratio = 0.5  # 50% term_saving
            # Term months: 50% medium-term (3, 6, 9, 12), 50% short-term (1, 3)
            term_months_distribution = {
                3: 0.2, 6: 0.2, 9: 0.1, 12: 0.1,  # Medium-term: 50%
                1: 0.2, 3: 0.2                    # Short-term: 50%
            }
            # Interest rates: 50% medium (5-7%), 50% low (3-5%)
            interest_rate_ranges = {
                'medium': (0.05, 0.07, 0.5),
                'low': (0.03, 0.05, 0.5)
            }
        else:  # Z - LOW
            min_accounts, max_accounts = 1, 2
            term_saving_ratio = 0.2  # 20% term_saving
            # Term months: 20% short-term (1, 3), 80% demand
            term_months_distribution = {
                1: 0.1, 3: 0.1  # Short-term: 20%
            }
            # Interest rates: 70% high (>=7%), 30% medium (5-7%)
            interest_rate_ranges = {
                'high': (0.07, 0.10, 0.7),
                'medium': (0.05, 0.07, 0.3)
            }
        
        accounts = []
        num_accounts = random.randint(min_accounts, max_accounts)
        
        for i in range(num_accounts):
            # Generate account ID
            account_id = f"ACC_{customer_code}_{i+1:02d}"
            
            # Determine product type based on segment preferences
            if random.random() < term_saving_ratio:
                product_type = 'term_saving'
                # Select term months based on distribution
                term_months = random.choices(
                    list(term_months_distribution.keys()),
                    weights=list(term_months_distribution.values()),
                    k=1
                )[0]
            else:
                product_type = 'demand_saving'
                term_months = 0
            
            # Generate open date
            open_date = self._generate_random_date(start_date, end_date)
            
            # Generate maturity date based on product type
            if product_type == 'demand_saving':
                maturity_date = None
            else:
                maturity_date = open_date + timedelta(days=term_months * 30)
            
            # Generate interest rate based on segment
            rate_type = random.choices(
                list(interest_rate_ranges.keys()),
                weights=[r[2] for r in interest_rate_ranges.values()],
                k=1
            )[0]
            min_rate, max_rate, _ = interest_rate_ranges[rate_type]
            interest_rate = round(random.uniform(min_rate, max_rate), 5)
            
            # Generate status based on distribution
            status_distribution = {'active': 0.825, 'closed': 0.125, 'suspend': 0.05}
            status = random.choices(
                list(status_distribution.keys()),
                weights=list(status_distribution.values()),
                k=1
            )[0]
            
            # Generate channel
            channels = ['mobile/internet', 'atm', 'branch']
            channel_opened = random.choice(channels)
            
            # Generate currency
            currency_distribution = {'VND': 0.85, 'USD': 0.10, 'EUR': 0.05}
            currency = random.choices(
                list(currency_distribution.keys()),
                weights=list(currency_distribution.values()),
                k=1
            )[0]
            
            # Initial balance
            current_balance = 0.0
            
            account = Phase2Account(
                account_id=account_id,
                customer_code=customer_code,
                product_type=product_type,
                open_date=open_date,
                maturity_date=maturity_date,
                term_months=term_months,
                interest_rate=interest_rate,
                status=status,
                channel_opened=channel_opened,
                currency=currency,
                current_balance=current_balance
            )
            
            accounts.append(account)
        
        return accounts

    def _generate_balanced_transactions_for_account(self, account: Phase2Account, segment: str, start_date: datetime, end_date: datetime) -> List[EnhancedTransaction]:
        """Generate balanced transactions for account with fixed amount ranges"""
        
        transactions = []
        effective_maturity_date = account.maturity_date if account.maturity_date else end_date
        
        # RFM requirements by segment with fixed amount ranges
        rfm_requirements = {
            'X': {
                'frequency_per_month': (6, 8),
                'amount_min': 50_000_000,  # 50M VND minimum
                'amount_max': 200_000_000, # 200M VND maximum
                'recency_days': 30
            },
            'Y': {
                'frequency_per_month': (3, 4),
                'amount_min': 30_000_000,  # 30M VND minimum
                'amount_max': 100_000_000, # 100M VND maximum
                'recency_days': 180
            },
            'Z': {
                'frequency_per_month': (2, 3),
                'amount_min': 5_000_000,   # 5M VND minimum
                'amount_max': 20_000_000,  # 20M VND maximum
                'recency_days': 365
            }
        }
        
        req = rfm_requirements[segment]
        
        # Calculate total transactions needed
        months = (end_date - start_date).days // 30
        min_transactions = req['frequency_per_month'][0] * months
        max_transactions = req['frequency_per_month'][1] * months
        total_transactions = random.randint(min_transactions, max_transactions)
        
        # Generate transactions with balanced amounts
        for i in range(total_transactions):
            # Generate date with RFM compliance
            if segment == 'X':
                # X segment: bias towards recent transactions
                if random.random() < 0.8:
                    random_days = random.randint((end_date - start_date).days - 30, (end_date - start_date).days)
                else:
                    random_days = random.randint(0, (end_date - start_date).days)
            elif segment == 'Y':
                # Y segment: bias towards recent transactions within 6 months
                if random.random() < 0.6:
                    random_days = random.randint((end_date - start_date).days - 180, (end_date - start_date).days)
                else:
                    random_days = random.randint(0, (end_date - start_date).days)
            else:  # Z
                # Z segment: spread throughout period, avoid recent transactions
                if random.random() < 0.8 and (end_date - start_date).days > 180:
                    random_days = random.randint(0, (end_date - start_date).days - 180)
                else:
                    random_days = random.randint(0, (end_date - start_date).days)
            
            transaction_date = start_date + timedelta(days=random_days)
            
            # Determine transaction type based on date and account
            days_from_open = (transaction_date - account.open_date).days
            days_to_maturity = (effective_maturity_date - transaction_date).days if effective_maturity_date else float('inf')
            
            # Logic: gần open_date → Deposit, gần maturity_date → Withdrawal
            if days_from_open < 30:  # Near open_date
                transaction_type = 'Deposit'
            elif days_to_maturity < 30:  # Near maturity_date
                transaction_type = random.choice(['Principal Withdrawal', 'Interest Withdrawal'])
            else:  # In between
                if random.random() < 0.7:  # 70% deposits for better RFM compliance
                    transaction_type = 'Deposit'
                else:
                    transaction_type = random.choice(['Principal Withdrawal', 'Interest Withdrawal', 'Fund Transfer', 'Fee Transaction'])
            
            # Determine amount based on segment and transaction type with fixed ranges
            if transaction_type in ['Deposit', 'Fund Transfer']:
                amount = random.randint(req['amount_min'], req['amount_max'])
            else:  # Withdrawals, Fees
                # Withdrawals should be smaller than deposits but still >= 5M minimum
                withdrawal_max = min(req['amount_max'] // 2, req['amount_max'])
                withdrawal_min = max(req['amount_min'] // 2, 5_000_000)  # At least 5M for withdrawals
                amount = random.randint(withdrawal_min, withdrawal_max)
            
            # Generate transaction
            currency = random.choices(['VND', 'USD', 'EUR'], weights=[0.85, 0.10, 0.05], k=1)[0]
            tran_amt_lcy = amount * {'VND': 1, 'USD': 25, 'EUR': 30}.get(currency, 1)
            status = random.choices(['Pending', 'Posted', 'Declined'], weights=[0.10, 0.85, 0.05], k=1)[0]
            channel = random.choice(['mobile/internet', 'atm', 'branch'])
            
            transaction = EnhancedTransaction(
                transaction_id=f"TXN_{random.randint(100000, 999999)}",
                account_id=account.account_id,
                customer_code=account.customer_code,
                transaction_date=transaction_date,
                transaction_type=transaction_type,
                transaction_desc=f"{transaction_type} transaction for {account.customer_code}",
                amount=amount,
                balance=0,  # Will be calculated later
                channel_txn=channel,
                status_txn=status,
                tran_amt_acy=amount,
                tran_amt_lcy=tran_amt_lcy,
                currency=currency
            )
            transactions.append(transaction)
        
        # Sort by date
        transactions.sort(key=lambda x: x.transaction_date)
        
        return transactions

    def _generate_balanced_customers_from_data(self, customer_accounts: List[Dict], customer_transactions: List[Dict]) -> List[Phase3Customer]:
        """Generate balanced customers from account and transaction data"""
        
        customers = []
        customer_data_map = {}
        
        # Group data by customer
        for account_data in customer_accounts:
            customer_code = account_data['customer_code']
            if customer_code not in customer_data_map:
                customer_data_map[customer_code] = {
                    'accounts': [],
                    'transactions': []
                }
            customer_data_map[customer_code]['accounts'].append(account_data)
        
        for transaction_data in customer_transactions:
            customer_code = transaction_data['customer_code']
            if customer_code in customer_data_map:
                customer_data_map[customer_code]['transactions'].append(transaction_data)
        
        # Generate customer for each customer_code
        for customer_code, data in customer_data_map.items():
            customer = self._create_balanced_customer_from_data(customer_code, data)
            customers.append(customer)
        
        return customers

    def _create_balanced_customer_from_data(self, customer_code: str, data: Dict) -> Phase3Customer:
        """Create balanced customer from account and transaction data"""
        
        # Determine segment from customer_code
        if customer_code.startswith('X_'):
            segment = 'X'
        elif customer_code.startswith('Y_'):
            segment = 'Y'
        else:
            segment = 'Z'
        
        # Generate demographics based on segment
        gender = random.choice(['Nam', 'Nữ'])
        full_name = self._generate_vietnamese_name(gender)
        
        # Age generation based on segment
        if segment == 'X':  # VIP: 25-40 tuổi
            age = random.randint(25, 40)
        elif segment == 'Y':  # MEDIUM: 20-55 tuổi
            age = random.randint(20, 55)
        else:  # Z - LOW: <25 tuổi hoặc >=55 tuổi
            if random.random() < 0.5:
                age = random.randint(18, 24)  # <25 tuổi
            else:
                age = random.randint(55, 80)  # >=55 tuổi
        
        dob = datetime.now() - timedelta(days=age * 365)
        
        # City generation
        cities = [
            'Hà Nội', 'TP. Hồ Chí Minh', 'Đà Nẵng', 'Hải Phòng', 'Cần Thơ',
            'An Giang', 'Bà Rịa - Vũng Tàu', 'Bắc Giang', 'Bắc Kạn', 'Bạc Liêu',
            'Bắc Ninh', 'Bến Tre', 'Bình Định', 'Bình Dương', 'Bình Phước',
            'Bình Thuận', 'Cà Mau', 'Cao Bằng', 'Đắk Lắk', 'Đắk Nông',
            'Điện Biên', 'Đồng Nai', 'Đồng Tháp', 'Gia Lai', 'Hà Giang',
            'Hà Nam', 'Hà Tĩnh', 'Hải Dương', 'Hậu Giang', 'Hòa Bình',
            'Hưng Yên', 'Khánh Hòa', 'Kiên Giang', 'Kon Tum', 'Lai Châu',
            'Lâm Đồng', 'Lạng Sơn', 'Lào Cai', 'Long An', 'Nam Định',
            'Nghệ An', 'Ninh Bình', 'Ninh Thuận', 'Phú Thọ', 'Phú Yên',
            'Quảng Bình', 'Quảng Nam', 'Quảng Ngãi', 'Quảng Ninh', 'Quảng Trị',
            'Sóc Trăng', 'Sơn La', 'Tây Ninh', 'Thái Bình', 'Thái Nguyên',
            'Thanh Hóa', 'Thừa Thiên Huế', 'Tiền Giang', 'Trà Vinh', 'Tuyên Quang',
            'Vĩnh Long', 'Vĩnh Phúc', 'Yên Bái'
        ]
        city = random.choice(cities)
        
        marital_status = random.choice(['Độc thân', 'Kết hôn'])
        nationality = random.choices(['Việt Nam', 'Nước ngoài'], weights=[0.98, 0.02], k=1)[0]
        
        # Occupation generation based on segment
        if segment == 'X':  # VIP: Quản lý/Chuyên gia + Kinh doanh cá thể
            occupation = random.choices(
                ['Quản lý / chuyên gia', 'Kinh doanh cá thể'],
                weights=[0.6, 0.4],
                k=1
            )[0]
        elif segment == 'Y':  # MEDIUM: Công nhân/Lao động + Nhân viên văn phòng
            occupation = random.choices(
                ['Công nhân / lao động phổ thông', 'Nhân viên văn phòng'],
                weights=[0.5, 0.5],
                k=1
            )[0]
        else:  # Z - LOW: Nhóm khác
            occupation = random.choices(
                ['Khác (sinh viên, nội trợ…)', 'Nhân viên văn phòng', 'Công nhân / lao động phổ thông'],
                weights=[0.8, 0.1, 0.1],
                k=1
            )[0]
        
        # Income generation based on segment
        if segment == 'X':  # VIP: 20-50M, >50M
            income_range = random.choices(['20-50 triệu', '>50 triệu'], weights=[0.6, 0.4], k=1)[0]
        elif segment == 'Y':  # MEDIUM: 10-20M, 20-50M
            income_range = random.choices(['10-20 triệu', '20-50 triệu'], weights=[0.5, 0.5], k=1)[0]
        else:  # Z - LOW: <10M, 10-20M
            income_range = random.choices(['<10 triệu', '10-20 triệu'], weights=[0.7, 0.3], k=1)[0]
        
        income_currency = random.choices(['VND', 'USD'], weights=[0.95, 0.05], k=1)[0]
        
        # Source of income based on segment
        if segment == 'X':  # VIP: Lương, Kinh doanh, Đầu tư
            source_of_income = random.choices(['Lương', 'Kinh doanh', 'Đầu tư'], weights=[0.4, 0.4, 0.2], k=1)[0]
        elif segment == 'Y':  # MEDIUM: Lương, Kinh doanh
            source_of_income = random.choices(['Lương', 'Kinh doanh'], weights=[0.7, 0.3], k=1)[0]
        else:  # Z - LOW: Lương, Khác
            source_of_income = random.choices(['Lương', 'Khác'], weights=[0.6, 0.4], k=1)[0]
        
        # Status generation
        status = random.choices(['Active', 'Inactive', 'Closed'], weights=[0.80, 0.15, 0.05], k=1)[0]
        
        return Phase3Customer(
            customer_code=customer_code,
            full_name=full_name,
            gender=gender,
            dob=dob,
            city=city,
            marital_status=marital_status,
            nationality=nationality,
            occupation=occupation,
            income_range=income_range,
            income_currency=income_currency,
            source_of_income=source_of_income,
            status=status,
            customer_segment=segment
        )

    def _generate_vietnamese_name(self, gender: str) -> str:
        """Generate Vietnamese full name"""
        vietnamese_names = {
            'male': [
                'Nguyễn Văn An', 'Trần Văn Bình', 'Lê Văn Cường', 'Phạm Văn Dũng', 'Hoàng Văn Em',
                'Vũ Văn Phong', 'Đặng Văn Giang', 'Bùi Văn Hải', 'Đỗ Văn Hùng', 'Hồ Văn Khoa',
                'Ngô Văn Long', 'Dương Văn Minh', 'Lý Văn Nam', 'Phan Văn Oanh', 'Võ Văn Phúc',
                'Đinh Văn Quang', 'Tôn Văn Rồng', 'Lưu Văn Sơn', 'Chu Văn Tài', 'Lương Văn Uy'
            ],
            'female': [
                'Nguyễn Thị An', 'Trần Thị Bình', 'Lê Thị Cường', 'Phạm Thị Dũng', 'Hoàng Thị Em',
                'Vũ Thị Phong', 'Đặng Thị Giang', 'Bùi Thị Hải', 'Đỗ Thị Hùng', 'Hồ Thị Khoa',
                'Ngô Thị Long', 'Dương Thị Minh', 'Lý Thị Nam', 'Phan Thị Oanh', 'Võ Thị Phúc',
                'Đinh Thị Quang', 'Tôn Thị Rồng', 'Lưu Thị Sơn', 'Chu Thị Tài', 'Lương Thị Uy'
            ]
        }
        
        if gender == 'Nam':
            return random.choice(vietnamese_names['male'])
        else:
            return random.choice(vietnamese_names['female'])

    def _generate_random_date(self, start_date: datetime, end_date: datetime) -> datetime:
        """Generate random date between start and end"""
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        random_date = start_date + timedelta(days=random_number_of_days)
        return random_date

    def export_to_csv(self, dataset: Dict[str, pd.DataFrame], output_prefix: str = "output/balanced_banking_data"):
        """Export data to CSV files"""
        print("\n📁 Exporting data to CSV files...")
        transactions_file = f"{output_prefix}_transactions.csv"
        accounts_file = f"{output_prefix}_accounts.csv"
        customers_file = f"{output_prefix}_customers.csv"

        dataset['transactions'].to_csv(transactions_file, index=False)
        dataset['accounts'].to_csv(accounts_file, index=False)
        dataset['customers'].to_csv(customers_file, index=False)

        print(f"   ✅ Transactions exported to {transactions_file}")
        print(f"   ✅ Accounts exported to {accounts_file}")
        print(f"   ✅ Customers exported to {customers_file}")
        return {'transactions_file': transactions_file, 'accounts_file': accounts_file, 'customers_file': customers_file}

def main():
    """Test Balanced Data Generator"""
    generator = BalancedDataGenerator()
    
    # Generate dataset
    dataset = generator.generate_balanced_dataset(1000)
    output_files = generator.export_to_csv(dataset)
    
    print("\n✅ Balanced dataset generation completed!")
    print(f"📁 Files saved to: {output_files}")

    # Print summary
    print("\n📊 SUMMARY:")
    print(f"  • Total customers: {len(dataset['customers'])}")
    print(f"  • Total accounts: {len(dataset['accounts'])}")
    print(f"  • Total transactions: {len(dataset['transactions'])}")

    # Segment distribution
    segment_counts = dataset['customers']['customer_segment'].value_counts()
    print(f"\n📈 SEGMENT DISTRIBUTION:")
    for segment, count in segment_counts.items():
        percentage = (count / len(dataset['customers'])) * 100
        print(f"  • {segment}: {count} ({percentage:.1f}%)")

    # Transaction amount summary
    amounts = dataset['transactions']['amount']
    print(f"\n💰 TRANSACTION AMOUNT SUMMARY:")
    print(f"  • Min: {amounts.min():,.0f} VND")
    print(f"  • Max: {amounts.max():,.0f} VND")
    print(f"  • Mean: {amounts.mean():,.0f} VND")

if __name__ == "__main__":
    main()
