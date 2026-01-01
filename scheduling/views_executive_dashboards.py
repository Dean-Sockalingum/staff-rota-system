"""
Executive Dashboard Views
=========================

Three advanced analytics dashboards for senior leadership:
1. Budget Dashboard - Real-time budget tracking and forecasting
2. Early Warning System - 14-day shortage prediction with escalation
3. Retention Predictor - ML-powered staff turnover risk analysis

All dashboards include interactive charts, data exports, and actionable insights.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta
import json

# Import executive utilities
from scheduling.utils_budget_dashboard import get_budget_dashboard_api
from scheduling.utils_early_warning import get_early_warning_executive_dashboard, export_early_warning_excel
from scheduling.utils_retention_predictor import get_retention_executive_dashboard, export_retention_dashboard_excel
from scheduling.utils_auto_roster import get_auto_roster_executive_dashboard
from scheduling.utils_care_home_predictor import get_ci_performance_executive_dashboard
from scheduling.utils_predictive_budget import get_predictive_budget_executive_dashboard
from scheduling.models_multi_home import CareHome


def is_manager_or_above(user):
    """Check if user is a manager, head of service, or admin"""
    if user.is_superuser or user.is_staff:
        return True
    if hasattr(user, 'role') and user.role:
        return user.role.is_management or user.role.name in ['HEAD_OF_SERVICE', 'ADMINISTRATOR']
    return False


@login_required
@user_passes_test(is_manager_or_above, login_url='/login/')
def budget_dashboard(request):
    """
    Real-Time Budget Dashboard
    
    Features:
    - Monthly spend vs budget
    - Trend charts (6-month history)
    - Cost breakdowns by category
    - Projected end-of-month totals
    - Alerts for over-budget categories
    """
    
    # Get filter parameters
    care_home_id = request.GET.get('care_home')
    month = request.GET.get('month')
    year = request.GET.get('year')
    
    # Parse month/year or use current
    if month and year:
        month = int(month)
        year = int(year)
    else:
        today = timezone.now()
        month = today.month
        year = today.year
    
    # Get care home filter
    care_home = None
    if care_home_id:
        try:
            care_home = CareHome.objects.get(id=care_home_id)
        except CareHome.DoesNotExist:
            pass
    
    # Get dashboard data from API
    dashboard_data = get_budget_dashboard_api(care_home=care_home, month=month, year=year)
    
    # Get all care homes for filter dropdown
    care_homes = CareHome.objects.all().order_by('name')
    
    # Generate month/year options (last 12 months)
    today = timezone.now()
    month_options = []
    for i in range(12):
        dt = today - timedelta(days=30 * i)
        month_options.append({
            'month': dt.month,
            'year': dt.year,
            'display': dt.strftime('%B %Y')
        })
    
    context = {
        'page_title': 'Budget Dashboard',
        'dashboard_data': dashboard_data,
        'care_homes': care_homes,
        'selected_care_home': care_home,
        'selected_month': month,
        'selected_year': year,
        'month_options': month_options,
        'current_month': today.month,
        'current_year': today.year,
    }
    
    return render(request, 'scheduling/budget_dashboard.html', context)


@login_required
@user_passes_test(is_manager_or_above, login_url='/login/')
def early_warning_dashboard(request):
    """
    Early Warning System Dashboard
    
    Features:
    - 14-day shortage heatmap
    - 4-level escalation system
    - Unit-by-unit analysis
    - Predicted critical dates
    - Actionable recommendations
    """
    
    # Get care home filter
    care_home_id = request.GET.get('care_home')
    care_home = None
    if care_home_id:
        try:
            care_home = CareHome.objects.get(id=care_home_id)
        except CareHome.DoesNotExist:
            pass
    
    # Get dashboard data
    dashboard_data = get_early_warning_executive_dashboard(care_home=care_home)
    
    # Get all care homes for filter
    care_homes = CareHome.objects.all().order_by('name')
    
    context = {
        'page_title': 'Early Warning System',
        'dashboard_data': dashboard_data,
        'care_homes': care_homes,
        'selected_care_home': care_home,
    }
    
    return render(request, 'scheduling/early_warning_dashboard.html', context)


@login_required
@user_passes_test(is_manager_or_above, login_url='/login/')
def retention_predictor_dashboard(request):
    """
    Staff Retention Predictor Dashboard
    
    Features:
    - ML-powered turnover risk scores
    - At-risk staff identification
    - Health score trends
    - Personalized intervention plans
    - Cost impact analysis
    """
    
    # Get care home filter
    care_home_id = request.GET.get('care_home')
    care_home = None
    if care_home_id:
        try:
            care_home = CareHome.objects.get(id=care_home_id)
        except CareHome.DoesNotExist:
            pass
    
    # Get retention dashboard data (includes intervention plans)
    dashboard_data = get_retention_executive_dashboard(care_home=care_home)
    
    # Get all care homes for filter
    care_homes = CareHome.objects.all().order_by('name')
    
    context = {
        'page_title': 'Retention Predictor',
        'dashboard_data': dashboard_data,
        'care_homes': care_homes,
        'selected_care_home': care_home,
    }
    
    return render(request, 'scheduling/retention_predictor_dashboard.html', context)


# Export endpoints

@login_required
@user_passes_test(is_manager_or_above, login_url='/login/')
def export_budget_excel(request):
    """Export budget dashboard to Excel"""
    care_home_id = request.GET.get('care_home')
    month = request.GET.get('month')
    year = request.GET.get('year')
    
    care_home = None
    if care_home_id:
        try:
            care_home = CareHome.objects.get(id=care_home_id)
        except:
            pass
    
    # Parse dates
    if month and year:
        month = int(month)
        year = int(year)
    else:
        today = timezone.now()
        month = today.month
        year = today.year
    
    # Get data
    dashboard_data = get_budget_dashboard_api(care_home=care_home, month=month, year=year)
    
    # Create Excel response
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Budget Dashboard Export'])
    writer.writerow([f'Period: {month}/{year}'])
    writer.writerow([f'Care Home: {care_home.name if care_home else "All Homes"}'])
    writer.writerow([])
    
    # Summary
    writer.writerow(['Summary'])
    writer.writerow(['Total Budget', dashboard_data.get('total_budget', 0)])
    writer.writerow(['Total Spend', dashboard_data.get('total_spend', 0)])
    writer.writerow(['Remaining', dashboard_data.get('remaining_budget', 0)])
    writer.writerow(['Status', dashboard_data.get('status', 'Unknown')])
    writer.writerow([])
    
    # Category breakdown
    writer.writerow(['Category', 'Budget', 'Actual', 'Variance', '% Used'])
    for category in dashboard_data.get('category_breakdown', []):
        writer.writerow([
            category.get('name'),
            category.get('budget'),
            category.get('actual'),
            category.get('variance'),
            category.get('percent_used')
        ])
    
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="budget_dashboard_{month}_{year}.csv"'
    return response


@login_required
@user_passes_test(is_manager_or_above, login_url='/login/')
def export_early_warning(request):
    """Export early warning dashboard to Excel"""
    care_home_id = request.GET.get('care_home')
    care_home = None
    if care_home_id:
        try:
            care_home = CareHome.objects.get(id=care_home_id)
        except:
            pass
    
    # Use the existing Excel export function
    filepath = export_early_warning_excel(care_home=care_home)
    
    with open(filepath, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/vnd.ms-excel')
        filename = f'early_warning_{care_home.name if care_home else "all_homes"}_{timezone.now().strftime("%Y%m%d")}.csv'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


@login_required
@user_passes_test(is_manager_or_above, login_url='/login/')
def export_retention_csv(request):
    """Export retention data using backend export function"""
    care_home_id = request.GET.get('care_home')
    care_home = None
    if care_home_id:
        try:
            care_home = CareHome.objects.get(id=care_home_id)
        except:
            pass
    
    # Use the backend export function
    return export_retention_dashboard_excel(care_home=care_home)


# ============================================================================
# AUTO-ROSTER GENERATOR DASHBOARD
# ============================================================================

@login_required
@user_passes_test(is_manager_or_above, login_url='/login/')
def auto_roster_dashboard(request):
    """
    Auto-Roster Quality Dashboard
    
    Features:
    - Quality score (0-100)
    - Fairness score (0-100)
    - Constraint violations
    - Staff distribution metrics
    """
    
    # Get date range (default to next 14 days)
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    else:
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=13)
    
    # Get care home filter
    care_home_id = request.GET.get('care_home')
    care_home = None
    if care_home_id:
        try:
            care_home = CareHome.objects.get(id=care_home_id)
        except:
            pass
    
    # Get auto-roster dashboard data
    roster_data = get_auto_roster_executive_dashboard(start_date, end_date, care_home)
    
    context = {
        'roster_data': roster_data,
        'care_homes': CareHome.objects.all(),
        'selected_care_home': care_home,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'scheduling/auto_roster_dashboard.html', context)


@login_required
@user_passes_test(is_manager_or_above, login_url='/login/')
def export_auto_roster(request):
    """Export auto-roster analysis to CSV"""
    import csv
    from io import StringIO
    
    # Get parameters (same as dashboard)
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    else:
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=13)
    
    care_home_id = request.GET.get('care_home')
    care_home = None
    if care_home_id:
        try:
            care_home = CareHome.objects.get(id=care_home_id)
        except:
            pass
    
    roster_data = get_auto_roster_executive_dashboard(start_date, end_date, care_home)
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Summary section
    summary = roster_data.get('executive_summary', {})
    writer.writerow(['Auto-Roster Quality Analysis'])
    writer.writerow(['Period', f'{start_date} to {end_date}'])
    writer.writerow(['Care Home', care_home.name if care_home else 'All Homes'])
    writer.writerow([])
    writer.writerow(['Quality Score', summary.get('quality_score')])
    writer.writerow(['Fairness Score', summary.get('fairness_score')])
    writer.writerow(['Overall Score', summary.get('overall_score')])
    writer.writerow(['Status', summary.get('status_text')])
    writer.writerow(['Total Shifts', summary.get('total_shifts')])
    writer.writerow([])
    
    # Quality metrics
    writer.writerow(['Quality Metrics'])
    quality = roster_data.get('quality_metrics', {})
    for metric, value in quality.items():
        writer.writerow([metric.replace('_', ' ').title(), f'{value}%'])
    writer.writerow([])
    
    # Fairness metrics
    writer.writerow(['Fairness Metrics'])
    fairness = roster_data.get('fairness_metrics', {})
    for metric, value in fairness.items():
        writer.writerow([metric.replace('_', ' ').title(), value])
    
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    filename = f'auto_roster_analysis_{start_date}_{end_date}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# ============================================================================
# CI PERFORMANCE DASHBOARD
# ============================================================================

@login_required
@user_passes_test(is_manager_or_above, login_url='/login/')
def ci_performance_dashboard(request):
    """
    Care Inspectorate Performance Dashboard
    
    Features:
    - Predicted CI rating (0-100)
    - Peer benchmarking
    - 6-month trend analysis
    - Improvement recommendations
    """
    import json
    from django.core.serializers.json import DjangoJSONEncoder
    
    # Get care home filter
    care_home_id = request.GET.get('care_home')
    care_home = None
    if care_home_id:
        try:
            care_home = CareHome.objects.get(id=care_home_id)
        except:
            pass
    
    # Default to first care home if none selected
    if not care_home:
        care_home = CareHome.objects.first()
    
    # Get CI performance data
    ci_data = get_ci_performance_executive_dashboard(care_home)
    
    # Serialize ci_data to JSON for JavaScript consumption (using DjangoJSONEncoder to handle dates)
    ci_data_json = json.dumps(ci_data, cls=DjangoJSONEncoder)
    
    context = {
        'ci_data': ci_data,
        'ci_data_json': ci_data_json,
        'care_homes': CareHome.objects.all(),
        'selected_care_home': care_home,
    }
    
    return render(request, 'scheduling/ci_performance_dashboard.html', context)


@login_required
@user_passes_test(is_manager_or_above, login_url='/login/')
def export_ci_performance(request):
    """Export CI performance analysis to CSV"""
    import csv
    from io import StringIO
    
    # Get care home
    care_home_id = request.GET.get('care_home')
    care_home = None
    if care_home_id:
        try:
            care_home = CareHome.objects.get(id=care_home_id)
        except:
            pass
    
    if not care_home:
        care_home = CareHome.objects.first()
    
    ci_data = get_ci_performance_executive_dashboard(care_home)
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Summary section
    summary = ci_data.get('executive_summary', {})
    writer.writerow(['CI Performance Analysis'])
    writer.writerow(['Care Home', care_home.name])
    writer.writerow(['Generated', timezone.now().strftime('%Y-%m-%d %H:%M')])
    writer.writerow([])
    writer.writerow(['CI Rating Score', summary.get('ci_rating_score')])
    writer.writerow(['Predicted Grade', summary.get('predicted_grade')])
    writer.writerow(['Status', summary.get('status_text')])
    writer.writerow(['Peer Rank', f"{summary.get('peer_rank')} of {summary.get('total_homes')}"])
    writer.writerow([])
    
    # Peer benchmarking
    writer.writerow(['Peer Benchmarking'])
    writer.writerow(['Rank', 'Home Name', 'CI Score', 'Staffing Score', 'Quality Score'])
    for peer in ci_data.get('peer_benchmarking', []):
        writer.writerow([
            peer.get('rank'),
            peer.get('home_name'),
            peer.get('ci_score'),
            peer.get('staffing_score'),
            peer.get('quality_score')
        ])
    
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    filename = f'ci_performance_{care_home.name}_{timezone.now().strftime("%Y%m%d")}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# ============================================================================
# PREDICTIVE BUDGET DASHBOARD
# ============================================================================

@login_required
@user_passes_test(is_manager_or_above, login_url='/login/')
def predictive_budget_dashboard(request):
    """
    Predictive Budget & Scenario Analysis Dashboard
    
    Features:
    - Forecast accuracy metrics
    - Scenario modeling (best/expected/worst case)
    - ROI analysis
    - Cost projections
    """
    
    # Get care home filter
    care_home_id = request.GET.get('care_home')
    care_home = None
    if care_home_id:
        try:
            care_home = CareHome.objects.get(id=care_home_id)
        except:
            pass
    
    # Default to first care home if none selected
    if not care_home:
        care_home = CareHome.objects.first()
    
    # Get predictive budget data
    budget_data = get_predictive_budget_executive_dashboard(care_home)
    
    context = {
        'budget_data': budget_data,
        'care_homes': CareHome.objects.all(),
        'selected_care_home': care_home,
    }
    
    return render(request, 'scheduling/predictive_budget_dashboard.html', context)


@login_required
@user_passes_test(is_manager_or_above, login_url='/login/')
def export_predictive_budget(request):
    """Export predictive budget analysis to CSV"""
    import csv
    from io import StringIO
    
    # Get care home
    care_home_id = request.GET.get('care_home')
    care_home = None
    if care_home_id:
        try:
            care_home = CareHome.objects.get(id=care_home_id)
        except:
            pass
    
    if not care_home:
        care_home = CareHome.objects.first()
    
    budget_data = get_predictive_budget_executive_dashboard(care_home)
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Summary section
    summary = budget_data.get('executive_summary', {})
    writer.writerow(['Predictive Budget Analysis'])
    writer.writerow(['Care Home', care_home.name])
    writer.writerow(['Generated', timezone.now().strftime('%Y-%m-%d %H:%M')])
    writer.writerow([])
    writer.writerow(['Forecast Accuracy', f"{summary.get('forecast_accuracy')}%"])
    writer.writerow(['Status', summary.get('status_text')])
    writer.writerow(['Next Quarter Projection', f"£{summary.get('next_quarter_projection', 0):,.2f}"])
    writer.writerow([])
    
    # Scenario analysis
    writer.writerow(['Scenario Analysis'])
    writer.writerow(['Scenario', 'Total Cost', 'Regular', 'Overtime', 'Agency'])
    scenarios = budget_data.get('scenario_analysis', {})
    for scenario_name, scenario in scenarios.items():
        writer.writerow([
            scenario_name.replace('_', ' ').title(),
            f"£{scenario.get('total_cost', 0):,.2f}",
            f"£{scenario.get('regular', 0):,.2f}",
            f"£{scenario.get('overtime', 0):,.2f}",
            f"£{scenario.get('agency', 0):,.2f}"
        ])
    writer.writerow([])
    
    # ROI metrics
    writer.writerow(['ROI Metrics'])
    roi = budget_data.get('roi_metrics', {})
    writer.writerow(['Cost Avoidance', f"£{roi.get('cost_avoidance', 0):,.2f}"])
    writer.writerow(['Efficiency Gains', f"£{roi.get('efficiency_gains', 0):,.2f}"])
    writer.writerow(['Total ROI', f"£{roi.get('total_roi', 0):,.2f}"])
    writer.writerow(['ROI Percentage', f"{roi.get('roi_percentage', 0)}%"])
    
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    filename = f'predictive_budget_{care_home.name}_{timezone.now().strftime("%Y%m%d")}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
