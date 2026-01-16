"""
Email notification utilities for compliance violations.

This module handles sending email notifications for compliance violations:
- Critical violation alerts (immediate)
- Daily violation digests (8 AM summary)
- Weekly compliance summaries (Monday 9 AM)
"""

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from scheduling.models import ComplianceViolation, ComplianceCheck, ComplianceRule


def get_notification_recipients():
    """Get list of email addresses for compliance notifications."""
    return getattr(settings, 'COMPLIANCE_NOTIFICATION_EMAILS', [
        'manager@carehome.com',
        'compliance@carehome.com'
    ])


def get_site_url():
    """Get the site URL for email links."""
    return getattr(settings, 'SITE_URL', 'http://localhost:8000')


def send_critical_violation_alert(violation):
    """
    Send immediate email alert for CRITICAL compliance violations.
    
    Args:
        violation: ComplianceViolation instance with severity='CRITICAL'
    
    Returns:
        Number of successfully sent emails
    """
    if violation.severity != 'CRITICAL':
        return 0
    
    subject = f"🚨 CRITICAL Compliance Violation: {violation.rule.name}"
    recipients = get_notification_recipients()
    site_url = get_site_url()
    
    # Prepare context for email template
    context = {
        'violation': violation,
        'site_url': site_url,
        'violation_url': f"{site_url}/audit/violations/{violation.id}/",
        'dashboard_url': f"{site_url}/audit/compliance/",
    }
    
    # Render HTML email
    html_content = render_to_string(
        'scheduling/emails/critical_violation_alert.html',
        context
    )
    
    # Create email message
    email = EmailMultiAlternatives(
        subject=subject,
        body=f"CRITICAL Compliance Violation Detected\n\n{violation.description}\n\nView details: {context['violation_url']}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients
    )
    email.attach_alternative(html_content, "text/html")
    
    # Send email
    try:
        return email.send()
    except Exception as e:
        print(f"Error sending critical violation alert: {e}")
        return 0


def send_daily_violation_digest():
    """
    Send daily email digest of HIGH and MEDIUM violations.
    Intended to run at 8:00 AM daily via cron or Django-Q.
    
    Returns:
        Number of successfully sent emails
    """
    # Get violations from today
    today = timezone.now().date()
    
    violations = ComplianceViolation.objects.filter(
        detected_at__date=today,
        severity__in=['HIGH', 'MEDIUM'],
        status__in=['OPEN', 'ACKNOWLEDGED']
    ).select_related('rule', 'compliance_check').order_by('-severity', '-detected_at')
    
    # Skip if no violations
    if not violations.exists():
        print(f"No HIGH/MEDIUM violations detected today ({today}). Skipping daily digest.")
        return 0
    
    # Separate by severity
    high_violations = violations.filter(severity='HIGH')
    medium_violations = violations.filter(severity='MEDIUM')
    
    subject = f"Daily Compliance Digest - {today.strftime('%d %B %Y')}"
    recipients = get_notification_recipients()
    site_url = get_site_url()
    
    # Prepare context
    context = {
        'date': today,
        'violations': violations,
        'high_violations': high_violations,
        'medium_violations': medium_violations,
        'total_count': violations.count(),
        'high_count': high_violations.count(),
        'medium_count': medium_violations.count(),
        'open_count': violations.filter(status='OPEN').count(),
        'site_url': site_url,
        'violations_url': f"{site_url}/audit/violations/",
        'dashboard_url': f"{site_url}/audit/compliance/",
    }
    
    # Render HTML email
    html_content = render_to_string(
        'scheduling/emails/daily_violation_digest.html',
        context
    )
    
    # Plain text version
    text_content = f"""Daily Compliance Violation Digest
Date: {today.strftime('%d %B %Y')}

Summary:
- Total violations: {context['total_count']}
- HIGH priority: {context['high_count']}
- MEDIUM priority: {context['medium_count']}
- Open violations: {context['open_count']}

View all violations: {context['violations_url']}
"""
    
    # Create email
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients
    )
    email.attach_alternative(html_content, "text/html")
    
    # Send email
    try:
        sent = email.send()
        print(f"Sent daily digest with {violations.count()} violations to {len(recipients)} recipients")
        return sent
    except Exception as e:
        print(f"Error sending daily violation digest: {e}")
        return 0


