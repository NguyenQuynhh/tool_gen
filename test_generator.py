"""
Script test để kiểm tra hệ thống sinh dữ liệu
"""

from main_data_generator import DataGenerator
import pandas as pd

def test_small_dataset():
    """Test với dataset nhỏ"""
    print("🧪 TESTING HỆ THỐNG SINH DỮ LIỆU")
    print("=" * 50)
    
    # Tạo generator
    generator = DataGenerator(seed=42)
    
    # Sinh dữ liệu test (100 khách hàng)
    print("Sinh dữ liệu test với 100 khách hàng...")
    datasets = generator.generate_full_dataset(num_customers=100, test_mode=True)
    
    # Kiểm tra dữ liệu
    customers_df = datasets['customers']
    accounts_df = datasets['accounts']
    transactions_df = datasets['transactions']
    
    print(f"\n✅ Kết quả test:")
    print(f"  - Khách hàng: {len(customers_df)}")
    print(f"  - Tài khoản: {len(accounts_df)}")
    print(f"  - Giao dịch: {len(transactions_df)}")
    
    # Kiểm tra tính hợp lệ
    print(f"\n🔍 Kiểm tra tính hợp lệ:")
    
    # 1. Kiểm tra customer_code unique
    assert customers_df['customer_code'].nunique() == len(customers_df), "Customer codes không unique!"
    print("  ✅ Customer codes unique")
    
    # 2. Kiểm tra account_id unique
    assert accounts_df['account_id'].nunique() == len(accounts_df), "Account IDs không unique!"
    print("  ✅ Account IDs unique")
    
    # 3. Kiểm tra foreign key relationships
    customer_codes = set(customers_df['customer_code'])
    account_customer_codes = set(accounts_df['customer_code'])
    assert account_customer_codes.issubset(customer_codes), "Account có customer_code không tồn tại!"
    print("  ✅ Foreign key relationships hợp lệ")
    
    # 4. Kiểm tra transaction amounts > 0
    assert (transactions_df['amount'] > 0).all(), "Có giao dịch với số tiền <= 0!"
    print("  ✅ Tất cả giao dịch có số tiền > 0")
    
    # 5. Kiểm tra balance không âm
    assert (transactions_df['balance'] >= 0).all(), "Có số dư âm!"
    print("  ✅ Tất cả số dư >= 0")
    
    # 6. Kiểm tra phân khúc
    segment_counts = customers_df['segment'].value_counts()
    print(f"\n📊 Phân bố phân khúc:")
    for segment, count in segment_counts.items():
        percentage = count / len(customers_df) * 100
        print(f"  {segment}: {count} ({percentage:.1f}%)")
    
    # 7. Kiểm tra loại sản phẩm
    product_counts = accounts_df['product_type'].value_counts()
    print(f"\n💳 Phân bố loại sản phẩm:")
    for product, count in product_counts.items():
        percentage = count / len(accounts_df) * 100
        print(f"  {product}: {count} ({percentage:.1f}%)")
    
    # 8. Kiểm tra loại giao dịch
    txn_counts = transactions_df['transaction_type'].value_counts()
    print(f"\n💰 Phân bố loại giao dịch:")
    for txn_type, count in txn_counts.items():
        percentage = count / len(transactions_df) * 100
        print(f"  {txn_type}: {count} ({percentage:.1f}%)")
    
    print(f"\n🎉 TEST THÀNH CÔNG! Hệ thống hoạt động đúng.")
    
    return True

if __name__ == "__main__":
    try:
        test_small_dataset()
    except Exception as e:
        print(f"\n❌ TEST THẤT BẠI: {str(e)}")
        import traceback
        traceback.print_exc()
