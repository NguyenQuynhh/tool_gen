"""
Customer Segment Generator
Implement customer segmentation logic theo RFM analysis
"""

import random
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from test_config import test_config

@dataclass
class CustomerSegment:
    """Customer segment data structure"""
    customer_code: str
    segment: str
    expected_frequency: int
    expected_amount_min: int
    expected_recency_days: int
    expected_accounts: int
    created_at: datetime

class CustomerSegmentGenerator:
    """Generator cho customer segmentation theo RFM analysis"""
    
    def __init__(self, config: test_config = None):
        self.config = config or test_config()
        self.segments = ['VIP', 'MEDIUM', 'LOW']
        self.distribution = self.config.SEGMENT_DISTRIBUTION
        self.rfm_constraints = self.config.RFM_CONSTRAINTS
    
    def generate_customers_by_count(self, total_customers: int) -> List[CustomerSegment]:
        """Generate customers theo total count với distribution"""
        customers = []
        
        # Calculate segment counts
        vip_count = int(total_customers * self.distribution['VIP'])
        medium_count = int(total_customers * self.distribution['MEDIUM'])
        low_count = total_customers - vip_count - medium_count
        
        # Generate VIP customers
        for i in range(vip_count):
            customer = self._create_vip_customer(f"VIP_{i+1:06d}")
            customers.append(customer)
        
        # Generate Medium customers
        for i in range(medium_count):
            customer = self._create_medium_customer(f"MED_{i+1:06d}")
            customers.append(customer)
        
        # Generate Low customers
        for i in range(low_count):
            customer = self._create_low_customer(f"LOW_{i+1:06d}")
            customers.append(customer)
        
        # Shuffle để randomize order
        random.shuffle(customers)
        
        return customers
    
    def generate_customers_by_segment(self, segment: str, count: int) -> List[CustomerSegment]:
        """Generate customers cho specific segment"""
        customers = []
        
        for i in range(count):
            if segment == 'VIP':
                customer = self._create_vip_customer(f"VIP_{i+1:06d}")
            elif segment == 'MEDIUM':
                customer = self._create_medium_customer(f"MED_{i+1:06d}")
            elif segment == 'LOW':
                customer = self._create_low_customer(f"LOW_{i+1:06d}")
            else:
                raise ValueError(f"Invalid segment: {segment}")
            
            customers.append(customer)
        
        return customers
    
    def _create_vip_customer(self, customer_code: str) -> CustomerSegment:
        """Tạo VIP customer với high-end characteristics"""
        constraints = self.rfm_constraints['VIP']
        
        return CustomerSegment(
            customer_code=customer_code,
            segment='VIP',
            expected_frequency=random.randint(*constraints['frequency_range']),
            expected_amount_min=constraints['amount_min'],
            expected_recency_days=random.randint(1, constraints['recency_days']),
            expected_accounts=random.randint(2, 5),  # VIP có nhiều accounts
            created_at=datetime.now()
        )
    
    def _create_medium_customer(self, customer_code: str) -> CustomerSegment:
        """Tạo Medium customer với medium characteristics"""
        constraints = self.rfm_constraints['MEDIUM']
        
        return CustomerSegment(
            customer_code=customer_code,
            segment='MEDIUM',
            expected_frequency=random.randint(*constraints['frequency_range']),
            expected_amount_min=constraints['amount_min'],
            expected_recency_days=random.randint(constraints['recency_days'], constraints['recency_days']),
            expected_accounts=random.randint(1, 3),
            created_at=datetime.now()
        )
    
    def _create_low_customer(self, customer_code: str) -> CustomerSegment:
        """Tạo Low customer với low-end characteristics"""
        constraints = self.rfm_constraints['LOW']
        
        return CustomerSegment(
            customer_code=customer_code,
            segment='LOW',
            expected_frequency=random.randint(*constraints['frequency_range']),
            expected_amount_min=random.randint(
                constraints['amount_min'], 
                constraints.get('amount_max', constraints['amount_min'] * 2)
            ),
            expected_recency_days=random.randint(constraints['recency_days'], 365),
            expected_accounts=1,  # Low chỉ có 1 account
            created_at=datetime.now()
        )
    
    def get_segment_statistics(self, customers: List[CustomerSegment]) -> Dict[str, Any]:
        """Tính toán statistics cho customer segments"""
        if not customers:
            return {}
        
        total_customers = len(customers)
        segment_counts = {}
        
        for customer in customers:
            segment = customer.segment
            segment_counts[segment] = segment_counts.get(segment, 0) + 1
        
        # Calculate percentages
        statistics = {
            'total_customers': total_customers,
            'segment_counts': segment_counts,
            'segment_percentages': {},
            'average_accounts_per_segment': {},
            'average_frequency_per_segment': {},
            'average_amount_per_segment': {}
        }
        
        for segment in self.segments:
            count = segment_counts.get(segment, 0)
            statistics['segment_percentages'][segment] = count / total_customers if total_customers > 0 else 0
            
            # Calculate averages for each segment
            segment_customers = [c for c in customers if c.segment == segment]
            if segment_customers:
                statistics['average_accounts_per_segment'][segment] = sum(c.expected_accounts for c in segment_customers) / len(segment_customers)
                statistics['average_frequency_per_segment'][segment] = sum(c.expected_frequency for c in segment_customers) / len(segment_customers)
                statistics['average_amount_per_segment'][segment] = sum(c.expected_amount_min for c in segment_customers) / len(segment_customers)
        
        return statistics
    
    def validate_distribution(self, customers: List[CustomerSegment], tolerance: float = 0.05) -> Dict[str, bool]:
        """Validate distribution có đúng với expected percentages không"""
        statistics = self.get_segment_statistics(customers)
        validation_results = {}
        
        for segment in self.segments:
            expected_percentage = self.distribution[segment]
            actual_percentage = statistics['segment_percentages'][segment]
            difference = abs(actual_percentage - expected_percentage)
            
            validation_results[segment] = {
                'expected': expected_percentage,
                'actual': actual_percentage,
                'difference': difference,
                'valid': difference <= tolerance
            }
        
        return validation_results
    
    def export_to_dict(self, customers: List[CustomerSegment]) -> List[Dict[str, Any]]:
        """Export customers to dictionary format"""
        return [
            {
                'customer_code': customer.customer_code,
                'segment': customer.segment,
                'expected_frequency': customer.expected_frequency,
                'expected_amount_min': customer.expected_amount_min,
                'expected_recency_days': customer.expected_recency_days,
                'expected_accounts': customer.expected_accounts,
                'created_at': customer.created_at.isoformat()
            }
            for customer in customers
        ]

def main():
    """Test function"""
    generator = CustomerSegmentGenerator()
    
    # Test với 1000 customers
    customers = generator.generate_customers_by_count(1000)
    
    # Print statistics
    stats = generator.get_segment_statistics(customers)
    print("Customer Segment Statistics:")
    print(f"Total customers: {stats['total_customers']}")
    print("\nSegment Distribution:")
    for segment, percentage in stats['segment_percentages'].items():
        print(f"  {segment}: {percentage:.1%}")
    
    # Validate distribution
    validation = generator.validate_distribution(customers)
    print("\nDistribution Validation:")
    for segment, result in validation.items():
        status = "✅" if result['valid'] else "❌"
        print(f"  {segment}: {status} Expected: {result['expected']:.1%}, Actual: {result['actual']:.1%}")

if __name__ == "__main__":
    main()
