"""
Predictive Staffing Model using Machine Learning
Forecasts staffing needs based on historical patterns
"""

from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta, date
from collections import defaultdict
import logging
import json

from .models import Shift, User, CareHome, Unit, ShiftType, LeaveRequest, Vacancy

logger = logging.getLogger(__name__)

# Try to import ML libraries (will be installed)
try:
    import numpy as np
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    import pandas as pd
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logger.warning("ML libraries not available. Install scikit-learn, pandas, numpy for predictions.")


class PredictiveStaffingError(Exception):
    """Custom exception for predictive staffing operations"""
    pass


def get_historical_staffing_data(care_home=None, unit=None, weeks_back=12):
    """
    Retrieve historical staffing data for ML training
    
    Args:
        care_home: CareHome object (optional)
        unit: Unit object (optional)
        weeks_back: Number of weeks of historical data
    
    Returns:
        list: [{date, day_of_week, shifts_count, staff_count, leave_count, occupancy}, ...]
    """
    end_date = timezone.now().date()
    start_date = end_date - timedelta(weeks=weeks_back)
    
    # Build base queryset
    shifts = Shift.objects.filter(date__range=[start_date, end_date])
    
    if unit:
        shifts = shifts.filter(unit=unit)
    elif care_home:
        shifts = shifts.filter(care_home=care_home)
    
    # Group by date
    daily_data = []
    current_date = start_date
    
    while current_date <= end_date:
        day_shifts = shifts.filter(date=current_date)
        
        # Get leave requests for this date
        leave_query = LeaveRequest.objects.filter(
            start_date__lte=current_date,
            end_date__gte=current_date,
            status='approved'
        )
        
        if unit:
            leave_query = leave_query.filter(user__unit=unit)
        elif care_home:
            leave_query = leave_query.filter(user__care_home=care_home)
        
        leave_count = leave_query.count()
        
        # Calculate occupancy (simplified)
        if unit:
            bed_capacity = unit.bed_capacity or 30
        elif care_home:
            bed_capacity = sum(u.bed_capacity or 30 for u in care_home.units.all())
        else:
            bed_capacity = 100  # Default assumption
        
        occupancy = 0.85  # Simplified - in production, get actual resident count
        
        daily_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'day_of_week': current_date.weekday(),  # 0=Monday, 6=Sunday
            'shifts_count': day_shifts.count(),
            'staff_count': day_shifts.values('staff').distinct().count(),
            'leave_count': leave_count,
            'occupancy': occupancy,
            'is_weekend': current_date.weekday() >= 5,
            'month': current_date.month,
            'week_of_year': current_date.isocalendar()[1]
        })
        
        current_date += timedelta(days=1)
    
    return daily_data


def prepare_ml_features(historical_data):
    """
    Prepare features for ML model training
    
    Args:
        historical_data: List of daily data dicts
    
    Returns:
        tuple: (X, y) - features and target arrays
    """
    if not ML_AVAILABLE:
        raise PredictiveStaffingError("ML libraries not installed")
    
    df = pd.DataFrame(historical_data)
    
    # Features: day_of_week, is_weekend, month, week_of_year, leave_count, occupancy
    features = ['day_of_week', 'is_weekend', 'month', 'week_of_year', 'leave_count', 'occupancy']
    
    X = df[features].values
    y = df['shifts_count'].values
    
    return X, y


def train_staffing_model(care_home=None, unit=None, weeks_back=12):
    """
    Train ML model to predict staffing needs
    
    Returns:
        dict: {
            'model': trained model object,
            'scaler': feature scaler,
            'accuracy': model accuracy score,
            'features': list of feature names
        }
    """
    if not ML_AVAILABLE:
        return {
            'error': 'ML libraries not installed. Install scikit-learn, pandas, numpy.',
            'model': None
        }
    
    # Get historical data
    historical_data = get_historical_staffing_data(care_home, unit, weeks_back)
    
    if len(historical_data) < 30:
        return {
            'error': f'Insufficient data: {len(historical_data)} days. Need at least 30 days.',
            'model': None
        }
    
    # Prepare features
    X, y = prepare_ml_features(historical_data)
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train Random Forest model (better for non-linear patterns)
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        min_samples_split=5
    )
    
    model.fit(X_scaled, y)
    
    # Calculate model score
    accuracy = model.score(X_scaled, y)
    
    features = ['day_of_week', 'is_weekend', 'month', 'week_of_year', 'leave_count', 'occupancy']
    
    return {
        'model': model,
        'scaler': scaler,
        'accuracy': round(accuracy * 100, 2),
        'features': features,
        'training_samples': len(historical_data),
        'error': None
    }


