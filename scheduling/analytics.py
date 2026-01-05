"""
Analytics Service Layer for Staff Rota System
Provides KPI calculations, metrics, and data analysis functions
"""

from django.db.models import Count, Q, Sum, Avg, F, ExpressionWrapper, fields
from django.utils import timezone
from datetime import datetime, timedelta, date
from decimal import Decimal
from collections import defaultdict
import logging

from .models import Shift, User, CareHome, Unit, ShiftType, LeaveRequest

logger = logging.getLogger(__name__)


class AnalyticsError(Exception):
    """Custom exception for analytics operations"""
    pass


def get_date_range(range_type='week', custom_start=None, custom_end=None):
    """
    Get standardized date ranges for analytics
    
    Args:
        range_type: 'today', 'week', 'month', 'quarter', 'year', 'custom'
        custom_start: datetime.date for custom range start
        custom_end: datetime.date for custom range end
    
    Returns:
        tuple: (start_date, end_date)
    """
    today = timezone.now().date()
    
    if range_type == 'today':
        return (today, today)
    
    elif range_type == 'week':
        # Current week (Monday to Sunday)
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        return (start, end)
    
    elif range_type == 'month':
        # Current month
        start = today.replace(day=1)
        if today.month == 12:
            end = today.replace(day=31)
        else:
            end = (today.replace(month=today.month + 1, day=1) - timedelta(days=1))
        return (start, end)
    
    elif range_type == 'quarter':
        # Current quarter
        quarter = (today.month - 1) // 3
        start = today.replace(month=quarter * 3 + 1, day=1)
        end_month = start.month + 2
        if end_month > 12:
            end = today.replace(year=today.year + 1, month=end_month - 12, day=1) - timedelta(days=1)
        else:
            end = today.replace(month=end_month + 1, day=1) - timedelta(days=1)
        return (start, end)
    
    elif range_type == 'year':
        # Current year
        start = today.replace(month=1, day=1)
        end = today.replace(month=12, day=31)
        return (start, end)
    
    elif range_type == 'custom':
        if custom_start and custom_end:
            return (custom_start, custom_end)
        raise ValueError("Custom range requires both start and end dates")
    
    else:
        raise ValueError(f"Invalid range_type: {range_type}")


def calculate_occupancy_rate(care_home=None, unit=None, start_date=None, end_date=None):
    """
    Calculate bed occupancy rate for care homes/units
    
    Args:
        care_home: CareHome object (optional)
        unit: Unit object (optional)
        start_date: date object (optional, defaults to current month)
        end_date: date object (optional, defaults to current month)
    
    Returns:
        dict: {
            'total_beds': int,
            'occupied_beds': int,
            'occupancy_rate': float (percentage),
            'vacant_beds': int
        }
    """
    if not start_date or not end_date:
        start_date, end_date = get_date_range('month')
    
    # Base queryset
    if unit:
        total_beds = unit.bed_capacity or 0
        homes = [unit.care_home]
    elif care_home:
        total_beds = sum(u.bed_capacity or 0 for u in care_home.units.all())
        homes = [care_home]
    else:
        # All care homes
        homes = CareHome.objects.all()
        total_beds = sum(
            sum(u.bed_capacity or 0 for u in home.units.all())
            for home in homes
        )
    
    if total_beds == 0:
        return {
            'total_beds': 0,
            'occupied_beds': 0,
            'occupancy_rate': 0.0,
            'vacant_beds': 0
        }
    
    # Calculate average occupancy over date range
    # This is simplified - in production, you'd integrate with resident management system
    # For now, we estimate based on staffing levels
    days = (end_date - start_date).days + 1
    
    # Rough estimation: Average 0.85 occupancy (85%) as baseline
    # In production, this would query actual resident data
    occupied_beds = int(total_beds * 0.85)
    occupancy_rate = (occupied_beds / total_beds) * 100
    
    return {
        'total_beds': total_beds,
        'occupied_beds': occupied_beds,
        'occupancy_rate': round(occupancy_rate, 2),
        'vacant_beds': total_beds - occupied_beds
    }


