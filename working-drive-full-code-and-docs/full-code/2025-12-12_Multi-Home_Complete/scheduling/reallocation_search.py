"""
Cross-Home Staff Reallocation Search
Priority 1: Zero-cost internal staff movement

Finds eligible staff from other care homes/units who can cover shifts
Criteria: Same/higher qualification, within travel limits, WTD compliant
"""

from datetime import timedelta
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from decimal import Decimal


def find_eligible_staff_for_reallocation(shift, source_care_home=None):
    """
    Find staff from other units/homes who can cover this shift
    
    Args:
        shift: Shift instance that needs coverage
        source_care_home: CareHome instance (optional, defaults to shift's home)
        
    Returns:
        list: Sorted list of dicts with staff and eligibility details
    """
    from scheduling.models import User, Shift as ShiftModel, LeaveRequest
    from scheduling.wdt_compliance import is_wdt_compliant_for_ot
    
    # Get source care home
    if source_care_home is None:
        if hasattr(shift.unit, 'care_home'):
            source_care_home = shift.unit.care_home
        else:
            # Can't perform cross-home search without home info
            return []
    
    # Get required role for this shift
    required_role = _get_shift_required_role(shift)
    
    # Step 1: Get all potentially eligible staff
    # - Active users
    # - Not in same unit
    # - Same or higher qualification
    # - Not on leave
    # - Not already scheduled that day
    
    # Get scheduled user IDs for this date
    scheduled_ids = ShiftModel.objects.filter(
        date=shift.date,
        status__in=['SCHEDULED', 'CONFIRMED']
    ).values_list('user_id', flat=True)
    
    # Get users on leave
    on_leave_ids = LeaveRequest.objects.filter(
        start_date__lte=shift.date,
        end_date__gte=shift.date,
        status='APPROVED'
    ).values_list('user_id', flat=True)
    
    # Build base queryset
    eligible_staff = User.objects.filter(
        is_active=True,
        role__isnull=False
    ).exclude(
        pk__in=list(scheduled_ids) + list(on_leave_ids)
    ).exclude(
        unit=shift.unit  # Not from same unit
    ).exclude(
        role__name='Back Office Staff'  # Exclude admin staff
    )
    
    # Filter by qualification
    if required_role:
        # Get same role or higher qualifications
        eligible_roles = _get_eligible_roles_for_shift(required_role)
        eligible_staff = eligible_staff.filter(role__name__in=eligible_roles)
    
    # Step 2: Check additional eligibility criteria for each staff member
    eligible_list = []
    max_travel_minutes = settings.STAFFING_WORKFLOW.get('REALLOCATION_MAX_TRAVEL_MINUTES', 30)
    max_radius_km = settings.STAFFING_WORKFLOW.get('REALLOCATION_SEARCH_RADIUS_KM', 15)
    
    for staff_member in eligible_staff:
        eligibility = _check_reallocation_eligibility(
            staff_member,
            shift,
            source_care_home,
            max_travel_minutes,
            max_radius_km
        )
        
        if eligibility['eligible']:
            eligible_list.append(eligibility)
    
    # Step 3: Sort by priority
    # Priority order from settings
    priority_order = settings.STAFFING_WORKFLOW.get('REALLOCATION_PRIORITY_ORDER', [
        'same_qualification',
        'higher_qualification',
        'willing_to_travel',
    ])
    
    sorted_list = _sort_by_reallocation_priority(eligible_list, priority_order)
    
    return sorted_list


def _get_shift_required_role(shift):
    """Get the role required for this shift"""
    # Try shift type first
    if hasattr(shift.shift_type, 'role') and shift.shift_type.role:
        return shift.shift_type.role
    
    # Try original staff member's role
    if hasattr(shift, 'user') and shift.user and hasattr(shift.user, 'role'):
        return shift.user.role
    
    # Try unit's preferred role
    if hasattr(shift.unit, 'primary_role') and shift.unit.primary_role:
        return shift.unit.primary_role
    
    return None


def _get_eligible_roles_for_shift(required_role):
    """
    Get list of roles that can fulfill this shift requirement
    
    Args:
        required_role: Role instance
        
    Returns:
        list: Role names that are eligible
    """
    role_hierarchy = {
        'Unit Manager': ['Unit Manager', 'Deputy Manager'],
        'Deputy Manager': ['Unit Manager', 'Deputy Manager', 'Registered Nurse'],
        'Registered Nurse': ['Unit Manager', 'Deputy Manager', 'Registered Nurse'],
        'Senior Carer': ['Unit Manager', 'Deputy Manager', 'Registered Nurse', 'Senior Carer'],
        'Healthcare Assistant': ['Unit Manager', 'Deputy Manager', 'Registered Nurse', 'Senior Carer', 'Healthcare Assistant'],
        'Carer': ['Unit Manager', 'Deputy Manager', 'Registered Nurse', 'Senior Carer', 'Healthcare Assistant', 'Carer'],
    }
    
    eligible_roles = role_hierarchy.get(required_role.name, [required_role.name])
    return eligible_roles


