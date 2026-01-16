"""
Leave Approval Likelihood Predictor
====================================

Analyzes the probability of leave approval based on:
- Current staffing levels
- Existing approved leave
- Leave balance and usage patterns
- Business rules (blackout dates, minimum coverage)
- Historical approval patterns

Returns actionable insights to help staff choose optimal leave dates.
"""

from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta, date
from decimal import Decimal
from scheduling.models import Shift, LeaveRequest, Unit
from scheduling.models_multi_home import CareHome
from staff_records.models import AnnualLeaveEntitlement, StaffProfile


def predict_leave_approval_likelihood(user, start_date, end_date):
    """
    Predict the likelihood of leave approval for given dates.
    
    Args:
        user: User requesting leave
        start_date: Proposed start date
        end_date: Proposed end date
    
    Returns:
        dict with:
            - likelihood_score: 0-100 percentage
            - approval_status: 'HIGH', 'MEDIUM', 'LOW'
            - factors: list of factors affecting likelihood
            - recommendations: list of suggestions
            - can_proceed: boolean if user should proceed with request
            - alternative_dates: suggested better dates if likelihood is low
    """
    
    # Initialize result
    result = {
        'likelihood_score': 100,
        'approval_status': 'HIGH',
        'factors': [],
        'recommendations': [],
        'can_proceed': True,
        'alternative_dates': [],
        'warnings': []
    }
    
    # Get user's unit and care home
    try:
        profile = user.profile
        user_unit = profile.unit
        care_home = user_unit.care_home if user_unit else None
    except:
        result['likelihood_score'] = 0
        result['approval_status'] = 'ERROR'
        result['factors'].append('❌ Unable to determine your unit assignment')
        result['can_proceed'] = False
        return result
    
    # Check 1: Leave balance
    try:
        entitlement = AnnualLeaveEntitlement.objects.get(
            profile=profile,
            leave_year_start__lte=start_date,
            leave_year_end__gte=end_date
        )
        
        # Calculate days requested
        working_days = Shift.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date
        ).count()
        
        if working_days == 0:
            # Estimate based on weekdays
            current = start_date
            working_days = 0
            while current <= end_date:
                if current.weekday() < 5:
                    working_days += 1
                current += timedelta(days=1)
        
        # Calculate hours
        if user.role and user.role.is_management:
            hours_per_day = Decimal('7.00')
        elif entitlement.contracted_hours_per_week >= Decimal('30.00'):
            hours_per_day = Decimal('11.66')
        else:
            hours_per_day = Decimal('12.00')
        
        hours_needed = Decimal(str(working_days)) * hours_per_day
        
        if hours_needed > entitlement.hours_remaining:
            result['likelihood_score'] -= 50
            result['factors'].append(f'❌ Insufficient leave balance: Need {hours_needed}hrs, have {entitlement.hours_remaining}hrs')
            result['can_proceed'] = False
        else:
            balance_percentage = (float(entitlement.hours_remaining) / float(hours_needed)) * 100
            if balance_percentage > 200:
                result['factors'].append(f'✅ Excellent leave balance: {entitlement.hours_remaining}hrs available')
            else:
                result['factors'].append(f'✅ Sufficient leave balance: {entitlement.hours_remaining}hrs available')
    
    except AnnualLeaveEntitlement.DoesNotExist:
        result['likelihood_score'] -= 60
        result['factors'].append('❌ No leave entitlement found for this period')
        result['can_proceed'] = False
    
    # Check 2: Existing approved leave on same dates
    conflicting_leave = LeaveRequest.objects.filter(
        user=user,
        status='APPROVED',
        start_date__lte=end_date,
        end_date__gte=start_date
    ).count()
    
    if conflicting_leave > 0:
        result['likelihood_score'] = 0
        result['approval_status'] = 'BLOCKED'
        result['factors'].append('❌ You already have approved leave during this period')
        result['can_proceed'] = False
        return result
    
    # Check 3: Staffing coverage during requested dates
    if user_unit:
        coverage_issues = []
        current = start_date
        
        while current <= end_date:
            # Get scheduled shifts for this date and unit
            total_shifts = Shift.objects.filter(
                unit=user_unit,
                date=current,
                status__in=['SCHEDULED', 'CONFIRMED']
            ).count()
            
            # Get other staff on leave this date
            staff_on_leave = LeaveRequest.objects.filter(
                user__profile__unit=user_unit,
                status='APPROVED',
                start_date__lte=current,
                end_date__gte=current
            ).count()
            
            # Get your shifts this date
            your_shifts = Shift.objects.filter(
                user=user,
                date=current
            ).count()
            
            # Calculate impact
            if your_shifts > 0:
                coverage_ratio = (total_shifts - your_shifts - staff_on_leave) / max(total_shifts, 1)
                
                if coverage_ratio < 0.5:  # Less than 50% coverage remaining
                    coverage_issues.append(current)
                    result['likelihood_score'] -= 5
                elif coverage_ratio < 0.7:  # 50-70% coverage
                    result['likelihood_score'] -= 2
            
            current += timedelta(days=1)
        
        if coverage_issues:
            if len(coverage_issues) > 3:
                result['factors'].append(f'⚠️ Low staffing coverage on {len(coverage_issues)} dates - may need manager approval')
                result['approval_status'] = 'MEDIUM'
            else:
                dates_str = ', '.join([d.strftime('%b %d') for d in coverage_issues[:3]])
                result['factors'].append(f'⚠️ Low coverage on: {dates_str}')
                result['likelihood_score'] -= 10
        else:
            result['factors'].append('✅ Good staffing coverage maintained')
    
    # Check 4: Peak periods / Blackout dates (December, summer holidays)
    peak_months = []
    current = start_date
    while current <= end_date:
        if current.month == 12:  # December
            peak_months.append('December')
        elif current.month in [7, 8]:  # Summer
            peak_months.append('Summer')
        current += timedelta(days=32)
        current = current.replace(day=1)
    
    if peak_months:
        result['likelihood_score'] -= 15
        result['factors'].append(f'⚠️ Peak period: {", ".join(set(peak_months))} - higher competition for leave')
    
    # Check 5: Notice period (requests within 7 days)
    days_notice = (start_date - timezone.now().date()).days
    
    if days_notice < 0:
        result['likelihood_score'] = 0
        result['factors'].append('❌ Cannot request leave for past dates')
        result['can_proceed'] = False
    elif days_notice < 7:
        result['likelihood_score'] -= 20
        result['factors'].append(f'⚠️ Short notice ({days_notice} days) - may require manager approval')
        result['approval_status'] = 'MEDIUM'
    elif days_notice > 60:
        result['factors'].append(f'✅ Good advance notice ({days_notice} days)')
    
    # Check 6: Recent leave usage pattern
    recent_leave = LeaveRequest.objects.filter(
        user=user,
        status='APPROVED',
        start_date__gte=timezone.now().date() - timedelta(days=90)
    ).count()
    
    if recent_leave > 3:
        result['likelihood_score'] -= 10
        result['factors'].append(f'⚠️ {recent_leave} leave requests approved in last 90 days')
    elif recent_leave == 0:
        result['factors'].append('✅ No recent leave taken - good availability record')
    
    # Determine final approval status
    if result['likelihood_score'] >= 85:
        result['approval_status'] = 'HIGH'
        result['recommendations'].append('✅ Strong chance of auto-approval - safe to proceed')
    elif result['likelihood_score'] >= 60:
        result['approval_status'] = 'MEDIUM'
        result['recommendations'].append('⚠️ Likely requires manager review - still worth requesting')
    elif result['likelihood_score'] >= 40:
        result['approval_status'] = 'LOW'
        result['recommendations'].append('⚠️ May be declined - consider alternative dates')
        result['can_proceed'] = True  # Still allow, but warn
    else:
        result['approval_status'] = 'VERY_LOW'
        result['recommendations'].append('❌ High risk of denial - strongly recommend choosing different dates')
    
    # Generate alternative date suggestions if score is low
    if result['likelihood_score'] < 70 and result['can_proceed']:
        alternatives = find_better_leave_dates(user, start_date, end_date)
        result['alternative_dates'] = alternatives
    
    return result


