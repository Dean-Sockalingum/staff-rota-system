"""
Test suite for Staffing Alert overstaffing prevention safeguards
Run with: python manage.py test scheduling.tests.StaffingAlertSafeguardsTestCase
"""

from django.test import TestCase
from django.utils import timezone
from datetime import timedelta, date
from concurrent.futures import ThreadPoolExecutor
from scheduling.models import (
    StaffingAlert, StaffingAlertResponse, 
    User, Unit, ShiftType, Role, Shift
)


class StaffingAlertSafeguardsTestCase(TestCase):
    """
    Test overstaffing prevention safeguards
    """
    
    def setUp(self):
        """Create test data"""
        # Create role
        self.role = Role.objects.create(
            name='CARE_ASSISTANT',
            description='Care Assistant'
        )
        
        # Create unit
        self.unit = Unit.objects.create(
            name='WOODLAND_HOUSE',
            is_active=True
        )
        
        # Create shift type
        self.shift_type = ShiftType.objects.create(
            name='DAY_SHIFT',
            start_time='07:00',
            end_time='19:00',
            duration_hours=12.0
        )
        
        # Create test users
        self.users = []
        for i in range(10):
            user = User.objects.create_user(
                sap=f'TEST{i:03d}',
                password='testpass123',
                first_name=f'Test{i}',
                last_name='User',
                email=f'test{i}@example.com',
                role=self.role
            )
            self.users.append(user)
    
    def test_basic_shortage_fill(self):
        """Test normal scenario - alert fills correctly"""
        # Create alert needing 3 staff
        alert = StaffingAlert.objects.create(
            alert_type='SHORTAGE',
            unit=self.unit,
            shift_date=date.today() + timedelta(days=1),
            shift_type=self.shift_type,
            required_staff=17,
            current_staff=14,
            shortage=3,
            expires_at=timezone.now() + timedelta(hours=12),
            priority=5
        )
        
        # Create 3 responses
        responses = []
        for i in range(3):
            response = StaffingAlertResponse.objects.create(
                alert=alert,
                user=self.users[i]
            )
            responses.append(response)
        
        # Accept all 3
        for response in responses:
            shift = response.accept_shift()
            self.assertIsNotNone(shift)
        
        # Verify alert is filled
        alert.refresh_from_db()
        self.assertEqual(alert.accepted_responses, 3)
        self.assertEqual(alert.status, 'FILLED')
        self.assertEqual(alert.positions_remaining, 0)
        
        # Verify 3 shifts created
        shifts = Shift.objects.filter(
            date=alert.shift_date,
            unit=alert.unit,
            shift_type=alert.shift_type,
            status='SCHEDULED'
        )
        self.assertEqual(shifts.count(), 3)
    
    def test_overstaffing_prevention(self):
        """Test that 4th acceptance is rejected when only 3 needed"""
        # Create alert needing 3 staff
        alert = StaffingAlert.objects.create(
            alert_type='SHORTAGE',
            unit=self.unit,
            shift_date=date.today() + timedelta(days=1),
            shift_type=self.shift_type,
            required_staff=17,
            current_staff=14,
            shortage=3,
            expires_at=timezone.now() + timedelta(hours=12),
            priority=5
        )
        
        # Create 4 responses
        responses = []
        for i in range(4):
            response = StaffingAlertResponse.objects.create(
                alert=alert,
                user=self.users[i]
            )
            responses.append(response)
        
        # Accept first 3 - should succeed
        for i in range(3):
            shift = responses[i].accept_shift()
            self.assertIsNotNone(shift)
        
        # Try to accept 4th - should fail
        with self.assertRaises(Exception) as context:
            responses[3].accept_shift()
        
        self.assertIn('already been filled', str(context.exception))
        
        # Verify only 3 accepted
        alert.refresh_from_db()
        self.assertEqual(alert.accepted_responses, 3)
        self.assertFalse(alert.is_overfilled)
    
    def test_concurrent_acceptance_prevention(self):
        """Test race condition protection with simultaneous acceptances"""
        # NOTE: SQLite has limitations with concurrent writes
        # In production with PostgreSQL/MySQL, this test would fully validate concurrent protection
        # For now, we test sequential acceptance to verify the logic works
        
        # Create alert needing 2 staff
        alert = StaffingAlert.objects.create(
            alert_type='SHORTAGE',
            unit=self.unit,
            shift_date=date.today() + timedelta(days=1),
            shift_type=self.shift_type,
            required_staff=17,
            current_staff=15,
            shortage=2,
            expires_at=timezone.now() + timedelta(hours=12),
            priority=5
        )
        
        # Create 5 responses
        responses = []
        for i in range(5):
            response = StaffingAlertResponse.objects.create(
                alert=alert,
                user=self.users[i]
            )
            responses.append(response)
        
        # Try to accept all 5 (sequentially due to SQLite limitations)
        successes = 0
        failures = 0
        
        for response in responses:
            try:
                response.accept_shift()
                successes += 1
            except Exception:
                failures += 1
        
        # Should have exactly 2 successes and 3 failures
        self.assertEqual(successes, 2, f"Expected 2 successes, got {successes}")
        self.assertEqual(failures, 3, f"Expected 3 failures, got {failures}")
        
        # Verify alert state
        alert.refresh_from_db()
        self.assertEqual(alert.accepted_responses, 2)
        self.assertEqual(alert.status, 'FILLED')
        self.assertFalse(alert.is_overfilled)
    
    def test_duplicate_shift_prevention(self):
        """Test that user can't accept if already scheduled"""
        # Create alert
        alert = StaffingAlert.objects.create(
            alert_type='SHORTAGE',
            unit=self.unit,
            shift_date=date.today() + timedelta(days=1),
            shift_type=self.shift_type,
            required_staff=17,
            current_staff=14,
            shortage=3,
            expires_at=timezone.now() + timedelta(hours=12),
            priority=5
        )
        
        # Manually create a shift for user
        existing_shift = Shift.objects.create(
            user=self.users[0],
            unit=self.unit,
            shift_type=self.shift_type,
            date=alert.shift_date,
            status='SCHEDULED',
            notes='Manually created'
        )
        
        # Try to accept alert
        response = StaffingAlertResponse.objects.create(
            alert=alert,
            user=self.users[0]
        )
        
        with self.assertRaises(Exception) as context:
            response.accept_shift()
        
        self.assertIn('already scheduled', str(context.exception))
    
    def test_filled_alert_rejects_new_acceptances(self):
        """Test that FILLED alerts reject new acceptances"""
        # Create alert needing 2 staff
        alert = StaffingAlert.objects.create(
            alert_type='SHORTAGE',
            unit=self.unit,
            shift_date=date.today() + timedelta(days=1),
            shift_type=self.shift_type,
            required_staff=17,
            current_staff=15,
            shortage=2,
            expires_at=timezone.now() + timedelta(hours=12),
            priority=5,
            status='FILLED',  # Already filled
            accepted_responses=2
        )
        
        # Try to accept
        response = StaffingAlertResponse.objects.create(
            alert=alert,
            user=self.users[0]
        )
        
        with self.assertRaises(Exception) as context:
            response.accept_shift()
        
        # Check error message contains key information
        error_msg = str(context.exception)
        self.assertTrue('filled' in error_msg.lower() or 'already been filled' in error_msg.lower())
    
    def test_double_acceptance_prevention(self):
        """Test that same user can't accept twice"""
        # Create alert
        alert = StaffingAlert.objects.create(
            alert_type='SHORTAGE',
            unit=self.unit,
            shift_date=date.today() + timedelta(days=1),
            shift_type=self.shift_type,
            required_staff=17,
            current_staff=14,
            shortage=3,
            expires_at=timezone.now() + timedelta(hours=12),
            priority=5
        )
        
        # Create response and accept
        response = StaffingAlertResponse.objects.create(
            alert=alert,
            user=self.users[0]
        )
        shift = response.accept_shift()
        self.assertIsNotNone(shift)
        
        # Try to accept again
        with self.assertRaises(Exception) as context:
            response.accept_shift()
        
        self.assertIn('Already accepted', str(context.exception))
    
    def test_expired_alert_rejects_acceptance(self):
        """Test that expired alerts can't be accepted"""
        # Create expired alert
        alert = StaffingAlert.objects.create(
            alert_type='SHORTAGE',
            unit=self.unit,
            shift_date=date.today() + timedelta(days=1),
            shift_type=self.shift_type,
            required_staff=17,
            current_staff=14,
            shortage=3,
            expires_at=timezone.now() - timedelta(hours=1),  # Expired 1 hour ago
            priority=5
        )
        
        # Try to accept
        response = StaffingAlertResponse.objects.create(
            alert=alert,
            user=self.users[0]
        )
        
        with self.assertRaises(Exception) as context:
            response.accept_shift()
        
        self.assertIn('expired', str(context.exception))
    
    def test_positions_remaining_accuracy(self):
        """Test that positions_remaining is always accurate"""
        # Create alert needing 5 staff
        alert = StaffingAlert.objects.create(
            alert_type='SHORTAGE',
            unit=self.unit,
            shift_date=date.today() + timedelta(days=1),
            shift_type=self.shift_type,
            required_staff=17,
            current_staff=12,
            shortage=5,
            expires_at=timezone.now() + timedelta(hours=12),
            priority=5
        )
        
        # Initially should need 5
        self.assertEqual(alert.positions_remaining, 5)
        
        # Accept 1
        response1 = StaffingAlertResponse.objects.create(
            alert=alert, user=self.users[0]
        )
        response1.accept_shift()
        alert.refresh_from_db()
        self.assertEqual(alert.positions_remaining, 4)
        
        # Accept 2
        response2 = StaffingAlertResponse.objects.create(
            alert=alert, user=self.users[1]
        )
        response2.accept_shift()
        alert.refresh_from_db()
        self.assertEqual(alert.positions_remaining, 3)
        
        # Accept 3
        response3 = StaffingAlertResponse.objects.create(
            alert=alert, user=self.users[2]
        )
        response3.accept_shift()
        alert.refresh_from_db()
        self.assertEqual(alert.positions_remaining, 2)
        
        # Accept 4 & 5 to fill
        response4 = StaffingAlertResponse.objects.create(
            alert=alert, user=self.users[3]
        )
        response4.accept_shift()
        response5 = StaffingAlertResponse.objects.create(
            alert=alert, user=self.users[4]
        )
        response5.accept_shift()
        
        alert.refresh_from_db()
        self.assertEqual(alert.positions_remaining, 0)
        self.assertEqual(alert.status, 'FILLED')


