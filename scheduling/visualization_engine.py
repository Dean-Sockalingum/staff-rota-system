"""
TASK 29: DATA VISUALIZATION ENGINE
Generate Chart.js configurations, heat maps, and data aggregations
"""

from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json


# ============================================================================
# CHART.JS CONFIGURATION GENERATORS
# ============================================================================

def generate_line_chart_config(data, labels, title, colors=None):
    """
    Generate Chart.js line chart configuration
    """
    if colors is None:
        colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe']
    
    datasets = []
    for idx, (label, values) in enumerate(data.items()):
        color = colors[idx % len(colors)]
        datasets.append({
            'label': label,
            'data': values,
            'borderColor': color,
            'backgroundColor': color + '20',
            'tension': 0.4,
            'fill': True,
        })
    
    config = {
        'type': 'line',
        'data': {
            'labels': labels,
            'datasets': datasets,
        },
        'options': {
            'responsive': True,
            'maintainAspectRatio': False,
            'plugins': {
                'title': {
                    'display': True,
                    'text': title,
                    'font': {'size': 16, 'weight': 'bold'}
                },
                'legend': {
                    'display': True,
                    'position': 'bottom',
                }
            },
            'scales': {
                'y': {
                    'beginAtZero': True,
                    'grid': {'color': '#e5e7eb'}
                },
                'x': {
                    'grid': {'display': False}
                }
            }
        }
    }
    
    return config


def generate_bar_chart_config(data, labels, title, colors=None):
    """
    Generate Chart.js bar chart configuration
    """
    if colors is None:
        colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe']
    
    datasets = []
    for idx, (label, values) in enumerate(data.items()):
        color = colors[idx % len(colors)]
        datasets.append({
            'label': label,
            'data': values,
            'backgroundColor': color,
            'borderColor': color,
            'borderWidth': 1,
        })
    
    config = {
        'type': 'bar',
        'data': {
            'labels': labels,
            'datasets': datasets,
        },
        'options': {
            'responsive': True,
            'maintainAspectRatio': False,
            'plugins': {
                'title': {
                    'display': True,
                    'text': title,
                    'font': {'size': 16, 'weight': 'bold'}
                },
                'legend': {
                    'display': True,
                    'position': 'bottom',
                }
            },
            'scales': {
                'y': {
                    'beginAtZero': True,
                    'grid': {'color': '#e5e7eb'}
                },
                'x': {
                    'grid': {'display': False}
                }
            }
        }
    }
    
    return config


def generate_pie_chart_config(data, labels, title):
    """
    Generate Chart.js pie chart configuration
    """
    colors = [
        '#667eea', '#764ba2', '#f093fb', '#4facfe',
        '#43e97b', '#fa709a', '#fee140', '#30cfd0'
    ]
    
    config = {
        'type': 'pie',
        'data': {
            'labels': labels,
            'datasets': [{
                'data': data,
                'backgroundColor': colors[:len(data)],
                'borderWidth': 2,
                'borderColor': '#ffffff'
            }]
        },
        'options': {
            'responsive': True,
            'maintainAspectRatio': False,
            'plugins': {
                'title': {
                    'display': True,
                    'text': title,
                    'font': {'size': 16, 'weight': 'bold'}
                },
                'legend': {
                    'display': True,
                    'position': 'right',
                }
            }
        }
    }
    
    return config


def generate_doughnut_chart_config(data, labels, title):
    """
    Generate Chart.js doughnut chart configuration
    """
    config = generate_pie_chart_config(data, labels, title)
    config['type'] = 'doughnut'
    config['options']['plugins']['legend']['position'] = 'bottom'
    config['options']['cutout'] = '70%'
    
    return config


def generate_gauge_config(value, max_value, title, thresholds=None):
    """
    Generate gauge chart configuration (using doughnut)
    """
    if thresholds is None:
        thresholds = {'critical': 30, 'warning': 60, 'good': 100}
    
    # Determine color based on value
    if value <= thresholds.get('critical', 30):
        color = '#ef4444'
    elif value <= thresholds.get('warning', 60):
        color = '#f59e0b'
    else:
        color = '#10b981'
    
    config = {
        'type': 'doughnut',
        'data': {
            'datasets': [{
                'data': [value, max_value - value],
                'backgroundColor': [color, '#e5e7eb'],
                'borderWidth': 0,
            }]
        },
        'options': {
            'responsive': True,
            'maintainAspectRatio': False,
            'circumference': 180,
            'rotation': -90,
            'cutout': '75%',
            'plugins': {
                'title': {
                    'display': True,
                    'text': title,
                    'font': {'size': 14, 'weight': 'bold'}
                },
                'legend': {'display': False},
                'tooltip': {'enabled': False}
            }
        }
    }
    
    return config


# ============================================================================
# DATA AGGREGATION FUNCTIONS
# ============================================================================

