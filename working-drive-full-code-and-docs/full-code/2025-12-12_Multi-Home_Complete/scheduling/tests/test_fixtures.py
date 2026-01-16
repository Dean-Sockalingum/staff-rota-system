"""
Test Configuration and Common Test Utilities
Use this module in your tests to get properly configured test data
"""

from datetime import date, timedelta
from decimal import Decimal

class TestDataFactory:
    """Factory for creating properly configured test data"""
    
    @staticmethod
    def compliance_metric_defaults():
        """Get default fields for ComplianceMetric creation"""
        return {
            'period_start': date.today() - timedelta(days=30),
            'period_end': date.today(),
            'current_value': Decimal('95.0'),
            'target_value': Decimal('95.0'),
            'compliant_count': 38,
            'at_risk_count': 2,
            'non_compliant_count': 0,
            'total_count': 40,
        }
    
    @staticmethod
    def create_compliance_metric(care_home, category='TRAINING', **kwargs):
        """Create a ComplianceMetric with sensible defaults"""
        from scheduling.models_compliance_widgets import ComplianceMetric
        
        defaults = TestDataFactory.compliance_metric_defaults()
        defaults.update({
            'care_home': care_home,
            'category': category,
            'metric_name': f"{category.replace('_', ' ').title()} Compliance",
        })
        defaults.update(kwargs)
        
        return ComplianceMetric.objects.create(**defaults)
    
    @staticmethod
    def create_test_user(sap=None, **kwargs):
        """Create a test user with valid SAP number"""
        from django.contrib.auth import get_user_model
        import random
        
        User = get_user_model()
        
        if sap is None:
            sap = f"{random.randint(100000, 999999)}"
        
        defaults = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': f'test{sap}@example.com',
        }
        defaults.update(kwargs)
        
        return User.objects.create_user(sap=sap, **defaults)

# Constants for tests
TEST_CARE_HOME_DATA = {
    'name': 'ORCHARD_GROVE',
    'location_address': '123 Test Street',
    'bed_capacity': 40,
    'care_inspectorate_id': 'CS123456',
}

TEST_UNIT_DATA = {
    'name': 'MAIN_UNIT',
    'capacity': 20,
    'is_active': True,
}