def _check_reallocation_eligibility(staff_member, shift, source_care_home, max_travel_minutes, max_radius_km):
    """
    Check if staff member is eligible for reallocation
    
    Returns:
        dict: Eligibility details
    """
    from scheduling.wdt_compliance import is_wdt_compliant_for_ot
    
    eligibility = {
        'eligible': False,
        'staff_member': staff_member,
        'staff_name': staff_member.full_name,
        'staff_role': staff_member.role.name if hasattr(staff_member, 'role') and staff_member.role else 'Unknown',
        'from_home': None,
        'from_unit': None,
        'qualification_match': None,
        'distance_km': None,
        'travel_time_minutes': None,
        'wdt_compliant': False,
        'willing_to_travel': False,
        'reasons_ineligible': []
    }
    
    # Get staff's home
    if hasattr(staff_member, 'unit') and hasattr(staff_member.unit, 'care_home'):
        eligibility['from_home'] = staff_member.unit.care_home
        eligibility['from_unit'] = staff_member.unit
    else:
        eligibility['from_home'] = getattr(staff_member, 'care_home', None)
        eligibility['from_unit'] = getattr(staff_member, 'unit', None)
    
    # Check 1: Qualification match
    required_role = _get_shift_required_role(shift)
    if required_role:
        if staff_member.role == required_role:
            eligibility['qualification_match'] = 'EXACT'
        elif staff_member.role.name in _get_eligible_roles_for_shift(required_role):
            eligibility['qualification_match'] = 'HIGHER'
        else:
            eligibility['reasons_ineligible'].append('Insufficient qualification')
            return eligibility
    else:
        eligibility['qualification_match'] = 'ASSUMED_OK'
    
    # Check 2: Travel distance
    if hasattr(staff_member, 'postcode') and hasattr(shift.unit, 'postcode'):
        distance = _estimate_distance(staff_member.postcode, shift.unit.postcode)
        travel_time = _estimate_travel_time(distance)
        
        eligibility['distance_km'] = distance
        eligibility['travel_time_minutes'] = travel_time
        
        if distance > max_radius_km:
            eligibility['reasons_ineligible'].append(f'Too far: {distance:.1f}km > {max_radius_km}km limit')
            return eligibility
        
        if travel_time > max_travel_minutes:
            eligibility['reasons_ineligible'].append(f'Travel time too long: {travel_time:.0f}min > {max_travel_minutes}min limit')
            return eligibility
    else:
        # No location data - assume OK but flag
        eligibility['distance_km'] = None
        eligibility['travel_time_minutes'] = None
    
    # Check 3: WTD compliance
    wdt_check = is_wdt_compliant_for_ot(staff_member, shift.date, shift.duration_hours)
    eligibility['wdt_compliant'] = wdt_check['compliant']
    
    if not wdt_check['compliant']:
        eligibility['reasons_ineligible'].append(f"WTD violation: {', '.join(wdt_check['violations'])}")
        return eligibility
    
    # Check 4: Willingness to travel (optional field on User model)
    if hasattr(staff_member, 'willing_to_travel'):
        eligibility['willing_to_travel'] = staff_member.willing_to_travel
    else:
        # Assume willing if no preference specified
        eligibility['willing_to_travel'] = True
    
    # All checks passed!
    eligibility['eligible'] = True
    
    return eligibility


def _estimate_distance(postcode1, postcode2):
    """
    Estimate distance between postcodes
    
    Returns:
        float: Distance in kilometers
    """
    # This would use a real geolocation service in production
    # For now, use simple heuristic
    
    if not postcode1 or not postcode2:
        return 10.0  # Default assumption
    
    p1 = postcode1.replace(' ', '').upper()
    p2 = postcode2.replace(' ', '').upper()
    
    if p1 == p2:
        return 0.0
    
    # Same outward code (first part before space)
    if p1.split()[0] == p2.split()[0] if ' ' in postcode1 and ' ' in postcode2 else p1[:4] == p2[:4]:
        return 3.0  # Estimate: same area ~3km
    
    # Different areas - estimate based on postcode similarity
    # This is very rough - replace with real API
    return 12.0  # Default estimate for different areas


