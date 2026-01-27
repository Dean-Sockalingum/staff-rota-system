# Audit Trail & Activity Logging Guide

## Overview

The Audit Trail system provides comprehensive tracking of all user actions, data changes, system access, and compliance events. This ensures full accountability, supports regulatory compliance (GDPR, HIPAA, etc.), and enables security monitoring.

## Features

### 1. Data Change Logging
- Track all CREATE, UPDATE, DELETE operations
- Field-level change tracking (before/after values)
- User attribution and timestamps
- IP address and session tracking
- Automated vs manual change identification
- Change reason documentation

### 2. Access Logging
- Login/logout tracking
- Failed login attempt monitoring
- Password change events
- Session management
- IP address and user agent tracking
- Geographic location (optional)

### 3. Compliance Monitoring
- Configurable compliance rules
- Automated compliance checking
- Violation detection and tracking
- Remediation workflows
- Multiple compliance frameworks (GDPR, HIPAA, etc.)

### 4. Audit Reporting
- Customizable audit reports
- Multiple report types
- Date range filtering
- Export to CSV/PDF
- Automated report generation
- Report archiving

### 5. Security Monitoring
- Suspicious activity detection
- Multiple failed login alerts
- Unusual deletion patterns
- Multi-IP access detection
- Real-time alerting

## Architecture

### Models

#### DataChangeLog
Tracks all data modifications:
```python
{
    'content_type': ContentType,  # Model being changed
    'object_id': str,              # PK of object
    'action': str,                 # CREATE, UPDATE, DELETE, etc.
    'field_name': str,             # Specific field changed
    'old_value': str,              # Previous value
    'new_value': str,              # New value
    'user': User,                  # Who made the change
    'timestamp': datetime,         # When it happened
    'ip_address': str,             # Client IP
    'user_agent': str,             # Browser info
    'session_key': str,            # Session ID
    'reason': str,                 # Why the change was made
    'is_automated': bool           # Was it automated?
}
```

#### SystemAccessLog
Tracks system access events:
```python
{
    'user': User,
    'username_attempt': str,       # For failed logins
    'access_type': str,            # LOGIN, LOGOUT, etc.
    'timestamp': datetime,
    'ip_address': str,
    'user_agent': str,
    'session_key': str,
    'country': str,                # Optional geolocation
    'city': str,
    'success': bool,
    'failure_reason': str
}
```

#### ComplianceRule
Defines compliance requirements:
```python
{
    'name': str,
    'code': str,                   # Unique identifier
    'category': str,               # WORKING_TIME, REST_PERIOD, etc.
    'description': str,
    'parameters': dict,            # Rule-specific config
    'severity': str,               # CRITICAL, HIGH, MEDIUM, LOW
    'is_active': bool,
    'remediation_steps': str
}
```

#### ComplianceCheck
Records compliance verification:
```python
{
    'rule': ComplianceRule,
    'check_date': date,
    'period_start': date,
    'period_end': date,
    'status': str,                 # PENDING, COMPLETED, FAILED
    'violations_found': int,
    'items_checked': int,
    'check_results': dict,
    'performed_by': User,
    'is_automated': bool
}
```

#### ComplianceViolation
Tracks individual violations:
```python
{
    'compliance_check': ComplianceCheck,
    'rule': ComplianceRule,
    'content_object': GenericForeignKey,  # What violated
    'description': str,
    'severity': str,
    'affected_user': User,         # Staff member affected
    'status': str,                 # OPEN, ACKNOWLEDGED, RESOLVED
    'detected_at': datetime,
    'acknowledged_by': User,
    'resolved_by': User,
    'resolution_notes': str
}
```

#### AuditReport
Generated audit reports:
```python
{
    'report_type': str,            # DAILY_ACTIVITY, MONTHLY_COMPLIANCE, etc.
    'title': str,
    'period_start': date,
    'period_end': date,
    'generated_by': User,
    'status': str,                 # GENERATING, COMPLETED, FAILED
    'report_data': dict,           # Report content
    'file': FileField,             # PDF/CSV export
    'filters': dict,               # Applied filters
    'total_records': int
}
```

### Service Layer

#### AuditService Class

