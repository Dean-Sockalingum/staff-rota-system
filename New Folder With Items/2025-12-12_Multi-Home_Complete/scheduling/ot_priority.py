"""
Overtime Priority Scoring Algorithm
Smart OT distribution based on: 50% fair rotation, 30% qualifications, 20% proximity

This algorithm ensures:
- Equitable distribution of OT opportunities
- Right qualifications for the shift
- Minimal travel burden on staff
"""

from datetime import timedelta
from django.conf import settings
from django.db.models import Count, Q, Sum
from django.utils import timezone
from decimal import Decimal
import math


def calculate_fair_rotation_score(staff_member, max_score=50):
    """
    Calculate fair rotation score (50% of total priority)
    
    Logic: Staff with fewer recent OT shifts get higher scores
    
    Args:
        staff_member: User instance
        max_score: Maximum possible score (default 50)
        
    Returns:
        Decimal: Score from 0 to max_score
    """
    from scheduling.models import Shift
    
    # Count OT shifts in last 30 days
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    
    recent_ot_count = Shift.objects.filter(
        user=staff_member,
        date__gte=thirty_days_ago,
        shift_classification='OVERTIME',
        status__in=['SCHEDULED', 'CONFIRMED']
    ).count()
    
    # Count accepted OT offers (from OvertimeOffer model)
    try:
        from scheduling.models import OvertimeOffer
        recent_ot_offers_accepted = OvertimeOffer.objects.filter(
            staff_member=staff_member,
            status='ACCEPTED',
            batch__created_at__gte=timezone.now() - timedelta(days=30)
        ).count()
    except ImportError:
        recent_ot_offers_accepted = 0
    
    total_recent_ot = recent_ot_count + recent_ot_offers_accepted
    
    # Scoring: Inverse relationship - fewer OT = higher score
    # 0 OT shifts = full score
    # 5+ OT shifts = minimal score
    if total_recent_ot == 0:
        score = max_score
    elif total_recent_ot == 1:
        score = max_score * Decimal('0.9')
    elif total_recent_ot == 2:
        score = max_score * Decimal('0.75')
    elif total_recent_ot == 3:
        score = max_score * Decimal('0.5')
    elif total_recent_ot == 4:
        score = max_score * Decimal('0.25')
    else:
        score = max_score * Decimal('0.1')  # Minimum score, not zero
    
    return score


def calculate_qualification_score(staff_member, shift, max_score=30):
    """
    Calculate qualification/experience score (30% of total priority)
    
    Logic: 
    - Exact role match = full score
    - Higher qualification = 80% score
    - Related experience = 60% score
    - Basic qualification = 40% score
    
    Args:
        staff_member: User instance
        shift: Shift instance that needs coverage
        max_score: Maximum possible score (default 30)
        
    Returns:
        Decimal: Score from 0 to max_score
    """
    # Get staff role and shift requirement
    staff_role = staff_member.role if hasattr(staff_member, 'role') else None
    
    if not staff_role:
        return Decimal('0')
    
    # Get the role required for this shift
    # This could come from shift_type, unit requirements, or the original absent staff
    try:
        required_role = shift.shift_type.role if hasattr(shift.shift_type, 'role') else None
        if not required_role and hasattr(shift, 'user'):
            required_role = shift.user.role
    except:
        required_role = None
    
    if not required_role:
        # No specific requirement - base on staff seniority
        seniority_scores = {
            'Unit Manager': max_score,
            'Deputy Manager': max_score * Decimal('0.9'),
            'Registered Nurse': max_score * Decimal('0.85'),
            'Senior Carer': max_score * Decimal('0.7'),
            'Healthcare Assistant': max_score * Decimal('0.6'),
            'Carer': max_score * Decimal('0.5'),
        }
        return seniority_scores.get(staff_role.name, max_score * Decimal('0.5'))
    
    # Calculate match score
    if staff_role == required_role:
        # Exact match
        score = max_score
    elif _is_higher_qualification(staff_role, required_role):
        # Higher qualification
        score = max_score * Decimal('0.8')
    elif _is_related_role(staff_role, required_role):
        # Related experience
        score = max_score * Decimal('0.6')
    else:
        # Basic qualification only
        score = max_score * Decimal('0.4')
    
    # Bonus for experience (years in role)
    if hasattr(staff_member, 'date_joined'):
        years_experience = (timezone.now().date() - staff_member.date_joined.date()).days / 365.25
        if years_experience >= 5:
            score *= Decimal('1.1')  # 10% bonus for 5+ years
        elif years_experience >= 3:
            score *= Decimal('1.05')  # 5% bonus for 3+ years
    
    # Cap at max_score
    return min(score, Decimal(str(max_score)))


