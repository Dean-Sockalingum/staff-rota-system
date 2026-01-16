"""
Unit tests for Production Forecast Monitoring

Tests:
- ForecastMonitor.check_forecast_drift()
- ForecastMonitor.calculate_mape()
- ForecastMonitor.should_retrain()
- ForecastMonitor.detect_anomalies()
- ProphetModelMetrics model
"""

from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
import numpy as np
from scheduling.forecast_monitoring import ForecastMonitor
from scheduling.models import CareHome, Unit, ProphetModelMetrics


class ForecastMonitorTestCase(TestCase):
    """Test ForecastMonitor class methods"""
    
    def setUp(self):
        """Create test fixtures"""
        self.monitor = ForecastMonitor(
            mape_threshold=0.30,
            drift_threshold=0.05,
            retrain_days=7
        )
        
        # Create test care home and unit
        self.care_home = CareHome.objects.create(
            name='ORCHARD_GROVE',
            bed_capacity=60,
            current_occupancy=50,
            location_address='123 Test Street',
            postcode='G1 1AA',
            care_inspectorate_id='CS2025000001'
        )
        self.unit = Unit.objects.create(
            name='OG_MULBERRY',
            care_home=self.care_home,
            is_active=True,
            min_day_staff=2,
            min_night_staff=1,
            min_weekend_staff=2
        )
    
    def test_calculate_mape_perfect_forecast(self):
        """MAPE should be 0% for perfect forecasts"""
        actuals = [10, 20, 30, 40, 50]
        forecasts = [10, 20, 30, 40, 50]
        
        mape = self.monitor.calculate_mape(actuals, forecasts)
        
        self.assertEqual(mape, 0.0)
    
    def test_calculate_mape_typical_error(self):
        """MAPE should calculate correctly for typical errors"""
        actuals = [100, 200, 300]
        forecasts = [90, 220, 280]  # 10%, 10%, 6.67% errors
        
        mape = self.monitor.calculate_mape(actuals, forecasts)
        
        # Expected: (10 + 10 + 6.67) / 3 = 8.89%
        self.assertAlmostEqual(mape, 8.89, places=1)
    
    def test_calculate_mape_handles_zeros(self):
        """MAPE should skip zero actuals to avoid division by zero"""
        actuals = [0, 10, 20]
        forecasts = [5, 12, 18]
        
        mape = self.monitor.calculate_mape(actuals, forecasts)
        
        # Should only use [10, 20] actuals: (20% + 10%) / 2 = 15%
        self.assertAlmostEqual(mape, 15.0, places=1)
    
    def test_calculate_mape_empty_arrays(self):
        """MAPE should return None for empty input"""
        mape = self.monitor.calculate_mape([], [])
        
        self.assertIsNone(mape)
    
    def test_check_forecast_drift_no_drift(self):
        """Should not detect drift when distributions match"""
        np.random.seed(42)
        forecasts = np.random.normal(100, 10, 100)
        actuals = np.random.normal(100, 10, 100)
        
        drift_detected, p_value = self.monitor.check_forecast_drift(
            forecasts, actuals, threshold=0.05
        )
        
        self.assertFalse(drift_detected)
        self.assertIsNotNone(p_value)
        self.assertGreater(p_value, 0.05)
    
    def test_check_forecast_drift_with_drift(self):
        """Should detect drift when distributions differ"""
        np.random.seed(42)
        forecasts = np.random.normal(100, 10, 100)
        actuals = np.random.normal(120, 10, 100)  # Shifted mean
        
        drift_detected, p_value = self.monitor.check_forecast_drift(
            forecasts, actuals, threshold=0.05
        )
        
        self.assertTrue(drift_detected)
        self.assertIsNotNone(p_value)
        self.assertLess(p_value, 0.05)
    
    def test_check_forecast_drift_insufficient_data(self):
        """Should not detect drift with <30 observations"""
        forecasts = [100, 105, 110]
        actuals = [95, 100, 105]
        
        drift_detected, p_value = self.monitor.check_forecast_drift(
            forecasts, actuals
        )
        
        self.assertFalse(drift_detected)
        self.assertIsNone(p_value)
    
    def test_detect_anomalies_no_anomalies(self):
        """Should not detect anomalies in normal distribution"""
        np.random.seed(42)
        forecasts = np.random.normal(100, 10, 100)
        
        anomaly_indices = self.monitor.detect_anomalies(forecasts, threshold=1.5)
        
        # Should have very few outliers (< 5%)
        self.assertLess(len(anomaly_indices), 5)
    
    def test_detect_anomalies_with_outliers(self):
        """Should detect anomalies when outliers present"""
        forecasts = [100, 105, 110, 500, 95, 102, -100]  # 500 and -100 are outliers
        
        anomaly_indices = self.monitor.detect_anomalies(forecasts, threshold=1.5)
        
        # Should detect the two outliers
        self.assertGreaterEqual(len(anomaly_indices), 2)
        self.assertIn(3, anomaly_indices)  # 500
        self.assertIn(6, anomaly_indices)  # -100
    
    def test_log_forecast_metrics(self):
        """Should save metrics to database"""
        forecast_date = timezone.now().date()
        
        metrics = self.monitor.log_forecast_metrics(
            care_home=self.care_home,
            unit=self.unit,
            forecast_date=forecast_date,
            actual_value=100.0,
            forecast_value=95.0,
            mape=5.0,
            drift_score=0.25,
            model_version='v1.2024-12-15'
        )
        
        # Verify saved
        self.assertIsNotNone(metrics.id)
        self.assertEqual(metrics.care_home, self.care_home)
        self.assertEqual(metrics.unit, self.unit)
        self.assertEqual(metrics.mape, 5.0)
        self.assertTrue(metrics.is_accurate)  # < 30%
        self.assertFalse(metrics.has_drift)  # p > 0.05
    
    def test_should_retrain_no_metrics(self):
        """Should not retrain when no metrics exist"""
        should_retrain, reason = self.monitor.should_retrain(
            self.care_home, self.unit
        )
        
        self.assertFalse(should_retrain)
        self.assertEqual(reason, "No recent metrics")
    
    def test_should_retrain_mape_degradation(self):
        """Should retrain when MAPE degrades >10%"""
        base_date = timezone.now().date() - timedelta(days=30)
        
        # Create baseline metrics (MAPE = 20%)
        for i in range(10):
            ProphetModelMetrics.objects.create(
                care_home=self.care_home,
                unit=self.unit,
                forecast_date=base_date + timedelta(days=i),
                actual_value=100.0,
                forecast_value=80.0,
                mape=20.0,
                drift_score=0.5,
                model_version='v1',
                model_version_date=base_date
            )
        
        # Create recent metric with degraded MAPE (30%)
        ProphetModelMetrics.objects.create(
            care_home=self.care_home,
            unit=self.unit,
            forecast_date=timezone.now().date(),
            actual_value=100.0,
            forecast_value=70.0,
            mape=30.0,  # 50% increase from baseline
            drift_score=0.5,
            model_version='v1',
            model_version_date=base_date
        )
        
        should_retrain, reason = self.monitor.should_retrain(
            self.care_home, self.unit
        )
        
        self.assertTrue(should_retrain)
        self.assertIn("MAPE increased", reason)


