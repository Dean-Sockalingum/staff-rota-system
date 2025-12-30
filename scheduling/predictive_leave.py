"""
Predictive Leave Forecasting Service

Analyzes historical leave patterns and predicts future leave
requests to enable proactive staffing planning.
"""

from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta, date
from decimal import Decimal
from collections import defaultdict
import calendar


def analyze_leave_patterns(staff_member, months_back=12):
    """Analyze leave patterns for a staff member"""
    from .models import LeaveRequest, LeavePattern
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=months_back * 30)
    
    # Get all approved leave
    leave_requests = LeaveRequest.objects.filter(
        user=staff_member,
        status='APPROVED',
        start_date__gte=start_date,
        end_date__lte=end_date
    ).order_by('start_date')
    
    if not leave_requests.exists():
        return {
            'has_patterns': False,
            'patterns': [],
            'total_requests': 0,
        }
    
    # Analyze monthly distribution
    monthly_counts = defaultdict(int)
    monthly_days = defaultdict(int)
    
    for leave in leave_requests:
        month = leave.start_date.month
        days = (leave.end_date - leave.start_date).days + 1
        monthly_counts[month] += 1
        monthly_days[month] += days
    
    # Identify preferred months
    preferred_months = sorted(monthly_counts.keys(), key=lambda m: monthly_counts[m], reverse=True)[:3]
    
    # Analyze day of week preferences
    dow_counts = defaultdict(int)
    for leave in leave_requests:
        dow_counts[leave.start_date.weekday()] += 1
    
    preferred_days = sorted(dow_counts.keys(), key=lambda d: dow_counts[d], reverse=True)[:2]
    
    # Calculate typical duration
    durations = [(leave.end_date - leave.start_date).days + 1 for leave in leave_requests]
    typical_duration = int(sum(durations) / len(durations)) if durations else 1
    
    # Calculate frequency
    frequency_per_year = (leave_requests.count() / months_back) * 12
    
    # Determine pattern type
    if len(preferred_months) >= 2 and monthly_counts[preferred_months[0]] >= 3:
        pattern_type = 'SEASONAL'
        pattern_name = f"Seasonal - Prefers {calendar.month_name[preferred_months[0]]}"
    elif frequency_per_year >= 12:
        pattern_type = 'MONTHLY'
        pattern_name = "Regular monthly leave"
    elif len(preferred_days) == 1:
        pattern_type = 'WEEKLY'
        pattern_name = f"Prefers {calendar.day_name[preferred_days[0]]}s"
    else:
        pattern_type = 'RANDOM'
        pattern_name = "No clear pattern"
    
    # Calculate pattern strength
    if pattern_type == 'SEASONAL':
        top_month_count = monthly_counts[preferred_months[0]]
        pattern_strength = min((top_month_count / leave_requests.count()) * 100, 100)
    elif pattern_type == 'MONTHLY':
        pattern_strength = min((frequency_per_year / 12) * 100, 100)
    else:
        pattern_strength = 30  # Low strength for random
    
    # Create or update pattern
    pattern, created = LeavePattern.objects.update_or_create(
        staff_member=staff_member,
        pattern_type=pattern_type,
        defaults={
            'care_home': staff_member.care_home,
            'pattern_name': pattern_name,
            'pattern_description': f"Based on {leave_requests.count()} leave requests over {months_back} months",
            'typical_duration_days': typical_duration,
            'frequency_per_year': Decimal(str(frequency_per_year)),
            'preferred_months': preferred_months,
            'preferred_days_of_week': preferred_days,
            'occurrences_found': leave_requests.count(),
            'pattern_strength': Decimal(str(pattern_strength)),
            'last_occurrence': leave_requests.last().start_date,
            'analyzed_from': start_date,
            'analyzed_to': end_date,
        }
    )
    
    return {
        'has_patterns': True,
        'patterns': [pattern],
        'total_requests': leave_requests.count(),
        'typical_duration': typical_duration,
        'frequency_per_year': frequency_per_year,
        'preferred_months': preferred_months,
        'pattern_strength': pattern_strength,
    }