def find_better_leave_dates(user, original_start, original_end):
    """
    Suggest alternative dates with better approval likelihood.
    Looks at ±2 weeks from requested dates.
    """
    
    alternatives = []
    duration = (original_end - original_start).days + 1
    
    # Check dates 1-2 weeks before
    for offset in [-14, -7]:
        test_start = original_start + timedelta(days=offset)
        test_end = test_start + timedelta(days=duration - 1)
        
        if test_start >= timezone.now().date():
            prediction = predict_leave_approval_likelihood(user, test_start, test_end)
            if prediction['likelihood_score'] > 70:
                alternatives.append({
                    'start_date': test_start,
                    'end_date': test_end,
                    'score': prediction['likelihood_score'],
                    'description': f'{test_start.strftime("%b %d")} - {test_end.strftime("%b %d")} ({prediction["likelihood_score"]}% approval chance)'
                })
    
    # Check dates 1-2 weeks after
    for offset in [7, 14]:
        test_start = original_start + timedelta(days=offset)
        test_end = test_start + timedelta(days=duration - 1)
        
        prediction = predict_leave_approval_likelihood(user, test_start, test_end)
        if prediction['likelihood_score'] > 70:
            alternatives.append({
                'start_date': test_start,
                'end_date': test_end,
                'score': prediction['likelihood_score'],
                'description': f'{test_start.strftime("%b %d")} - {test_end.strftime("%b %d")} ({prediction["likelihood_score"]}% approval chance)'
            })
    
    # Return top 3 alternatives sorted by score
    alternatives.sort(key=lambda x: x['score'], reverse=True)
    return alternatives[:3]


