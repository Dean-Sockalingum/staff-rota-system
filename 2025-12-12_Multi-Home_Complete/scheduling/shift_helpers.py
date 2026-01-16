"""
Helper methods for Shift model
These methods support the automated workflow system
"""

from datetime import timedelta
from django.conf import settings
from django.db.models import Count, Q


def is_understaffed(shift_instance):
    """
    Check if shift has insufficient staff coverage
    
    Returns:
        bool: True if shift needs more staff
    """
    current = shift_instance.current_staff_count()
    required = shift_instance.required_staff_count()
    return current < required


def current_staff_count(shift_instance):
    """
    Count currently assigned staff for this shift
    
    Returns:
        int: Number of staff assigned and confirmed
    """
    # Get the date and shift type
    same_shift_staff = shift_instance.__class__.objects.filter(
        date=shift_instance.date,
        shift_type=shift_instance.shift_type,
        unit=shift_instance.unit,
        status__in=['SCHEDULED', 'CONFIRMED']
    ).exclude(
        shift_classification='AGENCY'  # Don't count agency in regular count
    ).values('user').distinct().count()
    
    return same_shift_staff


def required_staff_count(shift_instance):
    """
    Get required staffing level for this shift
    
    Returns:
        int: Minimum required staff count
    """
    # Check if unit has staffing requirements model
    # This would be defined in Unit model or a StaffingRequirement model
    # For now, use a default based on shift type
    
    # Try to get from unit's staffing requirements
    try:
        from scheduling.models import StaffingRequirement
        requirement = StaffingRequirement.objects.filter(
            unit=shift_instance.unit,
            shift_type=shift_instance.shift_type
        ).first()
        
        if requirement:
            return requirement.minimum_staff
    except ImportError:
        pass
    
    # Fallback: Use shift type default or unit default
    if hasattr(shift_instance.shift_type, 'minimum_staff'):
        return shift_instance.shift_type.minimum_staff
    
    if hasattr(shift_instance.unit, 'minimum_staff_per_shift'):
        return shift_instance.unit.minimum_staff_per_shift
    
    # Ultimate fallback: Default values by shift pattern
    if shift_instance.shift_pattern == 'NIGHT_2000_0800':
        return 2  # Night shifts typically need fewer staff
    else:
        return 3  # Day shifts typically need more staff


def staff_shortfall(shift_instance):
    """
    Calculate staffing gap (how many staff short)
    
    Returns:
        int: Number of additional staff needed (0 if fully staffed)
    """
    shortfall = shift_instance.required_staff_count() - shift_instance.current_staff_count()
    return max(0, shortfall)


def calculate_ot_rate(shift_instance):
    """
    Calculate overtime hourly rate for this shift
    
    Returns:
        Decimal: Hourly rate for overtime (1.5x base rate)
    """
    from decimal import Decimal
    
    # Get staff member's base rate
    if hasattr(shift_instance.user, 'hourly_rate'):
        base_rate = shift_instance.user.hourly_rate
    elif hasattr(shift_instance.user, 'role') and hasattr(shift_instance.user.role, 'base_hourly_rate'):
        base_rate = shift_instance.user.role.base_hourly_rate
    else:
        # Fallback: Use default rates by role name
        role_defaults = {
            'Registered Nurse': Decimal('18.50'),
            'Healthcare Assistant': Decimal('12.50'),
            'Senior Carer': Decimal('14.00'),
            'Carer': Decimal('11.50'),
            'Unit Manager': Decimal('22.00'),
        }
        role_name = shift_instance.user.role.name if hasattr(shift_instance.user, 'role') else 'Carer'
        base_rate = role_defaults.get(role_name, Decimal('12.00'))
    
    # Apply OT multiplier from settings
    ot_multiplier = Decimal(str(settings.STAFFING_WORKFLOW.get('OT_HOURLY_RATE_MULTIPLIER', 1.5)))
    ot_rate = base_rate * ot_multiplier
    
    return ot_rate


