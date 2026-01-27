"""
TASK 28: KPI TRACKING SYSTEM
Calculate KPIs, track performance vs targets, and generate alerts
"""

from django.db.models import Count, Sum, Avg, F, Q, ExpressionWrapper, DecimalField
from django.utils import timezone
from datetime import datetime, timedelta, date
from decimal import Decimal


# ============================================================================
# PREDEFINED KPI CALCULATORS
# Each function calculates a specific KPI and returns the measurement value
# ============================================================================

def calculate_staff_turnover_rate(care_home=None, unit=None, start_date=None, end_date=None):
    """
    Calculate staff turnover rate
    Formula: (Number of staff who left / Average total staff) * 100
    """
    from .models import User
    
    if not start_date or not end_date:
        # Default to last month
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
    
    # Build queryset
    qs = User.objects.all()
    if care_home:
        qs = qs.filter(care_home=care_home)
    if unit:
        qs = qs.filter(unit=unit)
    
    # Count staff who left during period (became inactive)
    staff_left = qs.filter(
        is_active=False,
        updated_at__gte=start_date,
        updated_at__lte=end_date
    ).count()
    
    # Get average total staff (start + end / 2)
    staff_at_start = qs.filter(
        Q(is_active=True) | Q(updated_at__gte=start_date),
        created_at__lte=start_date
    ).count()
    
    staff_at_end = qs.filter(is_active=True).count()
    
    average_staff = (staff_at_start + staff_at_end) / 2 if (staff_at_start + staff_at_end) > 0 else 0
    
    if average_staff == 0:
        return 0, {'staff_left': staff_left, 'average_staff': 0}
    
    turnover_rate = (staff_left / average_staff) * 100
    
    details = {
        'staff_left': staff_left,
        'staff_at_start': staff_at_start,
        'staff_at_end': staff_at_end,
        'average_staff': average_staff
    }
    
    return round(turnover_rate, 2), details


def calculate_occupancy_rate(care_home=None, unit=None, start_date=None, end_date=None):
    """
    Calculate occupancy rate
    Formula: (Occupied beds / Total beds) * 100
    """
    from .models import Resident, Unit
    
    if not start_date or not end_date:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
    
    # Get units
    units_qs = Unit.objects.all()
    if care_home:
        units_qs = units_qs.filter(care_home=care_home)
    if unit:
        units_qs = units_qs.filter(id=unit.id)
    
    total_capacity = units_qs.aggregate(total=Sum('capacity'))['total'] or 0
    
    if total_capacity == 0:
        return 0, {'occupied': 0, 'capacity': 0}
    
    # Count active residents during period
    occupied = Resident.objects.filter(
        Q(care_home=care_home) if care_home else Q(),
        Q(unit=unit) if unit else Q(),
        is_active=True,
        admission_date__lte=end_date
    ).count()
    
    occupancy_rate = (occupied / total_capacity) * 100
    
    details = {
        'occupied_beds': occupied,
        'total_capacity': total_capacity,
    }
    
    return round(occupancy_rate, 2), details


def calculate_agency_usage_percentage(care_home=None, unit=None, start_date=None, end_date=None):
    """
    Calculate percentage of shifts filled by agency staff
    Formula: (Agency shifts / Total shifts) * 100
    """
    from .models import Shift
    
    if not start_date or not end_date:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
    
    # Build queryset
    qs = Shift.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    )
    
    if care_home:
        qs = qs.filter(care_home=care_home)
    if unit:
        qs = qs.filter(unit=unit)
    
    total_shifts = qs.count()
    
    if total_shifts == 0:
        return 0, {'agency_shifts': 0, 'total_shifts': 0}
    
    agency_shifts = qs.filter(is_agency=True).count()
    
    agency_percentage = (agency_shifts / total_shifts) * 100
    
    details = {
        'agency_shifts': agency_shifts,
        'total_shifts': total_shifts,
    }
    
    return round(agency_percentage, 2), details


