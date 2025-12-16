"""
Minimal working test suite for automated staffing workflow.
Tests core workflow functionality with corrected model fields.
"""

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import date, time, timedelta

from scheduling.models import Shift, Unit, Role, ShiftType
from scheduling.models_automated_workflow import (
    SicknessAbsence, StaffingCoverRequest
)
from scheduling.models_multi_home import CareHome

User = get_user_model()


class WorkflowBasicTest(TestCase):
    """Basic workflow test with corrected model usage"""
    
    def setUp(self):
        """Set up test data with actual model fields"""
        # Create care home
        self.care_home = CareHome.objects.create(
            name="Test Care Home",
            bed_capacity=20,
            location_address="123 Test Street",
            postcode="G1 1AA",
            care_inspectorate_id="CS2025000001"
        )
        
        # Create role
        self.role = Role.objects.create(
            name="SSCW",
            description="Senior Social Care Worker",
            is_management=False,
            required_headcount=3
        )
        
        # Create unit
        self.unit = Unit.objects.create(
            name="Test Unit",
            description="Test Unit",
            is_active=True,
            min_day_staff=2,
            min_night_staff=2,
            min_weekend_staff=2
        )
        
        # Create shift type
        self.shift_type = ShiftType.objects.create(
            name="DAY_SENIOR",
            start_time=time(9, 0),
            end_time=time(17, 0),
            duration_hours=8.0,
            is_active=True,
            applicable_roles="SSCW,SCW"
        )
        
        # Create staff member
        import random
        sap = f"TEST{random.randint(1000, 9999)}"
        self.staff = User.objects.create_user(
            sap=sap,
            first_name="Test",
            last_name="User",
            email="test@example.com"
        )
        self.staff.role = self.role
        self.staff.unit = self.unit
        self.staff.save()
        
        # Create shift
        tomorrow = date.today() + timedelta(days=1)
        self.shift = Shift.objects.create(
            unit=self.unit,
            user=self.staff,
            shift_type=self.shift_type,
            date=tomorrow,
            shift_classification='REGULAR',
            status='SCHEDULED'
        )
    
    def test_models_created(self):
        """Test that test data is created correctly"""
        self.assertIsNotNone(self.care_home)
        self.assertIsNotNone(self.role)
        self.assertIsNotNone(self.unit)
        self.assertIsNotNone(self.staff)
        self.assertIsNotNone(self.shift)
        self.assertEqual(self.shift.user, self.staff)
        self.assertEqual(self.shift.unit, self.unit)
    
    def test_sickness_absence_creation(self):
        """Test creating sickness absence correctly"""
        absence = SicknessAbsence.objects.create(
            staff_member=self.staff,
            reported_datetime=timezone.now(),
            reported_by=self.staff,
            start_date=self.shift.date,
            end_date=self.shift.date,
            expected_duration_days=1,
            status='REPORTED',
            reason='Test sickness'
        )
        
        # Add affected shift
        absence.affected_shifts.add(self.shift)
        
        self.assertIsNotNone(absence)
        self.assertEqual(absence.staff_member, self.staff)
        self.assertEqual(absence.affected_shifts.count(), 1)
        
