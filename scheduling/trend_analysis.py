"""
TASK 30: TREND ANALYSIS ENGINE
Time series decomposition, seasonality detection, anomaly detection, and forecasting
"""

from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import statistics
import json


# ============================================================================
# TIME SERIES DATA COLLECTION
# ============================================================================

def collect_metric_time_series(metric_type, care_home=None, unit=None, start_date=None, end_date=None):
    """
    Collect time series data for a specific metric
    
    Returns: dict with {date: value} mappings
    """
    from .models import User, Shift, Resident, LeaveRequest, Incident, TrainingRecord
    
    if not start_date or not end_date:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=90)
    
    time_series = {}
    current = start_date
    
    while current <= end_date:
        if metric_type == 'STAFF_COUNT':
            qs = User.objects.filter(is_active=True, created_at__lte=current)
            if care_home:
                qs = qs.filter(care_home=care_home)
            if unit:
                qs = qs.filter(unit=unit)
            value = qs.count()
        
        elif metric_type == 'SHIFT_VOLUME':
            qs = Shift.objects.filter(date=current)
            if care_home:
                qs = qs.filter(care_home=care_home)
            if unit:
                qs = qs.filter(unit=unit)
            value = qs.count()
        
        elif metric_type == 'OCCUPANCY':
            from .models import Unit as UnitModel
            units_qs = UnitModel.objects.all()
            if care_home:
                units_qs = units_qs.filter(care_home=care_home)
            if unit:
                units_qs = units_qs.filter(id=unit.id)
            
            capacity = units_qs.aggregate(total=Sum('capacity'))['total'] or 1
            occupied = Resident.objects.filter(
                Q(care_home=care_home) if care_home else Q(),
                Q(unit=unit) if unit else Q(),
                is_active=True,
                admission_date__lte=current
            ).count()
            
            value = (occupied / capacity * 100) if capacity > 0 else 0
        
        elif metric_type == 'AGENCY_USAGE':
            qs = Shift.objects.filter(date=current)
            if care_home:
                qs = qs.filter(care_home=care_home)
            if unit:
                qs = qs.filter(unit=unit)
            
            total = qs.count()
            agency = qs.filter(is_agency=True).count()
            value = (agency / total * 100) if total > 0 else 0
        
        elif metric_type == 'OVERTIME':
            qs = Shift.objects.filter(date=current, shift_classification='OVERTIME')
            if care_home:
                qs = qs.filter(care_home=care_home)
            if unit:
                qs = qs.filter(unit=unit)
            value = qs.count()
        
        elif metric_type == 'LEAVE_REQUESTS':
            qs = LeaveRequest.objects.filter(start_date=current)
            if care_home:
                qs = qs.filter(staff__care_home=care_home)
            if unit:
                qs = qs.filter(staff__unit=unit)
            value = qs.count()
        
        elif metric_type == 'INCIDENTS':
            qs = Incident.objects.filter(incident_date=current)
            if care_home:
                qs = qs.filter(care_home=care_home)
            if unit:
                qs = qs.filter(unit=unit)
            value = qs.count()
        
        else:
            value = 0
        
        time_series[current.strftime('%Y-%m-%d')] = float(value)
        current += timedelta(days=1)
    
    return time_series


# ============================================================================
# STATISTICAL ANALYSIS
# ============================================================================

def calculate_statistics(values):
    """
    Calculate basic statistical measures
    """
    if not values:
        return {}
    
    return {
        'mean': statistics.mean(values),
        'median': statistics.median(values),
        'std_dev': statistics.stdev(values) if len(values) > 1 else 0,
        'variance': statistics.variance(values) if len(values) > 1 else 0,
        'min': min(values),
        'max': max(values),
        'range': max(values) - min(values),
        'count': len(values),
    }


def calculate_linear_regression(x_values, y_values):
    """
    Calculate linear regression slope and R-squared
    
    Returns: (slope, intercept, r_squared)
    """
    if len(x_values) != len(y_values) or len(x_values) < 2:
        return 0, 0, 0
    
    n = len(x_values)
    
    # Calculate means
    mean_x = statistics.mean(x_values)
    mean_y = statistics.mean(y_values)
    
    # Calculate slope
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_values, y_values))
    denominator = sum((x - mean_x) ** 2 for x in x_values)
    
    slope = numerator / denominator if denominator != 0 else 0
    intercept = mean_y - (slope * mean_x)
    
    # Calculate R-squared
    ss_tot = sum((y - mean_y) ** 2 for y in y_values)
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(x_values, y_values))
    
    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
    
    return slope, intercept, r_squared


def determine_trend_direction(slope, r_squared_threshold=0.5):
    """
    Determine trend direction based on slope and R-squared
    """
    if abs(slope) < 0.01:
        return 'STABLE'
    elif slope > 0:
        return 'INCREASING'
    elif slope < 0:
        return 'DECREASING'
    else:
        return 'VOLATILE'


# ============================================================================
# TIME SERIES DECOMPOSITION
# ============================================================================

