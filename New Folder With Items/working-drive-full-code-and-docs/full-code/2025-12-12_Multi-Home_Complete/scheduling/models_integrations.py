"""
Integration API Models
=====================

Models for API authentication, rate limiting, and third-party integrations.

Created: 30 December 2025
Task 41: Integration APIs
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import URLValidator
import secrets
import hashlib
from datetime import timedelta

User = get_user_model()


class APIClient(models.Model):
    """
    Third-party client that can access the API.
    
    Represents external systems like HR software, payroll systems, etc.
    """
    
    CLIENT_TYPE_CHOICES = [
        ('HR', 'HR System'),
        ('PAYROLL', 'Payroll System'),
        ('ANALYTICS', 'Analytics Platform'),
        ('MOBILE', 'Mobile Application'),
        ('WEBHOOK', 'Webhook Integration'),
        ('CUSTOM', 'Custom Integration'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('SUSPENDED', 'Suspended'),
        ('REVOKED', 'Revoked'),
    ]
    
    # Client identification
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    client_type = models.CharField(max_length=20, choices=CLIENT_TYPE_CHOICES)
    
    # Authentication
    client_id = models.CharField(max_length=100, unique=True, db_index=True)
    client_secret = models.CharField(max_length=255)  # Hashed
    api_key = models.CharField(max_length=100, unique=True, db_index=True)
    
    # Authorization
    allowed_endpoints = models.JSONField(
        default=list,
        help_text='List of endpoint patterns this client can access'
    )
    allowed_methods = models.JSONField(
        default=list,
        help_text='HTTP methods allowed (GET, POST, PUT, DELETE)'
    )
    ip_whitelist = models.JSONField(
        default=list,
        help_text='IP addresses allowed to use this client'
    )
    
    # Rate limiting
    rate_limit_per_minute = models.IntegerField(default=60)
    rate_limit_per_hour = models.IntegerField(default=1000)
    rate_limit_per_day = models.IntegerField(default=10000)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )
    is_active = models.BooleanField(default=True)
    
    # Ownership
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_api_clients'
    )
    organization = models.CharField(max_length=200, blank=True)
    contact_email = models.EmailField()
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    # Usage tracking
    total_requests = models.BigIntegerField(default=0)
    successful_requests = models.BigIntegerField(default=0)
    failed_requests = models.BigIntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['client_id']),
            models.Index(fields=['api_key']),
            models.Index(fields=['status', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_client_type_display()})"
    
    def generate_api_key(self):
        """Generate a new API key"""
        self.api_key = f"sk_{secrets.token_urlsafe(32)}"
        return self.api_key
    
    def set_client_secret(self, secret):
        """Hash and set client secret"""
        self.client_secret = hashlib.sha256(secret.encode()).hexdigest()
    
    def verify_client_secret(self, secret):
        """Verify client secret"""
        return self.client_secret == hashlib.sha256(secret.encode()).hexdigest()
    
    def increment_request_count(self, success=True):
        """Update request statistics"""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        self.last_used_at = timezone.now()
        self.save()


class APIToken(models.Model):
    """
    OAuth-style access tokens for API authentication.
    """
    
    TOKEN_TYPE_CHOICES = [
        ('ACCESS', 'Access Token'),
        ('REFRESH', 'Refresh Token'),
    ]
    
    client = models.ForeignKey(
        APIClient,
        on_delete=models.CASCADE,
        related_name='tokens'
    )
    token = models.CharField(max_length=255, unique=True, db_index=True)
    token_type = models.CharField(max_length=20, choices=TOKEN_TYPE_CHOICES)
    
    # Scope and permissions
    scope = models.JSONField(
        default=list,
        help_text='Specific permissions granted to this token'
    )
    
    # Expiration
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    # Usage tracking
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    use_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['expires_at', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.client.name} - {self.get_token_type_display()}"
    
    def is_valid(self):
        """Check if token is valid and not expired"""
        return (
            self.is_active and
            self.expires_at > timezone.now()
        )
    
    def refresh(self, days=30):
        """Extend token expiration"""
        self.expires_at = timezone.now() + timedelta(days=days)
        self.save()


class APIRateLimit(models.Model):
    """
    Track API rate limiting per client.
    """
    
    WINDOW_CHOICES = [
        ('MINUTE', 'Per Minute'),
        ('HOUR', 'Per Hour'),
        ('DAY', 'Per Day'),
    ]
    
    client = models.ForeignKey(
        APIClient,
        on_delete=models.CASCADE,
        related_name='rate_limits'
    )
    window_type = models.CharField(max_length=10, choices=WINDOW_CHOICES)
    window_start = models.DateTimeField()
    request_count = models.IntegerField(default=0)
    
    # Endpoint-specific tracking
    endpoint = models.CharField(max_length=200, blank=True)
    
    class Meta:
        unique_together = ['client', 'window_type', 'window_start', 'endpoint']
        indexes = [
            models.Index(fields=['client', 'window_start']),
            models.Index(fields=['window_type', 'window_start']),
        ]
    
    def __str__(self):
        return f"{self.client.name} - {self.get_window_type_display()}: {self.request_count}"
    
    @classmethod
    def check_rate_limit(cls, client, window_type='MINUTE', endpoint=''):
        """Check if client has exceeded rate limit"""
        now = timezone.now()
        
        # Determine window boundaries
        if window_type == 'MINUTE':
            window_start = now.replace(second=0, microsecond=0)
            limit = client.rate_limit_per_minute
        elif window_type == 'HOUR':
            window_start = now.replace(minute=0, second=0, microsecond=0)
            limit = client.rate_limit_per_hour
        else:  # DAY
            window_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            limit = client.rate_limit_per_day
        
        # Get or create rate limit record
        rate_limit, created = cls.objects.get_or_create(
            client=client,
            window_type=window_type,
            window_start=window_start,
            endpoint=endpoint,
            defaults={'request_count': 0}
        )
        
        # Check if limit exceeded
        if rate_limit.request_count >= limit:
            return False, rate_limit
        
        # Increment count
        rate_limit.request_count += 1
        rate_limit.save()
        
        return True, rate_limit


class APIRequestLog(models.Model):
    """
    Log all API requests for auditing and monitoring.
    """
    
    client = models.ForeignKey(
        APIClient,
        on_delete=models.SET_NULL,
        null=True,
        related_name='request_logs'
    )
    
    # Request details
    endpoint = models.CharField(max_length=500)
    method = models.CharField(max_length=10)
    query_params = models.JSONField(default=dict)
    request_body = models.JSONField(default=dict, blank=True)
    
    # Request metadata
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=500, blank=True)
    
    # Response details
    status_code = models.IntegerField()
    response_time_ms = models.IntegerField(help_text='Response time in milliseconds')
    response_size = models.IntegerField(default=0, help_text='Response size in bytes')
    
    # Error tracking
    error_message = models.TextField(blank=True)
    stack_trace = models.TextField(blank=True)
    
    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['client', '-timestamp']),
            models.Index(fields=['endpoint', '-timestamp']),
            models.Index(fields=['status_code', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code}"


class WebhookEndpoint(models.Model):
    """
    Webhook endpoints for real-time event notifications.
    """
    
    EVENT_TYPE_CHOICES = [
        ('shift.created', 'Shift Created'),
        ('shift.updated', 'Shift Updated'),
        ('shift.deleted', 'Shift Deleted'),
        ('leave.requested', 'Leave Requested'),
        ('leave.approved', 'Leave Approved'),
        ('leave.rejected', 'Leave Rejected'),
        ('staff.created', 'Staff Created'),
        ('staff.updated', 'Staff Updated'),
        ('swap.requested', 'Swap Requested'),
        ('swap.approved', 'Swap Approved'),
        ('all', 'All Events'),
    ]
    
    client = models.ForeignKey(
        APIClient,
        on_delete=models.CASCADE,
        related_name='webhooks'
    )
    
    # Webhook configuration
    url = models.URLField(validators=[URLValidator()])
    event_types = models.JSONField(
        default=list,
        help_text='Event types this webhook subscribes to'
    )
    
    # Security
    secret = models.CharField(
        max_length=100,
        help_text='Secret for HMAC signature verification'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Retry configuration
    max_retries = models.IntegerField(default=3)
    retry_delay_seconds = models.IntegerField(default=60)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    total_deliveries = models.IntegerField(default=0)
    successful_deliveries = models.IntegerField(default=0)
    failed_deliveries = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.client.name} - {self.url}"
    
    def generate_secret(self):
        """Generate webhook secret"""
        self.secret = secrets.token_urlsafe(32)
        return self.secret


class WebhookDelivery(models.Model):
    """
    Track webhook delivery attempts.
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENDING', 'Sending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('RETRYING', 'Retrying'),
    ]
    
    webhook = models.ForeignKey(
        WebhookEndpoint,
        on_delete=models.CASCADE,
        related_name='deliveries'
    )
    
    # Event details
    event_type = models.CharField(max_length=50)
    event_data = models.JSONField()
    event_id = models.CharField(max_length=100, unique=True)
    
    # Delivery details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    attempt_count = models.IntegerField(default=0)
    
    # Response
    response_status_code = models.IntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    response_time_ms = models.IntegerField(null=True, blank=True)
    
    # Error tracking
    error_message = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['webhook', '-created_at']),
            models.Index(fields=['status', 'next_retry_at']),
            models.Index(fields=['event_id']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.status}"


class DataSyncJob(models.Model):
    """
    Track data synchronization jobs with external systems.
    """
    
    SYNC_TYPE_CHOICES = [
        ('STAFF_EXPORT', 'Staff Data Export'),
        ('STAFF_IMPORT', 'Staff Data Import'),
        ('SHIFT_EXPORT', 'Shift Data Export'),
        ('LEAVE_EXPORT', 'Leave Data Export'),
        ('PAYROLL_EXPORT', 'Payroll Data Export'),
        ('FULL_SYNC', 'Full System Sync'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('RUNNING', 'Running'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    client = models.ForeignKey(
        APIClient,
        on_delete=models.CASCADE,
        related_name='sync_jobs'
    )
    
    # Job configuration
    sync_type = models.CharField(max_length=20, choices=SYNC_TYPE_CHOICES)
    parameters = models.JSONField(default=dict)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Results
    records_processed = models.IntegerField(default=0)
    records_succeeded = models.IntegerField(default=0)
    records_failed = models.IntegerField(default=0)
    error_details = models.JSONField(default=list)
    
    # File export
    export_file_path = models.CharField(max_length=500, blank=True)
    export_file_size = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Duration
    duration_seconds = models.IntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['client', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_sync_type_display()} - {self.status}"