def predict_staffing_needs(target_date, care_home=None, unit=None, leave_count=0):
    """
    Predict staffing needs for a specific date
    
    Args:
        target_date: date object
        care_home: CareHome object (optional)
        unit: Unit object (optional)
        leave_count: Expected number of staff on leave
    
    Returns:
        dict: {
            'predicted_shifts': int,
            'confidence': float,
            'recommendation': str,
            'current_scheduled': int,
            'gap': int
        }
    """
    if not ML_AVAILABLE:
        # Fallback to rule-based prediction
        return rule_based_prediction(target_date, care_home, unit, leave_count)
    
    # Train model
    model_data = train_staffing_model(care_home, unit)
    
    if model_data['error']:
        # Fallback to rule-based
        return rule_based_prediction(target_date, care_home, unit, leave_count)
    
    model = model_data['model']
    scaler = model_data['scaler']
    
    # Prepare features for target date
    features = np.array([[
        target_date.weekday(),  # day_of_week
        1 if target_date.weekday() >= 5 else 0,  # is_weekend
        target_date.month,  # month
        target_date.isocalendar()[1],  # week_of_year
        leave_count,  # leave_count
        0.85  # occupancy (default assumption)
    ]])
    
    # Scale features
    features_scaled = scaler.transform(features)
    
    # Predict
    prediction = model.predict(features_scaled)[0]
    predicted_shifts = int(round(prediction))
    
    # Get current scheduled shifts
    current_shifts = Shift.objects.filter(date=target_date)
    
    if unit:
        current_shifts = current_shifts.filter(unit=unit)
    elif care_home:
        current_shifts = current_shifts.filter(care_home=care_home)
    
    current_scheduled = current_shifts.count()
    gap = predicted_shifts - current_scheduled
    
    # Generate recommendation
    if gap > 5:
        recommendation = f"⚠️ Under-staffed: Need {gap} more shifts. Consider hiring agency staff."
    elif gap > 0:
        recommendation = f"ℹ️ Slightly under-staffed: Need {gap} more shifts."
    elif gap < -5:
        recommendation = f"✅ Over-staffed: {abs(gap)} excess shifts. Consider reducing overtime."
    elif gap < 0:
        recommendation = f"✅ Slightly over-staffed: {abs(gap)} excess shifts."
    else:
        recommendation = "✅ Optimal staffing level."
    
    # Confidence based on model accuracy
    confidence = model_data['accuracy']
    
    return {
        'predicted_shifts': predicted_shifts,
        'confidence': confidence,
        'recommendation': recommendation,
        'current_scheduled': current_scheduled,
        'gap': gap,
        'model_accuracy': model_data['accuracy'],
        'training_samples': model_data['training_samples']
    }


def rule_based_prediction(target_date, care_home=None, unit=None, leave_count=0):
    """
    Fallback rule-based prediction when ML is not available
    
    Returns:
        dict: Similar to ML prediction
    """
    # Get historical average for same day of week
    day_of_week = target_date.weekday()
    
    # Look at past 8 weeks of same day
    historical_dates = []
    check_date = target_date - timedelta(weeks=8)
    
    while check_date < target_date:
        if check_date.weekday() == day_of_week:
            historical_dates.append(check_date)
        check_date += timedelta(days=1)
    
    # Get shift counts for those dates
    shifts = Shift.objects.filter(date__in=historical_dates)
    
    if unit:
        shifts = shifts.filter(unit=unit)
    elif care_home:
        shifts = shifts.filter(care_home=care_home)
    
    # Calculate average
    if historical_dates:
        avg_shifts = shifts.count() / len(historical_dates)
    else:
        # Default assumption: 20 shifts per day
        avg_shifts = 20
    
    # Adjust for leave
    predicted_shifts = int(round(avg_shifts + leave_count * 1.2))  # Need 1.2 shifts per leave
    
    # Get current scheduled
    current_shifts = Shift.objects.filter(date=target_date)
    
    if unit:
        current_shifts = current_shifts.filter(unit=unit)
    elif care_home:
        current_shifts = current_shifts.filter(care_home=care_home)
    
    current_scheduled = current_shifts.count()
    gap = predicted_shifts - current_scheduled
    
    # Generate recommendation
    if gap > 5:
        recommendation = f"⚠️ Under-staffed: Need {gap} more shifts (rule-based estimate)."
    elif gap > 0:
        recommendation = f"ℹ️ Slightly under-staffed: Need {gap} more shifts (rule-based estimate)."
    elif gap < -5:
        recommendation = "✅ Over-staffed (rule-based estimate)."
    elif gap < 0:
        recommendation = "✅ Slightly over-staffed (rule-based estimate)."
    else:
        recommendation = "✅ Optimal staffing level (rule-based estimate)."
    
    return {
        'predicted_shifts': predicted_shifts,
        'confidence': 70.0,  # Lower confidence for rule-based
        'recommendation': recommendation,
        'current_scheduled': current_scheduled,
        'gap': gap,
        'model_accuracy': 70.0,
        'training_samples': len(historical_dates),
        'method': 'rule_based'
    }


