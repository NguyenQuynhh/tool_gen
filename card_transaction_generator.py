"""
Card Transaction Generator với phân khúc khách hàng
Sử dụng dữ liệu cards từ card_generator.py để tạo card transactions
X_VIP (50%) - Khách hàng VIP: 6-8 transactions, >20 triệu, có giao dịch trong 30 ngày
Y_medium (30%) - Khách hàng trung bình: 3+ transactions/ngày, 10-15 triệu, giao dịch trong 2-6 tháng  
Z_low (20%) - Khách hàng thấp: 2-3 transactions/ngày, <10 triệu, giao dịch >6 tháng
"""

import random
import pandas as pd
import os
from datetime import datetime, timedelta
from typing import List, Dict
from dataclasses import dataclass

from test_config import test_config

@dataclass
class Card:
    """Card data structure"""
    card_id: str
    card_number: str
    customer_code: str
    card_type: str
    credit_limit: float
    active_date: datetime
    expiry_date: datetime
    status: str

@dataclass
class CardTransaction:
    """Card Transaction data structure"""
    tran_id: str
    card_id: str
    card_number: str
    customer_code: str
    card_type: str
    tran_amt_acy: float
    tran_amt_lcy: float
    tran_currency: str
    cr_dr: str
    tran_date: datetime
    tran_type: str
    tran_type_name: str
    tran_desc: str
    merchant_id: str
    merchant_name: str
    tran_status: str

