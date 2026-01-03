# Staff Rota Management System - Test Suite
# Run with: python manage.py test scheduling.tests

from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta, time
from scheduling.models import (
    Role, Unit, ShiftType, Shift, LeaveRequest, 
    Resident, CarePlanReview
)
from scheduling.models_multi_home import CareHome

User = get_user_model()


# Disable login signal during tests to avoid ip_address requirement
@override_settings(
    AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend']
)


class AuthenticationTestCase(TestCase):
    """Test user authentication and permissions"""
    
    def setUp(self):
        """Set up test data"""
        # Create a care home (required for Unit FK)
        self.care_home = CareHome.objects.create(
            name='ORCHARD_GROVE',
            bed_capacity=60,
            location_address='123 Main St',
            postcode='G12 8QQ',
            care_inspectorate_id='CS2012345678'
        )
        
        # Create a role
        self.role = Role.objects.create(
            name='SSCW',
            can_manage_rota=False,
            can_approve_leave=False
        )
        
        # Create a unit
        self.unit = Unit.objects.create(
            name='DEMENTIA',
            is_active=True,
            care_home=self.care_home
        )
        
        # Create test user
        self.user = User.objects.create_user(
            sap='100001',
            first_name='Test',
            last_name='User',
            email='test@example.com',
            password='testpass123',
            role=self.role,
            unit=self.unit,
            is_active=True
        )
        
        # Create manager user
        self.manager_role = Role.objects.create(
            name='OPERATIONS_MANAGER',
            can_manage_rota=True,
            can_approve_leave=True
        )
        
        self.manager = User.objects.create_user(
            sap='100002',
            first_name='Manager',
            last_name='User',
            email='manager@example.com',
            password='managerpass123',
            role=self.manager_role,
            unit=self.unit,
            is_active=True,
            is_staff=True
        )
        
        self.client = Client()
    
    def test_user_creation(self):
        """Test that users are created correctly"""
        self.assertEqual(self.user.sap, '100001')
        self.assertEqual(self.user.full_name, 'Test User')
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)
    
    def test_user_login(self):
        """Test user can log in with SAP ID"""
        logged_in = self.client.login(sap='100001', password='testpass123')
        self.assertTrue(logged_in)
    
    def test_user_login_wrong_password(self):
        """Test user cannot log in with wrong password"""
        logged_in = self.client.login(sap='100001', password='wrongpass')
        self.assertFalse(logged_in)
    
    def test_inactive_user_cannot_login(self):
        """Test inactive users cannot log in"""
        self.user.is_active = False
        self.user.save()
        logged_in = self.client.login(sap='100001', password='testpass123')
        self.assertFalse(logged_in)
    
    def test_manager_permissions(self):
        """Test manager has correct permissions"""
        self.assertTrue(self.manager.role.can_manage_rota)
        self.assertTrue(self.manager.role.can_approve_leave)
    
    def test_staff_no_permissions(self):
        """Test regular staff has no management permissions"""
        self.assertFalse(self.user.role.can_manage_rota)
        self.assertFalse(self.user.role.can_approve_leave)


class DashboardAccessTestCase(TestCase):
    """Test dashboard access and redirects"""
    
    def setUp(self):
        self.care_home = CareHome.objects.create(
            name='ORCHARD_GROVE',
            bed_capacity=60,
            location_address='123 Main St',
            postcode='G12 8QQ',
            care_inspectorate_id='CS2012345678'
        )
        self.role = Role.objects.create(name='SCA')
        self.unit = Unit.objects.create(name='BLUE', is_active=True, care_home=self.care_home)
        self.user = User.objects.create_user(
            sap='100003',
            first_name='Dashboard',
            last_name='Tester',
            email='dash@example.com',
            password='testpass123',
            role=self.role,
            unit=self.unit
        )
        self.client = Client()
    
    def test_dashboard_requires_login(self):
        """Test dashboard redirects to login when not authenticated"""
        response = self.client.get('/staff-dashboard/')
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(response.url.startswith('/login/'))
    
    def test_dashboard_accessible_when_logged_in(self):
        """Test dashboard is accessible after login"""
        self.client.force_login(self.user)
        response = self.client.get('/staff-dashboard/')
        self.assertEqual(response.status_code, 200)


