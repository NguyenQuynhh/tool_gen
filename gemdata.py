try:
    import pandas as pd
    import numpy as np
    import random
    from datetime import datetime, timedelta
    from faker import Faker
    import uuid
except ImportError as e:
    print(f"Lỗi import: {e}")
    print("Vui lòng cài đặt các packages cần thiết:")
    print("pip install pandas numpy faker")
    exit(1)

# Initialize Faker for Vietnamese locale
fake = Faker('vi_VN')

class BankingDataGenerator:
    def __init__(self):
        self.customers = []
        self.savings_accounts = []
        self.savings_transactions = []
        
        # Customer segments for RFM/CLV analysis
        self.customer_segments = {
            'premium': {'weight': 0.15, 'income_range': (50, 200), 'accounts_per_customer': (3, 6)},
            'loyal': {'weight': 0.25, 'income_range': (20, 50), 'accounts_per_customer': (2, 4)},
            'regular': {'weight': 0.35, 'income_range': (10, 20), 'accounts_per_customer': (1, 3)},
            'basic': {'weight': 0.25, 'income_range': (5, 10), 'accounts_per_customer': (1, 2)}
        }
        
        # Vietnamese cities with different transaction patterns
        self.cities = {
            'Hồ Chí Minh': {'mobile_ratio': 0.6, 'atm_ratio': 0.25, 'branch_ratio': 0.15},
            'Hà Nội': {'mobile_ratio': 0.55, 'atm_ratio': 0.3, 'branch_ratio': 0.15},
            'Đà Nẵng': {'mobile_ratio': 0.5, 'atm_ratio': 0.35, 'branch_ratio': 0.15},
            'Cần Thơ': {'mobile_ratio': 0.45, 'atm_ratio': 0.4, 'branch_ratio': 0.15},
            'Hải Phòng': {'mobile_ratio': 0.45, 'atm_ratio': 0.4, 'branch_ratio': 0.15},
            'Other': {'mobile_ratio': 0.4, 'atm_ratio': 0.45, 'branch_ratio': 0.15}
        }
        
        # Interest rates by term
        self.interest_rates = {
            'demand': (0.01, 0.5),
            '1_month': (2.8, 3.2),
            '3_month': (3.5, 4.0),
            '6_month': (4.2, 4.8),
            '9_month': (4.5, 5.0),
            '12_month': (4.8, 5.5),
            '24_month': (5.0, 6.0),
            '36_month': (6.0, 7.0)
        }
        
        # Transaction types and their constraints
        self.transaction_types = {
            'Deposit': {'weight': 0.4, 'amount_range': (1000000, 50000000)},
            'Interest Withdrawal': {'weight': 0.2, 'amount_range': (100000, 5000000)},
            'Principal Withdrawal': {'weight': 0.15, 'amount_range': (1000000, 20000000)},
            'Fund Transfer': {'weight': 0.2, 'amount_range': (500000, 10000000)},
            'Fee Transaction': {'weight': 0.05, 'amount_range': (50000, 200000)}
        }

    def generate_customers(self, num_customers=10000):
        """Generate customer data following RFM/CLV segmentation"""
        print("Generating customers...")
        
        for i in range(num_customers):
            # Determine customer segment
            segment = np.random.choice(
                list(self.customer_segments.keys()),
                p=[seg['weight'] for seg in self.customer_segments.values()]
            )
            
            # Generate customer data
            customer = {
                'customer_code': f"CIF{str(i+1).zfill(6)}",
                'full_name': fake.name(),
                'gender': random.choice(['Nam', 'Nữ']),
                'DOB': self._generate_dob(),
                'city': random.choice(list(self.cities.keys())),
                'marital_status': random.choice(['Độc thân', 'Kết hôn']),
                'nationality': 'Việt Nam' if random.random() < 0.98 else 'Nước ngoài',
                'occupation': self._generate_occupation(segment),
                'income_range': self._generate_income_range(segment),
                'income_currency': random.choices(['VND', 'USD'], weights=[0.85, 0.15])[0],
                'source_of_income': random.choices(
                    ['Lương', 'Kinh doanh', 'Đầu tư', 'Khác'],
                    weights=[0.4, 0.3, 0.2, 0.1]
                )[0],
                'status': random.choices(
                    ['Active', 'Inactive', 'Closed'],
                    weights=[0.8, 0.15, 0.05]
                )[0],
                'segment': segment
            }
            
            self.customers.append(customer)
        
        print(f"Generated {len(self.customers)} customers")
        return self.customers

    def generate_savings_accounts(self):
        """Generate savings accounts based on customer segments"""
        print("Generating savings accounts...")
        
        account_id = 1
        for customer in self.customers:
            segment = customer['segment']
            segment_config = self.customer_segments[segment]
            
            # Number of accounts per customer based on segment
            num_accounts = random.randint(
                segment_config['accounts_per_customer'][0],
                segment_config['accounts_per_customer'][1]
            )
            
            for _ in range(num_accounts):
                # Generate account data
                product_type = self._generate_product_type(segment)
                term_months = self._generate_term_months(product_type)
                open_date = self._generate_open_date()
                maturity_date = self._generate_maturity_date(open_date, term_months)
                interest_rate = self._generate_interest_rate(product_type, term_months)
                
                account = {
                    'account_id': f"SAV{str(account_id).zfill(8)}",
                    'customer_code': customer['customer_code'],
                    'product_type': product_type,
                    'open_date': open_date,
                    'maturity_date': maturity_date,
                    'term_months': term_months,
                    'interest_rate': interest_rate,
                    'status': self._generate_account_status(open_date, maturity_date),
                    'channel_opened': self._generate_channel(customer['city'])
                }
                
                self.savings_accounts.append(account)
                account_id += 1
        
        print(f"Generated {len(self.savings_accounts)} savings accounts")
        return self.savings_accounts

    def generate_savings_transactions(self):
        """Generate transactions following business rules"""
        print("Generating savings transactions...")
        
        transaction_id = 1
        
        for account in self.savings_accounts:
            customer = next(c for c in self.customers if c['customer_code'] == account['customer_code'])
            
            # Generate transactions for this account
            num_transactions = self._calculate_transaction_count(account, customer)
            balance = 0
            
            for i in range(num_transactions):
                transaction_date = self._generate_transaction_date(account)
                transaction_type = self._generate_transaction_type(account, transaction_date, i)
                amount = self._generate_transaction_amount(transaction_type, customer['segment'])
                
                # Update balance
                if transaction_type in ['Deposit', 'Fund Transfer']:
                    balance += amount
                else:
                    balance = max(0, balance - amount)
                
                transaction = {
                    'transaction_id': f"TXN{str(transaction_id).zfill(10)}",
                    'account_id': account['account_id'],
                    'customer_code': account['customer_code'],
                    'transaction_date': transaction_date,
                    'transaction_type': transaction_type,
                    'transaction_desc': self._generate_transaction_desc(transaction_type),
                    'amount': amount,
                    'balance': balance,
                    'channel_txn': self._generate_channel(customer['city']),
                    'status_txn': random.choices(
                        ['Pending', 'Posted', 'Declined'],
                        weights=[0.1, 0.85, 0.05]
                    )[0],
                    'TRAN_AMT_ACY': amount,
                    'TRAN_AMT_LCY': self._convert_currency(amount, customer['income_currency']),
                    'currency': customer['income_currency']
                }
                
                self.savings_transactions.append(transaction)
                transaction_id += 1
        
        print(f"Generated {len(self.savings_transactions)} transactions")
        return self.savings_transactions

    def _generate_dob(self):
        """Generate date of birth with age distribution"""
        age_groups = [(18, 25), (25, 40), (40, 55), (55, 70)]
        weights = [0.2, 0.4, 0.3, 0.1]
        
        age_group = random.choices(age_groups, weights=weights)[0]
        age = random.randint(age_group[0], age_group[1])
        
        start_date = datetime.now() - timedelta(days=age * 365)
        end_date = start_date + timedelta(days=365)
        
        return fake.date_between(start_date=start_date, end_date=end_date)

    def _generate_occupation(self, segment):
        """Generate occupation based on customer segment"""
        if segment == 'premium':
            return random.choices(
                ['Quản lý / chuyên gia', 'Kinh doanh cá thể'],
                weights=[0.7, 0.3]
            )[0]
        elif segment == 'loyal':
            return random.choices(
                ['Quản lý / chuyên gia', 'Nhân viên văn phòng', 'Kinh doanh cá thể'],
                weights=[0.4, 0.4, 0.2]
            )[0]
        else:
            return random.choices(
                ['Nhân viên văn phòng', 'Công nhân / lao động phổ thông', 'Khác'],
                weights=[0.5, 0.3, 0.2]
            )[0]

    def _generate_income_range(self, segment):
        """Generate income range based on segment"""
        segment_config = self.customer_segments[segment]
        min_income, max_income = segment_config['income_range']
        
        if max_income <= 10:
            return '<10 triệu'
        elif max_income <= 20:
            return '10–20 triệu'
        elif max_income <= 50:
            return '20–50 triệu'
        else:
            return '>50 triệu'

    def _generate_product_type(self, segment):
        """Generate product type based on customer segment"""
        if segment in ['premium', 'loyal']:
            return random.choices(
                ['demand_saving', 'term_saving'],
                weights=[0.3, 0.7]
            )[0]
        else:
            return random.choices(
                ['demand_saving', 'term_saving'],
                weights=[0.7, 0.3]
            )[0]

    def _generate_term_months(self, product_type):
        """Generate term months based on product type"""
        if product_type == 'demand_saving':
            return 0
        else:
            return random.choice([1, 3, 6, 9, 12, 24, 36])

    def _generate_open_date(self):
        """Generate account opening date within last 3 years"""
        start_date = datetime.now() - timedelta(days=3*365)
        end_date = datetime.now() - timedelta(days=30)
        return fake.date_between(start_date=start_date, end_date=end_date)

    def _generate_maturity_date(self, open_date, term_months):
        """Generate maturity date based on term months"""
        if term_months == 0:
            return None
        
        open_dt = datetime.strptime(str(open_date), '%Y-%m-%d')
        maturity_dt = open_dt + timedelta(days=term_months * 30)
        return maturity_dt.date()

    def _generate_interest_rate(self, product_type, term_months):
        """Generate interest rate based on product type and term"""
        if product_type == 'demand_saving':
            return round(random.uniform(*self.interest_rates['demand']), 2)
        
        term_key = f"{term_months}_month"
        if term_key in self.interest_rates:
            return round(random.uniform(*self.interest_rates[term_key]), 2)
        else:
            return round(random.uniform(4.0, 6.0), 2)

    def _generate_account_status(self, open_date, maturity_date):
        """Generate account status based on dates and activity"""
        open_dt = datetime.strptime(str(open_date), '%Y-%m-%d')
        now = datetime.now()
        
        if maturity_date:
            maturity_dt = datetime.strptime(str(maturity_date), '%Y-%m-%d')
            if now > maturity_dt:
                return random.choices(['active', 'closed'], weights=[0.2, 0.8])[0]
        
        # Check if account is old enough to be suspended
        if (now - open_dt).days > 180:
            return random.choices(['active', 'suspend'], weights=[0.9, 0.1])[0]
        
        return random.choices(['active', 'suspend'], weights=[0.95, 0.05])[0]

    def _generate_channel(self, city):
        """Generate channel based on city"""
        city_config = self.cities.get(city, self.cities['Other'])
        return random.choices(
            ['mobile/internet', 'atm', 'branch'],
            weights=[city_config['mobile_ratio'], city_config['atm_ratio'], city_config['branch_ratio']]
        )[0]

    def _calculate_transaction_count(self, account, customer):
        """Calculate number of transactions based on account and customer segment"""
        base_count = 5
        segment_multiplier = {'premium': 2.5, 'loyal': 2.0, 'regular': 1.5, 'basic': 1.0}
        
        # More transactions for term accounts
        if account['product_type'] == 'term_saving':
            base_count *= 1.5
        
        # More transactions for active customers
        if customer['status'] == 'Active':
            base_count *= 1.3
        
        return int(base_count * segment_multiplier[customer['segment']] * random.uniform(0.5, 1.5))

    def _generate_transaction_date(self, account):
        """Generate transaction date within account lifecycle"""
        open_date = datetime.strptime(str(account['open_date']), '%Y-%m-%d')
        
        if account['maturity_date']:
            maturity_date = datetime.strptime(str(account['maturity_date']), '%Y-%m-%d')
            end_date = min(maturity_date, datetime.now())
        else:
            end_date = datetime.now()
        
        return fake.date_between(start_date=open_date, end_date=end_date)

    def _generate_transaction_type(self, account, transaction_date, transaction_index):
        """Generate transaction type based on business rules"""
        open_date = datetime.strptime(str(account['open_date']), '%Y-%m-%d')
        transaction_dt = datetime.strptime(str(transaction_date), '%Y-%m-%d')
        
        # For term accounts
        if account['product_type'] == 'term_saving':
            if account['maturity_date']:
                maturity_date = datetime.strptime(str(account['maturity_date']), '%Y-%m-%d')
                
                # Near maturity - more withdrawals
                if (maturity_date - transaction_dt).days < 30:
                    return random.choices(
                        ['Interest Withdrawal', 'Principal Withdrawal'],
                        weights=[0.6, 0.4]
                    )[0]
                
                # Near opening - more deposits
                elif (transaction_dt - open_date).days < 30:
                    return random.choices(
                        ['Deposit', 'Fund Transfer'],
                        weights=[0.7, 0.3]
                    )[0]
            
            # During term period
            return random.choices(
                ['Interest Withdrawal', 'Deposit', 'Fund Transfer', 'Fee Transaction'],
                weights=[0.4, 0.3, 0.25, 0.05]
            )[0]
        
        # For demand accounts
        else:
            return random.choices(
                ['Deposit', 'Interest Withdrawal', 'Principal Withdrawal', 'Fund Transfer', 'Fee Transaction'],
                weights=[0.4, 0.25, 0.2, 0.1, 0.05]
            )[0]

    def _generate_transaction_amount(self, transaction_type, segment):
        """Generate transaction amount based on type and customer segment"""
        base_ranges = self.transaction_types[transaction_type]['amount_range']
        
        # Adjust based on customer segment
        segment_multiplier = {'premium': 3.0, 'loyal': 2.0, 'regular': 1.0, 'basic': 0.5}
        multiplier = segment_multiplier[segment]
        
        min_amount = int(base_ranges[0] * multiplier)
        max_amount = int(base_ranges[1] * multiplier)
        
        return random.randint(min_amount, max_amount)

    def _generate_transaction_desc(self, transaction_type):
        """Generate transaction description based on type"""
        descriptions = {
            'Deposit': 'Gửi tiền vào tài khoản tiết kiệm',
            'Interest Withdrawal': 'Rút lãi tiết kiệm',
            'Principal Withdrawal': 'Rút gốc tiết kiệm',
            'Fund Transfer': 'Chuyển tiền từ tài khoản thanh toán',
            'Fee Transaction': 'Phí dịch vụ ngân hàng'
        }
        return descriptions[transaction_type]

    def _convert_currency(self, amount, currency):
        """Convert amount to local currency"""
        if currency == 'VND':
            return amount
        elif currency == 'USD':
            return int(amount * 25)
        elif currency == 'EUR':
            return int(amount * 30)
        return amount

    def export_to_csv(self, output_dir='output'):
        """Export all data to CSV files"""
        import os
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        print(f"Đang lưu dữ liệu vào thư mục: {output_dir}")
        
        # Export customers
        customers_df = pd.DataFrame(self.customers)
        customers_file = f'{output_dir}/customers.csv'
        customers_df.to_csv(customers_file, index=False, encoding='utf-8-sig')
        print(f"✓ Đã lưu {len(customers_df)} khách hàng vào: {customers_file}")
        
        # Export savings accounts
        accounts_df = pd.DataFrame(self.savings_accounts)
        accounts_file = f'{output_dir}/savings_accounts.csv'
        accounts_df.to_csv(accounts_file, index=False, encoding='utf-8-sig')
        print(f"✓ Đã lưu {len(accounts_df)} tài khoản tiết kiệm vào: {accounts_file}")
        
        # Export transactions
        transactions_df = pd.DataFrame(self.savings_transactions)
        transactions_file = f'{output_dir}/savings_transactions.csv'
        transactions_df.to_csv(transactions_file, index=False, encoding='utf-8-sig')
        print(f"✓ Đã lưu {len(transactions_df)} giao dịch vào: {transactions_file}")
        
        print(f"\n📁 Dữ liệu đã được lưu vào thư mục: {output_dir}/")
        
        # Print summary statistics
        self.print_summary()


    def print_summary(self):
        """Print summary statistics"""
        print("\n=== DATA GENERATION SUMMARY ===")
        print(f"Customers: {len(self.customers)}")
        print(f"Savings Accounts: {len(self.savings_accounts)}")
        print(f"Transactions: {len(self.savings_transactions)}")
        
        # Customer segment distribution
        segment_counts = {}
        for customer in self.customers:
            segment = customer['segment']
            segment_counts[segment] = segment_counts.get(segment, 0) + 1
        
        print("\nCustomer Segment Distribution:")
        for segment, count in segment_counts.items():
            percentage = (count / len(self.customers)) * 100
            print(f"  {segment}: {count} ({percentage:.1f}%)")
        
        # Account type distribution
        account_types = {}
        for account in self.savings_accounts:
            acc_type = account['product_type']
            account_types[acc_type] = account_types.get(acc_type, 0) + 1
        
        print("\nAccount Type Distribution:")
        for acc_type, count in account_types.items():
            percentage = (count / len(self.savings_accounts)) * 100
            print(f"  {acc_type}: {count} ({percentage:.1f}%)")
        
        # Transaction type distribution
        txn_types = {}
        for txn in self.savings_transactions:
            txn_type = txn['transaction_type']
            txn_types[txn_type] = txn_types.get(txn_type, 0) + 1
        
        print("\nTransaction Type Distribution:")
        for txn_type, count in txn_types.items():
            percentage = (count / len(self.savings_transactions)) * 100
            print(f"  {txn_type}: {count} ({percentage:.1f}%)")

def main():
    """Main function to generate all data"""
    print("🚀 Bắt đầu tạo dữ liệu ngân hàng...")
    
    # Initialize generator
    generator = BankingDataGenerator()
    
    # Generate data
    generator.generate_customers(10000)
    generator.generate_savings_accounts()
    generator.generate_savings_transactions()
    
    # Export to CSV
    print("\n📊 Đang xuất dữ liệu...")
    generator.export_to_csv()  # Chỉ lưu vào output/
    
    print("\n✅ Hoàn thành tạo dữ liệu thành công!")
    print("\n📁 Dữ liệu đã được lưu vào thư mục: output/")

if __name__ == "__main__":
    main()