def calculate_staffing_levels(care_home=None, unit=None, start_date=None, end_date=None):
    """
    Calculate actual vs required staffing levels
    
    Returns:
        dict: {
            'required_shifts': int,
            'scheduled_shifts': int,
            'fill_rate': float (percentage),
            'vacancies': int,
            'avg_staff_per_day': float
        }
    """
    if not start_date or not end_date:
        start_date, end_date = get_date_range('week')
    
    # Build queryset
    shifts = Shift.objects.filter(date__range=[start_date, end_date])
    
    if unit:
        shifts = shifts.filter(unit=unit)
    elif care_home:
        shifts = shifts.filter(care_home=care_home)
    
    scheduled_shifts = shifts.count()
    
    # Calculate required shifts based on expected coverage
    # Since Vacancy model doesn't exist, estimate based on expected shifts per day
    # Typical care home: ~15-20 staff per day across all units
    days = (end_date - start_date).days + 1
    
    if unit:
        expected_shifts_per_day = 5  # Estimate per unit
    elif care_home:
        expected_shifts_per_day = 15  # Estimate per care home
    else:
        expected_shifts_per_day = 50  # Estimate for all homes
    
    required_shifts = days * expected_shifts_per_day
    vacancies_count = max(0, required_shifts - scheduled_shifts)
    
    # Calculate fill rate
    fill_rate = (scheduled_shifts / required_shifts * 100) if required_shifts > 0 else 100.0
    
    # Calculate average staff per day
    avg_staff_per_day = scheduled_shifts / days if days > 0 else 0
    
    return {
        'required_shifts': required_shifts,
        'scheduled_shifts': scheduled_shifts,
        'fill_rate': round(fill_rate, 2),
        'vacancies': vacancies_count,
        'avg_staff_per_day': round(avg_staff_per_day, 2)
    }


def calculate_overtime_metrics(care_home=None, unit=None, start_date=None, end_date=None):
    """
    Calculate overtime hours and costs
    
    Returns:
        dict: {
            'total_overtime_hours': float,
            'overtime_shifts': int,
            'estimated_overtime_cost': float,
            'percentage_overtime': float
        }
    """
    if not start_date or not end_date:
        start_date, end_date = get_date_range('month')
    
    # Get shifts
    shifts = Shift.objects.filter(date__range=[start_date, end_date])
    
    if unit:
        shifts = shifts.filter(unit=unit)
    elif care_home:
        shifts = shifts.filter(care_home=care_home)
    
    total_shifts = shifts.count()
    
    # Calculate overtime (shifts marked as overtime or over standard hours)
    # This is simplified - in production, track actual hours worked
    overtime_shifts = shifts.filter(
        Q(shift_type__name__icontains='overtime') |
        Q(shift_type__hours__gt=8)
    ).count()
    
    # Estimate overtime hours (average 2 hours OT per overtime shift)
    avg_overtime_hours_per_shift = 2.0
    total_overtime_hours = overtime_shifts * avg_overtime_hours_per_shift
    
    # Estimate cost (£25/hour average overtime rate)
    overtime_rate = 25.0
    estimated_overtime_cost = total_overtime_hours * overtime_rate
    
    # Calculate percentage
    percentage_overtime = (overtime_shifts / total_shifts * 100) if total_shifts > 0 else 0.0
    
    return {
        'total_overtime_hours': round(total_overtime_hours, 2),
        'overtime_shifts': overtime_shifts,
        'estimated_overtime_cost': round(estimated_overtime_cost, 2),
        'percentage_overtime': round(percentage_overtime, 2)
    }


def calculate_cost_metrics(care_home=None, unit=None, start_date=None, end_date=None):
    """
    Calculate staffing costs
    
    Returns:
        dict: {
            'total_shifts': int,
            'estimated_regular_cost': float,
            'estimated_overtime_cost': float,
            'estimated_total_cost': float,
            'cost_per_shift': float,
            'cost_per_day': float
        }
    """
    if not start_date or not end_date:
        start_date, end_date = get_date_range('month')
    
    # Get shifts
    shifts = Shift.objects.filter(date__range=[start_date, end_date])
    
    if unit:
        shifts = shifts.filter(unit=unit)
    elif care_home:
        shifts = shifts.filter(care_home=care_home)
    
    total_shifts = shifts.count()
    
    # Calculate shift type breakdown
    shift_breakdown = shifts.values('shift_type__name', 'shift_type__hours').annotate(
        count=Count('id')
    )
    
    # Estimate regular cost (£15/hour average base rate)
    regular_rate = 15.0
    estimated_regular_hours = sum(
        (st['shift_type__hours'] or 8) * st['count']
        for st in shift_breakdown
    )
    estimated_regular_cost = estimated_regular_hours * regular_rate
    
    # Get overtime cost
    overtime_metrics = calculate_overtime_metrics(care_home, unit, start_date, end_date)
    estimated_overtime_cost = overtime_metrics['estimated_overtime_cost']
    
    estimated_total_cost = estimated_regular_cost + estimated_overtime_cost
    
    # Calculate averages
    cost_per_shift = estimated_total_cost / total_shifts if total_shifts > 0 else 0.0
    days = (end_date - start_date).days + 1
    cost_per_day = estimated_total_cost / days if days > 0 else 0.0
    
    return {
        'total_shifts': total_shifts,
        'estimated_regular_cost': round(estimated_regular_cost, 2),
        'estimated_overtime_cost': round(estimated_overtime_cost, 2),
        'estimated_total_cost': round(estimated_total_cost, 2),
        'cost_per_shift': round(cost_per_shift, 2),
        'cost_per_day': round(cost_per_day, 2)
    }