class CardTransactionGenerator:
    """Card Transaction Generator với phân khúc khách hàng"""
    
    def __init__(self, config: test_config = None):
        self.config = config or test_config()
        
        # Segment distribution (theo yêu cầu mới)
        self.segment_distribution = {
            'X_VIP': 0.50,      # 50% - Khách hàng VIP
            'Y_medium': 0.30,   # 30% - Khách hàng trung bình  
            'Z_low': 0.20       # 20% - Khách hàng thấp
        }
        
        # Transaction patterns by segment (theo yêu cầu mới) - TĂNG SỐ LƯỢNG GIAO DỊCH
        self.segment_patterns = {
            'A': {  # Champions/VIPs
                'min_transactions': 15,  # Tăng từ 6-8 lên 15-25
                'max_transactions': 25,
                'min_amount': 20000000,  # >20 triệu
                'max_amount': 100000000,  # 100 triệu
                'recent_days': 30,  # Có giao dịch trong 30 ngày
                'transactions_per_day': (1, 3)  # 1-3 giao dịch/ngày
            },
            'B': {  # Potential Loyalists
                'min_transactions': 10,  # Tăng từ 3-5 lên 10-18
                'max_transactions': 18,
                'min_amount': 10000000,  # 10-15 triệu
                'max_amount': 15000000,  # 10-15 triệu
                'recent_days': 180,  # Có giao dịch trong 2-6 tháng (180 ngày)
                'transactions_per_day': (3, 5)  # >3 giao dịch/ngày
            },
            'C': {  # At-Risk High Value
                'min_transactions': 8,  # Tăng từ 2-3 lên 8-12
                'max_transactions': 12,
                'min_amount': 1000000,  # <10 triệu
                'max_amount': 10000000,  # <10 triệu
                'recent_days': 180,  # Có giao dịch >6 tháng (180+ ngày)
                'transactions_per_day': (2, 3)  # 2-3 giao dịch/ngày
            },
            'D': {  # Stable Savers
                'min_transactions': 6,  # Tăng từ 2-4 lên 6-10
                'max_transactions': 10,
                'min_amount': 5000000,  # 5-10 triệu
                'max_amount': 10000000,  # 5-10 triệu
                'recent_days': 90,  # Có giao dịch trong 2-3 tháng (90 ngày)
                'transactions_per_week': (2, 4)  # 2-4 giao dịch/tuần
            },
            'E': {  # New/Occasional Users
                'min_transactions': 3,  # Tăng từ 1-2 lên 3-6
                'max_transactions': 6,
                'min_amount': 1000000,  # <5 triệu
                'max_amount': 5000000,  # <5 triệu
                'recent_days': 365,  # Có giao dịch trong 6-12 tháng (365 ngày)
                'transactions_per_month': (1, 2)  # 1-2 giao dịch/tháng
            }
        }
        
        
        # Currency distribution
        self.currency_distribution = {
            'VND': 0.85,  # 85% VND
            'USD': 0.10,  # 10% USD
            'EUR': 0.05   # 5% EUR
        }
        
        # Transaction types and names
        self.transaction_types = {
            'ONLINE PAYMENT': {
                'weight': 0.50,
                'type_names': ['Payment to Wallet', 'Payment From Wallet', 'Payment To Repost', 'Repost Retail']
            },
            'CASH BY CODE': {
                'weight': 0.15,
                'type_names': ['Cash Dispense (Cardless)']
            },
            'OTHER': {
                'weight': 0.05,
                'type_names': ['Unique', 'Note Acceptance']
            },
            'CASHBACK': {
                'weight': 0.10,
                'type_names': ['Cash Back']
            },
            'ATM/POS': {
                'weight': 0.15,
                'type_names': ['ATM', 'ATM 2Prs']
            },
            'CREDIT': {
                'weight': 0.05,
                'type_names': ['Credit', 'Payment To Credit Card']
            }
        }
        
        # Merchant data
        self.merchants = {
            'VinMart': 0.03,
            'Shopee': 0.03,
            'Tiki': 0.03,
            'Grab': 0.02,
            'Foody': 0.02,
            'Lazada': 0.02,
            'FPT Shop': 0.02,
            'The Gioi Di Dong': 0.02,
            'Dien May Xanh': 0.02,
            'BigC': 0.02,
            'Coopmart': 0.02,
            'Aeon Mall': 0.02,
            'Lotte Mart': 0.02,
            'Metro': 0.02,
            'Circle K': 0.02,
            'FamilyMart': 0.02,
            '7-Eleven': 0.02,
            'Highlands Coffee': 0.02,
            'Starbucks': 0.02,
            'McDonald\'s': 0.02,
            'KFC': 0.02,
            'Pizza Hut': 0.02,
            'Domino\'s Pizza': 0.02,
            'Lotteria': 0.02,
            'Jollibee': 0.02,
            'Phuc Long': 0.02,
            'Trung Nguyen Coffee': 0.02,
            'Cong Coffee': 0.02,
            'The Coffee House': 0.02,
            'Gong Cha': 0.02,
            'Tocotoco': 0.02,
            'Ding Tea': 0.02,
            'Chatime': 0.02,
            'Koi Thé': 0.02,
            'Boba': 0.02,
            'Other': 0.20  # 20% other merchants
        }
        
        # Transaction status distribution
        self.status_distribution = {
            'posted': 0.80,      # 80% posted
            'decline service': 0.10,  # 10% decline
            'closed': 0.05,      # 5% closed
            'inactive': 0.05     # 5% inactive
        }
        
        # CR/DR logic based on transaction type
        self.cr_dr_mapping = {
            'ONLINE PAYMENT': 'DR',  # Chi tiêu = ghi nợ
            'CASH BY CODE': 'DR',    # Rút tiền = ghi nợ
            'OTHER': 'DR',           # Chi tiêu khác = ghi nợ
            'CASHBACK': 'CR',        # Hoàn tiền = ghi có
            'ATM/POS': 'DR',         # Rút tiền = ghi nợ
            'CREDIT': 'CR'           # Hoàn tiền = ghi có
        }


    def load_cards_from_csv(self, cards_file: str = "output/banking_data_cards.csv") -> List[Card]:
        """Load cards from CSV file generated by card_generator.py"""
        
        if not os.path.exists(cards_file):
            raise FileNotFoundError(f"Cards file {cards_file} not found. Please run card_generator.py first.")
        
        print(f"Loading cards from {cards_file}...")
        df_cards = pd.read_csv(cards_file)
        
        cards = []
        for _, row in df_cards.iterrows():
            card = Card(
                card_id=row['card_id'],
                card_number=row['card_number'],
                customer_code=row['customer_code'],
                card_type=row['card_type'],
                credit_limit=row['credit_limit'],
                active_date=datetime.strptime(row['issue_date'], '%Y-%m-%d'),
                expiry_date=datetime.strptime(row['expire_date'], '%Y-%m-%d'),
                status=row['card_status']
            )
            cards.append(card)
        
        print(f"Loaded {len(cards)} cards from CSV file")
        return cards

    def generate_transactions_for_cards(self, cards: List[Card], 
                                      start_date: datetime, end_date: datetime) -> List[CardTransaction]:
        """Generate transactions for cards based on customer segments"""
        
        all_transactions = []
        
        for card in cards:
            # Generate transactions for all cards regardless of status
            # Different status cards will have different transaction patterns
                
            # Determine segment from customer code
            segment = self._determine_segment_from_customer_code(card.customer_code)
            
            # Generate transactions for this card
            transactions = self._generate_transactions_for_card(card, segment, start_date, end_date)
            all_transactions.extend(transactions)
        
        return all_transactions

    def _determine_segment_from_customer_code(self, customer_code: str) -> str:
        """Determine segment from customer code"""
        if customer_code.startswith('A_'):
            return 'A'
        elif customer_code.startswith('B_'):
            return 'B'
        elif customer_code.startswith('C_'):
            return 'C'
        elif customer_code.startswith('D_'):
            return 'D'
        else:  # E_
            return 'E'

    def _generate_transactions_for_card(self, card: Card, segment: str, 
                                      start_date: datetime, end_date: datetime) -> List[CardTransaction]:
        """Generate transactions for a specific card based on segment pattern"""
        
        pattern = self.segment_patterns[segment]
        transactions = []
        
        # Determine number of transactions based on card status
        base_min = pattern['min_transactions']
        base_max = pattern['max_transactions']
        
        if card.status == 'posted':
            # Active cards get full transaction count
            num_transactions = random.randint(base_min, base_max)
        elif card.status == 'decline service':
            # Declined cards get fewer transactions (50-70% of normal)
            min_txns = max(1, int(base_min * 0.5))
            max_txns = max(1, int(base_max * 0.7))
            num_transactions = random.randint(min_txns, max_txns)
        elif card.status == 'closed':
            # Closed cards get very few transactions (20-40% of normal)
            min_txns = max(1, int(base_min * 0.2))
            max_txns = max(1, int(base_max * 0.4))
            num_transactions = random.randint(min_txns, max_txns)
        else:  # inactive
            # Inactive cards get minimal transactions (10-30% of normal)
            min_txns = max(1, int(base_min * 0.1))
            max_txns = max(1, int(base_max * 0.3))
            num_transactions = random.randint(min_txns, max_txns)
        
        # Generate transaction dates
        transaction_dates = self._generate_transaction_dates(
            card.active_date, card.expiry_date, num_transactions, pattern
        )
        
        for i, tran_date in enumerate(transaction_dates):
            # Generate transaction amount
            amount = self._generate_transaction_amount(pattern, card)
            
            # Generate currency
            currency = random.choices(
                list(self.currency_distribution.keys()),
                weights=list(self.currency_distribution.values()),
                k=1
            )[0]
            
            # Calculate LCY amount
            lcy_amount = self._calculate_lcy_amount(amount, currency)
            
            # Generate transaction type
            tran_type = random.choices(
                list(self.transaction_types.keys()),
                weights=[t['weight'] for t in self.transaction_types.values()],
                k=1
            )[0]
            
            # Generate transaction type name
            tran_type_name = random.choice(self.transaction_types[tran_type]['type_names'])
            
            # Generate CR/DR
            cr_dr = self.cr_dr_mapping[tran_type]
            
            # Generate merchant
            merchant_name = random.choices(
                list(self.merchants.keys()),
                weights=list(self.merchants.values()),
                k=1
            )[0]
            merchant_id = f"MERCH_{random.randint(10000, 99999)}"
            
            # Generate transaction description
            tran_desc = self._generate_transaction_description(tran_type_name, merchant_name)
            
            # Generate transaction status
            tran_status = random.choices(
                list(self.status_distribution.keys()),
                weights=list(self.status_distribution.values()),
                k=1
            )[0]
            
            # Generate transaction ID
            tran_id = f"TXN_{card.card_id}_{i+1:06d}"
            
            transaction = CardTransaction(
                tran_id=tran_id,
                card_id=card.card_id,
                card_number=card.card_number,
                customer_code=card.customer_code,
                card_type=card.card_type,
                tran_amt_acy=amount,
                tran_amt_lcy=lcy_amount,
                tran_currency=currency,
                cr_dr=cr_dr,
                tran_date=tran_date,
                tran_type=tran_type,
                tran_type_name=tran_type_name,
                tran_desc=tran_desc,
                merchant_id=merchant_id,
                merchant_name=merchant_name,
                tran_status=tran_status
            )
            
            transactions.append(transaction)
        
        return transactions

    def _generate_transaction_dates(self, active_date: datetime, expiry_date: datetime, 
                                  num_transactions: int, pattern: Dict) -> List[datetime]:
        """Generate transaction dates based on segment pattern"""
        
        current_date = datetime.now()
        dates = []
        
        # Generate dates based on segment pattern
        if pattern.get('transactions_per_month'):  # Segment E - 1-2 transactions/month
            # Spread transactions over months
            months_range = (expiry_date - active_date).days // 30
            if months_range == 0:
                months_range = 1
            
            for i in range(num_transactions):
                # Random month within range
                random_month = random.randint(0, months_range - 1)
                month_start = active_date + timedelta(days=random_month * 30)
                month_end = min(month_start + timedelta(days=30), expiry_date)
                
                # Random day within month
                days_in_month = (month_end - month_start).days
                random_day = random.randint(0, days_in_month - 1)
                tran_date = month_start + timedelta(days=random_day)
                
                # Ensure not in future
                if tran_date > current_date:
                    tran_date = current_date - timedelta(days=random.randint(1, 30))
                
                dates.append(tran_date)
                
        elif pattern.get('transactions_per_week'):  # Segment D - 2-4 transactions/week
            # Spread transactions over weeks
            weeks_range = (expiry_date - active_date).days // 7
            if weeks_range == 0:
                weeks_range = 1
            
            for i in range(num_transactions):
                # Random week within range
                random_week = random.randint(0, weeks_range - 1)
                week_start = active_date + timedelta(days=random_week * 7)
                week_end = min(week_start + timedelta(days=7), expiry_date)
                
                # Random day within week
                days_in_week = (week_end - week_start).days
                random_day = random.randint(0, days_in_week - 1)
                tran_date = week_start + timedelta(days=random_day)
                
                # Ensure not in future
                if tran_date > current_date:
                    tran_date = current_date - timedelta(days=random.randint(1, 30))
                
                dates.append(tran_date)
                
        else:  # Segments A, B, C - daily transactions
            # Ensure we have at least one recent transaction
            recent_cutoff = current_date - timedelta(days=pattern['recent_days'])
            
            # Generate dates within the active period
            date_range = expiry_date - active_date
            days_range = date_range.days
            
            for i in range(num_transactions):
                if i == 0 and pattern['recent_days'] <= 30:
                    # First transaction should be recent for A segment
                    random_days = random.randint(0, pattern['recent_days'])
                    tran_date = current_date - timedelta(days=random_days)
                else:
                    # Other transactions can be anywhere in the active period
                    random_days = random.randint(0, days_range)
                    tran_date = active_date + timedelta(days=random_days)
                
                # Ensure transaction is not in the future
                if tran_date > current_date:
                    tran_date = current_date - timedelta(days=random.randint(1, 30))
                
                dates.append(tran_date)
        
        # Sort dates
        dates.sort()
        return dates

    def _generate_transaction_amount(self, pattern: Dict, card: Card) -> float:
        """Generate transaction amount based on pattern and card constraints"""
        
        amount = random.uniform(pattern['min_amount'], pattern['max_amount'])
        
        # For credit cards, ensure amount doesn't exceed credit limit
        if card.card_type == 'CREDIT' and amount > card.credit_limit:
            amount = random.uniform(pattern['min_amount'], card.credit_limit * 0.8)
        
        return round(amount, 2)

    def _calculate_lcy_amount(self, amount: float, currency: str) -> float:
        """Calculate LCY amount based on currency"""
        if currency == 'VND':
            return amount
        elif currency == 'USD':
            return amount * 25  # USD to VND
        elif currency == 'EUR':
            return amount * 30  # EUR to VND
        else:
            return amount

    def _generate_transaction_description(self, tran_type_name: str, merchant_name: str) -> str:
        """Generate transaction description"""
        descriptions = {
            'Payment to Wallet': f'Payment to {merchant_name} Wallet',
            'Payment From Wallet': f'Payment From {merchant_name} Wallet',
            'Payment To Repost': f'Payment To {merchant_name} Repost',
            'Repost Retail': f'{merchant_name} Retail Payment',
            'Cash Dispense (Cardless)': f'Cash Withdrawal at {merchant_name} ATM',
            'Cash Back': f'Cash Back from {merchant_name}',
            'ATM': f'ATM Withdrawal at {merchant_name}',
            'ATM 2Prs': f'ATM Transaction at {merchant_name}',
            'Credit': f'Credit Refund from {merchant_name}',
            'Payment To Credit Card': f'Credit Card Payment to {merchant_name}',
            'Unique': f'Unique Transaction at {merchant_name}',
            'Note Acceptance': f'Note Acceptance at {merchant_name}'
        }
        
        return descriptions.get(tran_type_name, f'{tran_type_name} at {merchant_name}')

    def _generate_random_date(self, start_date: datetime, end_date: datetime) -> datetime:
        """Generate random date between start and end"""
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        random_date = start_date + timedelta(days=random_number_of_days)
        return random_date


    def export_transactions_to_csv(self, transactions: List[CardTransaction], 
                                 output_file: str = "output/banking_data_card_transactions.csv") -> str:
        """Export card transactions to CSV file"""
        
        # Ensure output directory exists
        os.makedirs("output", exist_ok=True)
        
        # Convert transactions to list of dictionaries
        transactions_data = []
        for txn in transactions:
            txn_dict = {
                'tran_id': txn.tran_id,
                'card_id': txn.card_id,
                'card_number': txn.card_number,
                'customer_code': txn.customer_code,
                'card_type': txn.card_type,
                'tran_amt_acy': txn.tran_amt_acy,
                'tran_amt_lcy': txn.tran_amt_lcy,
                'tran_currency': txn.tran_currency,
                'cr_dr': txn.cr_dr,
                'tran_date': txn.tran_date.strftime('%Y-%m-%d'),
                'tran_type': txn.tran_type,
                'tran_type_name': txn.tran_type_name,
                'tran_desc': txn.tran_desc,
                'merchant_id': txn.merchant_id,
                'merchant_name': txn.merchant_name,
                'tran_status': txn.tran_status
            }
            transactions_data.append(txn_dict)
        
        # Create DataFrame and export to CSV
        df = pd.DataFrame(transactions_data)
        df.to_csv(output_file, index=False)
        
        print(f"[SUCCESS] Exported {len(transactions)} card transactions to {output_file}")
        return output_file

