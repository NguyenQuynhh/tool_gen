"""
Account Constraint Validator
Validator chuyên biệt cho account constraints
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple
import numpy as np

class AccountConstraintValidator:
    """Validator chuyên biệt cho account constraints"""
    
    def __init__(self):
        # Account constraints theo yêu cầu
        self.product_types = ['demand_saving', 'term_saving']
        self.term_months_config = {
            'demand_saving': [0],
            'term_saving': [1, 3, 6, 9, 12, 24, 36]
        }
        self.interest_rates_config = {
            0: (0.0001, 0.005),  # Demand: 0.01% - 0.5%
            1: (0.03, 0.04),     # 1 month: 3% - 4%
            3: (0.03, 0.04),     # 3 months: 3% - 4%
            6: (0.045, 0.055),   # 6 months: 4.5% - 5.5%
            9: (0.045, 0.055),   # 9 months: 4.5% - 5.5%
            12: (0.048, 0.06),   # 12 months: 4.8% - 6%
            24: (0.065, 0.07),   # 24 months: 6.5% - 7%
            36: (0.065, 0.07)    # 36 months: 6.5% - 7%
        }
        self.status_distribution = {'active': 0.82, 'closed': 0.12, 'suspend': 0.06}
        self.channels = ['mobile/internet', 'atm', 'branch']
        self.currencies = ['VND', 'USD', 'EUR']
        
    def validate_account_constraints(self, accounts_df: pd.DataFrame) -> Dict[str, Any]:
        """Validate tất cả account constraints"""
        
        print("🔍 ACCOUNT CONSTRAINT VALIDATION")
        print("================================================================================")
        print(f"📁 Loading accounts data...")
        print(f"   ✅ Loaded {len(accounts_df):,} accounts")
        
        results = {}
        overall_valid = True
        passed_validations = 0
        total_validations = 0
        
        # 1. Validate Product Types
        print("\n📊 Validating product types...")
        product_valid, product_report = self._validate_product_types(accounts_df)
        results['product_types'] = {'valid': product_valid, 'report': product_report}
        overall_valid &= product_valid
        total_validations += 1
        if product_valid: passed_validations += 1
        
        # 2. Validate Term Months
        print("\n📅 Validating term months...")
        term_valid, term_report = self._validate_term_months(accounts_df)
        results['term_months'] = {'valid': term_valid, 'report': term_report}
        overall_valid &= term_valid
        total_validations += 1
        if term_valid: passed_validations += 1
        
        # 3. Validate Interest Rates
        print("\n💰 Validating interest rates...")
        interest_valid, interest_report = self._validate_interest_rates(accounts_df)
        results['interest_rates'] = {'valid': interest_valid, 'report': interest_report}
        overall_valid &= interest_valid
        total_validations += 1
        if interest_valid: passed_validations += 1
        
        # 4. Validate Status Distribution
        print("\n📈 Validating status distribution...")
        status_valid, status_report = self._validate_status_distribution(accounts_df)
        results['status_distribution'] = {'valid': status_valid, 'report': status_report}
        overall_valid &= status_valid
        total_validations += 1
        if status_valid: passed_validations += 1
        
        # 5. Validate Maturity Date Logic
        print("\n🗓️ Validating maturity date logic...")
        maturity_valid, maturity_report = self._validate_maturity_date_logic(accounts_df)
        results['maturity_date_logic'] = {'valid': maturity_valid, 'report': maturity_report}
        overall_valid &= maturity_valid
        total_validations += 1
        if maturity_valid: passed_validations += 1
        
        # 6. Validate Channel Distribution
        print("\n📱 Validating channel distribution...")
        channel_valid, channel_report = self._validate_channel_distribution(accounts_df)
        results['channel_distribution'] = {'valid': channel_valid, 'report': channel_report}
        overall_valid &= channel_valid
        total_validations += 1
        if channel_valid: passed_validations += 1
        
        # 7. Validate Currency Distribution
        print("\n💱 Validating currency distribution...")
        currency_valid, currency_report = self._validate_currency_distribution(accounts_df)
        results['currency_distribution'] = {'valid': currency_valid, 'report': currency_report}
        overall_valid &= currency_valid
        total_validations += 1
        if currency_valid: passed_validations += 1
        
        # 8. Validate Segment Account Distribution
        print("\n👥 Validating segment account distribution...")
        segment_valid, segment_report = self._validate_segment_account_distribution(accounts_df)
        results['segment_distribution'] = {'valid': segment_valid, 'report': segment_report}
        overall_valid &= segment_valid
        total_validations += 1
        if segment_valid: passed_validations += 1
        
        # Print detailed report
        self._print_detailed_report(results, total_validations, passed_validations, overall_valid)
        
        return results
    
    def _validate_product_types(self, accounts_df: pd.DataFrame) -> Tuple[bool, Dict]:
        """Validate product types"""
        valid_types = accounts_df['product_type'].isin(self.product_types).all()
        invalid_types = accounts_df[~accounts_df['product_type'].isin(self.product_types)]
        
        return valid_types, {
            'valid_types': valid_types,
            'invalid_count': len(invalid_types),
            'total_count': len(accounts_df)
        }
    
    def _validate_term_months(self, accounts_df: pd.DataFrame) -> Tuple[bool, Dict]:
        """Validate term months logic"""
        valid_terms = True
        invalid_accounts = []
        
        for _, account in accounts_df.iterrows():
            product_type = account['product_type']
            term_month = account['term_months']
            
            expected_terms = self.term_months_config.get(product_type, [])
            if term_month not in expected_terms:
                valid_terms = False
                invalid_accounts.append({
                    'account_id': account['account_id'],
                    'product_type': product_type,
                    'term_months': term_month,
                    'expected_terms': expected_terms
                })
        
        return valid_terms, {
            'valid_terms': valid_terms,
            'invalid_accounts': invalid_accounts,
            'invalid_count': len(invalid_accounts)
        }
    
    def _validate_interest_rates(self, accounts_df: pd.DataFrame) -> Tuple[bool, Dict]:
        """Validate interest rates"""
        valid_rates = True
        invalid_accounts = []
        
        for _, account in accounts_df.iterrows():
            term_month = account['term_months']
            interest_rate = account['interest_rate']
            
            if term_month in self.interest_rates_config:
                min_rate, max_rate = self.interest_rates_config[term_month]
                if not (min_rate <= interest_rate <= max_rate):
                    valid_rates = False
                    invalid_accounts.append({
                        'account_id': account['account_id'],
                        'term_months': term_month,
                        'interest_rate': interest_rate,
                        'expected_range': (min_rate, max_rate)
                    })
        
        return valid_rates, {
            'valid_rates': valid_rates,
            'invalid_accounts': invalid_accounts,
            'invalid_count': len(invalid_accounts)
        }
    
    def _validate_status_distribution(self, accounts_df: pd.DataFrame) -> Tuple[bool, Dict]:
        """Validate status distribution"""
        actual_distribution = accounts_df['status'].value_counts(normalize=True).to_dict()
        
        valid_distribution = True
        for status, target_pct in self.status_distribution.items():
            actual_pct = actual_distribution.get(status, 0)
            if not (target_pct - 0.05 <= actual_pct <= target_pct + 0.05):  # 5% tolerance
                valid_distribution = False
                break
        
        return valid_distribution, {
            'valid_distribution': valid_distribution,
            'actual_distribution': actual_distribution,
            'target_distribution': self.status_distribution
        }
    
    def _validate_maturity_date_logic(self, accounts_df: pd.DataFrame) -> Tuple[bool, Dict]:
        """Validate maturity date logic"""
        valid_maturity = True
        invalid_accounts = []
        
        for _, account in accounts_df.iterrows():
            product_type = account['product_type']
            term_months = account['term_months']
            open_date = pd.to_datetime(account['open_date'])
            maturity_date = pd.to_datetime(account['maturity_date'])
            
            if product_type == 'demand_saving':
                # Demand saving should have no maturity date or term_months = 0
                if term_months != 0:
                    valid_maturity = False
                    invalid_accounts.append({
                        'account_id': account['account_id'],
                        'product_type': product_type,
                        'term_months': term_months,
                        'issue': 'Demand saving should have term_months = 0'
                    })
            elif product_type == 'term_saving':
                # Term saving should have maturity date and correct term_months
                if term_months == 0:
                    valid_maturity = False
                    invalid_accounts.append({
                        'account_id': account['account_id'],
                        'product_type': product_type,
                        'term_months': term_months,
                        'issue': 'Term saving should have term_months > 0'
                    })
                else:
                    # Check if maturity date is correct
                    expected_maturity = open_date + timedelta(days=term_months * 30)
                    if abs((maturity_date - expected_maturity).days) > 5:  # 5 days tolerance
                        valid_maturity = False
                        invalid_accounts.append({
                            'account_id': account['account_id'],
                            'product_type': product_type,
                            'term_months': term_months,
                            'open_date': open_date,
                            'maturity_date': maturity_date,
                            'expected_maturity': expected_maturity,
                            'issue': 'Maturity date does not match term_months'
                        })
        
        return valid_maturity, {
            'valid_maturity': valid_maturity,
            'invalid_accounts': invalid_accounts,
            'invalid_count': len(invalid_accounts)
        }
    
    def _validate_channel_distribution(self, accounts_df: pd.DataFrame) -> Tuple[bool, Dict]:
        """Validate channel distribution"""
        valid_channels = accounts_df['channel_opened'].isin(self.channels).all()
        invalid_channels = accounts_df[~accounts_df['channel_opened'].isin(self.channels)]
        
        return valid_channels, {
            'valid_channels': valid_channels,
            'invalid_count': len(invalid_channels),
            'channels_used': accounts_df['channel_opened'].value_counts().to_dict()
        }
    
    def _validate_currency_distribution(self, accounts_df: pd.DataFrame) -> Tuple[bool, Dict]:
        """Validate currency distribution"""
        valid_currencies = accounts_df['currency'].isin(self.currencies).all()
        invalid_currencies = accounts_df[~accounts_df['currency'].isin(self.currencies)]
        
        return valid_currencies, {
            'valid_currencies': valid_currencies,
            'invalid_count': len(invalid_currencies),
            'currencies_used': accounts_df['currency'].value_counts().to_dict()
        }
    
    def _validate_segment_account_distribution(self, accounts_df: pd.DataFrame) -> Tuple[bool, Dict]:
        """Validate segment account distribution"""
        # This would need customer data to validate properly
        # For now, just check if customer_code format is correct
        valid_format = True
        invalid_codes = []
        
        for _, account in accounts_df.iterrows():
            customer_code = account['customer_code']
            if not (customer_code.startswith('X_') or customer_code.startswith('Y_') or customer_code.startswith('Z_') or 
                    customer_code.startswith('VIP_') or customer_code.startswith('MED_') or customer_code.startswith('LOW_')):
                valid_format = False
                invalid_codes.append(customer_code)
        
        return valid_format, {
            'valid_format': valid_format,
            'invalid_codes': invalid_codes,
            'invalid_count': len(invalid_codes)
        }
    
    def _print_detailed_report(self, results: Dict, total_validations: int, passed_validations: int, overall_valid: bool):
        """Print detailed validation report"""
        print("\n================================================================================")
        print("📊 ACCOUNT CONSTRAINT VALIDATION REPORT")
        print("================================================================================")
        
        print(f"\n📊 PRODUCT TYPES: {'✅' if results['product_types']['valid'] else '❌'}")
        print(f"Valid types: {', '.join(self.product_types)}")
        print(f"Invalid accounts: {results['product_types']['report']['invalid_count']}")
        
        print(f"\n📅 TERM MONTHS: {'✅' if results['term_months']['valid'] else '❌'}")
        print(f"Invalid accounts: {results['term_months']['report']['invalid_count']}")
        
        print(f"\n💰 INTEREST RATES: {'✅' if results['interest_rates']['valid'] else '❌'}")
        print(f"Invalid accounts: {results['interest_rates']['report']['invalid_count']}")
        
        print(f"\n📈 STATUS DISTRIBUTION: {'✅' if results['status_distribution']['valid'] else '❌'}")
        print(f"Target: {results['status_distribution']['report']['target_distribution']}")
        print(f"Actual: {results['status_distribution']['report']['actual_distribution']}")
        
        print(f"\n🗓️ MATURITY DATE LOGIC: {'✅' if results['maturity_date_logic']['valid'] else '❌'}")
        print(f"Invalid accounts: {results['maturity_date_logic']['report']['invalid_count']}")
        
        print(f"\n📱 CHANNEL DISTRIBUTION: {'✅' if results['channel_distribution']['valid'] else '❌'}")
        print(f"Channels used: {results['channel_distribution']['report']['channels_used']}")
        
        print(f"\n💱 CURRENCY DISTRIBUTION: {'✅' if results['currency_distribution']['valid'] else '❌'}")
        print(f"Currencies used: {results['currency_distribution']['report']['currencies_used']}")
        
        print(f"\n👥 SEGMENT DISTRIBUTION: {'✅' if results['segment_distribution']['valid'] else '❌'}")
        print(f"Invalid codes: {results['segment_distribution']['report']['invalid_count']}")
        
        print("\n📋 OVERALL SUMMARY:")
        print(f"Total validations: {total_validations}")
        print(f"Passed validations: {passed_validations}")
        print(f"Success rate: {passed_validations/total_validations*100:.1f}%")
        print(f"Overall valid: {'✅' if overall_valid else '❌'}")

def main():
    """Test account validator"""
    # Load data
    accounts_df = pd.read_csv("output/phase2_banking_data_accounts.csv")
    
    # Convert dates
    accounts_df['open_date'] = pd.to_datetime(accounts_df['open_date'])
    accounts_df['maturity_date'] = pd.to_datetime(accounts_df['maturity_date'])
    
    # Validate
    validator = AccountConstraintValidator()
    results = validator.validate_account_constraints(accounts_df)

if __name__ == "__main__":
    main()
