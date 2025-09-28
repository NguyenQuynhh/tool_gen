"""
Test Configuration
Configuration cho banking data generator
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple
from datetime import datetime, timedelta

@dataclass
class test_config:
    """Configuration cho test cases và generators"""
    
    # Dataset sizes
    SMALL_DATASET: int = 100
    MEDIUM_DATASET: int = 1000
    LARGE_DATASET: int = 10000
    
    # Segment distribution
    SEGMENT_DISTRIBUTION: Dict[str, float] = field(default_factory=lambda: {
        'VIP': 0.20,
        'MEDIUM': 0.30,
        'LOW': 0.50
    })
    
    # RFM constraints
    RFM_CONSTRAINTS: Dict[str, Dict] = field(default_factory=lambda: {
        'VIP': {
            'frequency_range': (6, 8),
            'amount_min': 50_000_000,
            'recency_days': 30,
            'description': 'High frequency, high value, recent'
        },
        'MEDIUM': {
            'frequency_range': (3, 4),
            'amount_min': 30_000_000,
            'recency_days': 180,
            'description': 'Medium frequency, medium value, moderate recency'
        },
        'LOW': {
            'frequency_range': (2, 3),
            'amount_min': 5_000_000,
            'recency_days': 365,
            'description': 'Low frequency, low value, old'
        }
    })
    
    # Transaction types
    TRANSACTION_TYPES: list = field(default_factory=lambda: ['DEPOSIT', 'WITHDRAWAL', 'INTEREST', 'FEE'])
    
    # Channel transaction
    CHANNEL_TXN: list = field(default_factory=lambda: ['MOBILE', 'ATM', 'BRANCH', 'ONLINE'])
    
    # Status transaction
    STATUS_TXN: list = field(default_factory=lambda: ['SUCCESS', 'FAILED', 'PENDING'])
    
    # Term months
    TERM_MONTHS: list = field(default_factory=lambda: [3, 6, 12, 24, 36])
    
    # Interest rates by term
    INTEREST_RATES: Dict[int, float] = field(default_factory=lambda: {
        3: 0.05,
        6: 0.06,
        12: 0.07,
        24: 0.08,
        36: 0.09
    })
    
    # Product types by segment
    PRODUCT_TYPES: Dict[str, list] = field(default_factory=lambda: {
        'VIP': ['PREMIUM_SAVINGS', 'VIP_TERM_DEPOSIT'],
        'MEDIUM': ['STANDARD_SAVINGS', 'TERM_DEPOSIT'],
        'LOW': ['BASIC_SAVINGS']
    })
    
    # Cities
    CITIES: list = field(default_factory=lambda: [
        'Hà Nội', 'TP.HCM', 'Đà Nẵng', 'Hải Phòng', 'Cần Thơ',
        'An Giang', 'Bà Rịa - Vũng Tàu', 'Bắc Giang', 'Bắc Kạn',
        'Bạc Liêu', 'Bắc Ninh', 'Bến Tre', 'Bình Định', 'Bình Dương',
        'Bình Phước', 'Bình Thuận', 'Cà Mau', 'Cao Bằng', 'Đắk Lắk',
        'Đắk Nông', 'Điện Biên', 'Đồng Nai', 'Đồng Tháp', 'Gia Lai',
        'Hà Giang', 'Hà Nam', 'Hà Tĩnh', 'Hải Dương', 'Hậu Giang',
        'Hòa Bình', 'Hưng Yên', 'Khánh Hòa', 'Kiên Giang', 'Kon Tum',
        'Lai Châu', 'Lâm Đồng', 'Lạng Sơn', 'Lào Cai', 'Long An',
        'Nam Định', 'Nghệ An', 'Ninh Bình', 'Ninh Thuận', 'Phú Thọ',
        'Phú Yên', 'Quảng Bình', 'Quảng Nam', 'Quảng Ngãi', 'Quảng Ninh',
        'Quảng Trị', 'Sóc Trăng', 'Sơn La', 'Tây Ninh', 'Thái Bình',
        'Thái Nguyên', 'Thanh Hóa', 'Thừa Thiên Huế', 'Tiền Giang',
        'Trà Vinh', 'Tuyên Quang', 'Vĩnh Long', 'Vĩnh Phúc', 'Yên Bái'
    ])
    
    # Genders
    GENDERS: list = field(default_factory=lambda: ['M', 'F'])
    
    # Marital status
    MARITAL_STATUS: list = field(default_factory=lambda: ['SINGLE', 'MARRIED', 'DIVORCED', 'WIDOWED'])
    
    # Occupations
    OCCUPATIONS: list = field(default_factory=lambda: [
        'BUSINESS_OWNER', 'MANAGER', 'PROFESSIONAL', 'OFFICE_WORKER',
        'TECHNICIAN', 'SERVICE_WORKER', 'STUDENT', 'RETIRED', 'UNEMPLOYED'
    ])
    
    # Income ranges
    INCOME_RANGES: list = field(default_factory=lambda: ['5-20tr', '10-50tr', '50-200tr'])
    
    # Currencies
    CURRENCIES: list = field(default_factory=lambda: ['VND', 'USD', 'EUR'])
    DEFAULT_CURRENCY: str = 'VND'
    
    # Date ranges
    START_DATE: datetime = datetime(2023, 1, 1)
    END_DATE: datetime = datetime(2024, 12, 31)
    
    # Account settings
    MIN_ACCOUNTS_PER_CUSTOMER: int = 1
    MAX_ACCOUNTS_PER_CUSTOMER: int = 5
    
    # Transaction settings
    MIN_TRANSACTIONS_PER_ACCOUNT: int = 5
    MAX_TRANSACTIONS_PER_ACCOUNT: int = 50
    
    # Amount ranges by segment
    AMOUNT_RANGES: Dict[str, Tuple[int, int]] = field(default_factory=lambda: {
        'VIP': (50_000_000, 500_000_000),
        'MEDIUM': (30_000_000, 200_000_000),
        'LOW': (5_000_000, 50_000_000)
    })
    
    # Frequency ranges by segment
    FREQUENCY_RANGES: Dict[str, Tuple[int, int]] = field(default_factory=lambda: {
        'VIP': (6, 12),
        'MEDIUM': (3, 6),
        'LOW': (1, 3)
    })