def calculate_compliance_metrics(care_home=None, unit=None, start_date=None, end_date=None):
    """
    Calculate compliance metrics (rest periods, max hours, etc.)
    
    Returns:
        dict: {
            'total_staff': int,
            'compliance_rate': float,
            'violations': int,
            'warnings': int,
            'at_risk_staff': list
        }
    """
    if not start_date or not end_date:
        start_date, end_date = get_date_range('week')
    
    # Get active staff
    staff_query = User.objects.filter(is_active=True)
    
    if unit:
        staff_query = staff_query.filter(unit=unit)
    elif care_home:
        staff_query = staff_query.filter(care_home=care_home)
    
    total_staff = staff_query.count()
    
    violations = 0
    warnings = 0
    at_risk_staff = []
    
    # Check each staff member's shifts
    for staff_member in staff_query:
        shifts = Shift.objects.filter(
            staff=staff_member,
            date__range=[start_date, end_date]
        ).order_by('date')
        
        # Check for violations
        # 1. Max hours per week (48 hours)
        total_hours = sum(shift.shift_type.hours or 8 for shift in shifts)
        if total_hours > 48:
            violations += 1
            at_risk_staff.append({
                'staff_id': staff_member.id,
                'staff_name': staff_member.get_full_name(),
                'issue': f'Excessive hours: {total_hours}h/week'
            })
        
        # 2. Minimum rest period (11 hours between shifts)
        for i in range(len(shifts) - 1):
            current_shift = shifts[i]
            next_shift = shifts[i + 1]
            
            # Calculate rest period (simplified - assumes end of shift + rest)
            if (next_shift.date - current_shift.date).days == 0:
                # Same day shifts - potential violation
                warnings += 1
        
        # 3. Check for excessive consecutive days
        consecutive_days = 0
        prev_date = None
        max_consecutive = 0
        
        for shift in shifts:
            if prev_date and (shift.date - prev_date).days == 1:
                consecutive_days += 1
            else:
                consecutive_days = 1
            
            max_consecutive = max(max_consecutive, consecutive_days)
            prev_date = shift.date
        
        if max_consecutive > 6:
            warnings += 1
    
    compliance_rate = ((total_staff - violations) / total_staff * 100) if total_staff > 0 else 100.0
    
    return {
        'total_staff': total_staff,
        'compliance_rate': round(compliance_rate, 2),
        'violations': violations,
        'warnings': warnings,
        'at_risk_staff': at_risk_staff[:10]  # Limit to top 10
    }


def calculate_leave_metrics(care_home=None, unit=None, start_date=None, end_date=None):
    """
    Calculate leave request metrics
    
    Returns:
        dict: {
            'total_requests': int,
            'approved': int,
            'pending': int,
            'rejected': int,
            'total_leave_days': int,
            'approval_rate': float
        }
    """
    if not start_date or not end_date:
        start_date, end_date = get_date_range('month')
    
    # Get leave requests overlapping with date range
    leave_requests = LeaveRequest.objects.filter(
        Q(start_date__range=[start_date, end_date]) |
        Q(end_date__range=[start_date, end_date]) |
        Q(start_date__lte=start_date, end_date__gte=end_date)
    )
    
    if unit:
        leave_requests = leave_requests.filter(user__unit=unit)
    elif care_home:
        leave_requests = leave_requests.filter(user__care_home=care_home)
    
    total_requests = leave_requests.count()
    approved = leave_requests.filter(status='approved').count()
    pending = leave_requests.filter(status='pending').count()
    rejected = leave_requests.filter(status='rejected').count()
    
    # Calculate total leave days
    total_leave_days = 0
    for leave in leave_requests.filter(status='approved'):
        days = (leave.end_date - leave.start_date).days + 1
        total_leave_days += days
    
    approval_rate = (approved / total_requests * 100) if total_requests > 0 else 0.0
    
    return {
        'total_requests': total_requests,
        'approved': approved,
        'pending': pending,
        'rejected': rejected,
        'total_leave_days': total_leave_days,
        'approval_rate': round(approval_rate, 2)
    }


