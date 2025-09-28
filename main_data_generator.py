"""
Main script để sinh dữ liệu theo thứ tự: SAVING TRANSACTION -> SAVING ACCOUNT -> CUSTOMER
Tuân thủ quy tắc RFM và phân khúc khách hàng theo README
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import json
from typing import Dict

from customer_generator import CustomerGenerator
from savings_account_generator import SavingsAccountGenerator
from transaction_generator import TransactionGenerator

class DataGenerator:
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.customer_gen = CustomerGenerator(seed)
        self.account_gen = SavingsAccountGenerator(seed)
        self.txn_gen = TransactionGenerator(seed)
        
        # Tạo thư mục output nếu chưa có
        os.makedirs('output', exist_ok=True)
    
    def generate_full_dataset(self, num_customers: int = 55000, 
                            test_mode: bool = False) -> Dict[str, pd.DataFrame]:
        """
        Sinh toàn bộ dataset theo thứ tự yêu cầu
        
        Args:
            num_customers: Số lượng khách hàng (mặc định 55,000)
            test_mode: Nếu True, chỉ sinh 1,000 khách hàng để test
        """
        if test_mode:
            num_customers = 1000
            print("🧪 CHẠY CHẾ ĐỘ TEST - Chỉ sinh 1,000 khách hàng")
        
        print(f"🚀 Bắt đầu sinh dữ liệu cho {num_customers:,} khách hàng...")
        print("=" * 60)
        
        # Bước 1: Sinh dữ liệu khách hàng
        print("📋 Bước 1: Sinh dữ liệu bảng Customers...")
        start_time = datetime.now()
        customers_df = self.customer_gen.generate_customers(num_customers)
        print(f"✅ Hoàn thành: {len(customers_df):,} khách hàng trong {datetime.now() - start_time}")
        
        # Bước 2: Sinh dữ liệu tài khoản tiết kiệm
        print("\n💳 Bước 2: Sinh dữ liệu bảng Savings Accounts...")
        start_time = datetime.now()
        accounts_df = self.account_gen.generate_accounts_for_customers(customers_df)
        print(f"✅ Hoàn thành: {len(accounts_df):,} tài khoản trong {datetime.now() - start_time}")
        
        # Bước 3: Sinh dữ liệu giao dịch
        print("\n💰 Bước 3: Sinh dữ liệu bảng Savings Transactions...")
        start_time = datetime.now()
        transactions_df = self.txn_gen.generate_all_transactions(accounts_df)
        print(f"✅ Hoàn thành: {len(transactions_df):,} giao dịch trong {datetime.now() - start_time}")
        
        # Bước 4: Cập nhật trạng thái tài khoản dựa trên giao dịch
        print("\n🔄 Bước 4: Cập nhật trạng thái tài khoản...")
        start_time = datetime.now()
        accounts_df = self.account_gen.update_account_status(accounts_df, transactions_df)
        print(f"✅ Hoàn thành cập nhật trạng thái trong {datetime.now() - start_time}")
        
        # Bước 5: Validate và báo cáo
        print("\n📊 Bước 5: Kiểm tra và báo cáo dữ liệu...")
        self.generate_reports(customers_df, accounts_df, transactions_df)
        
        return {
            'customers': customers_df,
            'accounts': accounts_df, 
            'transactions': transactions_df
        }
    
    def generate_reports(self, customers_df: pd.DataFrame, 
                        accounts_df: pd.DataFrame, 
                        transactions_df: pd.DataFrame):
        """Tạo báo cáo thống kê dữ liệu"""
        
        print("\n" + "="*60)
        print("📈 BÁO CÁO THỐNG KÊ DỮ LIỆU")
        print("="*60)
        
        # Báo cáo khách hàng
        print("\n👥 THỐNG KÊ KHÁCH HÀNG:")
        print(f"Tổng số khách hàng: {len(customers_df):,}")
        print("\nPhân bố theo phân khúc:")
        segment_counts = customers_df['segment'].value_counts()
        for segment, count in segment_counts.items():
            percentage = count / len(customers_df) * 100
            print(f"  {segment.upper()}: {count:,} ({percentage:.1f}%)")
        
        print("\nPhân bố theo thu nhập:")
        income_counts = customers_df['income_range'].value_counts()
        for income, count in income_counts.items():
            percentage = count / len(customers_df) * 100
            print(f"  {income}: {count:,} ({percentage:.1f}%)")
        
        # Báo cáo tài khoản
        print(f"\n💳 THỐNG KÊ TÀI KHOẢN:")
        print(f"Tổng số tài khoản: {len(accounts_df):,}")
        print(f"Trung bình tài khoản/khách hàng: {len(accounts_df)/len(customers_df):.2f}")
        
        print("\nPhân bố theo loại sản phẩm:")
        product_counts = accounts_df['product_type'].value_counts()
        for product, count in product_counts.items():
            percentage = count / len(accounts_df) * 100
            print(f"  {product}: {count:,} ({percentage:.1f}%)")
        
        print("\nPhân bố theo kỳ hạn:")
        term_counts = accounts_df['term_months'].value_counts()
        for term, count in term_counts.items():
            percentage = count / len(accounts_df) * 100
            print(f"  {term} tháng: {count:,} ({percentage:.1f}%)")
        
        print("\nPhân bố theo trạng thái:")
        status_counts = accounts_df['status'].value_counts()
        for status, count in status_counts.items():
            percentage = count / len(accounts_df) * 100
            print(f"  {status}: {count:,} ({percentage:.1f}%)")
        
        # Báo cáo giao dịch
        print(f"\n💰 THỐNG KÊ GIAO DỊCH:")
        print(f"Tổng số giao dịch: {len(transactions_df):,}")
        print(f"Trung bình giao dịch/tài khoản: {len(transactions_df)/len(accounts_df):.2f}")
        
        print("\nPhân bố theo loại giao dịch:")
        txn_type_counts = transactions_df['transaction_type'].value_counts()
        for txn_type, count in txn_type_counts.items():
            percentage = count / len(transactions_df) * 100
            print(f"  {txn_type}: {count:,} ({percentage:.1f}%)")
        
        print("\nPhân bố theo kênh:")
        channel_counts = transactions_df['channel_txn'].value_counts()
        for channel, count in channel_counts.items():
            percentage = count / len(transactions_df) * 100
            print(f"  {channel}: {count:,} ({percentage:.1f}%)")
        
        print("\nPhân bố theo trạng thái giao dịch:")
        status_txn_counts = transactions_df['status_txn'].value_counts()
        for status, count in status_txn_counts.items():
            percentage = count / len(transactions_df) * 100
            print(f"  {status}: {count:,} ({percentage:.1f}%)")
        
        # Thống kê tiền tệ
        print("\nPhân bố theo loại tiền tệ:")
        currency_counts = transactions_df['currency'].value_counts()
        for currency, count in currency_counts.items():
            percentage = count / len(transactions_df) * 100
            print(f"  {currency}: {count:,} ({percentage:.1f}%)")
        
        # Thống kê số tiền
        print(f"\nThống kê số tiền giao dịch:")
        print(f"  Tổng số tiền: {transactions_df['amount'].sum():,.0f} VND")
        print(f"  Số tiền trung bình: {transactions_df['amount'].mean():,.0f} VND")
        print(f"  Số tiền lớn nhất: {transactions_df['amount'].max():,.0f} VND")
        print(f"  Số tiền nhỏ nhất: {transactions_df['amount'].min():,.0f} VND")
        
        # Kiểm tra RFM
        print(f"\n🎯 KIỂM TRA PHÂN KHÚC RFM:")
        rfm_stats = self.txn_gen.validate_rfm_segments(transactions_df, accounts_df)
        print(f"Premium: {rfm_stats['premium_count']:,} ({rfm_stats['premium_percentage']:.1f}%)")
        print(f"Standard: {rfm_stats['standard_count']:,} ({rfm_stats['standard_percentage']:.1f}%)")
        print(f"Basic: {rfm_stats['basic_count']:,} ({rfm_stats['basic_percentage']:.1f}%)")
        
        # Lưu báo cáo
        self.save_reports(customers_df, accounts_df, transactions_df, rfm_stats)
    
    def save_reports(self, customers_df: pd.DataFrame, 
                    accounts_df: pd.DataFrame, 
                    transactions_df: pd.DataFrame,
                    rfm_stats: Dict):
        """Lưu báo cáo và dữ liệu ra file"""
        
        # Lưu dữ liệu CSV
        print(f"\n💾 Lưu dữ liệu ra file...")
        customers_df.to_csv('output/customers.csv', index=False, encoding='utf-8-sig')
        accounts_df.to_csv('output/savings_accounts.csv', index=False, encoding='utf-8-sig')
        transactions_df.to_csv('output/savings_transactions.csv', index=False, encoding='utf-8-sig')
        
        # Lưu báo cáo JSON
        report = {
            "generation_time": datetime.now().isoformat(),
            "total_customers": len(customers_df),
            "total_accounts": len(accounts_df),
            "total_transactions": len(transactions_df),
            "segment_distribution": customers_df['segment'].value_counts().to_dict(),
            "product_type_distribution": accounts_df['product_type'].value_counts().to_dict(),
            "transaction_type_distribution": transactions_df['transaction_type'].value_counts().to_dict(),
            "rfm_analysis": rfm_stats,
            "amount_statistics": {
                "total_amount": float(transactions_df['amount'].sum()),
                "average_amount": float(transactions_df['amount'].mean()),
                "max_amount": float(transactions_df['amount'].max()),
                "min_amount": float(transactions_df['amount'].min())
            }
        }
        
        with open('output/data_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print("✅ Đã lưu dữ liệu vào thư mục 'output/':")
        print("  - customers.csv")
        print("  - savings_accounts.csv") 
        print("  - savings_transactions.csv")
        print("  - data_report.json")

def main():
    """Hàm main để chạy sinh dữ liệu"""
    print("🏦 HỆ THỐNG SINH DỮ LIỆU NGÂN HÀNG")
    print("📋 Tuân thủ quy tắc RFM và phân khúc khách hàng")
    print("=" * 60)
    
    # Tạo generator
    generator = DataGenerator(seed=42)
    
    # Hỏi người dùng về chế độ chạy
    print("\nChọn chế độ chạy:")
    print("1. Test mode (1,000 khách hàng)")
    print("2. Full mode (55,000 khách hàng)")
    
    choice = input("\nNhập lựa chọn (1 hoặc 2): ").strip()
    
    if choice == "1":
        test_mode = True
        print("\n🧪 Chạy chế độ TEST...")
    else:
        test_mode = False
        print("\n🚀 Chạy chế độ FULL...")
    
    # Sinh dữ liệu
    try:
        datasets = generator.generate_full_dataset(test_mode=test_mode)
        print(f"\n🎉 HOÀN THÀNH! Dữ liệu đã được sinh thành công.")
        
    except Exception as e:
        print(f"\n❌ LỖI: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
