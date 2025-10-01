"""
New Customer Generator với phân khúc RFM mới
A(10%) - Champions/VIPs - Khách hàng VIP, tiêu nhiều tiền, hoạt động thường xuyên
B(15%) - Potential Loyalists - Khách hàng tiềm năng, có thể phát triển
C(5%) - At-Risk High Value - Khách hàng giá trị cao nhưng có nguy cơ rời bỏ
D(20%) - Stable Savers - Khách hàng tiết kiệm ổn định
E(30%) - New/Occasional Users - Khách hàng mới hoặc thỉnh thoảng sử dụng
"""

import random
import pandas as pd
import os
from datetime import datetime, timedelta
from typing import List, Dict
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
    """New Customer Generator với phân khúc RFM mới"""
    
    def __init__(self, config: test_config = None):
        self.config = config or test_config()
        
        # RFM segment distribution
        self.segment_distribution = {
            'A': 0.10,  # 10% - Champions/VIPs
            'B': 0.15,  # 15% - Potential Loyalists
            'C': 0.05,  # 5% - At-Risk High Value
            'D': 0.20,  # 20% - Stable Savers
            'E': 0.30   # 30% - New/Occasional Users
        }
        
        # Age groups by RFM segment
        self.age_groups_by_segment = {
            'A': (30, 50),      # 30-50 tuổi - VIPs thường ở độ tuổi trung niên
            'B': (25, 45),      # 25-45 tuổi - Potential Loyalists
            'C': (35, 55),      # 35-55 tuổi - At-Risk High Value
            'D': (40, 65),      # 40-65 tuổi - Stable Savers
            'E': [(18, 30), (55, 80)]  # <30 tuổi hoặc >=55 tuổi - New/Occasional
        }
        
        # Occupation by RFM segment (phụ thuộc vào account_id và transaction amount)
        self.occupation_by_segment = {
            'A': ['Quan ly cap cao', 'Giam doc', 'Chu doanh nghiep', 'Chuyen gia cao cap'],
            'B': ['Quan ly trung cap', 'Chuyen gia', 'Kinh doanh ca the', 'Nhan vien cao cap'],
            'C': ['Quan ly cap cao', 'Giam doc', 'Chu doanh nghiep', 'Chuyen gia cao cap'],
            'D': ['Nhan vien van phong', 'Cong chuc', 'Giao vien', 'Nhan vien ngan hang'],
            'E': ['Sinh vien', 'Cong nhan / lao dong pho thong', 'Noi tro', 'Nhan vien van phong']
        }
        
        # Income ranges by RFM segment (phụ thuộc vào account_id và transaction amount)
        self.income_ranges_by_segment = {
            'A': ['50-100 trieu', '100-200 trieu', '>200 trieu'],  # VIPs - thu nhập cao
            'B': ['20-50 trieu', '50-100 trieu'],  # Potential Loyalists
            'C': ['50-100 trieu', '100-200 trieu', '>200 trieu'],  # At-Risk High Value
            'D': ['10-20 trieu', '20-50 trieu'],  # Stable Savers
            'E': ['<10 trieu', '10-20 trieu']  # New/Occasional Users
        }
        
        # Source of income by RFM segment
        self.source_of_income_by_segment = {
            'A': ['Kinh doanh', 'Dau tu', 'Luong cao cap'],
            'B': ['Luong', 'Kinh doanh', 'Dau tu'],
            'C': ['Kinh doanh', 'Dau tu', 'Luong cao cap'],
            'D': ['Luong', 'Tiet kiem'],
            'E': ['Luong', 'Ho tro gia dinh', 'Khac']
        }
        
        # Vietnamese names
        self.vietnamese_names = {
            'male': [
                'Nguyen Van An', 'Tran Van Binh', 'Le Van Cuong', 'Pham Van Dung', 'Hoang Van Em',
                'Vu Van Phong', 'Dang Van Giang', 'Bui Van Hai', 'Do Van Hung', 'Ho Van Khoa',
                'Ngo Van Long', 'Duong Van Minh', 'Ly Van Nam', 'Phan Van Oanh', 'Vo Van Phuc',
                'Dinh Van Quang', 'Ton Van Rong', 'Luu Van Son', 'Chu Van Tai', 'Luong Van Uy',
                'Nguyen Minh Tuan', 'Tran Duc Thanh', 'Le Hoang Nam', 'Pham Quang Huy', 'Hoang Van Duc',
                'Vu Minh Tam', 'Dang Quoc Bao', 'Bui Van Thang', 'Do Minh Khang', 'Ho Van Tai'
            ],
            'female': [
                'Nguyen Thi An', 'Tran Thi Binh', 'Le Thi Cuong', 'Pham Thi Dung', 'Hoang Thi Em',
                'Vu Thi Phong', 'Dang Thi Giang', 'Bui Thi Hai', 'Do Thi Hung', 'Ho Thi Khoa',
                'Ngo Thi Long', 'Duong Thi Minh', 'Ly Thi Nam', 'Phan Thi Oanh', 'Vo Thi Phuc',
                'Dinh Thi Quang', 'Ton Thi Rong', 'Luu Thi Son', 'Chu Thi Tai', 'Luong Thi Uy',
                'Nguyen Thi Mai', 'Tran Thi Lan', 'Le Thi Huong', 'Pham Thi Nga', 'Hoang Thi Linh',
                'Vu Thi Hoa', 'Dang Thi Thu', 'Bui Thi Ngoc', 'Do Thi Yen', 'Ho Thi Trang'
            ]
        }
        
        # Cities in Vietnam - phân loại theo mức độ phát triển
        self.major_cities = [
            'Ha Noi', 'TP. Ho Chi Minh', 'Da Nang', 'Hai Phong', 'Can Tho'
        ]
        
        self.secondary_cities = [
            'An Giang', 'Ba Ria - Vung Tau', 'Binh Duong', 'Dong Nai', 'Khanh Hoa',
            'Kien Giang', 'Lam Dong', 'Long An', 'Nghe An', 'Quang Ninh',
            'Thanh Hoa', 'Thua Thien Hue', 'Tien Giang'
        ]
        
        self.other_cities = [
            'Bac Giang', 'Bac Kan', 'Bac Lieu', 'Bac Ninh', 'Ben Tre',
            'Binh Dinh', 'Binh Phuoc', 'Binh Thuan', 'Ca Mau', 'Cao Bang',
            'Dak Lak', 'Dak Nong', 'Dien Bien', 'Dong Thap', 'Gia Lai',
            'Ha Giang', 'Ha Nam', 'Ha Tinh', 'Hai Duong', 'Hau Giang',
            'Hoa Binh', 'Hung Yen', 'Kon Tum', 'Lai Chau', 'Lang Son',
            'Lao Cai', 'Nam Dinh', 'Ninh Binh', 'Ninh Thuan', 'Phu Tho',
            'Phu Yen', 'Quang Binh', 'Quang Nam', 'Quang Ngai', 'Quang Tri',
            'Soc Trang', 'Son La', 'Tay Ninh', 'Thai Binh', 'Thai Nguyen',
            'Tra Vinh', 'Tuyen Quang', 'Vinh Long', 'Vinh Phuc', 'Yen Bai'
        ]
        
        # Channel preferences by city type
        self.channel_preferences = {
            'major': ['mobile/internet', 'qr_code', 'fund_transfer'],  # Thành phố lớn: nhiều chuyển khoản, QR
            'secondary': ['mobile/internet', 'atm', 'fund_transfer'],
            'other': ['atm', 'branch', 'mobile/internet']
        }

    def generate_customers_by_count(self, num_customers: int) -> List[NewCustomer]:
        """Generate customers by count with RFM segment distribution"""
        customers = []
        
        # Calculate segment counts
        a_count = int(num_customers * self.segment_distribution['A'])
        b_count = int(num_customers * self.segment_distribution['B'])
        c_count = int(num_customers * self.segment_distribution['C'])
        d_count = int(num_customers * self.segment_distribution['D'])
        e_count = num_customers - a_count - b_count - c_count - d_count  # Remaining for E
        
        print(f"[TARGET] Generating customers with RFM distribution:")
        print(f"   A (Champions/VIPs - 10%): {a_count} customers")
        print(f"   B (Potential Loyalists - 15%): {b_count} customers")
        print(f"   C (At-Risk High Value - 5%): {c_count} customers")
        print(f"   D (Stable Savers - 20%): {d_count} customers")
        print(f"   E (New/Occasional Users - 30%): {e_count} customers")
        
        # Generate A segment customers
        for i in range(a_count):
            customer = self._generate_customer_by_segment('A', i + 1)
            customers.append(customer)
        
        # Generate B segment customers
        for i in range(b_count):
            customer = self._generate_customer_by_segment('B', a_count + i + 1)
            customers.append(customer)
        
        # Generate C segment customers
        for i in range(c_count):
            customer = self._generate_customer_by_segment('C', a_count + b_count + i + 1)
            customers.append(customer)
        
        # Generate D segment customers
        for i in range(d_count):
            customer = self._generate_customer_by_segment('D', a_count + b_count + c_count + i + 1)
            customers.append(customer)
        
        # Generate E segment customers
        for i in range(e_count):
            customer = self._generate_customer_by_segment('E', a_count + b_count + c_count + d_count + i + 1)
            customers.append(customer)
        
        return customers

    def _generate_customer_by_segment(self, segment: str, customer_id: int) -> NewCustomer:
        """Generate customer by specific RFM segment"""
        
        # Generate customer code
        customer_code = f"{segment}_{customer_id:06d}"
        
        # Generate gender
        gender = random.choice(['Nam', 'Nữ'])
        
        # Generate full name
        full_name = self._generate_vietnamese_name(gender)
        
        # Generate age based on segment
        age = self._generate_age_by_segment(segment)
        dob = datetime.now() - timedelta(days=age * 365)
        
        # Generate city based on segment (phụ thuộc vào channel_txn)
        city = self._generate_city_by_segment(segment)
        
        # Generate marital status
        marital_status = random.choice(['Độc thân', 'Kết hôn'])
        
        # Generate nationality (98% người VN)
        nationality = random.choices(['Việt Nam', 'Nước ngoài'], weights=[0.98, 0.02])[0]
        
        # Generate occupation based on segment (phụ thuộc vào account_id và transaction amount)
        occupation = self._generate_occupation_by_segment(segment)
        
        # Generate income range based on segment (phụ thuộc vào account_id và transaction amount)
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
        """Generate age based on RFM segment"""
        if segment == 'A':
            # A: 30-50 tuổi - VIPs thường ở độ tuổi trung niên
            return random.randint(30, 50)
        elif segment == 'B':
            # B: 25-45 tuổi - Potential Loyalists
            return random.randint(25, 45)
        elif segment == 'C':
            # C: 35-55 tuổi - At-Risk High Value
            return random.randint(35, 55)
        elif segment == 'D':
            # D: 40-65 tuổi - Stable Savers
            return random.randint(40, 65)
        else:  # E
            # E: <30 tuổi (60%) hoặc >=55 tuổi (40%) - New/Occasional
            if random.random() < 0.6:
                return random.randint(18, 30)  # <30 tuổi
            else:
                return random.randint(55, 80)  # >=55 tuổi

    def _generate_occupation_by_segment(self, segment: str) -> str:
        """Generate occupation based on RFM segment (phụ thuộc vào account_id và transaction amount)"""
        if segment == 'A':
            # A: Champions/VIPs - nghề nghiệp thuộc top thu nhập cao
            return random.choices(
                self.occupation_by_segment['A'],
                weights=[0.3, 0.3, 0.2, 0.2]
            )[0]
        elif segment == 'B':
            # B: Potential Loyalists - nghề nghiệp trung cấp
            return random.choices(
                self.occupation_by_segment['B'],
                weights=[0.3, 0.3, 0.2, 0.2]
            )[0]
        elif segment == 'C':
            # C: At-Risk High Value - nghề nghiệp thuộc top thu nhập cao
            return random.choices(
                self.occupation_by_segment['C'],
                weights=[0.3, 0.3, 0.2, 0.2]
            )[0]
        elif segment == 'D':
            # D: Stable Savers - nghề nghiệp ổn định
            return random.choices(
                self.occupation_by_segment['D'],
                weights=[0.3, 0.3, 0.2, 0.2]
            )[0]
        else:  # E
            # E: New/Occasional Users - nghề nghiệp đa dạng
            return random.choices(
                self.occupation_by_segment['E'],
                weights=[0.3, 0.3, 0.2, 0.2]
            )[0]

    def _generate_income_range_by_segment(self, segment: str) -> str:
        """Generate income range based on RFM segment (phụ thuộc vào account_id và transaction amount)"""
        if segment == 'A':
            # A: Champions/VIPs - thu nhập cao 50-200tr
            return random.choices(
                self.income_ranges_by_segment['A'],
                weights=[0.3, 0.4, 0.3]
            )[0]
        elif segment == 'B':
            # B: Potential Loyalists - thu nhập trung bình
            return random.choices(
                self.income_ranges_by_segment['B'],
                weights=[0.6, 0.4]
            )[0]
        elif segment == 'C':
            # C: At-Risk High Value - thu nhập cao nhưng có nguy cơ
            return random.choices(
                self.income_ranges_by_segment['C'],
                weights=[0.3, 0.4, 0.3]
            )[0]
        elif segment == 'D':
            # D: Stable Savers - thu nhập ổn định
            return random.choices(
                self.income_ranges_by_segment['D'],
                weights=[0.6, 0.4]
            )[0]
        else:  # E
            # E: New/Occasional Users - thu nhập thấp
            return random.choices(
                self.income_ranges_by_segment['E'],
                weights=[0.7, 0.3]
            )[0]

    def _generate_source_of_income_by_segment(self, segment: str) -> str:
        """Generate source of income based on RFM segment"""
        if segment == 'A':
            # A: Champions/VIPs - đa dạng nguồn thu nhập
            return random.choices(
                self.source_of_income_by_segment['A'],
                weights=[0.4, 0.4, 0.2]
            )[0]
        elif segment == 'B':
            # B: Potential Loyalists - cân bằng
            return random.choices(
                self.source_of_income_by_segment['B'],
                weights=[0.5, 0.3, 0.2]
            )[0]
        elif segment == 'C':
            # C: At-Risk High Value - đa dạng nguồn thu nhập
            return random.choices(
                self.source_of_income_by_segment['C'],
                weights=[0.4, 0.4, 0.2]
            )[0]
        elif segment == 'D':
            # D: Stable Savers - chủ yếu lương và tiết kiệm
            return random.choices(
                self.source_of_income_by_segment['D'],
                weights=[0.8, 0.2]
            )[0]
        else:  # E
            # E: New/Occasional Users - đa dạng nguồn
            return random.choices(
                self.source_of_income_by_segment['E'],
                weights=[0.5, 0.3, 0.2]
            )[0]

    def _generate_city_by_segment(self, segment: str) -> str:
        """Generate city based on RFM segment (phụ thuộc vào channel_txn)"""
        if segment in ['A', 'B']:
            # A, B: Champions/VIPs và Potential Loyalists - ưu tiên thành phố lớn
            # Thành phố lớn có nhiều chuyển khoản, QR code
            city_type = random.choices(
                ['major', 'secondary', 'other'],
                weights=[0.6, 0.3, 0.1]
            )[0]
        elif segment == 'C':
            # C: At-Risk High Value - có thể ở thành phố lớn hoặc trung bình
            city_type = random.choices(
                ['major', 'secondary', 'other'],
                weights=[0.4, 0.4, 0.2]
            )[0]
        elif segment == 'D':
            # D: Stable Savers - phân bố đều
            city_type = random.choices(
                ['major', 'secondary', 'other'],
                weights=[0.3, 0.4, 0.3]
            )[0]
        else:  # E
            # E: New/Occasional Users - đa dạng, có thể ở bất kỳ đâu
            city_type = random.choices(
                ['major', 'secondary', 'other'],
                weights=[0.2, 0.3, 0.5]
            )[0]
        
        # Select city from chosen type
        if city_type == 'major':
            return random.choice(self.major_cities)
        elif city_type == 'secondary':
            return random.choice(self.secondary_cities)
        else:
            return random.choice(self.other_cities)

    def _generate_vietnamese_name(self, gender: str) -> str:
        """Generate Vietnamese full name"""
        if gender == 'Nam':
            return random.choice(self.vietnamese_names['male'])
        else:
            return random.choice(self.vietnamese_names['female'])

    def export_customers_to_csv(self, customers: List[NewCustomer], 
                               output_file: str = "output/banking_data_customers.csv") -> str:
        """Export customers to CSV file"""
        
        # Ensure output directory exists
        os.makedirs("output", exist_ok=True)
        
        # Convert customers to list of dictionaries
        customers_data = []
        for customer in customers:
            customer_dict = {
                'customer_code': customer.customer_code,
                'full_name': customer.full_name,
                'gender': customer.gender,
                'dob': customer.dob.strftime('%Y-%m-%d'),
                'city': customer.city,
                'marital_status': customer.marital_status,
                'nationality': customer.nationality,
                'occupation': customer.occupation,
                'income_range': customer.income_range,
                'income_currency': customer.income_currency,
                'source_of_income': customer.source_of_income,
                'status': customer.status,
                'customer_segment': customer.customer_segment
            }
            customers_data.append(customer_dict)
        
        # Create DataFrame and export to CSV
        df = pd.DataFrame(customers_data)
        df.to_csv(output_file, index=False)
        
        print(f"[SUCCESS] Exported {len(customers)} customers to {output_file}")
        return output_file