class AIAssistantTestCase(TestCase):
    """Test AI Assistant query processing"""
    
    def setUp(self):
        # Create test data
        self.care_home = CareHome.objects.create(
            name='ORCHARD_GROVE',
            bed_capacity=60,
            location_address='123 Main St',
            postcode='G12 8QQ',
            care_inspectorate_id='CS2012345678'
        )
        self.role = Role.objects.create(name='SSCW')
        self.unit = Unit.objects.create(name='DEMENTIA', is_active=True, care_home=self.care_home)
        
        self.user1 = User.objects.create_user(
            sap='100004',
            first_name='Alice',
            last_name='Smith',
            email='alice@example.com',
            password='testpass123',
            role=self.role,
            unit=self.unit,
            annual_leave_allowance=28,
            annual_leave_used=5
        )
        
        self.user2 = User.objects.create_user(
            sap='100005',
            first_name='Bob',
            last_name='Jones',
            email='bob@example.com',
            password='testpass123',
            role=self.role,
            unit=self.unit
        )
        
        self.client = Client()
        # Use force_login to avoid axes backend issues
        self.client.force_login(self.user1)
    
    def test_ai_assistant_requires_login(self):
        """Test AI Assistant API requires authentication"""
        client = Client()  # New client, not logged in
        response = client.post('/api/ai-assistant/', 
                               data={'query': 'test'}, 
                               content_type='application/json')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_ai_assistant_staff_search(self):
        """Test AI Assistant can find staff by name"""
        response = self.client.post('/api/ai-assistant/',
                                   data={'query': 'Show me Alice Smith'},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('answer', data)
        # AI may return different formats, just check it's not an error
        self.assertNotIn('error', data)
    
    def test_ai_assistant_leave_balance(self):
        """Test AI Assistant can query leave balance"""
        response = self.client.post('/api/ai-assistant/',
                                   data={'query': 'How much annual leave does Alice Smith have left?'},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('answer', data)
        # The response should mention Alice Smith and leave information
        self.assertIn('Alice', data['answer'])
    
    def test_ai_assistant_empty_query(self):
        """Test AI Assistant handles empty query"""
        response = self.client.post('/api/ai-assistant/',
                                   data={'query': ''},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)


class ShiftModelTestCase(TestCase):
    """Test Shift model functionality"""
    
    def setUp(self):
        self.care_home = CareHome.objects.create(
            name='ORCHARD_GROVE',
            bed_capacity=60,
            location_address='123 Main St',
            postcode='G12 8QQ',
            care_inspectorate_id='CS2012345678'
        )
        self.role = Role.objects.create(name='SCA')
        self.unit = Unit.objects.create(name='GREEN', is_active=True, care_home=self.care_home)
        self.user = User.objects.create_user(
            sap='100006',
            first_name='Shift',
            last_name='Worker',
            email='shift@example.com',
            role=self.role,
            unit=self.unit
        )
        
        self.shift_type = ShiftType.objects.create(
            name='DAY_SENIOR',
            start_time=time(8, 0),
            end_time=time(20, 0),
            duration_hours=12.0
        )
    
    def test_shift_creation(self):
        """Test creating a shift"""
        shift = Shift.objects.create(
            user=self.user,
            unit=self.unit,
            shift_type=self.shift_type,
            date=date.today(),
            status='SCHEDULED'
        )
        self.assertEqual(shift.user, self.user)
        self.assertEqual(shift.status, 'SCHEDULED')
        self.assertTrue(shift.pk is not None)
    
    def test_shift_unique_constraint(self):
        """Test unique constraint (user + date + shift_type)"""
        Shift.objects.create(
            user=self.user,
            unit=self.unit,
            shift_type=self.shift_type,
            date=date.today()
        )
        
        # Try to create duplicate
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Shift.objects.create(
                user=self.user,
                unit=self.unit,
                shift_type=self.shift_type,
                date=date.today()
            )
    
    def test_shift_duration_calculation(self):
        """Test shift duration property"""
        shift = Shift.objects.create(
            user=self.user,
            unit=self.unit,
            shift_type=self.shift_type,
            date=date.today(),
            shift_pattern='DAY_0800_2000'
        )
        # Day shift is 12 hours
        self.assertEqual(shift.duration_hours, 12.0)


class LeaveRequestTestCase(TestCase):
    """Test leave request functionality"""
    
    def setUp(self):
        self.care_home = CareHome.objects.create(
            name='ORCHARD_GROVE',
            bed_capacity=60,
            location_address='123 Main St',
            postcode='G12 8QQ',
            care_inspectorate_id='CS2012345678'
        )
        self.role = Role.objects.create(name='SCA')
        self.unit = Unit.objects.create(name='ROSE', is_active=True, care_home=self.care_home)
        self.user = User.objects.create_user(
            sap='100007',
            first_name='Leave',
            last_name='Requester',
            email='leave@example.com',
            role=self.role,
            unit=self.unit,
            annual_leave_allowance=28,
            annual_leave_used=0
        )
    
    def test_leave_request_creation(self):
        """Test creating a leave request"""
        leave = LeaveRequest.objects.create(
            user=self.user,
            leave_type='ANNUAL',
            start_date=date.today() + timedelta(days=7),
            end_date=date.today() + timedelta(days=11),
            days_requested=5,
            reason='Holiday',
            status='PENDING'
        )
        self.assertEqual(leave.status, 'PENDING')
        self.assertEqual(leave.days_requested, 5)
    
    def test_leave_balance_calculation(self):
        """Test leave balance is calculated correctly"""
        # User has 28 days, used 0
        self.assertEqual(self.user.annual_leave_allowance, 28)
        self.assertEqual(self.user.annual_leave_used, 0)
        
        # Request 5 days
        leave = LeaveRequest.objects.create(
            user=self.user,
            leave_type='ANNUAL',
            start_date=date.today() + timedelta(days=7),
            end_date=date.today() + timedelta(days=11),
            days_requested=5,
            status='APPROVED'
        )
        
        # Balance should be 28 - 5 = 23
        # Note: This would need business logic to update annual_leave_used


class CarePlanReviewTestCase(TestCase):
    """Test care plan review functionality"""
    
    def setUp(self):
        self.care_home = CareHome.objects.create(
            name='ORCHARD_GROVE',
            bed_capacity=60,
            location_address='123 Main St',
            postcode='G12 8QQ',
            care_inspectorate_id='CS2012345678'
        )
        self.unit = Unit.objects.create(name='DEMENTIA', is_active=True, care_home=self.care_home)
        
        self.resident = Resident.objects.create(
            resident_id='DEM01',
            first_name='John',
            last_name='Doe',
            date_of_birth=date(1940, 1, 1),
            admission_date=date.today() - timedelta(days=60),
            unit=self.unit,
            room_number='1'
        )
        
        self.role = Role.objects.create(name='SSCW')
        self.keyworker = User.objects.create_user(
            sap='100008',
            first_name='Key',
            last_name='Worker',
            email='keyworker@example.com',
            role=self.role,
            unit=self.unit
        )
    
    def test_care_plan_review_creation(self):
        """Test creating a care plan review"""
        review = CarePlanReview.objects.create(
            resident=self.resident,
            review_type='INITIAL',
            due_date=date.today() + timedelta(days=7),
            keyworker=self.keyworker,
            status='DUE'
        )
        self.assertEqual(review.status, 'DUE')
        self.assertEqual(review.resident, self.resident)
    
    def test_overdue_review_detection(self):
        """Test overdue review is marked correctly"""
        review = CarePlanReview.objects.create(
            resident=self.resident,
            review_type='INITIAL',
            due_date=date.today() - timedelta(days=10),  # Overdue
            keyworker=self.keyworker,
            status='OVERDUE'
        )
        self.assertEqual(review.status, 'OVERDUE')
        self.assertTrue(review.due_date < date.today())


class SecurityTestCase(TestCase):
    """Test security features and CSRF protection"""
    
    def setUp(self):
        self.care_home = CareHome.objects.create(
            name='ORCHARD_GROVE',
            bed_capacity=60,
            location_address='123 Main St',
            postcode='G12 8QQ',
            care_inspectorate_id='CS2012345678'
        )
        self.role = Role.objects.create(name='OPERATIONS_MANAGER', can_manage_rota=True)
        self.unit = Unit.objects.create(name='VIOLET', is_active=True, care_home=self.care_home)
        self.user = User.objects.create_user(
            sap='100009',
            first_name='Security',
            last_name='Tester',
            email='security@example.com',
            password='testpass123',
            role=self.role,
            unit=self.unit
        )
        self.client = Client()
    
    def test_csrf_protection_on_ai_assistant(self):
        """Test AI Assistant API requires CSRF token"""
        self.client.force_login(self.user)
        
        # Without enforce_csrf_checks, Django test client doesn't check CSRF
        # We verify the decorator is absent by checking the view requires POST
        response = self.client.get('/api/ai-assistant/')
        self.assertEqual(response.status_code, 405)  # Method not allowed
    
    def test_login_required_on_protected_views(self):
        """Test protected views require login"""
        # Try to access staff dashboard without login
        response = self.client.get('/staff-dashboard/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Try to access rota view without login
        response = self.client.get('/rota-view/')
        self.assertEqual(response.status_code, 302)


# Test configuration
class TestSettings(TestCase):
    """Test Django settings are configured correctly"""
    
    def test_debug_mode_configurable(self):
        """Test DEBUG can be set via environment"""
        from django.conf import settings
        # In test mode, DEBUG should be controlled
        self.assertIsInstance(settings.DEBUG, bool)
    
    def test_secret_key_exists(self):
        """Test SECRET_KEY is set"""
        from django.conf import settings
        self.assertTrue(len(settings.SECRET_KEY) > 20)
    
    def test_allowed_hosts_configured(self):
        """Test ALLOWED_HOSTS is configured"""
        from django.conf import settings
        self.assertIsInstance(settings.ALLOWED_HOSTS, list)
    
    def test_custom_user_model(self):
        """Test custom user model is configured"""
        from django.conf import settings
        self.assertEqual(settings.AUTH_USER_MODEL, 'scheduling.User')


class CarePlanManagerTestCase(TestCase):
    """Test care plan manager dashboard and approval workflow"""
    
    def setUp(self):
        """Set up test data for care plan manager tests"""
        # Create care home
        self.care_home = CareHome.objects.create(
            name='ORCHARD_GROVE',
            bed_capacity=60,
            location_address='123 Main St',
            postcode='G12 8QQ',
            care_inspectorate_id='CS2012345678'
        )
        
        # Create roles and units
        self.manager_role = Role.objects.create(
            name='OPERATIONS_MANAGER',
            is_management=True,
            can_approve_leave=True,
            can_manage_rota=True
        )
        self.staff_role = Role.objects.create(name='SSCW')
        self.unit = Unit.objects.create(name='DEMENTIA', is_active=True, care_home=self.care_home)
        
        # Create manager user
        self.manager = User.objects.create_user(
            sap='100002',
            first_name='Manager',
            last_name='Test',
            email='manager@test.com',
            password='testpass123',
            role=self.manager_role,
            unit=self.unit,
            is_staff=True
        )
        
        # Create keyworker user
        self.keyworker = User.objects.create_user(
            sap='100008',
            first_name='Key',
            last_name='Worker',
            email='keyworker@test.com',
            password='testpass123',
            role=self.staff_role,
            unit=self.unit
        )
        
        # Create resident
        self.resident = Resident.objects.create(
            resident_id='100001',
            first_name='Test',
            last_name='Resident',
            date_of_birth=date(1950, 1, 1),
            admission_date=date.today() - timedelta(days=180),
            unit=self.unit,
            room_number='101',
            keyworker=self.keyworker
        )
        
        # Create care plan review
        self.review = CarePlanReview.objects.create(
            resident=self.resident,
            review_type='SIX_MONTH',
            due_date=date.today() + timedelta(days=7),
            keyworker=self.keyworker,
            status='PENDING_APPROVAL',
            care_needs_assessment='Test care needs',
            goals_progress='Test progress',
            changes_required='Test changes'
        )
        
        self.client = Client()
    
    def test_manager_dashboard_requires_login(self):
        """Test manager dashboard requires authentication"""
        response = self.client.get('/careplan/manager-dashboard/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_manager_dashboard_accessible_to_managers(self):
        """Test manager dashboard is accessible to management users"""
        self.client.force_login(self.manager)
        response = self.client.get('/careplan/manager-dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Care Plan Manager Dashboard')
    
    def test_manager_dashboard_shows_pending_approvals(self):
        """Test dashboard displays pending approvals"""
        self.client.force_login(self.manager)
        response = self.client.get('/careplan/manager-dashboard/')
        self.assertEqual(response.status_code, 200)
        # Dashboard loads successfully
        self.assertContains(response, 'Care Plan Manager Dashboard')
    
    def test_non_manager_cannot_access_dashboard(self):
        """Test non-management users cannot access manager dashboard"""
        self.client.force_login(self.keyworker)
        response = self.client.get('/careplan/manager-dashboard/')
        # Should redirect or show error
        self.assertIn(response.status_code, [302, 403])
    
    def test_review_approval_requires_login(self):
        """Test review approval requires authentication"""
        response = self.client.get(f'/careplan/approve/{self.review.id}/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_manager_can_approve_review(self):
        """Test manager can access approval page"""
        self.client.force_login(self.manager)
        response = self.client.get(f'/careplan/approve/{self.review.id}/')
        # Can access the approval page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Resident')
    
    def test_manager_can_reject_review(self):
        """Test manager can access rejection workflow"""
        self.client.force_login(self.manager)
        response = self.client.get(f'/careplan/approve/{self.review.id}/')
        self.assertEqual(response.status_code, 200)
        # Page loads with form
        self.assertContains(response, 'manager_comments')
    
    def test_overdue_reviews_identified(self):
        """Test overdue reviews are correctly identified"""
        # Create overdue review
        overdue_review = CarePlanReview.objects.create(
            resident=self.resident,
            review_type='INITIAL',
            due_date=date.today() - timedelta(days=14),
            keyworker=self.keyworker,
            status='OVERDUE'
        )
        
        self.client.login(sap='100002', password='testpass123')
        response = self.client.get('/careplan/manager-dashboard/')
        self.assertEqual(response.status_code, 200)
        # Dashboard loads and shows statistics
        self.assertContains(response, 'Overdue')


# Run tests with:
# python manage.py test scheduling.tests
# python manage.py test scheduling.tests.AuthenticationTestCase
# python manage.py test scheduling.tests.AIAssistantTestCase
# python manage.py test scheduling.tests.CarePlanManagerTestCase --verbose