def calculate_shift_cost(shift_instance):
    """
    Calculate total cost for this shift
    
    Returns:
        Decimal: Total cost based on classification
    """
    from decimal import Decimal
    
    hours = Decimal(str(shift_instance.duration_hours))
    
    if shift_instance.shift_classification == 'AGENCY':
        # Use actual agency rate if available
        if shift_instance.agency_hourly_rate:
            return hours * shift_instance.agency_hourly_rate
        
        # Otherwise estimate: base rate * 1.8
        base_rate = Decimal('15.00')  # Default estimate
        agency_multiplier = Decimal(str(settings.STAFFING_WORKFLOW.get('AGENCY_HOURLY_RATE_MULTIPLIER', 1.8)))
        return hours * base_rate * agency_multiplier
    
    elif shift_instance.shift_classification == 'OVERTIME':
        return hours * shift_instance.calculate_ot_rate()
    
    else:  # REGULAR
        # Regular rate
        if hasattr(shift_instance.user, 'hourly_rate'):
            return hours * shift_instance.user.hourly_rate
        else:
            return hours * Decimal('12.50')  # Default


def get_available_staff_for_date(shift_instance):
    """
    Get list of staff NOT already assigned on this date
    
    Returns:
        QuerySet: Available staff members
    """
    from scheduling.models import User, Shift
    
    # Get staff already scheduled this date
    scheduled_user_ids = Shift.objects.filter(
        date=shift_instance.date,
        status__in=['SCHEDULED', 'CONFIRMED']
    ).values_list('user_id', flat=True)
    
    # Get staff on leave this date
    from scheduling.models import LeaveRequest
    on_leave_user_ids = LeaveRequest.objects.filter(
        start_date__lte=shift_instance.date,
        end_date__gte=shift_instance.date,
        status='APPROVED'
    ).values_list('user_id', flat=True)
    
    # Combine exclusions
    excluded_ids = list(scheduled_user_ids) + list(on_leave_user_ids)
    
    # Return available staff
    available_staff = User.objects.filter(
        is_active=True,
        role__isnull=False
    ).exclude(
        id__in=excluded_ids
    ).exclude(
        role__name='Back Office Staff'  # Exclude admin staff
    )
    
    return available_staff


def is_consecutive_shift(shift_instance, other_shift):
    """
    Check if two shifts are consecutive (for WTD rest period checks)
    
    Args:
        other_shift: Another Shift instance
        
    Returns:
        bool: True if shifts are consecutive (same or adjacent days)
    """
    date_diff = abs((shift_instance.date - other_shift.date).days)
    
    # Same day but different shift times
    if date_diff == 0:
        return True
    
    # Adjacent days
    if date_diff == 1:
        # Check if they're actually consecutive (night shift followed by day shift)
        if shift_instance.date < other_shift.date:
            # shift_instance is earlier
            return shift_instance.shift_pattern == 'NIGHT_2000_0800' and other_shift.shift_pattern == 'DAY_0800_2000'
        else:
            # other_shift is earlier
            return other_shift.shift_pattern == 'NIGHT_2000_0800' and shift_instance.shift_pattern == 'DAY_0800_2000'
    
    return False


# Attach methods to Shift model
def attach_workflow_methods():
    """
    Attach helper methods to Shift model as instance methods
    Call this during Django app initialization
    """
    from scheduling.models import Shift
    
    # Add methods to Shift class
    Shift.is_understaffed = is_understaffed
    Shift.current_staff_count = current_staff_count
    Shift.required_staff_count = required_staff_count
    Shift.staff_shortfall = staff_shortfall
    Shift.calculate_ot_rate = calculate_ot_rate
    Shift.calculate_shift_cost = calculate_shift_cost
    Shift.get_available_staff_for_date = get_available_staff_for_date
    Shift.is_consecutive_shift = is_consecutive_shift