def main():
    """Test New Customer Generator with RFM segments and export to CSV"""
    generator = NewCustomerGenerator()
    
    # Generate test customers
    customers = generator.generate_customers_by_count(1000)
    
    print(f"\n[SUCCESS] Generated {len(customers)} customers")
    
    # Export to CSV
    output_file = generator.export_customers_to_csv(customers)
    
    # Analyze segment distribution
    segment_counts = {}
    for customer in customers:
        segment = customer.customer_segment
        segment_counts[segment] = segment_counts.get(segment, 0) + 1
    
    print(f"\n[ANALYSIS] RFM Segment Distribution:")
    segment_names = {
        'A': 'Champions/VIPs',
        'B': 'Potential Loyalists', 
        'C': 'At-Risk High Value',
        'D': 'Stable Savers',
        'E': 'New/Occasional Users'
    }
    for segment, count in segment_counts.items():
        percentage = (count / len(customers)) * 100
        print(f"   {segment} ({segment_names[segment]}): {count} ({percentage:.1f}%)")
    
    # Analyze age distribution by segment
    print(f"\n[ANALYSIS] Age Distribution by RFM Segment:")
    for segment in ['A', 'B', 'C', 'D', 'E']:
        segment_customers = [c for c in customers if c.customer_segment == segment]
        if segment_customers:
            ages = [(datetime.now() - c.dob).days // 365 for c in segment_customers]
            print(f"   {segment} ({segment_names[segment]}): Min={min(ages)}, Max={max(ages)}, Mean={sum(ages)/len(ages):.1f}")
    
    # Analyze occupation distribution by segment
    print(f"\n[ANALYSIS] Occupation Distribution by RFM Segment:")
    for segment in ['A', 'B', 'C', 'D', 'E']:
        segment_customers = [c for c in customers if c.customer_segment == segment]
        if segment_customers:
            occupations = [c.occupation for c in segment_customers]
            occupation_counts = {}
            for occ in occupations:
                occupation_counts[occ] = occupation_counts.get(occ, 0) + 1
            
            print(f"   {segment} ({segment_names[segment]}):")
            for occ, count in occupation_counts.items():
                percentage = (count / len(segment_customers)) * 100
                print(f"     {occ}: {count} ({percentage:.1f}%)")
    
    # Analyze income distribution by segment
    print(f"\n[ANALYSIS] Income Distribution by RFM Segment:")
    for segment in ['A', 'B', 'C', 'D', 'E']:
        segment_customers = [c for c in customers if c.customer_segment == segment]
        if segment_customers:
            incomes = [c.income_range for c in segment_customers]
            income_counts = {}
            for income in incomes:
                income_counts[income] = income_counts.get(income, 0) + 1
            
            print(f"   {segment} ({segment_names[segment]}):")
            for income, count in income_counts.items():
                percentage = (count / len(segment_customers)) * 100
                print(f"     {income}: {count} ({percentage:.1f}%)")
    
    # Analyze city distribution by segment
    print(f"\n[ANALYSIS] City Distribution by RFM Segment:")
    for segment in ['A', 'B', 'C', 'D', 'E']:
        segment_customers = [c for c in customers if c.customer_segment == segment]
        if segment_customers:
            cities = [c.city for c in segment_customers]
            city_counts = {}
            for city in cities:
                city_counts[city] = city_counts.get(city, 0) + 1
            
            print(f"   {segment} ({segment_names[segment]}):")
            # Show top 5 cities
            sorted_cities = sorted(city_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            for city, count in sorted_cities:
                percentage = (count / len(segment_customers)) * 100
                print(f"     {city}: {count} ({percentage:.1f}%)")
    
    print(f"\n[EXPORT] Data exported to: {output_file}")
    print(f"[SUMMARY] Total customers: {len(customers)}")
    print(f"[SUMMARY] RFM segments: A(10%), B(15%), C(5%), D(20%), E(30%)")

if __name__ == "__main__":
    main()
