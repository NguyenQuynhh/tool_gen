"""
New Main Generator với flow mới: CUSTOMER → TRANSACTION → ACCOUNT
X(50%) - Khách hàng giàu có, tiêu nhiều tiền
Y(30%) - Khách hàng trung bình
Z(20%) - Khách hàng ít tiền
"""

import pandas as pd
import random
from datetime import datetime, timedelta
from typing import List, Dict
import os

from test_config import test_config
from customer_generator import NewCustomerGenerator, NewCustomer
from transaction_generator import NewTransactionGenerator, NewTransaction
from account_generator import NewAccountGenerator, NewAccount

class NewMainGenerator:
    """New Main Generator với flow CUSTOMER → TRANSACTION → ACCOUNT"""
    
    def __init__(self, config: test_config = None):
        self.config = config or test_config()
        self.customer_generator = NewCustomerGenerator(self.config)
        self.transaction_generator = NewTransactionGenerator(self.config)
        self.account_generator = NewAccountGenerator(self.config)

    def generate_balanced_dataset(self, num_customers: int) -> Dict[str, pd.DataFrame]:
        """Generate balanced dataset với flow mới"""
        
        print(f"🚀 Bắt đầu generate NEW BALANCED dataset với {num_customers} customers")
        print(f"📅 Thời gian: {self.config.START_DATE.strftime('%Y-%m-%d')} đến {self.config.END_DATE.strftime('%Y-%m-%d')}")
        print(f"🎯 Target segments: X(50%), Y(30%), Z(20%)")
        print(f"🔄 Flow: CUSTOMER → TRANSACTION → ACCOUNT")

        # STEP 1: Generate customers trước
        print("\n1️⃣ Generating customers...")
        customers = self.customer_generator.generate_customers_by_count(num_customers)
        print(f"   ✅ Generated {len(customers)} customers")
        
        # Convert customers to dict for easier processing
        customers_dict = [customer.__dict__ for customer in customers]

        # STEP 2: Generate accounts dựa trên customer segments
        print("\n2️⃣ Generating accounts based on customer segments...")
        accounts = self.account_generator.generate_accounts_for_customers(
            customers_dict, self.config.START_DATE, self.config.END_DATE
        )
        print(f"   ✅ Generated {len(accounts)} accounts")
        
        # Convert accounts to dict for easier processing
        accounts_dict = [account.__dict__ for account in accounts]

        # STEP 3: Generate transactions dựa trên customer behavior
        print("\n3️⃣ Generating transactions based on customer behavior...")
        transactions = self.transaction_generator.generate_transactions_for_accounts(
            accounts_dict, self.config.START_DATE, self.config.END_DATE
        )
        print(f"   ✅ Generated {len(transactions)} transactions")
        
        # Convert transactions to dict for easier processing
        transactions_dict = [transaction.__dict__ for transaction in transactions]

        # STEP 4: Update account balances
        print("\n4️⃣ Updating account balances...")
        accounts = self.account_generator.update_account_balances(accounts, transactions_dict)
        print(f"   ✅ Updated {len(accounts)} account balances")

        # Convert to DataFrames
        customers_df = pd.DataFrame(customers_dict)
        accounts_df = pd.DataFrame([account.__dict__ for account in accounts])
        transactions_df = pd.DataFrame(transactions_dict)

        return {
            'customers': customers_df,
            'accounts': accounts_df,
            'transactions': transactions_df
        }

    def export_to_csv(self, dataset: Dict[str, pd.DataFrame], output_prefix: str = "output/banking_data"):
        """Export data to CSV files"""
        print("\n📁 Exporting data to CSV files...")
        
        # Ensure output directory exists
        os.makedirs("output", exist_ok=True)
        
        customers_file = f"{output_prefix}_customers.csv"
        accounts_file = f"{output_prefix}_accounts.csv"
        transactions_file = f"{output_prefix}_transactions.csv"

        dataset['customers'].to_csv(customers_file, index=False)
        dataset['accounts'].to_csv(accounts_file, index=False)
        dataset['transactions'].to_csv(transactions_file, index=False)

        print(f"   ✅ Customers exported to {customers_file}")
        print(f"   ✅ Accounts exported to {accounts_file}")
        print(f"   ✅ Transactions exported to {transactions_file}")
        
        return {
            'customers_file': customers_file,
            'accounts_file': accounts_file,
            'transactions_file': transactions_file
        }

    def analyze_dataset(self, dataset: Dict[str, pd.DataFrame]):
        """Analyze the generated dataset"""
        print("\n📊 DATASET ANALYSIS")
        print("=" * 50)
        
        customers_df = dataset['customers']
        accounts_df = dataset['accounts']
        transactions_df = dataset['transactions']
        
        # Basic counts
        print(f"📈 Record Counts:")
        print(f"   Customers: {len(customers_df):,}")
        print(f"   Accounts: {len(accounts_df):,}")
        print(f"   Transactions: {len(transactions_df):,}")
        
        # Segment distribution
        print(f"\n🎯 Segment Distribution:")
        segment_counts = customers_df['customer_segment'].value_counts()
        for segment, count in segment_counts.items():
            percentage = (count / len(customers_df)) * 100
            print(f"   {segment}: {count:,} ({percentage:.1f}%)")
        
        # Age distribution by segment
        print(f"\n🎂 Age Distribution by Segment:")
        customers_df['age'] = (datetime.now() - pd.to_datetime(customers_df['dob'])).dt.days // 365
        for segment in ['X', 'Y', 'Z']:
            segment_customers = customers_df[customers_df['customer_segment'] == segment]
            if len(segment_customers) > 0:
                ages = segment_customers['age']
                print(f"   {segment}: Min={ages.min()}, Max={ages.max()}, Mean={ages.mean():.1f}")
        
        # Occupation distribution by segment
        print(f"\n💼 Occupation Distribution by Segment:")
        for segment in ['X', 'Y', 'Z']:
            segment_customers = customers_df[customers_df['customer_segment'] == segment]
            if len(segment_customers) > 0:
                occupations = segment_customers['occupation'].value_counts()
                print(f"   {segment}:")
                for occ, count in occupations.items():
                    percentage = (count / len(segment_customers)) * 100
                    print(f"     {occ}: {count} ({percentage:.1f}%)")
        
        # Income distribution by segment
        print(f"\n💰 Income Distribution by Segment:")
        for segment in ['X', 'Y', 'Z']:
            segment_customers = customers_df[customers_df['customer_segment'] == segment]
            if len(segment_customers) > 0:
                incomes = segment_customers['income_range'].value_counts()
                print(f"   {segment}:")
                for income, count in incomes.items():
                    percentage = (count / len(segment_customers)) * 100
                    print(f"     {income}: {count} ({percentage:.1f}%)")
        
        # Account analysis by segment
        print(f"\n🏦 Account Analysis by Segment:")
        for segment in ['X', 'Y', 'Z']:
            segment_accounts = accounts_df[accounts_df['customer_code'].str.startswith(segment)]
            if len(segment_accounts) > 0:
                print(f"   {segment} ({len(segment_accounts)} accounts):")
                
                # Product type distribution
                product_types = segment_accounts['product_type'].value_counts()
                for p_type, count in product_types.items():
                    percentage = (count / len(segment_accounts)) * 100
                    print(f"     {p_type}: {count} ({percentage:.1f}%)")
                
                # Term months distribution
                term_accounts = segment_accounts[segment_accounts['term_months'] > 0]
                if len(term_accounts) > 0:
                    term_months = term_accounts['term_months'].value_counts().sort_index()
                    print(f"     Term Months:")
                    for term, count in term_months.items():
                        percentage = (count / len(term_accounts)) * 100
                        print(f"       {term} months: {count} ({percentage:.1f}%)")
                
                # Interest rate analysis
                interest_rates = segment_accounts['interest_rate']
                print(f"     Interest Rates: Min={interest_rates.min():.3f}%, Max={interest_rates.max():.3f}%, Mean={interest_rates.mean():.3f}%")
        
        # Transaction analysis by segment
        print(f"\n💳 Transaction Analysis by Segment:")
        for segment in ['X', 'Y', 'Z']:
            segment_transactions = transactions_df[transactions_df['customer_code'].str.startswith(segment)]
            if len(segment_transactions) > 0:
                print(f"   {segment} ({len(segment_transactions)} transactions):")
                
                # Amount analysis
                amounts = segment_transactions['amount']
                print(f"     Amount: Min={amounts.min():,.0f}, Max={amounts.max():,.0f}, Mean={amounts.mean():,.0f}")
                
                # Transaction type distribution
                types = segment_transactions['transaction_type'].value_counts()
                print(f"     Types:")
                for t_type, count in types.items():
                    percentage = (count / len(segment_transactions)) * 100
                    print(f"       {t_type}: {count} ({percentage:.1f}%)")

def main():
    """Test New Main Generator"""
    generator = NewMainGenerator()
    
    # Generate dataset
    dataset = generator.generate_balanced_dataset(1000)
    
    # Export to CSV
    output_files = generator.export_to_csv(dataset)
    
    # Analyze dataset
    generator.analyze_dataset(dataset)
    
    print("\n✅ New balanced dataset generation completed!")
    print(f"📁 Files saved to: {output_files}")

if __name__ == "__main__":
    main()
