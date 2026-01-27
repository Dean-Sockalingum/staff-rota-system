"""
Audit Trail Dashboard Views
Views for audit logging, compliance monitoring, and activity tracking
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Count, Q
from django.core.paginator import Paginator
from datetime import timedelta, datetime
import csv
import json

from .models_audit import (
    DataChangeLog, SystemAccessLog, ComplianceCheck,
    ComplianceViolation, ComplianceRule, AuditReport
)
from .audit_service import AuditService


@staff_member_required
def audit_dashboard(request):
    """Main audit trail dashboard"""
    
    # Get date range from query params (default: last 7 days)
    days = int(request.GET.get('days', 7))
    since = timezone.now() - timedelta(days=days)
    
    # Get recent activity
    data_changes = DataChangeLog.objects.filter(timestamp__gte=since)
    access_logs = SystemAccessLog.objects.filter(timestamp__gte=since)
    
    # Summary statistics
    stats = {
        'total_data_changes': data_changes.count(),
        'total_access_events': access_logs.count(),
        'unique_users': data_changes.values('user').distinct().count(),
        'failed_logins': access_logs.filter(access_type='LOGIN_FAILED').count(),
    }
    
    # Changes by action
    changes_by_action = dict(
        data_changes.values('action').annotate(
            count=Count('id')
        ).values_list('action', 'count')
    )
    
    # Access by type
    access_by_type = dict(
        access_logs.values('access_type').annotate(
            count=Count('id')
        ).values_list('access_type', 'count')
    )
    
    # Most active users
    most_active_users = data_changes.values(
        'user__username', 'user__first_name', 'user__last_name'
    ).annotate(
        change_count=Count('id')
    ).order_by('-change_count')[:10]
    
    # Recent suspicious activity
    suspicious_activity = AuditService.detect_suspicious_activity(hours=24*days)
    
    # Recent compliance violations
    recent_violations = ComplianceViolation.objects.filter(
        status='OPEN'
    ).order_by('-detected_at')[:10]
    
    # Recent data changes
    recent_changes = data_changes.order_by('-timestamp')[:20]
    
    # Recent access events
    recent_access = access_logs.order_by('-timestamp')[:20]
    
    context = {
        'days': days,
        'stats': stats,
        'changes_by_action': changes_by_action,
        'access_by_type': access_by_type,
        'most_active_users': most_active_users,
        'suspicious_activity': suspicious_activity,
        'recent_violations': recent_violations,
        'recent_changes': recent_changes,
        'recent_access': recent_access,
    }
    
    return render(request, 'scheduling/audit_dashboard.html', context)


@staff_member_required
def data_changes_log(request):
    """View data change logs with filtering"""
    
    # Get filters
    user_id = request.GET.get('user')
    action = request.GET.get('action')
    days = int(request.GET.get('days', 30))
    search = request.GET.get('search', '')
    
    since = timezone.now() - timedelta(days=days)
    logs = DataChangeLog.objects.filter(timestamp__gte=since)
    
    # Apply filters
    if user_id:
        logs = logs.filter(user_id=user_id)
    if action:
        logs = logs.filter(action=action)
    if search:
        logs = logs.filter(
            Q(field_name__icontains=search) |
            Q(old_value__icontains=search) |
            Q(new_value__icontains=search) |
            Q(reason__icontains=search)
        )
    
    logs = logs.order_by('-timestamp').select_related('user', 'content_type')
    
    # Pagination
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get unique users for filter dropdown
    from django.contrib.auth import get_user_model
    User = get_user_model()
    users = User.objects.filter(
        id__in=DataChangeLog.objects.values('user').distinct()
    ).order_by('username')
    
    context = {
        'logs': page_obj,
        'users': users,
        'filters': {
            'user_id': user_id,
            'action': action,
            'days': days,
            'search': search,
        },
        'action_choices': DataChangeLog.ACTION_CHOICES,
    }
    
    return render(request, 'scheduling/data_changes_log.html', context)


@staff_member_required
def access_log_view(request):
    """View system access logs"""
    
    # Get filters
    user_id = request.GET.get('user')
    access_type = request.GET.get('access_type')
    success = request.GET.get('success', '')
    days = int(request.GET.get('days', 30))
    
    since = timezone.now() - timedelta(days=days)
    logs = SystemAccessLog.objects.filter(timestamp__gte=since)
    
    # Apply filters
    if user_id:
        logs = logs.filter(user_id=user_id)
    if access_type:
        logs = logs.filter(access_type=access_type)
    if success == 'true':
        logs = logs.filter(success=True)
    elif success == 'false':
        logs = logs.filter(success=False)
    
    logs = logs.order_by('-timestamp').select_related('user')
    
    # Pagination
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    stats = {
        'total': logs.count(),
        'successful': logs.filter(success=True).count(),
        'failed': logs.filter(success=False).count(),
        'unique_ips': logs.values('ip_address').distinct().count(),
    }
    
    # Get unique users for filter dropdown
    from django.contrib.auth import get_user_model
    User = get_user_model()
    users = User.objects.filter(
        id__in=SystemAccessLog.objects.values('user').distinct()
    ).order_by('username')
    
    context = {
        'logs': page_obj,
        'users': users,
        'stats': stats,
        'filters': {
            'user_id': user_id,
            'access_type': access_type,
            'success': success,
            'days': days,
        },
        'access_type_choices': SystemAccessLog.ACCESS_TYPE_CHOICES,
    }
    
    return render(request, 'scheduling/access_log.html', context)


@staff_member_required
def user_activity_view(request, user_id):
    """View all activity for a specific user"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    user = get_object_or_404(User, id=user_id)
    
    # Get date range
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    activity = AuditService.get_user_activity(
        user=user,
        start_date=start_date
    )
    
    # Combine and sort all activity
    all_activity = []
    
    for change in activity['data_changes']:
        all_activity.append({
            'type': 'data_change',
            'timestamp': change.timestamp,
            'description': f"{change.action} {change.content_type.model}",
            'details': change,
        })
    
    for access in activity['access_logs']:
        all_activity.append({
            'type': 'access',
            'timestamp': access.timestamp,
            'description': access.access_type,
            'details': access,
        })
    
    all_activity.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Pagination
    paginator = Paginator(all_activity, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'target_user': user,
        'activity': page_obj,
        'stats': {
            'total_changes': activity['total_changes'],
            'total_accesses': activity['total_accesses'],
        },
        'days': days,
    }
    
    return render(request, 'scheduling/user_activity.html', context)


