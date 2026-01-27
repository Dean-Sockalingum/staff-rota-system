"""
Shift Pattern Analysis Service

Analyzes shift patterns, identifies coverage gaps, and provides
staffing optimization recommendations.
"""

from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from collections import defaultdict
import statistics


def analyze_shift_patterns(care_home=None, unit=None, start_date=None, end_date=None):
    """
    Analyze shift patterns to identify peaks, troughs, and coverage issues
    
    Returns: Dictionary with pattern analysis results
    """
    from .models import Shift
    
    # Default to last 30 days
    if not end_date:
        end_date = timezone.now().date()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Filter shifts
    shifts = Shift.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    )
    
    if care_home:
        shifts = shifts.filter(care_home=care_home)
    if unit:
        shifts = shifts.filter(unit=unit)
    
    # Group by day of week and shift type
    patterns_by_day = defaultdict(lambda: defaultdict(list))
    patterns_by_shift_type = defaultdict(list)
    
    for shift in shifts:
        day_of_week = shift.date.weekday()
        shift_type = shift.shift_type
        
        # Count staff on this shift
        staff_count = shift.staff_members.count()
        
        patterns_by_day[day_of_week][shift_type].append({
            'date': shift.date,
            'staff_count': staff_count,
            'required': getattr(shift.unit, 'min_staff_required', 5) if shift.unit else 5,
        })
        
        patterns_by_shift_type[shift_type].append({
            'date': shift.date,
            'day_of_week': day_of_week,
            'staff_count': staff_count,
        })
    
    # Analyze patterns
    day_patterns = []
    for day, shift_types in patterns_by_day.items():
        for shift_type, shifts_data in shift_types.items():
            avg_staff = statistics.mean([s['staff_count'] for s in shifts_data])
            avg_required = statistics.mean([s['required'] for s in shifts_data])
            coverage_pct = (avg_staff / avg_required * 100) if avg_required > 0 else 0
            
            # Classify pattern
            if coverage_pct < 80:
                pattern_type = 'UNDERSTAFFED'
            elif coverage_pct > 120:
                pattern_type = 'OVERSTAFFED'
            elif avg_staff >= avg_required:
                pattern_type = 'BALANCED'
            else:
                pattern_type = 'TROUGH'
            
            day_patterns.append({
                'day_of_week': day,
                'shift_type': shift_type,
                'pattern_type': pattern_type,
                'average_staff': avg_staff,
                'required_staff': avg_required,
                'coverage_percentage': coverage_pct,
                'frequency': len(shifts_data),
            })
    
    # Identify peak and trough periods
    shift_type_patterns = []
    for shift_type, shifts_data in patterns_by_shift_type.items():
        staff_counts = [s['staff_count'] for s in shifts_data]
        avg_staff = statistics.mean(staff_counts)
        max_staff = max(staff_counts)
        min_staff = min(staff_counts)
        std_dev = statistics.stdev(staff_counts) if len(staff_counts) > 1 else 0
        
        # Identify peak days (above average + 0.5 std dev)
        peak_threshold = avg_staff + (0.5 * std_dev)
        trough_threshold = avg_staff - (0.5 * std_dev)
        
        peak_days = [
            s['day_of_week'] for s in shifts_data 
            if s['staff_count'] >= peak_threshold
        ]
        trough_days = [
            s['day_of_week'] for s in shifts_data 
            if s['staff_count'] <= trough_threshold
        ]
        
        # Count occurrences
        from collections import Counter
        peak_day_counts = Counter(peak_days)
        trough_day_counts = Counter(trough_days)
        
        shift_type_patterns.append({
            'shift_type': shift_type,
            'average_staff': avg_staff,
            'max_staff': max_staff,
            'min_staff': min_staff,
            'std_deviation': std_dev,
            'peak_days': dict(peak_day_counts.most_common(3)),
            'trough_days': dict(trough_day_counts.most_common(3)),
        })
    
    return {
        'day_patterns': day_patterns,
        'shift_type_patterns': shift_type_patterns,
        'start_date': start_date,
        'end_date': end_date,
        'total_shifts_analyzed': shifts.count(),
    }


