"""
Working Time Directive (WTD) Compliance Checker
Ensures staff don't exceed legal working time limits

UK WTD Requirements:
- Maximum 48 hours per week (17-week rolling average)
- Minimum 11 hours rest between shifts
- 24-hour rest period per week
"""

from datetime import datetime, timedelta, time
from django.conf import settings
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal


def calculate_weekly_hours(staff_member, week_start_date=None, weeks=1):
    """
    Calculate total hours worked in a given week or period
    
    Args:
        staff_member: User instance
        week_start_date: Date to start counting from (defaults to this week's Monday)
        weeks: Number of weeks to calculate (default 1)
        
    Returns:
        Decimal: Total hours worked in the period
    """
    from scheduling.models import Shift
    
    if week_start_date is None:
        # Get this week's Monday
        today = timezone.now().date()
        week_start_date = today - timedelta(days=today.weekday())
    
    # Calculate period end
    period_end = week_start_date + timedelta(weeks=weeks)
    
    # Get all confirmed shifts in this period
    shifts = Shift.objects.filter(
        user=staff_member,
        date__gte=week_start_date,
        date__lt=period_end,
        status__in=['SCHEDULED', 'CONFIRMED']
    )
    
    # Calculate total hours
    total_hours = Decimal('0.00')
    for shift in shifts:
        total_hours += Decimal(str(shift.duration_hours))
    
    return total_hours


def calculate_rolling_average_hours(staff_member, weeks=17):
    """
    Calculate rolling average hours over specified weeks
    
    Args:
        staff_member: User instance
        weeks: Number of weeks for rolling average (default 17 for WTD)
        
    Returns:
        Decimal: Average hours per week over the period
    """
    # Get date 'weeks' ago
    end_date = timezone.now().date()
    start_date = end_date - timedelta(weeks=weeks)
    
    # Calculate total hours in period
    total_hours = calculate_weekly_hours(staff_member, start_date, weeks)
    
    # Calculate average
    average_hours = total_hours / Decimal(str(weeks))
    
    return average_hours


def check_rest_period(shift1, shift2):
    """
    Check if there's sufficient rest between two shifts
    
    Args:
        shift1: First Shift instance
        shift2: Second Shift instance
        
    Returns:
        dict: {
            'compliant': bool,
            'hours_rest': Decimal,
            'required_hours': Decimal,
            'shortfall': Decimal (if non-compliant)
        }
    """
    from scheduling.models import Shift
    
    min_rest_hours = Decimal(str(settings.STAFFING_WORKFLOW.get('WTD_MIN_REST_HOURS', 11)))
    
    # Determine which shift comes first
    if shift1.date < shift2.date:
        earlier_shift = shift1
        later_shift = shift2
    elif shift1.date > shift2.date:
        earlier_shift = shift2
        later_shift = shift1
    else:
        # Same day - check times
        if shift1.start_time < shift2.start_time:
            earlier_shift = shift1
            later_shift = shift2
        else:
            earlier_shift = shift2
            later_shift = shift1
    
    # Calculate end datetime of earlier shift
    earlier_end = datetime.combine(earlier_shift.date, earlier_shift.end_time)
    if earlier_shift.end_time < earlier_shift.start_time:
        # Overnight shift
        earlier_end += timedelta(days=1)
    
    # Calculate start datetime of later shift
    later_start = datetime.combine(later_shift.date, later_shift.start_time)
    
    # Calculate rest period
    rest_period = later_start - earlier_end
    hours_rest = Decimal(str(rest_period.total_seconds() / 3600))
    
    # Check compliance
    compliant = hours_rest >= min_rest_hours
    shortfall = max(Decimal('0'), min_rest_hours - hours_rest) if not compliant else Decimal('0')
    
    return {
        'compliant': compliant,
        'hours_rest': hours_rest,
        'required_hours': min_rest_hours,
        'shortfall': shortfall,
        'earlier_shift': earlier_shift,
        'later_shift': later_shift
    }


