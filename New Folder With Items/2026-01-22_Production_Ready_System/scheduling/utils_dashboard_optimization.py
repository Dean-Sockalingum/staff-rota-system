"""
Dashboard Query Optimization Utilities
Provides optimized database queries for dashboard views to handle 189k+ shifts efficiently
"""

from django.db.models import Count, Q, Prefetch, F
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta
from collections import defaultdict

from .models import Shift, Unit, User


def get_optimized_coverage_summary(start_date, end_date, care_home=None):
    """
    Get coverage summary using a single optimized query instead of per-day/per-unit iteration.
    
    Args:
        start_date: Start date for coverage period
        end_date: End date for coverage period
        care_home: Optional CareHome to filter by
    
    Returns:
        dict: Coverage data grouped by date and unit with counts by shift type and role
    """
    # Base queryset with filters
    shifts_qs = Shift.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    ).select_related('unit', 'shift_type', 'user__role')
    
    if care_home:
        shifts_qs = shifts_qs.filter(unit__care_home=care_home)
    
    # Define shift type categories using Q objects for efficient filtering
    day_shift_q = Q(shift_type__name__in=['DAY', 'DAY_SENIOR', 'DAY_ASSISTANT'])
    night_shift_q = Q(shift_type__name__in=['NIGHT', 'NIGHT_SENIOR', 'NIGHT_ASSISTANT'])
    
    # Aggregate by date and unit in a single query
    coverage_data = shifts_qs.values('date', 'unit__name', 'unit__id').annotate(
        # Day shift counts by role
        sscw_day=Count('id', filter=day_shift_q & Q(user__role__name='SSCW')),
        scw_day=Count('id', filter=day_shift_q & Q(user__role__name='SCW')),
        sca_day=Count('id', filter=day_shift_q & Q(user__role__name='SCA')),
        total_care_day=Count('id', filter=day_shift_q & Q(user__role__name__in=['SCW', 'SCA'])),
        
        # Night shift counts by role  
        sscwn_night=Count('id', filter=night_shift_q & Q(user__role__name='SSCWN')),
        scwn_night=Count('id', filter=night_shift_q & Q(user__role__name='SCWN')),
        scan_night=Count('id', filter=night_shift_q & Q(user__role__name='SCAN')),
        total_care_night=Count('id', filter=night_shift_q & Q(user__role__name__in=['SCWN', 'SCAN'])),
        
        # Total counts
        total_day=Count('id', filter=day_shift_q),
        total_night=Count('id', filter=night_shift_q),
    ).order_by('date', 'unit__name')
    
    # Restructure for easy template access
    coverage_table = defaultdict(lambda: defaultdict(dict))
    for row in coverage_data:
        date = row['date']
        unit_name = row['unit__name']
        coverage_table[date][unit_name] = {
            'day_sscw': row['sscw_day'],
            'day_care': row['total_care_day'],
            'night_sscw': row['sscwn_night'],
            'night_care': row['total_care_night'],
            'total_day': row['total_day'],
            'total_night': row['total_night'],
        }
    
    return coverage_table


def get_optimized_unit_coverage(date, care_home=None):
    """
    Get today's coverage by unit using optimized aggregation.
    
    Args:
        date: Date to get coverage for
        care_home: Optional CareHome to filter by
        
    Returns:
        dict: Coverage counts by unit
    """
    shifts_qs = Shift.objects.filter(date=date).select_related('unit', 'shift_type', 'user__role')
    
    if care_home:
        shifts_qs = shifts_qs.filter(unit__care_home=care_home)
    
    day_shift_q = Q(shift_type__name__in=['DAY', 'DAY_SENIOR', 'DAY_ASSISTANT'])
    night_shift_q = Q(shift_type__name__in=['NIGHT', 'NIGHT_SENIOR', 'NIGHT_ASSISTANT'])
    
    coverage = shifts_qs.values('unit__id', 'unit__name').annotate(
        day_count=Count('id', filter=day_shift_q),
        night_count=Count('id', filter=night_shift_q),
        total_count=Count('id')
    ).order_by('unit__name')
    
    return {item['unit__name']: item for item in coverage}


