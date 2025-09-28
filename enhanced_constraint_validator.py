"""
Enhanced Constraint Validator
Kiểm tra tất cả constraints theo yêu cầu mới
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import numpy as np

class EnhancedConstraintValidator:
    """Enhanced validator cho tất cả constraints"""
    
    def __init__(self):
        # Target segment distribution
        self.target_distribution = {
            'X': 0.20,  # 20%
            'Y': 0.30,  # 30%
            'Z': 0.50   # 50%
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
        
        # Transaction type constraints
        self.transaction_type_constraints = {
            'Interest Withdrawal': 'Rút lãi tiết kiệm',
            'Principal Withdrawal': 'Rút gốc tiết kiệm',
            'Deposit': 'Gửi tiền tiết kiệm',
            'Fund Transfer': 'Chuyển tiền từ tài khoản thanh toán',
            'Fee Transaction': 'Thu phí dịch vụ ngân hàng'
        }
        
        # Account constraints
        self.account_constraints = {
            'product_types': ['demand_saving', 'term_saving'],
            'term_months': [0, 1, 3, 6, 9, 12, 24, 36],
            'status_distribution': {'active': 0.82, 'closed': 0.12, 'suspend': 0.06}
        }
        
        # Customer constraints
        self.customer_constraints = {
            'genders': ['Nam', 'Nữ'],
            'marital_status': ['Độc thân', 'Kết hôn'],
            'nationality': ['Việt Nam', 'Nước ngoài'],
            'income_ranges': ['<10 triệu', '10-20 triệu', '20-50 triệu', '>50 triệu'],
            'status_distribution': {'Active': 0.80, 'Inactive': 0.15, 'Closed': 0.05}
        }
    
    def validate_all_constraints(self, 
                               transactions_file: str,
                               accounts_file: str,
                               customers_file: str) -> Dict:
        """Validate tất cả constraints"""
        
        print("🔍 ENHANCED CONSTRAINT VALIDATION")
        print("=" * 80)
        
        # Load data
        print("📁 Loading data...")
        transactions_df = pd.read_csv(transactions_file)
        accounts_df = pd.read_csv(accounts_file)
        customers_df = pd.read_csv(customers_file)
        
        print(f"   ✅ Loaded {len(transactions_df):,} transactions")
        print(f"   ✅ Loaded {len(accounts_df):,} accounts")
        print(f"   ✅ Loaded {len(customers_df):,} customers")
        
        # Convert dates
        transactions_df['transaction_date'] = pd.to_datetime(transactions_df['transaction_date'])
        accounts_df['open_date'] = pd.to_datetime(accounts_df['open_date'])
        accounts_df['maturity_date'] = pd.to_datetime(accounts_df['maturity_date'])
        customers_df['dob'] = pd.to_datetime(customers_df['dob'])
        
        # Validate all constraints
        validation_results = {
            'segment_distribution': self._validate_segment_distribution(customers_df),
            'transaction_types': self._validate_transaction_types(transactions_df),
            'transaction_logic': self._validate_transaction_logic(transactions_df, accounts_df),
            'account_constraints': self._validate_account_constraints(accounts_df),
            'customer_constraints': self._validate_customer_constraints(customers_df),
            'rfm_constraints': self._validate_rfm_constraints(transactions_df, customers_df),
            'data_consistency': self._validate_data_consistency(transactions_df, accounts_df, customers_df)
        }
        
        # Generate summary
        validation_results['summary'] = self._generate_validation_summary(validation_results)
        
        return validation_results
    
    def _validate_segment_distribution(self, customers_df: pd.DataFrame) -> Dict:
        """Validate segment distribution"""
        print("\n📊 Validating segment distribution...")
        
        # Customer segments are already in X, Y, Z format
        customers_df_mapped = customers_df.copy()
        
        segment_counts = customers_df_mapped['customer_segment'].value_counts()
        total_customers = len(customers_df_mapped)
        
        actual_distribution = {}
        for segment in ['X', 'Y', 'Z']:
            count = segment_counts.get(segment, 0)
            actual_distribution[segment] = count / total_customers
        
        # Check if within tolerance (5%)
        tolerance = 0.05
        is_valid = True
        differences = {}
        
        for segment in ['X', 'Y', 'Z']:
            diff = abs(actual_distribution[segment] - self.target_distribution[segment])
            differences[segment] = diff
            if diff > tolerance:
                is_valid = False
        
        return {
            'target': self.target_distribution,
            'actual': actual_distribution,
            'differences': differences,
            'is_valid': is_valid,
            'tolerance': tolerance
        }
    
    def _validate_transaction_types(self, transactions_df: pd.DataFrame) -> Dict:
        """Validate transaction types"""
        print("\n💳 Validating transaction types...")
        
        # Check if all transaction types are valid
        valid_types = list(self.transaction_type_constraints.keys())
        actual_types = transactions_df['transaction_type'].unique()
        
        invalid_types = [t for t in actual_types if t not in valid_types]
        missing_types = [t for t in valid_types if t not in actual_types]
        
        # Check transaction descriptions
        desc_matches = 0
        total_transactions = len(transactions_df)
        
        for _, row in transactions_df.iterrows():
            expected_desc = self.transaction_type_constraints.get(row['transaction_type'], '')
            if expected_desc in row['transaction_desc']:
                desc_matches += 1
        
        desc_accuracy = desc_matches / total_transactions if total_transactions > 0 else 0
        
        return {
            'valid_types': valid_types,
            'actual_types': actual_types.tolist(),
            'invalid_types': invalid_types,
            'missing_types': missing_types,
            'is_valid': len(invalid_types) == 0,
            'desc_accuracy': desc_accuracy
        }
    
    def _validate_transaction_logic(self, transactions_df: pd.DataFrame, accounts_df: pd.DataFrame) -> Dict:
        """Validate transaction logic (gần open_date → Deposit, gần maturity_date → Withdrawal)"""
        print("\n🔄 Validating transaction logic...")
        
        # Merge with account data
        merged_df = transactions_df.merge(accounts_df[['account_id', 'open_date', 'maturity_date', 'product_type']], on='account_id')
        
        # Calculate transaction position in account lifecycle
        merged_df['days_from_open'] = (merged_df['transaction_date'] - merged_df['open_date']).dt.days
        merged_df['days_to_maturity'] = (merged_df['maturity_date'] - merged_df['transaction_date']).dt.days
        merged_df['total_days'] = (merged_df['maturity_date'] - merged_df['open_date']).dt.days
        
        # Check logic for each transaction
        logic_valid = 0
        total_checked = 0
        
        for _, row in merged_df.iterrows():
            total_checked += 1
            position = row['days_from_open'] / row['total_days'] if row['total_days'] > 0 else 0
            
            # Check if transaction type matches position
            if position < 0.2:  # Near open_date
                if row['transaction_type'] in ['Deposit', 'Fund Transfer']:
                    logic_valid += 1
            elif position > 0.8:  # Near maturity_date
                if row['transaction_type'] in ['Principal Withdrawal', 'Interest Withdrawal']:
                    logic_valid += 1
            else:  # Middle period
                logic_valid += 1  # Any type is valid in middle period
        
        logic_accuracy = logic_valid / total_checked if total_checked > 0 else 0
        
        return {
            'logic_accuracy': logic_accuracy,
            'is_valid': logic_accuracy > 0.7,  # 70% accuracy threshold
            'total_checked': total_checked,
            'logic_valid': logic_valid
        }
    
    def _validate_account_constraints(self, accounts_df: pd.DataFrame) -> Dict:
        """Validate account constraints"""
        print("\n🏦 Validating account constraints...")
        
        # Check product types
        valid_product_types = self.account_constraints['product_types']
        actual_product_types = accounts_df['product_type'].unique()
        product_types_valid = all(t in valid_product_types for t in actual_product_types)
        
        # Check term months
        valid_term_months = self.account_constraints['term_months']
        actual_term_months = accounts_df['term_months'].unique()
        term_months_valid = all(t in valid_term_months for t in actual_term_months)
        
        # Check status distribution
        status_counts = accounts_df['status'].value_counts()
        total_accounts = len(accounts_df)
        
        status_distribution = {}
        for status in ['active', 'closed', 'suspend']:
            count = status_counts.get(status, 0)
            status_distribution[status] = count / total_accounts
        
        # Check if status distribution is within tolerance
        status_valid = True
        for status, expected_ratio in self.account_constraints['status_distribution'].items():
            actual_ratio = status_distribution.get(status, 0)
            if abs(actual_ratio - expected_ratio) > 0.1:  # 10% tolerance
                status_valid = False
                break
        
        return {
            'product_types_valid': product_types_valid,
            'term_months_valid': term_months_valid,
            'status_distribution': status_distribution,
            'status_valid': status_valid,
            'is_valid': product_types_valid and term_months_valid and status_valid
        }
    
    def _validate_customer_constraints(self, customers_df: pd.DataFrame) -> Dict:
        """Validate customer constraints"""
        print("\n👥 Validating customer constraints...")
        
        # Check genders
        valid_genders = self.customer_constraints['genders']
        actual_genders = customers_df['gender'].unique()
        genders_valid = all(g in valid_genders for g in actual_genders)
        
        # Check marital status
        valid_marital = self.customer_constraints['marital_status']
        actual_marital = customers_df['marital_status'].unique()
        marital_valid = all(m in valid_marital for m in actual_marital)
        
        # Check income ranges
        valid_income = self.customer_constraints['income_ranges']
        actual_income = customers_df['income_range'].unique()
        income_valid = all(i in valid_income for i in actual_income)
        
        # Check status distribution
        status_counts = customers_df['status'].value_counts()
        total_customers = len(customers_df)
        
        status_distribution = {}
        for status in ['Active', 'Inactive', 'Closed']:
            count = status_counts.get(status, 0)
            status_distribution[status] = count / total_customers
        
        status_valid = True
        for status, expected_ratio in self.customer_constraints['status_distribution'].items():
            actual_ratio = status_distribution.get(status, 0)
            if abs(actual_ratio - expected_ratio) > 0.1:  # 10% tolerance
                status_valid = False
                break
        
        return {
            'genders_valid': genders_valid,
            'marital_valid': marital_valid,
            'income_valid': income_valid,
            'status_distribution': status_distribution,
            'status_valid': status_valid,
            'is_valid': genders_valid and marital_valid and income_valid and status_valid
        }
    
    def _validate_rfm_constraints(self, transactions_df: pd.DataFrame, customers_df: pd.DataFrame) -> Dict:
        """Validate RFM constraints"""
        print("\n📈 Validating RFM constraints...")
        
        # Calculate RFM metrics for each customer
        customer_rfm = self._calculate_customer_rfm(transactions_df)
        
        # Merge with customer segments
        customer_rfm = customer_rfm.merge(customers_df[['customer_code', 'customer_segment']], on='customer_code')
        
        # Customer segments are already in X, Y, Z format
        
        # Validate each segment
        segment_validation = {}
        for segment in ['X', 'Y', 'Z']:
            segment_customers = customer_rfm[customer_rfm['customer_segment'] == segment]
            constraints = self.rfm_constraints[segment]
            
            if len(segment_customers) == 0:
                segment_validation[segment] = {
                    'count': 0,
                    'compliance_rate': 0,
                    'is_valid': False
                }
                continue
            
            # Check frequency constraint
            freq_min, freq_max = constraints['frequency_per_month']
            freq_valid = ((segment_customers['frequency_per_month'] >= freq_min) & 
                         (segment_customers['frequency_per_month'] <= freq_max)).sum()
            
            # Check deposit amount constraint
            if 'deposit_amount_min' in constraints:
                deposit_valid = (segment_customers['deposit_max'] >= constraints['deposit_amount_min']).sum()
            else:
                deposit_valid = len(segment_customers)
            
            # Check recency constraint
            if 'recency_days_max' in constraints:
                recency_valid = (segment_customers['recency_days'] <= constraints['recency_days_max']).sum()
            elif 'recency_days_min' in constraints:
                recency_valid = (segment_customers['recency_days'] >= constraints['recency_days_min']).sum()
            else:
                recency_valid = len(segment_customers)
            
            # Calculate compliance - customers must meet ALL three criteria
            customers_meeting_all = 0
            for _, customer in segment_customers.iterrows():
                freq_ok = freq_min <= customer['frequency_per_month'] <= freq_max
                deposit_ok = customer['deposit_max'] >= constraints.get('deposit_amount_min', 0)
                recency_ok = True
                if 'recency_days_max' in constraints:
                    recency_ok = customer['recency_days'] <= constraints['recency_days_max']
                elif 'recency_days_min' in constraints:
                    recency_ok = customer['recency_days'] >= constraints['recency_days_min']
                
                if freq_ok and deposit_ok and recency_ok:
                    customers_meeting_all += 1
            
            compliance_rate = customers_meeting_all / len(segment_customers)
            
            segment_validation[segment] = {
                'count': len(segment_customers),
                'compliance_rate': compliance_rate,
                'is_valid': compliance_rate > 0.5,  # 50% compliance threshold
                'freq_valid': freq_valid,
                'deposit_valid': deposit_valid,
                'recency_valid': recency_valid
            }
        
        return segment_validation
    
    def _calculate_customer_rfm(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate RFM metrics for each customer"""
        
        # Group by customer
        customer_stats = transactions_df.groupby('customer_code').agg({
            'transaction_date': ['min', 'max', 'count'],
            'amount': 'sum',
            'account_id': 'nunique'
        }).reset_index()
        
        customer_stats.columns = ['customer_code', 'first_transaction', 'last_transaction', 'frequency', 'monetary', 'num_accounts']
        
        # Calculate recency (from last transaction to end of period)
        # Use end_date instead of now for proper recency calculation
        end_date = transactions_df['transaction_date'].max()
        customer_stats['recency_days'] = (end_date - customer_stats['last_transaction']).dt.days
        
        # Debug: Print recency statistics
        print(f"Recency stats: min={customer_stats['recency_days'].min()}, max={customer_stats['recency_days'].max()}, avg={customer_stats['recency_days'].mean():.0f}")
        
        # Calculate frequency per month
        customer_stats['duration_days'] = (customer_stats['last_transaction'] - customer_stats['first_transaction']).dt.days
        customer_stats['duration_months'] = customer_stats['duration_days'] / 30.44
        customer_stats['frequency_per_month'] = customer_stats['frequency'] / customer_stats['duration_months'].clip(lower=1)
        
        # Calculate deposit statistics
        deposit_stats = transactions_df[transactions_df['transaction_type'] == 'Deposit'].groupby('customer_code').agg({
            'amount': ['count', 'mean', 'max', 'min']
        }).reset_index()
        
        if len(deposit_stats) > 0:
            deposit_stats.columns = ['customer_code', 'deposit_count', 'deposit_avg', 'deposit_max', 'deposit_min']
        else:
            # Create empty dataframe with correct columns
            deposit_stats = pd.DataFrame(columns=['customer_code', 'deposit_count', 'deposit_avg', 'deposit_max', 'deposit_min'])
        
        # Merge deposit stats
        customer_rfm = customer_stats.merge(deposit_stats, on='customer_code', how='left')
        customer_rfm['deposit_count'] = customer_rfm['deposit_count'].fillna(0)
        customer_rfm['deposit_avg'] = customer_rfm['deposit_avg'].fillna(0)
        customer_rfm['deposit_max'] = customer_rfm['deposit_max'].fillna(0)
        customer_rfm['deposit_min'] = customer_rfm['deposit_min'].fillna(0)
        
        return customer_rfm
    
    def _validate_data_consistency(self, transactions_df: pd.DataFrame, accounts_df: pd.DataFrame, customers_df: pd.DataFrame) -> Dict:
        """Validate data consistency between tables"""
        print("\n🔗 Validating data consistency...")
        
        # Check customer_code consistency
        transaction_customers = set(transactions_df['customer_code'].unique())
        account_customers = set(accounts_df['customer_code'].unique())
        customer_codes = set(customers_df['customer_code'].unique())
        
        customer_consistency = len(transaction_customers - customer_codes) == 0 and len(account_customers - customer_codes) == 0
        
        # Check account_id consistency
        transaction_accounts = set(transactions_df['account_id'].unique())
        account_ids = set(accounts_df['account_id'].unique())
        
        account_consistency = len(transaction_accounts - account_ids) == 0
        
        # Check balance consistency
        balance_consistency = True
        balance_errors = 0
        total_accounts_checked = 0
        
        for _, account in accounts_df.iterrows():
            account_transactions = transactions_df[transactions_df['account_id'] == account['account_id']]
            if len(account_transactions) > 0:
                total_accounts_checked += 1
                
                # Calculate balance based on transaction types
                calculated_balance = 0
                for _, txn in account_transactions.iterrows():
                    if txn['transaction_type'] in ['Deposit', 'Fund Transfer']:
                        calculated_balance += txn['amount']
                    elif txn['transaction_type'] in ['Principal Withdrawal', 'Interest Withdrawal', 'Fee Transaction']:
                        calculated_balance -= txn['amount']
                
                # Check if calculated balance matches account balance
                if abs(calculated_balance - account['current_balance']) > 1000:  # 1000 VND tolerance
                    balance_errors += 1
                    if balance_errors > total_accounts_checked * 0.1:  # Allow 10% error rate
                        balance_consistency = False
                        break
        
        return {
            'customer_consistency': customer_consistency,
            'account_consistency': account_consistency,
            'balance_consistency': balance_consistency,
            'is_valid': customer_consistency and account_consistency and balance_consistency
        }
    
    def _generate_validation_summary(self, validation_results: Dict) -> Dict:
        """Generate validation summary"""
        
        total_validations = 0
        passed_validations = 0
        
        for key, result in validation_results.items():
            if key != 'summary' and isinstance(result, dict) and 'is_valid' in result:
                total_validations += 1
                if result['is_valid']:
                    passed_validations += 1
        
        overall_success_rate = passed_validations / total_validations if total_validations > 0 else 0
        
        return {
            'total_validations': total_validations,
            'passed_validations': passed_validations,
            'overall_success_rate': overall_success_rate,
            'is_overall_valid': overall_success_rate > 0.8  # 80% success rate threshold
        }
    
    def print_validation_report(self, validation_results: Dict):
        """Print detailed validation report"""
        
        print("\n" + "="*80)
        print("📊 ENHANCED CONSTRAINT VALIDATION REPORT")
        print("="*80)
        
        # Segment distribution
        dist_result = validation_results['segment_distribution']
        print(f"\n📈 SEGMENT DISTRIBUTION: {'✅' if dist_result['is_valid'] else '❌'}")
        print(f"Target: X={dist_result['target']['X']:.1%}, Y={dist_result['target']['Y']:.1%}, Z={dist_result['target']['Z']:.1%}")
        print(f"Actual: X={dist_result['actual']['X']:.1%}, Y={dist_result['actual']['Y']:.1%}, Z={dist_result['actual']['Z']:.1%}")
        
        # Transaction types
        txn_result = validation_results['transaction_types']
        print(f"\n💳 TRANSACTION TYPES: {'✅' if txn_result['is_valid'] else '❌'}")
        print(f"Valid types: {', '.join(txn_result['valid_types'])}")
        print(f"Description accuracy: {txn_result['desc_accuracy']:.1%}")
        
        # Transaction logic
        logic_result = validation_results['transaction_logic']
        print(f"\n🔄 TRANSACTION LOGIC: {'✅' if logic_result['is_valid'] else '❌'}")
        print(f"Logic accuracy: {logic_result['logic_accuracy']:.1%}")
        
        # Account constraints
        acc_result = validation_results['account_constraints']
        print(f"\n🏦 ACCOUNT CONSTRAINTS: {'✅' if acc_result['is_valid'] else '❌'}")
        print(f"Product types valid: {acc_result['product_types_valid']}")
        print(f"Term months valid: {acc_result['term_months_valid']}")
        print(f"Status distribution valid: {acc_result['status_valid']}")
        
        # Customer constraints
        cust_result = validation_results['customer_constraints']
        print(f"\n👥 CUSTOMER CONSTRAINTS: {'✅' if cust_result['is_valid'] else '❌'}")
        print(f"Genders valid: {cust_result['genders_valid']}")
        print(f"Marital status valid: {cust_result['marital_valid']}")
        print(f"Income ranges valid: {cust_result['income_valid']}")
        print(f"Status distribution valid: {cust_result['status_valid']}")
        
        # RFM constraints
        rfm_result = validation_results['rfm_constraints']
        print(f"\n📈 RFM CONSTRAINTS:")
        for segment, result in rfm_result.items():
            print(f"  {segment}: {'✅' if result['is_valid'] else '❌'} - {result['count']} customers - {result['compliance_rate']:.1%} compliance")
        
        # Data consistency
        consistency_result = validation_results['data_consistency']
        print(f"\n🔗 DATA CONSISTENCY: {'✅' if consistency_result['is_valid'] else '❌'}")
        print(f"Customer consistency: {consistency_result['customer_consistency']}")
        print(f"Account consistency: {consistency_result['account_consistency']}")
        print(f"Balance consistency: {consistency_result['balance_consistency']}")
        
        # Summary
        summary = validation_results['summary']
        print(f"\n📋 OVERALL SUMMARY:")
        print(f"Total validations: {summary['total_validations']}")
        print(f"Passed validations: {summary['passed_validations']}")
        print(f"Success rate: {summary['overall_success_rate']:.1%}")
        print(f"Overall valid: {'✅' if summary['is_overall_valid'] else '❌'}")

def main():
    """Test enhanced constraint validator"""
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python enhanced_constraint_validator.py <transactions_file> <accounts_file> <customers_file>")
        return 1
    
    transactions_file = sys.argv[1]
    accounts_file = sys.argv[2]
    customers_file = sys.argv[3]
    
    # Validate constraints
    validator = EnhancedConstraintValidator()
    results = validator.validate_all_constraints(transactions_file, accounts_file, customers_file)
    
    # Print report
    validator.print_validation_report(results)
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