def is_wdt_compliant_for_ot(staff_member, proposed_shift_date, proposed_shift_hours=12):
    """
    Check if staff member can work OT without violating WTD
    
    Args:
        staff_member: User instance
        proposed_shift_date: Date of proposed OT shift
        proposed_shift_hours: Hours for the proposed shift (default 12)
        
    Returns:
        dict: {
            'compliant': bool,
            'weekly_hours_after': Decimal,
            'max_weekly_hours': Decimal,
            'rolling_average_after': Decimal,
            'rest_period_compliant': bool,
            'violations': list of str (reasons if non-compliant)
        }
    """
    from scheduling.models import Shift
    
    max_weekly_hours = Decimal(str(settings.STAFFING_WORKFLOW.get('WTD_MAX_HOURS_PER_WEEK', 48)))
    rolling_weeks = settings.STAFFING_WORKFLOW.get('WTD_ROLLING_WEEKS', 17)
    
    violations = []
    
    # Check 1: Weekly hours limit
    # Get current week's hours
    week_start = proposed_shift_date - timedelta(days=proposed_shift_date.weekday())
    current_weekly_hours = calculate_weekly_hours(staff_member, week_start, 1)
    weekly_hours_after = current_weekly_hours + Decimal(str(proposed_shift_hours))
    
    if weekly_hours_after > max_weekly_hours:
        violations.append(
            f"Weekly hours would exceed limit: {weekly_hours_after}hrs > {max_weekly_hours}hrs"
        )
    
    # Check 2: Rolling average (17 weeks)
    current_rolling_avg = calculate_rolling_average_hours(staff_member, rolling_weeks)
    # Estimate impact (simplified - assumes even distribution)
    estimated_rolling_avg = current_rolling_avg + (Decimal(str(proposed_shift_hours)) / Decimal(str(rolling_weeks)))
    
    if estimated_rolling_avg > max_weekly_hours:
        violations.append(
            f"Rolling average would exceed limit: {estimated_rolling_avg:.2f}hrs > {max_weekly_hours}hrs"
        )
    
    # Check 3: Rest period with adjacent shifts
    rest_period_compliant = True
    
    # Check day before
    day_before_shifts = Shift.objects.filter(
        user=staff_member,
        date=proposed_shift_date - timedelta(days=1),
        status__in=['SCHEDULED', 'CONFIRMED']
    )
    
    for earlier_shift in day_before_shifts:
        # Create a mock shift for the proposed OT
        # We'll check against both common shift patterns
        for shift_pattern in ['DAY_0800_2000', 'NIGHT_2000_0800']:
            mock_shift = type('obj', (object,), {
                'date': proposed_shift_date,
                'start_time': time(8, 0) if shift_pattern == 'DAY_0800_2000' else time(20, 0),
                'end_time': time(20, 0) if shift_pattern == 'DAY_0800_2000' else time(8, 0),
                'shift_pattern': shift_pattern
            })()
            
            rest_check = check_rest_period(earlier_shift, mock_shift)
            if not rest_check['compliant']:
                violations.append(
                    f"Insufficient rest from previous shift: {rest_check['hours_rest']:.1f}hrs < {rest_check['required_hours']}hrs"
                )
                rest_period_compliant = False
                break
    
    # Check day after
    day_after_shifts = Shift.objects.filter(
        user=staff_member,
        date=proposed_shift_date + timedelta(days=1),
        status__in=['SCHEDULED', 'CONFIRMED']
    )
    
    for later_shift in day_after_shifts:
        # Check with both shift patterns
        for shift_pattern in ['DAY_0800_2000', 'NIGHT_2000_0800']:
            mock_shift = type('obj', (object,), {
                'date': proposed_shift_date,
                'start_time': time(8, 0) if shift_pattern == 'DAY_0800_2000' else time(20, 0),
                'end_time': time(20, 0) if shift_pattern == 'DAY_0800_2000' else time(8, 0),
                'shift_pattern': shift_pattern
            })()
            
            rest_check = check_rest_period(mock_shift, later_shift)
            if not rest_check['compliant']:
                violations.append(
                    f"Insufficient rest before next shift: {rest_check['hours_rest']:.1f}hrs < {rest_check['required_hours']}hrs"
                )
                rest_period_compliant = False
                break
    
    # Overall compliance
    compliant = len(violations) == 0
    
    return {
        'compliant': compliant,
        'weekly_hours_after': weekly_hours_after,
        'max_weekly_hours': max_weekly_hours,
        'rolling_average_after': estimated_rolling_avg,
        'rest_period_compliant': rest_period_compliant,
        'violations': violations,
        'current_weekly_hours': current_weekly_hours,
        'current_rolling_average': current_rolling_avg
    }