def send_weekly_compliance_summary():
    """
    Send weekly compliance summary email with metrics and trends.
    Intended to run every Monday at 9:00 AM via cron or Django-Q.
    
    Returns:
        Number of successfully sent emails
    """
    # Get last 7 days
    today = timezone.now().date()
    week_start = today - timedelta(days=7)
    
    # Get checks and violations from past week
    checks = ComplianceCheck.objects.filter(
        checked_at__date__gte=week_start,
        checked_at__date__lte=today
    )
    
    violations = ComplianceViolation.objects.filter(
        detected_at__date__gte=week_start,
        detected_at__date__lte=today
    ).select_related('rule', 'compliance_check')
    
    # Calculate metrics
    total_checks = checks.count()
    total_violations = violations.count()
    resolved_violations = violations.filter(status='RESOLVED').count()
    open_violations = violations.filter(status__in=['OPEN', 'ACKNOWLEDGED', 'IN_PROGRESS']).count()
    
    # Calculate compliance rate
    if total_checks > 0:
        compliance_rate = ((total_checks - total_violations) / total_checks) * 100
    else:
        compliance_rate = 100.0
    
    # Violations by category
    violations_by_category = {}
    for violation in violations:
        category = violation.rule.category
        if category not in violations_by_category:
            violations_by_category[category] = 0
        violations_by_category[category] += 1
    
    # Top violated rules
    top_rules = {}
    for violation in violations:
        rule_name = violation.rule.name
        if rule_name not in top_rules:
            top_rules[rule_name] = 0
        top_rules[rule_name] += 1
    
    # Sort and limit
    top_rules = sorted(top_rules.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Generate action items
    action_items = generate_action_items(violations)
    
    subject = f"Weekly Compliance Summary - {week_start.strftime('%d %b')} to {today.strftime('%d %b %Y')}"
    recipients = get_notification_recipients()
    site_url = get_site_url()
    
    # Prepare context
    context = {
        'week_start': week_start,
        'week_end': today,
        'total_checks': total_checks,
        'total_violations': total_violations,
        'resolved_violations': resolved_violations,
        'open_violations': open_violations,
        'compliance_rate': round(compliance_rate, 1),
        'violations_by_category': violations_by_category,
        'top_rules': top_rules,
        'action_items': action_items,
        'site_url': site_url,
        'dashboard_url': f"{site_url}/audit/compliance/",
        'violations_url': f"{site_url}/audit/violations/",
        'reports_url': f"{site_url}/audit/reports/",
    }
    
    # Render HTML email
    html_content = render_to_string(
        'scheduling/emails/weekly_compliance_summary.html',
        context
    )
    
    # Plain text version
    text_content = f"""Weekly Compliance Summary
Period: {week_start.strftime('%d %b')} to {today.strftime('%d %b %Y')}

Key Metrics:
- Compliance Rate: {compliance_rate:.1f}%
- Total Checks: {total_checks}
- Total Violations: {total_violations}
- Resolved: {resolved_violations}
- Still Open: {open_violations}

View full dashboard: {context['dashboard_url']}
"""
    
    # Create email
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients
    )
    email.attach_alternative(html_content, "text/html")
    
    # Send email
    try:
        sent = email.send()
        print(f"Sent weekly summary: {total_violations} violations, {compliance_rate:.1f}% compliance rate")
        return sent
    except Exception as e:
        print(f"Error sending weekly compliance summary: {e}")
        return 0


def generate_action_items(violations):
    """
    Generate smart action items based on violation patterns.
    
    Args:
        violations: QuerySet of ComplianceViolation instances
    
    Returns:
        List of action item strings
    """
    action_items = []
    
    # Count violations by category
    wtd_violations = violations.filter(rule__category='WORKING_TIME_DIRECTIVE').count()
    staffing_violations = violations.filter(rule__category='STAFFING_LEVELS').count()
    
    # Working Time Directive violations
    if wtd_violations > 5:
        action_items.append(
            "Review scheduling patterns - multiple Working Time Directive violations detected. "
            "Check weekly hour allocations and rest period compliance."
        )
    
    # Staffing level violations
    if staffing_violations > 0:
        action_items.append(
            "Address staffing shortfalls urgently - understaffing impacts resident safety and care quality. "
            "Review leave approvals and consider temporary agency staff."
        )
    
    # Long-standing open violations
    old_open = violations.filter(
        status='OPEN',
        detected_at__lte=timezone.now() - timedelta(days=3)
    ).count()
    
    if old_open > 0:
        action_items.append(
            f"{old_open} violation(s) have been open for 3+ days. "
            "Review and update status, or escalate if resolution is blocked."
        )
    
    # Critical violations still open
    critical_open = violations.filter(severity='CRITICAL', status='OPEN').count()
    if critical_open > 0:
        action_items.append(
            f"URGENT: {critical_open} CRITICAL violation(s) still open. "
            "These require immediate attention and resolution."
        )
    
    # Default message if no specific actions needed
    if not action_items:
        action_items.append(
            "Continue monitoring compliance checks and addressing violations promptly. "
            "Maintain current good practices."
        )
    
    return action_items