def moving_average(values, window=7):
    """
    Calculate moving average (trend component)
    """
    if len(values) < window:
        return values
    
    ma = []
    for i in range(len(values)):
        if i < window // 2:
            ma.append(values[i])
        elif i >= len(values) - window // 2:
            ma.append(values[i])
        else:
            start = i - window // 2
            end = i + window // 2 + 1
            ma.append(statistics.mean(values[start:end]))
    
    return ma


def decompose_time_series(time_series_data):
    """
    Decompose time series into trend, seasonal, and residual components
    
    Simple additive decomposition: Y = Trend + Seasonal + Residual
    """
    if not time_series_data:
        return {}
    
    dates = sorted(time_series_data.keys())
    values = [time_series_data[d] for d in dates]
    
    # Calculate trend (moving average)
    trend = moving_average(values, window=7)
    
    # Calculate detrended values
    detrended = [v - t for v, t in zip(values, trend)]
    
    # Extract seasonal component (simple approach - average by day of week)
    from datetime import datetime
    seasonal_by_dow = {i: [] for i in range(7)}
    
    for date_str, detrended_val in zip(dates, detrended):
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        dow = date_obj.weekday()
        seasonal_by_dow[dow].append(detrended_val)
    
    # Average seasonal component per day of week
    seasonal_pattern = {dow: statistics.mean(vals) if vals else 0 for dow, vals in seasonal_by_dow.items()}
    
    # Apply seasonal pattern to full series
    seasonal = []
    for date_str in dates:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        dow = date_obj.weekday()
        seasonal.append(seasonal_pattern[dow])
    
    # Calculate residual
    residual = [v - t - s for v, t, s in zip(values, trend, seasonal)]
    
    return {
        'trend': trend,
        'seasonal': seasonal,
        'residual': residual,
        'seasonal_pattern': seasonal_pattern,
    }


# ============================================================================
# SEASONALITY DETECTION
# ============================================================================

def detect_weekly_seasonality(time_series_data):
    """
    Detect weekly seasonal pattern
    
    Returns: (pattern_data, strength, is_significant)
    """
    from datetime import datetime
    
    # Group by day of week
    by_dow = {i: [] for i in range(7)}
    
    for date_str, value in time_series_data.items():
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        dow = date_obj.weekday()
        by_dow[dow].append(value)
    
    # Calculate averages
    pattern = {}
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    for dow in range(7):
        if by_dow[dow]:
            pattern[day_names[dow]] = statistics.mean(by_dow[dow])
        else:
            pattern[day_names[dow]] = 0
    
    # Calculate strength (coefficient of variation)
    pattern_values = list(pattern.values())
    if pattern_values:
        mean_val = statistics.mean(pattern_values)
        std_val = statistics.stdev(pattern_values) if len(pattern_values) > 1 else 0
        strength = (std_val / mean_val * 100) if mean_val > 0 else 0
    else:
        strength = 0
    
    # Simple significance test (strength > threshold)
    is_significant = strength > 10
    
    # Find peaks and troughs
    if pattern_values:
        max_val = max(pattern_values)
        min_val = min(pattern_values)
        peaks = [day for day, val in pattern.items() if val == max_val]
        troughs = [day for day, val in pattern.items() if val == min_val]
    else:
        peaks = []
        troughs = []
    
    return {
        'pattern': pattern,
        'strength': round(strength, 2),
        'is_significant': is_significant,
        'peaks': peaks,
        'troughs': troughs,
    }


def detect_monthly_seasonality(time_series_data):
    """
    Detect monthly seasonal pattern
    """
    from datetime import datetime
    
    # Group by day of month
    by_dom = {i: [] for i in range(1, 32)}
    
    for date_str, value in time_series_data.items():
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        dom = date_obj.day
        by_dom[dom].append(value)
    
    # Calculate averages
    pattern = {}
    for dom in range(1, 32):
        if by_dom[dom]:
            pattern[f"Day {dom}"] = statistics.mean(by_dom[dom])
    
    if not pattern:
        return {
            'pattern': {},
            'strength': 0,
            'is_significant': False,
            'peaks': [],
            'troughs': [],
        }
    
    # Calculate strength
    pattern_values = list(pattern.values())
    mean_val = statistics.mean(pattern_values)
    std_val = statistics.stdev(pattern_values) if len(pattern_values) > 1 else 0
    strength = (std_val / mean_val * 100) if mean_val > 0 else 0
    
    is_significant = strength > 15
    
    # Find peaks and troughs
    max_val = max(pattern_values)
    min_val = min(pattern_values)
    peaks = [day for day, val in pattern.items() if val == max_val]
    troughs = [day for day, val in pattern.items() if val == min_val]
    
    return {
        'pattern': pattern,
        'strength': round(strength, 2),
        'is_significant': is_significant,
        'peaks': peaks,
        'troughs': troughs,
    }


# ============================================================================
# ANOMALY DETECTION
# ============================================================================

