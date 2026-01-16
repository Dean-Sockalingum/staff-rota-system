"""
Audit and Compliance Models for Staff Rota System
Tracks all system changes, compliance checks, and regulatory requirements
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import json

User = get_user_model()


class DataChangeLog(models.Model):
    """
    Comprehensive audit trail of all data changes in the system.
    Tracks who changed what, when, and what the values were before/after.
    """
    ACTION_CHOICES = [
        ('CREATE', 'Created'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted'),
        ('APPROVE', 'Approved'),
        ('DENY', 'Denied'),
        ('CANCEL', 'Cancelled'),
    ]
    
    # What was changed
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Action details
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    field_name = models.CharField(max_length=100, blank=True, null=True)
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    
    # Who and when
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='data_changes')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Context
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)
    session_key = models.CharField(max_length=40, blank=True, null=True)
    
    # Additional metadata
    reason = models.TextField(blank=True, null=True)
    is_automated = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user} {self.action} {self.content_type} at {self.timestamp}"


class ComplianceRule(models.Model):
    """
    Defines compliance rules that the system must adhere to.
    Examples: Working Time Directive, rest period requirements, etc.
    """
    RULE_CATEGORY_CHOICES = [
        ('WORKING_TIME', 'Working Time Directive'),
        ('REST_PERIOD', 'Rest Period Requirements'),
        ('ANNUAL_LEAVE', 'Annual Leave Entitlement'),
        ('STAFFING_LEVELS', 'Minimum Staffing Levels'),
        ('TRAINING', 'Training & Certification'),
        ('DATA_PROTECTION', 'Data Protection (GDPR)'),
        ('HEALTH_SAFETY', 'Health & Safety'),
        ('OTHER', 'Other'),
    ]
    
    SEVERITY_CHOICES = [
        ('CRITICAL', 'Critical'),
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
        ('INFO', 'Informational'),
    ]
    
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=50, unique=True, help_text="Short code for the rule (e.g., WTD_48_HOURS)")
    category = models.CharField(max_length=30, choices=RULE_CATEGORY_CHOICES)
    description = models.TextField()
    
    # Rule parameters (stored as JSON)
    parameters = models.JSONField(default=dict, help_text="Rule-specific parameters")
    
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='MEDIUM')
    is_active = models.BooleanField(default=True)
    
    # Remediation
    remediation_steps = models.TextField(blank=True, help_text="Steps to resolve violations")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.code}: {self.name}"


class ComplianceCheck(models.Model):
    """
    Records of compliance checks performed on the system.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    rule = models.ForeignKey(ComplianceRule, on_delete=models.CASCADE, related_name='checks')
    
    # Check scope
    check_date = models.DateField(default=timezone.now)
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Results
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    violations_found = models.IntegerField(default=0)
    items_checked = models.IntegerField(default=0)
    
    # Details
    check_results = models.JSONField(default=dict)
    error_message = models.TextField(blank=True, null=True)
    
    # Execution
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_automated = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['rule', 'check_date']),
            models.Index(fields=['status', 'started_at']),
        ]
    
    def __str__(self):
        return f"{self.rule.code} check on {self.check_date}"


class ComplianceViolation(models.Model):
    """
    Individual compliance violations detected during checks.
    """
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('ACKNOWLEDGED', 'Acknowledged'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('ACCEPTED_RISK', 'Accepted Risk'),
        ('FALSE_POSITIVE', 'False Positive'),
    ]
    
    compliance_check = models.ForeignKey(ComplianceCheck, on_delete=models.CASCADE, related_name='violations')
    rule = models.ForeignKey(ComplianceRule, on_delete=models.CASCADE)
    
    # What violated
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.CharField(max_length=255, blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Violation details
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=ComplianceRule.SEVERITY_CHOICES)
    
    # Staff member affected (if applicable)
    affected_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='compliance_violations')
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    detected_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(blank=True, null=True)
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='acknowledged_violations')
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_violations')
    
    # Resolution
    resolution_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['affected_user', 'status']),
        ]
    
    def __str__(self):
        return f"{self.rule.code} violation - {self.status}"


class AuditReport(models.Model):
    """
    Generated audit reports for management and compliance purposes.
    """
    REPORT_TYPE_CHOICES = [
        ('DAILY_ACTIVITY', 'Daily Activity Log'),
        ('WEEKLY_SUMMARY', 'Weekly Summary'),
        ('MONTHLY_COMPLIANCE', 'Monthly Compliance Report'),
        ('USER_ACTIVITY', 'User Activity Report'),
        ('DATA_CHANGES', 'Data Changes Report'),
        ('COMPLIANCE_VIOLATIONS', 'Compliance Violations Report'),
        ('SHIFT_AUDIT', 'Shift Audit Report'),
        ('LEAVE_AUDIT', 'Leave Request Audit'),
        ('ANNUAL_LEAVE', 'Annual Leave Entitlement Report'),
        ('CUSTOM', 'Custom Report'),
    ]
    
    STATUS_CHOICES = [
        ('GENERATING', 'Generating'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    report_type = models.CharField(max_length=30, choices=REPORT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Report period
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Generation
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='GENERATING')
    
    # Report data
    report_data = models.JSONField(default=dict)
    file = models.FileField(upload_to='audit_reports/', blank=True, null=True)
    
    # Filters/parameters used
    filters = models.JSONField(default=dict, blank=True)
    
    # Metadata
    total_records = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['report_type', 'generated_at']),
            models.Index(fields=['generated_by', 'generated_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.period_start} to {self.period_end})"


class SystemAccessLog(models.Model):
    """
    Tracks user access to the system for security auditing.
    """
    ACCESS_TYPE_CHOICES = [
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('LOGIN_FAILED', 'Failed Login'),
        ('SESSION_EXPIRED', 'Session Expired'),
        ('PASSWORD_CHANGE', 'Password Changed'),
        ('PASSWORD_RESET', 'Password Reset'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='access_logs')
    username_attempt = models.CharField(max_length=150, blank=True, null=True, help_text="Username used (for failed attempts)")
    
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPE_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Session info
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=255, blank=True, null=True)
    session_key = models.CharField(max_length=40, blank=True, null=True)
    
    # Geolocation (optional)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    
    # Success/failure
    success = models.BooleanField(default=True)
    failure_reason = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['access_type', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]
    
    def __str__(self):
        user_str = self.user.full_name if self.user else self.username_attempt
        return f"{user_str} - {self.access_type} at {self.timestamp}"
