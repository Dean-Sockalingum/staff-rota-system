"""
Analytics Dashboard Views
=========================

Views for the advanced analytics dashboard.

Created: 30 December 2025
Task 39: Advanced Analytics Dashboard
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .decorators_api import api_login_required

from .models import User, Unit, Shift, LeaveRequest
from .models_multi_home import CareHome
from .analytics import (
    get_dashboard_summary,
    calculate_staffing_levels,
    calculate_compliance_metrics,
    calculate_cost_metrics,
    get_trending_data,
    get_shift_distribution
)


@login_required
def executive_dashboard(request):
    """
    Executive-level dashboard with system-wide analytics.
    
    Accessible by senior management team.
    """
    # Check if user has executive access
    if not (request.user.is_superuser or (request.user.role and request.user.role.is_senior_management_team)):
        return render(request, 'scheduling/error.html', {
            'message': 'Access denied. Executive dashboard requires senior management privileges.'
        })
    
    care_home_id = request.GET.get('care_home')
    care_home = None
    if care_home_id:
        care_home = get_object_or_404(CareHome, id=care_home_id)
    
    # Use existing function-based API from analytics.py
    dashboard_data = get_dashboard_summary(care_home=care_home, date_range='month')
    
    # Get weekly trends for charts (staffing, costs, compliance)
    weekly_trends = {
        'staffing': get_trending_data(care_home, metric='staffing', periods=12),
        'costs': get_trending_data(care_home, metric='costs', periods=12),
        'compliance': get_trending_data(care_home, metric='compliance', periods=12)
    }
    
    context = {
        'dashboard': dashboard_data,
        'weekly_trends': weekly_trends,
        'selected_care_home': care_home,
        'care_homes': CareHome.objects.filter(is_active=True),
        'page_title': 'Executive Dashboard'
    }
    
    return render(request, 'scheduling/analytics/executive_dashboard.html', context)


@login_required
def manager_dashboard(request):
    """
    Manager-level dashboard for care home operations.
    
    Accessible by home managers and senior management.
    """
    # Get care home (from user's assignment or parameter)
    care_home = None
    
    if request.user.role and request.user.role.is_senior_management_team:
        # Senior management can select any care home
        care_home_id = request.GET.get('care_home')
        if care_home_id:
            care_home = get_object_or_404(CareHome, id=care_home_id)
        else:
            care_home = CareHome.objects.filter(is_active=True).first()
    elif request.user.unit and request.user.unit.care_home:
        # Regular managers see their assigned care home
        care_home = request.user.unit.care_home
    else:
        return render(request, 'scheduling/error.html', {
            'message': 'No care home assigned to your account.'
        })
    
    if not care_home:
        return render(request, 'scheduling/error.html', {
            'message': 'Please select a care home.'
        })
    
    # Use existing function-based API from analytics.py
    dashboard_data = get_dashboard_summary(care_home=care_home, date_range='week')
    
    context = {
        'dashboard': dashboard_data,
        'care_home': care_home,
        'care_homes': CareHome.objects.filter(is_active=True) if request.user.role and request.user.role.is_senior_management_team else None,
        'page_title': f'{care_home.get_name_display()} Dashboard'
    }
    
    return render(request, 'scheduling/analytics/manager_dashboard.html', context)


@login_required
def staff_performance_view(request, sap=None):
    """
    Staff performance analytics view.
    """
    if sap:
        staff_member = get_object_or_404(User, sap=sap)
    else:
        staff_member = request.user
    
    # Get date range from request or default to last 3 months
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=90)
    
    if request.GET.get('start_date'):
        start_date = request.GET.get('start_date')
    if request.GET.get('end_date'):
        end_date = request.GET.get('end_date')
    
    # Calculate performance metrics using existing data
    total_shifts = Shift.objects.filter(
        staff=staff_member,
        date__range=[start_date, end_date]
    ).count()
    
    # Attendance rate (shifts worked vs expected)
    expected_shifts = 60  # Assume ~5 shifts/week over 12 weeks
    attendance_rate = (total_shifts / expected_shifts * 100) if expected_shifts > 0 else 0
    
    # Get leave summary
    leave_requests = LeaveRequest.objects.filter(
        user=staff_member,
        start_date__lte=end_date,
        end_date__gte=start_date
    )
    
    leave_summary = {
        'total_requests': leave_requests.count(),
        'approved': leave_requests.filter(status='approved').count(),
        'pending': leave_requests.filter(status='pending').count(),
        'rejected': leave_requests.filter(status='rejected').count(),
        'total_days_taken': sum(
            (lr.end_date - lr.start_date).days + 1
            for lr in leave_requests.filter(status='approved')
        )
    }
    
    # Overtime hours (simplified calculation)
    overtime_shifts = Shift.objects.filter(
        staff=staff_member,
        date__range=[start_date, end_date],
        shift_type__hours__gt=8
    ).count()
    overtime_hours = overtime_shifts * 2  # Assume 2 hours OT per shift
    
    # Punctuality score (simplified - would need clock-in data in production)
    punctuality = 95.0  # Placeholder
    
    context = {
        'staff_member': staff_member,
        'attendance_rate': round(attendance_rate, 2),
        'punctuality': punctuality,
        'overtime_hours': overtime_hours,
        'total_shifts': total_shifts,
        'leave_summary': leave_summary,
        'start_date': start_date,
        'end_date': end_date,
        'page_title': f'Performance: {staff_member.full_name}'
    }
    
    return render(request, 'scheduling/analytics/staff_performance.html', context)


@login_required
def unit_analytics_view(request, unit_id):
    """
    Unit-level analytics view.
    """
    unit = get_object_or_404(Unit, id=unit_id)
    
    # Check access
    if not request.user.role:
        return render(request, 'scheduling/error.html', {
            'message': 'Access denied.'
        })
    
    # Get date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Use existing analytics functions
    staffing_levels = calculate_staffing_levels(
        care_home=unit.care_home,
        unit=unit,
        start_date=start_date,
        end_date=end_date
    )
    
    # Shift coverage by shift type
    shift_coverage = get_shift_distribution(
        care_home=unit.care_home,
        unit=unit,
        start_date=start_date,
        end_date=end_date
    )
    
    # Simplified prediction (would use ML in production)
    future_date = end_date + timedelta(days=7)
    prediction = {
        'predicted_staff_needed': int(staffing_levels['avg_staff_per_day']),
        'confidence': 85.0,
        'factors': ['Historical patterns', 'Leave requests', 'Occupancy trends']
    }
    
    context = {
        'unit': unit,
        'staffing_levels': staffing_levels,
        'shift_coverage': shift_coverage,
        'prediction': prediction,
        'start_date': start_date,
        'end_date': end_date,
        'page_title': f'Unit Analytics: {unit.get_name_display()}'
    }
    
    return render(request, 'scheduling/analytics/unit_analytics.html', context)


@login_required
def budget_analysis_view(request, care_home_id=None):
    """
    Budget analysis and tracking view.
    """
    if care_home_id:
        care_home = get_object_or_404(CareHome, id=care_home_id)
    elif request.user.unit and request.user.unit.care_home:
        care_home = request.user.unit.care_home
    else:
        care_home = CareHome.objects.filter(is_active=True).first()
    
    if not care_home:
        return render(request, 'scheduling/error.html', {
            'message': 'No care home available for budget analysis.'
        })
    
    # Get month/year from request or default to current
    month = int(request.GET.get('month', timezone.now().month))
    year = int(request.GET.get('year', timezone.now().year))
    
    # Calculate date range for the month
    from datetime import date
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year, 12, 31)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    # Get budget analysis using existing functions
    cost_metrics = calculate_cost_metrics(
        care_home=care_home,
        start_date=start_date,
        end_date=end_date
    )
    
    staffing_metrics = calculate_staffing_levels(
        care_home=care_home,
        start_date=start_date,
        end_date=end_date
    )
    
    budget_analysis = {
        **cost_metrics,
        **staffing_metrics,
        'month': month,
        'year': year,
        'budget_vs_actual': {
            'budget': 50000,  # Placeholder - would come from budget table
            'actual': cost_metrics['estimated_total_cost'],
            'variance': 50000 - cost_metrics['estimated_total_cost'],
            'variance_percentage': ((50000 - cost_metrics['estimated_total_cost']) / 50000 * 100) if 50000 > 0 else 0
        }
    }
    
    # Simple overtime prediction for next month
    overtime_prediction = {
        'predicted_overtime_hours': cost_metrics['estimated_overtime_cost'] / 25,  # Reverse calculate hours
        'predicted_overtime_cost': cost_metrics['estimated_overtime_cost'] * 1.1,  # 10% increase estimate
        'confidence': 75.0
    }
    
    context = {
        'care_home': care_home,
        'budget': budget_analysis,
        'prediction': overtime_prediction,
        'month': month,
        'year': year,
        'care_homes': CareHome.objects.filter(is_active=True),
        'page_title': f'Budget Analysis: {care_home.get_name_display()}'
    }
    
    return render(request, 'scheduling/analytics/budget_analysis.html', context)


@login_required
def trends_analysis_view(request):
    """
    Trends and patterns analysis view.
    """
    care_home_id = request.GET.get('care_home')
    care_home = None
    if care_home_id:
        care_home = get_object_or_404(CareHome, id=care_home_id)
    
    # Get various trends using existing functions
    weekly_trends = {
        'staffing': get_trending_data(care_home, metric='staffing', periods=12),
        'costs': get_trending_data(care_home, metric='costs', periods=12),
        'compliance': get_trending_data(care_home, metric='compliance', periods=12)
    }
    
    # Monthly leave patterns
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=90)
    leave_requests = LeaveRequest.objects.filter(
        start_date__gte=start_date,
        end_date__lte=end_date
    )
    
    if care_home:
        leave_requests = leave_requests.filter(user__care_home=care_home)
    
    monthly_leave = []
    for month_offset in range(3):
        month_start = end_date.replace(day=1) - timedelta(days=30 * month_offset)
        month_end = month_start + timedelta(days=30)
        month_requests = leave_requests.filter(
            start_date__gte=month_start,
            start_date__lt=month_end
        ).count()
        monthly_leave.append({
            'month': month_start.strftime('%B'),
            'count': month_requests
        })
    
    # Shift swap patterns (simplified - would need shift swap table)
    swap_patterns = {
        'total_swaps': 0,
        'successful_swaps': 0,
        'common_reasons': ['Annual leave', 'Childcare', 'Illness']
    }
    
    context = {
        'weekly_trends': weekly_trends,
        'monthly_leave': monthly_leave,
        'swap_patterns': swap_patterns,
        'care_home': care_home,
        'care_homes': CareHome.objects.filter(is_active=True),
        'page_title': 'Trends Analysis'
    }
    
    return render(request, 'scheduling/analytics/trends_analysis.html', context)


# AJAX/API endpoints for dashboard data


@api_login_required
def api_dashboard_summary(request):
    """
    API endpoint for dashboard summary data (JSON).
    Restricted to management users only.
    """
    # Management-only access for analytics
    if not request.user.is_management and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied. Management access required.'}, status=403)
    
    care_home_id = request.GET.get('care_home')
    care_home = None
    if care_home_id:
        care_home = CareHome.objects.filter(id=care_home_id).first()
    
    # Use existing function
    data = get_dashboard_summary(care_home=care_home, date_range='month')
    
    return JsonResponse(data)


@api_login_required
def api_unit_staffing(request, unit_id):
    """
    API endpoint for unit staffing data (JSON).
    """
    unit = get_object_or_404(Unit, id=unit_id)
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=int(request.GET.get('days', 30)))
    
    # Use existing function
    data = calculate_staffing_levels(
        care_home=unit.care_home,
        unit=unit,
        start_date=start_date,
        end_date=end_date
    )
    
    return JsonResponse(data)


@api_login_required
def api_budget_analysis(request, care_home_id):
    """
    API endpoint for budget analysis data (JSON).
    """
    care_home = get_object_or_404(CareHome, id=care_home_id)
    
    month = int(request.GET.get('month', timezone.now().month))
    year = int(request.GET.get('year', timezone.now().year))
    
    # Calculate date range
    from datetime import date
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year, 12, 31)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    # Use existing functions
    cost_data = calculate_cost_metrics(
        care_home=care_home,
        start_date=start_date,
        end_date=end_date
    )
    
    data = {
        **cost_data,
        'month': month,
        'year': year
    }
    
    return JsonResponse(data)


@api_login_required
def api_weekly_trends(request):
    """
    API endpoint for weekly shift trends (JSON).
    """
    care_home_id = request.GET.get('care_home')
    care_home = None
    if care_home_id:
        care_home = CareHome.objects.filter(id=care_home_id).first()
    
    weeks = int(request.GET.get('weeks', 12))
    
    # Use existing function for multiple metrics
    data = {
        'staffing': get_trending_data(care_home, metric='staffing', periods=weeks),
        'costs': get_trending_data(care_home, metric='costs', periods=weeks),
        'compliance': get_trending_data(care_home, metric='compliance', periods=weeks)
    }
    
    return JsonResponse({'trends': data})
