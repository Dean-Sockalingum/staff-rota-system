"""
Helper functions for generating audit report data.
These functions populate the report_data JSON field for different report types.
"""
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict
import json

from scheduling.models import Shift, User, LeaveRequest, ShiftSwapRequest
from scheduling.models_audit import (
    DataChangeLog, SystemAccessLog, ComplianceViolation, 
    ComplianceCheck, ComplianceRule
)


def generate_daily_activity_report(start_date, end_date):
    """
    Generate daily activity report showing all changes in the last 24 hours.
    Returns dict with change counts by action type, user, and model.
    """
    changes = DataChangeLog.objects.filter(
        timestamp__gte=start_date,
        timestamp__lte=end_date
    )
    
    # Aggregate by action type
    by_action = changes.values('action').annotate(count=Count('id'))
    action_counts = {item['action']: item['count'] for item in by_action}
    
    # Aggregate by user
    by_user = changes.values('user__sap', 'user__first_name', 'user__last_name').annotate(count=Count('id')).order_by('-count')[:10]
    top_users = [
        {
            'sap': item['user__sap'],
            'name': f"{item['user__first_name']} {item['user__last_name']}",
            'changes': item['count']
        }
        for item in by_user
    ]
    
    # Aggregate by model type
    by_model = changes.values('content_type__model').annotate(count=Count('id')).order_by('-count')
    model_counts = {item['content_type__model']: item['count'] for item in by_model}
    
    return {
        'total_changes': changes.count(),
        'period': f"{start_date.strftime('%Y-%m-%d %H:%M')} to {end_date.strftime('%Y-%m-%d %H:%M')}",
        'by_action': action_counts,
        'top_users': top_users,
        'by_model': model_counts,
        'generated_at': timezone.now().isoformat()
    }


def generate_weekly_summary_report(start_date, end_date):
    """
    Generate weekly summary with stats for past 7 days.
    Includes changes, access events, violations.
    """
    # Changes
    changes = DataChangeLog.objects.filter(
        timestamp__gte=start_date,
        timestamp__lte=end_date
    )
    
    # Access events
    access_events = SystemAccessLog.objects.filter(
        timestamp__gte=start_date,
        timestamp__lte=end_date
    )
    
    # Violations
    violations = ComplianceViolation.objects.filter(
        detected_at__gte=start_date,
        detected_at__lte=end_date
    )
    
    # Daily breakdown
    daily_stats = []
    current = start_date.date()
    while current <= end_date.date():
        day_start = timezone.make_aware(timezone.datetime.combine(current, timezone.datetime.min.time()))
        day_end = timezone.make_aware(timezone.datetime.combine(current, timezone.datetime.max.time()))
        
        daily_stats.append({
            'date': current.isoformat(),
            'changes': changes.filter(timestamp__gte=day_start, timestamp__lte=day_end).count(),
            'logins': access_events.filter(timestamp__gte=day_start, timestamp__lte=day_end, access_type='LOGIN').count(),
            'violations': violations.filter(detected_at__gte=day_start, detected_at__lte=day_end).count()
        })
        current += timedelta(days=1)
    
    return {
        'period': f"{start_date.date()} to {end_date.date()}",
        'summary': {
            'total_changes': changes.count(),
            'total_access_events': access_events.count(),
            'total_violations': violations.count(),
            'unique_users': changes.values('user').distinct().count()
        },
        'daily_breakdown': daily_stats,
        'top_changed_models': list(
            changes.values('content_type__model')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        ),
        'generated_at': timezone.now().isoformat()
    }