def get_wdt_compliant_staff_for_ot(shift, eligible_staff_queryset):
    """
    Filter staff queryset to only those who are WTD compliant for OT
    
    Args:
        shift: The Shift instance that needs OT coverage
        eligible_staff_queryset: QuerySet of User objects
        
    Returns:
        list: List of tuples (staff_member, compliance_details)
    """
    compliant_staff = []
    
    for staff_member in eligible_staff_queryset:
        compliance = is_wdt_compliant_for_ot(
            staff_member,
            shift.date,
            shift.duration_hours
        )
        
        if compliance['compliant']:
            compliant_staff.append((staff_member, compliance))
    
    return compliant_staff


def calculate_max_ot_hours_available(staff_member, proposed_date):
    """
    Calculate maximum OT hours staff can work without WTD violation
    
    Args:
        staff_member: User instance
        proposed_date: Date of proposed OT
        
    Returns:
        Decimal: Maximum hours available (0 if none available)
    """
    max_weekly_hours = Decimal(str(settings.STAFFING_WORKFLOW.get('WTD_MAX_HOURS_PER_WEEK', 48)))
    
    # Get current week's hours
    week_start = proposed_date - timedelta(days=proposed_date.weekday())
    current_weekly_hours = calculate_weekly_hours(staff_member, week_start, 1)
    
    # Calculate available hours
    available_hours = max_weekly_hours - current_weekly_hours
    
    # Cannot be negative
    return max(Decimal('0'), available_hours)


def generate_wdt_compliance_report(staff_member, weeks=4):
    """
    Generate compliance report for a staff member
    
    Args:
        staff_member: User instance
        weeks: Number of weeks to report on
        
    Returns:
        dict: Comprehensive compliance report
    """
    from scheduling.models import Shift
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(weeks=weeks)
    
    # Get all shifts in period
    shifts = Shift.objects.filter(
        user=staff_member,
        date__gte=start_date,
        date__lte=end_date,
        status__in=['SCHEDULED', 'CONFIRMED']
    ).order_by('date')
    
    # Calculate weekly breakdown
    weekly_hours = []
    for week_offset in range(weeks):
        week_start = start_date + timedelta(weeks=week_offset)
        hours = calculate_weekly_hours(staff_member, week_start, 1)
        weekly_hours.append({
            'week_start': week_start,
            'week_end': week_start + timedelta(days=6),
            'hours': hours,
            'compliant': hours <= Decimal(str(settings.STAFFING_WORKFLOW.get('WTD_MAX_HOURS_PER_WEEK', 48)))
        })
    
    # Check for rest period violations
    rest_violations = []
    shift_list = list(shifts)
    for i in range(len(shift_list) - 1):
        rest_check = check_rest_period(shift_list[i], shift_list[i+1])
        if not rest_check['compliant']:
            rest_violations.append({
                'shift1_date': shift_list[i].date,
                'shift2_date': shift_list[i+1].date,
                'hours_rest': rest_check['hours_rest'],
                'shortfall': rest_check['shortfall']
            })
    
    # Rolling average
    rolling_avg = calculate_rolling_average_hours(staff_member, 17)
    
    return {
        'staff_member': staff_member.get_full_name(),
        'period_start': start_date,
        'period_end': end_date,
        'weekly_breakdown': weekly_hours,
        'rest_period_violations': rest_violations,
        'rolling_average_17_weeks': rolling_avg,
        'overall_compliant': rolling_avg <= Decimal(str(settings.STAFFING_WORKFLOW.get('WTD_MAX_HOURS_PER_WEEK', 48))) and len(rest_violations) == 0,
        'total_shifts': shifts.count(),
        'total_hours': sum(w['hours'] for w in weekly_hours)
    }