def forecast_leave(staff_member, forecast_months=3, forecast_type='ALL'):
    """Generate leave forecast for a staff member"""
    from .models import LeaveForecast, LeaveRequest, LeavePattern
    
    # Analyze patterns first
    pattern_analysis = analyze_leave_patterns(staff_member, months_back=12)
    
    # Define forecast period
    forecast_start = timezone.now().date()
    forecast_end = forecast_start + timedelta(days=forecast_months * 30)
    
    # Get historical data
    historical_start = forecast_start - timedelta(days=365)
    historical_leave = LeaveRequest.objects.filter(
        user=staff_member,
        status='APPROVED',
        start_date__gte=historical_start,
        start_date__lt=forecast_start
    )
    
    if forecast_type != 'ALL':
        historical_leave = historical_leave.filter(leave_type=forecast_type)
    
    # Calculate historical average
    total_days = sum((leave.end_date - leave.start_date).days + 1 for leave in historical_leave)
    avg_days_per_month = Decimal(str(total_days / 12)) if total_days > 0 else Decimal('0')
    
    # Predict days for forecast period
    if pattern_analysis['has_patterns']:
        # Use pattern-based prediction
        frequency = float(pattern_analysis['frequency_per_year'])
        typical_duration = pattern_analysis['typical_duration']
        
        predicted_requests = int((frequency / 12) * forecast_months)
        predicted_days = predicted_requests * typical_duration
        
        # Identify peak month
        preferred_months = pattern_analysis['preferred_months']
        forecast_month_nums = [(forecast_start + timedelta(days=30*i)).month for i in range(forecast_months)]
        peak_months = [m for m in preferred_months if m in forecast_month_nums]
        predicted_peak = calendar.month_name[peak_months[0]] if peak_months else ""
        
        confidence_score = pattern_analysis['pattern_strength']
        if confidence_score >= 70:
            confidence_level = 'HIGH'
        elif confidence_score >= 50:
            confidence_level = 'MEDIUM'
        else:
            confidence_level = 'LOW'
        
        trend_factor = 'STABLE'
        pattern_desc = f"Based on {pattern_analysis['patterns'][0].pattern_name}"
    else:
        # Use simple average
        predicted_days = int(float(avg_days_per_month) * forecast_months)
        predicted_peak = ""
        confidence_score = Decimal('40')
        confidence_level = 'LOW'
        trend_factor = 'STABLE'
        pattern_desc = "Based on historical average (no clear pattern)"
    
    # Calculate prediction range (±20%)
    prediction_range_min = max(0, int(predicted_days * 0.8))
    prediction_range_max = int(predicted_days * 1.2)
    
    # Determine impact level
    if predicted_days > forecast_months * 5:
        impact_level = 'HIGH'
    elif predicted_days > forecast_months * 3:
        impact_level = 'MEDIUM'
    else:
        impact_level = 'LOW'
    
    # Generate recommendations
    recommendations = []
    if impact_level in ['HIGH', 'CRITICAL']:
        recommendations.append(f"High leave volume expected - plan for {predicted_days} days coverage")
        recommendations.append("Consider advance notice requirements")
    
    if predicted_peak:
        recommendations.append(f"Peak leave expected in {predicted_peak}")
        recommendations.append(f"Ensure adequate coverage for {predicted_peak}")
    
    coverage_req = f"Estimated {predicted_days} shift coverage days needed over {forecast_months} months"
    
    # Create forecast
    forecast = LeaveForecast.objects.create(
        staff_member=staff_member,
        care_home=staff_member.care_home,
        forecast_type=forecast_type,
        forecast_date=timezone.now().date(),
        forecast_start=forecast_start,
        forecast_end=forecast_end,
        predicted_days=predicted_days,
        predicted_peak_month=predicted_peak,
        predicted_pattern=pattern_desc,
        historical_period_months=12,
        total_historical_days=total_days,
        average_days_per_month=avg_days_per_month,
        confidence_level=confidence_level,
        confidence_score=confidence_score,
        prediction_range_min=prediction_range_min,
        prediction_range_max=prediction_range_max,
        seasonal_factor=pattern_analysis['has_patterns'],
        trend_factor=trend_factor,
        impact_level=impact_level,
        recommended_actions='\n'.join(recommendations),
        coverage_requirements=coverage_req,
    )
    
    return forecast