def detect_coverage_gaps(care_home=None, unit=None, start_date=None, end_date=None, threshold=0.8):
    """
    Detect coverage gaps where staffing falls below required levels
    
    Args:
        threshold: Coverage threshold (0.8 = 80% of required staff)
    
    Returns: List of coverage gap dictionaries
    """
    from .models import Shift
    
    # Default to next 14 days
    if not start_date:
        start_date = timezone.now().date()
    if not end_date:
        end_date = start_date + timedelta(days=14)
    
    # Filter shifts
    shifts = Shift.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    )
    
    if care_home:
        shifts = shifts.filter(care_home=care_home)
    if unit:
        shifts = shifts.filter(unit=unit)
    
    gaps = []
    
    for shift in shifts:
        actual_staff = shift.staff_members.count()
        required_staff = getattr(shift.unit, 'min_staff_required', 5) if shift.unit else 5
        
        coverage = actual_staff / required_staff if required_staff > 0 else 1
        
        if coverage < threshold:
            gap_size = required_staff - actual_staff
            gap_percentage = ((required_staff - actual_staff) / required_staff * 100) if required_staff > 0 else 0
            
            # Calculate severity
            if coverage < 0.5:
                severity = 'CRITICAL'
                impact_score = 100
            elif coverage < 0.6:
                severity = 'HIGH'
                impact_score = 80
            elif coverage < 0.7:
                severity = 'MEDIUM'
                impact_score = 60
            else:
                severity = 'LOW'
                impact_score = 40
            
            gaps.append({
                'gap_date': shift.date,
                'shift_type': shift.shift_type,
                'shift_id': shift.id,
                'required_staff': required_staff,
                'actual_staff': actual_staff,
                'gap_size': gap_size,
                'gap_percentage': gap_percentage,
                'severity': severity,
                'impact_score': impact_score,
                'care_home_id': shift.care_home_id,
                'unit_id': shift.unit_id,
            })
    
    # Sort by severity and gap size
    severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    gaps.sort(key=lambda x: (severity_order[x['severity']], -x['gap_size']))
    
    return gaps


