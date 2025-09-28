"""
New Transaction Generator với hành vi khách hàng theo phân khúc mới
X(50%) - Tiêu nhiều tiền, ưa deposits
Y(30%) - Cân bằng deposits/withdrawals  
Z(20%) - Tiêu ít tiền, nhiều withdrawals
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict
from dataclasses import dataclass

from test_config import test_config

@dataclass
class NewTransaction:
    """New Transaction data structure"""
    transaction_id: str
    account_id: str
    customer_code: str
    transaction_date: datetime
    transaction_type: str
    transaction_desc: str
    amount: int
    balance: int
    channel_txn: str
    status_txn: str
    tran_amt_acy: int
    tran_amt_lcy: int
    currency: str

class NewTransactionGenerator:
    """New Transaction Generator với hành vi khách hàng theo phân khúc"""
    
    def __init__(self, config: test_config = None):
        self.config = config or test_config()
        
        # Transaction types
        self.transaction_types = [
            'Deposit', 'Principal Withdrawal', 'Interest Withdrawal', 
            'Fund Transfer', 'Fee Transaction'
        ]
        
        # Channels
        self.channels = ['mobile/internet', 'atm', 'branch']
        
        # Status distribution
        self.status_distribution = {
            'Posted': 0.85,
            'Pending': 0.10,
            'Declined': 0.05
        }
        
        # Currency distribution
        self.currency_distribution = {
            'VND': 0.85,
            'USD': 0.10,
            'EUR': 0.05
        }
        
        # RFM requirements by segment với hành vi mới
        self.rfm_requirements = {
            'X': {
                'frequency_per_month': (6, 8),
                'amount_min': 50_000_000,  # 50M VND minimum
                'amount_max': 200_000_000, # 200M VND maximum
                'recency_days': 30,
                'deposit_ratio': 0.8,      # 80% deposits (tiêu nhiều tiền)
                'withdrawal_ratio': 0.2    # 20% withdrawals
            },
            'Y': {
                'frequency_per_month': (3, 4),
                'amount_min': 30_000_000,  # 30M VND minimum
                'amount_max': 100_000_000, # 100M VND maximum
                'recency_days': 180,
                'deposit_ratio': 0.5,      # 50% deposits (cân bằng)
                'withdrawal_ratio': 0.5    # 50% withdrawals
            },
            'Z': {
                'frequency_per_month': (2, 3),
                'amount_min': 5_000_000,   # 5M VND minimum
                'amount_max': 20_000_000,  # 20M VND maximum
                'recency_days': 365,
                'deposit_ratio': 0.2,      # 20% deposits (tiêu ít tiền)
                'withdrawal_ratio': 0.8    # 80% withdrawals
            }
        }

    def generate_transactions_for_customer(self, customer_code: str, segment: str, 
                                         accounts: List[Dict], start_date: datetime, 
                                         end_date: datetime) -> List[NewTransaction]:
        """Generate transactions for customer based on segment behavior"""
        
        transactions = []
        req = self.rfm_requirements[segment]
        
        # Calculate total transactions needed based on frequency
        months = (end_date - start_date).days // 30
        min_transactions = req['frequency_per_month'][0] * months
        max_transactions = req['frequency_per_month'][1] * months
        total_transactions = random.randint(min_transactions, max_transactions)
        
        print(f"   Generating {total_transactions} transactions for {customer_code} ({segment})")
        
        # Generate transactions with segment-specific behavior
        for i in range(total_transactions):
            # Select random account
            account = random.choice(accounts)
            account_id = account['account_id']
            
            # Generate transaction date with recency bias
            transaction_date = self._generate_transaction_date(start_date, end_date, segment, req)
            
            # Generate transaction type based on segment behavior
            transaction_type = self._generate_transaction_type_by_segment(segment, req)
            
            # Generate amount based on segment
            amount = self._generate_amount_by_segment(segment, transaction_type, req)
            
            # Generate other transaction details
            currency = random.choices(
                list(self.currency_distribution.keys()),
                weights=list(self.currency_distribution.values()),
                k=1
            )[0]
            
            tran_amt_lcy = amount * {'VND': 1, 'USD': 25, 'EUR': 30}.get(currency, 1)
            
            status = random.choices(
                list(self.status_distribution.keys()),
                weights=list(self.status_distribution.values()),
                k=1
            )[0]
            
            channel = random.choice(self.channels)
            
            transaction = NewTransaction(
                transaction_id=f"TXN_{random.randint(100000, 999999)}",
                account_id=account_id,
                customer_code=customer_code,
                transaction_date=transaction_date,
                transaction_type=transaction_type,
                transaction_desc=f"{transaction_type} transaction for {customer_code}",
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

    def _generate_transaction_date(self, start_date: datetime, end_date: datetime, 
                                 segment: str, req: Dict) -> datetime:
        """Generate transaction date with segment-specific recency bias"""
        
        if segment == 'X':
            # X: 80% recent transactions (tiêu nhiều tiền, hoạt động thường xuyên)
            if random.random() < 0.8:
                # Recent transactions within recency_days
                random_days = random.randint(
                    (end_date - start_date).days - req['recency_days'],
                    (end_date - start_date).days
                )
            else:
                # Some older transactions
                random_days = random.randint(0, (end_date - start_date).days)
                
        elif segment == 'Y':
            # Y: 60% recent transactions (cân bằng)
            if random.random() < 0.6:
                # Recent transactions within recency_days
                random_days = random.randint(
                    (end_date - start_date).days - req['recency_days'],
                    (end_date - start_date).days
                )
            else:
                # Some older transactions
                random_days = random.randint(0, (end_date - start_date).days)
                
        else:  # Z
            # Z: 20% recent transactions (tiêu ít tiền, ít hoạt động)
            if random.random() < 0.2:
                # Recent transactions within recency_days
                random_days = random.randint(
                    (end_date - start_date).days - req['recency_days'],
                    (end_date - start_date).days
                )
            else:
                # Mostly older transactions
                random_days = random.randint(0, (end_date - start_date).days)
        
        return start_date + timedelta(days=random_days)

    def _generate_transaction_type_by_segment(self, segment: str, req: Dict) -> str:
        """Generate transaction type based on segment behavior"""
        
        if segment == 'X':
            # X: 80% deposits (tiêu nhiều tiền, ưa deposits)
            if random.random() < req['deposit_ratio']:
                return random.choice(['Deposit', 'Fund Transfer'])
            else:
                return random.choice(['Principal Withdrawal', 'Interest Withdrawal', 'Fee Transaction'])
                
        elif segment == 'Y':
            # Y: 50% deposits, 50% withdrawals (cân bằng)
            if random.random() < req['deposit_ratio']:
                return random.choice(['Deposit', 'Fund Transfer'])
            else:
                return random.choice(['Principal Withdrawal', 'Interest Withdrawal', 'Fee Transaction'])
                
        else:  # Z
            # Z: 20% deposits, 80% withdrawals (tiêu ít tiền, nhiều withdrawals)
            if random.random() < req['deposit_ratio']:
                return random.choice(['Deposit', 'Fund Transfer'])
            else:
                return random.choice(['Principal Withdrawal', 'Interest Withdrawal', 'Fee Transaction'])

    def _generate_amount_by_segment(self, segment: str, transaction_type: str, req: Dict) -> int:
        """Generate amount based on segment and transaction type"""
        
        if transaction_type in ['Deposit', 'Fund Transfer']:
            # Deposits: use full range
            return random.randint(req['amount_min'], req['amount_max'])
        else:
            # Withdrawals: smaller amounts but still within segment range
            withdrawal_max = min(req['amount_max'] // 2, req['amount_max'])
            withdrawal_min = max(req['amount_min'] // 2, 5_000_000)  # At least 5M
            return random.randint(withdrawal_min, withdrawal_max)

    def generate_transactions_for_accounts(self, customer_accounts: List[Dict], 
                                         start_date: datetime, end_date: datetime) -> List[NewTransaction]:
        """Generate transactions for all customer accounts"""
        
        all_transactions = []
        
        # Group accounts by customer
        customer_accounts_map = {}
        for account in customer_accounts:
            customer_code = account['customer_code']
            if customer_code not in customer_accounts_map:
                customer_accounts_map[customer_code] = []
            customer_accounts_map[customer_code].append(account)
        
        # Generate transactions for each customer
        for customer_code, accounts in customer_accounts_map.items():
            # Determine segment from customer_code
            segment = customer_code.split('_')[0]
            
            # Generate transactions for this customer
            transactions = self.generate_transactions_for_customer(
                customer_code, segment, accounts, start_date, end_date
            )
            all_transactions.extend(transactions)
        
        return all_transactions

def main():
    """Test New Transaction Generator"""
    generator = NewTransactionGenerator()
    
    # Test data
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    # Sample customer accounts
    customer_accounts = [
        {'account_id': 'ACC_X_000001_01', 'customer_code': 'X_000001'},
        {'account_id': 'ACC_X_000001_02', 'customer_code': 'X_000001'},
        {'account_id': 'ACC_Y_000001_01', 'customer_code': 'Y_000001'},
        {'account_id': 'ACC_Z_000001_01', 'customer_code': 'Z_000001'},
    ]
    
    # Generate transactions
    transactions = generator.generate_transactions_for_accounts(
        customer_accounts, start_date, end_date
    )
    
    print(f"✅ Generated {len(transactions)} transactions")
    
    # Analyze by segment
    segment_transactions = {}
    for txn in transactions:
        segment = txn.customer_code.split('_')[0]
        if segment not in segment_transactions:
            segment_transactions[segment] = []
        segment_transactions[segment].append(txn)
    
    print(f"\n📊 Transaction Analysis by Segment:")
    for segment, txns in segment_transactions.items():
        if txns:
            amounts = [t.amount for t in txns]
            types = [t.transaction_type for t in txns]
            
            print(f"\n   {segment} Segment ({len(txns)} transactions):")
            print(f"     Amount: Min={min(amounts):,}, Max={max(amounts):,}, Mean={sum(amounts)/len(amounts):,.0f}")
            
            # Transaction type distribution
            type_counts = {}
            for t in types:
                type_counts[t] = type_counts.get(t, 0) + 1
            
            print(f"     Types:")
            for t_type, count in type_counts.items():
                percentage = (count / len(txns)) * 100
                print(f"       {t_type}: {count} ({percentage:.1f}%)")

if __name__ == "__main__":
    main()