def calculate_compliance_rate(care_home=None, unit=None, start_date=None, end_date=None):
    """
    Calculate training compliance rate
    Formula: (Staff with current training / Total staff) * 100
    """
    from .models import User, TrainingRecord
    
    if not end_date:
        end_date = timezone.now().date()
    
    # Get active staff
    staff_qs = User.objects.filter(is_active=True)
    
    if care_home:
        staff_qs = staff_qs.filter(care_home=care_home)
    if unit:
        staff_qs = staff_qs.filter(unit=unit)
    
    total_staff = staff_qs.count()
    
    if total_staff == 0:
        return 0, {'compliant_staff': 0, 'total_staff': 0}
    
    # Count staff with all mandatory training up to date
    compliant_staff = 0
    
    for staff in staff_qs:
        # Check if all their mandatory training is current
        mandatory_training = TrainingRecord.objects.filter(
            staff=staff,
            course__is_mandatory=True
        )
        
        # Check if any are expired
        expired = mandatory_training.filter(
            expiry_date__lt=end_date
        ).exists()
        
        if not expired and mandatory_training.exists():
            compliant_staff += 1
    
    compliance_rate = (compliant_staff / total_staff) * 100
    
    details = {
        'compliant_staff': compliant_staff,
        'total_staff': total_staff,
    }
    
    return round(compliance_rate, 2), details


def calculate_average_shift_fill_time(care_home=None, unit=None, start_date=None, end_date=None):
    """
    Calculate average time to fill vacant shifts (in hours)
    """
    from .models import Shift
    
    if not start_date or not end_date:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
    
    # Get shifts that were created as vacant and then filled
    qs = Shift.objects.filter(
        date__gte=start_date,
        date__lte=end_date,
        created_at__isnull=False,
        updated_at__isnull=False
    )
    
    if care_home:
        qs = qs.filter(care_home=care_home)
    if unit:
        qs = qs.filter(unit=unit)
    
    # Calculate time differences
    fill_times = []
    for shift in qs:
        if shift.staff:  # Shift is filled
            time_diff = (shift.updated_at - shift.created_at).total_seconds() / 3600  # hours
            fill_times.append(time_diff)
    
    if not fill_times:
        return 0, {'shifts_analyzed': 0, 'average_hours': 0}
    
    average_hours = sum(fill_times) / len(fill_times)
    
    details = {
        'shifts_analyzed': len(fill_times),
        'average_hours': round(average_hours, 2),
        'fastest_fill': round(min(fill_times), 2),
        'slowest_fill': round(max(fill_times), 2),
    }
    
    return round(average_hours, 2), details


def calculate_overtime_percentage(care_home=None, unit=None, start_date=None, end_date=None):
    """
    Calculate percentage of shifts that are overtime
    Formula: (Overtime shifts / Total shifts) * 100
    """
    from .models import Shift
    
    if not start_date or not end_date:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
    
    qs = Shift.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    )
    
    if care_home:
        qs = qs.filter(care_home=care_home)
    if unit:
        qs = qs.filter(unit=unit)
    
    total_shifts = qs.count()
    
    if total_shifts == 0:
        return 0, {'overtime_shifts': 0, 'total_shifts': 0}
    
    overtime_shifts = qs.filter(shift_classification='OVERTIME').count()
    
    overtime_percentage = (overtime_shifts / total_shifts) * 100
    
    details = {
        'overtime_shifts': overtime_shifts,
        'total_shifts': total_shifts,
    }
    
    return round(overtime_percentage, 2), details


# ============================================================================
# KPI MEASUREMENT ENGINE
# ============================================================================

def calculate_kpi_value(kpi_definition, start_date=None, end_date=None):
    """
    Calculate KPI value based on KPI definition
    
    Returns: (value, calculation_details)
    """
    kpi_name = kpi_definition.name.lower()
    
    # Map KPI names to calculation functions
    calculators = {
        'staff turnover rate': calculate_staff_turnover_rate,
        'occupancy rate': calculate_occupancy_rate,
        'agency usage': calculate_agency_usage_percentage,
        'compliance rate': calculate_compliance_rate,
        'shift fill time': calculate_average_shift_fill_time,
        'overtime percentage': calculate_overtime_percentage,
    }
    
    # Find matching calculator
    calculator = None
    for key, func in calculators.items():
        if key in kpi_name:
            calculator = func
            break
    
    if not calculator:
        # Default calculation - return 0
        return 0, {'error': 'No calculator found for this KPI'}
    
    # Execute calculation
    value, details = calculator(
        care_home=kpi_definition.care_home,
        unit=kpi_definition.unit,
        start_date=start_date,
        end_date=end_date
    )
    
    return value, details