def main():
    """Test Card Transaction Generator"""
    generator = CardTransactionGenerator()
    
    # Test data
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    
    # Load cards from CSV file generated by card_generator.py
    print("Loading cards from CSV file...")
    try:
        cards = generator.load_cards_from_csv()
        print(f"Loaded {len(cards)} cards from CSV file")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please run card_generator.py first to generate cards data.")
        return
    
    # Generate transactions
    print("Generating card transactions...")
    transactions = generator.generate_transactions_for_cards(cards, start_date, end_date)
    print(f"Generated {len(transactions)} card transactions")
    
    # Export to CSV (only transactions, not cards)
    transactions_file = generator.export_transactions_to_csv(transactions)
    
    # Analyze by segment
    print("\n[ANALYSIS] Card Transaction Analysis by Segment:")
    segment_transactions = {}
    for txn in transactions:
        segment = generator._determine_segment_from_customer_code(txn.customer_code)
        if segment not in segment_transactions:
            segment_transactions[segment] = []
        segment_transactions[segment].append(txn)
    
    for segment, txns in segment_transactions.items():
        if txns:
            amounts = [t.tran_amt_acy for t in txns]
            print(f"\n{segment} ({len(txns)} transactions):")
            print(f"  Amount: Min={min(amounts):,.0f}, Max={max(amounts):,.0f}, Mean={sum(amounts)/len(amounts):,.0f}")
            
            # Transaction types
            types = [t.tran_type for t in txns]
            type_counts = {}
            for t in types:
                type_counts[t] = type_counts.get(t, 0) + 1
            
            print(f"  Transaction Types:")
            for t_type, count in type_counts.items():
                percentage = (count / len(txns)) * 100
                print(f"    {t_type}: {count} ({percentage:.1f}%)")
    
    print(f"\n[EXPORT] Files saved:")
    print(f"  Card Transactions: {transactions_file}")

if __name__ == "__main__":
    main()