def get_staff_count_data(care_home=None, unit=None, days_back=30):
    """
    Get staff count trend over time
    """
    from .models import User
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days_back)
    
    # Get active staff
    staff_qs = User.objects.filter(is_active=True)
    if care_home:
        staff_qs = staff_qs.filter(care_home=care_home)
    if unit:
        staff_qs = staff_qs.filter(unit=unit)
    
    # Group by role
    by_role = staff_qs.values('role__name').annotate(count=Count('id'))
    
    labels = [item['role__name'] for item in by_role]
    data = [item['count'] for item in by_role]
    
    return {
        'labels': labels,
        'data': data,
        'total': sum(data)
    }


def get_shift_count_data(care_home=None, unit=None, days_back=30):
    """
    Get shift count trend over time
    """
    from .models import Shift
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days_back)
    
    shifts_qs = Shift.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    )
    
    if care_home:
        shifts_qs = shifts_qs.filter(care_home=care_home)
    if unit:
        shifts_qs = shifts_qs.filter(unit=unit)
    
    # Daily counts
    daily = {}
    current = start_date
    while current <= end_date:
        count = shifts_qs.filter(date=current).count()
        daily[current.strftime('%Y-%m-%d')] = count
        current += timedelta(days=1)
    
    return {
        'labels': list(daily.keys()),
        'data': list(daily.values()),
        'total': sum(daily.values())
    }


def get_occupancy_data(care_home=None, unit=None, days_back=30):
    """
    Get occupancy rate trend
    """
    from .models import Resident, Unit
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days_back)
    
    # Get capacity
    units_qs = Unit.objects.all()
    if care_home:
        units_qs = units_qs.filter(care_home=care_home)
    if unit:
        units_qs = units_qs.filter(id=unit.id)
    
    total_capacity = units_qs.aggregate(total=Sum('capacity'))['total'] or 0
    
    if total_capacity == 0:
        return {'labels': [], 'data': [], 'total': 0}
    
    # Daily occupancy
    daily = {}
    current = start_date
    while current <= end_date:
        occupied = Resident.objects.filter(
            Q(care_home=care_home) if care_home else Q(),
            Q(unit=unit) if unit else Q(),
            is_active=True,
            admission_date__lte=current
        ).count()
        
        rate = (occupied / total_capacity) * 100 if total_capacity > 0 else 0
        daily[current.strftime('%Y-%m-%d')] = round(rate, 1)
        current += timedelta(days=1)
    
    return {
        'labels': list(daily.keys()),
        'data': list(daily.values()),
        'capacity': total_capacity
    }


def get_training_status_data(care_home=None, unit=None):
    """
    Get training compliance status breakdown
    """
    from .models import User, TrainingRecord
    
    end_date = timezone.now().date()
    
    staff_qs = User.objects.filter(is_active=True)
    if care_home:
        staff_qs = staff_qs.filter(care_home=care_home)
    if unit:
        staff_qs = staff_qs.filter(unit=unit)
    
    total_staff = staff_qs.count()
    
    if total_staff == 0:
        return {'labels': [], 'data': []}
    
    compliant = 0
    expired = 0
    no_training = 0
    
    for staff in staff_qs:
        mandatory = TrainingRecord.objects.filter(
            staff=staff,
            course__is_mandatory=True
        )
        
        if not mandatory.exists():
            no_training += 1
        elif mandatory.filter(expiry_date__lt=end_date).exists():
            expired += 1
        else:
            compliant += 1
    
    return {
        'labels': ['Compliant', 'Expired', 'No Training'],
        'data': [compliant, expired, no_training]
    }


def get_agency_usage_data(care_home=None, unit=None, days_back=30):
    """
    Get agency vs permanent staff shift breakdown
    """
    from .models import Shift
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days_back)
    
    shifts_qs = Shift.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    )
    
    if care_home:
        shifts_qs = shifts_qs.filter(care_home=care_home)
    if unit:
        shifts_qs = shifts_qs.filter(unit=unit)
    
    total = shifts_qs.count()
    agency = shifts_qs.filter(is_agency=True).count()
    permanent = total - agency
    
    return {
        'labels': ['Permanent Staff', 'Agency Staff'],
        'data': [permanent, agency]
    }


def get_leave_requests_data(care_home=None, unit=None, days_back=30):
    """
    Get leave requests by status
    """
    from .models import LeaveRequest
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days_back)
    
    requests_qs = LeaveRequest.objects.filter(
        start_date__gte=start_date,
        start_date__lte=end_date
    )
    
    if care_home:
        requests_qs = requests_qs.filter(staff__care_home=care_home)
    if unit:
        requests_qs = requests_qs.filter(staff__unit=unit)
    
    by_status = requests_qs.values('status').annotate(count=Count('id'))
    
    labels = [item['status'] for item in by_status]
    data = [item['count'] for item in by_status]
    
    return {
        'labels': labels,
        'data': data
    }


# ============================================================================
# HEATMAP GENERATION
# ============================================================================