def detect_anomalies_zscore(time_series_data, threshold=2.5):
    """
    Detect anomalies using Z-score method
    
    Z-score > threshold = anomaly
    """
    values = list(time_series_data.values())
    dates = list(time_series_data.keys())
    
    if len(values) < 3:
        return []
    
    mean = statistics.mean(values)
    std_dev = statistics.stdev(values)
    
    anomalies = []
    
    for date, value in zip(dates, values):
        if std_dev > 0:
            z_score = (value - mean) / std_dev
            
            if abs(z_score) > threshold:
                # Determine type
                if z_score > 0:
                    anomaly_type = 'SPIKE'
                else:
                    anomaly_type = 'DROP'
                
                # Determine severity
                if abs(z_score) > 4:
                    severity = 'CRITICAL'
                elif abs(z_score) > 3:
                    severity = 'HIGH'
                elif abs(z_score) > 2.5:
                    severity = 'MEDIUM'
                else:
                    severity = 'LOW'
                
                deviation = value - mean
                deviation_pct = (deviation / mean * 100) if mean != 0 else 0
                
                anomalies.append({
                    'date': date,
                    'type': anomaly_type,
                    'severity': severity,
                    'actual_value': value,
                    'expected_value': mean,
                    'deviation': deviation,
                    'deviation_percentage': deviation_pct,
                    'z_score': z_score,
                    'confidence': min(abs(z_score) / 4 * 100, 100),
                })
    
    return anomalies


def detect_trend_shifts(time_series_data, window=14):
    """
    Detect significant trend shifts
    """
    dates = sorted(time_series_data.keys())
    values = [time_series_data[d] for d in dates]
    
    if len(values) < window * 2:
        return []
    
    shifts = []
    
    # Sliding window to detect shifts
    for i in range(window, len(values) - window):
        before = values[i-window:i]
        after = values[i:i+window]
        
        mean_before = statistics.mean(before)
        mean_after = statistics.mean(after)
        
        shift = mean_after - mean_before
        shift_pct = (shift / mean_before * 100) if mean_before != 0 else 0
        
        # Significant shift threshold
        if abs(shift_pct) > 20:
            shifts.append({
                'date': dates[i],
                'type': 'SHIFT',
                'severity': 'HIGH' if abs(shift_pct) > 50 else 'MEDIUM',
                'actual_value': mean_after,
                'expected_value': mean_before,
                'deviation': shift,
                'deviation_percentage': shift_pct,
                'z_score': None,
                'confidence': min(abs(shift_pct) / 50 * 100, 100),
            })
    
    return shifts


# ============================================================================
# FORECASTING
# ============================================================================

def simple_forecast(time_series_data, days_ahead=7):
    """
    Simple linear extrapolation forecast
    """
    dates = sorted(time_series_data.keys())
    values = [time_series_data[d] for d in dates]
    
    if len(values) < 2:
        return {}
    
    # Linear regression
    x_values = list(range(len(values)))
    slope, intercept, r_squared = calculate_linear_regression(x_values, values)
    
    # Generate forecast
    forecast = {}
    from datetime import datetime, timedelta
    
    last_date = datetime.strptime(dates[-1], '%Y-%m-%d')
    
    for i in range(1, days_ahead + 1):
        future_date = last_date + timedelta(days=i)
        future_x = len(values) + i - 1
        predicted_value = slope * future_x + intercept
        
        forecast[future_date.strftime('%Y-%m-%d')] = max(0, predicted_value)
    
    confidence = r_squared * 100
    
    return {
        'forecast': forecast,
        'confidence': round(confidence, 2),
        'method': 'Linear Regression',
    }


# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================

def run_trend_analysis(metric_type, care_home=None, unit=None, start_date=None, end_date=None):
    """
    Run complete trend analysis
    
    Returns: Dictionary with all analysis results
    """
    # Collect data
    time_series = collect_metric_time_series(metric_type, care_home, unit, start_date, end_date)
    
    if not time_series:
        return {'error': 'No data available for analysis'}
    
    values = list(time_series.values())
    
    # Statistics
    stats = calculate_statistics(values)
    
    # Trend analysis
    x_values = list(range(len(values)))
    slope, intercept, r_squared = calculate_linear_regression(x_values, values)
    trend_direction = determine_trend_direction(slope)
    
    # Decomposition
    decomposition = decompose_time_series(time_series)
    
    # Seasonality
    weekly_pattern = detect_weekly_seasonality(time_series)
    monthly_pattern = detect_monthly_seasonality(time_series)
    
    # Anomalies
    anomalies_zscore = detect_anomalies_zscore(time_series)
    trend_shifts = detect_trend_shifts(time_series)
    all_anomalies = anomalies_zscore + trend_shifts
    
    # Forecast
    forecast_result = simple_forecast(time_series, days_ahead=7)
    
    return {
        'time_series_data': time_series,
        'statistics': stats,
        'trend': {
            'direction': trend_direction,
            'slope': slope,
            'r_squared': r_squared,
        },
        'decomposition': decomposition,
        'seasonality': {
            'weekly': weekly_pattern,
            'monthly': monthly_pattern,
        },
        'anomalies': all_anomalies,
        'forecast': forecast_result,
    }
