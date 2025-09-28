"""
Customer Constraint Validator
Validator chuyên biệt cho customer constraints
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple
import numpy as np

class CustomerConstraintValidator:
    """Validator chuyên biệt cho customer constraints"""
    
    def __init__(self):
        # Customer constraints theo yêu cầu
        self.genders = ['Nam', 'Nữ']
        self.marital_statuses = ['Độc thân', 'Kết hôn']
        self.nationalities = ['Việt Nam', 'Nước ngoài']
        self.occupations = [
            'Nhân viên văn phòng',
            'Kinh doanh cá thể', 
            'Công nhân / lao động phổ thông',
            'Quản lý / chuyên gia',
            'Khác (sinh viên, nội trợ…)'
        ]
        self.income_ranges = ['<10 triệu', '10-20 triệu', '20-50 triệu', '>50 triệu']
        self.income_currencies = ['VND', 'USD']
        self.sources_of_income = ['Lương', 'Kinh doanh', 'Đầu tư', 'Khác']
        self.statuses = ['Active', 'Inactive', 'Closed']
        
        # Target distributions
        self.nationality_distribution = {'Việt Nam': 0.98, 'Nước ngoài': 0.02}
        self.status_distribution = {'Active': 0.80, 'Inactive': 0.15, 'Closed': 0.05}
        
        # Age groups
        self.age_groups = ['<25', '25-40', '40-55', '>55']
        
        # Segment-based income expectations
        self.segment_income_expectations = {
            'X': ['20-50 triệu', '>50 triệu'],  # VIP customers
            'Y': ['10-20 triệu', '20-50 triệu'],  # MEDIUM customers
            'Z': ['<10 triệu', '10-20 triệu']  # LOW customers
        }
        
    def validate_customer_constraints(self, customers_df: pd.DataFrame) -> Dict[str, Any]:
        """Validate tất cả customer constraints"""
        
        print("🔍 CUSTOMER CONSTRAINT VALIDATION")
        print("================================================================================")
        print(f"📁 Loading customers data...")
        print(f"   ✅ Loaded {len(customers_df):,} customers")
        
        results = {}
        overall_valid = True
        passed_validations = 0
        total_validations = 0
        
        # 1. Validate Demographics
        print("\n👥 Validating demographics...")
        demo_valid, demo_report = self._validate_demographics(customers_df)
        results['demographics'] = {'valid': demo_valid, 'report': demo_report}
        overall_valid &= demo_valid
        total_validations += 1
        if demo_valid: passed_validations += 1
        
        # 2. Validate Income Ranges
        print("\n💰 Validating income ranges...")
        income_valid, income_report = self._validate_income_ranges(customers_df)
        results['income_ranges'] = {'valid': income_valid, 'report': income_report}
        overall_valid &= income_valid
        total_validations += 1
        if income_valid: passed_validations += 1
        
        # 3. Validate Status Distribution
        print("\n📈 Validating status distribution...")
        status_valid, status_report = self._validate_status_distribution(customers_df)
        results['status_distribution'] = {'valid': status_valid, 'report': status_report}
        overall_valid &= status_valid
        total_validations += 1
        if status_valid: passed_validations += 1
        
        # 4. Validate Age Distribution
        print("\n🎂 Validating age distribution...")
        age_valid, age_report = self._validate_age_distribution(customers_df)
        results['age_distribution'] = {'valid': age_valid, 'report': age_report}
        overall_valid &= age_valid
        total_validations += 1
        if age_valid: passed_validations += 1
        
        # 5. Validate Segment Income Mapping
        print("\n🎯 Validating segment income mapping...")
        segment_income_valid, segment_income_report = self._validate_segment_income_mapping(customers_df)
        results['segment_income_mapping'] = {'valid': segment_income_valid, 'report': segment_income_report}
        overall_valid &= segment_income_valid
        total_validations += 1
        if segment_income_valid: passed_validations += 1
        
        # 6. Validate Data Consistency
        print("\n🔗 Validating data consistency...")
        consistency_valid, consistency_report = self._validate_data_consistency(customers_df)
        results['data_consistency'] = {'valid': consistency_valid, 'report': consistency_report}
        overall_valid &= consistency_valid
        total_validations += 1
        if consistency_valid: passed_validations += 1
        
        # Print detailed report
        self._print_detailed_report(results, total_validations, passed_validations, overall_valid)
        
        return results
    
    def _validate_demographics(self, customers_df: pd.DataFrame) -> Tuple[bool, Dict]:
        """Validate demographics"""
        valid_genders = customers_df['gender'].isin(self.genders).all()
        valid_marital = customers_df['marital_status'].isin(self.marital_statuses).all()
        valid_nationality = customers_df['nationality'].isin(self.nationalities).all()
        valid_occupation = customers_df['occupation'].isin(self.occupations).all()
        
        return (valid_genders and valid_marital and valid_nationality and valid_occupation), {
            'valid_genders': valid_genders,
            'valid_marital': valid_marital,
            'valid_nationality': valid_nationality,
            'valid_occupation': valid_occupation,
            'gender_distribution': customers_df['gender'].value_counts().to_dict(),
            'marital_distribution': customers_df['marital_status'].value_counts().to_dict(),
            'nationality_distribution': customers_df['nationality'].value_counts(normalize=True).to_dict(),
            'occupation_distribution': customers_df['occupation'].value_counts().to_dict()
        }
    
    def _validate_income_ranges(self, customers_df: pd.DataFrame) -> Tuple[bool, Dict]:
        """Validate income ranges"""
        valid_income_ranges = customers_df['income_range'].isin(self.income_ranges).all()
        valid_income_currency = customers_df['income_currency'].isin(self.income_currencies).all()
        valid_source = customers_df['source_of_income'].isin(self.sources_of_income).all()
        
        return (valid_income_ranges and valid_income_currency and valid_source), {
            'valid_income_ranges': valid_income_ranges,
            'valid_income_currency': valid_income_currency,
            'valid_source': valid_source,
            'income_range_distribution': customers_df['income_range'].value_counts().to_dict(),
            'income_currency_distribution': customers_df['income_currency'].value_counts().to_dict(),
            'source_distribution': customers_df['source_of_income'].value_counts().to_dict()
        }
    
    def _validate_status_distribution(self, customers_df: pd.DataFrame) -> Tuple[bool, Dict]:
        """Validate status distribution"""
        actual_distribution = customers_df['status'].value_counts(normalize=True).to_dict()
        
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
    
    def _validate_age_distribution(self, customers_df: pd.DataFrame) -> Tuple[bool, Dict]:
        """Validate age distribution"""
        # Convert DOB to age
        customers_df_copy = customers_df.copy()
        customers_df_copy['dob'] = pd.to_datetime(customers_df_copy['dob'])
        customers_df_copy['age'] = (datetime.now() - customers_df_copy['dob']).dt.days // 365
        
        # Check age ranges
        valid_ages = (customers_df_copy['age'] >= 18) & (customers_df_copy['age'] <= 100)
        age_distribution = {}
        
        for age_group in self.age_groups:
            if age_group == '<25':
                count = ((customers_df_copy['age'] < 25) & valid_ages).sum()
            elif age_group == '25-40':
                count = ((customers_df_copy['age'] >= 25) & (customers_df_copy['age'] <= 40) & valid_ages).sum()
            elif age_group == '40-55':
                count = ((customers_df_copy['age'] >= 40) & (customers_df_copy['age'] <= 55) & valid_ages).sum()
            else:  # >55
                count = ((customers_df_copy['age'] > 55) & valid_ages).sum()
            age_distribution[age_group] = count
        
        return valid_ages.all(), {
            'valid_ages': valid_ages.all(),
            'age_distribution': age_distribution,
            'age_stats': {
                'min': customers_df_copy['age'].min(),
                'max': customers_df_copy['age'].max(),
                'mean': customers_df_copy['age'].mean()
            }
        }
    
    def _validate_segment_income_mapping(self, customers_df: pd.DataFrame) -> Tuple[bool, Dict]:
        """Validate segment income mapping"""
        valid_mapping = True
        invalid_customers = []
        
        for _, customer in customers_df.iterrows():
            segment = customer['customer_segment']
            income_range = customer['income_range']
            
            expected_income_ranges = self.segment_income_expectations.get(segment, [])
            if expected_income_ranges and income_range not in expected_income_ranges:
                valid_mapping = False
                invalid_customers.append({
                    'customer_code': customer['customer_code'],
                    'segment': segment,
                    'income_range': income_range,
                    'expected_ranges': expected_income_ranges
                })
        
        return valid_mapping, {
            'valid_mapping': valid_mapping,
            'invalid_customers': invalid_customers,
            'invalid_count': len(invalid_customers)
        }
    
    def _validate_data_consistency(self, customers_df: pd.DataFrame) -> Tuple[bool, Dict]:
        """Validate data consistency"""
        # Check for missing values
        missing_values = customers_df.isnull().sum().to_dict()
        has_missing = any(count > 0 for count in missing_values.values())
        
        # Check for duplicate customer codes
        duplicate_codes = customers_df['customer_code'].duplicated().sum()
        has_duplicates = duplicate_codes > 0
        
        # Check for invalid dates
        customers_df_copy = customers_df.copy()
        customers_df_copy['dob'] = pd.to_datetime(customers_df_copy['dob'], errors='coerce')
        invalid_dates = customers_df_copy['dob'].isnull().sum()
        has_invalid_dates = invalid_dates > 0
        
        return not (has_missing or has_duplicates or has_invalid_dates), {
            'missing_values': missing_values,
            'duplicate_codes': duplicate_codes,
            'invalid_dates': invalid_dates,
            'has_missing': has_missing,
            'has_duplicates': has_duplicates,
            'has_invalid_dates': has_invalid_dates
        }
    
    def _print_detailed_report(self, results: Dict, total_validations: int, passed_validations: int, overall_valid: bool):
        """Print detailed validation report"""
        print("\n================================================================================")
        print("📊 CUSTOMER CONSTRAINT VALIDATION REPORT")
        print("================================================================================")
        
        print(f"\n👥 DEMOGRAPHICS: {'✅' if results['demographics']['valid'] else '❌'}")
        print(f"Genders: {results['demographics']['report']['gender_distribution']}")
        print(f"Marital: {results['demographics']['report']['marital_distribution']}")
        print(f"Nationality: {results['demographics']['report']['nationality_distribution']}")
        print(f"Occupation: {results['demographics']['report']['occupation_distribution']}")
        
        print(f"\n💰 INCOME RANGES: {'✅' if results['income_ranges']['valid'] else '❌'}")
        print(f"Income ranges: {results['income_ranges']['report']['income_range_distribution']}")
        print(f"Currencies: {results['income_ranges']['report']['income_currency_distribution']}")
        print(f"Sources: {results['income_ranges']['report']['source_distribution']}")
        
        print(f"\n📈 STATUS DISTRIBUTION: {'✅' if results['status_distribution']['valid'] else '❌'}")
        print(f"Target: {results['status_distribution']['report']['target_distribution']}")
        print(f"Actual: {results['status_distribution']['report']['actual_distribution']}")
        
        print(f"\n🎂 AGE DISTRIBUTION: {'✅' if results['age_distribution']['valid'] else '❌'}")
        print(f"Age groups: {results['age_distribution']['report']['age_distribution']}")
        print(f"Age stats: {results['age_distribution']['report']['age_stats']}")
        
        print(f"\n🎯 SEGMENT INCOME MAPPING: {'✅' if results['segment_income_mapping']['valid'] else '❌'}")
        print(f"Invalid customers: {results['segment_income_mapping']['report']['invalid_count']}")
        
        print(f"\n🔗 DATA CONSISTENCY: {'✅' if results['data_consistency']['valid'] else '❌'}")
        print(f"Missing values: {results['data_consistency']['report']['missing_values']}")
        print(f"Duplicate codes: {results['data_consistency']['report']['duplicate_codes']}")
        print(f"Invalid dates: {results['data_consistency']['report']['invalid_dates']}")
        
        print("\n📋 OVERALL SUMMARY:")
        print(f"Total validations: {total_validations}")
        print(f"Passed validations: {passed_validations}")
        print(f"Success rate: {passed_validations/total_validations*100:.1f}%")
        print(f"Overall valid: {'✅' if overall_valid else '❌'}")

def main():
    """Test customer validator"""
    # Load data
    customers_df = pd.read_csv("output/phase3_banking_data_customers.csv")
    
    # Convert dates
    customers_df['dob'] = pd.to_datetime(customers_df['dob'])
    
    # Validate
    validator = CustomerConstraintValidator()
    results = validator.validate_customer_constraints(customers_df)

if __name__ == "__main__":
    main()
