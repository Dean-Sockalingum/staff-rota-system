"""
Email notification utilities for compliance violations
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from datetime import date


def send_compliance_violation_alert(violation):
    """Send email alert for a single compliance violation"""
    
    subject = f'🚨 Compliance Violation: {violation.rule.name}'
    
    context = {
        'violation': violation,
        'severity_emoji': {
            'CRITICAL': '🔴',
            'HIGH': '🟠',
            'MEDIUM': '🟡',
            'LOW': '🟢',
            'INFO': 'ℹ️'
        }.get(violation.severity, '⚠️'),
        'dashboard_url': f'{getattr(settings, "SITE_URL", "http://localhost:8000")}/management/compliance-dashboard/',
    }
    
    # Plain text version
    message = f"""
Compliance Violation Detected
{'=' * 60}

Rule: {violation.rule.name} ({violation.rule.code})
Severity: {violation.severity}
Detected: {violation.detected_at.strftime('%d/%m/%Y %H:%M')}

Description:
{violation.description}

Remediation Steps:
{violation.rule.remediation_steps}

View Details:
{context['dashboard_url']}

This is an automated notification from the Staff Rota System.
"""
    
    # Get recipients
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    recipients = list(User.objects.filter(
        is_active=True,
        is_superuser=True,
        email__isnull=False
    ).exclude(email='').values_list('email', flat=True))
    
    if recipients:
        try:
            send_mail(
                subject=subject,
                message=message.strip(),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Failed to send compliance violation email: {e}")
            return False
    return False


def send_weekly_compliance_report(start_date, end_date):
    """Send weekly compliance summary report"""
    from scheduling.models import ComplianceCheck, ComplianceViolation
    
    # Get data for the week
    checks = ComplianceCheck.objects.filter(
        check_date__gte=start_date,
        check_date__lte=end_date
    ).select_related('rule')
    
    violations = ComplianceViolation.objects.filter(
        detected_at__date__gte=start_date,
        detected_at__date__lte=end_date
    ).select_related('rule', 'affected_user')
    
    # Count by severity
    severity_counts = {
        'CRITICAL': violations.filter(severity='CRITICAL').count(),
        'HIGH': violations.filter(severity='HIGH').count(),
        'MEDIUM': violations.filter(severity='MEDIUM').count(),
        'LOW': violations.filter(severity='LOW').count(),
    }
    
    # Count by status
    status_counts = {
        'OPEN': violations.filter(status='OPEN').count(),
        'ACKNOWLEDGED': violations.filter(status='ACKNOWLEDGED').count(),
        'IN_PROGRESS': violations.filter(status='IN_PROGRESS').count(),
        'RESOLVED': violations.filter(status='RESOLVED').count(),
    }
    
    subject = f'📊 Weekly Compliance Report - {start_date.strftime("%d/%m/%Y")} to {end_date.strftime("%d/%m/%Y")}'
    
    message_lines = [
        'Weekly Compliance Summary Report',
        '=' * 60,
        f'Period: {start_date.strftime("%d/%m/%Y")} to {end_date.strftime("%d/%m/%Y")}',
        '',
        '📋 Compliance Checks Performed:',
        f'   Total Checks: {checks.count()}',
        f'   Completed: {checks.filter(status="COMPLETED").count()}',
        f'   Failed: {checks.filter(status="FAILED").count()}',
        '',
        '⚠️  Violations Summary:',
        f'   Total Violations: {violations.count()}',
        '',
        '   By Severity:',
        f'   🔴 Critical: {severity_counts["CRITICAL"]}',
        f'   🟠 High: {severity_counts["HIGH"]}',
        f'   🟡 Medium: {severity_counts["MEDIUM"]}',
        f'   🟢 Low: {severity_counts["LOW"]}',
        '',
        '   By Status:',
        f'   Open: {status_counts["OPEN"]}',
        f'   Acknowledged: {status_counts["ACKNOWLEDGED"]}',
        f'   In Progress: {status_counts["IN_PROGRESS"]}',
        f'   Resolved: {status_counts["RESOLVED"]}',
        '',
    ]
    
    # Add top violations
    if violations.exists():
        message_lines.extend([
            '🔝 Top Violations:',
            '-' * 60,
        ])
        
        for v in violations.order_by('-severity', '-detected_at')[:5]:
            message_lines.append(f'• [{v.severity}] {v.rule.name}')
            message_lines.append(f'  {v.description[:80]}...' if len(v.description) > 80 else f'  {v.description}')
            message_lines.append('')
    
    message_lines.extend([
        '',
        'View Full Dashboard:',
        f'{getattr(settings, "SITE_URL", "http://localhost:8000")}/management/compliance-dashboard/',
        '',
        'This is an automated weekly report from the Staff Rota System.',
    ])
    
    message = '\n'.join(message_lines)
    
    # Get recipients
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    recipients = list(User.objects.filter(
        is_active=True,
        is_superuser=True,
        email__isnull=False
    ).exclude(email='').values_list('email', flat=True))
    
    if recipients:
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Failed to send weekly compliance report: {e}")
            return False
    return False
