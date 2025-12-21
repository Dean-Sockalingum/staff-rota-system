"""
Forecasting Dashboard Views - ML Phase 3
Task 11: Dashboard Visualization

Provides Prophet-based staffing forecasts with:
- 30-day demand predictions with confidence intervals
- Predicted vs actual comparison
- High-risk uncertainty alerts
- Unit performance metrics (MAE, MAPE)

Scottish Design Principles:
- Evidence-Based: MAE/MAPE metrics for model validation
- Transparent: Prophet components (trend/weekly/yearly) visible
- User-Centered: OM/SM-focused interface with actionable alerts
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Avg, Count, F, Q, Max, Min
from django.http import JsonResponse
from datetime import date, datetime, timedelta
from collections import defaultdict
import json

from .models import Shift, Unit, StaffingForecast
from .models_multi_home import CareHome


def is_operations_or_senior_manager(user):
    """Check if user has OM/SM permissions"""
    if not user.is_authenticated:
        return False
    if user.role is None:
        return False
    return (
        user.role.is_operations_manager or 
        user.role.is_senior_management_team
    )


@login_required
@user_passes_test(is_operations_or_senior_manager)
def forecasting_dashboard(request):
    """
    Main forecasting dashboard for OM/SM users.
    
    Features:
    1. 30-day forecast view with confidence intervals
    2. High-risk alerts (uncertainty > 50%)
    3. Care home/unit filters
    4. Date range selection
    """
    # Get filter parameters
    care_home_filter = request.GET.get('care_home', '')
    unit_filter = request.GET.get('unit', '')
    days_ahead = int(request.GET.get('days_ahead', 7))  # Default 7 days
    
    # Date range
    today = date.today()
    start_date = today
    end_date = today + timedelta(days=days_ahead)
    
    # Base queryset
    forecasts_qs = StaffingForecast.objects.filter(
        forecast_date__gte=start_date,
        forecast_date__lte=end_date
    ).select_related('care_home', 'unit')
    
    # Apply filters
    if care_home_filter:
        forecasts_qs = forecasts_qs.filter(care_home__name=care_home_filter)
    elif request.user.care_home:
        # Filter to user's assigned care home
        forecasts_qs = forecasts_qs.filter(care_home=request.user.care_home)
    
    if unit_filter:
        forecasts_qs = forecasts_qs.filter(unit__name=unit_filter)
    
    forecasts = forecasts_qs.order_by('forecast_date', 'unit__name')
    
    # Calculate high-risk alerts (uncertainty > 50% of prediction)
    alerts = []
    for forecast in forecasts:
        uncertainty_pct = (
            (forecast.confidence_upper - forecast.confidence_lower) / 
            float(forecast.predicted_shifts)
        ) if forecast.predicted_shifts > 0 else 0
        
        if uncertainty_pct > 0.5:
            alerts.append({
                'date': forecast.forecast_date,
                'care_home': forecast.care_home.get_name_display(),
                'unit': forecast.unit.name,
                'predicted': float(forecast.predicted_shifts),
                'ci_lower': float(forecast.confidence_lower),
                'ci_upper': float(forecast.confidence_upper),
                'uncertainty_pct': uncertainty_pct * 100,
            })
    
    # Get available care homes and units for filters
    care_homes = CareHome.objects.all().order_by('name')
    units = Unit.objects.all().order_by('name')
    if care_home_filter:
        units = units.filter(care_home__name=care_home_filter)
    elif request.user.care_home:
        units = units.filter(care_home=request.user.care_home)
    
    # Prepare chart data (JSON for Chart.js)
    chart_data = prepare_forecast_chart_data(forecasts)
    
    # Summary statistics
    total_forecasts = forecasts.count()
    avg_predicted = forecasts.aggregate(avg=Avg('predicted_shifts'))['avg'] or 0
    avg_mape = forecasts.aggregate(avg=Avg('mape'))['avg'] or 0
    
    context = {
        'forecasts': forecasts,
        'alerts': alerts,
        'care_homes': care_homes,
        'units': units,
        'selected_care_home': care_home_filter,
        'selected_unit': unit_filter,
        'days_ahead': days_ahead,
        'start_date': start_date,
        'end_date': end_date,
        'chart_data': chart_data,
        'total_forecasts': total_forecasts,
        'avg_predicted': round(avg_predicted, 1),
        'avg_mape': round(avg_mape, 1),
        'alert_count': len(alerts),
    }
    
    return render(request, 'scheduling/forecasting_dashboard.html', context)


@login_required
@user_passes_test(is_operations_or_senior_manager)
def forecast_accuracy_view(request):
    """
    Predicted vs Actual comparison for past forecasts.
    
    Shows:
    - Historical forecast accuracy
    - MAE/MAPE trends over time
    - Forecasts falling outside confidence intervals
    - Unit performance rankings
    """
    # Get filter parameters
    care_home_filter = request.GET.get('care_home', '')
    unit_filter = request.GET.get('unit', '')
    lookback_days = int(request.GET.get('lookback_days', 30))
    
    # Date range (past dates only)
    today = date.today()
    start_date = today - timedelta(days=lookback_days)
    end_date = today - timedelta(days=1)  # Yesterday
    
    # Get forecasts
    forecasts_qs = StaffingForecast.objects.filter(
        forecast_date__gte=start_date,
        forecast_date__lte=end_date
    ).select_related('care_home', 'unit')
    
    # Apply filters
    if care_home_filter:
        forecasts_qs = forecasts_qs.filter(care_home__name=care_home_filter)
    elif request.user.care_home:
        forecasts_qs = forecasts_qs.filter(care_home=request.user.care_home)
    
    if unit_filter:
        forecasts_qs = forecasts_qs.filter(unit__name=unit_filter)
    
    forecasts = forecasts_qs.order_by('forecast_date', 'unit__name')
    
    # Compare with actual shifts
    comparisons = []
    accuracy_stats = {
        'total_comparisons': 0,
        'within_ci': 0,
        'outside_ci': 0,
        'mae_sum': 0,
        'mape_sum': 0,
    }
    
    for forecast in forecasts:
        # Get actual shifts for this date/unit
        actual_count = Shift.objects.filter(
            care_home=forecast.care_home,
            unit=forecast.unit,
            shift_date=forecast.forecast_date
        ).count()
        
        # Calculate error
        predicted = float(forecast.predicted_shifts)
        error = actual_count - predicted
        abs_error = abs(error)
        pct_error = (abs_error / actual_count * 100) if actual_count > 0 else 0
        
        # Check if within CI
        within_ci = forecast.is_actual_within_ci(actual_count)
        
        comparisons.append({
            'date': forecast.forecast_date,
            'care_home': forecast.care_home.get_name_display(),
            'unit': forecast.unit.name,
            'predicted': predicted,
            'actual': actual_count,
            'error': error,
            'abs_error': abs_error,
            'pct_error': round(pct_error, 1),
            'ci_lower': float(forecast.confidence_lower),
            'ci_upper': float(forecast.confidence_upper),
            'within_ci': within_ci,
        })
        
        # Update stats
        accuracy_stats['total_comparisons'] += 1
        if within_ci:
            accuracy_stats['within_ci'] += 1
        else:
            accuracy_stats['outside_ci'] += 1
        accuracy_stats['mae_sum'] += abs_error
        accuracy_stats['mape_sum'] += pct_error
    
    # Calculate averages
    if accuracy_stats['total_comparisons'] > 0:
        avg_mae = accuracy_stats['mae_sum'] / accuracy_stats['total_comparisons']
        avg_mape = accuracy_stats['mape_sum'] / accuracy_stats['total_comparisons']
        ci_coverage = (accuracy_stats['within_ci'] / accuracy_stats['total_comparisons']) * 100
    else:
        avg_mae = 0
        avg_mape = 0
        ci_coverage = 0
    
    # Get available care homes and units for filters
    care_homes = CareHome.objects.all().order_by('name')
    units = Unit.objects.all().order_by('name')
    if care_home_filter:
        units = units.filter(care_home__name=care_home_filter)
    elif request.user.care_home:
        units = units.filter(care_home=request.user.care_home)
    
    # Prepare chart data
    accuracy_chart_data = prepare_accuracy_chart_data(comparisons)
    
    context = {
        'comparisons': comparisons,
        'care_homes': care_homes,
        'units': units,
        'selected_care_home': care_home_filter,
        'selected_unit': unit_filter,
        'lookback_days': lookback_days,
        'start_date': start_date,
        'end_date': end_date,
        'total_comparisons': accuracy_stats['total_comparisons'],
        'avg_mae': round(avg_mae, 2),
        'avg_mape': round(avg_mape, 1),
        'ci_coverage': round(ci_coverage, 1),
        'within_ci_count': accuracy_stats['within_ci'],
        'outside_ci_count': accuracy_stats['outside_ci'],
        'chart_data': accuracy_chart_data,
    }
    
    return render(request, 'scheduling/forecast_accuracy.html', context)


@login_required
@user_passes_test(is_operations_or_senior_manager)
def unit_performance_view(request):
    """
    Unit-level model performance heatmap.
    
    Shows:
    - MAPE by care home and unit
    - Best/worst performing models
    - Units requiring retraining
    - Component analysis (trend, weekly, yearly)
    """
    care_home_filter = request.GET.get('care_home', '')
    
    # Get all forecasts with metrics
    forecasts_qs = StaffingForecast.objects.filter(
        mape__isnull=False
    ).select_related('care_home', 'unit')
    
    # Apply filters
    if care_home_filter:
        forecasts_qs = forecasts_qs.filter(care_home__name=care_home_filter)
    elif request.user.care_home:
        forecasts_qs = forecasts_qs.filter(care_home=request.user.care_home)
    
    # Aggregate by unit
    unit_performance = forecasts_qs.values(
        'care_home__name',
        'unit__name'
    ).annotate(
        avg_mape=Avg('mape'),
        avg_mae=Avg('mae'),
        avg_predicted=Avg('predicted_shifts'),
        forecast_count=Count('id'),
        avg_uncertainty=Avg(F('confidence_upper') - F('confidence_lower'))
    ).order_by('avg_mape')
    
    # Convert to list for easier template rendering
    performance_list = []
    for perf in unit_performance:
        # Get CareHome object to call get_name_display()
        care_home_obj = CareHome.objects.get(name=perf['care_home__name'])
        performance_list.append({
            'care_home': care_home_obj.get_name_display(),
            'unit': perf['unit__name'],
            'avg_mape': round(perf['avg_mape'], 1),
            'avg_mae': round(perf['avg_mae'], 2),
            'avg_predicted': round(perf['avg_predicted'], 1),
            'avg_uncertainty': round(perf['avg_uncertainty'], 1),
            'forecast_count': perf['forecast_count'],
            'quality': get_quality_rating(perf['avg_mape']),
        })
    
    # Get best and worst performers
    best_performers = performance_list[:5] if performance_list else []
    worst_performers = performance_list[-5:] if len(performance_list) >= 5 else []
    worst_performers.reverse()  # Highest MAPE first
    
    # Get available care homes for filters
    care_homes = CareHome.objects.all().order_by('name')
    
    # Prepare heatmap data
    heatmap_data = prepare_performance_heatmap_data(performance_list)
    
    context = {
        'performance_list': performance_list,
        'best_performers': best_performers,
        'worst_performers': worst_performers,
        'care_homes': care_homes,
        'selected_care_home': care_home_filter,
        'heatmap_data': heatmap_data,
        'total_units': len(performance_list),
    }
    
    return render(request, 'scheduling/unit_performance.html', context)


def prepare_forecast_chart_data(forecasts):
    """
    Prepare JSON data for Chart.js forecast visualization.
    
    Returns:
    - Line chart with predicted shifts, CI bounds, shaded area
    - Grouped by unit for multi-line display
    """
    # Group by unit
    unit_data = defaultdict(lambda: {
        'dates': [],
        'predicted': [],
        'ci_lower': [],
        'ci_upper': [],
    })
    
    for forecast in forecasts:
        unit_key = f"{forecast.unit.name}"
        unit_data[unit_key]['dates'].append(forecast.forecast_date.strftime('%Y-%m-%d'))
        unit_data[unit_key]['predicted'].append(float(forecast.predicted_shifts))
        unit_data[unit_key]['ci_lower'].append(float(forecast.confidence_lower))
        unit_data[unit_key]['ci_upper'].append(float(forecast.confidence_upper))
    
    # Convert to JSON-serializable format
    chart_data = {
        'units': list(unit_data.keys()),
        'datasets': []
    }
    
    colors = [
        '#4CAF50',  # Green
        '#2196F3',  # Blue
        '#FF9800',  # Orange
        '#9C27B0',  # Purple
        '#F44336',  # Red
    ]
    
    for idx, (unit_name, data) in enumerate(unit_data.items()):
        color = colors[idx % len(colors)]
        
        chart_data['datasets'].append({
            'label': unit_name,
            'dates': data['dates'],
            'predicted': data['predicted'],
            'ci_lower': data['ci_lower'],
            'ci_upper': data['ci_upper'],
            'borderColor': color,
            'backgroundColor': color + '20',  # 20% opacity
        })
    
    return json.dumps(chart_data)


def prepare_accuracy_chart_data(comparisons):
    """Prepare JSON data for predicted vs actual comparison chart"""
    dates = []
    predicted = []
    actual = []
    ci_lower = []
    ci_upper = []
    
    for comp in comparisons:
        dates.append(comp['date'].strftime('%Y-%m-%d'))
        predicted.append(comp['predicted'])
        actual.append(comp['actual'])
        ci_lower.append(comp['ci_lower'])
        ci_upper.append(comp['ci_upper'])
    
    chart_data = {
        'dates': dates,
        'predicted': predicted,
        'actual': actual,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper,
    }
    
    return json.dumps(chart_data)


def prepare_performance_heatmap_data(performance_list):
    """Prepare JSON data for MAPE heatmap"""
    # Group by care home
    heatmap = defaultdict(list)
    
    for perf in performance_list:
        heatmap[perf['care_home']].append({
            'unit': perf['unit'],
            'mape': perf['avg_mape'],
            'quality': perf['quality'],
        })
    
    return json.dumps(heatmap)


def get_quality_rating(mape):
    """
    Convert MAPE to quality rating.
    
    Benchmarks for social care forecasting:
    - Excellent: < 15% MAPE
    - Good: 15-25% MAPE
    - Fair: 25-40% MAPE
    - Poor: > 40% MAPE
    """
    if mape < 15:
        return 'excellent'
    elif mape < 25:
        return 'good'
    elif mape < 40:
        return 'fair'
    else:
        return 'poor'