def get_optimal_leave_period(user, month=None, duration_days=5):
    """
    Find the best period in a given month for taking leave based on actual staff absence data.
    
    Args:
        user: User object
        month: Target month (1-12), defaults to next month
        duration_days: How many days leave needed
    
    Returns:
        dict with best date range, staff off count, and availability status
    """
    from scheduling.models import LeaveRequest
    
    if month is None:
        target_date = timezone.now().date() + timedelta(days=30)
        month = target_date.month
        year = target_date.year
    else:
        year = timezone.now().year
        if month < timezone.now().month:
            year += 1
    
    from calendar import monthrange
    _, last_day = monthrange(year, month)
    
    all_options = []
    
    # Check every potential start date in the month
    for start_day in range(1, last_day - duration_days + 2):
        test_start = date(year, month, start_day)
        test_end = test_start + timedelta(days=duration_days - 1)
        
        # Skip past dates
        if test_start < timezone.now().date():
            continue
        
        # Count how many staff are off during this period
        overlapping_leave = LeaveRequest.objects.filter(
            status='approved',
            start_date__lte=test_end,
            end_date__gte=test_start
        ).exclude(user=user).count()
        
        # Calculate availability score (lower staff off = better)
        available = overlapping_leave < 3
        score = 100 - (overlapping_leave * 20)  # Each person off reduces score by 20
        if score < 0:
            score = 0
        
        all_options.append({
            'start_date': test_start,
            'end_date': test_end,
            'staff_off': overlapping_leave,
            'available': available,
            'score': score,
            'description': f'{test_start.strftime("%b %d")} - {test_end.strftime("%b %d")}'
        })
    
    # If no options (all dates in past), return None
    if not all_options:
        return None
    
    # Sort by fewest staff off, then earliest date
    all_options.sort(key=lambda x: (x['staff_off'], x['start_date']))
    best_option = all_options[0]
    
    # Add additional info
    best_option['total_options'] = len(all_options)
    best_option['available_periods'] = sum(1 for opt in all_options if opt['available'])
    
    return best_option
