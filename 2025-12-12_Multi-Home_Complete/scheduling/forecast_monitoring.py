"""
Production Monitoring for Prophet Forecasting Models

Monitors forecast performance and triggers automated retraining:
- Drift detection (KS test)
- MAPE tracking and degradation alerts
- Weekly automated retraining
- Anomaly detection
"""

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Avg
from datetime import datetime, timedelta
import numpy as np
from scipy.stats import ks_2samp
import logging

logger = logging.getLogger(__name__)


class ForecastMonitor:
    """
    Monitor Prophet forecasting model performance in production
    
    Features:
    - Drift detection (distribution shifts in forecasts)
    - MAPE calculation and tracking
    - Automated retrain triggering
    - Anomaly detection
    - Performance logging to database
    """
    
    def __init__(self, mape_threshold=0.30, drift_threshold=0.05, retrain_days=7):
        """
        Initialize monitor
        
        Args:
            mape_threshold: MAPE threshold for retraining (default: 0.30 = 30%)
            drift_threshold: KS test p-value threshold (default: 0.05)
            retrain_days: Days between automatic retrains (default: 7)
        """
        self.mape_threshold = mape_threshold
        self.drift_threshold = drift_threshold
        self.retrain_days = retrain_days
    
    def check_forecast_drift(self, recent_forecasts, recent_actuals, threshold=0.05):
        """
        Detect if forecast distribution has shifted significantly
        
        Uses Kolmogorov-Smirnov test to compare:
        - Recent forecasts vs recent actuals
        - If p-value < threshold → drift detected
        
        Args:
            recent_forecasts: Array of recent forecast values
            recent_actuals: Array of recent actual values
            threshold: KS test p-value threshold (default: 0.05)
        
        Returns: (drift_detected: bool, p_value: float)
        """
        if len(recent_forecasts) < 30 or len(recent_actuals) < 30:
            return False, None  # Not enough data
        
        statistic, p_value = ks_2samp(recent_forecasts, recent_actuals)
        drift_detected = p_value < threshold
        
        return drift_detected, p_value
    
    def calculate_mape(self, actuals, forecasts):
        """
        Mean Absolute Percentage Error
        
        MAPE = mean(|actual - forecast| / actual) * 100
        
        Handles edge cases:
        - Zero actuals (skip to avoid division by zero)
        - Empty arrays (return None)
        
        Args:
            actuals: Array of actual values
            forecasts: Array of forecast values
        
        Returns: MAPE percentage (e.g., 25.1) or None
        """
        actuals = np.array(actuals)
        forecasts = np.array(forecasts)
        
        # Remove zeros to avoid division by zero
        non_zero_mask = actuals != 0
        actuals = actuals[non_zero_mask]
        forecasts = forecasts[non_zero_mask]
        
        if len(actuals) == 0:
            return None
        
        mape = np.mean(np.abs((actuals - forecasts) / actuals)) * 100
        return round(mape, 2)
    
    def should_retrain(self, care_home, unit, mape_threshold=0.30, drift_threshold=0.05):
        """
        Determine if model needs retraining based on:
        1. MAPE exceeds threshold (accuracy degraded >10%)
        2. Significant drift detected (KS test p < 0.05)
        3. Weekly retraining schedule (every 7 days)
        
        Args:
            care_home: CareHome instance
            unit: Unit instance
            mape_threshold: MAPE threshold (default: 0.30 = 30%)
            drift_threshold: KS test p-value threshold (default: 0.05)
        
        Returns: (should_retrain: bool, reason: str)
        """
        # Get recent performance from database
        recent_metrics = self.get_recent_performance(care_home, unit, days=30)
        
        if len(recent_metrics) == 0:
            return False, "No recent metrics"
        
        # Check 1: MAPE threshold
        latest_mape = recent_metrics.latest('forecast_date').mape
        baseline_mape = recent_metrics.order_by('forecast_date')[:10].aggregate(Avg('mape'))['mape__avg']
        
        if latest_mape > baseline_mape * 1.10:  # 10% degradation
            return True, f"MAPE increased from {baseline_mape:.1f}% to {latest_mape:.1f}%"
        
        # Check 2: Drift detection
        recent_forecasts = list(recent_metrics.values_list('forecast_value', flat=True))
        recent_actuals = list(recent_metrics.values_list('actual_value', flat=True))
        drift_detected, p_value = self.check_forecast_drift(recent_forecasts, recent_actuals)
        
        if drift_detected:
            return True, f"Significant drift detected (p={p_value:.4f})"
        
        # Check 3: Weekly schedule
        last_train_date = recent_metrics.latest('forecast_date').model_version_date
        days_since_train = (timezone.now().date() - last_train_date).days
        
        if days_since_train >= self.retrain_days:
            return True, f"Scheduled retrain ({days_since_train} days since last train)"
        
        return False, "Model performance stable"
    
    def log_forecast_metrics(self, care_home, unit, forecast_date, actual_value, forecast_value, 
                            mape, drift_score, model_version):
        """
        Save forecast performance metrics to ProphetModelMetrics table
        
        Creates audit trail for:
        - Forecast accuracy over time
        - Drift patterns
        - Model version tracking
        
        Args:
            care_home: CareHome instance
            unit: Unit instance
            forecast_date: Date the forecast was made for
            actual_value: Actual number of shifts
            forecast_value: Predicted number of shifts
            mape: MAPE for this forecast
            drift_score: KS test p-value
            model_version: Model version identifier
        
        Returns: ProphetModelMetrics instance
        """
        from scheduling.models import ProphetModelMetrics
        
        metrics = ProphetModelMetrics.objects.create(
            care_home=care_home,
            unit=unit,
            forecast_date=forecast_date,
            actual_value=actual_value,
            forecast_value=forecast_value,
            mape=mape,
            drift_score=drift_score,
            model_version=model_version,
            model_version_date=timezone.now().date()
        )
        
        return metrics
    
    def get_recent_performance(self, care_home, unit, days=30):
        """
        Retrieve last N days of forecast metrics
        
        Args:
            care_home: CareHome instance
            unit: Unit instance
            days: Number of days to retrieve (default: 30)
        
        Returns: QuerySet of ProphetModelMetrics
        """
        from scheduling.models import ProphetModelMetrics
        
        cutoff_date = timezone.now().date() - timedelta(days=days)
        
        return ProphetModelMetrics.objects.filter(
            care_home=care_home,
            unit=unit,
            forecast_date__gte=cutoff_date
        ).order_by('forecast_date')
    
    def detect_anomalies(self, forecasts, method='iqr', threshold=1.5):
        """
        Detect anomalous forecasts using IQR method
        
        Anomaly = value outside [Q1 - 1.5*IQR, Q3 + 1.5*IQR]
        
        Args:
            forecasts: Array of forecast values
            method: Detection method (default: 'iqr')
            threshold: IQR multiplier (default: 1.5)
        
        Returns: List of indices where forecasts are anomalous
        """
        forecasts = np.array(forecasts)
        
        Q1 = np.percentile(forecasts, 25)
        Q3 = np.percentile(forecasts, 75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        
        anomaly_indices = np.where((forecasts < lower_bound) | (forecasts > upper_bound))[0]
        
        return anomaly_indices.tolist()