@staff_member_required
def object_history_view(request):
    """View change history for a specific object"""
    from django.contrib.contenttypes.models import ContentType
    
    content_type_id = request.GET.get('content_type')
    object_id = request.GET.get('object_id')
    
    if not content_type_id or not object_id:
        return render(request, 'scheduling/object_history.html', {
            'error': 'Missing content_type or object_id parameter'
        })
    
    content_type = get_object_or_404(ContentType, id=content_type_id)
    
    # Get change history
    history = DataChangeLog.objects.filter(
        content_type=content_type,
        object_id=object_id
    ).order_by('-timestamp').select_related('user')
    
    # Try to get the object
    try:
        obj = content_type.get_object_for_this_type(pk=object_id)
    except:
        obj = None
    
    context = {
        'content_type': content_type,
        'object_id': object_id,
        'object': obj,
        'history': history,
    }
    
    return render(request, 'scheduling/object_history.html', context)


@staff_member_required
def compliance_dashboard(request):
    """Compliance monitoring dashboard"""
    
    # Get active rules
    active_rules = ComplianceRule.objects.filter(is_active=True)
    
    # Recent checks
    recent_checks = ComplianceCheck.objects.order_by('-started_at')[:20]
    
    # Open violations by severity
    violations = ComplianceViolation.objects.filter(status='OPEN')
    violations_by_severity = dict(
        violations.values('severity').annotate(
            count=Count('id')
        ).values_list('severity', 'count')
    )
    
    # Critical violations
    critical_violations = violations.filter(
        severity='CRITICAL'
    ).order_by('-detected_at')[:10]
    
    # Compliance trends (last 30 days)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    checks_by_day = ComplianceCheck.objects.filter(
        check_date__gte=thirty_days_ago
    ).values('check_date').annotate(
        total_checks=Count('id'),
        total_violations=Count('violations')
    ).order_by('check_date')
    
    context = {
        'active_rules': active_rules,
        'recent_checks': recent_checks,
        'violations_by_severity': violations_by_severity,
        'critical_violations': critical_violations,
        'checks_by_day': list(checks_by_day),
        'total_open_violations': violations.count(),
    }
    
    return render(request, 'scheduling/compliance_dashboard.html', context)


