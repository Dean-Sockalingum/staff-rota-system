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

from .models import User, Unit
from .models_multi_home import CareHome
from .analytics import (
    StaffPerformanceAnalytics,
    UnitAnalytics,
    CareHomeAnalytics,
    TrendAnalytics,
    PredictiveAnalytics,
    DashboardAggregator
)


@login_required
def executive_dashboard(request):
    """
    Executive-level dashboard with system-wide analytics.
    
    Accessible by senior management team.
    """
    # Check if user has executive access
    if not request.user.role or not request.user.role.is_senior_management_team:
        return render(request, 'scheduling/error.html', {
            'message': 'Access denied. Executive dashboard requires senior management privileges.'
        })
    
    care_home_id = request.GET.get('care_home')
    care_home = None
    if care_home_id:
        care_home = get_object_or_404(CareHome, id=care_home_id)
    
    dashboard_data = DashboardAggregator.get_executive_dashboard(care_home)
    
    # Get weekly trends for charts
    weekly_trends = TrendAnalytics.get_weekly_shift_trends(care_home, weeks=12)
    
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
    
    dashboard_data = DashboardAggregator.get_manager_dashboard(care_home)
    
    context = {
        'dashboard': dashboard_data,
        'care_home': care_home,
        'care_homes': CareHome.objects.filter(is_active=True) if request.user.role.is_senior_management_team else None,
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
    
    # Get performance metrics
    attendance_rate = StaffPerformanceAnalytics.get_staff_attendance_rate(
        staff_member, start_date, end_date
    )
    
    punctuality = StaffPerformanceAnalytics.get_staff_punctuality_score(
        staff_member, start_date, end_date
    )
    
    overtime_hours = StaffPerformanceAnalytics.get_staff_overtime_hours(
        staff_member, start_date, end_date
    )
    
    leave_summary = StaffPerformanceAnalytics.get_staff_leave_summary(
        staff_member
    )
    
    context = {
        'staff_member': staff_member,
        'attendance_rate': attendance_rate,
        'punctuality': punctuality,
        'overtime_hours': overtime_hours,
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
    
    staffing_levels = UnitAnalytics.get_unit_staffing_levels(
        unit, start_date, end_date
    )
    
    shift_coverage = UnitAnalytics.get_unit_shift_coverage(
        unit, start_date, end_date
    )
    
    # Predict future staffing needs
    future_date = end_date + timedelta(days=7)
    prediction = PredictiveAnalytics.predict_staffing_needs(unit, future_date)
    
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
    
    budget_analysis = CareHomeAnalytics.get_care_home_budget_analysis(
        care_home, month, year
    )
    
    # Get prediction for next month
    overtime_prediction = PredictiveAnalytics.predict_overtime_cost(
        care_home, next_month=True
    )
    
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
    
    # Get various trends
    weekly_trends = TrendAnalytics.get_weekly_shift_trends(care_home, weeks=12)
    monthly_leave = TrendAnalytics.get_monthly_leave_patterns()
    swap_patterns = TrendAnalytics.get_shift_swap_patterns(
        start_date=timezone.now() - timedelta(days=90)
    )
    
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


@login_required
def api_dashboard_summary(request):
    """
    API endpoint for dashboard summary data (JSON).
    """
    care_home_id = request.GET.get('care_home')
    care_home = None
    if care_home_id:
        care_home = CareHome.objects.filter(id=care_home_id).first()
    
    data = DashboardAggregator.get_executive_dashboard(care_home)
    
    return JsonResponse(data)


@login_required
def api_unit_staffing(request, unit_id):
    """
    API endpoint for unit staffing data (JSON).
    """
    unit = get_object_or_404(Unit, id=unit_id)
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=int(request.GET.get('days', 30)))
    
    data = UnitAnalytics.get_unit_staffing_levels(unit, start_date, end_date)
    
    return JsonResponse(data)


@login_required
def api_budget_analysis(request, care_home_id):
    """
    API endpoint for budget analysis data (JSON).
    """
    care_home = get_object_or_404(CareHome, id=care_home_id)
    
    month = int(request.GET.get('month', timezone.now().month))
    year = int(request.GET.get('year', timezone.now().year))
    
    data = CareHomeAnalytics.get_care_home_budget_analysis(care_home, month, year)
    
    return JsonResponse(data)


@login_required
def api_weekly_trends(request):
    """
    API endpoint for weekly shift trends (JSON).
    """
    care_home_id = request.GET.get('care_home')
    care_home = None
    if care_home_id:
        care_home = CareHome.objects.filter(id=care_home_id).first()
    
    weeks = int(request.GET.get('weeks', 12))
    
    data = TrendAnalytics.get_weekly_shift_trends(care_home, weeks)
    
    return JsonResponse({'trends': data})