def assess_kpi_performance(kpi_definition, measured_value, target_value):
    """
    Assess KPI performance vs target and return status
    
    Returns: (status, variance, variance_percentage, alert_message)
    """
    if target_value is None:
        return 'GOOD', None, None, None
    
    variance = float(measured_value) - float(target_value)
    variance_percentage = (variance / float(target_value)) * 100 if target_value != 0 else 0
    
    # Determine status based on thresholds and direction
    higher_is_better = kpi_definition.higher_is_better
    critical_threshold = kpi_definition.critical_threshold
    warning_threshold = kpi_definition.warning_threshold
    
    status = 'GOOD'
    alert_message = None
    
    if higher_is_better:
        # Higher values are better (e.g., compliance rate)
        if critical_threshold and measured_value < critical_threshold:
            status = 'CRITICAL'
            alert_message = f"{kpi_definition.name} is critically low: {measured_value} (threshold: {critical_threshold})"
        elif warning_threshold and measured_value < warning_threshold:
            status = 'WARNING'
            alert_message = f"{kpi_definition.name} is below warning threshold: {measured_value} (threshold: {warning_threshold})"
        elif measured_value >= target_value:
            status = 'EXCELLENT'
    else:
        # Lower values are better (e.g., turnover rate)
        if critical_threshold and measured_value > critical_threshold:
            status = 'CRITICAL'
            alert_message = f"{kpi_definition.name} is critically high: {measured_value} (threshold: {critical_threshold})"
        elif warning_threshold and measured_value > warning_threshold:
            status = 'WARNING'
            alert_message = f"{kpi_definition.name} is above warning threshold: {measured_value} (threshold: {warning_threshold})"
        elif measured_value <= target_value:
            status = 'EXCELLENT'
    
    return status, variance, variance_percentage, alert_message


def record_kpi_measurement(kpi_definition, measurement_date=None):
    """
    Calculate and record a KPI measurement
    
    Returns: KPIMeasurement instance
    """
    from .models import KPIMeasurement, KPITarget
    
    if measurement_date is None:
        measurement_date = timezone.now().date()
    
    # Determine period based on frequency
    frequency = kpi_definition.measurement_frequency
    
    if frequency == 'DAILY':
        period_start = measurement_date
        period_end = measurement_date
    elif frequency == 'WEEKLY':
        # Last 7 days
        period_end = measurement_date
        period_start = measurement_date - timedelta(days=7)
    elif frequency == 'MONTHLY':
        # Last 30 days
        period_end = measurement_date
        period_start = measurement_date - timedelta(days=30)
    elif frequency == 'QUARTERLY':
        # Last 90 days
        period_end = measurement_date
        period_start = measurement_date - timedelta(days=90)
    else:
        period_end = measurement_date
        period_start = measurement_date - timedelta(days=30)
    
    # Calculate KPI value
    measured_value, calculation_details = calculate_kpi_value(
        kpi_definition,
        start_date=period_start,
        end_date=period_end
    )
    
    # Get current target
    year = measurement_date.year
    month = measurement_date.month
    quarter = (month - 1) // 3 + 1
    
    # Try to find target (most specific first)
    target = KPITarget.objects.filter(
        kpi=kpi_definition,
        year=year,
        month=month
    ).first()
    
    if not target:
        target = KPITarget.objects.filter(
            kpi=kpi_definition,
            year=year,
            quarter=quarter
        ).first()
    
    if not target:
        target = KPITarget.objects.filter(
            kpi=kpi_definition,
            year=year,
            month__isnull=True,
            quarter__isnull=True
        ).first()
    
    target_value = target.target_value if target else None
    
    # Assess performance
    status, variance, variance_pct, alert_message = assess_kpi_performance(
        kpi_definition,
        measured_value,
        target_value
    )
    
    # Create or update measurement
    measurement, created = KPIMeasurement.objects.update_or_create(
        kpi=kpi_definition,
        measurement_date=measurement_date,
        defaults={
            'period_start': period_start,
            'period_end': period_end,
            'measured_value': measured_value,
            'calculation_details': calculation_details,
            'target_value': target_value,
            'variance': variance,
            'variance_percentage': variance_pct,
            'status': status,
            'alert_generated': alert_message is not None,
            'alert_message': alert_message,
            'is_automated': True,
        }
    )
    
    return measurement


