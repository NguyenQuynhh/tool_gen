"""
Phase 2 Account Generator
Account generator với tất cả constraints được sửa
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict
from dataclasses import dataclass
from test_config import test_config

@dataclass
class Phase2Account:
    """Phase 2 account model với tất cả constraints đúng"""
    account_id: str
    customer_code: str
    product_type: str  # demand_saving, term_saving
    open_date: datetime
    maturity_date: datetime
    term_months: int  # 0 for demand_saving, 1,3,6,9,12,24,36 for term_saving
    interest_rate: float  # Lãi suất/năm
    status: str  # active(80-85%), closed(10-15%), suspend(2-5%)
    channel_opened: str  # mobile/internet, atm, branch
    currency: str  # VND, USD, EUR
    current_balance: float

class Phase2AccountGenerator:
    """Phase 2 account generator với tất cả constraints đúng"""
    
    def __init__(self, config: test_config = None):
        self.config = config or test_config()
        
        # Product types
        self.product_types = ['demand_saving', 'term_saving']
        
        # Term months for term_saving
        self.term_months = [1, 3, 6, 9, 12, 24, 36]
        
        # Interest rates by term (corrected ranges)
        self.interest_rates = {
            0: (0.0001, 0.005),  # Demand: 0.01% - 0.5%
            1: (0.03, 0.04),     # 1 month: 3% - 4%
            3: (0.03, 0.04),     # 3 months: 3% - 4%
            6: (0.045, 0.055),   # 6 months: 4.5% - 5.5%
            9: (0.045, 0.055),   # 9 months: 4.5% - 5.5%
            12: (0.048, 0.06),   # 12 months: 4.8% - 6%
            24: (0.065, 0.07),   # 24 months: 6.5% - 7%
            36: (0.065, 0.07)    # 36 months: 6.5% - 7%
        }
        
        # Status distribution (corrected to match target)
        self.status_distribution = {
            'active': 0.825,   # 82.5% (within 80-85%)
            'closed': 0.125,   # 12.5% (within 10-15%)
            'suspend': 0.05    # 5% (within 2-5%)
        }
        
        # Channel distribution
        self.channels = ['mobile/internet', 'atm', 'branch']
        
        # Currency distribution
        self.currency_distribution = {
            'VND': 0.85,
            'USD': 0.10,
            'EUR': 0.05
        }
        
        # Segment-based account preferences
        self.segment_account_preferences = {
            'X': {  # VIP customers
                'min_accounts': 2,
                'max_accounts': 5,
                'term_saving_ratio': 0.7,  # 70% term_saving
                'demand_saving_ratio': 0.3  # 30% demand_saving
            },
            'Y': {  # MEDIUM customers
                'min_accounts': 1,
                'max_accounts': 3,
                'term_saving_ratio': 0.5,  # 50% term_saving
                'demand_saving_ratio': 0.5  # 50% demand_saving
            },
            'Z': {  # LOW customers
                'min_accounts': 1,
                'max_accounts': 2,
                'term_saving_ratio': 0.2,  # 20% term_saving
                'demand_saving_ratio': 0.8  # 80% demand_saving
            }
        }
    
    def generate_accounts_for_customer(self, 
                                     customer_code: str,
                                     segment: str,
                                     start_date: datetime,
                                     end_date: datetime) -> List[Phase2Account]:
        """Generate accounts for a customer based on segment"""
        
        accounts = []
        preferences = self.segment_account_preferences[segment]
        
        # Determine number of accounts
        num_accounts = random.randint(preferences['min_accounts'], preferences['max_accounts'])
        
        for i in range(num_accounts):
            # Generate account ID
            account_id = f"ACC_{customer_code}_{i+1:02d}"
            
            # Determine product type based on segment preferences
            if random.random() < preferences['term_saving_ratio']:
                product_type = 'term_saving'
                term_months = random.choice(self.term_months)
            else:
                product_type = 'demand_saving'
                term_months = 0
            
            # Generate open date
            open_date = self._generate_random_date(start_date, end_date)
            
            # Generate maturity date based on product type
            if product_type == 'demand_saving':
                maturity_date = None  # No maturity for demand saving
            else:
                maturity_date = open_date + timedelta(days=term_months * 30)
            
            # Generate interest rate based on term
            if term_months in self.interest_rates:
                min_rate, max_rate = self.interest_rates[term_months]
                interest_rate = round(random.uniform(min_rate, max_rate), 5)
            else:
                interest_rate = 0.03  # Default rate
            
            # Generate status based on distribution
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
            
            # Initial balance (will be updated by transactions)
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
    
    def _generate_random_date(self, start_date: datetime, end_date: datetime) -> datetime:
        """Generate random date between start and end"""
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        random_date = start_date + timedelta(days=random_number_of_days)
        return random_date
    
    def update_account_balance(self, account: Phase2Account, transactions: List[Dict]):
        """Update account balance based on transactions"""
        balance = 0.0
        
        for transaction in transactions:
            if transaction['transaction_type'] in ['Deposit', 'Fund Transfer']:
                balance += transaction['amount']
            elif transaction['transaction_type'] in ['Principal Withdrawal', 'Interest Withdrawal', 'Fee Transaction']:
                balance -= transaction['amount']
        
        account.current_balance = balance

def main():
    """Test Phase 2 Account Generator"""
    generator = Phase2AccountGenerator()
    
    # Test with different segments
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    print("🧪 Testing Phase 2 Account Generator")
    print("=" * 50)
    
    # Test X segment
    print("\n📊 X Segment (VIP) Accounts:")
    x_accounts = generator.generate_accounts_for_customer("X_TEST", "X", start_date, end_date)
    for acc in x_accounts:
        print(f"  {acc.account_id}: {acc.product_type} - {acc.term_months} months - {acc.interest_rate*100:.3f}% - {acc.status}")
    
    # Test Y segment
    print("\n📊 Y Segment (MEDIUM) Accounts:")
    y_accounts = generator.generate_accounts_for_customer("Y_TEST", "Y", start_date, end_date)
    for acc in y_accounts:
        print(f"  {acc.account_id}: {acc.product_type} - {acc.term_months} months - {acc.interest_rate*100:.3f}% - {acc.status}")
    
    # Test Z segment
    print("\n📊 Z Segment (LOW) Accounts:")
    z_accounts = generator.generate_accounts_for_customer("Z_TEST", "Z", start_date, end_date)
    for acc in z_accounts:
        print(f"  {acc.account_id}: {acc.product_type} - {acc.term_months} months - {acc.interest_rate*100:.3f}% - {acc.status}")

if __name__ == "__main__":
    main()