def _estimate_travel_time(distance_km):
    """
    Estimate travel time from distance
    
    Args:
        distance_km: Distance in kilometers
        
    Returns:
        float: Estimated travel time in minutes
    """
    # Assume average speed of 40 km/h for urban/suburban driving
    avg_speed_kmh = 40
    travel_time_hours = distance_km / avg_speed_kmh
    travel_time_minutes = travel_time_hours * 60
    
    # Add buffer for parking, security, etc. (5 minutes)
    return travel_time_minutes + 5


def _sort_by_reallocation_priority(eligible_list, priority_order):
    """
    Sort eligible staff by reallocation priority
    
    Args:
        eligible_list: List of eligibility dicts
        priority_order: List of priority criteria
        
    Returns:
        list: Sorted eligible staff
    """
    def priority_score(item):
        score = 0
        
        # Same qualification gets highest priority (score 1000)
        if item['qualification_match'] == 'EXACT':
            score += 1000
        elif item['qualification_match'] == 'HIGHER':
            score += 800
        
        # Shorter distance is better (inverse score, max 500 points)
        if item['distance_km'] is not None:
            # 0km = 500 points, 15km = 0 points
            distance_score = max(0, 500 - (item['distance_km'] * 33))
            score += distance_score
        else:
            score += 250  # Middle score if no distance data
        
        # Willing to travel bonus (200 points)
        if item['willing_to_travel']:
            score += 200
        
        # Same home but different unit gets bonus (300 points)
        if item['from_home'] and hasattr(item['staff_member'], 'unit'):
            if hasattr(item['staff_member'].unit, 'care_home'):
                # Would need to compare with shift's care_home
                # For now, assume not same home
                pass
        
        return -score  # Negative for descending sort
    
    return sorted(eligible_list, key=priority_score)


def create_reallocation_requests(shift, cover_request, eligible_staff_list, max_requests=5):
    """
    Create ReallocationRequest records for top eligible staff
    
    Args:
        shift: Shift instance needing coverage
        cover_request: StaffingCoverRequest instance
        eligible_staff_list: Sorted list from find_eligible_staff_for_reallocation()
        max_requests: Maximum number of requests to create (default 5)
        
    Returns:
        list: Created ReallocationRequest instances
    """
    from scheduling.models import ReallocationRequest
    from scheduling.notifications import notify_reallocation_request
    
    created_requests = []
    
    for item in eligible_staff_list[:max_requests]:
        staff_member = item['staff_member']
        
        # Create reallocation request
        reallocation = ReallocationRequest.objects.create(
            cover_request=cover_request,
            staff_member=staff_member,
            from_care_home=item['from_home'],
            to_care_home=shift.unit.care_home if hasattr(shift.unit, 'care_home') else None,
            shift=shift,
            qualification_match=item['qualification_match'],
            estimated_travel_km=item['distance_km'],
            estimated_travel_minutes=item['travel_time_minutes'],
            status='PENDING'
        )
        
        # Send notification
        notify_reallocation_request(
            staff_member,
            shift,
            item['from_home'],
            shift.unit.care_home if hasattr(shift.unit, 'care_home') else None
        )
        
        created_requests.append(reallocation)
    
    return created_requests


def get_reallocation_summary(shift):
    """
    Get summary of reallocation options for a shift
    
    Args:
        shift: Shift instance
        
    Returns:
        dict: Summary with counts and details
    """
    eligible = find_eligible_staff_for_reallocation(shift)
    
    summary = {
        'total_eligible': len(eligible),
        'by_qualification': {
            'exact_match': len([e for e in eligible if e['qualification_match'] == 'EXACT']),
            'higher_qualification': len([e for e in eligible if e['qualification_match'] == 'HIGHER']),
        },
        'by_distance': {
            'within_5km': len([e for e in eligible if e['distance_km'] and e['distance_km'] <= 5]),
            'within_10km': len([e for e in eligible if e['distance_km'] and e['distance_km'] <= 10]),
            'within_15km': len([e for e in eligible if e['distance_km'] and e['distance_km'] <= 15]),
        },
        'willing_to_travel': len([e for e in eligible if e['willing_to_travel']]),
        'top_5_candidates': eligible[:5],
        'shift_date': shift.date,
        'shift_unit': shift.unit.name,
        'required_role': _get_shift_required_role(shift).name if _get_shift_required_role(shift) else 'Any'
    }
    
    return summary