**Log Data Change**:
```python
from scheduling.audit_service import AuditService

# Log a single field change
AuditService.log_data_change(
    user=request.user,
    obj=shift,
    action='UPDATE',
    field_name='status',
    old_value='PENDING',
    new_value='APPROVED',
    reason='Approved by manager',
    request=request
)

# Log multiple fields
changes = {
    'status': ('PENDING', 'APPROVED'),
    'approved_by': (None, request.user.username),
    'approved_at': (None, str(timezone.now()))
}
AuditService.log_object_changes(
    user=request.user,
    obj=shift,
    changes_dict=changes,
    request=request
)
```

**Log Access Event**:
```python
# Log successful login
AuditService.log_access(
    user=user,
    access_type='LOGIN',
    ip_address='192.168.1.100',
    user_agent=request.META.get('HTTP_USER_AGENT'),
    session_key=request.session.session_key,
    success=True
)

# Log failed login
AuditService.log_access(
    user=None,
    access_type='LOGIN_FAILED',
    ip_address='192.168.1.100',
    username_attempt='john.doe',
    success=False,
    failure_reason='Invalid password'
)
```

**Get Object History**:
```python
# Get change history for an object
history = AuditService.get_object_history(shift, limit=50)

for change in history:
    print(f"{change.user} {change.action} {change.field_name}")
    print(f"  {change.old_value} → {change.new_value}")
```

**Get User Activity**:
```python
from datetime import timedelta

activity = AuditService.get_user_activity(
    user=staff_member,
    start_date=timezone.now() - timedelta(days=30)
)

print(f"Data changes: {activity['total_changes']}")
print(f"Access events: {activity['total_accesses']}")
```

**Detect Suspicious Activity**:
```python
findings = AuditService.detect_suspicious_activity(hours=24)

for finding in findings:
    print(f"[{finding['severity']}] {finding['type']}")
    print(f"  {finding['description']}")
```

**Generate Audit Report**:
```python
report = AuditService.generate_activity_report(
    start_date=date(2025, 12, 1),
    end_date=date(2025, 12, 31),
    report_type='MONTHLY_COMPLIANCE',
    user=request.user,
    filters={'user_id': staff_member.id}
)

print(f"Report status: {report.status}")
print(f"Total records: {report.total_records}")
```

## Usage

### Accessing the Audit Dashboard

Navigate to `/audit/` to view the main audit trail dashboard.

**Dashboard Sections**:
1. **Summary Statistics**: Total changes, access events, unique users, failed logins
2. **Changes by Action**: CREATE, UPDATE, DELETE breakdown
3. **Access by Type**: LOGIN, LOGOUT, PASSWORD_CHANGE distribution
4. **Most Active Users**: Top users by activity count
5. **Suspicious Activity**: Recent security concerns
6. **Compliance Violations**: Open violations requiring attention
7. **Recent Activity**: Latest data changes and access events

### Viewing Data Changes

Navigate to `/audit/data-changes/` to view detailed change logs.

**Available Filters**:
- User: Filter by specific user
- Action: CREATE, UPDATE, DELETE, APPROVE, DENY, CANCEL
- Time Period: Last 7/30/90 days
- Search: Search in field names, values, reasons

**Information Displayed**:
- Timestamp of change
- User who made the change
- Action performed
- Object type and ID
- Field changed
- Old and new values
- IP address
- Reason (if provided)

### Monitoring Access Logs

Navigate to `/audit/access-log/` to view system access events.

**Filters**:
- User: Specific user
- Access Type: LOGIN, LOGOUT, LOGIN_FAILED, etc.
- Success: Successful/Failed only
- Time Period: Customizable

**Statistics**:
- Total access events
- Successful logins
- Failed login attempts
- Unique IP addresses

**Security Alerts**:
- Multiple failed logins from same IP
- Access from unusual locations
- Multiple IPs for single user

### User Activity Tracking

Navigate to `/audit/user/<user_id>/` to view all activity for a specific user.

**Unified Timeline**:
- Data changes and access events combined
- Chronological order
- Type indicators (data change vs access)
- Detailed information for each event

**Statistics**:
- Total data changes
- Total access events
- Activity patterns
- Most frequent actions

### Object History

Navigate to `/audit/object-history/?content_type=X&object_id=Y` to view change history for a specific object.

**Information**:
- Complete change history
- Chronological timeline
- Field-by-field changes
- User attribution
- Timestamps

### Compliance Monitoring

Navigate to `/audit/compliance/` to view compliance dashboard.

**Features**:
- Active compliance rules
- Recent compliance checks
- Open violations by severity
- Critical violations requiring immediate attention
- Compliance trends over time