def analyze_workload_distribution(care_home=None, unit=None, start_date=None, end_date=None):
    """
    Analyze workload distribution across staff members
    
    Returns: Dictionary with distribution analysis
    """
    from .models import Shift, StaffProfile
    
    # Default to last 30 days
    if not end_date:
        end_date = timezone.now().date()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Get all shifts in period
    shifts = Shift.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    )
    
    if care_home:
        shifts = shifts.filter(care_home=care_home)
    if unit:
        shifts = shifts.filter(unit=unit)
    
    # Count shifts per staff member
    staff_shift_counts = defaultdict(int)
    staff_shift_types = defaultdict(lambda: defaultdict(int))
    
    for shift in shifts:
        for staff in shift.staff_members.all():
            staff_shift_counts[staff.id] += 1
            staff_shift_types[staff.id][shift.shift_type] += 1
    
    if not staff_shift_counts:
        return {
            'error': 'No shifts found for analysis',
            'distribution_data': {},
        }
    
    # Calculate distribution metrics
    shift_counts = list(staff_shift_counts.values())
    avg_shifts = statistics.mean(shift_counts)
    max_shifts = max(shift_counts)
    min_shifts = min(shift_counts)
    std_dev = statistics.stdev(shift_counts) if len(shift_counts) > 1 else 0
    
    # Calculate Gini coefficient (measure of inequality)
    gini = calculate_gini_coefficient(shift_counts)
    
    # Calculate balance score (100 - normalized std deviation)
    normalized_std_dev = (std_dev / avg_shifts * 100) if avg_shifts > 0 else 0
    balance_score = max(0, 100 - normalized_std_dev)
    
    # Determine if balanced (Gini < 0.3 and std dev < 30% of mean)
    is_balanced = gini < 0.3 and normalized_std_dev < 30
    unfairness_score = gini * 100
    
    # Analyze shift type distribution
    shift_type_totals = defaultdict(int)
    for staff_id, types in staff_shift_types.items():
        for shift_type, count in types.items():
            shift_type_totals[shift_type] += count
    
    total_shifts = sum(shift_type_totals.values())
    shift_type_percentages = {
        shift_type: (count / total_shifts * 100) if total_shifts > 0 else 0
        for shift_type, count in shift_type_totals.items()
    }
    
    # Build distribution data
    distribution_data = {
        'staff_counts': dict(staff_shift_counts),
        'staff_shift_types': {k: dict(v) for k, v in staff_shift_types.items()},
        'shift_type_totals': dict(shift_type_totals),
        'shift_type_percentages': shift_type_percentages,
    }
    
    # Generate recommendations
    recommendations = []
    if not is_balanced:
        recommendations.append(f"Workload distribution is unbalanced (Gini: {gini:.3f})")
        recommendations.append(f"Standard deviation is {std_dev:.1f} shifts ({normalized_std_dev:.1f}% of mean)")
        
        # Identify overworked and underworked staff
        overworked_threshold = avg_shifts + std_dev
        underworked_threshold = avg_shifts - std_dev
        
        overworked = [sid for sid, count in staff_shift_counts.items() if count > overworked_threshold]
        underworked = [sid for sid, count in staff_shift_counts.items() if count < underworked_threshold]
        
        if overworked:
            recommendations.append(f"{len(overworked)} staff members are working above average + 1 std dev")
        if underworked:
            recommendations.append(f"{len(underworked)} staff members are working below average - 1 std dev")
        
        recommendations.append("Consider redistributing shifts more evenly")
    else:
        recommendations.append("Workload is well-balanced across staff")
    
    # Check shift type balance
    for shift_type, percentage in shift_type_percentages.items():
        if percentage > 50:
            recommendations.append(f"{shift_type} shifts account for {percentage:.1f}% of total - consider diversifying")
    
    return {
        'distribution_data': distribution_data,
        'balance_score': balance_score,
        'gini_coefficient': gini,
        'average_shifts_per_staff': avg_shifts,
        'max_shifts_per_staff': max_shifts,
        'min_shifts_per_staff': min_shifts,
        'standard_deviation': std_dev,
        'shift_type_balance': shift_type_percentages,
        'is_balanced': is_balanced,
        'unfairness_score': unfairness_score,
        'recommendations': '\n'.join(recommendations),
        'start_date': start_date,
        'end_date': end_date,
    }


def calculate_gini_coefficient(values):
    """
    Calculate Gini coefficient for inequality measurement
    
    Gini coefficient ranges from 0 (perfect equality) to 1 (maximum inequality)
    """
    if not values or len(values) == 0:
        return 0
    
    # Sort values
    sorted_values = sorted(values)
    n = len(sorted_values)
    
    # Calculate Gini
    cumsum = 0
    for i, value in enumerate(sorted_values):
        cumsum += (i + 1) * value
    
    sum_values = sum(sorted_values)
    
    if sum_values == 0:
        return 0
    
    gini = (2 * cumsum) / (n * sum_values) - (n + 1) / n
    
    return gini


