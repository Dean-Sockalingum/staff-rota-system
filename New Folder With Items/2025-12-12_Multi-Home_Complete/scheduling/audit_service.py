"""
Audit Trail Service
Centralized service for logging audit events and tracking system activity
"""
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from .models_audit import (
    DataChangeLog, SystemAccessLog, ComplianceCheck, 
    ComplianceViolation, AuditReport
)
import json


class AuditService:
    """Centralized audit logging service"""
    
    @staticmethod
    def log_data_change(user, obj, action, field_name=None, old_value=None, 
                       new_value=None, reason=None, request=None, is_automated=False):
        """
        Log a data change event
        
        Args:
            user: User making the change
            obj: Object being changed
            action: Action type (CREATE, UPDATE, DELETE, etc.)
            field_name: Specific field changed (optional)
            old_value: Previous value
            new_value: New value
            reason: Reason for change
            request: HTTP request object
            is_automated: Whether change was automated
        """
        log_entry = DataChangeLog(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=str(obj.pk),
            action=action,
            field_name=field_name,
            old_value=str(old_value) if old_value is not None else None,
            new_value=str(new_value) if new_value is not None else None,
            user=user,
            reason=reason,
            is_automated=is_automated
        )
        
        if request:
            log_entry.ip_address = AuditService._get_client_ip(request)
            log_entry.user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]
            if hasattr(request, 'session'):
                log_entry.session_key = request.session.session_key
        
        log_entry.save()
        return log_entry
    
    @staticmethod
    def log_access(user, access_type, ip_address, user_agent=None, 
                   session_key=None, success=True, failure_reason=None, 
                   username_attempt=None):
        """
        Log a system access event
        
        Args:
            user: User accessing system (None for failed logins)
            access_type: Type of access (LOGIN, LOGOUT, etc.)
            ip_address: Client IP address
            user_agent: Browser user agent
            session_key: Session identifier
            success: Whether access was successful
            failure_reason: Reason for failure (if failed)
            username_attempt: Username attempted (for failed logins)
        """
        return SystemAccessLog.objects.create(
            user=user,
            username_attempt=username_attempt,
            access_type=access_type,
            ip_address=ip_address,
            user_agent=user_agent[:255] if user_agent else None,
            session_key=session_key,
            success=success,
            failure_reason=failure_reason
        )
    
    @staticmethod
    def log_object_changes(user, obj, changes_dict, action='UPDATE', request=None):
        """
        Log multiple field changes for an object
        
        Args:
            user: User making changes
            obj: Object being modified
            changes_dict: Dict of {field_name: (old_value, new_value)}
            action: Action type
            request: HTTP request
        """
        logs = []
        for field_name, (old_val, new_val) in changes_dict.items():
            if old_val != new_val:  # Only log actual changes
                log = AuditService.log_data_change(
                    user=user,
                    obj=obj,
                    action=action,
                    field_name=field_name,
                    old_value=old_val,
                    new_value=new_val,
                    request=request
                )
                logs.append(log)
        return logs
    
    @staticmethod
    def get_object_history(obj, limit=None):
        """
        Get change history for a specific object
        
        Args:
            obj: Object to get history for
            limit: Maximum number of records to return
        """
        content_type = ContentType.objects.get_for_model(obj)
        history = DataChangeLog.objects.filter(
            content_type=content_type,
            object_id=str(obj.pk)
        ).order_by('-timestamp')
        
        if limit:
            history = history[:limit]
        
        return history
    
    @staticmethod
    def get_user_activity(user, start_date=None, end_date=None):
        """
        Get all activity for a specific user
        
        Args:
            user: User to get activity for
            start_date: Start of date range
            end_date: End of date range
        """
        data_changes = DataChangeLog.objects.filter(user=user)
        access_logs = SystemAccessLog.objects.filter(user=user)
        
        if start_date:
            data_changes = data_changes.filter(timestamp__gte=start_date)
            access_logs = access_logs.filter(timestamp__gte=start_date)
        
        if end_date:
            data_changes = data_changes.filter(timestamp__lte=end_date)
            access_logs = access_logs.filter(timestamp__lte=end_date)
        
        return {
            'data_changes': data_changes.order_by('-timestamp'),
            'access_logs': access_logs.order_by('-timestamp'),
            'total_changes': data_changes.count(),
            'total_accesses': access_logs.count(),
        }
    
    @staticmethod
    def get_recent_activity(hours=24, limit=100):
        """
        Get recent system activity
        
        Args:
            hours: Number of hours to look back
            limit: Maximum records per type
        """
        from datetime import timedelta
        since = timezone.now() - timedelta(hours=hours)
        
        return {
            'data_changes': DataChangeLog.objects.filter(
                timestamp__gte=since
            ).order_by('-timestamp')[:limit],
            'access_logs': SystemAccessLog.objects.filter(
                timestamp__gte=since
            ).order_by('-timestamp')[:limit],
        }
    
    @staticmethod
    def generate_activity_report(start_date, end_date, report_type='DAILY_ACTIVITY', 
                                 user=None, filters=None):
        """
        Generate an audit report
        
        Args:
            start_date: Report start date
            end_date: Report end date
            report_type: Type of report
            user: User generating report
            filters: Additional filters
        """
        report = AuditReport.objects.create(
            report_type=report_type,
            title=f"{report_type} Report: {start_date} to {end_date}",
            period_start=start_date,
            period_end=end_date,
            generated_by=user,
            status='GENERATING',
            filters=filters or {}
        )
        
        try:
            # Gather data
            data_changes = DataChangeLog.objects.filter(
                timestamp__gte=start_date,
                timestamp__lte=end_date
            )
            
            access_logs = SystemAccessLog.objects.filter(
                timestamp__gte=start_date,
                timestamp__lte=end_date
            )
            
            # Apply filters if provided
            if filters:
                if 'user_id' in filters:
                    data_changes = data_changes.filter(user_id=filters['user_id'])
                    access_logs = access_logs.filter(user_id=filters['user_id'])
                
                if 'action' in filters:
                    data_changes = data_changes.filter(action=filters['action'])
            
            # Compile report data
            report_data = {
                'summary': {
                    'total_data_changes': data_changes.count(),
                    'total_access_events': access_logs.count(),
                    'unique_users': data_changes.values('user').distinct().count(),
                },
                'data_changes_by_action': dict(
                    data_changes.values('action').annotate(
                        count=models.Count('id')
                    ).values_list('action', 'count')
                ),
                'access_by_type': dict(
                    access_logs.values('access_type').annotate(
                        count=models.Count('id')
                    ).values_list('access_type', 'count')
                ),
                'failed_logins': access_logs.filter(
                    access_type='LOGIN_FAILED'
                ).count(),
            }
            
            report.report_data = report_data
            report.total_records = data_changes.count() + access_logs.count()
            report.status = 'COMPLETED'
            report.save()
            
        except Exception as e:
            report.status = 'FAILED'
            report.error_message = str(e)
            report.save()
        
        return report
    
    @staticmethod
    def detect_suspicious_activity(hours=24):
        """
        Detect potentially suspicious activity patterns
        
        Returns dict of suspicious findings
        """
        from datetime import timedelta
        from django.db.models import Count
        
        since = timezone.now() - timedelta(hours=hours)
        findings = []
        
        # Multiple failed login attempts
        failed_logins = SystemAccessLog.objects.filter(
            timestamp__gte=since,
            access_type='LOGIN_FAILED'
        ).values('username_attempt', 'ip_address').annotate(
            count=Count('id')
        ).filter(count__gte=5)
        
        for item in failed_logins:
            findings.append({
                'type': 'MULTIPLE_FAILED_LOGINS',
                'severity': 'HIGH',
                'description': f"Multiple failed login attempts for {item['username_attempt']} from {item['ip_address']}",
                'count': item['count']
            })
        
        # Unusual deletion activity
        deletions = DataChangeLog.objects.filter(
            timestamp__gte=since,
            action='DELETE'
        ).values('user').annotate(
            count=Count('id')
        ).filter(count__gte=10)
        
        for item in deletions:
            findings.append({
                'type': 'EXCESSIVE_DELETIONS',
                'severity': 'MEDIUM',
                'description': f"Unusual number of deletions by user {item['user']}",
                'count': item['count']
            })
        
        # Access from multiple IPs in short time
        multi_ip_users = SystemAccessLog.objects.filter(
            timestamp__gte=since,
            access_type='LOGIN',
            success=True
        ).values('user').annotate(
            ip_count=Count('ip_address', distinct=True)
        ).filter(ip_count__gte=3)
        
        for item in multi_ip_users:
            findings.append({
                'type': 'MULTIPLE_IP_ADDRESSES',
                'severity': 'MEDIUM',
                'description': f"User logged in from {item['ip_count']} different IPs",
                'user_id': item['user']
            })
        
        return findings
    
    @staticmethod
    def _get_client_ip(request):
        """Extract client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


# Import here to avoid circular dependency
from django.db import models
