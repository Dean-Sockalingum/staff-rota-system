"""
Tests for Performance KPIs Module
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import KPIAlert, AlertThreshold

User = get_user_model()


class KPIAlertModelTest(TestCase):
    """Test KPIAlert model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            sap='123456',
            password='testpass123',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
    
    def test_create_kpi_alert(self):
        """Test creating a KPI alert"""
        alert = KPIAlert.objects.create(
            title='Test Alert',
            description='Test Description',
            module='MODULE_1',
            metric_name='test_metric',
            current_value=75.50,
            threshold_value=80.00,
            severity='WARNING',
            assigned_to=self.user
        )
        
        self.assertEqual(alert.title, 'Test Alert')
        self.assertEqual(alert.status, 'ACTIVE')
        self.assertTrue(alert.is_active())
    
    def test_acknowledge_alert(self):
        """Test acknowledging an alert"""
        alert = KPIAlert.objects.create(
            title='Test Alert',
            description='Test',
            module='MODULE_1',
            metric_name='test_metric',
            current_value=75.50,
            threshold_value=80.00
        )
        
        alert.acknowledge(self.user)
        self.assertEqual(alert.status, 'ACKNOWLEDGED')
        self.assertEqual(alert.acknowledged_by, self.user)
        self.assertIsNotNone(alert.acknowledged_at)
    
    def test_resolve_alert(self):
        """Test resolving an alert"""
        alert = KPIAlert.objects.create(
            title='Test Alert',
            description='Test',
            module='MODULE_1',
            metric_name='test_metric',
            current_value=75.50,
            threshold_value=80.00
        )
        
        alert.resolve(self.user, 'Fixed the issue')
        self.assertEqual(alert.status, 'RESOLVED')
        self.assertEqual(alert.resolved_by, self.user)
        self.assertEqual(alert.resolution_notes, 'Fixed the issue')
        self.assertIsNotNone(alert.resolved_at)


class AlertThresholdModelTest(TestCase):
    """Test AlertThreshold model functionality"""
    
    def test_create_alert_threshold(self):
        """Test creating an alert threshold"""
        threshold = AlertThreshold.objects.create(
            metric_name='incident_rate',
            display_name='Incident Rate',
            module='MODULE_2',
            warning_threshold=10.00,
            critical_threshold=15.00,
            comparison_operator='GT'
        )
        
        self.assertEqual(threshold.metric_name, 'incident_rate')
        self.assertTrue(threshold.is_active)
    
    def test_check_threshold_greater_than(self):
        """Test threshold checking with GT operator"""
        threshold = AlertThreshold.objects.create(
            metric_name='incident_rate',
            display_name='Incident Rate',
            module='MODULE_2',
            warning_threshold=10.00,
            critical_threshold=15.00,
            comparison_operator='GT'
        )
        
        # Below warning
        result = threshold.check_threshold(5.0)
        self.assertIsNone(result)
        
        # Warning level
        result = threshold.check_threshold(12.0)
        self.assertEqual(result, 'WARNING')
        
        # Critical level
        result = threshold.check_threshold(20.0)
        self.assertEqual(result, 'CRITICAL')
    
    def test_check_threshold_less_than(self):
        """Test threshold checking with LT operator"""
        threshold = AlertThreshold.objects.create(
            metric_name='completion_rate',
            display_name='Completion Rate',
            module='MODULE_4',
            warning_threshold=80.00,
            critical_threshold=70.00,
            comparison_operator='LT'
        )
        
        # Above warning (good)
        result = threshold.check_threshold(85.0)
        self.assertIsNone(result)
        
        # Warning level
        result = threshold.check_threshold(75.0)
        self.assertEqual(result, 'WARNING')
        
        # Critical level
        result = threshold.check_threshold(65.0)
        self.assertEqual(result, 'CRITICAL')
    
    def test_inactive_threshold(self):
        """Test that inactive thresholds don't trigger"""
        threshold = AlertThreshold.objects.create(
            metric_name='test_metric',
            display_name='Test Metric',
            module='MODULE_1',
            warning_threshold=10.00,
            critical_threshold=15.00,
            comparison_operator='GT',
            is_active=False
        )
        
        result = threshold.check_threshold(20.0)
        self.assertIsNone(result)
