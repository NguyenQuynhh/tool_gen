"""
New Account Generator với logic mới theo phân khúc khách hàng
X(50%) - Không dùng demand saving, chỉ dài hạn, lãi cao
Y(30%) - Mix term và demand saving, lãi trung bình
Z(20%) - Chủ yếu demand saving, ít term ngắn hạn, lãi thấp
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict
from dataclasses import dataclass

from test_config import test_config

@dataclass
class NewAccount:
    """New Account data structure"""
    account_id: str
    customer_code: str
    product_type: str
    open_date: datetime
    maturity_date: datetime
    term_months: int
    interest_rate: float
    status: str
    channel_opened: str
    currency: str
    current_balance: float

class NewAccountGenerator:
    """New Account Generator với logic mới theo phân khúc"""
    
    def __init__(self, config: test_config = None):
        self.config = config or test_config()
        
        # Channels
        self.channels = ['mobile/internet', 'atm', 'branch']
        
        # Currency distribution
        self.currency_distribution = {
            'VND': 0.85,
            'USD': 0.10,
            'EUR': 0.05
        }
        
        # Status distribution
        self.status_distribution = {
            'active': 0.825,
            'closed': 0.125,
            'suspend': 0.05
        }
        
        # Segment-specific account preferences
        self.segment_account_preferences = {
            'X': {  # VIP customers - Không dùng demand saving
                'min_accounts': 2,
                'max_accounts': 5,
                'term_saving_ratio': 0.9,  # 90% term_saving (không dùng demand)
                'demand_saving_ratio': 0.1,  # 10% demand_saving (rất ít)
                'term_months_distribution': {
                    12: 0.3,  # 30% 12 tháng
                    24: 0.3,  # 30% 24 tháng
                    36: 0.4   # 40% 36 tháng
                }
            },
            'Y': {  # MEDIUM customers - Mix term và demand
                'min_accounts': 1,
                'max_accounts': 3,
                'term_saving_ratio': 0.5,  # 50% term_saving
                'demand_saving_ratio': 0.5,  # 50% demand_saving
                'term_months_distribution': {
                    3: 0.2,   # 20% 3 tháng
                    6: 0.3,   # 30% 6 tháng
                    9: 0.2,   # 20% 9 tháng
                    12: 0.3   # 30% 12 tháng
                }
            },
            'Z': {  # LOW customers - Chủ yếu demand saving
                'min_accounts': 1,
                'max_accounts': 2,
                'term_saving_ratio': 0.2,  # 20% term_saving
                'demand_saving_ratio': 0.8,  # 80% demand_saving
                'term_months_distribution': {
                    1: 0.5,   # 50% 1 tháng
                    3: 0.5    # 50% 3 tháng
                }
            }
        }
        
        # Interest rate ranges by term months (dài hạn lãi cao, ngắn hạn lãi thấp)
        self.interest_rate_ranges = {
            0: (0.0001, 0.005),   # Demand: 0.01% - 0.5% (thấp nhất)
            1: (0.03, 0.04),      # 1 tháng: 3% - 4% (thấp)
            3: (0.03, 0.04),      # 3 tháng: 3% - 4% (thấp)
            6: (0.045, 0.055),    # 6 tháng: 4.5% - 5.5% (trung bình)
            9: (0.045, 0.055),    # 9 tháng: 4.5% - 5.5% (trung bình)
            12: (0.05, 0.06),     # 12 tháng: 5% - 6% (trung bình-cao)
            24: (0.06, 0.07),     # 24 tháng: 6% - 7% (cao)
            36: (0.065, 0.075)    # 36 tháng: 6.5% - 7.5% (cao nhất)
        }

    def generate_accounts_for_customers(self, customers: List[Dict], 
                                      start_date: datetime, end_date: datetime) -> List[NewAccount]:
        """Generate accounts for all customers based on their segments"""
        
        all_accounts = []
        
        for customer in customers:
            customer_code = customer['customer_code']
            segment = customer['customer_segment']
            
            # Generate accounts for this customer
            accounts = self._generate_accounts_for_customer(
                customer_code, segment, start_date, end_date
            )
            all_accounts.extend(accounts)
        
        return all_accounts

    def _generate_accounts_for_customer(self, customer_code: str, segment: str,
                                      start_date: datetime, end_date: datetime) -> List[NewAccount]:
        """Generate accounts for a specific customer based on segment"""
        
        preferences = self.segment_account_preferences[segment]
        accounts = []
        
        # Determine number of accounts for this customer
        num_accounts = random.randint(preferences['min_accounts'], preferences['max_accounts'])
        
        for i in range(num_accounts):
            # Generate account ID
            account_id = f"ACC_{customer_code}_{i+1:02d}"
            
            # Determine product type based on segment preferences
            if random.random() < preferences['term_saving_ratio']:
                product_type = 'term_saving'
                # Select term months based on segment distribution
                term_months = random.choices(
                    list(preferences['term_months_distribution'].keys()),
                    weights=list(preferences['term_months_distribution'].values()),
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
            
            # Generate interest rate based on term months
            min_rate, max_rate = self.interest_rate_ranges[term_months]
            interest_rate = round(random.uniform(min_rate, max_rate), 5)
            
            # Generate status
            status = random.choices(
                list(self.status_distribution.keys()),
                weights=list(self.status_distribution.values()),
                k=1
            )[0]
            
            # Generate channel
            channel_opened = random.choice(self.channels)
            
            # Generate currency
            currency = random.choices(
                list(self.currency_distribution.keys()),
                weights=list(self.currency_distribution.values()),
                k=1
            )[0]
            
            # Initial balance
            current_balance = 0.0
            
            account = NewAccount(
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

    def _generate_random_date(self, start_date: datetime, end_date: datetime) -> datetime:
        """Generate random date between start and end"""
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        random_date = start_date + timedelta(days=random_number_of_days)
        return random_date

    def update_account_balances(self, accounts: List[NewAccount], 
                              transactions: List[Dict]) -> List[NewAccount]:
        """Update account balances based on transactions"""
        
        # Group transactions by account
        account_transactions = {}
        for txn in transactions:
            account_id = txn['account_id']
            if account_id not in account_transactions:
                account_transactions[account_id] = []
            account_transactions[account_id].append(txn)
        
        # Update balances for each account
        for account in accounts:
            if account.account_id in account_transactions:
                # Sort transactions by date
                txns = sorted(account_transactions[account.account_id], 
                            key=lambda x: x['transaction_date'])
                
                # Calculate balance
                current_balance = 0.0
                for txn in txns:
                    if txn['transaction_type'] in ['Deposit', 'Fund Transfer']:
                        current_balance += txn['amount']
                    elif txn['transaction_type'] in ['Principal Withdrawal', 'Interest Withdrawal', 'Fee Transaction']:
                        current_balance -= txn['amount']
                
                account.current_balance = current_balance
        
        return accounts

def main():
    """Test New Account Generator"""
    generator = NewAccountGenerator()
    
    # Test data
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    # Sample customers
    customers = [
        {'customer_code': 'X_000001', 'customer_segment': 'X'},
        {'customer_code': 'Y_000001', 'customer_segment': 'Y'},
        {'customer_code': 'Z_000001', 'customer_segment': 'Z'},
    ]
    
    # Generate accounts
    accounts = generator.generate_accounts_for_customers(customers, start_date, end_date)
    
    print(f"✅ Generated {len(accounts)} accounts")
    
    # Analyze by segment
    segment_accounts = {}
    for account in accounts:
        segment = account.customer_code.split('_')[0]
        if segment not in segment_accounts:
            segment_accounts[segment] = []
        segment_accounts[segment].append(account)
    
    print(f"\n📊 Account Analysis by Segment:")
    for segment, accs in segment_accounts.items():
        if accs:
            print(f"\n   {segment} Segment ({len(accs)} accounts):")
            
            # Product type distribution
            product_types = [a.product_type for a in accs]
            product_counts = {}
            for p in product_types:
                product_counts[p] = product_counts.get(p, 0) + 1
            
            print(f"     Product Types:")
            for p_type, count in product_counts.items():
                percentage = (count / len(accs)) * 100
                print(f"       {p_type}: {count} ({percentage:.1f}%)")
            
            # Term months distribution
            term_months = [a.term_months for a in accs if a.term_months > 0]
            if term_months:
                term_counts = {}
                for t in term_months:
                    term_counts[t] = term_counts.get(t, 0) + 1
                
                print(f"     Term Months:")
                for term, count in term_counts.items():
                    percentage = (count / len(term_months)) * 100
                    print(f"       {term} months: {count} ({percentage:.1f}%)")
            
            # Interest rate analysis
            interest_rates = [a.interest_rate for a in accs]
            print(f"     Interest Rates:")
            print(f"       Min: {min(interest_rates):.3f}%")
            print(f"       Max: {max(interest_rates):.3f}%")
            print(f"       Mean: {sum(interest_rates)/len(interest_rates):.3f}%")
            
            # Currency distribution
            currencies = [a.currency for a in accs]
            currency_counts = {}
            for c in currencies:
                currency_counts[c] = currency_counts.get(c, 0) + 1
            
            print(f"     Currencies:")
            for currency, count in currency_counts.items():
                percentage = (count / len(accs)) * 100
                print(f"       {currency}: {count} ({percentage:.1f}%)")

if __name__ == "__main__":
    main()