def generate_monthly_compliance_report(start_date, end_date):
    """
    Generate monthly compliance report with all compliance check results.
    """
    # Get all checks in period
    checks = ComplianceCheck.objects.filter(
        check_date__gte=start_date.date(),
        check_date__lte=end_date.date()
    )
    
    # Get all violations
    violations = ComplianceViolation.objects.filter(
        detected_at__gte=start_date,
        detected_at__lte=end_date
    )
    
    # Aggregate by rule category
    by_category = violations.values('rule__category').annotate(count=Count('id'))
    category_counts = {item['rule__category']: item['count'] for item in by_category}
    
    # Aggregate by severity
    by_severity = violations.values('severity').annotate(count=Count('id'))
    severity_counts = {item['severity']: item['count'] for item in by_severity}
    
    # Aggregate by status
    by_status = violations.values('status').annotate(count=Count('id'))
    status_counts = {item['status']: item['count'] for item in by_status}
    
    # Top violated rules
    top_rules = violations.values(
        'rule__code', 'rule__name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    return {
        'period': f"{start_date.date()} to {end_date.date()}",
        'summary': {
            'total_checks': checks.count(),
            'total_violations': violations.count(),
            'open_violations': violations.filter(status='OPEN').count(),
            'resolved_violations': violations.filter(status='RESOLVED').count()
        },
        'by_category': category_counts,
        'by_severity': severity_counts,
        'by_status': status_counts,
        'top_violated_rules': list(top_rules),
        'compliance_rate': round(
            ((checks.count() - violations.count()) / checks.count() * 100) if checks.count() > 0 else 100,
            2
        ),
        'generated_at': timezone.now().isoformat()
    }


def generate_user_activity_report(start_date, end_date, user_id=None):
    """
    Generate user activity report showing all changes made by specific user or all users.
    """
    changes = DataChangeLog.objects.filter(
        timestamp__gte=start_date,
        timestamp__lte=end_date
    )
    
    if user_id:
        changes = changes.filter(user_id=user_id)
    
    # Group by user
    by_user = changes.values(
        'user__sap', 'user__first_name', 'user__last_name'
    ).annotate(
        total_changes=Count('id'),
        creates=Count('id', filter=Q(action='CREATE')),
        updates=Count('id', filter=Q(action='UPDATE')),
        deletes=Count('id', filter=Q(action='DELETE'))
    ).order_by('-total_changes')
    
    return {
        'period': f"{start_date.date()} to {end_date.date()}",
        'total_changes': changes.count(),
        'users': list(by_user),
        'generated_at': timezone.now().isoformat()
    }


def generate_data_changes_report(start_date, end_date, model_type=None):
    """
    Export all changes in period with full details.
    """
    changes = DataChangeLog.objects.filter(
        timestamp__gte=start_date,
        timestamp__lte=end_date
    ).select_related('user', 'content_type')
    
    if model_type:
        changes = changes.filter(content_type__model=model_type)
    
    change_list = []
    for change in changes[:1000]:  # Limit to 1000 for performance
        change_list.append({
            'timestamp': change.timestamp.isoformat(),
            'user': change.user.sap if change.user else 'System',
            'action': change.action,
            'model': change.content_type.model,
            'object_id': change.object_id,
            'field': change.field_name,
            'old_value': change.old_value[:100] if change.old_value else '',
            'new_value': change.new_value[:100] if change.new_value else '',
        })
    
    return {
        'period': f"{start_date.date()} to {end_date.date()}",
        'total_changes': changes.count(),
        'changes': change_list,
        'truncated': changes.count() > 1000,
        'generated_at': timezone.now().isoformat()
    }


def generate_compliance_violations_report(start_date, end_date, severity=None, status=None):
    """
    Generate report of compliance violations with filters.
    """
    violations = ComplianceViolation.objects.filter(
        detected_at__gte=start_date,
        detected_at__lte=end_date
    ).select_related('rule', 'affected_user')
    
    if severity:
        violations = violations.filter(severity=severity)
    if status:
        violations = violations.filter(status=status)
    
    violation_list = []
    for v in violations[:500]:  # Limit to 500
        violation_list.append({
            'detected_at': v.detected_at.isoformat(),
            'rule': v.rule.name,
            'severity': v.severity,
            'status': v.status,
            'affected_user': v.affected_user.sap if v.affected_user else 'N/A',
            'description': v.description
        })
    
    return {
        'period': f"{start_date.date()} to {end_date.date()}",
        'filters': {
            'severity': severity,
            'status': status
        },
        'total_violations': violations.count(),
        'violations': violation_list,
        'truncated': violations.count() > 500,
        'generated_at': timezone.now().isoformat()
    }


