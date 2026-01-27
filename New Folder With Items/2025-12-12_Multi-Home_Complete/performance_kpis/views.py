"""
TQM Module 7: Performance Metrics & KPIs Views

Dashboard and KPI management views with Chart.js visualizations.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Avg, Count, Q, Max, Min
from django.utils import timezone
from datetime import timedelta, datetime
from .models import (
    KPIDefinition,
    KPIMeasurement,
    ExecutiveDashboard,
    DashboardKPI,
    PerformanceTarget,
    BenchmarkData,
    BalancedScorecardPerspective
)


@login_required
def dashboard_view(request):
    """Executive dashboard with KPI overview and charts."""
    
    # Get user's dashboards
    user_dashboards = ExecutiveDashboard.objects.filter(
        Q(owner=request.user) | Q(is_public=True) | Q(shared_with=request.user)
    ).distinct()
    
    # Get selected dashboard (default to first)
    dashboard_id = request.GET.get('dashboard')
    if dashboard_id:
        dashboard = get_object_or_404(ExecutiveDashboard, id=dashboard_id)
    else:
        dashboard = user_dashboards.first()
    
    # Get KPIs for dashboard
    dashboard_kpis = []
    if dashboard:
        dashboard.last_viewed = timezone.now()
        dashboard.save(update_fields=['last_viewed'])
        
        for dk in dashboard.dashboardkpi_set.all().order_by('display_order'):
            # Get latest measurement
            latest = KPIMeasurement.objects.filter(
                kpi=dk.kpi
            ).order_by('-measurement_date').first()
            
            # Get measurements for time range
            from_date = timezone.now().date() - timedelta(days=dk.time_range_days)
            measurements = KPIMeasurement.objects.filter(
                kpi=dk.kpi,
                measurement_date__gte=from_date
            ).order_by('measurement_date')
            
            dashboard_kpis.append({
                'dashboard_kpi': dk,
                'kpi': dk.kpi,
                'latest': latest,
                'measurements': measurements,
                'chart_data': _prepare_chart_data(measurements, dk),
            })
    
    # Summary statistics
    total_kpis = KPIDefinition.objects.filter(is_active=True).count()
    green_count = KPIMeasurement.objects.filter(
        rag_status='GREEN',
        measurement_date__gte=timezone.now().date() - timedelta(days=30)
    ).values('kpi').distinct().count()
    
    amber_count = KPIMeasurement.objects.filter(
        rag_status='AMBER',
        measurement_date__gte=timezone.now().date() - timedelta(days=30)
    ).values('kpi').distinct().count()
    
    red_count = KPIMeasurement.objects.filter(
        rag_status='RED',
        measurement_date__gte=timezone.now().date() - timedelta(days=30)
    ).values('kpi').distinct().count()
    
    context = {
        'user_dashboards': user_dashboards,
        'current_dashboard': dashboard,
        'dashboard_kpis': dashboard_kpis,
        'total_kpis': total_kpis,
        'green_count': green_count,
        'amber_count': amber_count,
        'red_count': red_count,
    }
    
    return render(request, 'performance_kpis/dashboard.html', context)


@login_required
def kpi_list_view(request):
    """List all KPI definitions with filtering."""
    
    kpis = KPIDefinition.objects.filter(is_active=True)
    
    # Filters
    category = request.GET.get('category')
    if category:
        kpis = kpis.filter(category=category)
    
    search = request.GET.get('search')
    if search:
        kpis = kpis.filter(
            Q(code__icontains=search) |
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Add latest measurement to each KPI
    kpi_data = []
    for kpi in kpis:
        latest = KPIMeasurement.objects.filter(kpi=kpi).order_by('-measurement_date').first()
        kpi_data.append({
            'kpi': kpi,
            'latest_measurement': latest,
        })
    
    context = {
        'kpi_data': kpi_data,
        'categories': KPIDefinition.KPICategory.choices,
        'selected_category': category,
        'search_query': search,
    }
    
    return render(request, 'performance_kpis/kpi_list.html', context)


@login_required
def kpi_detail_view(request, kpi_id):
    """Detailed view of a KPI with trend chart and measurements."""
    
    kpi = get_object_or_404(KPIDefinition, id=kpi_id)
    
    # Get time range
    days = int(request.GET.get('days', 90))
    from_date = timezone.now().date() - timedelta(days=days)
    
    # Get measurements
    measurements = KPIMeasurement.objects.filter(
        kpi=kpi,
        measurement_date__gte=from_date
    ).order_by('measurement_date')
    
    # Get targets
    current_targets = PerformanceTarget.objects.filter(
        kpi=kpi,
        period_start__lte=timezone.now().date(),
        period_end__gte=timezone.now().date()
    )
    
    # Get benchmarks
    benchmarks = BenchmarkData.objects.filter(kpi=kpi).order_by('-period_start')[:5]
    
    # Calculate statistics
    stats = measurements.aggregate(
        avg_value=Avg('actual_value'),
        max_value=Max('actual_value'),
        min_value=Min('actual_value'),
        green_count=Count('id', filter=Q(rag_status='GREEN')),
        amber_count=Count('id', filter=Q(rag_status='AMBER')),
        red_count=Count('id', filter=Q(rag_status='RED')),
    )
    
    context = {
        'kpi': kpi,
        'measurements': measurements,
        'current_targets': current_targets,
        'benchmarks': benchmarks,
        'stats': stats,
        'days': days,
        'chart_data': _prepare_kpi_chart_data(measurements, kpi),
    }
    
    return render(request, 'performance_kpis/kpi_detail.html', context)


@login_required
def measurement_create_view(request, kpi_id):
    """Record a new KPI measurement."""
    
    kpi = get_object_or_404(KPIDefinition, id=kpi_id)
    
    if request.method == 'POST':
        try:
            # Create measurement
            measurement = KPIMeasurement(
                kpi=kpi,
                measurement_date=request.POST.get('measurement_date'),
                actual_value=request.POST.get('actual_value'),
                recorded_by=request.user,
            )
            
            # Optional fields
            if request.POST.get('period_start'):
                measurement.period_start = request.POST.get('period_start')
            if request.POST.get('period_end'):
                measurement.period_end = request.POST.get('period_end')
            if request.POST.get('target_value'):
                measurement.target_value = request.POST.get('target_value')
            if request.POST.get('numerator'):
                measurement.numerator = request.POST.get('numerator')
            if request.POST.get('denominator'):
                measurement.denominator = request.POST.get('denominator')
            if request.POST.get('notes'):
                measurement.notes = request.POST.get('notes')
            
            # Care home if specified
            care_home_id = request.POST.get('care_home')
            if care_home_id:
                from scheduling.models import CareHome
                measurement.care_home = CareHome.objects.get(id=care_home_id)
            
            measurement.save()
            
            messages.success(request, f'Measurement recorded for {kpi.name}')
            return redirect('performance_kpis:kpi_detail', kpi_id=kpi.id)
            
        except Exception as e:
            messages.error(request, f'Error recording measurement: {str(e)}')
    
    # Get care homes for dropdown
    from scheduling.models import CareHome
    care_homes = CareHome.objects.all()
    
    context = {
        'kpi': kpi,
        'care_homes': care_homes,
        'today': timezone.now().date(),
    }
    
    return render(request, 'performance_kpis/measurement_form.html', context)


@login_required
def balanced_scorecard_view(request):
    """Balanced scorecard view with 4 perspectives."""
    
    perspectives = BalancedScorecardPerspective.objects.filter(
        is_active=True
    ).order_by('display_order')
    
    # For each perspective, get relevant KPIs
    scorecard_data = []
    for perspective in perspectives:
        # Get KPIs (would need to add perspective field to KPIDefinition)
        # For now, showing all active KPIs
        kpis = KPIDefinition.objects.filter(is_active=True)[:5]
        
        perspective_kpis = []
        for kpi in kpis:
            latest = KPIMeasurement.objects.filter(kpi=kpi).order_by('-measurement_date').first()
            perspective_kpis.append({
                'kpi': kpi,
                'latest': latest,
            })
        
        scorecard_data.append({
            'perspective': perspective,
            'kpis': perspective_kpis,
        })
    
    context = {
        'scorecard_data': scorecard_data,
    }
    
    return render(request, 'performance_kpis/balanced_scorecard.html', context)


@login_required
def dashboard_api(request, dashboard_id):
    """API endpoint for dashboard chart data."""
    
    dashboard = get_object_or_404(ExecutiveDashboard, id=dashboard_id)
    
    chart_data = []
    for dk in dashboard.dashboardkpi_set.all().order_by('display_order'):
        from_date = timezone.now().date() - timedelta(days=dk.time_range_days)
        measurements = KPIMeasurement.objects.filter(
            kpi=dk.kpi,
            measurement_date__gte=from_date
        ).order_by('measurement_date')
        
        data = {
            'kpi_code': dk.kpi.code,
            'kpi_name': dk.kpi.name,
            'chart_type': dk.chart_type,
            'data': _prepare_chart_data(measurements, dk),
        }
        chart_data.append(data)
    
    return JsonResponse({'charts': chart_data})


@login_required
def kpi_trend_api(request, kpi_id):
    """API endpoint for KPI trend data."""
    
    kpi = get_object_or_404(KPIDefinition, id=kpi_id)
    days = int(request.GET.get('days', 90))
    from_date = timezone.now().date() - timedelta(days=days)
    
    measurements = KPIMeasurement.objects.filter(
        kpi=kpi,
        measurement_date__gte=from_date
    ).order_by('measurement_date')
    
    data = _prepare_kpi_chart_data(measurements, kpi)
    
    return JsonResponse(data)


def _prepare_chart_data(measurements, dashboard_kpi):
    """Prepare chart data for Chart.js."""
    
    labels = []
    values = []
    targets = []
    rag_colors = []
    
    for m in measurements:
        labels.append(m.measurement_date.strftime('%Y-%m-%d'))
        values.append(float(m.actual_value))
        
        target = m.target_value or dashboard_kpi.kpi.target_value
        targets.append(float(target) if target else None)
        
        # RAG colors
        color_map = {
            'GREEN': '#28a745',
            'AMBER': '#ffc107',
            'RED': '#dc3545',
            'UNKNOWN': '#6c757d',
        }
        rag_colors.append(color_map.get(m.rag_status, '#6c757d'))
    
    return {
        'labels': labels,
        'values': values,
        'targets': targets,
        'rag_colors': rag_colors,
        'chart_type': dashboard_kpi.chart_type,
        'show_trend': dashboard_kpi.show_trend,
        'show_target': dashboard_kpi.show_target,
    }


def _prepare_kpi_chart_data(measurements, kpi):
    """Prepare detailed KPI chart data."""
    
    labels = []
    values = []
    targets = []
    rag_colors = []
    
    for m in measurements:
        labels.append(m.measurement_date.strftime('%Y-%m-%d'))
        values.append(float(m.actual_value))
        
        target = m.target_value or kpi.target_value
        targets.append(float(target) if target else None)
        
        color_map = {
            'GREEN': '#28a745',
            'AMBER': '#ffc107',
            'RED': '#dc3545',
            'UNKNOWN': '#6c757d',
        }
        rag_colors.append(color_map.get(m.rag_status, '#6c757d'))
    
    # Add threshold lines
    thresholds = {
        'green': float(kpi.threshold_green) if kpi.threshold_green else None,
        'amber': float(kpi.threshold_amber) if kpi.threshold_amber else None,
        'red': float(kpi.threshold_red) if kpi.threshold_red else None,
    }
    
    return {
        'labels': labels,
        'values': values,
        'targets': targets,
        'rag_colors': rag_colors,
        'thresholds': thresholds,
        'kpi_name': kpi.name,
        'measurement_type': kpi.measurement_type,
    }