def generate_optimization_recommendations(care_home=None, unit=None):
    """
    Generate staffing optimization recommendations based on pattern analysis
    
    Returns: List of recommendation dictionaries
    """
    from .models import Shift
    from datetime import date
    
    recommendations = []
    
    # Analyze patterns
    patterns = analyze_shift_patterns(care_home, unit)
    
    # Check for understaffed patterns
    understaffed = [p for p in patterns['day_patterns'] if p['pattern_type'] == 'UNDERSTAFFED']
    if understaffed:
        for pattern in understaffed[:5]:  # Top 5
            day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][pattern['day_of_week']]
            recommendations.append({
                'type': 'INCREASE_STAFFING',
                'priority': 'HIGH',
                'title': f'Increase staffing on {day_name} {pattern["shift_type"]} shifts',
                'description': f'Currently averaging {pattern["average_staff"]:.1f} staff but need {pattern["required_staff"]:.1f}',
                'impact': f'Coverage at {pattern["coverage_percentage"]:.1f}%',
                'action': f'Add {int(pattern["required_staff"] - pattern["average_staff"])} staff members',
            })
    
    # Check for overstaffed patterns
    overstaffed = [p for p in patterns['day_patterns'] if p['pattern_type'] == 'OVERSTAFFED']
    if overstaffed:
        for pattern in overstaffed[:3]:  # Top 3
            day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][pattern['day_of_week']]
            recommendations.append({
                'type': 'REDUCE_STAFFING',
                'priority': 'MEDIUM',
                'title': f'Optimize staffing on {day_name} {pattern["shift_type"]} shifts',
                'description': f'Currently averaging {pattern["average_staff"]:.1f} staff but only need {pattern["required_staff"]:.1f}',
                'impact': f'Coverage at {pattern["coverage_percentage"]:.1f}% (overstaffed)',
                'action': f'Reduce by {int(pattern["average_staff"] - pattern["required_staff"])} staff members or reallocate',
            })
    
    # Detect upcoming coverage gaps
    gaps = detect_coverage_gaps(care_home, unit)
    critical_gaps = [g for g in gaps if g['severity'] in ['CRITICAL', 'HIGH']]
    
    if critical_gaps:
        for gap in critical_gaps[:5]:  # Top 5
            recommendations.append({
                'type': 'FILL_GAP',
                'priority': gap['severity'],
                'title': f'Fill coverage gap on {gap["gap_date"]} ({gap["shift_type"]})',
                'description': f'{gap["gap_size"]} staff members short',
                'impact': f'Only {gap["actual_staff"]} of {gap["required_staff"]} staff scheduled',
                'action': f'Recruit or reassign {gap["gap_size"]} staff members',
            })
    
    # Analyze workload distribution
    workload = analyze_workload_distribution(care_home, unit)
    
    if 'error' not in workload and not workload['is_balanced']:
        recommendations.append({
            'type': 'BALANCE_WORKLOAD',
            'priority': 'MEDIUM',
            'title': 'Rebalance staff workload distribution',
            'description': f'Current Gini coefficient: {workload["gini_coefficient"]:.3f} (0 = perfect balance)',
            'impact': f'Unfairness score: {workload["unfairness_score"]:.1f}/100',
            'action': workload['recommendations'],
        })
    
    # Sort by priority
    priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    recommendations.sort(key=lambda x: priority_order[x['priority']])
    
    return recommendations


def get_shift_pattern_heat_map(care_home=None, unit=None, days_back=30):
    """
    Generate heat map data for shift patterns
    
    Returns: Dictionary with heat map data
    """
    from .models import Shift
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days_back)
    
    shifts = Shift.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    )
    
    if care_home:
        shifts = shifts.filter(care_home=care_home)
    if unit:
        shifts = shifts.filter(unit=unit)
    
    # Initialize heat map data structure
    # day_of_week x shift_type matrix
    heat_map = defaultdict(lambda: defaultdict(list))
    
    for shift in shifts:
        day_of_week = shift.date.weekday()
        shift_type = shift.shift_type
        staff_count = shift.staff_members.count()
        
        heat_map[day_of_week][shift_type].append(staff_count)
    
    # Calculate averages
    heat_map_averages = {}
    for day in range(7):
        heat_map_averages[day] = {}
        for shift_type in ['EARLY', 'LATE', 'NIGHT', 'LONG_DAY']:
            if heat_map[day][shift_type]:
                avg = statistics.mean(heat_map[day][shift_type])
                heat_map_averages[day][shift_type] = round(avg, 1)
            else:
                heat_map_averages[day][shift_type] = 0
    
    return {
        'heat_map_data': heat_map_averages,
        'day_labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        'shift_type_labels': ['EARLY', 'LATE', 'NIGHT', 'LONG_DAY'],
    }