def generate_shift_audit_report(start_date, end_date):
    """
    Generate shift audit report showing allocations, swaps, cancellations.
    """
    # Shift changes
    shift_changes = DataChangeLog.objects.filter(
        timestamp__gte=start_date,
        timestamp__lte=end_date,
        content_type__model='shift'
    )
    
    # Shift swaps
    swaps = ShiftSwapRequest.objects.filter(
        created_at__gte=start_date,
        created_at__lte=end_date
    )
    
    # Actual shifts in period
    shifts = Shift.objects.filter(
        date__gte=start_date.date(),
        date__lte=end_date.date()
    )
    
    return {
        'period': f"{start_date.date()} to {end_date.date()}",
        'summary': {
            'total_shifts': shifts.count(),
            'shift_changes': shift_changes.count(),
            'swap_requests': swaps.count(),
            'approved_swaps': swaps.filter(status='APPROVED').count(),
            'cancelled_swaps': swaps.filter(status='CANCELLED').count()
        },
        'by_shift_type': list(
            shifts.values('shift_type__name').annotate(count=Count('id'))
        ),
        'by_unit': list(
            shifts.values('unit__name').annotate(count=Count('id')).order_by('-count')
        ),
        'generated_at': timezone.now().isoformat()
    }


def generate_leave_audit_report(start_date, end_date):
    """
    Generate leave audit report showing requests, approvals, cancellations.
    """
    leave_requests = LeaveRequest.objects.filter(
        created_at__gte=start_date,
        created_at__lte=end_date
    )
    
    return {
        'period': f"{start_date.date()} to {end_date.date()}",
        'summary': {
            'total_requests': leave_requests.count(),
            'approved': leave_requests.filter(status='APPROVED').count(),
            'pending': leave_requests.filter(status='PENDING').count(),
            'denied': leave_requests.filter(status='DENIED').count(),
            'cancelled': leave_requests.filter(status='CANCELLED').count()
        },
        'by_user': list(
            leave_requests.values('user__sap', 'user__first_name', 'user__last_name')
            .annotate(count=Count('id'))
            .order_by('-count')[:20]
        ),
        'total_days_requested': sum([
            (lr.end_date - lr.start_date).days + 1 
            for lr in leave_requests
        ]),
        'generated_at': timezone.now().isoformat()
    }


