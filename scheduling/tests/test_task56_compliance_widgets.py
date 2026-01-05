"""
Test Suite for Task 56: Compliance Dashboard Widgets
Tests compliance metrics, widgets, and dashboard functionality
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal
from scheduling.models import Unit, TrainingRecord, SupervisionRecord, TrainingCourse
from scheduling.models_multi_home import CareHome
from scheduling.models_compliance_widgets import ComplianceMetric, ComplianceWidget

User = get_user_model()


class ComplianceMetricModelTests(TestCase):
    """Test ComplianceMetric model"""
    
    def setUp(self):
        self.care_home = CareHome.objects.create(
            name="Test Care Home",
            address="123 Test St"
        )
    
    def test_metric_creation(self):
        """Test creating a compliance metric"""
        metric = ComplianceMetric.objects.create(
            care_home=self.care_home,
            category='TRAINING',
            current_value=Decimal('92.5'),
            target_value=Decimal('95.0'),
            compliant_count=37,
            at_risk_count=3,
            non_compliant_count=0,
            total_count=40
        )
        
        self.assertIsNotNone(metric.id)
        self.assertEqual(metric.category, 'TRAINING')
        self.assertEqual(metric.status, 'AMBER')  # 92.5% is 85-94%
    
    def test_traffic_light_status_green(self):
        """Test green status (≥95%)"""
        metric = ComplianceMetric.objects.create(
            care_home=self.care_home,
            category='SUPERVISION',
            current_value=Decimal('96.0'),
            target_value=Decimal('95.0'),
            total_count=100
        )
        
        self.assertEqual(metric.status, 'GREEN')
    
    def test_traffic_light_status_amber(self):
        """Test amber status (85-94%)"""
        metric = ComplianceMetric.objects.create(
            care_home=self.care_home,
            category='WTD',
            current_value=Decimal('88.0'),
            target_value=Decimal('95.0'),
            total_count=100
        )
        
        self.assertEqual(metric.status, 'AMBER')
    
    def test_traffic_light_status_red(self):
        """Test red status (<85%)"""
        metric = ComplianceMetric.objects.create(
            care_home=self.care_home,
            category='INDUCTION',
            current_value=Decimal('75.0'),
            target_value=Decimal('95.0'),
            total_count=100
        )
        
        self.assertEqual(metric.status, 'RED')
    
    def test_trend_calculation(self):
        """Test trend direction calculation"""
        metric = ComplianceMetric.objects.create(
            care_home=self.care_home,
            category='TRAINING',
            current_value=Decimal('95.0'),
            previous_value=Decimal('90.0'),
            target_value=Decimal('95.0'),
            total_count=100
        )
        
        self.assertEqual(metric.trend_direction, 'UP')
        
        # Test downward trend
        metric.current_value = Decimal('85.0')
        metric.previous_value = Decimal('90.0')
        metric.save()
        
        self.assertEqual(metric.trend_direction, 'DOWN')
        
        # Test stable
        metric.current_value = Decimal('90.0')
        metric.previous_value = Decimal('90.0')
        metric.save()
        
        self.assertEqual(metric.trend_direction, 'STABLE')


class ComplianceWidgetModelTests(TestCase):
    """Test ComplianceWidget model"""
    
    def setUp(self):
        self.care_home = CareHome.objects.create(
            name='ORCHARD_GROVE',
            location_address="123 Test St",
            bed_capacity=40,
            care_inspectorate_id="CS123456"
        )
        
        self.user = User.objects.create_user(
            sap='SAP100001',
            email='test@example.com',
            password='testpass123'
        )
        
        self.metric = ComplianceMetric.objects.create(
            care_home=self.care_home,
            category='TRAINING',
            current_value=Decimal('95.0'),
            target_value=Decimal('95.0'),
            total_count=100
        )
    
    def test_widget_creation(self):
        """Test creating a compliance widget"""
        widget = ComplianceWidget.objects.create(
            name='Training Compliance',
            widget_type='SINGLE_METRIC',
            care_home=self.care_home,
            size='MEDIUM',
            created_by=self.user
        )
        widget.metric_ids.add(self.metric)
        
        self.assertIsNotNone(widget.id)
        self.assertEqual(widget.widget_type, 'SINGLE_METRIC')
        self.assertTrue(widget.is_active)
    
    def test_widget_ordering(self):
        """Test widget display ordering"""
        widget1 = ComplianceWidget.objects.create(
            name='Widget 1',
            widget_type='TRAFFIC_LIGHT',
            care_home=self.care_home,
            display_order=1,
            created_by=self.user
        )
        
        widget2 = ComplianceWidget.objects.create(
            name='Widget 2',
            widget_type='TREND_CHART',
            care_home=self.care_home,
            display_order=0,
            created_by=self.user
        )
        
        widgets = ComplianceWidget.objects.filter(care_home=self.care_home).order_by('display_order')
        
        self.assertEqual(widgets.first(), widget2)
    
    def test_auto_refresh_interval(self):
        """Test auto-refresh interval validation"""
        widget = ComplianceWidget.objects.create(
            name='Test Widget',
            widget_type='SINGLE_METRIC',
            care_home=self.care_home,
            auto_refresh_seconds=300,  # 5 minutes
            created_by=self.user
        )
        
        self.assertEqual(widget.auto_refresh_seconds, 300)


class ComplianceDashboardViewTests(TestCase):
    """Test compliance dashboard views"""
    
    def setUp(self):
        self.client = Client()
        self.care_home = CareHome.objects.create(
            name='MEADOWBURN',
            location_address="456 Dashboard Ave",
            bed_capacity=35,
            care_inspectorate_id="CS234567"
        )
        self.unit = Unit.objects.create(
            name="Test Unit",
            care_home=self.care_home
        )
        
        self.user = User.objects.create_user(
            sap='SAP100002',
            email='test@example.com',
            password='testpass123'
        )
        
        StaffProfile.objects.create(
            user=self.user,
            sap_number='123456',
            unit=self.unit,
            permission_level='FULL'
        )
        
        # Create test metric
        self.metric = ComplianceMetric.objects.create(
            care_home=self.care_home,
            category='TRAINING',
            current_value=Decimal('95.0'),
            target_value=Decimal('95.0'),
            total_count=100
        )
        
        # Create test widget
        self.widget = ComplianceWidget.objects.create(
            name='Training Widget',
            widget_type='SINGLE_METRIC',
            care_home=self.care_home,
            created_by=self.user
        )
        self.widget.metric_ids.add(self.metric)
    
    def test_compliance_dashboard_requires_login(self):
        """Test dashboard requires authentication"""
        url = reverse('compliance_dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
    
    def test_compliance_dashboard_authenticated(self):
        """Test dashboard for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('compliance_dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Compliance Dashboard')
    
    def test_widget_data_api(self):
        """Test widget data API endpoint"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('widget_data_api', args=[self.widget.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = response.json()
        self.assertIn('metrics', data)
        self.assertIn('timestamp', data)


class ComplianceCalculationTests(TestCase):
    """Test compliance calculation functions"""
    
    def setUp(self):
        self.care_home = CareHome.objects.create(
            name='HAWTHORN_HOUSE',
            location_address="123 Test St",
            bed_capacity=40,
            care_inspectorate_id="CS345678"
        )
        self.unit = Unit.objects.create(
            name="Test Unit",
            care_home=self.care_home
        )
        
        # Create test staff
        self.user1 = User.objects.create_user(
            sap='SAP100003',
            email='staff1@example.com',
            password='testpass123'
        )
        self.user1.care_home_access.add(self.care_home)
        
        self.profile1 = StaffProfile.objects.create(
            user=self.user1,
            sap_number='123456',
            unit=self.unit
        )
        
        self.user2 = User.objects.create_user(
            sap='SAP100004',
            email='staff2@example.com',
            password='testpass123'
        )
        self.user2.care_home_access.add(self.care_home)
        
        self.profile2 = StaffProfile.objects.create(
            user=self.user2,
            sap_number='234567',
            unit=self.unit
        )
    
    def test_training_compliance_calculation(self):
        """Test training compliance percentage calculation"""
        from scheduling.views_compliance_widgets import calculate_training_compliance
        
        # Create training course
        course = TrainingCourse.objects.create(
            name='Fire Safety',
            category='MANDATORY',
            validity_months=12
        )
        
        # Create training record for staff1 (current)
        TrainingRecord.objects.create(
            staff_profile=self.profile1,
            course=course,
            completion_date=date.today(),
            expiry_date=date.today() + timedelta(days=365),
            status='CURRENT'
        )
        
        # Staff2 has no training (non-compliant)
        
        metric = calculate_training_compliance(self.care_home)
        
        # 1 out of 2 staff compliant = 50%
        self.assertEqual(metric.current_value, Decimal('50.0'))
        self.assertEqual(metric.compliant_count, 1)
        self.assertEqual(metric.non_compliant_count, 1)
        self.assertEqual(metric.total_count, 2)
    
    def test_supervision_compliance_calculation(self):
        """Test supervision compliance calculation"""
        from scheduling.views_compliance_widgets import calculate_supervision_compliance
        
        # Create recent supervision for staff1
        SupervisionRecord.objects.create(
            staff_member=self.profile1,
            supervisor=self.profile1,
            session_date=date.today() - timedelta(days=30),
            session_type='REGULAR'
        )
        
        # Staff2 has no supervision
        
        metric = calculate_supervision_compliance(self.care_home)
        
        # 1 out of 2 staff supervised in last 90 days = 50%
        self.assertEqual(metric.current_value, Decimal('50.0'))


class ComplianceWidgetManagementTests(TestCase):
    """Test widget management (create, edit, delete)"""
    
    def setUp(self):
        self.client = Client()
        self.care_home = CareHome.objects.create(
            name='RIVERSIDE',
            location_address="789 Widget Rd",
            bed_capacity=50,
            care_inspectorate_id="CS456789"
        )
        self.unit = Unit.objects.create(
            name="Test Unit",
            care_home=self.care_home
        )
        
        self.user = User.objects.create_user(
            sap='SAP100005',
            email='manager@example.com',
            password='testpass123'
        )
        self.user.care_home_access.add(self.care_home)
        
        StaffProfile.objects.create(
            user=self.user,
            sap_number='123456',
            unit=self.unit,
            permission_level='FULL'
        )
    
    def test_create_widget_view(self):
        """Test creating a new widget"""
        self.client.login(username='manager', password='testpass123')
        url = reverse('create_widget')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Widget')
    
    def test_delete_widget(self):
        """Test deleting a widget"""
        widget = ComplianceWidget.objects.create(
            name='Test Widget',
            widget_type='SINGLE_METRIC',
            care_home=self.care_home,
            created_by=self.user
        )
        
        self.client.login(username='manager', password='testpass123')
        url = reverse('delete_widget', args=[widget.id])
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Redirect after delete
        
        # Widget should be deleted
        self.assertFalse(ComplianceWidget.objects.filter(id=widget.id).exists())