def predict_week_staffing(start_date, care_home=None, unit=None):
    """
    Predict staffing needs for entire week
    
    Args:
        start_date: Monday of the week
        care_home: CareHome object (optional)
        unit: Unit object (optional)
    
    Returns:
        list: [{date, predicted, scheduled, gap, recommendation}, ...]
    """
    predictions = []
    
    # Get expected leave for the week
    leave_requests = LeaveRequest.objects.filter(
        start_date__lte=start_date + timedelta(days=6),
        end_date__gte=start_date,
        status='approved'
    )
    
    if unit:
        leave_requests = leave_requests.filter(user__unit=unit)
    elif care_home:
        leave_requests = leave_requests.filter(user__care_home=care_home)
    
    # Count leave per day
    leave_per_day = defaultdict(int)
    for leave in leave_requests:
        current = max(leave.start_date, start_date)
        end = min(leave.end_date, start_date + timedelta(days=6))
        
        while current <= end:
            leave_per_day[current] += 1
            current += timedelta(days=1)
    
    # Predict for each day
    for i in range(7):
        target_date = start_date + timedelta(days=i)
        leave_count = leave_per_day.get(target_date, 0)
        
        prediction = predict_staffing_needs(target_date, care_home, unit, leave_count)
        
        predictions.append({
            'date': target_date.strftime('%Y-%m-%d'),
            'day_name': target_date.strftime('%A'),
            'predicted_shifts': prediction['predicted_shifts'],
            'current_scheduled': prediction['current_scheduled'],
            'gap': prediction['gap'],
            'recommendation': prediction['recommendation'],
            'leave_count': leave_count,
            'confidence': prediction['confidence']
        })
    
    return predictions


def get_staffing_recommendations(care_home=None, unit=None, days_ahead=14):
    """
    Get staffing recommendations for upcoming days
    
    Returns:
        dict: {
            'urgent': [{date, gap, recommendation}, ...],
            'warnings': [{date, gap, recommendation}, ...],
            'optimal': [{date}, ...],
            'summary': {total_gap, avg_confidence, critical_days}
        }
    """
    today = timezone.now().date()
    end_date = today + timedelta(days=days_ahead)
    
    urgent = []
    warnings = []
    optimal = []
    total_gap = 0
    confidences = []
    
    current = today
    while current <= end_date:
        prediction = predict_staffing_needs(current, care_home, unit)
        
        gap = prediction['gap']
        total_gap += gap
        confidences.append(prediction['confidence'])
        
        entry = {
            'date': current.strftime('%Y-%m-%d'),
            'day_name': current.strftime('%A'),
            'gap': gap,
            'predicted': prediction['predicted_shifts'],
            'scheduled': prediction['current_scheduled'],
            'recommendation': prediction['recommendation']
        }
        
        if gap > 5:
            urgent.append(entry)
        elif gap > 0 or gap < -5:
            warnings.append(entry)
        else:
            optimal.append(entry)
        
        current += timedelta(days=1)
    
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    
    return {
        'urgent': urgent,
        'warnings': warnings,
        'optimal': optimal,
        'summary': {
            'total_gap': total_gap,
            'avg_confidence': round(avg_confidence, 2),
            'critical_days': len(urgent),
            'days_analyzed': days_ahead + 1
        }
    }


