"""
RFM Fix Generator
Generator chuyên biệt để sửa RFM constraints
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

class RFMFixGenerator:
    """RFM Fix Generator để sửa RFM constraints"""
    
    def __init__(self, config: test_config = None):
        self.config = config or test_config()
        self.customer_segment_generator = CustomerSegmentGenerator(self.config)
        self.transaction_generator = EnhancedTransactionGenerator(self.config)
        self.account_generator = Phase2AccountGenerator(self.config)
        self.customer_generator = Phase3CustomerGenerator(self.config)

    def generate_rfm_fixed_dataset(self, num_customers: int) -> Dict[str, pd.DataFrame]:
        """Generate dataset với RFM constraints được sửa"""
        
        print(f"🚀 Bắt đầu generate RFM FIXED dataset với {num_customers} customers")
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

        # 2. Generate accounts using Phase 2 Account Generator
        print("\n2️⃣ Generating accounts with Phase 2 Account Generator...")
        for segment_info in customer_segments:
            customer_code = segment_info.customer_code
            customer_segment = segment_info.segment
            
            # Generate accounts for this customer
            accounts_for_customer = self.account_generator.generate_accounts_for_customer(
                customer_code, customer_segment, self.config.START_DATE, self.config.END_DATE
            )
            all_accounts.extend(accounts_for_customer)
            customer_accounts_map[customer_code] = accounts_for_customer
        print(f"   ✅ Generated {len(all_accounts)} accounts")

        # 3. Generate transactions with RFM fix
        print("\n3️⃣ Generating transactions with RFM fix...")
        for account in all_accounts:
            # Determine segment
            if account.customer_code.startswith('X_'):
                segment = 'X'
            elif account.customer_code.startswith('Y_'):
                segment = 'Y'
            else:
                segment = 'Z'
            
            # Generate transactions with RFM compliance
            transactions_for_account = self._generate_rfm_compliant_transactions(
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

        # 5. Generate customers using Phase 3 Customer Generator
        print("\n5️⃣ Generating customers with Phase 3 Customer Generator...")
        customers = self.customer_generator.generate_customers_from_data(
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

    def _generate_rfm_compliant_transactions(self, account: Phase2Account, segment: str, start_date: datetime, end_date: datetime) -> List[EnhancedTransaction]:
        """Generate RFM compliant transactions for an account"""
        
        transactions = []
        effective_maturity_date = account.maturity_date if account.maturity_date else end_date
        
        # RFM requirements by segment
        rfm_requirements = {
            'X': {
                'frequency_per_month': (6, 8),
                'amount_min': 50_000_000,
                'recency_days': 30
            },
            'Y': {
                'frequency_per_month': (3, 4),
                'amount_min': 30_000_000,
                'recency_days': 180
            },
            'Z': {
                'frequency_per_month': (2, 3),
                'amount_min': 5_000_000,
                'recency_days': 365
            }
        }
        
        req = rfm_requirements[segment]
        
        # Calculate total transactions needed
        months = (end_date - start_date).days // 30
        min_transactions = req['frequency_per_month'][0] * months
        max_transactions = req['frequency_per_month'][1] * months
        total_transactions = random.randint(min_transactions, max_transactions)
        
        # Generate transactions with RFM compliance
        for i in range(total_transactions):
            # Generate date with RFM compliance
            if segment == 'X':
                # X segment: bias towards recent transactions
                if random.random() < 0.8:
                    # 80% chance for recent transaction within last 30 days
                    random_days = random.randint((end_date - start_date).days - 30, (end_date - start_date).days)
                else:
                    random_days = random.randint(0, (end_date - start_date).days)
            elif segment == 'Y':
                # Y segment: bias towards recent transactions within 6 months
                if random.random() < 0.6:
                    # 60% chance for recent transaction within last 6 months
                    random_days = random.randint((end_date - start_date).days - 180, (end_date - start_date).days)
                else:
                    random_days = random.randint(0, (end_date - start_date).days)
            else:  # Z
                # Z segment: spread throughout period, avoid recent transactions
                if random.random() < 0.8 and (end_date - start_date).days > 180:
                    # 80% chance for old transactions (>180 days ago)
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
            
            # Determine amount based on segment and transaction type
            if transaction_type in ['Deposit', 'Fund Transfer']:
                if segment == 'X':
                    amount = random.randint(req['amount_min'], req['amount_min'] * 4)
                elif segment == 'Y':
                    amount = random.randint(req['amount_min'], req['amount_min'] * 3)
                else:  # Z
                    amount = random.randint(req['amount_min'], req['amount_min'] * 4)
            else:  # Withdrawals, Fees
                if segment == 'X':
                    amount = random.randint(10_000_000, 50_000_000)
                elif segment == 'Y':
                    amount = random.randint(5_000_000, 20_000_000)
                else:  # Z
                    amount = random.randint(10_000, 5_000_000)
            
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

    def export_to_csv(self, dataset: Dict[str, pd.DataFrame], output_prefix: str = "output/rfm_fixed_banking_data"):
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
    """Test RFM Fix Generator"""
    generator = RFMFixGenerator()
    
    # Generate dataset
    dataset = generator.generate_rfm_fixed_dataset(1000)
    output_files = generator.export_to_csv(dataset)
    
    print("\n✅ RFM Fixed dataset generation completed!")
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

if __name__ == "__main__":
    main()
