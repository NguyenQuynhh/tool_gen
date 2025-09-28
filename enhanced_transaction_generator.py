"""
Enhanced Transaction Generator
Tạo transactions theo đúng yêu cầu constraint mới
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from dataclasses import dataclass
from test_config import test_config

@dataclass
class EnhancedTransaction:
    """Enhanced transaction model theo yêu cầu mới"""
    transaction_id: str
    account_id: str
    customer_code: str
    transaction_date: datetime
    transaction_type: str  # Interest Withdrawal, Principal Withdrawal, Deposit, Fund Transfer, Fee Transaction
    transaction_desc: str
    amount: float  # Số tiền giao dịch (>0)
    balance: float  # Số dư sau giao dịch
    channel_txn: str  # mobile/internet, atm, branch
    status_txn: str  # Pending(10%), Posted(85%), Declined(5%)
    tran_amt_acy: float  # Số tiền theo nguyên tệ
    tran_amt_lcy: float  # Số tiền quy đổi
    currency: str  # VND(85%), USD/EUR(15%)

class EnhancedTransactionGenerator:
    """Enhanced transaction generator theo constraint mới"""
    
    def __init__(self, config: test_config = None):
        self.config = config or test_config()
        
        # Transaction types theo yêu cầu
        self.transaction_types = [
            'Interest Withdrawal',
            'Principal Withdrawal', 
            'Deposit',
            'Fund Transfer',
            'Fee Transaction'
        ]
        
        # Channel distribution
        self.channels = ['mobile/internet', 'atm', 'branch']
        
        # Status distribution
        self.status_distribution = {
            'Pending': 0.10,
            'Posted': 0.85,
            'Declined': 0.05
        }
        
        # Currency distribution
        self.currency_distribution = {
            'VND': 0.85,
            'USD': 0.10,
            'EUR': 0.05
        }
        
        # Currency conversion rates
        self.currency_rates = {
            'VND': 1.0,
            'USD': 25.0,
            'EUR': 30.0
        }
        
        # RFM constraints
        self.rfm_constraints = {
            'X': {
                'frequency_per_month': (6, 8),
                'deposit_amount_min': 50_000_000,
                'recency_days_max': 30,
                'description': 'VIP - High frequency, high value, recent'
            },
            'Y': {
                'frequency_per_month': (3, 4),
                'deposit_amount_min': 30_000_000,
                'recency_days_max': 180,
                'description': 'MEDIUM - Medium frequency, medium value, moderate recency'
            },
            'Z': {
                'frequency_per_month': (2, 3),
                'deposit_amount_min': 5_000_000,
                'deposit_amount_max': 20_000_000,
                'recency_days_min': 180,
                'description': 'LOW - Low frequency, low value, old'
            }
        }
    
    def generate_transactions_for_customer(self, 
                                         customer_code: str,
                                         segment: str,
                                         accounts: List[Dict],
                                         start_date: datetime,
                                         end_date: datetime) -> List[EnhancedTransaction]:
        """Generate transactions cho một customer theo RFM constraints"""
        
        transactions = []
        
        # Get RFM requirements for segment
        rfm_req = self.rfm_constraints[segment]
        
        # Calculate total transactions needed
        duration_months = (end_date - start_date).days / 30.44
        freq_min, freq_max = rfm_req['frequency_per_month']
        total_transactions = int(random.uniform(freq_min, freq_max) * duration_months)
        
        # Ensure minimum transactions for RFM compliance
        min_transactions = max(10, int(freq_min * duration_months))
        total_transactions = max(total_transactions, min_transactions)
        
        # Generate transactions with proper RFM distribution
        deposit_count = 0
        withdrawal_count = 0
        
        # Ensure at least 1 transaction in recency period for X segment
        if segment == 'X':
            # For X segment, ensure recent transaction within last 30 days
            recent_date = end_date - timedelta(days=random.randint(1, 30))
            if recent_date < start_date:
                recent_date = start_date
            
            # Generate recent transaction
            account = random.choice(accounts)
            recent_transaction = self._generate_single_transaction(
                customer_code, account, recent_date, segment, rfm_req, is_recent=True, forced_type='Deposit'
            )
            transactions.append(recent_transaction)
            deposit_count += 1
            total_transactions -= 1
            
            # Add more recent transactions for X segment (ensure last transaction is recent)
            for _ in range(min(5, total_transactions // 3)):
                recent_date = end_date - timedelta(days=random.randint(1, 30))
                if recent_date < start_date:
                    recent_date = start_date
                
                account = random.choice(accounts)
                recent_transaction = self._generate_single_transaction(
                    customer_code, account, recent_date, segment, rfm_req, is_recent=True, forced_type='Deposit'
                )
                transactions.append(recent_transaction)
                deposit_count += 1
                total_transactions -= 1
                
        elif segment == 'Y':
            # For Y segment, ensure transaction within last 2-6 months
            recent_date = end_date - timedelta(days=random.randint(60, 180))
            if recent_date < start_date:
                recent_date = start_date
            
            # Generate recent transaction
            account = random.choice(accounts)
            recent_transaction = self._generate_single_transaction(
                customer_code, account, recent_date, segment, rfm_req, is_recent=True, forced_type='Deposit'
            )
            transactions.append(recent_transaction)
            deposit_count += 1
            total_transactions -= 1
            
            # Add more recent transactions for Y segment
            for _ in range(min(3, total_transactions // 4)):
                recent_date = end_date - timedelta(days=random.randint(60, 180))
                if recent_date < start_date:
                    recent_date = start_date
                
                account = random.choice(accounts)
                recent_transaction = self._generate_single_transaction(
                    customer_code, account, recent_date, segment, rfm_req, is_recent=True, forced_type='Deposit'
                )
                transactions.append(recent_transaction)
                deposit_count += 1
                total_transactions -= 1
        
        # Generate remaining transactions with proper distribution
        for i in range(total_transactions):
            # Select random account
            account = random.choice(accounts)
            
            # Generate date with strong bias towards end of period for better recency
            if segment == 'X':
                # X segment: 80% chance for recent transaction within last 30 days
                if random.random() < 0.8:
                    random_days = random.randint((end_date - start_date).days - 30, (end_date - start_date).days)
                else:
                    random_days = random.randint(0, (end_date - start_date).days)
            elif segment == 'Y':
                # Y segment: 60% chance for recent transaction within last 6 months
                if random.random() < 0.6:
                    random_days = random.randint((end_date - start_date).days - 180, (end_date - start_date).days)
                else:
                    random_days = random.randint(0, (end_date - start_date).days)
            else:
                # Z segment: spread throughout period, but avoid last 6 months
                if random.random() < 0.8 and (end_date - start_date).days > 180:
                    random_days = random.randint(0, (end_date - start_date).days - 180)
                else:
                    random_days = random.randint(0, (end_date - start_date).days)
            
            transaction_date = start_date + timedelta(days=random_days)
            
            # Determine transaction type based on current distribution
            if deposit_count < total_transactions * 0.7:  # 70% deposits for better RFM compliance
                transaction_type = 'Deposit'
                deposit_count += 1
            else:
                transaction_type = random.choice(['Principal Withdrawal', 'Interest Withdrawal'])
                withdrawal_count += 1
            
            # Generate transaction
            transaction = self._generate_single_transaction(
                customer_code, account, transaction_date, segment, rfm_req, forced_type=transaction_type
            )
            transactions.append(transaction)
        
        # Sort by date
        transactions.sort(key=lambda x: x.transaction_date)
        
        # Ensure last transaction is recent for X and Y segments
        if segment == 'X':
            # Ensure last transaction is within last 30 days
            last_transaction = transactions[-1]
            if (end_date - last_transaction.transaction_date).days > 30:
                # Replace last transaction with recent one
                recent_date = end_date - timedelta(days=random.randint(1, 30))
                if recent_date < start_date:
                    recent_date = start_date
                
                account = random.choice(accounts)
                recent_transaction = self._generate_single_transaction(
                    customer_code, account, recent_date, segment, rfm_req, is_recent=True, forced_type='Deposit'
                )
                transactions[-1] = recent_transaction
        elif segment == 'Y':
            # Ensure last transaction is within last 6 months
            last_transaction = transactions[-1]
            if (end_date - last_transaction.transaction_date).days > 180:
                # Replace last transaction with recent one
                recent_date = end_date - timedelta(days=random.randint(60, 180))
                if recent_date < start_date:
                    recent_date = start_date
                
                account = random.choice(accounts)
                recent_transaction = self._generate_single_transaction(
                    customer_code, account, recent_date, segment, rfm_req, is_recent=True, forced_type='Deposit'
                )
                transactions[-1] = recent_transaction
        
        # Re-sort by date
        transactions.sort(key=lambda x: x.transaction_date)
        
        # Calculate balances
        self._calculate_balances(transactions)
        
        return transactions
    
    def _generate_single_transaction(self, 
                                   customer_code: str,
                                   account: Dict,
                                   transaction_date: datetime,
                                   segment: str,
                                   rfm_req: Dict,
                                   is_recent: bool = False,
                                   forced_type: str = None) -> EnhancedTransaction:
        """Generate single transaction theo logic"""
        
        # Determine transaction type based on date and account
        if forced_type:
            transaction_type = forced_type
        else:
            transaction_type = self._determine_transaction_type(
                transaction_date, account, segment, is_recent
            )
        
        # Determine amount based on segment and transaction type
        amount = self._determine_amount(transaction_type, segment, rfm_req)
        
        # Determine currency
        currency = self._determine_currency()
        
        # Calculate amounts
        tran_amt_acy = amount
        tran_amt_lcy = amount * self.currency_rates[currency]
        
        # Generate transaction
        transaction = EnhancedTransaction(
            transaction_id=f"TXN_{random.randint(100000, 999999)}",
            account_id=account['account_id'],
            customer_code=customer_code,
            transaction_date=transaction_date,
            transaction_type=transaction_type,
            transaction_desc=self._generate_transaction_desc(transaction_type),
            amount=amount,
            balance=0,  # Will be calculated later
            channel_txn=random.choice(self.channels),
            status_txn=self._determine_status(),
            tran_amt_acy=tran_amt_acy,
            tran_amt_lcy=tran_amt_lcy,
            currency=currency
        )
        
        return transaction
    
    def _determine_transaction_type(self, 
                                  transaction_date: datetime,
                                  account: Dict,
                                  segment: str,
                                  is_recent: bool = False) -> str:
        """Determine transaction type based on date and account logic"""
        
        open_date = account['open_date']
        maturity_date = account['maturity_date']
        product_type = account['product_type']
        
        # Calculate days from open and to maturity
        days_from_open = (transaction_date - open_date).days
        days_to_maturity = (maturity_date - transaction_date).days
        total_days = (maturity_date - open_date).days
        
        # Logic: gần open_date → Deposit, gần maturity_date → Withdrawal
        if days_from_open < total_days * 0.2:  # First 20% of period
            # Near open_date - usually Deposit or Fund Transfer
            if random.random() < 0.8:
                return 'Deposit'
            else:
                return 'Fund Transfer'
        
        elif days_to_maturity < total_days * 0.2:  # Last 20% of period
            # Near maturity_date - usually Withdrawal
            if product_type == 'term_saving':
                # Term saving: Principal Withdrawal only after maturity
                if days_to_maturity <= 0:
                    return random.choice(['Principal Withdrawal', 'Interest Withdrawal'])
                else:
                    return 'Interest Withdrawal'
            else:
                # Demand saving: can withdraw anytime
                return random.choice(['Principal Withdrawal', 'Interest Withdrawal'])
        
        else:
            # Middle period - mixed transactions
            if product_type == 'term_saving':
                # Term saving: mostly Interest Withdrawal, some Deposit
                if random.random() < 0.7:
                    return 'Interest Withdrawal'
                else:
                    return 'Deposit'
            else:
                # Demand saving: mixed
                return random.choice(['Deposit', 'Fund Transfer', 'Interest Withdrawal'])
    
    def _determine_amount(self, 
                         transaction_type: str,
                         segment: str,
                         rfm_req: Dict) -> float:
        """Determine transaction amount based on type and segment"""
        
        if transaction_type in ['Deposit', 'Fund Transfer']:
            # Deposit amounts based on segment
            if segment == 'X':
                return random.randint(50_000_000, 200_000_000)
            elif segment == 'Y':
                return random.randint(30_000_000, 100_000_000)
            else:  # Z
                return random.randint(5_000_000, 20_000_000)
        
        elif transaction_type in ['Principal Withdrawal', 'Interest Withdrawal']:
            # Withdrawal amounts (usually smaller than deposits)
            if segment == 'X':
                return random.randint(20_000_000, 100_000_000)
            elif segment == 'Y':
                return random.randint(15_000_000, 50_000_000)
            else:  # Z
                return random.randint(2_000_000, 10_000_000)
        
        else:  # Fee Transaction
            # Fee amounts (small)
            return random.randint(50_000, 500_000)
    
    def _determine_currency(self) -> str:
        """Determine currency based on distribution"""
        rand = random.random()
        if rand < self.currency_distribution['VND']:
            return 'VND'
        elif rand < self.currency_distribution['VND'] + self.currency_distribution['USD']:
            return 'USD'
        else:
            return 'EUR'
    
    def _determine_status(self) -> str:
        """Determine transaction status based on distribution"""
        rand = random.random()
        if rand < self.status_distribution['Pending']:
            return 'Pending'
        elif rand < self.status_distribution['Pending'] + self.status_distribution['Posted']:
            return 'Posted'
        else:
            return 'Declined'
    
    def _generate_transaction_desc(self, transaction_type: str) -> str:
        """Generate transaction description based on type"""
        descriptions = {
            'Interest Withdrawal': 'Rút lãi tiết kiệm',
            'Principal Withdrawal': 'Rút gốc tiết kiệm',
            'Deposit': 'Gửi tiền tiết kiệm',
            'Fund Transfer': 'Chuyển tiền từ tài khoản thanh toán',
            'Fee Transaction': 'Thu phí dịch vụ ngân hàng'
        }
        return descriptions.get(transaction_type, 'Giao dịch tiết kiệm')
    
    def _calculate_balances(self, transactions: List[EnhancedTransaction]):
        """Calculate running balances for transactions"""
        current_balance = 0
        
        for transaction in transactions:
            transaction.balance = current_balance
            
            if transaction.transaction_type in ['Deposit', 'Fund Transfer']:
                current_balance += transaction.amount
            elif transaction.transaction_type in ['Principal Withdrawal', 'Interest Withdrawal']:
                current_balance -= transaction.amount
            elif transaction.transaction_type == 'Fee Transaction':
                current_balance -= transaction.amount
            
            transaction.balance = current_balance

def main():
    """Test enhanced transaction generator"""
    generator = EnhancedTransactionGenerator()
    
    # Test data
    test_accounts = [
        {
            'account_id': 'ACC_TEST_001',
            'open_date': datetime(2023, 1, 1),
            'maturity_date': datetime(2023, 12, 31),
            'product_type': 'term_saving'
        }
    ]
    
    # Generate transactions
    transactions = generator.generate_transactions_for_customer(
        customer_code='TEST_001',
        segment='X',
        accounts=test_accounts,
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2023, 12, 31)
    )
    
    print(f"Generated {len(transactions)} transactions")
    for i, txn in enumerate(transactions[:5]):  # Show first 5
        print(f"{i+1}. {txn.transaction_type} - {txn.amount:,.0f} {txn.currency} - {txn.transaction_date.strftime('%Y-%m-%d')}")

if __name__ == "__main__":
    main()