def analyze_leave_impact(care_home, start_date, end_date, unit=None):
    """Analyze the impact of leave on staffing"""
    from .models import LeaveRequest, Shift, LeaveImpactAnalysis
    
    # Get all approved leave in period
    leave_requests = LeaveRequest.objects.filter(
        user__care_home=care_home,
        status='APPROVED',
        start_date__lte=end_date,
        end_date__gte=start_date
    )
    
    if unit:
        leave_requests = leave_requests.filter(user__unit=unit)
    
    total_leave_days = 0
    staff_on_leave = set()
    daily_leave_count = defaultdict(int)
    
    # Calculate daily leave impact
    current_date = start_date
    while current_date <= end_date:
        day_count = 0
        for leave in leave_requests:
            if leave.start_date <= current_date <= leave.end_date:
                day_count += 1
                staff_on_leave.add(leave.user.id)
                total_leave_days += 1
        
        daily_leave_count[current_date] = day_count
        current_date += timedelta(days=1)
    
    # Find peak
    if daily_leave_count:
        peak_date = max(daily_leave_count.items(), key=lambda x: x[1])
        concurrent_peak = peak_date[1]
        concurrent_peak_date = peak_date[0]
    else:
        concurrent_peak = 0
        concurrent_peak_date = None
    
    # Get total scheduled shifts
    total_shifts = Shift.objects.filter(
        care_home=care_home,
        date__gte=start_date,
        date__lte=end_date
    )
    if unit:
        total_shifts = total_shifts.filter(unit=unit)
    
    total_shifts_count = total_shifts.count()
    
    # Calculate coverage gap
    shifts_affected = 0
    for leave in leave_requests:
        affected = Shift.objects.filter(
            staff_member=leave.user,
            date__gte=leave.start_date,
            date__lte=leave.end_date
        ).count()
        shifts_affected += affected
    
    # Estimate impact
    if total_shifts_count > 0:
        impact_percentage = (shifts_affected / total_shifts_count) * 100
    else:
        impact_percentage = 0
    
    if impact_percentage > 50:
        impact_severity = 'SEVERE'
        risk_level = 'CRITICAL'
    elif impact_percentage > 25:
        impact_severity = 'SIGNIFICANT'
        risk_level = 'HIGH'
    elif impact_percentage > 10:
        impact_severity = 'MODERATE'
        risk_level = 'MEDIUM'
    else:
        impact_severity = 'MINIMAL'
        risk_level = 'LOW'
    
    # Calculate estimated costs (assuming £15/hr overtime, £25/hr agency)
    coverage_gap_hours = Decimal(str(shifts_affected * 8))  # Assume 8hr shifts
    overtime_hours = coverage_gap_hours * Decimal('0.3')  # 30% via overtime
    agency_shifts = int(shifts_affected * 0.7 / 8)  # 70% via agency
    
    estimated_cost = (overtime_hours * Decimal('15')) + (Decimal(str(agency_shifts * 8)) * Decimal('25'))
    
    # Generate mitigation strategies
    strategies = []
    if risk_level in ['HIGH', 'CRITICAL']:
        strategies.append("URGENT: Recruit temporary staff or arrange agency cover")
        strategies.append("Consider mandatory presence days")
    
    if concurrent_peak > 5:
        strategies.append(f"Peak concurrent leave ({concurrent_peak} staff) on {concurrent_peak_date}")
        strategies.append("Implement staggered leave approval")
    
    # Create analysis
    analysis = LeaveImpactAnalysis.objects.create(
        care_home=care_home,
        unit=unit,
        period_start=start_date,
        period_end=end_date,
        total_leave_days=total_leave_days,
        staff_on_leave_count=len(staff_on_leave),
        concurrent_leave_peak=concurrent_peak,
        concurrent_leave_peak_date=concurrent_peak_date,
        impact_severity=impact_severity,
        coverage_gap_hours=coverage_gap_hours,
        overtime_hours_required=overtime_hours,
        agency_shifts_needed=agency_shifts,
        estimated_cost_impact=estimated_cost,
        understaffing_days=sum(1 for count in daily_leave_count.values() if count > 3),
        risk_level=risk_level,
        mitigation_strategies='\n'.join(strategies),
        recommended_hires=int(concurrent_peak * 0.5) if concurrent_peak > 5 else 0,
        impact_by_day={str(k): v for k, v in daily_leave_count.items()},
        affected_staff_list=list(staff_on_leave),
    )
    
    return analysis


def get_team_leave_forecast(care_home, months_ahead=3):
    """Get aggregated leave forecast for entire team"""
    from .models import User, LeaveForecast
    
    staff_members = User.objects.filter(care_home=care_home, is_active=True)
    
    forecasts = []
    total_predicted_days = 0
    high_impact_staff = []
    
    for staff in staff_members:
        try:
            forecast = forecast_leave(staff, forecast_months=months_ahead)
            forecasts.append(forecast)
            total_predicted_days += forecast.predicted_days
            
            if forecast.impact_level in ['HIGH', 'CRITICAL']:
                high_impact_staff.append({
                    'staff': staff,
                    'forecast': forecast,
                })
        except Exception as e:
            print(f"Error forecasting for {staff}: {e}")
            continue
    
    return {
        'forecasts': forecasts,
        'total_staff': staff_members.count(),
        'total_predicted_days': total_predicted_days,
        'average_days_per_staff': total_predicted_days / staff_members.count() if staff_members.count() > 0 else 0,
        'high_impact_staff': high_impact_staff,
    }


def identify_leave_conflicts(care_home, start_date, end_date):
    """Identify potential leave conflicts and overlaps"""
    from .models import LeaveRequest
    
    approved_leave = LeaveRequest.objects.filter(
        user__care_home=care_home,
        status='APPROVED',
        start_date__lte=end_date,
        end_date__gte=start_date
    ).select_related('user').order_by('start_date')
    
    conflicts = []
    daily_overlaps = defaultdict(list)
    
    # Track overlaps by day
    for leave in approved_leave:
        current = leave.start_date
        while current <= leave.end_date:
            if start_date <= current <= end_date:
                daily_overlaps[current].append(leave)
            current += timedelta(days=1)
    
    # Identify high overlap days
    for date, leaves in daily_overlaps.items():
        if len(leaves) >= 3:  # 3+ people on same day
            conflicts.append({
                'date': date,
                'count': len(leaves),
                'severity': 'HIGH' if len(leaves) >= 5 else 'MEDIUM',
                'staff': [leave.user for leave in leaves],
            })
    
    return sorted(conflicts, key=lambda x: x['count'], reverse=True)