def generate_staffing_heatmap(care_home=None, unit=None, days_back=7):
    """
    Generate staffing heatmap data (day x shift type)
    """
    from .models import Shift
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days_back)
    
    shifts_qs = Shift.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    )
    
    if care_home:
        shifts_qs = shifts_qs.filter(care_home=care_home)
    if unit:
        shifts_qs = shifts_qs.filter(unit=unit)
    
    # Build matrix
    shift_types = ['EARLY', 'LATE', 'NIGHT', 'LONG_DAY']
    matrix = []
    labels_y = []
    
    current = start_date
    while current <= end_date:
        row = []
        for shift_type in shift_types:
            count = shifts_qs.filter(
                date=current,
                shift_type=shift_type
            ).count()
            row.append(count)
        
        matrix.append(row)
        labels_y.append(current.strftime('%a %d/%m'))
        current += timedelta(days=1)
    
    return {
        'matrix': matrix,
        'labels_x': ['Early', 'Late', 'Night', 'Long Day'],
        'labels_y': labels_y
    }


# ============================================================================
# WIDGET DATA FETCHERS
# ============================================================================

def fetch_widget_data(data_source, config, care_home=None, unit=None):
    """
    Fetch data for a widget based on data source and configuration
    
    Returns: dict with labels, data, and chart config
    """
    days_back = config.get('days_back', 30)
    
    if data_source == 'STAFF_COUNT':
        result = get_staff_count_data(care_home, unit, days_back)
        chart_config = generate_pie_chart_config(
            result['data'],
            result['labels'],
            'Staff Distribution by Role'
        )
        
    elif data_source == 'SHIFT_COUNT':
        result = get_shift_count_data(care_home, unit, days_back)
        data_dict = {'Shifts': result['data']}
        chart_config = generate_line_chart_config(
            data_dict,
            result['labels'],
            'Daily Shift Count'
        )
        
    elif data_source == 'OCCUPANCY':
        result = get_occupancy_data(care_home, unit, days_back)
        data_dict = {'Occupancy %': result['data']}
        chart_config = generate_line_chart_config(
            data_dict,
            result['labels'],
            'Occupancy Rate Trend'
        )
        
    elif data_source == 'TRAINING_STATUS':
        result = get_training_status_data(care_home, unit)
        chart_config = generate_doughnut_chart_config(
            result['data'],
            result['labels'],
            'Training Compliance Status'
        )
        
    elif data_source == 'AGENCY_USAGE':
        result = get_agency_usage_data(care_home, unit, days_back)
        chart_config = generate_pie_chart_config(
            result['data'],
            result['labels'],
            'Agency vs Permanent Staff'
        )
        
    elif data_source == 'LEAVE_REQUESTS':
        result = get_leave_requests_data(care_home, unit, days_back)
        chart_config = generate_bar_chart_config(
            {'Requests': result['data']},
            result['labels'],
            'Leave Requests by Status'
        )
        
    else:
        # Default empty
        result = {'labels': [], 'data': []}
        chart_config = {}
    
    return {
        'data': result,
        'chart_config': chart_config
    }


def generate_stat_card_data(data_source, config, care_home=None, unit=None):
    """
    Generate data for stat card widget
    """
    from .models import User, Shift, Resident, LeaveRequest
    
    if data_source == 'STAFF_COUNT':
        qs = User.objects.filter(is_active=True)
        if care_home:
            qs = qs.filter(care_home=care_home)
        if unit:
            qs = qs.filter(unit=unit)
        
        count = qs.count()
        return {
            'value': count,
            'label': 'Active Staff',
            'icon': 'users',
            'color': '#667eea'
        }
    
    elif data_source == 'SHIFT_COUNT':
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=7)
        
        qs = Shift.objects.filter(date__gte=start_date, date__lte=end_date)
        if care_home:
            qs = qs.filter(care_home=care_home)
        if unit:
            qs = qs.filter(unit=unit)
        
        count = qs.count()
        return {
            'value': count,
            'label': 'Shifts This Week',
            'icon': 'calendar',
            'color': '#764ba2'
        }
    
    elif data_source == 'OCCUPANCY':
        from .models import Unit
        
        units_qs = Unit.objects.all()
        if care_home:
            units_qs = units_qs.filter(care_home=care_home)
        if unit:
            units_qs = units_qs.filter(id=unit.id)
        
        capacity = units_qs.aggregate(total=Sum('capacity'))['total'] or 0
        
        occupied = Resident.objects.filter(
            Q(care_home=care_home) if care_home else Q(),
            Q(unit=unit) if unit else Q(),
            is_active=True
        ).count()
        
        rate = (occupied / capacity * 100) if capacity > 0 else 0
        
        return {
            'value': f"{rate:.1f}%",
            'label': 'Occupancy Rate',
            'icon': 'home',
            'color': '#10b981'
        }
    
    return {
        'value': 0,
        'label': 'N/A',
        'icon': 'info',
        'color': '#6b7280'
    }
