"""
Test Configuration cho Banking Data Generator
Cấu hình các tham số test và constants
"""

from dataclasses import dataclass
from typing import Dict, Tuple
from datetime import datetime, timedelta

@dataclass
class TestConfig:
    """Configuration cho test cases"""
    
    # Dataset sizes
    SMALL_DATASET: int = 100
    MEDIUM_DATASET: int = 1000
    LARGE_DATASET: int = 10000
    
    # Customer segment distribution (X=50%, Y=30%, Z=20%)
    SEGMENT_DISTRIBUTION: Dict[str, float] = {
        'VIP': 0.50,
        'MEDIUM': 0.30, 
        'LOW': 0.20
    }
    
    # RFM Constraints cho từng segment
    RFM_CONSTRAINTS: Dict[str, Dict] = {
        'VIP': {
            'frequency_range': (6, 8),  # transactions per month
            'amount_min': 50_000_000,   # VND
            'recency_days': 30,         # within 30 days
            'description': 'High frequency, high value, recent'
        },
        'MEDIUM': {
            'frequency_range': (3, 4),  # transactions per month
            'amount_min': 30_000_000,   # VND
            'recency_days': (60, 180),  # 2-6 months
            'description': 'Medium frequency, medium value, moderate recency'
        },
        'LOW': {
            'frequency_range': (2, 3),  # transactions per month
            'amount_min': 5_000_000,    # VND
            'amount_max': 20_000_000,   # VND
            'recency_days': 180,        # >6 months
            'description': 'Low frequency, low value, old'
        }
    }
    
    # Transaction types và patterns
    TRANSACTION_TYPES = ['DEPOSIT', 'WITHDRAWAL', 'INTEREST', 'FEE']
    CHANNEL_TXN = ['MOBILE', 'ATM', 'BRANCH', 'ONLINE', 'QR_CODE']
    STATUS_TXN = ['SUCCESS', 'PENDING', 'FAILED']
    
    # Account settings
    TERM_MONTHS = [1, 3]  # 1 tháng hoặc 3 tháng
    INTEREST_RATES = {
        1: 0.05,  # 5% per annum
        3: 0.06   # 6% per annum
    }
    PRODUCT_TYPES = ['TERM_SAVING', 'DEMAND_SAVING']
    
    # Customer demographics
    CITIES = ['HCM', 'HN', 'DN', 'HP', 'CT', 'BD', 'VT', 'KH']
    GENDERS = ['M', 'F']
    MARITAL_STATUS = ['SINGLE', 'MARRIED', 'DIVORCED', 'WIDOWED']
    OCCUPATIONS = {
        'VIP': ['CEO', 'DIRECTOR', 'MANAGER', 'DOCTOR', 'LAWYER', 'ENGINEER'],
        'MEDIUM': ['TEACHER', 'NURSE', 'ACCOUNTANT', 'SALES', 'TECHNICIAN'],
        'LOW': ['WORKER', 'FARMER', 'STUDENT', 'RETIRED', 'UNEMPLOYED']
    }
    INCOME_RANGES = {
        'VIP': '50-200tr',
        'MEDIUM': '10-50tr', 
        'LOW': '5-20tr'
    }
    
    # Date ranges
    START_DATE = datetime(2023, 1, 1)
    END_DATE = datetime(2024, 12, 31)
    
    # Currency settings
    CURRENCIES = ['VND', 'USD', 'EUR']
    DEFAULT_CURRENCY = 'VND'
    
    # Test tolerance
    DISTRIBUTION_TOLERANCE = 0.05  # 5% tolerance cho distribution tests
    BALANCE_TOLERANCE = 0.01       # 1% tolerance cho balance calculations

# Global test config instance
test_config = TestConfig()
