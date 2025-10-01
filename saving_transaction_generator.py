"""
New Transaction Generator với hành vi khách hàng theo phân khúc mới
X(50%) - Tiêu nhiều tiền, ưa deposits
Y(30%) - Cân bằng deposits/withdrawals  
Z(20%) - Tiêu ít tiền, nhiều withdrawals
"""

import random
import csv
import os
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
    term_month: int = 0  # Kỳ hạn tiết kiệm (tháng)
    maturity_date: datetime = None  # Ngày đáo hạn
    open_date: datetime = None  # Ngày mở tài khoản
    account_type: str = "term_saving"  # term_saving hoặc demand_saving

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
        
        # RFM requirements by segment theo yêu cầu mới
        self.rfm_requirements = {
            'A': {  # Champions/VIPs
                'frequency_per_month': (6, 8),
                'deposit_amount_min': 50_000_000,  # 50M VND minimum
                'deposit_amount_max': 200_000_000, # 200M VND maximum
                'withdrawal_amount_min': 10_000_000,  # 10M VND minimum
                'withdrawal_amount_max': 50_000_000,  # 50M VND maximum
                'recency_days': 30,
                'deposit_ratio': 0.7,      # 70% deposits
                'withdrawal_ratio': 0.3,   # 30% withdrawals
                'term_month_range': (6, 12),  # Kỳ hạn dài 6-12 tháng
                'balance_range': (100_000_000, 500_000_000),  # Số dư cao
                'account_count_range': (3, 5)  # Nhiều sổ tiết kiệm
            },
            'B': {  # Potential Loyalists
                'frequency_per_month': (0, 1),
                'deposit_amount_min': 5_000_000,   # 5M VND minimum
                'deposit_amount_max': 10_000_000,  # 10M VND maximum
                'withdrawal_amount_min': 2_000_000,  # 2M VND minimum
                'withdrawal_amount_max': 8_000_000,  # 8M VND maximum
                'recency_days': 90,
                'deposit_ratio': 0.6,      # 60% deposits
                'withdrawal_ratio': 0.4,   # 40% withdrawals
                'term_month_range': (1, 3),    # Kỳ hạn ngắn 1-3 tháng
                'balance_range': (40_000_000, 60_000_000),  # Số dư trung bình 50tr
                'account_count_range': (1, 2)  # 1-2 account
            },
            'C': {  # At-Risk High Value
                'frequency_per_month': (3, 4),
                'deposit_amount_min': 20_000_000,  # 20M VND minimum
                'deposit_amount_max': 80_000_000,  # 80M VND maximum
                'withdrawal_amount_min': 15_000_000,  # 15M VND minimum
                'withdrawal_amount_max': 60_000_000,  # 60M VND maximum
                'recency_days': 90,
                'deposit_ratio': 0.3,      # 30% deposits (ít deposits)
                'withdrawal_ratio': 0.7,   # 70% withdrawals (nhiều withdrawals)
                'term_month_range': (1, 3),    # Chuyển sang demand_saving (kỳ hạn ngắn)
                'balance_range': (30_000_000, 80_000_000),  # Số dư giảm
                'account_count_range': (1, 2),  # Ít account hơn
                'early_withdrawal_ratio': 0.6  # 60% rút trước hạn
            },
            'D': {  # Stable Savers
                'frequency_per_month': (1, 2),
                'deposit_amount_min': 10_000_000,  # 10M VND minimum
                'deposit_amount_max': 50_000_000,  # 50M VND maximum
                'withdrawal_amount_min': 5_000_000,   # 5M VND minimum
                'withdrawal_amount_max': 30_000_000,  # 30M VND maximum
                'recency_days': 30,
                'deposit_ratio': 0.6,      # 60% deposits
                'withdrawal_ratio': 0.4,   # 40% withdrawals
                'term_month_range': (6, 6),    # Kỳ hạn trung bình 6 tháng
                'balance_range': (50_000_000, 100_000_000),  # Số dư 50-100tr
                'account_count_range': (2, 3)  # 2-3 account
            },
            'E': {  # New/Occasional Users
                'frequency_per_month': (0, 1),
                'deposit_amount_min': 5_000_000,   # 5M VND minimum
                'deposit_amount_max': 10_000_000,  # 10M VND maximum
                'withdrawal_amount_min': 2_000_000,  # 2M VND minimum
                'withdrawal_amount_max': 8_000_000,  # 8M VND maximum
                'recency_days': 90,  # 2-3 tháng
                'deposit_ratio': 0.7,      # 70% deposits
                'withdrawal_ratio': 0.3,   # 30% withdrawals
                'term_month_range': (1, 3),    # Kỳ hạn ngắn 1-3 tháng
                'balance_range': (30_000_000, 60_000_000),  # Số dư trung bình 50tr
                'account_count_range': (1, 1),  # 1 account
                'demand_saving_ratio': 0.8  # 80% demand_saving
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
            
            # Generate amount based on segment and transaction type
            amount = self._generate_amount_by_segment_and_type(segment, transaction_type, req)
            
            # Use account details from loaded data
            term_month = account.get('term_months', 0)
            maturity_date = account.get('maturity_date')
            open_date = account.get('open_date')
            account_type = account.get('product_type', 'term_saving')
            
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
            
            # Use balance from account data with some variation
            base_balance = account.get('current_balance', 0)
            # Add some variation to balance (±20%)
            variation = random.uniform(0.8, 1.2)
            balance = int(base_balance * variation)
            
            transaction = NewTransaction(
                transaction_id=f"TXN_{random.randint(100000, 999999)}",
                account_id=account_id,
                customer_code=customer_code,
                transaction_date=transaction_date,
                transaction_type=transaction_type,
                transaction_desc=f"{transaction_type} transaction for {customer_code}",
                amount=amount,
                balance=balance,
                channel_txn=channel,
                status_txn=status,
                tran_amt_acy=amount,
                tran_amt_lcy=tran_amt_lcy,
                currency=currency,
                term_month=term_month,
                maturity_date=maturity_date,
                open_date=open_date,
                account_type=account_type
            )
            
            transactions.append(transaction)
        
        # Sort by date
        transactions.sort(key=lambda x: x.transaction_date)
        
        return transactions

    def _generate_transaction_date(self, start_date: datetime, end_date: datetime, 
                                 segment: str, req: Dict) -> datetime:
        """Generate transaction date with segment-specific recency bias"""
        
        if segment == 'A':
            # A: 80% recent transactions (Champions/VIPs hoạt động thường xuyên)
            if random.random() < 0.8:
                # Recent transactions within recency_days
                random_days = random.randint(
                    (end_date - start_date).days - req['recency_days'],
                    (end_date - start_date).days
                )
            else:
                # Some older transactions
                random_days = random.randint(0, (end_date - start_date).days)
                
        elif segment == 'B':
            # B: 40% recent transactions (Potential Loyalists ít hoạt động)
            if random.random() < 0.4:
                # Recent transactions within recency_days
                random_days = random.randint(
                    (end_date - start_date).days - req['recency_days'],
                    (end_date - start_date).days
                )
            else:
                # Mostly older transactions
                random_days = random.randint(0, (end_date - start_date).days)
                
        elif segment == 'C':
            # C: 60% recent transactions (At-Risk High Value)
            if random.random() < 0.6:
                # Recent transactions within recency_days
                random_days = random.randint(
                    (end_date - start_date).days - req['recency_days'],
                    (end_date - start_date).days
                )
            else:
                # Some older transactions
                random_days = random.randint(0, (end_date - start_date).days)
                
        elif segment == 'D':
            # D: 70% recent transactions (Stable Savers)
            if random.random() < 0.7:
                # Recent transactions within recency_days
                random_days = random.randint(
                    (end_date - start_date).days - req['recency_days'],
                    (end_date - start_date).days
                )
            else:
                # Some older transactions
                random_days = random.randint(0, (end_date - start_date).days)
                
        else:  # E
            # E: 30% recent transactions (New/Occasional Users)
            if random.random() < 0.3:
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
        
        if segment == 'A':
            # A: 70% deposits (Champions/VIPs ưa deposits)
            if random.random() < req['deposit_ratio']:
                return random.choice(['Deposit', 'Fund Transfer'])
            else:
                return random.choice(['Principal Withdrawal', 'Interest Withdrawal', 'Fee Transaction'])
                
        elif segment == 'B':
            # B: 60% deposits, 40% withdrawals (Potential Loyalists)
            if random.random() < req['deposit_ratio']:
                return random.choice(['Deposit', 'Fund Transfer'])
            else:
                return random.choice(['Principal Withdrawal', 'Interest Withdrawal', 'Fee Transaction'])
                
        elif segment == 'C':
            # C: 30% deposits, 70% withdrawals (At-Risk High Value - nhiều withdrawals)
            if random.random() < req['deposit_ratio']:
                return random.choice(['Deposit', 'Fund Transfer'])
            else:
                return random.choice(['Principal Withdrawal', 'Interest Withdrawal', 'Fee Transaction'])
                
        elif segment == 'D':
            # D: 60% deposits, 40% withdrawals (Stable Savers)
            if random.random() < req['deposit_ratio']:
                return random.choice(['Deposit', 'Fund Transfer'])
            else:
                return random.choice(['Principal Withdrawal', 'Interest Withdrawal', 'Fee Transaction'])
                
        else:  # E
            # E: 70% deposits, 30% withdrawals (New/Occasional Users)
            if random.random() < req['deposit_ratio']:
                return random.choice(['Deposit', 'Fund Transfer'])
            else:
                return random.choice(['Principal Withdrawal', 'Interest Withdrawal', 'Fee Transaction'])

    def _generate_amount_by_segment_and_type(self, segment: str, transaction_type: str, req: Dict) -> int:
        """Generate amount based on segment and transaction type"""
        
        if transaction_type in ['Deposit', 'Fund Transfer']:
            # Deposits: use deposit range
            return random.randint(req['deposit_amount_min'], req['deposit_amount_max'])
        else:
            # Withdrawals: use withdrawal range
            return random.randint(req['withdrawal_amount_min'], req['withdrawal_amount_max'])
    
    def _generate_account_details(self, segment: str, transaction_date: datetime, req: Dict) -> tuple:
        """Generate account details (term_month, maturity_date, open_date, account_type)"""
        
        # Generate term_month based on segment
        term_month = random.randint(req['term_month_range'][0], req['term_month_range'][1])
        
        # Generate open_date (account opening date)
        if segment == 'B' or segment == 'E':
            # B, E: Open_date gần đây (trong 6 tháng)
            open_date = transaction_date - timedelta(days=random.randint(30, 180))
        else:
            # A, C, D: Open_date có thể xa hơn
            open_date = transaction_date - timedelta(days=random.randint(30, 365))
        
        # Generate account_type
        if segment == 'E' and 'demand_saving_ratio' in req:
            # E: 80% demand_saving
            account_type = 'demand_saving' if random.random() < req['demand_saving_ratio'] else 'term_saving'
        elif segment == 'C':
            # C: Chuyển sang demand_saving (3 tháng gần đây)
            if random.random() < 0.7:  # 70% demand_saving
                account_type = 'demand_saving'
                term_month = 0  # Demand saving không có kỳ hạn
            else:
                account_type = 'term_saving'
        else:
            # A, B, D: Chủ yếu term_saving
            account_type = 'term_saving' if random.random() < 0.8 else 'demand_saving'
            if account_type == 'demand_saving':
                term_month = 0
        
        # Generate maturity_date
        if account_type == 'term_saving' and term_month > 0:
            maturity_date = open_date + timedelta(days=term_month * 30)
        else:
            maturity_date = None
        
        return term_month, maturity_date, open_date, account_type
    
    def _generate_balance_by_segment(self, segment: str, req: Dict) -> int:
        """Generate balance based on segment"""
        return random.randint(req['balance_range'][0], req['balance_range'][1])
    
    def load_accounts_from_csv(self, csv_file_path: str) -> List[Dict]:
        """Load accounts data from CSV file"""
        accounts = []
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Convert string dates to datetime objects
                    open_date = datetime.strptime(row['open_date'], '%Y-%m-%d')
                    maturity_date = datetime.strptime(row['maturity_date'], '%Y-%m-%d') if row['maturity_date'] else None
                    
                    account = {
                        'account_id': row['account_id'],
                        'customer_code': row['customer_code'],
                        'product_type': row['product_type'],
                        'open_date': open_date,
                        'maturity_date': maturity_date,
                        'term_months': int(row['term_months']),
                        'interest_rate': float(row['interest_rate']),
                        'status': row['status'],
                        'channel_opened': row['channel_opened'],
                        'currency': row['currency'],
                        'current_balance': float(row['current_balance'])
                    }
                    accounts.append(account)
            
            print(f"[INFO] Loaded {len(accounts)} accounts from {csv_file_path}")
            return accounts
            
        except FileNotFoundError:
            print(f"[ERROR] File not found: {csv_file_path}")
            return []
        except Exception as e:
            print(f"[ERROR] Error loading accounts: {e}")
            return []
    
    def save_transactions_to_csv(self, transactions: List[NewTransaction], output_file_path: str):
        """Save transactions to CSV file"""
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
            
            with open(output_file_path, 'w', newline='', encoding='utf-8') as file:
                fieldnames = [
                    'transaction_id', 'account_id', 'customer_code', 'transaction_date',
                    'transaction_type', 'transaction_desc', 'amount', 'balance',
                    'channel_txn', 'status_txn', 'tran_amt_acy', 'tran_amt_lcy',
                    'currency', 'term_month', 'maturity_date', 'open_date', 'account_type'
                ]
                
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                
                for txn in transactions:
                    writer.writerow({
                        'transaction_id': txn.transaction_id,
                        'account_id': txn.account_id,
                        'customer_code': txn.customer_code,
                        'transaction_date': txn.transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'transaction_type': txn.transaction_type,
                        'transaction_desc': txn.transaction_desc,
                        'amount': txn.amount,
                        'balance': txn.balance,
                        'channel_txn': txn.channel_txn,
                        'status_txn': txn.status_txn,
                        'tran_amt_acy': txn.tran_amt_acy,
                        'tran_amt_lcy': txn.tran_amt_lcy,
                        'currency': txn.currency,
                        'term_month': txn.term_month,
                        'maturity_date': txn.maturity_date.strftime('%Y-%m-%d') if txn.maturity_date else '',
                        'open_date': txn.open_date.strftime('%Y-%m-%d') if txn.open_date else '',
                        'account_type': txn.account_type
                    })
            
            print(f"[SUCCESS] Saved {len(transactions)} transactions to {output_file_path}")
            
        except Exception as e:
            print(f"[ERROR] Error saving transactions: {e}")

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
            # Determine segment from customer_code (A, B, C, D, E)
            segment = customer_code.split('_')[0]
            
            # Skip if segment not in our requirements
            if segment not in self.rfm_requirements:
                print(f"   Skipping unknown segment: {segment} for customer {customer_code}")
                continue
            
            # Generate transactions for this customer
            transactions = self.generate_transactions_for_customer(
                customer_code, segment, accounts, start_date, end_date
            )
            all_transactions.extend(transactions)
        
        return all_transactions

def main():
    """Generate transactions using real account data and save to CSV"""
    generator = NewTransactionGenerator()
    
    # Date range for transaction generation
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    # Load real account data from CSV
    accounts_file_path = "output/banking_data_accounts.csv"
    print(f"[INFO] Loading accounts from {accounts_file_path}")
    all_accounts = generator.load_accounts_from_csv(accounts_file_path)
    
    if not all_accounts:
        print("[ERROR] No accounts loaded. Exiting.")
        return
    
    # Filter accounts by customer segment (A, B, C, D, E)
    # Map X->A, Y->B, Z->C, W->D, V->E based on the actual data structure
    segment_mapping = {
        'X': 'A',  # Champions/VIPs
        'Y': 'B',  # Potential Loyalists  
        'Z': 'C',  # At-Risk High Value
        'W': 'D',  # Stable Savers
        'V': 'E'   # New/Occasional Users
    }
    
    # Filter and map accounts
    filtered_accounts = []
    for account in all_accounts:
        customer_code = account['customer_code']
        original_segment = customer_code.split('_')[0]
        
        if original_segment in segment_mapping:
            # Update customer_code to match our segment requirements
            new_segment = segment_mapping[original_segment]
            new_customer_code = customer_code.replace(original_segment, new_segment, 1)
            account['customer_code'] = new_customer_code
            filtered_accounts.append(account)
    
    print(f"[INFO] Filtered to {len(filtered_accounts)} accounts for segments A, B, C, D, E")
    
    # Generate transactions
    print(f"[INFO] Generating transactions from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    transactions = generator.generate_transactions_for_accounts(
        filtered_accounts, start_date, end_date
    )
    
    print(f"[SUCCESS] Generated {len(transactions)} transactions")
    
    # Save transactions to CSV
    output_file_path = "output/banking_data_transactions.csv"
    generator.save_transactions_to_csv(transactions, output_file_path)
    
    # Analyze by segment
    segment_transactions = {}
    for txn in transactions:
        segment = txn.customer_code.split('_')[0]
        if segment not in segment_transactions:
            segment_transactions[segment] = []
        segment_transactions[segment].append(txn)
    
    print(f"\n[ANALYSIS] Transaction Analysis by Segment:")
    for segment, txns in segment_transactions.items():
        if txns:
            amounts = [t.amount for t in txns]
            types = [t.transaction_type for t in txns]
            balances = [t.balance for t in txns]
            term_months = [t.term_month for t in txns if t.term_month > 0]
            account_types = [t.account_type for t in txns]
            
            print(f"\n   {segment} Segment ({len(txns)} transactions):")
            print(f"     Amount: Min={min(amounts):,}, Max={max(amounts):,}, Mean={sum(amounts)/len(amounts):,.0f}")
            print(f"     Balance: Min={min(balances):,}, Max={max(balances):,}, Mean={sum(balances)/len(balances):,.0f}")
            
            if term_months:
                print(f"     Term Months: Min={min(term_months)}, Max={max(term_months)}, Mean={sum(term_months)/len(term_months):.1f}")
            
            # Transaction type distribution
            type_counts = {}
            for t in types:
                type_counts[t] = type_counts.get(t, 0) + 1
            
            print(f"     Types:")
            for t_type, count in type_counts.items():
                percentage = (count / len(txns)) * 100
                print(f"       {t_type}: {count} ({percentage:.1f}%)")
            
            # Account type distribution
            account_type_counts = {}
            for at in account_types:
                account_type_counts[at] = account_type_counts.get(at, 0) + 1
            
            print(f"     Account Types:")
            for at_type, count in account_type_counts.items():
                percentage = (count / len(txns)) * 100
                print(f"       {at_type}: {count} ({percentage:.1f}%)")
    
    print(f"\n[COMPLETED] Transaction generation completed. Data saved to {output_file_path}")

if __name__ == "__main__":
    main()
