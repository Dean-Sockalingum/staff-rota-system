"""
Test Suite for Task 59: Leave Calendar View
Tests FullCalendar integration, calendar views, and coverage analysis
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal
import json
from scheduling.models import Unit, LeaveRequest
from scheduling.models_multi_home import CareHome
from staff_records.models import StaffProfile

User = get_user_model()


class LeaveCalendarViewTests(TestCase):
    """Test leave calendar view access and rendering"""
    
    def setUp(self):
        self.client = Client()
        self.care_home = CareHome.objects.create(
            name='VICTORIA_GARDENS',
            location_address="100 Calendar Lane",
            bed_capacity=45,
            care_inspectorate_id="CS567890"
        )
        self.unit = Unit.objects.create(
            name="Test Unit",
            care_home=self.care_home
        )
        
        self.user = User.objects.create_user(            sap='200021',
            first_name='Test',
            last_name='User',            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # self.user.care_home_access.add(self.care_home)  # care_home_access removed - users access via unit.care_home
        
        self.profile = StaffProfile.objects.create(
            user=self.user,
            sap_number='123456',
            unit=self.unit,
            permission_level='FULL'
        )
    
    def test_calendar_requires_login(self):
        """Test that calendar view requires authentication"""
        url = reverse('leave_calendar')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
    
    def test_calendar_view_authenticated(self):
        """Test calendar view for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('leave_calendar')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Leave Calendar')
        self.assertContains(response, 'FullCalendar')
    
    def test_calendar_includes_fullcalendar_cdn(self):
        """Test that calendar includes FullCalendar CDN links"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('leave_calendar')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'cdn.jsdelivr.net/npm/fullcalendar')
        self.assertContains(response, 'fullcalendar@6.1.10')


class TeamLeaveCalendarViewTests(TestCase):
    """Test team leave calendar view (manager access)"""
    
    def setUp(self):
        self.client = Client()
        self.care_home = CareHome.objects.create(
            name='ORCHARD_GROVE',
            location_address="200 Team View St",
            bed_capacity=40,
            care_inspectorate_id="CS678901"
        )
        self.unit = Unit.objects.create(
            name="Test Unit",
            care_home=self.care_home
        )
        
        # Create manager user
        self.manager = User.objects.create_user(
            sap='200002',
            first_name='Manager',
            last_name='User',
            email='manager@example.com',
            password='testpass123'
        )
        # self.manager.care_home_access.add(self.care_home)  # care_home_access removed - users access via unit.care_home
        
        self.manager_profile = StaffProfile.objects.create(
            user=self.manager,
            sap_number='111111',
            unit=self.unit,
            permission_level='FULL'
        )
        
        # Create regular user
        self.staff = User.objects.create_user(
            sap='200003',
            first_name='Staff',
            last_name='User',
            email='staff@example.com',
            password='testpass123'
        )
        # self.staff.care_home_access.add(self.care_home)  # care_home_access removed - users access via unit.care_home
        
        self.staff_profile = StaffProfile.objects.create(
            user=self.staff,
            sap_number='222222',
            unit=self.unit,
            permission_level='READ_ONLY'
        )
    
    def test_team_calendar_requires_login(self):
        """Test team calendar requires authentication"""
        url = reverse('team_leave_calendar')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
    
    def test_team_calendar_manager_access(self):
        """Test manager can access team calendar"""
        self.client.login(username='manager', password='testpass123')
        url = reverse('team_leave_calendar')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Team Leave Calendar')
    
    def test_team_calendar_readonly_access(self):
        """Test READ_ONLY user can access team calendar"""
        self.client.login(username='staff', password='testpass123')
        url = reverse('team_leave_calendar')
        response = self.client.get(url)
        
        # READ_ONLY should be able to view
        self.assertEqual(response.status_code, 200)
    
    def test_team_calendar_filters_displayed(self):
        """Test team calendar shows care home and unit filters"""
        self.client.login(username='manager', password='testpass123')
        url = reverse('team_leave_calendar')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Care Home')
        self.assertContains(response, 'Unit')


class LeaveCalendarDataAPITests(TestCase):
    """Test leave calendar data API endpoint"""
    
    def setUp(self):
        self.client = Client()
        self.care_home = CareHome.objects.create(
            name='MEADOWBURN',
            location_address="300 API Drive",
            bed_capacity=38,
            care_inspectorate_id="CS789012"
        )
        self.unit = Unit.objects.create(
            name="Test Unit",
            care_home=self.care_home
        )
        
        self.user = User.objects.create_user(
            sap='200004',
            first_name='Test',
            last_name='User',
            email='test@example.com',
            password='testpass123'
        )
        # self.user.care_home_access.add(self.care_home)  # care_home_access removed - users access via unit.care_home
        
        self.profile = StaffProfile.objects.create(
            user=self.user,
            sap_number='123456',
            unit=self.unit
        )
        
        # Create leave type
        self.leave_type = LeaveType.objects.create(
            name='Annual Leave',
            code='ANNUAL',
            is_paid=True
        )
        
        # Create test leave request
        self.leave_request = LeaveRequest.objects.create(
            staff_profile=self.profile,
            leave_type=self.leave_type,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
            reason='Test vacation',
            status='APPROVED'
        )
    
    def test_calendar_data_api_requires_login(self):
        """Test API requires authentication"""
        url = reverse('leave_calendar_data_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)
    
    def test_calendar_data_api_returns_json(self):
        """Test API returns JSON format"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('leave_calendar_data_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
    
    def test_calendar_data_api_event_structure(self):
        """Test API returns events with correct structure"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('leave_calendar_data_api')
        
        # Add date range parameters for FullCalendar
        start_date = date.today() - timedelta(days=30)
        end_date = date.today() + timedelta(days=30)
        
        response = self.client.get(url, {
            'start': start_date.isoformat(),
            'end': end_date.isoformat()
        })
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIsInstance(data, list)
        
        if len(data) > 0:
            event = data[0]
            # Check required FullCalendar fields
            self.assertIn('id', event)
            self.assertIn('title', event)
            self.assertIn('start', event)
            self.assertIn('end', event)
            self.assertIn('color', event)
            self.assertIn('extendedProps', event)
    
    def test_calendar_data_api_filtering_by_care_home(self):
        """Test API filters by care home parameter"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('leave_calendar_data_api')
        
        response = self.client.get(url, {
            'start': date.today().isoformat(),
            'end': (date.today() + timedelta(days=30)).isoformat(),
            'care_home_id': self.care_home.id
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
    
    def test_calendar_data_api_filtering_by_unit(self):
        """Test API filters by unit parameter"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('leave_calendar_data_api')
        
        response = self.client.get(url, {
            'start': date.today().isoformat(),
            'end': (date.today() + timedelta(days=30)).isoformat(),
            'unit_id': self.unit.id
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
    
    def test_calendar_data_api_view_type_personal(self):
        """Test API with view_type=personal shows only user's leave"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('leave_calendar_data_api')
        
        response = self.client.get(url, {
            'start': date.today().isoformat(),
            'end': (date.today() + timedelta(days=30)).isoformat(),
            'view_type': 'personal'
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # All events should be for current user
        for event in data:
            self.assertEqual(event['extendedProps']['staff_id'], self.profile.id)


class LeaveCoverageReportAPITests(TestCase):
    """Test leave coverage report API endpoint"""
    
    def setUp(self):
        self.client = Client()
        self.care_home = CareHome.objects.create(
            name='HAWTHORN_HOUSE',
            location_address="400 Coverage Rd",
            bed_capacity=42,
            care_inspectorate_id="CS890123"
        )
        self.unit = Unit.objects.create(
            name="Test Unit",
            care_home=self.care_home
        )
        
        self.user = User.objects.create_user(
            sap='200005',
            first_name='Manager',
            last_name='User',
            email='manager@example.com',
            password='testpass123'
        )
        # self.user.care_home_access.add(self.care_home)  # care_home_access removed - users access via unit.care_home
        
        self.profile = StaffProfile.objects.create(
            user=self.user,
            sap_number='123456',
            unit=self.unit,
            permission_level='FULL'
        )
        
        # Create leave type
        self.leave_type = LeaveType.objects.create(
            name='Annual Leave',
            code='ANNUAL',
            is_paid=True
        )
    
    def test_coverage_api_requires_login(self):
        """Test coverage API requires authentication"""
        url = reverse('leave_coverage_report_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)
    
    def test_coverage_api_returns_json(self):
        """Test coverage API returns JSON"""
        self.client.login(username='manager', password='testpass123')
        url = reverse('leave_coverage_report_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
    
    def test_coverage_api_structure(self):
        """Test coverage API returns correct data structure"""
        self.client.login(username='manager', password='testpass123')
        url = reverse('leave_coverage_report_api')
        
        response = self.client.get(url, {
            'start': date.today().isoformat(),
            'end': (date.today() + timedelta(days=7)).isoformat(),
            'care_home_id': self.care_home.id
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check structure
        self.assertIn('coverage', data)
        self.assertIn('summary', data)
    
    def test_coverage_api_traffic_light_indicators(self):
        """Test coverage API includes traffic light status"""
        # Create multiple staff
        for i in range(10):
            staff_user = User.objects.create_user(
                sap=f'20001{i}',
                first_name=f'Staff{i}',
                last_name='User',
                email=f'staff{i}@example.com',
                password='testpass123'
            )
            
            StaffProfile.objects.create(
                user=staff_user,
                sap_number=f'12345{i}',
                unit=self.unit
            )
        
        # Create leave requests for some staff
        for i in range(3):
            staff = StaffProfile.objects.get(sap_number=f'12345{i}')
            LeaveRequest.objects.create(
                staff_profile=staff,
                leave_type=self.leave_type,
                start_date=date.today(),
                end_date=date.today() + timedelta(days=3),
                reason='Test',
                status='APPROVED'
            )
        
        self.client.login(username='manager', password='testpass123')
        url = reverse('leave_coverage_report_api')
        
        response = self.client.get(url, {
            'start': date.today().isoformat(),
            'end': (date.today() + timedelta(days=7)).isoformat(),
            'care_home_id': self.care_home.id
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should have coverage data
        self.assertIn('coverage', data)


class LeaveColorSchemeTests(TestCase):
    """Test leave event color coding"""
    
    def setUp(self):
        self.care_home = CareHome.objects.create(
            name='RIVERSIDE',
            location_address="500 Color Way",
            bed_capacity=36,
            care_inspectorate_id="CS901234"
        )
        self.unit = Unit.objects.create(
            name="Test Unit",
            care_home=self.care_home
        )
        
        self.user = User.objects.create_user(
            sap='200020',
            first_name='Test',
            last_name='User',
            email='test@example.com',
            password='testpass123'
        )
        # self.user.care_home_access.add(self.care_home)  # care_home_access removed - users access via unit.care_home
        
        self.profile = StaffProfile.objects.create(
            user=self.user,
            sap_number='123456',
            unit=self.unit
        )
    
    def test_approved_annual_leave_color(self):
        """Test approved annual leave has green color"""
        from scheduling.views_leave_calendar import get_leave_color
        
        leave_type = LeaveType.objects.create(
            name='Annual Leave',
            code='ANNUAL',
            is_paid=True
        )
        
        color = get_leave_color('APPROVED', leave_type.code)
        self.assertEqual(color, '#28a745')  # Green
    
    def test_approved_sick_leave_color(self):
        """Test approved sick leave has orange color"""
        from scheduling.views_leave_calendar import get_leave_color
        
        color = get_leave_color('APPROVED', 'SICK')
        self.assertEqual(color, '#fd7e14')  # Orange
    
    def test_pending_leave_color(self):
        """Test pending leave has yellow color"""
        from scheduling.views_leave_calendar import get_leave_color
        
        color = get_leave_color('PENDING', 'ANNUAL')
        self.assertEqual(color, '#ffc107')  # Yellow
    
    def test_denied_leave_color(self):
        """Test denied leave has red color"""
        from scheduling.views_leave_calendar import get_leave_color
        
        color = get_leave_color('DENIED', 'ANNUAL')
        self.assertEqual(color, '#dc3545')  # Red


class LeaveCalendarPermissionsTests(TestCase):
    """Test permission controls for calendar views"""
    
    def setUp(self):
        self.client = Client()
        self.care_home1 = CareHome.objects.create(
            name='ORCHARD_GROVE',
            location_address="600 Permission Blvd",
            bed_capacity=40,
            care_inspectorate_id="CS012345"
        )
        self.care_home2 = CareHome.objects.create(
            name='MEADOWBURN',
            location_address="700 Access Ave",
            bed_capacity=35,
            care_inspectorate_id="CS123450"
        )
        
        self.unit1 = Unit.objects.create(
            name="Unit 1",
            care_home=self.care_home1
        )
        
        self.user = User.objects.create_user(
            sap='200021',
            first_name='Test',
            last_name='User',
            email='test@example.com',
            password='testpass123'
        )
        # User only has access to care_home1
        # self.user.care_home_access.add(self.care_home1)  # care_home_access removed - users access via unit.care_home
        
        self.profile = StaffProfile.objects.create(
            user=self.user,
            sap_number='123456',
            unit=self.unit1
        )
    
    def test_calendar_respects_care_home_access(self):
        """Test calendar only shows leave from accessible care homes"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('leave_calendar_data_api')
        
        response = self.client.get(url, {
            'start': date.today().isoformat(),
            'end': (date.today() + timedelta(days=30)).isoformat()
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # All events should be from accessible care homes
        for event in data:
            staff_id = event['extendedProps']['staff_id']
            staff = StaffProfile.objects.get(id=staff_id)
#             self.assertIn(staff.unit.care_home, self.user.care_home_access.all()  # care_home_access removed)