def get_optimized_staffing_by_unit(shifts_queryset):
    """
    Get staffing breakdown by unit without iterating through individual shifts.
    
    Args:
        shifts_queryset: Pre-filtered Shift queryset
        
    Returns:
        dict: Staffing counts grouped by unit with day/night breakdown
    """
    day_shift_q = Q(shift_type__name__icontains='DAY')
    night_shift_q = Q(shift_type__name__icontains='NIGHT')
    
    by_unit = shifts_queryset.values('unit__id', 'unit__name').annotate(
        day_count=Count('id', filter=day_shift_q),
        night_count=Count('id', filter=night_shift_q),
        total_count=Count('id')
    ).order_by('unit__name')
    
    return {
        item['unit__name']: {
            'day': item['day_count'],
            'night': item['night_count'],
            'total': item['total_count']
        }
        for item in by_unit
    }


def get_optimized_staff_list_by_unit(date, care_home=None, max_staff_per_unit=50):
    """
    Get staff names by unit with a limit to prevent massive queries.
    Uses efficient prefetch_related to minimize database hits.
    
    Args:
        date: Date to get staff for
        care_home: Optional CareHome filter
        max_staff_per_unit: Maximum staff to return per unit (prevents huge lists)
        
    Returns:
        dict: Staff lists grouped by unit and shift type
    """
    shifts_qs = Shift.objects.filter(
        date=date,
        user__isnull=False
    ).select_related('user', 'shift_type', 'unit').only(
        'user__first_name',
        'user__last_name', 
        'shift_type__name',
        'unit__name'
    )
    
    if care_home:
        shifts_qs = shifts_qs.filter(unit__care_home=care_home)
    
    # Limit to prevent massive memory usage
    shifts_qs = shifts_qs[:max_staff_per_unit * 50]
    
    staff_by_unit = defaultdict(lambda: {'day_staff': [], 'night_staff': []})
    
    for shift in shifts_qs:
        unit_name = shift.unit.name
        staff_name = f"{shift.user.full_name} ({shift.shift_type.get_name_display()})"
        
        if 'DAY' in shift.shift_type.name.upper():
            if len(staff_by_unit[unit_name]['day_staff']) < max_staff_per_unit:
                staff_by_unit[unit_name]['day_staff'].append(staff_name)
        elif 'NIGHT' in shift.shift_type.name.upper():
            if len(staff_by_unit[unit_name]['night_staff']) < max_staff_per_unit:
                staff_by_unit[unit_name]['night_staff'].append(staff_name)
    
    return dict(staff_by_unit)


def get_optimized_role_distribution(shifts_queryset):
    """
    Get role distribution using aggregation instead of iteration.
    
    Args:
        shifts_queryset: Pre-filtered Shift queryset
        
    Returns:
        dict: Counts by role name
    """
    role_counts = shifts_queryset.filter(
        user__isnull=False
    ).values('user__role__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    return {item['user__role__name']: item['count'] for item in role_counts if item['user__role__name']}


def get_weekly_shift_trends(care_home=None, weeks=12):
    """
    Get weekly shift trends using efficient date truncation and aggregation.
    
    Args:
        care_home: Optional CareHome filter
        weeks: Number of weeks to analyze
        
    Returns:
        list: Weekly aggregated data
    """
    start_date = datetime.now().date() - timedelta(weeks=weeks)
    
    shifts_qs = Shift.objects.filter(date__gte=start_date)
    
    if care_home:
        shifts_qs = shifts_qs.filter(unit__care_home=care_home)
    
    # Group by week using TruncDate
    weekly_data = shifts_qs.annotate(
        week=TruncDate('date')
    ).values('week').annotate(
        total_shifts=Count('id'),
        filled_shifts=Count('id', filter=Q(user__isnull=False)),
        vacant_shifts=Count('id', filter=Q(user__isnull=True))
    ).order_by('week')
    
    return list(weekly_data)