def calculate_all_kpis(care_home=None, measurement_date=None):
    """
    Calculate all active KPIs for a care home
    
    Returns: List of KPIMeasurement instances
    """
    from .models import KPIDefinition
    
    if measurement_date is None:
        measurement_date = timezone.now().date()
    
    # Get active KPIs
    kpis = KPIDefinition.objects.filter(is_active=True)
    
    if care_home:
        kpis = kpis.filter(Q(care_home=care_home) | Q(care_home__isnull=True))
    
    measurements = []
    
    for kpi in kpis:
        try:
            measurement = record_kpi_measurement(kpi, measurement_date)
            measurements.append(measurement)
        except Exception as e:
            # Log error but continue with other KPIs
            print(f"Error calculating KPI {kpi.name}: {str(e)}")
            continue
    
    return measurements


def get_kpi_trend(kpi_definition, days_back=30):
    """
    Get historical trend for a KPI
    
    Returns: List of measurements ordered by date
    """
    from .models import KPIMeasurement
    
    cutoff_date = timezone.now().date() - timedelta(days=days_back)
    
    measurements = KPIMeasurement.objects.filter(
        kpi=kpi_definition,
        measurement_date__gte=cutoff_date
    ).order_by('measurement_date')
    
    return list(measurements)


def get_kpi_summary(care_home=None, period='month'):
    """
    Get summary of all KPI statuses
    
    Returns: Dictionary with KPI summaries
    """
    from .models import KPIDefinition, KPIMeasurement
    
    # Determine date range
    end_date = timezone.now().date()
    if period == 'week':
        start_date = end_date - timedelta(days=7)
    elif period == 'month':
        start_date = end_date - timedelta(days=30)
    elif period == 'quarter':
        start_date = end_date - timedelta(days=90)
    else:
        start_date = end_date - timedelta(days=30)
    
    # Get KPIs
    kpis = KPIDefinition.objects.filter(is_active=True)
    if care_home:
        kpis = kpis.filter(Q(care_home=care_home) | Q(care_home__isnull=True))
    
    summary = {
        'total_kpis': kpis.count(),
        'excellent': 0,
        'good': 0,
        'warning': 0,
        'critical': 0,
        'by_category': {},
        'recent_alerts': [],
    }
    
    for kpi in kpis:
        # Get most recent measurement
        latest = KPIMeasurement.objects.filter(
            kpi=kpi,
            measurement_date__gte=start_date
        ).order_by('-measurement_date').first()
        
        if latest:
            # Count by status
            if latest.status == 'EXCELLENT':
                summary['excellent'] += 1
            elif latest.status == 'GOOD':
                summary['good'] += 1
            elif latest.status == 'WARNING':
                summary['warning'] += 1
            elif latest.status == 'CRITICAL':
                summary['critical'] += 1
            
            # Count by category
            category = kpi.category
            if category not in summary['by_category']:
                summary['by_category'][category] = {'excellent': 0, 'good': 0, 'warning': 0, 'critical': 0}
            
            if latest.status in summary['by_category'][category]:
                summary['by_category'][category][latest.status.lower()] += 1
            
            # Collect alerts
            if latest.alert_generated:
                summary['recent_alerts'].append({
                    'kpi': kpi.name,
                    'message': latest.alert_message,
                    'date': latest.measurement_date,
                    'severity': latest.status,
                })
    
    # Sort alerts by severity
    severity_order = {'CRITICAL': 0, 'WARNING': 1}
    summary['recent_alerts'].sort(key=lambda x: severity_order.get(x['severity'], 2))
    
    return summary