def calculate_proximity_score(staff_member, shift, max_score=20):
    """
    Calculate travel distance/time score (20% of total priority)
    
    Logic: Closer staff get higher scores
    
    Args:
        staff_member: User instance
        shift: Shift instance
        max_score: Maximum possible score (default 20)
        
    Returns:
        Decimal: Score from 0 to max_score
    """
    # Check if shift is at staff member's home unit
    if hasattr(staff_member, 'unit') and shift.unit == staff_member.unit:
        # Same unit - full score
        return Decimal(str(max_score))
    
    # Check if staff has assigned care home
    if hasattr(staff_member, 'care_home') and hasattr(shift.unit, 'care_home'):
        if staff_member.care_home == shift.unit.care_home:
            # Same care home, different unit - high score
            return max_score * Decimal('0.9')
    
    # Calculate distance if location data available
    if hasattr(staff_member, 'postcode') and hasattr(shift.unit, 'postcode'):
        distance_km = _calculate_distance(staff_member.postcode, shift.unit.postcode)
        
        if distance_km is not None:
            # Score decreases with distance
            if distance_km <= 5:
                score = max_score
            elif distance_km <= 10:
                score = max_score * Decimal('0.8')
            elif distance_km <= 15:
                score = max_score * Decimal('0.6')
            elif distance_km <= 20:
                score = max_score * Decimal('0.4')
            elif distance_km <= 30:
                score = max_score * Decimal('0.2')
            else:
                score = max_score * Decimal('0.1')
            
            return score
    
    # Default: medium score if no location data
    return max_score * Decimal('0.5')


def calculate_total_priority_score(staff_member, shift):
    """
    Calculate total priority score combining all factors
    
    Args:
        staff_member: User instance
        shift: Shift instance
        
    Returns:
        dict: {
            'total_score': Decimal (0-100),
            'fair_rotation': Decimal (0-50),
            'qualification': Decimal (0-30),
            'proximity': Decimal (0-20),
            'rank': int (set later when comparing all staff)
        }
    """
    weights = settings.STAFFING_WORKFLOW.get('OT_PRIORITY_WEIGHTS', {
        'FAIR_ROTATION': 50,
        'QUALIFICATION': 30,
        'PROXIMITY': 20,
    })
    
    fair_rotation = calculate_fair_rotation_score(staff_member, weights['FAIR_ROTATION'])
    qualification = calculate_qualification_score(staff_member, shift, weights['QUALIFICATION'])
    proximity = calculate_proximity_score(staff_member, shift, weights['PROXIMITY'])
    
    total = fair_rotation + qualification + proximity
    
    return {
        'total_score': total,
        'fair_rotation': fair_rotation,
        'qualification': qualification,
        'proximity': proximity,
        'staff_member': staff_member,
        'rank': None  # Set during ranking
    }


def rank_staff_for_ot_offer(shift, eligible_staff_list):
    """
    Rank staff members by priority score
    
    Args:
        shift: Shift instance that needs coverage
        eligible_staff_list: List of User instances (already WTD compliant)
        
    Returns:
        list: Sorted list of dicts with scores and rankings
    """
    scored_staff = []
    
    for staff_member in eligible_staff_list:
        score_data = calculate_total_priority_score(staff_member, shift)
        scored_staff.append(score_data)
    
    # Sort by total score (descending)
    scored_staff.sort(key=lambda x: x['total_score'], reverse=True)
    
    # Add rankings
    for rank, staff_data in enumerate(scored_staff, start=1):
        staff_data['rank'] = rank
    
    return scored_staff


