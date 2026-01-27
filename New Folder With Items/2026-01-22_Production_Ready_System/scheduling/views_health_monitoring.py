"""
Health Monitoring Dashboard Views
Views for system health monitoring, performance tracking, and error analysis
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Avg, Max, Min, Sum, Q
from django.core.paginator import Paginator
from datetime import timedelta
import json

from .models_health_monitoring import (
    SystemHealthMetric, PerformanceLog, ErrorLog,
    SystemUptime, HealthCheckEndpoint, HealthCheckResult, AlertRule
)
from .health_monitor import HealthMonitor


@staff_member_required
def health_dashboard(request):
    """Main health monitoring dashboard"""
    monitor = HealthMonitor()
    
    # Get current system status
    system_status = monitor.get_system_status()
    
    # Get recent metrics (last hour)
    one_hour_ago = timezone.now() - timedelta(hours=1)
    recent_metrics = SystemHealthMetric.objects.filter(
        timestamp__gte=one_hour_ago
    ).order_by('-timestamp')
    
    # Get latest metric of each type
    latest_metrics = {}
    for metric_type in ['CPU', 'MEMORY', 'DISK', 'DATABASE', 'RESPONSE_TIME', 'ERROR_RATE', 'ACTIVE_USERS']:
        metric = SystemHealthMetric.objects.filter(
            metric_type=metric_type
        ).order_by('-timestamp').first()
        if metric:
            latest_metrics[metric_type] = metric
    
    # Get health check endpoints
    health_checks = HealthCheckEndpoint.objects.all()
    unhealthy_checks = health_checks.filter(is_healthy=False)
    
    # Get recent errors
    recent_errors = ErrorLog.objects.filter(
        timestamp__gte=one_hour_ago,
        is_resolved=False
    ).order_by('-timestamp')[:10]
    
    # Get uptime stats
    uptime_30d = SystemUptime.calculate_uptime_percentage(days=30)
    uptime_7d = SystemUptime.calculate_uptime_percentage(days=7)
    
    # Get performance summary
    performance_summary = monitor.get_performance_summary(hours=24)
    
    # Get error summary
    error_summary = monitor.get_error_summary(hours=24)
    
    context = {
        'system_status': system_status,
        'latest_metrics': latest_metrics,
        'health_checks': health_checks,
        'unhealthy_checks_count': unhealthy_checks.count(),
        'recent_errors': recent_errors,
        'uptime_30d': round(uptime_30d, 2),
        'uptime_7d': round(uptime_7d, 2),
        'performance_summary': performance_summary,
        'error_summary': error_summary,
    }
    
    return render(request, 'scheduling/health_dashboard.html', context)


@staff_member_required
def health_metrics_api(request):
    """API endpoint for real-time health metrics"""
    metric_type = request.GET.get('type', 'CPU')
    hours = int(request.GET.get('hours', 24))
    
    since = timezone.now() - timedelta(hours=hours)
    metrics = SystemHealthMetric.objects.filter(
        metric_type=metric_type,
        timestamp__gte=since
    ).order_by('timestamp')
    
    data = {
        'metric_type': metric_type,
        'period_hours': hours,
        'data': [
            {
                'timestamp': m.timestamp.isoformat(),
                'value': m.value,
                'status': m.status,
                'unit': m.unit,
            }
            for m in metrics
        ]
    }
    
    return JsonResponse(data)


@staff_member_required
def performance_logs_view(request):
    """Performance logs listing with filtering"""
    log_type = request.GET.get('type', 'HTTP')
    hours = int(request.GET.get('hours', 24))
    min_duration = request.GET.get('min_duration', '')
    
    since = timezone.now() - timedelta(hours=hours)
    logs = PerformanceLog.objects.filter(
        log_type=log_type,
        timestamp__gte=since
    )
    
    # Filter by minimum duration if provided
    if min_duration:
        try:
            logs = logs.filter(duration_ms__gte=int(min_duration))
        except ValueError:
            pass
    
    logs = logs.order_by('-duration_ms')
    
    # Pagination
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Calculate statistics
    stats = logs.aggregate(
        avg_duration=Avg('duration_ms'),
        max_duration=Max('duration_ms'),
        min_duration=Min('duration_ms'),
        total_count=Count('id')
    )
    
    # Get slow endpoints (if HTTP)
    slow_endpoints = []
    if log_type == 'HTTP':
        slow_endpoints = PerformanceLog.get_slow_endpoints(
            threshold_ms=int(min_duration) if min_duration else 500,
            hours=hours
        )[:10]
    
    context = {
        'logs': page_obj,
        'log_type': log_type,
        'hours': hours,
        'min_duration': min_duration,
        'stats': stats,
        'slow_endpoints': slow_endpoints,
    }
    
    return render(request, 'scheduling/performance_logs.html', context)


@staff_member_required
def error_logs_view(request):
    """Error logs listing with filtering"""
    severity = request.GET.get('severity', '')
    error_type = request.GET.get('error_type', '')
    resolved = request.GET.get('resolved', 'false')
    hours = int(request.GET.get('hours', 24))
    
    since = timezone.now() - timedelta(hours=hours)
    errors = ErrorLog.objects.filter(timestamp__gte=since)
    
    # Apply filters
    if severity:
        errors = errors.filter(severity=severity)
    if error_type:
        errors = errors.filter(error_type=error_type)
    if resolved == 'true':
        errors = errors.filter(is_resolved=True)
    elif resolved == 'false':
        errors = errors.filter(is_resolved=False)
    
    errors = errors.order_by('-timestamp')
    
    # Pagination
    paginator = Paginator(errors, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get error statistics
    all_errors = ErrorLog.objects.filter(timestamp__gte=since)
    error_stats = {
        'total': all_errors.count(),
        'unresolved': all_errors.filter(is_resolved=False).count(),
        'critical': all_errors.filter(severity='CRITICAL').count(),
        'by_type': dict(
            all_errors.values('error_type').annotate(
                count=Count('id')
            ).values_list('error_type', 'count')
        ),
        'top_errors': list(
            all_errors.values('message', 'error_type').annotate(
                count=Sum('occurrence_count')
            ).order_by('-count')[:5]
        ),
    }
    
    context = {
        'errors': page_obj,
        'severity': severity,
        'error_type': error_type,
        'resolved': resolved,
        'hours': hours,
        'error_stats': error_stats,
        'severity_choices': ErrorLog.SEVERITY_CHOICES,
        'error_type_choices': ErrorLog.ERROR_TYPE_CHOICES,
    }
    
    return render(request, 'scheduling/error_logs.html', context)


@staff_member_required
def error_detail(request, error_id):
    """Detailed view of single error"""
    error = get_object_or_404(ErrorLog, id=error_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'resolve':
            notes = request.POST.get('notes', '')
            error.mark_resolved(request.user, notes)
            return JsonResponse({'status': 'success', 'message': 'Error marked as resolved'})
    
    context = {
        'error': error,
    }
    
    return render(request, 'scheduling/error_detail.html', context)


@staff_member_required
def uptime_history(request):
    """System uptime history view"""
    days = int(request.GET.get('days', 30))
    
    since = timezone.now() - timedelta(days=days)
    uptime_periods = SystemUptime.objects.filter(
        started_at__gte=since
    ).order_by('-started_at')
    
    # Calculate uptime percentages
    uptime_30d = SystemUptime.calculate_uptime_percentage(days=30)
    uptime_7d = SystemUptime.calculate_uptime_percentage(days=7)
    uptime_1d = SystemUptime.calculate_uptime_percentage(days=1)
    
    # Get downtime incidents
    incidents = uptime_periods.filter(
        status__in=['DOWN', 'DEGRADED']
    )
    
    # Calculate total downtime
    total_downtime_seconds = sum(
        (p.duration_seconds or 0) for p in incidents
    )
    total_downtime_hours = total_downtime_seconds / 3600
    
    context = {
        'uptime_periods': uptime_periods,
        'days': days,
        'uptime_30d': round(uptime_30d, 2),
        'uptime_7d': round(uptime_7d, 2),
        'uptime_1d': round(uptime_1d, 2),
        'incidents_count': incidents.count(),
        'total_downtime_hours': round(total_downtime_hours, 2),
        'current_status': SystemUptime.get_current_status(),
    }
    
    return render(request, 'scheduling/uptime_history.html', context)


@staff_member_required
def health_checks_view(request):
    """Health check endpoints management"""
    endpoints = HealthCheckEndpoint.objects.all().order_by('name')
    
    # Get recent results for each endpoint
    for endpoint in endpoints:
        endpoint.recent_results = endpoint.check_results.order_by('-timestamp')[:10]
        
        # Calculate success rate
        total = endpoint.check_results.count()
        if total > 0:
            successful = endpoint.check_results.filter(success=True).count()
            endpoint.success_rate = (successful / total) * 100
        else:
            endpoint.success_rate = 100
    
    context = {
        'endpoints': endpoints,
    }
    
    return render(request, 'scheduling/health_checks.html', context)


@staff_member_required
def run_health_check(request, endpoint_id):
    """Manually trigger health check for endpoint"""
    endpoint = get_object_or_404(HealthCheckEndpoint, id=endpoint_id)
    
    monitor = HealthMonitor()
    result = monitor._check_endpoint(endpoint)
    
    return JsonResponse({
        'status': 'success',
        'result': result,
        'endpoint_status': 'healthy' if endpoint.is_healthy else 'unhealthy',
    })


@staff_member_required
def alert_rules_view(request):
    """Alert rules management"""
    rules = AlertRule.objects.all().order_by('metric', 'severity')
    
    # Get triggered alerts (last 24 hours)
    one_day_ago = timezone.now() - timedelta(days=1)
    recent_triggers = rules.filter(
        last_triggered_at__gte=one_day_ago
    ).order_by('-last_triggered_at')
    
    context = {
        'rules': rules,
        'recent_triggers': recent_triggers,
    }
    
    return render(request, 'scheduling/alert_rules.html', context)


@staff_member_required
def collect_metrics_now(request):
    """Manually trigger metrics collection"""
    monitor = HealthMonitor()
    
    # Collect all metrics
    metrics = monitor.collect_all_metrics()
    
    # Check external services
    service_checks = monitor.check_external_services()
    
    # Check alert rules
    triggered_alerts = monitor.check_alert_rules()
    
    return JsonResponse({
        'status': 'success',
        'metrics_collected': len(metrics),
        'services_checked': len(service_checks),
        'alerts_triggered': len(triggered_alerts),
        'timestamp': timezone.now().isoformat(),
    })


@staff_member_required
def system_info_api(request):
    """API endpoint for system information"""
    import platform
    import sys
    from django import get_version
    
    try:
        import psutil
        
        info = {
            'system': {
                'platform': platform.system(),
                'platform_release': platform.release(),
                'platform_version': platform.version(),
                'architecture': platform.machine(),
                'processor': platform.processor(),
                'python_version': sys.version,
                'django_version': get_version(),
            },
            'resources': {
                'cpu_count': psutil.cpu_count(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_total_mb': round(psutil.virtual_memory().total / 1024 / 1024, 2),
                'memory_available_mb': round(psutil.virtual_memory().available / 1024 / 1024, 2),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_total_gb': round(psutil.disk_usage('/').total / 1024 / 1024 / 1024, 2),
                'disk_used_gb': round(psutil.disk_usage('/').used / 1024 / 1024 / 1024, 2),
                'disk_percent': psutil.disk_usage('/').percent,
            },
        }
    except ImportError:
        info = {
            'error': 'psutil not installed',
            'system': {
                'platform': platform.system(),
                'python_version': sys.version,
                'django_version': get_version(),
            },
        }
    
    return JsonResponse(info)