class ProphetModelMetricsTestCase(TestCase):
    """Test ProphetModelMetrics model"""
    
    def setUp(self):
        """Create test fixtures"""
        self.care_home = CareHome.objects.create(
            name='ORCHARD_GROVE',
            bed_capacity=60,
            current_occupancy=50,
            location_address='123 Test Street',
            postcode='G1 1AA',
            care_inspectorate_id='CS2025000001'
        )
        self.unit = Unit.objects.create(
            name='OG_MULBERRY',
            care_home=self.care_home,
            is_active=True,
            min_day_staff=2,
            min_night_staff=1,
            min_weekend_staff=2
        )
    
    def test_create_metric(self):
        """Should create metric with all fields"""
        metric = ProphetModelMetrics.objects.create(
            care_home=self.care_home,
            unit=self.unit,
            forecast_date=timezone.now().date(),
            actual_value=100.0,
            forecast_value=95.0,
            mape=5.0,
            drift_score=0.25,
            model_version='v1.2024-12-15',
            model_version_date=timezone.now().date()
        )
        
        self.assertIsNotNone(metric.id)
        self.assertEqual(metric.care_home, self.care_home)
        self.assertEqual(metric.unit, self.unit)
        self.assertEqual(metric.mape, 5.0)
    
    def test_is_accurate_property(self):
        """Should flag accurate forecasts (MAPE < 30%)"""
        accurate_metric = ProphetModelMetrics.objects.create(
            care_home=self.care_home,
            unit=self.unit,
            forecast_date=timezone.now().date(),
            actual_value=100.0,
            forecast_value=95.0,
            mape=5.0,
            model_version='v1',
            model_version_date=timezone.now().date()
        )
        
        inaccurate_metric = ProphetModelMetrics.objects.create(
            care_home=self.care_home,
            unit=self.unit,
            forecast_date=timezone.now().date(),
            actual_value=100.0,
            forecast_value=50.0,
            mape=50.0,
            model_version='v1',
            model_version_date=timezone.now().date()
        )
        
        self.assertTrue(accurate_metric.is_accurate)
        self.assertFalse(inaccurate_metric.is_accurate)
    
    def test_has_drift_property(self):
        """Should flag drift when p < 0.05"""
        no_drift = ProphetModelMetrics.objects.create(
            care_home=self.care_home,
            unit=self.unit,
            forecast_date=timezone.now().date(),
            actual_value=100.0,
            forecast_value=95.0,
            mape=5.0,
            drift_score=0.25,  # p > 0.05
            model_version='v1',
            model_version_date=timezone.now().date()
        )
        
        with_drift = ProphetModelMetrics.objects.create(
            care_home=self.care_home,
            unit=self.unit,
            forecast_date=timezone.now().date(),
            actual_value=100.0,
            forecast_value=95.0,
            mape=5.0,
            drift_score=0.01,  # p < 0.05
            model_version='v1',
            model_version_date=timezone.now().date()
        )
        
        self.assertFalse(no_drift.has_drift)
        self.assertTrue(with_drift.has_drift)
    
    def test_str_representation(self):
        """Should have readable string representation"""
        metric = ProphetModelMetrics.objects.create(
            care_home=self.care_home,
            unit=self.unit,
            forecast_date=timezone.now().date(),
            actual_value=100.0,
            forecast_value=95.0,
            mape=5.0,
            model_version='v1',
            model_version_date=timezone.now().date()
        )
        
        str_repr = str(metric)
        
        self.assertIn('ORCHARD_GROVE', str_repr)
        self.assertIn('OG_MULBERRY', str_repr)
        self.assertIn('5.0%', str_repr)