def get_top_ot_candidates(shift, eligible_staff_queryset, max_offers=20):
    """
    Get top N staff members for OT offer
    
    Args:
        shift: Shift instance that needs coverage
        eligible_staff_queryset: QuerySet of eligible User objects
        max_offers: Maximum number of offers to make (default 20)
        
    Returns:
        list: Top N scored staff members with full scoring details
    """
    from scheduling.wdt_compliance import get_wdt_compliant_staff_for_ot
    
    # First filter for WTD compliance
    wdt_compliant = get_wdt_compliant_staff_for_ot(shift, eligible_staff_queryset)
    compliant_staff = [staff for staff, compliance in wdt_compliant]
    
    # Rank by priority
    ranked_staff = rank_staff_for_ot_offer(shift, compliant_staff)
    
    # Get max_offers from settings if not specified
    if max_offers is None:
        max_offers = settings.STAFFING_WORKFLOW.get('MAX_OT_OFFERS_PER_BATCH', 20)
    
    # Return top N
    return ranked_staff[:max_offers]


# Helper functions

def _is_higher_qualification(staff_role, required_role):
    """
    Check if staff has higher qualification than required
    
    Args:
        staff_role: Role instance of staff
        required_role: Role instance required for shift
        
    Returns:
        bool: True if staff role is senior to required
    """
    # Define role hierarchy
    role_hierarchy = {
        'Unit Manager': 6,
        'Deputy Manager': 5,
        'Registered Nurse': 4,
        'Senior Carer': 3,
        'Healthcare Assistant': 2,
        'Carer': 1,
    }
    
    staff_level = role_hierarchy.get(staff_role.name, 0)
    required_level = role_hierarchy.get(required_role.name, 0)
    
    return staff_level > required_level


def _is_related_role(staff_role, required_role):
    """
    Check if roles are related/compatible
    
    Args:
        staff_role: Role instance of staff
        required_role: Role instance required
        
    Returns:
        bool: True if roles are related
    """
    # Define related role groups
    related_groups = [
        {'Carer', 'Healthcare Assistant', 'Senior Carer'},
        {'Registered Nurse', 'Senior Carer'},
        {'Unit Manager', 'Deputy Manager', 'Registered Nurse'},
    ]
    
    staff_name = staff_role.name
    required_name = required_role.name
    
    for group in related_groups:
        if staff_name in group and required_name in group:
            return True
    
    return False


def _calculate_distance(postcode1, postcode2):
    """
    Calculate distance between two postcodes
    
    Args:
        postcode1: First postcode string
        postcode2: Second postcode string
        
    Returns:
        float: Distance in kilometers, or None if can't calculate
    """
    # This would normally use a geolocation API or database
    # For now, return None to trigger default scoring
    # In production, integrate with Google Maps API, Postcodes.io, etc.
    
    # Placeholder: if postcodes are the same, distance is 0
    if postcode1 and postcode2:
        # Remove spaces and compare
        p1 = postcode1.replace(' ', '').upper()
        p2 = postcode2.replace(' ', '').upper()
        
        if p1 == p2:
            return 0.0
        
        # Check if same outward code (first part)
        if p1.split()[0] == p2.split()[0] if ' ' in postcode1 and ' ' in postcode2 else p1[:4] == p2[:4]:
            return 2.0  # Estimate: same area ~2km
    
    # Can't calculate - return None
    return None


def generate_ot_priority_report(shift, staff_list):
    """
    Generate detailed report of OT priority scoring
    
    Args:
        shift: Shift instance
        staff_list: List of User instances to score
        
    Returns:
        dict: Detailed scoring report
    """
    ranked = rank_staff_for_ot_offer(shift, staff_list)
    
    return {
        'shift_date': shift.date,
        'shift_unit': shift.unit.name,
        'total_candidates': len(ranked),
        'top_10': ranked[:10],
        'scoring_weights': settings.STAFFING_WORKFLOW.get('OT_PRIORITY_WEIGHTS'),
        'generated_at': timezone.now(),
        'all_scores': ranked
    }
