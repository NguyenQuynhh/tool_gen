"""
RFM Terminal Visualizer
CLI tool để visualize RFM analysis trên terminal
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
from typing import Dict, List, Tuple
import argparse

class RFMTerminalVisualizer:
    """RFM Terminal Visualizer với CLI tương tác"""
    
    def __init__(self):
        self.transactions_df = None
        self.accounts_df = None
        self.customers_df = None
        self.rfm_data = None
        
    def load_data(self, transactions_file: str, accounts_file: str, customers_file: str):
        """Load data từ CSV files"""
        try:
            print("📁 Loading data...")
            self.transactions_df = pd.read_csv(transactions_file)
            self.accounts_df = pd.read_csv(accounts_file)
            self.customers_df = pd.read_csv(customers_file)
            
            # Convert dates
            self.transactions_df['transaction_date'] = pd.to_datetime(self.transactions_df['transaction_date'])
            self.accounts_df['open_date'] = pd.to_datetime(self.accounts_df['open_date'])
            self.accounts_df['maturity_date'] = pd.to_datetime(self.accounts_df['maturity_date'])
            self.customers_df['dob'] = pd.to_datetime(self.customers_df['dob'])
            
            print(f"   ✅ Loaded {len(self.transactions_df):,} transactions")
            print(f"   ✅ Loaded {len(self.accounts_df):,} accounts")
            print(f"   ✅ Loaded {len(self.customers_df):,} customers")
            return True
        except Exception as e:
            print(f"   ❌ Error loading data: {e}")
            return False
    
    def calculate_rfm(self):
        """Calculate RFM metrics"""
        print("\n📊 Calculating RFM metrics...")
        
        # Calculate RFM for each customer
        rfm_data = []
        
        for _, customer in self.customers_df.iterrows():
            customer_code = customer['customer_code']
            segment = customer['customer_segment']
            
            # Get customer transactions
            customer_transactions = self.transactions_df[
                self.transactions_df['customer_code'] == customer_code
            ]
            
            if len(customer_transactions) == 0:
                continue
            
            # Calculate Recency (days since last transaction)
            last_transaction = customer_transactions['transaction_date'].max()
            recency = (datetime.now() - last_transaction).days
            
            # Calculate Frequency (transactions per month)
            months = (customer_transactions['transaction_date'].max() - 
                     customer_transactions['transaction_date'].min()).days / 30
            frequency = len(customer_transactions) / max(months, 1)
            
            # Calculate Monetary (average transaction amount)
            monetary = customer_transactions['amount'].mean()
            
            # Calculate total amount
            total_amount = customer_transactions['amount'].sum()
            
            rfm_data.append({
                'customer_code': customer_code,
                'segment': segment,
                'recency': recency,
                'frequency': frequency,
                'monetary': monetary,
                'total_amount': total_amount,
                'transaction_count': len(customer_transactions)
            })
        
        self.rfm_data = pd.DataFrame(rfm_data)
        print(f"   ✅ Calculated RFM for {len(self.rfm_data)} customers")
    
    def show_main_menu(self):
        """Show main menu"""
        print("\n" + "="*60)
        print("🎯 RFM TERMINAL VISUALIZER")
        print("="*60)
        print("1. 📊 RFM Overview")
        print("2. 📈 Segment Analysis")
        print("3. 📋 Transaction Distribution")
        print("4. 🏦 Account Distribution")
        print("5. 👥 Customer Distribution")
        print("6. 🔍 Search Customer")
        print("7. 📈 Export Report")
        print("8. ❌ Exit")
        print("="*60)
    
    def show_rfm_overview(self):
        """Show RFM overview với logic mới"""
        print("\n📊 RFM OVERVIEW - NEW LOGIC")
        print("-" * 50)
        
        if self.rfm_data is None:
            print("❌ No RFM data available. Please calculate RFM first.")
            return
        
        # Overall statistics
        print(f"📈 Total Customers: {len(self.rfm_data):,}")
        print(f"📈 Total Transactions: {len(self.transactions_df):,}")
        print(f"📈 Total Accounts: {len(self.accounts_df):,}")
        
        # Segment distribution với logic mới
        print(f"\n🎯 Segment Distribution (NEW LOGIC):")
        segment_counts = self.rfm_data['segment'].value_counts()
        for segment, count in segment_counts.items():
            percentage = (count / len(self.rfm_data)) * 100
            segment_name = {'X': 'VIP (50%)', 'Y': 'MEDIUM (30%)', 'Z': 'LOW (20%)'}.get(segment, segment)
            print(f"  {segment} ({segment_name}): {count:,} ({percentage:.1f}%)")
        
        # RFM statistics by segment
        print(f"\n📊 RFM Statistics by Segment:")
        for segment in ['X', 'Y', 'Z']:
            segment_data = self.rfm_data[self.rfm_data['segment'] == segment]
            if len(segment_data) > 0:
                segment_name = {'X': 'VIP', 'Y': 'MEDIUM', 'Z': 'LOW'}.get(segment, segment)
                print(f"\n  {segment} ({segment_name}) - {len(segment_data)} customers:")
                print(f"    Recency: Min={segment_data['recency'].min():.0f}, Max={segment_data['recency'].max():.0f}, Mean={segment_data['recency'].mean():.1f} days")
                print(f"    Frequency: Min={segment_data['frequency'].min():.1f}, Max={segment_data['frequency'].max():.1f}, Mean={segment_data['frequency'].mean():.1f} per month")
                print(f"    Monetary: Min={segment_data['monetary'].min():,.0f}, Max={segment_data['monetary'].max():,.0f}, Mean={segment_data['monetary'].mean():,.0f} VND")
    
    def show_segment_analysis(self):
        """Show segment analysis với logic mới"""
        print("\n📈 SEGMENT ANALYSIS - NEW LOGIC")
        print("-" * 50)
        
        if self.rfm_data is None:
            print("❌ No RFM data available. Please calculate RFM first.")
            return
        
        for segment in ['X', 'Y', 'Z']:
            segment_data = self.rfm_data[self.rfm_data['segment'] == segment]
            if len(segment_data) == 0:
                continue
            
            segment_name = {'X': 'VIP (50%)', 'Y': 'MEDIUM (30%)', 'Z': 'LOW (20%)'}.get(segment, segment)
            print(f"\n🎯 Segment {segment} ({segment_name}) - {len(segment_data)} customers:")
            print(f"  Recency: {segment_data['recency'].mean():.1f} days (avg)")
            print(f"  Frequency: {segment_data['frequency'].mean():.1f} transactions/month")
            print(f"  Monetary: {segment_data['monetary'].mean():,.0f} VND (avg)")
            print(f"  Total Amount: {segment_data['total_amount'].sum():,.0f} VND")
            
            # RFM compliance check với logic mới
            if segment == 'X':  # VIP - 50%
                recency_compliant = (segment_data['recency'] <= 30).sum()
                frequency_compliant = ((segment_data['frequency'] >= 6) & (segment_data['frequency'] <= 8)).sum()
                monetary_compliant = (segment_data['monetary'] >= 50_000_000).sum()
                print(f"  Target: Recent (≤30d), High freq (6-8/month), High amount (≥50M VND)")
            elif segment == 'Y':  # MEDIUM - 30%
                recency_compliant = ((segment_data['recency'] >= 60) & (segment_data['recency'] <= 180)).sum()
                frequency_compliant = ((segment_data['frequency'] >= 3) & (segment_data['frequency'] <= 4)).sum()
                monetary_compliant = (segment_data['monetary'] >= 30_000_000).sum()
                print(f"  Target: Medium recent (60-180d), Medium freq (3-4/month), Medium amount (≥30M VND)")
            else:  # Z - LOW - 20%
                recency_compliant = (segment_data['recency'] > 180).sum()
                frequency_compliant = ((segment_data['frequency'] >= 2) & (segment_data['frequency'] <= 3)).sum()
                monetary_compliant = ((segment_data['monetary'] >= 5_000_000) & (segment_data['monetary'] <= 20_000_000)).sum()
                print(f"  Target: Old (>180d), Low freq (2-3/month), Low amount (5-20M VND)")
            
            print(f"  Compliance:")
            print(f"    Recency: {recency_compliant}/{len(segment_data)} ({recency_compliant/len(segment_data)*100:.1f}%)")
            print(f"    Frequency: {frequency_compliant}/{len(segment_data)} ({frequency_compliant/len(segment_data)*100:.1f}%)")
            print(f"    Monetary: {monetary_compliant}/{len(segment_data)} ({monetary_compliant/len(segment_data)*100:.1f}%)")
    
    def show_customer_details(self):
        """Show customer details"""
        print("\n🔍 CUSTOMER DETAILS")
        print("-" * 40)
        
        if self.rfm_data is None:
            print("❌ No RFM data available. Please calculate RFM first.")
            return
        
        # Show top customers by different criteria
        print("🏆 Top 10 Customers by Total Amount:")
        top_customers = self.rfm_data.nlargest(10, 'total_amount')
        for i, (_, customer) in enumerate(top_customers.iterrows(), 1):
            print(f"  {i:2d}. {customer['customer_code']} ({customer['segment']}) - {customer['total_amount']:,.0f} VND")
        
        print("\n📊 Top 10 Customers by Frequency:")
        top_frequency = self.rfm_data.nlargest(10, 'frequency')
        for i, (_, customer) in enumerate(top_frequency.iterrows(), 1):
            print(f"  {i:2d}. {customer['customer_code']} ({customer['segment']}) - {customer['frequency']:.1f} transactions/month")
        
        print("\n⏰ Most Recent Customers:")
        most_recent = self.rfm_data.nsmallest(10, 'recency')
        for i, (_, customer) in enumerate(most_recent.iterrows(), 1):
            print(f"  {i:2d}. {customer['customer_code']} ({customer['segment']}) - {customer['recency']:.0f} days ago")
    
    def show_transaction_distribution(self):
        """Show transaction distribution analysis"""
        print("\n📋 TRANSACTION DISTRIBUTION")
        print("-" * 50)
        
        # Transaction Types Distribution
        print("💳 Transaction Types Distribution:")
        type_counts = self.transactions_df['transaction_type'].value_counts()
        total_txns = len(self.transactions_df)
        for txn_type, count in type_counts.items():
            percentage = (count / total_txns) * 100
            bar = "█" * int(percentage / 2)  # Visual bar
            print(f"  {txn_type:<20}: {count:>8,} ({percentage:>5.1f}%) {bar}")
        
        # Transaction Amount Distribution
        print(f"\n💰 Transaction Amount Distribution:")
        amounts = self.transactions_df['amount']
        print(f"  Min:     {amounts.min():>12,.0f} VND")
        print(f"  Max:     {amounts.max():>12,.0f} VND")
        print(f"  Mean:    {amounts.mean():>12,.0f} VND")
        print(f"  Median:  {amounts.median():>12,.0f} VND")
        print(f"  Total:   {amounts.sum():>12,.0f} VND")
        
        # Amount Ranges Distribution
        print(f"\n📊 Amount Ranges Distribution:")
        ranges = [
            ("< 1M VND", amounts < 1_000_000),
            ("1M - 10M VND", (amounts >= 1_000_000) & (amounts < 10_000_000)),
            ("10M - 50M VND", (amounts >= 10_000_000) & (amounts < 50_000_000)),
            ("50M - 100M VND", (amounts >= 50_000_000) & (amounts < 100_000_000)),
            (">= 100M VND", amounts >= 100_000_000)
        ]
        for range_name, condition in ranges:
            count = condition.sum()
            percentage = (count / total_txns) * 100
            bar = "█" * int(percentage / 2)
            print(f"  {range_name:<15}: {count:>8,} ({percentage:>5.1f}%) {bar}")
        
        # Channel Distribution
        print(f"\n📱 Channel Distribution:")
        channel_counts = self.transactions_df['channel_txn'].value_counts()
        for channel, count in channel_counts.items():
            percentage = (count / total_txns) * 100
            bar = "█" * int(percentage / 2)
            print(f"  {channel:<15}: {count:>8,} ({percentage:>5.1f}%) {bar}")
        
        # Status Distribution
        print(f"\n📊 Status Distribution:")
        status_counts = self.transactions_df['status_txn'].value_counts()
        for status, count in status_counts.items():
            percentage = (count / total_txns) * 100
            bar = "█" * int(percentage / 2)
            print(f"  {status:<15}: {count:>8,} ({percentage:>5.1f}%) {bar}")
        
        # Currency Distribution
        print(f"\n💱 Currency Distribution:")
        currency_counts = self.transactions_df['currency'].value_counts()
        for currency, count in currency_counts.items():
            percentage = (count / total_txns) * 100
            bar = "█" * int(percentage / 2)
            print(f"  {currency:<15}: {count:>8,} ({percentage:>5.1f}%) {bar}")
        
        # Monthly Transaction Distribution
        print(f"\n📅 Monthly Transaction Distribution:")
        self.transactions_df['month'] = self.transactions_df['transaction_date'].dt.to_period('M')
        monthly_counts = self.transactions_df['month'].value_counts().sort_index()
        for month, count in monthly_counts.items():
            percentage = (count / total_txns) * 100
            bar = "█" * int(percentage / 2)
            print(f"  {str(month):<15}: {count:>8,} ({percentage:>5.1f}%) {bar}")
    
    def show_account_distribution(self):
        """Show account distribution analysis"""
        print("\n🏦 ACCOUNT DISTRIBUTION")
        print("-" * 50)
        
        total_accounts = len(self.accounts_df)
        
        # Product Types Distribution
        print("💼 Product Types Distribution:")
        product_counts = self.accounts_df['product_type'].value_counts()
        for product, count in product_counts.items():
            percentage = (count / total_accounts) * 100
            bar = "█" * int(percentage / 2)
            print(f"  {product:<20}: {count:>6,} ({percentage:>5.1f}%) {bar}")
        
        # Term Months Distribution
        print(f"\n📅 Term Months Distribution:")
        term_counts = self.accounts_df['term_months'].value_counts().sort_index()
        for term, count in term_counts.items():
            percentage = (count / total_accounts) * 100
            bar = "█" * int(percentage / 2)
            term_label = f"{term} months" if term > 0 else "Demand (0 months)"
            print(f"  {term_label:<20}: {count:>6,} ({percentage:>5.1f}%) {bar}")
        
        # Account Status Distribution
        print(f"\n📊 Account Status Distribution:")
        status_counts = self.accounts_df['status'].value_counts()
        for status, count in status_counts.items():
            percentage = (count / total_accounts) * 100
            bar = "█" * int(percentage / 2)
            print(f"  {status:<20}: {count:>6,} ({percentage:>5.1f}%) {bar}")
        
        # Channel Opened Distribution
        print(f"\n📱 Channel Opened Distribution:")
        channel_counts = self.accounts_df['channel_opened'].value_counts()
        for channel, count in channel_counts.items():
            percentage = (count / total_accounts) * 100
            bar = "█" * int(percentage / 2)
            print(f"  {channel:<20}: {count:>6,} ({percentage:>5.1f}%) {bar}")
        
        # Currency Distribution
        print(f"\n💱 Currency Distribution:")
        currency_counts = self.accounts_df['currency'].value_counts()
        for currency, count in currency_counts.items():
            percentage = (count / total_accounts) * 100
            bar = "█" * int(percentage / 2)
            print(f"  {currency:<20}: {count:>6,} ({percentage:>5.1f}%) {bar}")
        
        # Interest Rate Distribution
        print(f"\n💰 Interest Rate Distribution:")
        interest_rates = self.accounts_df['interest_rate']
        print(f"  Min:     {interest_rates.min():>8.3f}%")
        print(f"  Max:     {interest_rates.max():>8.3f}%")
        print(f"  Mean:    {interest_rates.mean():>8.3f}%")
        print(f"  Median:  {interest_rates.median():>8.3f}%")
        
        # Interest Rate Ranges
        print(f"\n📊 Interest Rate Ranges:")
        rate_ranges = [
            ("< 1%", interest_rates < 0.01),
            ("1% - 3%", (interest_rates >= 0.01) & (interest_rates < 0.03)),
            ("3% - 5%", (interest_rates >= 0.03) & (interest_rates < 0.05)),
            ("5% - 7%", (interest_rates >= 0.05) & (interest_rates < 0.07)),
            (">= 7%", interest_rates >= 0.07)
        ]
        for range_name, condition in rate_ranges:
            count = condition.sum()
            percentage = (count / total_accounts) * 100
            bar = "█" * int(percentage / 2)
            print(f"  {range_name:<20}: {count:>6,} ({percentage:>5.1f}%) {bar}")
        
        # Account Balance Distribution
        print(f"\n💰 Account Balance Distribution:")
        balances = self.accounts_df['current_balance']
        print(f"  Min:     {balances.min():>12,.0f} VND")
        print(f"  Max:     {balances.max():>12,.0f} VND")
        print(f"  Mean:    {balances.mean():>12,.0f} VND")
        print(f"  Median:  {balances.median():>12,.0f} VND")
        print(f"  Total:   {balances.sum():>12,.0f} VND")
        
        # Balance Ranges Distribution
        print(f"\n📊 Balance Ranges Distribution:")
        balance_ranges = [
            ("< 1M VND", balances < 1_000_000),
            ("1M - 10M VND", (balances >= 1_000_000) & (balances < 10_000_000)),
            ("10M - 50M VND", (balances >= 10_000_000) & (balances < 50_000_000)),
            ("50M - 100M VND", (balances >= 50_000_000) & (balances < 100_000_000)),
            (">= 100M VND", balances >= 100_000_000)
        ]
        for range_name, condition in balance_ranges:
            count = condition.sum()
            percentage = (count / total_accounts) * 100
            bar = "█" * int(percentage / 2)
            print(f"  {range_name:<20}: {count:>6,} ({percentage:>5.1f}%) {bar}")
        
        # Accounts per Customer Distribution
        print(f"\n👥 Accounts per Customer Distribution:")
        accounts_per_customer = self.accounts_df['customer_code'].value_counts()
        account_counts = accounts_per_customer.value_counts().sort_index()
        for count, frequency in account_counts.items():
            percentage = (frequency / len(accounts_per_customer)) * 100
            bar = "█" * int(percentage / 2)
            print(f"  {count} accounts{' ':<12}: {frequency:>6,} customers ({percentage:>5.1f}%) {bar}")
    
    def show_customer_distribution(self):
        """Show customer distribution analysis"""
        print("\n👥 CUSTOMER DISTRIBUTION")
        print("-" * 50)
        
        total_customers = len(self.customers_df)
        
        # Gender Distribution
        print("👤 Gender Distribution:")
        gender_counts = self.customers_df['gender'].value_counts()
        for gender, count in gender_counts.items():
            percentage = (count / total_customers) * 100
            bar = "█" * int(percentage / 2)
            print(f"  {gender:<20}: {count:>6,} ({percentage:>5.1f}%) {bar}")
        
        # Marital Status Distribution
        print(f"\n💑 Marital Status Distribution:")
        marital_counts = self.customers_df['marital_status'].value_counts()
        for status, count in marital_counts.items():
            percentage = (count / total_customers) * 100
            bar = "█" * int(percentage / 2)
            print(f"  {status:<20}: {count:>6,} ({percentage:>5.1f}%) {bar}")
        
        # Nationality Distribution
        print(f"\n🌍 Nationality Distribution:")
        nationality_counts = self.customers_df['nationality'].value_counts()
        for nationality, count in nationality_counts.items():
            percentage = (count / total_customers) * 100
            bar = "█" * int(percentage / 2)
            print(f"  {nationality:<20}: {count:>6,} ({percentage:>5.1f}%) {bar}")
        
        # Occupation Distribution
        print(f"\n💼 Occupation Distribution:")
        occupation_counts = self.customers_df['occupation'].value_counts()
        for occupation, count in occupation_counts.items():
            percentage = (count / total_customers) * 100
            bar = "█" * int(percentage / 2)
            print(f"  {occupation:<20}: {count:>6,} ({percentage:>5.1f}%) {bar}")
        
        # Income Range Distribution
        print(f"\n💰 Income Range Distribution:")
        income_counts = self.customers_df['income_range'].value_counts()
        for income, count in income_counts.items():
            percentage = (count / total_customers) * 100
            bar = "█" * int(percentage / 2)
            print(f"  {income:<20}: {count:>6,} ({percentage:>5.1f}%) {bar}")
        
        # Income Currency Distribution
        print(f"\n💱 Income Currency Distribution:")
        currency_counts = self.customers_df['income_currency'].value_counts()
        for currency, count in currency_counts.items():
            percentage = (count / total_customers) * 100
            bar = "█" * int(percentage / 2)
            print(f"  {currency:<20}: {count:>6,} ({percentage:>5.1f}%) {bar}")
        
        # Source of Income Distribution
        print(f"\n📊 Source of Income Distribution:")
        source_counts = self.customers_df['source_of_income'].value_counts()
        for source, count in source_counts.items():
            percentage = (count / total_customers) * 100
            bar = "█" * int(percentage / 2)
            print(f"  {source:<20}: {count:>6,} ({percentage:>5.1f}%) {bar}")
        
        # Customer Status Distribution
        print(f"\n📊 Customer Status Distribution:")
        status_counts = self.customers_df['status'].value_counts()
        for status, count in status_counts.items():
            percentage = (count / total_customers) * 100
            bar = "█" * int(percentage / 2)
            print(f"  {status:<20}: {count:>6,} ({percentage:>5.1f}%) {bar}")
        
        # Customer Segment Distribution
        print(f"\n🎯 Customer Segment Distribution:")
        segment_counts = self.customers_df['customer_segment'].value_counts()
        for segment, count in segment_counts.items():
            percentage = (count / total_customers) * 100
            bar = "█" * int(percentage / 2)
            print(f"  {segment:<20}: {count:>6,} ({percentage:>5.1f}%) {bar}")
        
        # Age Distribution
        print(f"\n🎂 Age Distribution:")
        self.customers_df['age'] = (datetime.now() - self.customers_df['dob']).dt.days // 365
        ages = self.customers_df['age']
        print(f"  Min:     {ages.min():>3.0f} years")
        print(f"  Max:     {ages.max():>3.0f} years")
        print(f"  Mean:    {ages.mean():>3.1f} years")
        print(f"  Median:  {ages.median():>3.0f} years")
        
        # Age Groups Distribution
        print(f"\n📊 Age Groups Distribution:")
        age_groups = [
            ("< 25 years", ages < 25),
            ("25 - 40 years", (ages >= 25) & (ages < 40)),
            ("40 - 55 years", (ages >= 40) & (ages < 55)),
            (">= 55 years", ages >= 55)
        ]
        for group_name, condition in age_groups:
            count = condition.sum()
            percentage = (count / total_customers) * 100
            bar = "█" * int(percentage / 2)
            print(f"  {group_name:<20}: {count:>6,} ({percentage:>5.1f}%) {bar}")
        
        # Top Cities Distribution
        print(f"\n🏙️ Top 10 Cities Distribution:")
        city_counts = self.customers_df['city'].value_counts().head(10)
        for city, count in city_counts.items():
            percentage = (count / total_customers) * 100
            bar = "█" * int(percentage / 2)
            print(f"  {city:<20}: {count:>6,} ({percentage:>5.1f}%) {bar}")
        
        # Segment vs Income Analysis
        print(f"\n🎯 Segment vs Income Analysis:")
        segment_income = self.customers_df.groupby(['customer_segment', 'income_range']).size().unstack(fill_value=0)
        for segment in ['X', 'Y', 'Z']:
            if segment in segment_income.index:
                print(f"\n  {segment} Segment Income Distribution:")
                segment_data = segment_income.loc[segment]
                total_segment = segment_data.sum()
                for income, count in segment_data.items():
                    if count > 0:
                        percentage = (count / total_segment) * 100
                        bar = "█" * int(percentage / 2)
                        print(f"    {income:<18}: {count:>4,} ({percentage:>5.1f}%) {bar}")
    
    def search_customer(self):
        """Search customer by code"""
        print("\n🔍 SEARCH CUSTOMER")
        print("-" * 40)
        
        customer_code = input("Enter customer code (or 'back' to return): ").strip()
        if customer_code.lower() == 'back':
            return
        
        # Find customer
        customer = self.customers_df[self.customers_df['customer_code'] == customer_code]
        if len(customer) == 0:
            print(f"❌ Customer {customer_code} not found.")
            return
        
        customer = customer.iloc[0]
        print(f"\n👤 Customer: {customer['customer_code']}")
        print(f"  Name: {customer['full_name']}")
        print(f"  Segment: {customer['customer_segment']}")
        print(f"  Gender: {customer['gender']}")
        print(f"  City: {customer['city']}")
        print(f"  Occupation: {customer['occupation']}")
        print(f"  Income: {customer['income_range']} {customer['income_currency']}")
        print(f"  Status: {customer['status']}")
        
        # RFM data
        if self.rfm_data is not None:
            rfm_customer = self.rfm_data[self.rfm_data['customer_code'] == customer_code]
            if len(rfm_customer) > 0:
                rfm = rfm_customer.iloc[0]
                print(f"\n📊 RFM Data:")
                print(f"  Recency: {rfm['recency']:.0f} days")
                print(f"  Frequency: {rfm['frequency']:.1f} transactions/month")
                print(f"  Monetary: {rfm['monetary']:,.0f} VND")
                print(f"  Total Amount: {rfm['total_amount']:,.0f} VND")
                print(f"  Transaction Count: {rfm['transaction_count']}")
        
        # Customer accounts
        customer_accounts = self.accounts_df[self.accounts_df['customer_code'] == customer_code]
        print(f"\n🏦 Accounts ({len(customer_accounts)}):")
        for _, account in customer_accounts.iterrows():
            print(f"  {account['account_id']}: {account['product_type']} - {account['current_balance']:,.0f} VND")
    
    def export_report(self):
        """Export RFM report"""
        print("\n📈 EXPORT REPORT")
        print("-" * 40)
        
        if self.rfm_data is None:
            print("❌ No RFM data available. Please calculate RFM first.")
            return
        
        filename = input("Enter filename (default: rfm_report.csv): ").strip()
        if not filename:
            filename = "rfm_report.csv"
        
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        try:
            self.rfm_data.to_csv(filename, index=False)
            print(f"✅ Report exported to {filename}")
        except Exception as e:
            print(f"❌ Error exporting report: {e}")
    
    def run(self):
        """Run the visualizer"""
        print("🎯 RFM Terminal Visualizer")
        print("=" * 40)
        
        # Load data
        if not os.path.exists(self.transactions_file):
            print(f"❌ Data file not found: {self.transactions_file}")
            print("Please run the data generator first.")
            return
        
        if not self.load_data(self.transactions_file, self.accounts_file, self.customers_file):
            return
        
        # Calculate RFM
        self.calculate_rfm()
        
        # Main loop
        while True:
            self.show_main_menu()
            choice = input("\nSelect option (1-8): ").strip()
            
            if choice == '1':
                self.show_rfm_overview()
            elif choice == '2':
                self.show_segment_analysis()
            elif choice == '3':
                self.show_transaction_distribution()
            elif choice == '4':
                self.show_account_distribution()
            elif choice == '5':
                self.show_customer_distribution()
            elif choice == '6':
                self.search_customer()
            elif choice == '7':
                self.export_report()
            elif choice == '8':
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid option. Please try again.")
            
            input("\nPress Enter to continue...")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='RFM Terminal Visualizer - NEW LOGIC')
    parser.add_argument('--transactions', default='output/banking_data_transactions.csv',
                       help='Path to transactions CSV file')
    parser.add_argument('--accounts', default='output/banking_data_accounts.csv',
                       help='Path to accounts CSV file')
    parser.add_argument('--customers', default='output/banking_data_customers.csv',
                       help='Path to customers CSV file')
    
    args = parser.parse_args()
    
    visualizer = RFMTerminalVisualizer()
    
    # Override default files if provided
    visualizer.transactions_file = args.transactions
    visualizer.accounts_file = args.accounts
    visualizer.customers_file = args.customers
    
    visualizer.run()

if __name__ == "__main__":
    main()