def get_shift_distribution(care_home=None, unit=None, start_date=None, end_date=None):
    """
    Get shift distribution by type
    
    Returns:
        dict: {
            'by_type': [{name, count, percentage}, ...],
            'by_unit': [{name, count, percentage}, ...],
            'by_day_of_week': [{day, count}, ...]
        }
    """
    if not start_date or not end_date:
        start_date, end_date = get_date_range('week')
    
    # Get shifts
    shifts = Shift.objects.filter(date__range=[start_date, end_date])
    
    if unit:
        shifts = shifts.filter(unit=unit)
    elif care_home:
        shifts = shifts.filter(care_home=care_home)
    
    total_shifts = shifts.count()
    
    # By shift type
    by_type = shifts.values('shift_type__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    by_type_list = [
        {
            'name': item['shift_type__name'] or 'Unknown',
            'count': item['count'],
            'percentage': round(item['count'] / total_shifts * 100, 2) if total_shifts > 0 else 0
        }
        for item in by_type
    ]
    
    # By unit (if looking at care home level)
    by_unit_list = []
    if care_home and not unit:
        by_unit = shifts.values('unit__name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        by_unit_list = [
            {
                'name': item['unit__name'] or 'Unknown',
                'count': item['count'],
                'percentage': round(item['count'] / total_shifts * 100, 2) if total_shifts > 0 else 0
            }
            for item in by_unit
        ]
    
    # By day of week
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    by_day_of_week = defaultdict(int)
    
    for shift in shifts:
        day_index = shift.date.weekday()
        by_day_of_week[day_names[day_index]] += 1
    
    by_day_of_week_list = [
        {'day': day, 'count': by_day_of_week[day]}
        for day in day_names
    ]
    
    return {
        'by_type': by_type_list,
        'by_unit': by_unit_list,
        'by_day_of_week': by_day_of_week_list
    }


def get_trending_data(care_home=None, unit=None, metric='staffing', periods=12):
    """
    Get trending data for charts (last N periods)
    
    Args:
        metric: 'staffing', 'costs', 'occupancy', 'compliance'
        periods: number of periods to show (default 12 weeks)
    
    Returns:
        list: [{period_label, value}, ...]
    """
    today = timezone.now().date()
    trending_data = []
    
    for i in range(periods - 1, -1, -1):
        # Calculate week range
        end_date = today - timedelta(weeks=i)
        start_date = end_date - timedelta(days=6)
        
        period_label = f"{start_date.strftime('%m/%d')} - {end_date.strftime('%m/%d')}"
        
        if metric == 'staffing':
            data = calculate_staffing_levels(care_home, unit, start_date, end_date)
            value = data['fill_rate']
        
        elif metric == 'costs':
            data = calculate_cost_metrics(care_home, unit, start_date, end_date)
            value = data['estimated_total_cost']
        
        elif metric == 'occupancy':
            data = calculate_occupancy_rate(care_home, unit, start_date, end_date)
            value = data['occupancy_rate']
        
        elif metric == 'compliance':
            data = calculate_compliance_metrics(care_home, unit, start_date, end_date)
            value = data['compliance_rate']
        
        else:
            value = 0
        
        trending_data.append({
            'period': period_label,
            'value': value
        })
    
    return trending_data


def get_dashboard_summary(care_home=None, unit=None, date_range='week'):
    """
    Get complete dashboard summary with all KPIs
    
    Returns:
        dict: Complete dashboard data with all metrics
    """
    start_date, end_date = get_date_range(date_range)
    
    return {
        'date_range': {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d'),
            'type': date_range
        },
        'occupancy': calculate_occupancy_rate(care_home, unit, start_date, end_date),
        'staffing': calculate_staffing_levels(care_home, unit, start_date, end_date),
        'overtime': calculate_overtime_metrics(care_home, unit, start_date, end_date),
        'costs': calculate_cost_metrics(care_home, unit, start_date, end_date),
        'compliance': calculate_compliance_metrics(care_home, unit, start_date, end_date),
        'leave': calculate_leave_metrics(care_home, unit, start_date, end_date),
        'distribution': get_shift_distribution(care_home, unit, start_date, end_date)
    }