def generate_annual_leave_report(start_date, end_date):
    """
    Generate annual leave entitlement report showing balances, usage, and remaining hours.
    This uses the AnnualLeaveEntitlement and AnnualLeaveTransaction models.
    """
    from staff_records.models import AnnualLeaveEntitlement, AnnualLeaveTransaction
    from decimal import Decimal
    
    # Get all current entitlements
    entitlements = AnnualLeaveEntitlement.objects.select_related(
        'profile__user'
    ).all()
    
    # Calculate summary statistics
    total_staff = entitlements.count()
    total_entitlement = sum(e.total_entitlement_hours for e in entitlements)
    total_used = sum(e.hours_used for e in entitlements)
    total_pending = sum(e.hours_pending for e in entitlements)
    total_remaining = sum(e.hours_remaining for e in entitlements)
    total_carryover = sum(e.carryover_hours for e in entitlements)
    
    # Staff by contract type
    staff_35hr = entitlements.filter(contracted_hours_per_week=Decimal('34.5')).count()
    staff_24hr = entitlements.filter(contracted_hours_per_week=Decimal('23.0')).count()
    
    # Breakdown by usage
    staff_by_usage = []
    for ent in entitlements:
        usage_percentage = (ent.hours_used / ent.total_entitlement_hours * 100) if ent.total_entitlement_hours > 0 else 0
        
        # Calculate days_pending manually using 12-hour shift logic
        # 35hr staff (34.5 actual) work 11.66 hrs/day, 24hr staff (23.0 actual) work 12 hrs/day
        hours_per_day = Decimal('11.66') if ent.contracted_hours_per_week >= Decimal('30.00') else Decimal('12.00')
        days_pending = (ent.hours_pending / hours_per_day) if hours_per_day > 0 else Decimal('0.00')
        
        staff_by_usage.append({
            'sap': ent.profile.user.sap,
            'name': ent.profile.user.full_name,
            'total_hours': float(ent.total_entitlement_hours),
            'total_days': float(ent.days_entitlement),
            'used_hours': float(ent.hours_used),
            'used_days': float(ent.days_used),
            'pending_hours': float(ent.hours_pending),
            'pending_days': float(days_pending),
            'remaining_hours': float(ent.hours_remaining),
            'remaining_days': float(ent.days_remaining),
            'carryover_hours': float(ent.carryover_hours),
            'usage_percentage': round(usage_percentage, 1),
            'leave_year': f"{ent.leave_year_start} to {ent.leave_year_end}"
        })
    
    # Sort by usage percentage (descending)
    staff_by_usage.sort(key=lambda x: x['usage_percentage'], reverse=True)
    
    # Get transactions in the period
    transactions = AnnualLeaveTransaction.objects.filter(
        created_at__gte=start_date,
        created_at__lte=end_date
    ).select_related('entitlement__profile__user')
    
    transaction_list = []
    for txn in transactions[:100]:  # Limit to 100 most recent
        # Calculate days from hours using 12-hour shift logic
        # 35hr staff (34.5 actual) work 11.66 hrs/day, 24hr staff (23.0 actual) work 12 hrs/day
        ent = txn.entitlement
        hours_per_day = Decimal('11.66') if ent.contracted_hours_per_week >= Decimal('30.00') else Decimal('12.00')
        days = (txn.hours / hours_per_day) if hours_per_day > 0 else Decimal('0.00')
        
        transaction_list.append({
            'date': txn.created_at.date().isoformat(),
            'sap': txn.entitlement.profile.user.sap,
            'name': txn.entitlement.profile.user.full_name,
            'type': txn.transaction_type,
            'hours': float(txn.hours),
            'days': float(days),
            'balance_after_hours': float(txn.balance_after),
            'description': txn.description
        })
    
    return {
        'period': f"{start_date.date()} to {end_date.date()}",
        'summary': {
            'total_staff': total_staff,
            'staff_35hr_contract': staff_35hr,
            'staff_24hr_contract': staff_24hr,
            'total_entitlement_hours': round(float(total_entitlement), 1),
            'total_used_hours': round(float(total_used), 1),
            'total_pending_hours': round(float(total_pending), 1),
            'total_remaining_hours': round(float(total_remaining), 1),
            'total_carryover_hours': round(float(total_carryover), 1),
            'overall_usage_percentage': round((float(total_used) / float(total_entitlement) * 100) if total_entitlement > 0 else 0, 1)
        },
        'staff_breakdown': staff_by_usage,
        'recent_transactions': transaction_list,
        'transactions_in_period': transactions.count(),
        'generated_at': timezone.now().isoformat()
    }


# Map report types to generator functions
REPORT_GENERATORS = {
    'DAILY_ACTIVITY': generate_daily_activity_report,
    'WEEKLY_SUMMARY': generate_weekly_summary_report,
    'MONTHLY_COMPLIANCE': generate_monthly_compliance_report,
    'USER_ACTIVITY': generate_user_activity_report,
    'DATA_CHANGES': generate_data_changes_report,
    'COMPLIANCE_VIOLATIONS': generate_compliance_violations_report,
    'SHIFT_AUDIT': generate_shift_audit_report,
    'LEAVE_AUDIT': generate_leave_audit_report,
    'ANNUAL_LEAVE': generate_annual_leave_report,
}
