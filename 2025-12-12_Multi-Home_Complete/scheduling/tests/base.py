"""
Base test class with common fixtures for all test cases
"""
from django.test import TestCase
from scheduling.models_multi_home import CareHome


class StaffRotaTestCase(TestCase):
    """
    Base test class that provides common fixtures including CareHome
    
    All test classes should inherit from this instead of Django's TestCase
    to ensure proper care_home FK references for Unit model.
    """
    
    @classmethod
    def setUpTestData(cls):
        """Create common test data"""
        super().setUpTestData()
        
        # Create default care home for all tests
        cls.care_home = CareHome.objects.create(
            name='ORCHARD_GROVE',
            bed_capacity=60,
            current_occupancy=55,
            location_address='123 Test Street, Glasgow',
            postcode='G12 ABC',
            care_inspectorate_id='CS2012345678',
            is_active=True
        )
    
    def create_unit(self, name='OG_BRAMLEY', **kwargs):
        """Helper method to create a unit with proper care_home FK"""
        from scheduling.models import Unit
        
        if 'care_home' not in kwargs:
            kwargs['care_home'] = self.care_home
        
        return Unit.objects.create(name=name, **kwargs)