**Violation Management**:
1. View violations at `/audit/compliance/violations/`
2. Filter by status, severity, rule
3. Acknowledge violations
4. Add resolution notes
5. Mark as resolved

**Acknowledge Violation**:
```javascript
POST /audit/compliance/violations/<id>/acknowledge/
```

**Resolve Violation**:
```javascript
POST /audit/compliance/violations/<id>/resolve/
Body: {
    resolution_notes: "Issue corrected by adjusting shift times"
}
```

### Generating Audit Reports

Navigate to `/audit/reports/generate/` to create custom audit reports.

**Report Types**:
- Daily Activity Log
- Weekly Summary
- Monthly Compliance Report
- User Activity Report
- Data Changes Report
- Compliance Violations Report
- Shift Audit Report
- Leave Request Audit
- Custom Report

**Configuration**:
1. Select report type
2. Choose date range
3. Apply filters (user, action, etc.)
4. Generate report

**Report Output**:
- JSON data structure
- Summary statistics
- Detailed breakdowns
- Exportable to CSV/PDF

### Viewing Generated Reports

Navigate to `/audit/reports/` to list all generated reports.

**Actions**:
- View report details
- Download report file
- Re-generate with same parameters
- Filter by type and date

### Exporting Audit Data

Navigate to `/audit/export/` to export audit data to CSV.

**Export Types**:
- Data Changes: All change logs
- Access Logs: All access events

**CSV Columns**:

**Data Changes**:
- Timestamp
- User
- Action
- Object Type
- Object ID
- Field Name
- Old Value
- New Value
- IP Address

**Access Logs**:
- Timestamp
- User
- Access Type
- IP Address
- Success
- Failure Reason

## API Endpoints

### Suspicious Activity API
`GET /audit/suspicious-activity/api/?hours=24`

Detect suspicious activity patterns.

**Response**:
```json
{
    "findings": [
        {
            "type": "MULTIPLE_FAILED_LOGINS",
            "severity": "HIGH",
            "description": "Multiple failed login attempts for user123 from 192.168.1.100",
            "count": 7
        },
        {
            "type": "EXCESSIVE_DELETIONS",
            "severity": "MEDIUM",
            "description": "Unusual number of deletions by user 5",
            "count": 15
        }
    ],
    "count": 2,
    "period_hours": 24
}
```

## Automated Logging

### Middleware Integration

Create middleware to automatically log all requests:

```python
# scheduling/middleware.py
from .audit_service import AuditService

class AuditLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Log successful logins
        if request.path == '/login/' and response.status_code == 302:
            if request.user.is_authenticated:
                AuditService.log_access(
                    user=request.user,
                    access_type='LOGIN',
                    ip_address=self._get_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT'),
                    session_key=request.session.session_key,
                    success=True
                )
        
        return response
    
    def _get_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
```

### Model Signal Handlers

Automatically log model changes using Django signals:

```python
# scheduling/signals.py
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import Shift
from .audit_service import AuditService

@receiver(pre_save, sender=Shift)
def track_shift_changes(sender, instance, **kwargs):
    if instance.pk:  # Existing object being updated
        try:
            old_instance = Shift.objects.get(pk=instance.pk)
            changes = {}
            
            for field in ['status', 'start_time', 'end_time', 'user']:
                old_val = getattr(old_instance, field.name)
                new_val = getattr(instance, field.name)
                if old_val != new_val:
                    changes[field.name] = (old_val, new_val)
            
            if changes:
                # Store changes for post_save
                instance._audit_changes = changes
        except Shift.DoesNotExist:
            pass

@receiver(post_save, sender=Shift)
def log_shift_save(sender, instance, created, **kwargs):
    if created:
        AuditService.log_data_change(
            user=getattr(instance, '_audit_user', None),
            obj=instance,
            action='CREATE',
            reason='New shift created'
        )
    elif hasattr(instance, '_audit_changes'):
        AuditService.log_object_changes(
            user=getattr(instance, '_audit_user', None),
            obj=instance,
            changes_dict=instance._audit_changes,
            action='UPDATE'
        )

@receiver(post_delete, sender=Shift)
def log_shift_delete(sender, instance, **kwargs):
    AuditService.log_data_change(
        user=getattr(instance, '_audit_user', None),
        obj=instance,
        action='DELETE',
        reason='Shift deleted'
    )
```

### View Integration

Log actions in views:

