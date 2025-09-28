"""
Module sinh dữ liệu bảng Customers
Tạo 55,000 khách hàng với các thuộc tính theo phân khúc RFM
"""

import random
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
import numpy as np

class CustomerGenerator:
    def __init__(self, seed: int = 42):
        random.seed(seed)
        np.random.seed(seed)
        
        # Dữ liệu mẫu cho các trường
        self.cities = [
            "Hà Nội", "TP. Hồ Chí Minh", "Đà Nẵng", "Hải Phòng", "Cần Thơ",
            "An Giang", "Bà Rịa - Vũng Tàu", "Bắc Giang", "Bắc Kạn", "Bạc Liêu",
            "Bắc Ninh", "Bến Tre", "Bình Định", "Bình Dương", "Bình Phước",
            "Bình Thuận", "Cà Mau", "Cao Bằng", "Đắk Lắk", "Đắk Nông",
            "Điện Biên", "Đồng Nai", "Đồng Tháp", "Gia Lai", "Hà Giang",
            "Hà Nam", "Hà Tĩnh", "Hải Dương", "Hậu Giang", "Hòa Bình",
            "Hưng Yên", "Khánh Hòa", "Kiên Giang", "Kon Tum", "Lai Châu",
            "Lâm Đồng", "Lạng Sơn", "Lào Cai", "Long An", "Nam Định",
            "Nghệ An", "Ninh Bình", "Ninh Thuận", "Phú Thọ", "Phú Yên",
            "Quảng Bình", "Quảng Nam", "Quảng Ngãi", "Quảng Ninh", "Quảng Trị",
            "Sóc Trăng", "Sơn La", "Tây Ninh", "Thái Bình", "Thái Nguyên",
            "Thanh Hóa", "Thừa Thiên Huế", "Tiền Giang", "Trà Vinh", "Tuyên Quang",
            "Vĩnh Long", "Vĩnh Phúc", "Yên Bái"
        ]
        
        self.occupations = [
            "Nhân viên văn phòng", "Kinh doanh cá thể", "Công nhân / lao động phổ thông",
            "Quản lý / chuyên gia", "Sinh viên", "Nội trợ", "Giáo viên", "Bác sĩ",
            "Kỹ sư", "Luật sư", "Kế toán", "Nhân viên bán hàng", "Tài xế",
            "Đầu bếp", "Thợ may", "Thợ điện", "Thợ sửa chữa", "Nông dân"
        ]
        
        self.income_sources = ["Lương", "Kinh doanh", "Đầu tư", "Khác"]
        
        # Tỷ lệ phân khúc khách hàng
        self.segment_ratios = {
            "premium": 0.50,    # X = 50% - Khách hàng cao cấp
            "standard": 0.30,   # Y = 30% - Khách hàng tiêu chuẩn  
            "basic": 0.20       # Z = 20% - Khách hàng cơ bản
        }
        
    def generate_customer_segment(self, customer_code: str) -> str:
        """Xác định phân khúc khách hàng dựa trên customer_code"""
        # Sử dụng hash để đảm bảo tính nhất quán
        hash_value = hash(customer_code) % 100
        if hash_value < 50:
            return "premium"
        elif hash_value < 80:
            return "standard"
        else:
            return "basic"
    
    def generate_demographics(self, segment: str) -> Dict[str, Any]:
        """Sinh thông tin nhân khẩu học dựa trên phân khúc"""
        # Giới tính
        gender = random.choice(["Nam", "Nữ"])
        
        # Tuổi dựa trên phân khúc
        if segment == "premium":
            # Khách hàng cao cấp: 25-55 tuổi
            age = random.randint(25, 55)
        elif segment == "standard":
            # Khách hàng tiêu chuẩn: 25-50 tuổi
            age = random.randint(25, 50)
        else:
            # Khách hàng cơ bản: 18-60 tuổi
            age = random.randint(18, 60)
        
        # Ngày sinh
        birth_year = datetime.now().year - age
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)  # Đơn giản hóa
        dob = datetime(birth_year, birth_month, birth_day)
        
        # Tình trạng hôn nhân
        marital_status = random.choice(["Độc thân", "Kết hôn"])
        
        # Quốc tịch (98% VN)
        nationality = "Việt Nam" if random.random() < 0.98 else "Nước ngoài"
        
        return {
            "gender": gender,
            "DOB": dob.strftime("%Y-%m-%d"),
            "marital_status": marital_status,
            "nationality": nationality
        }
    
    def generate_occupation_and_income(self, segment: str) -> Dict[str, Any]:
        """Sinh nghề nghiệp và thu nhập dựa trên phân khúc"""
        if segment == "premium":
            # Khách hàng cao cấp: nghề nghiệp thu nhập cao
            occupation = random.choice([
                "Quản lý / chuyên gia", "Bác sĩ", "Kỹ sư", "Luật sư", 
                "Kế toán", "Giáo viên"
            ])
            income_range = random.choice([">50 triệu", "20–50 triệu"])
            source_of_income = random.choice(["Lương", "Kinh doanh", "Đầu tư"])
        elif segment == "standard":
            # Khách hàng tiêu chuẩn: nghề nghiệp trung bình
            occupation = random.choice([
                "Nhân viên văn phòng", "Kinh doanh cá thể", "Nhân viên bán hàng",
                "Tài xế", "Đầu bếp", "Thợ may"
            ])
            income_range = random.choice(["10–20 triệu", "20–50 triệu"])
            source_of_income = random.choice(["Lương", "Kinh doanh"])
        else:
            # Khách hàng cơ bản: nghề nghiệp đa dạng
            occupation = random.choice(self.occupations)
            income_range = random.choice(["<10 triệu", "10–20 triệu"])
            source_of_income = random.choice(["Lương", "Kinh doanh", "Khác"])
        
        # Loại tiền tệ
        income_currency = "VND" if random.random() < 0.95 else random.choice(["USD", "EUR"])
        
        return {
            "occupation": occupation,
            "income_range": income_range,
            "source_of_income": source_of_income,
            "income_currency": income_currency
        }
    
    def generate_location(self, segment: str) -> str:
        """Sinh thành phố dựa trên phân khúc"""
        if segment == "premium":
            # Khách hàng cao cấp: tập trung ở thành phố lớn
            city_weights = [0.4, 0.3, 0.1, 0.1, 0.1]  # Hà Nội, HCM, Đà Nẵng, Hải Phòng, Cần Thơ
            return random.choices(self.cities[:5], weights=city_weights)[0]
        elif segment == "standard":
            # Khách hàng tiêu chuẩn: phân bố đều
            return random.choice(self.cities)
        else:
            # Khách hàng cơ bản: ưu tiên thành phố nhỏ
            return random.choice(self.cities[5:])
    
    def generate_full_name(self, gender: str) -> str:
        """Sinh họ tên tiếng Việt"""
        last_names = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Phan", "Vũ", "Võ", "Đặng", "Bùi"]
        male_names = ["Anh", "Bình", "Cường", "Dũng", "Đức", "Giang", "Hải", "Hoàng", "Khánh", "Linh",
                     "Minh", "Nam", "Phong", "Quang", "Sơn", "Thành", "Tuấn", "Việt", "Xuân", "Yên"]
        female_names = ["An", "Bích", "Chi", "Dung", "Hương", "Lan", "Mai", "Nga", "Oanh", "Phương",
                       "Quỳnh", "Thảo", "Uyên", "Vân", "Xuân", "Yến", "Hoa", "Linh", "Minh", "Ngọc"]
        
        last_name = random.choice(last_names)
        if gender == "Nam":
            middle_name = random.choice(["Văn", "Đức", "Minh", "Quang", "Hữu"])
            first_name = random.choice(male_names)
        else:
            middle_name = random.choice(["Thị", "Thu", "Minh", "Ngọc", "Hồng"])
            first_name = random.choice(female_names)
        
        return f"{last_name} {middle_name} {first_name}"
    
    def generate_status(self, segment: str) -> str:
        """Sinh trạng thái khách hàng"""
        # Active: ~80%, Inactive: ~15%, Closed: ~5%
        rand = random.random()
        if rand < 0.80:
            return "Active"
        elif rand < 0.95:
            return "Inactive"
        else:
            return "Closed"
    
    def generate_customers(self, num_customers: int = 500000) -> pd.DataFrame:
        """Sinh dữ liệu khách hàng"""
        customers = []
        
        for i in range(num_customers):
            customer_code = f"CIF{i+1:06d}"
            segment = self.generate_customer_segment(customer_code)
            
            # Thông tin cơ bản
            demographics = self.generate_demographics(segment)
            occupation_income = self.generate_occupation_and_income(segment)
            
            # Tên đầy đủ
            full_name = self.generate_full_name(demographics["gender"])
            
            # Thành phố
            city = self.generate_location(segment)
            
            # Trạng thái
            status = self.generate_status(segment)
            
            customer = {
                "customer_code": customer_code,
                "full_name": full_name,
                "gender": demographics["gender"],
                "DOB": demographics["DOB"],
                "city": city,
                "marital_status": demographics["marital_status"],
                "nationality": demographics["nationality"],
                "occupation": occupation_income["occupation"],
                "income_range": occupation_income["income_range"],
                "income_currency": occupation_income["income_currency"],
                "source_of_income": occupation_income["source_of_income"],
                "status": status,
                "segment": segment  # Thêm trường segment để theo dõi
            }
            
            customers.append(customer)
        
        customers_df = pd.DataFrame(customers)
        
        # Lưu dữ liệu ra file CSV
        import os
        os.makedirs('output', exist_ok=True)
        output_file = 'output/customers.csv'
        customers_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"Đã lưu {len(customers_df)} khách hàng vào file: {output_file}")
        
        return customers_df

if __name__ == "__main__":
    generator = CustomerGenerator()
    customers_df = generator.generate_customers()
    
    print(f"Đã sinh {len(customers_df)} khách hàng")
    print("\nPhân bố theo phân khúc:")
    print(customers_df['segment'].value_counts())
    print("\nPhân bố theo thu nhập:")
    print(customers_df['income_range'].value_counts())
    print("\nPhân bố theo giới tính:")
    print(customers_df['gender'].value_counts())
    print("\nPhân bố theo trạng thái:")
    print(customers_df['status'].value_counts())
    print("\nMẫu dữ liệu:")
    print(customers_df.head())
