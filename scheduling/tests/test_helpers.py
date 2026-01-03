"""
Test helper functions for consistent fixture creation across all test files.
Provides centralized creation methods to handle multi-home constraints.
"""
from scheduling.models_multi_home import CareHome
from scheduling.models import Unit, Role, ShiftType, User
from datetime import time
from decimal import Decimal


def create_test_care_home(name='ORCHARD_GROVE', location='123 Test Street', **kwargs):
    """Create a standard CareHome for testing."""
    defaults = {
        'bed_capacity': 60,
        'current_occupancy': 0,
        'location_address': location,
        'postcode': 'G12 0AB',
        'care_inspectorate_id': f'CS2024{name[:3]}',
        'budget_agency_monthly': Decimal('9000.00'),
        'budget_overtime_monthly': Decimal('5000.00'),
        'is_active': True
    }
    defaults.update(kwargs)
    return CareHome.objects.create(
        name=name,
        **defaults
    )


def create_test_unit(care_home, name='OG_BRAMLEY', **kwargs):
    """Create a Unit with required care_home FK."""
    defaults = {
        'min_day_staff': 2,
        'min_night_staff': 1,
        'min_weekend_staff': 2,
        'ideal_day_staff': 3,
        'ideal_night_staff': 2,
        'is_active': True
    }
    defaults.update(kwargs)
    return Unit.objects.create(
        name=name,
        care_home=care_home,
        **defaults
    )


def create_test_role(name='SCW', **kwargs):
    """Create a Role for testing."""
    defaults = {
        'is_management': False,
        'can_approve_leave': False,
        'can_manage_rota': False,
        'permission_level': 'LIMITED'
    }
    defaults.update(kwargs)
    return Role.objects.create(name=name, **defaults)


def create_test_user(sap='100001', **kwargs):
    """Create a User with valid SAP number."""
    defaults = {
        'email': f'test{sap}@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'is_active': True
    }
    defaults.update(kwargs)
    return User.objects.create_user(sap=sap, password='testpass123', **defaults)


def create_test_shift_type(name='DAY_SENIOR', **kwargs):
    """Create a ShiftType for testing."""
    defaults = {
        'start_time': time(7, 0),
        'end_time': time(19, 0),
        'duration_hours': 12.0,
        'is_active': True
    }
    defaults.update(kwargs)
    return ShiftType.objects.create(name=name, **defaults)