```python
from .audit_service import AuditService

def approve_leave_request(request, request_id):
    leave_request = get_object_or_404(LeaveRequest, id=request_id)
    
    # Store old value
    old_status = leave_request.status
    
    # Make change
    leave_request.status = 'APPROVED'
    leave_request.approved_by = request.user
    leave_request.save()
    
    # Log the change
    AuditService.log_data_change(
        user=request.user,
        obj=leave_request,
        action='APPROVE',
        field_name='status',
        old_value=old_status,
        new_value='APPROVED',
        reason=f"Approved by {request.user.full_name}",
        request=request
    )
    
    return redirect('leave_requests')
```

## Compliance Rules

### Creating Compliance Rules

```python
from scheduling.models_audit import ComplianceRule

# Working Time Directive - 48 hour week
ComplianceRule.objects.create(
    name='48 Hour Working Week',
    code='WTD_48_HOURS',
    category='WORKING_TIME',
    description='Staff must not work more than 48 hours per week on average',
    parameters={
        'max_hours_per_week': 48,
        'averaging_period_weeks': 17
    },
    severity='HIGH',
    remediation_steps='Reduce scheduled hours or increase rest periods'
)

# Rest period requirements
ComplianceRule.objects.create(
    name='11 Hour Rest Period',
    code='REST_11_HOURS',
    category='REST_PERIOD',
    description='Staff must have at least 11 consecutive hours rest between shifts',
    parameters={
        'min_rest_hours': 11
    },
    severity='CRITICAL',
    remediation_steps='Reschedule shifts to ensure adequate rest'
)
```

### Running Compliance Checks

```python
from scheduling.models_audit import ComplianceCheck
from datetime import date, timedelta

# Create and run a compliance check
check = ComplianceCheck.objects.create(
    rule=rule,
    period_start=date.today() - timedelta(days=7),
    period_end=date.today(),
    performed_by=request.user,
    is_automated=False
)

# Run check logic (custom per rule type)
violations = run_compliance_check(check)

check.violations_found = len(violations)
check.status = 'COMPLETED'
check.completed_at = timezone.now()
check.save()
```

## Best Practices

### 1. What to Log
- **Always Log**: User logins, data modifications, deletions, approvals
- **Consider Logging**: Data views (for sensitive data), exports, configuration changes
- **Don't Log**: Read-only queries (unless required by policy), system health checks

### 2. Performance Considerations
- Use bulk_create for logging multiple changes
- Implement asynchronous logging for high-traffic sites
- Set up data retention policies
- Index frequently queried fields

### 3. Data Retention
```python
# Set retention policies
from scheduling.models_audit import AuditRetentionPolicy

AuditRetentionPolicy.objects.create(
    data_type='AUDIT_LOG',
    retention_days=2555,  # 7 years for compliance
    legal_requirement=True,
    regulation_reference='GDPR Article 17'
)

# Apply retention (run periodically)
for policy in AuditRetentionPolicy.objects.filter(is_active=True):
    deleted_count = policy.apply_retention()
    print(f"Deleted {deleted_count} old {policy.data_type} records")
```

### 4. Security
- Restrict audit dashboard access to admin users
- Log access to audit logs themselves
- Implement audit log integrity checks (hashing)
- Regular backup of audit data
- Encrypt sensitive data in audit logs

### 5. Compliance
- Document what events are logged
- Maintain audit log retention schedule
- Regular compliance audits
- Train staff on audit requirements
- Incident response procedures

## Troubleshooting

### High Audit Log Volume
1. Review what's being logged
2. Implement sampling for high-volume events
3. Use asynchronous logging
4. Optimize database queries with indexes
5. Archive old logs to cold storage

### Missing Audit Entries
1. Check signal handlers are connected
2. Verify middleware is installed
3. Review exception handling in logging code
4. Check database transaction rollbacks
5. Verify user context is available

### Compliance Check Failures
1. Review rule parameters
2. Check data quality
3. Verify date ranges
4. Review error messages in check results
5. Test rule logic with sample data

### Report Generation Issues
1. Check date range validity
2. Verify filters are correct
3. Review available data for period
4. Check file permissions for exports
5. Monitor memory usage for large reports

## Related Documentation

- [Health Monitoring Guide](HEALTH_MONITORING_GUIDE.md)
- [Security Best Practices](SECURITY.md)
- [GDPR Compliance](GDPR_COMPLIANCE.md)
- [Data Protection](DATA_PROTECTION.md)