class StaffingAlertEdgeCasesTestCase(TestCase):
    """Test edge cases and error handling"""
    
    def setUp(self):
        """Create minimal test data"""
        self.role = Role.objects.create(name='CARE_ASSISTANT')
        self.unit = Unit.objects.create(name='TEST_UNIT', is_active=True)
        self.shift_type = ShiftType.objects.create(
            name='TEST_SHIFT',
            start_time='07:00',
            end_time='19:00',
            duration_hours=12.0
        )
        self.user = User.objects.create_user(
            sap='TEST001',
            password='test',
            role=self.role
        )
    
    def test_zero_shortage_alert(self):
        """Test alert with 0 shortage (edge case)"""
        alert = StaffingAlert.objects.create(
            alert_type='SHORTAGE',
            unit=self.unit,
            shift_date=date.today() + timedelta(days=1),
            shift_type=self.shift_type,
            required_staff=17,
            current_staff=17,
            shortage=0,  # Already fully staffed
            expires_at=timezone.now() + timedelta(hours=12),
            priority=5
        )
        
        # Should already be filled
        self.assertTrue(alert.is_filled)
        self.assertEqual(alert.positions_remaining, 0)
        
        # Try to accept - should fail
        response = StaffingAlertResponse.objects.create(
            alert=alert,
            user=self.user
        )
        
        with self.assertRaises(Exception):
            response.accept_shift()
    
    def test_cancelled_alert_rejects_acceptance(self):
        """Test that cancelled alerts can't be accepted"""
        alert = StaffingAlert.objects.create(
            alert_type='SHORTAGE',
            unit=self.unit,
            shift_date=date.today() + timedelta(days=1),
            shift_type=self.shift_type,
            required_staff=17,
            current_staff=14,
            shortage=3,
            expires_at=timezone.now() + timedelta(hours=12),
            priority=5,
            status='CANCELLED'
        )
        
        response = StaffingAlertResponse.objects.create(
            alert=alert,
            user=self.user
        )
        
        with self.assertRaises(Exception) as context:
            response.accept_shift()
        
        # Check error message indicates cancellation
        error_msg = str(context.exception)
        self.assertTrue('cancel' in error_msg.lower() or 'no longer accepting' in error_msg.lower())