def get_feature_importance(care_home=None, unit=None):
    """
    Get feature importance from trained model
    
    Returns:
        list: [{feature, importance}, ...]
    """
    if not ML_AVAILABLE:
        return []
    
    model_data = train_staffing_model(care_home, unit)
    
    if model_data['error'] or not model_data['model']:
        return []
    
    model = model_data['model']
    features = model_data['features']
    
    # Get feature importances
    importances = model.feature_importances_
    
    feature_importance = [
        {
            'feature': features[i],
            'importance': round(importances[i] * 100, 2),
            'description': get_feature_description(features[i])
        }
        for i in range(len(features))
    ]
    
    # Sort by importance
    feature_importance.sort(key=lambda x: x['importance'], reverse=True)
    
    return feature_importance


def get_feature_description(feature_name):
    """Get human-readable description of feature"""
    descriptions = {
        'day_of_week': 'Day of the week (Mon-Sun)',
        'is_weekend': 'Weekend indicator',
        'month': 'Month of the year',
        'week_of_year': 'Week number in year',
        'leave_count': 'Staff on approved leave',
        'occupancy': 'Bed occupancy rate'
    }
    return descriptions.get(feature_name, feature_name)


def get_ml_model_stats(care_home=None, unit=None):
    """
    Get statistics about the ML model
    
    Returns:
        dict: Model performance metrics
    """
    if not ML_AVAILABLE:
        return {
            'available': False,
            'error': 'ML libraries not installed'
        }
    
    model_data = train_staffing_model(care_home, unit)
    
    if model_data['error']:
        return {
            'available': False,
            'error': model_data['error']
        }
    
    return {
        'available': True,
        'accuracy': model_data['accuracy'],
        'training_samples': model_data['training_samples'],
        'features_count': len(model_data['features']),
        'model_type': 'Random Forest Regressor',
        'estimators': 100,
        'feature_importance': get_feature_importance(care_home, unit)
    }


def detect_staffing_patterns(care_home=None, unit=None, weeks_back=12):
    """
    Detect patterns in historical staffing data
    
    Returns:
        dict: {
            'busiest_day': str,
            'quietest_day': str,
            'avg_weekend_vs_weekday': float,
            'seasonal_trend': str,
            'peak_hours': list
        }
    """
    historical_data = get_historical_staffing_data(care_home, unit, weeks_back)
    
    if not historical_data:
        return {
            'error': 'No historical data available'
        }
    
    # Group by day of week
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_totals = defaultdict(list)
    
    for entry in historical_data:
        day_totals[entry['day_of_week']].append(entry['shifts_count'])
    
    # Calculate averages
    day_averages = {
        day_names[day]: sum(counts) / len(counts) if counts else 0
        for day, counts in day_totals.items()
    }
    
    # Find busiest and quietest
    busiest_day = max(day_averages.items(), key=lambda x: x[1])[0] if day_averages else 'Unknown'
    quietest_day = min(day_averages.items(), key=lambda x: x[1])[0] if day_averages else 'Unknown'
    
    # Weekend vs weekday
    weekday_shifts = [e['shifts_count'] for e in historical_data if not e['is_weekend']]
    weekend_shifts = [e['shifts_count'] for e in historical_data if e['is_weekend']]
    
    avg_weekday = sum(weekday_shifts) / len(weekday_shifts) if weekday_shifts else 0
    avg_weekend = sum(weekend_shifts) / len(weekend_shifts) if weekend_shifts else 0
    
    weekend_vs_weekday_ratio = (avg_weekend / avg_weekday * 100) if avg_weekday > 0 else 100
    
    # Seasonal trend (simplified)
    monthly_totals = defaultdict(list)
    for entry in historical_data:
        monthly_totals[entry['month']].append(entry['shifts_count'])
    
    monthly_averages = {
        month: sum(counts) / len(counts)
        for month, counts in monthly_totals.items()
    }
    
    if monthly_averages:
        highest_month = max(monthly_averages.items(), key=lambda x: x[1])[0]
        seasonal_trend = f"Peak staffing in month {highest_month}"
    else:
        seasonal_trend = "Insufficient data for seasonal analysis"
    
    return {
        'busiest_day': busiest_day,
        'quietest_day': quietest_day,
        'avg_weekday': round(avg_weekday, 1),
        'avg_weekend': round(avg_weekend, 1),
        'weekend_vs_weekday_ratio': round(weekend_vs_weekday_ratio, 1),
        'seasonal_trend': seasonal_trend,
        'day_averages': {k: round(v, 1) for k, v in day_averages.items()}
    }
