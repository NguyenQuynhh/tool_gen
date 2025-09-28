"""
New Customer Generator với phân khúc mới
X(50%) - Khách hàng giàu có, tiêu nhiều tiền
Y(30%) - Khách hàng trung bình  
Z(20%) - Khách hàng ít tiền
"""

import random
from datetime import datetime, timedelta
from typing import List
from dataclasses import dataclass

from test_config import test_config

@dataclass
class NewCustomer:
    """New Customer data structure"""
    customer_code: str
    full_name: str
    gender: str
    dob: datetime
    city: str
    marital_status: str
    nationality: str
    occupation: str
    income_range: str
    income_currency: str
    source_of_income: str
    status: str
    customer_segment: str

class NewCustomerGenerator:
    """New Customer Generator với phân khúc mới"""
    
    def __init__(self, config: test_config = None):
        self.config = config or test_config()
        
        # Updated segment distribution
        self.segment_distribution = {
            'X': 0.50,  # 50% - Khách hàng giàu có
            'Y': 0.30,  # 30% - Khách hàng trung bình
            'Z': 0.20   # 20% - Khách hàng ít tiền
        }
        
        # Age groups by segment
        self.age_groups_by_segment = {
            'X': (25, 55),      # 25-55 tuổi
            'Y': (20, 55),      # 20-55 tuổi
            'Z': [(18, 24), (55, 80)]  # <25 tuổi hoặc >=55 tuổi
        }
        
        # Occupation by segment
        self.occupation_by_segment = {
            'X': ['Quản lý / chuyên gia', 'Kinh doanh cá thể'],
            'Y': ['Công nhân / lao động phổ thông', 'Nhân viên văn phòng'],
            'Z': ['Khác (sinh viên, nội trợ…)', 'Nhân viên văn phòng', 'Công nhân / lao động phổ thông']
        }
        
        # Income ranges by segment
        self.income_ranges_by_segment = {
            'X': ['20-50 triệu', '>50 triệu'],
            'Y': ['10-20 triệu', '20-50 triệu'],
            'Z': ['<10 triệu', '10-20 triệu']
        }
        
        # Source of income by segment
        self.source_of_income_by_segment = {
            'X': ['Lương', 'Kinh doanh', 'Đầu tư'],
            'Y': ['Lương', 'Kinh doanh'],
            'Z': ['Lương', 'Khác']
        }
        
        # Vietnamese names
        self.vietnamese_names = {
            'male': [
                'Nguyễn Văn An', 'Trần Văn Bình', 'Lê Văn Cường', 'Phạm Văn Dũng', 'Hoàng Văn Em',
                'Vũ Văn Phong', 'Đặng Văn Giang', 'Bùi Văn Hải', 'Đỗ Văn Hùng', 'Hồ Văn Khoa',
                'Ngô Văn Long', 'Dương Văn Minh', 'Lý Văn Nam', 'Phan Văn Oanh', 'Võ Văn Phúc',
                'Đinh Văn Quang', 'Tôn Văn Rồng', 'Lưu Văn Sơn', 'Chu Văn Tài', 'Lương Văn Uy',
                'Nguyễn Minh Tuấn', 'Trần Đức Thành', 'Lê Hoàng Nam', 'Phạm Quang Huy', 'Hoàng Văn Đức',
                'Vũ Minh Tâm', 'Đặng Quốc Bảo', 'Bùi Văn Thắng', 'Đỗ Minh Khang', 'Hồ Văn Tài'
            ],
            'female': [
                'Nguyễn Thị An', 'Trần Thị Bình', 'Lê Thị Cường', 'Phạm Thị Dũng', 'Hoàng Thị Em',
                'Vũ Thị Phong', 'Đặng Thị Giang', 'Bùi Thị Hải', 'Đỗ Thị Hùng', 'Hồ Thị Khoa',
                'Ngô Thị Long', 'Dương Thị Minh', 'Lý Thị Nam', 'Phan Thị Oanh', 'Võ Thị Phúc',
                'Đinh Thị Quang', 'Tôn Thị Rồng', 'Lưu Thị Sơn', 'Chu Thị Tài', 'Lương Thị Uy',
                'Nguyễn Thị Mai', 'Trần Thị Lan', 'Lê Thị Hương', 'Phạm Thị Nga', 'Hoàng Thị Linh',
                'Vũ Thị Hoa', 'Đặng Thị Thu', 'Bùi Thị Ngọc', 'Đỗ Thị Yến', 'Hồ Thị Trang'
            ]
        }
        
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

    def generate_customers_by_count(self, num_customers: int) -> List[NewCustomer]:
        """Generate customers by count with new segment distribution"""
        customers = []
        
        # Calculate segment counts
        x_count = int(num_customers * self.segment_distribution['X'])
        y_count = int(num_customers * self.segment_distribution['Y'])
        z_count = num_customers - x_count - y_count  # Remaining for Z
        
        print(f"🎯 Generating customers with new distribution:")
        print(f"   X (VIP - 50%): {x_count} customers")
        print(f"   Y (MEDIUM - 30%): {y_count} customers")
        print(f"   Z (LOW - 20%): {z_count} customers")
        
        # Generate X segment customers
        for i in range(x_count):
            customer = self._generate_customer_by_segment('X', i + 1)
            customers.append(customer)
        
        # Generate Y segment customers
        for i in range(y_count):
            customer = self._generate_customer_by_segment('Y', x_count + i + 1)
            customers.append(customer)
        
        # Generate Z segment customers
        for i in range(z_count):
            customer = self._generate_customer_by_segment('Z', x_count + y_count + i + 1)
            customers.append(customer)
        
        return customers

    def _generate_customer_by_segment(self, segment: str, customer_id: int) -> NewCustomer:
        """Generate customer by specific segment"""
        
        # Generate customer code
        customer_code = f"{segment}_{customer_id:06d}"
        
        # Generate gender
        gender = random.choice(['Nam', 'Nữ'])
        
        # Generate full name
        full_name = self._generate_vietnamese_name(gender)
        
        # Generate age based on segment
        age = self._generate_age_by_segment(segment)
        dob = datetime.now() - timedelta(days=age * 365)
        
        # Generate city
        city = random.choice(self.cities)
        
        # Generate marital status
        marital_status = random.choice(['Độc thân', 'Kết hôn'])
        
        # Generate nationality
        nationality = random.choices(['Việt Nam', 'Nước ngoài'], weights=[0.98, 0.02])[0]
        
        # Generate occupation based on segment
        occupation = self._generate_occupation_by_segment(segment)
        
        # Generate income range based on segment
        income_range = self._generate_income_range_by_segment(segment)
        
        # Generate income currency
        income_currency = random.choices(['VND', 'USD'], weights=[0.95, 0.05])[0]
        
        # Generate source of income based on segment
        source_of_income = self._generate_source_of_income_by_segment(segment)
        
        # Generate status
        status = random.choices(['Active', 'Inactive', 'Closed'], weights=[0.80, 0.15, 0.05])[0]
        
        return NewCustomer(
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

    def _generate_age_by_segment(self, segment: str) -> int:
        """Generate age based on segment"""
        if segment == 'X':
            # X: 25-55 tuổi
            return random.randint(25, 55)
        elif segment == 'Y':
            # Y: 20-55 tuổi
            return random.randint(20, 55)
        else:  # Z
            # Z: <25 tuổi (50%) hoặc >=55 tuổi (50%)
            if random.random() < 0.5:
                return random.randint(18, 24)  # <25 tuổi
            else:
                return random.randint(55, 80)  # >=55 tuổi

    def _generate_occupation_by_segment(self, segment: str) -> str:
        """Generate occupation based on segment"""
        if segment == 'X':
            # X: Quản lý/Chuyên gia (60%) + Kinh doanh cá thể (40%)
            return random.choices(
                self.occupation_by_segment['X'],
                weights=[0.6, 0.4]
            )[0]
        elif segment == 'Y':
            # Y: Công nhân/Lao động (50%) + Nhân viên văn phòng (50%)
            return random.choices(
                self.occupation_by_segment['Y'],
                weights=[0.5, 0.5]
            )[0]
        else:  # Z
            # Z: Nhóm khác (80%) + các nghề khác (20%)
            return random.choices(
                self.occupation_by_segment['Z'],
                weights=[0.8, 0.1, 0.1]
            )[0]

    def _generate_income_range_by_segment(self, segment: str) -> str:
        """Generate income range based on segment"""
        if segment == 'X':
            # X: 20-50M (40%) + >50M (60%)
            return random.choices(
                self.income_ranges_by_segment['X'],
                weights=[0.4, 0.6]
            )[0]
        elif segment == 'Y':
            # Y: 10-20M (50%) + 20-50M (50%)
            return random.choices(
                self.income_ranges_by_segment['Y'],
                weights=[0.5, 0.5]
            )[0]
        else:  # Z
            # Z: <10M (70%) + 10-20M (30%)
            return random.choices(
                self.income_ranges_by_segment['Z'],
                weights=[0.7, 0.3]
            )[0]

    def _generate_source_of_income_by_segment(self, segment: str) -> str:
        """Generate source of income based on segment"""
        if segment == 'X':
            # X: Lương (40%) + Kinh doanh (40%) + Đầu tư (20%)
            return random.choices(
                self.source_of_income_by_segment['X'],
                weights=[0.4, 0.4, 0.2]
            )[0]
        elif segment == 'Y':
            # Y: Lương (70%) + Kinh doanh (30%)
            return random.choices(
                self.source_of_income_by_segment['Y'],
                weights=[0.7, 0.3]
            )[0]
        else:  # Z
            # Z: Lương (60%) + Khác (40%)
            return random.choices(
                self.source_of_income_by_segment['Z'],
                weights=[0.6, 0.4]
            )[0]

    def _generate_vietnamese_name(self, gender: str) -> str:
        """Generate Vietnamese full name"""
        if gender == 'Nam':
            return random.choice(self.vietnamese_names['male'])
        else:
            return random.choice(self.vietnamese_names['female'])

def main():
    """Test New Customer Generator"""
    generator = NewCustomerGenerator()
    
    # Generate test customers
    customers = generator.generate_customers_by_count(1000)
    
    print(f"\n✅ Generated {len(customers)} customers")
    
    # Analyze segment distribution
    segment_counts = {}
    for customer in customers:
        segment = customer.customer_segment
        segment_counts[segment] = segment_counts.get(segment, 0) + 1
    
    print(f"\n📊 Segment Distribution:")
    for segment, count in segment_counts.items():
        percentage = (count / len(customers)) * 100
        print(f"   {segment}: {count} ({percentage:.1f}%)")
    
    # Analyze age distribution by segment
    print(f"\n🎂 Age Distribution by Segment:")
    for segment in ['X', 'Y', 'Z']:
        segment_customers = [c for c in customers if c.customer_segment == segment]
        if segment_customers:
            ages = [(datetime.now() - c.dob).days // 365 for c in segment_customers]
            print(f"   {segment}: Min={min(ages)}, Max={max(ages)}, Mean={sum(ages)/len(ages):.1f}")
    
    # Analyze occupation distribution by segment
    print(f"\n💼 Occupation Distribution by Segment:")
    for segment in ['X', 'Y', 'Z']:
        segment_customers = [c for c in customers if c.customer_segment == segment]
        if segment_customers:
            occupations = [c.occupation for c in segment_customers]
            occupation_counts = {}
            for occ in occupations:
                occupation_counts[occ] = occupation_counts.get(occ, 0) + 1
            
            print(f"   {segment}:")
            for occ, count in occupation_counts.items():
                percentage = (count / len(segment_customers)) * 100
                print(f"     {occ}: {count} ({percentage:.1f}%)")

if __name__ == "__main__":
    main()
