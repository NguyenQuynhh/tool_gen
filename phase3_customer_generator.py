"""
Phase 3 Customer Generator
Customer generator với tất cả constraints được sửa
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict
from dataclasses import dataclass
from test_config import test_config

@dataclass
class Phase3Customer:
    """Phase 3 customer model với tất cả constraints đúng"""
    customer_code: str
    full_name: str
    gender: str  # Nam, Nữ
    dob: datetime
    city: str
    marital_status: str  # Độc thân, Kết hôn
    nationality: str  # Việt Nam, Nước ngoài
    occupation: str  # Nhân viên văn phòng, Kinh doanh cá thể, etc.
    income_range: str  # <10 triệu, 10-20 triệu, 20-50 triệu, >50 triệu
    income_currency: str  # VND, USD
    source_of_income: str  # Lương, Kinh doanh, Đầu tư, Khác
    status: str  # Active(80%), Inactive(15%), Closed(5%)
    customer_segment: str  # X, Y, Z

class Phase3CustomerGenerator:
    """Phase 3 customer generator với tất cả constraints đúng"""
    
    def __init__(self, config: test_config = None):
        self.config = config or test_config()
        
        # Gender options
        self.genders = ['Nam', 'Nữ']
        
        # Marital status
        self.marital_status = ['Độc thân', 'Kết hôn']
        
        # Nationality (98% Vietnamese)
        self.nationality_distribution = {
            'Việt Nam': 0.98,
            'Nước ngoài': 0.02
        }
        
        # Occupation mapping by segment (corrected)
        self.occupation_by_segment = {
            'X': ['Quản lý / chuyên gia', 'Kinh doanh cá thể'],
            'Y': ['Nhân viên văn phòng', 'Quản lý / chuyên gia'],
            'Z': ['Nhân viên văn phòng', 'Công nhân / lao động phổ thông', 'Khác (sinh viên, nội trợ…)']
        }
        
        # Income ranges
        self.income_ranges = ['<10 triệu', '10-20 triệu', '20-50 triệu', '>50 triệu']
        
        # Income range mapping by segment
        self.income_by_segment = {
            'X': ['20-50 triệu', '>50 triệu'],
            'Y': ['10-20 triệu', '20-50 triệu'],
            'Z': ['<10 triệu', '10-20 triệu']
        }
        
        # Income currency distribution
        self.income_currency_distribution = {
            'VND': 0.95,
            'USD': 0.05
        }
        
        # Source of income mapping by segment
        self.source_by_segment = {
            'X': ['Lương', 'Kinh doanh', 'Đầu tư'],
            'Y': ['Lương', 'Kinh doanh'],
            'Z': ['Lương', 'Khác']
        }
        
        # Status distribution (corrected)
        self.status_distribution = {
            'Active': 0.80,
            'Inactive': 0.15,
            'Closed': 0.05
        }
        
        # Age groups (corrected to ensure min age 18)
        self.age_groups = [
            {'min': 18, 'max': 24, 'label': '<25 tuổi'},
            {'min': 25, 'max': 40, 'label': '25-40 tuổi'},
            {'min': 41, 'max': 55, 'label': '40-55 tuổi'},
            {'min': 56, 'max': 80, 'label': '>55 tuổi'}
        ]
        
        # Cities in Vietnam
        self.cities = [
            'Hà Nội', 'TP. Hồ Chí Minh', 'Đà Nẵng', 'Hải Phòng', 'Cần Thơ',
            'An Giang', 'Bà Rịa - Vũng Tàu', 'Bắc Giang', 'Bắc Kạn', 'Bạc Liêu',
            'Bắc Ninh', 'Bến Tre', 'Bình Định', 'Bình Dương', 'Bình Phước',
            'Bình Thuận', 'Cà Mau', 'Cao Bằng', 'Đắk Lắk', 'Đắk Nông',
            'Điện Biên', 'Đồng Nai', 'Đồng Tháp', 'Gia Lai', 'Hà Giang',
            'Hà Nam', 'Hà Tĩnh', 'Hải Dương', 'Hậu Giang', 'Hòa Bình',
            'Hưng Yên', 'Khánh Hòa', 'Kiên Giang', 'Kon Tum', 'Lai Châu',
            'Lâm Đồng', 'Lạng Sơn', 'Lào Cai', 'Long An', 'Nam Định',
            'Nghệ An', 'Ninh Bình', 'Ninh Thuận', 'Phú Thọ', 'Phú Yên',
            'Quảng Bình', 'Quảng Nam', 'Quảng Ngãi', 'Quảng Ninh', 'Quảng Trị',
            'Sóc Trăng', 'Sơn La', 'Tây Ninh', 'Thái Bình', 'Thái Nguyên',
            'Thanh Hóa', 'Thừa Thiên Huế', 'Tiền Giang', 'Trà Vinh', 'Tuyên Quang',
            'Vĩnh Long', 'Vĩnh Phúc', 'Yên Bái'
        ]
        
        # Vietnamese names
        self.vietnamese_names = {
            'male': [
                'Nguyễn Văn An', 'Trần Văn Bình', 'Lê Văn Cường', 'Phạm Văn Dũng', 'Hoàng Văn Em',
                'Vũ Văn Phong', 'Đặng Văn Giang', 'Bùi Văn Hải', 'Đỗ Văn Hùng', 'Hồ Văn Khoa',
                'Ngô Văn Long', 'Dương Văn Minh', 'Lý Văn Nam', 'Phan Văn Oanh', 'Võ Văn Phúc',
                'Đinh Văn Quang', 'Tôn Văn Rồng', 'Lưu Văn Sơn', 'Chu Văn Tài', 'Lương Văn Uy'
            ],
            'female': [
                'Nguyễn Thị An', 'Trần Thị Bình', 'Lê Thị Cường', 'Phạm Thị Dũng', 'Hoàng Thị Em',
                'Vũ Thị Phong', 'Đặng Thị Giang', 'Bùi Thị Hải', 'Đỗ Thị Hùng', 'Hồ Thị Khoa',
                'Ngô Thị Long', 'Dương Thị Minh', 'Lý Thị Nam', 'Phan Thị Oanh', 'Võ Thị Phúc',
                'Đinh Thị Quang', 'Tôn Thị Rồng', 'Lưu Thị Sơn', 'Chu Thị Tài', 'Lương Thị Uy'
            ]
        }
    
    def generate_customers_from_data(self, 
                                   customer_accounts: List[Dict], 
                                   customer_transactions: List[Dict]) -> List[Phase3Customer]:
        """Generate customers from account and transaction data"""
        
        customers = []
        customer_data_map = {}
        
        # Group data by customer
        for account_data in customer_accounts:
            customer_code = account_data['customer_code']
            if customer_code not in customer_data_map:
                customer_data_map[customer_code] = {
                    'accounts': [],
                    'transactions': []
                }
            customer_data_map[customer_code]['accounts'].append(account_data)
        
        for transaction_data in customer_transactions:
            customer_code = transaction_data['customer_code']
            if customer_code in customer_data_map:
                customer_data_map[customer_code]['transactions'].append(transaction_data)
        
        # Generate customer for each customer_code
        for customer_code, data in customer_data_map.items():
            customer = self._create_customer_from_data(customer_code, data)
            customers.append(customer)
        
        return customers
    
    def _create_customer_from_data(self, customer_code: str, data: Dict) -> Phase3Customer:
        """Create customer from account and transaction data"""
        
        # Determine segment from customer_code
        if customer_code.startswith('X_'):
            segment = 'X'
        elif customer_code.startswith('Y_'):
            segment = 'Y'
        else:
            segment = 'Z'
        
        # Generate demographics
        gender = random.choice(self.genders)
        full_name = self._generate_full_name(gender)
        dob = self._generate_dob()
        city = random.choice(self.cities)
        marital_status = random.choice(self.marital_status)
        nationality = random.choices(
            list(self.nationality_distribution.keys()),
            weights=list(self.nationality_distribution.values()),
            k=1
        )[0]
        
        # Generate occupation based on segment
        occupation = random.choice(self.occupation_by_segment[segment])
        
        # Generate income based on segment
        income_range = random.choice(self.income_by_segment[segment])
        income_currency = random.choices(
            list(self.income_currency_distribution.keys()),
            weights=list(self.income_currency_distribution.values()),
            k=1
        )[0]
        source_of_income = random.choice(self.source_by_segment[segment])
        
        # Generate status
        status = random.choices(
            list(self.status_distribution.keys()),
            weights=list(self.status_distribution.values()),
            k=1
        )[0]
        
        return Phase3Customer(
            customer_code=customer_code,
            full_name=full_name,
            gender=gender,
            dob=dob,
            city=city,
            marital_status=marital_status,
            nationality=nationality,
            occupation=occupation,
            income_range=income_range,
            income_currency=income_currency,
            source_of_income=source_of_income,
            status=status,
            customer_segment=segment
        )
    
    def _generate_full_name(self, gender: str) -> str:
        """Generate Vietnamese full name"""
        if gender == 'Nam':
            return random.choice(self.vietnamese_names['male'])
        else:
            return random.choice(self.vietnamese_names['female'])
    
    def _generate_dob(self) -> datetime:
        """Generate date of birth based on age groups (ensuring min age 18)"""
        age_group = random.choice(self.age_groups)
        age = random.randint(age_group['min'], age_group['max'])
        
        # Calculate birth year
        current_year = datetime.now().year
        birth_year = current_year - age
        
        # Generate random month and day
        month = random.randint(1, 12)
        day = random.randint(1, 28)  # Safe day range
        
        return datetime(birth_year, month, day)

def main():
    """Test Phase 3 Customer Generator"""
    generator = Phase3CustomerGenerator()
    
    # Test with sample data
    customer_accounts = [
        {'customer_code': 'X_001', 'account_id': 'ACC_001'},
        {'customer_code': 'Y_002', 'account_id': 'ACC_002'},
        {'customer_code': 'Z_003', 'account_id': 'ACC_003'}
    ]
    
    customer_transactions = [
        {'customer_code': 'X_001', 'account_id': 'ACC_001', 'amount': 1000000},
        {'customer_code': 'Y_002', 'account_id': 'ACC_002', 'amount': 500000},
        {'customer_code': 'Z_003', 'account_id': 'ACC_003', 'amount': 100000}
    ]
    
    print("🧪 Testing Phase 3 Customer Generator")
    print("=" * 50)
    
    customers = generator.generate_customers_from_data(customer_accounts, customer_transactions)
    
    for customer in customers:
        print(f"\n👤 {customer.customer_code}: {customer.full_name}")
        print(f"   Gender: {customer.gender}, Age: {(datetime.now() - customer.dob).days // 365}")
        print(f"   City: {customer.city}, Occupation: {customer.occupation}")
        print(f"   Income: {customer.income_range} {customer.income_currency}")
        print(f"   Segment: {customer.customer_segment}, Status: {customer.status}")

if __name__ == "__main__":
    main()