@staff_member_required
def compliance_violations_view(request):
    """View and manage compliance violations"""
    
    # Filters
    status = request.GET.get('status', 'OPEN')
    severity = request.GET.get('severity', '')
    rule_id = request.GET.get('rule')
    
    violations = ComplianceViolation.objects.all()
    
    if status:
        violations = violations.filter(status=status)
    if severity:
        violations = violations.filter(severity=severity)
    if rule_id:
        violations = violations.filter(rule_id=rule_id)
    
    violations = violations.order_by('-detected_at').select_related(
        'rule', 'affected_user', 'compliance_check'
    )
    
    # Pagination
    paginator = Paginator(violations, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get all rules for filter
    rules = ComplianceRule.objects.filter(is_active=True)
    
    context = {
        'violations': page_obj,
        'rules': rules,
        'filters': {
            'status': status,
            'severity': severity,
            'rule_id': rule_id,
        },
        'status_choices': ComplianceViolation.STATUS_CHOICES,
        'severity_choices': ComplianceRule.SEVERITY_CHOICES,
    }
    
    return render(request, 'scheduling/compliance_violations.html', context)


@staff_member_required
def acknowledge_violation(request, violation_id):
    """Acknowledge a compliance violation"""
    violation = get_object_or_404(ComplianceViolation, id=violation_id)
    
    if request.method == 'POST':
        violation.status = 'ACKNOWLEDGED'
        violation.acknowledged_at = timezone.now()
        violation.acknowledged_by = request.user
        violation.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Violation acknowledged'
        })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@staff_member_required
def resolve_violation(request, violation_id):
    """Resolve a compliance violation"""
    violation = get_object_or_404(ComplianceViolation, id=violation_id)
    
    if request.method == 'POST':
        resolution_notes = request.POST.get('resolution_notes', '')
        
        violation.status = 'RESOLVED'
        violation.resolved_at = timezone.now()
        violation.resolved_by = request.user
        violation.resolution_notes = resolution_notes
        violation.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Violation resolved'
        })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@staff_member_required
def generate_audit_report_view(request):
    """Generate an audit report"""
    
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        start_date = datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.POST.get('end_date'), '%Y-%m-%d').date()
        
        # Optional filters
        filters = {}
        if request.POST.get('user_id'):
            filters['user_id'] = request.POST.get('user_id')
        if request.POST.get('action'):
            filters['action'] = request.POST.get('action')
        
        # Generate report
        report = AuditService.generate_activity_report(
            start_date=start_date,
            end_date=end_date,
            report_type=report_type,
            user=request.user,
            filters=filters
        )
        
        return JsonResponse({
            'status': 'success',
            'report_id': report.id,
            'message': 'Report generated successfully'
        })
    
    # GET - show form
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    context = {
        'report_types': AuditReport.REPORT_TYPE_CHOICES,
        'users': User.objects.all().order_by('username'),
        'actions': DataChangeLog.ACTION_CHOICES,
    }
    
    return render(request, 'scheduling/generate_audit_report.html', context)


@staff_member_required
def audit_reports_list(request):
    """List all generated audit reports"""
    
    reports = AuditReport.objects.order_by('-generated_at')
    
    # Pagination
    paginator = Paginator(reports, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'reports': page_obj,
    }
    
    return render(request, 'scheduling/audit_reports_list.html', context)


@staff_member_required
def view_audit_report(request, report_id):
    """View a specific audit report"""
    
    report = get_object_or_404(AuditReport, id=report_id)
    
    context = {
        'report': report,
    }
    
    return render(request, 'scheduling/view_audit_report.html', context)


@staff_member_required
def export_audit_data(request):
    """Export audit data to CSV"""
    
    export_type = request.GET.get('type', 'data_changes')
    days = int(request.GET.get('days', 30))
    since = timezone.now() - timedelta(days=days)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="audit_{export_type}_{timezone.now().date()}.csv"'
    
    writer = csv.writer(response)
    
    if export_type == 'data_changes':
        writer.writerow(['Timestamp', 'User', 'Action', 'Object Type', 'Object ID', 
                        'Field', 'Old Value', 'New Value', 'IP Address'])
        
        logs = DataChangeLog.objects.filter(timestamp__gte=since).select_related('user', 'content_type')
        
        for log in logs:
            writer.writerow([
                log.timestamp,
                log.user.username if log.user else 'Unknown',
                log.action,
                log.content_type.model if log.content_type else 'N/A',
                log.object_id,
                log.field_name or '',
                log.old_value or '',
                log.new_value or '',
                log.ip_address or '',
            ])
    
    elif export_type == 'access_logs':
        writer.writerow(['Timestamp', 'User', 'Access Type', 'IP Address', 
                        'Success', 'Failure Reason'])
        
        logs = SystemAccessLog.objects.filter(timestamp__gte=since).select_related('user')
        
        for log in logs:
            writer.writerow([
                log.timestamp,
                log.user.username if log.user else log.username_attempt,
                log.access_type,
                log.ip_address,
                'Yes' if log.success else 'No',
                log.failure_reason or '',
            ])
    
    return response


@staff_member_required
def suspicious_activity_api(request):
    """API endpoint for suspicious activity detection"""
    
    hours = int(request.GET.get('hours', 24))
    findings = AuditService.detect_suspicious_activity(hours=hours)
    
    return JsonResponse({
        'findings': findings,
        'count': len(findings),
        'period_hours': hours,
    })
