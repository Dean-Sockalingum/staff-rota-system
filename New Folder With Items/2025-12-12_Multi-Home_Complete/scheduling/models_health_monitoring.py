"""
Health Monitoring Models
Tracks system health, performance metrics, error logs, and uptime statistics
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import json


class SystemHealthMetric(models.Model):
    """Real-time system health metrics"""
    
    METRIC_TYPE_CHOICES = [
        ('CPU', 'CPU Usage'),
        ('MEMORY', 'Memory Usage'),
        ('DISK', 'Disk Usage'),
        ('DATABASE', 'Database Performance'),
        ('RESPONSE_TIME', 'Response Time'),
        ('REQUEST_COUNT', 'Request Count'),
        ('ERROR_RATE', 'Error Rate'),
        ('ACTIVE_USERS', 'Active Users'),
    ]
    
    STATUS_CHOICES = [
        ('HEALTHY', 'Healthy'),
        ('WARNING', 'Warning'),
        ('CRITICAL', 'Critical'),
    ]
    
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPE_CHOICES)
    value = models.FloatField()
    unit = models.CharField(max_length=20, default='percent')  # percent, ms, count, MB, etc.
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='HEALTHY')
    threshold_warning = models.FloatField(null=True, blank=True)
    threshold_critical = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['metric_type', '-timestamp']),
            models.Index(fields=['status', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.metric_type}: {self.value}{self.unit} ({self.status})"
    
    def update_status(self):
        """Update status based on thresholds"""
        if self.threshold_critical and self.value >= self.threshold_critical:
            self.status = 'CRITICAL'
        elif self.threshold_warning and self.value >= self.threshold_warning:
            self.status = 'WARNING'
        else:
            self.status = 'HEALTHY'


class PerformanceLog(models.Model):
    """Detailed performance logging for endpoints and database queries"""
    
    LOG_TYPE_CHOICES = [
        ('HTTP', 'HTTP Request'),
        ('DATABASE', 'Database Query'),
        ('TASK', 'Background Task'),
        ('REPORT', 'Report Generation'),
    ]
    
    log_type = models.CharField(max_length=20, choices=LOG_TYPE_CHOICES)
    endpoint = models.CharField(max_length=500, null=True, blank=True)
    method = models.CharField(max_length=10, null=True, blank=True)  # GET, POST, etc.
    duration_ms = models.IntegerField()  # Duration in milliseconds
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # HTTP specific
    status_code = models.IntegerField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Database specific
    query = models.TextField(null=True, blank=True)
    query_count = models.IntegerField(default=1)
    
    # Resource usage
    memory_mb = models.FloatField(null=True, blank=True)
    cpu_percent = models.FloatField(null=True, blank=True)
    
    # Additional metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['log_type', '-timestamp']),
            models.Index(fields=['endpoint', '-timestamp']),
            models.Index(fields=['-duration_ms']),
            models.Index(fields=['user', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.log_type}: {self.endpoint or 'N/A'} - {self.duration_ms}ms"
    
    @classmethod
    def get_slow_queries(cls, threshold_ms=1000, hours=24):
        """Get slow database queries"""
        since = timezone.now() - timedelta(hours=hours)
        return cls.objects.filter(
            log_type='DATABASE',
            duration_ms__gte=threshold_ms,
            timestamp__gte=since
        ).order_by('-duration_ms')
    
    @classmethod
    def get_slow_endpoints(cls, threshold_ms=500, hours=24):
        """Get slow HTTP endpoints"""
        since = timezone.now() - timedelta(hours=hours)
        return cls.objects.filter(
            log_type='HTTP',
            duration_ms__gte=threshold_ms,
            timestamp__gte=since
        ).values('endpoint', 'method').annotate(
            avg_duration=models.Avg('duration_ms'),
            count=models.Count('id')
        ).order_by('-avg_duration')


class ErrorLog(models.Model):
    """Centralized error logging and tracking"""
    
    SEVERITY_CHOICES = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]
    
    ERROR_TYPE_CHOICES = [
        ('EXCEPTION', 'Python Exception'),
        ('HTTP_ERROR', 'HTTP Error'),
        ('DATABASE_ERROR', 'Database Error'),
        ('VALIDATION_ERROR', 'Validation Error'),
        ('PERMISSION_ERROR', 'Permission Error'),
        ('TIMEOUT', 'Timeout'),
        ('INTEGRATION_ERROR', 'Integration Error'),
    ]
    
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    error_type = models.CharField(max_length=50, choices=ERROR_TYPE_CHOICES)
    message = models.TextField()
    stack_trace = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Context
    endpoint = models.CharField(max_length=500, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Resolution tracking
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_errors')
    resolution_notes = models.TextField(null=True, blank=True)
    
    # Occurrence tracking
    occurrence_count = models.IntegerField(default=1)
    first_occurred = models.DateTimeField(auto_now_add=True)
    last_occurred = models.DateTimeField(auto_now_add=True)
    
    # Additional context
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['severity', '-timestamp']),
            models.Index(fields=['error_type', '-timestamp']),
            models.Index(fields=['is_resolved', '-timestamp']),
            models.Index(fields=['-occurrence_count']),
        ]
    
    def __str__(self):
        return f"[{self.severity}] {self.error_type}: {self.message[:100]}"
    
    def mark_resolved(self, user, notes=None):
        """Mark error as resolved"""
        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.resolved_by = user
        self.resolution_notes = notes
        self.save()
    
    @classmethod
    def increment_occurrence(cls, error_type, message, **kwargs):
        """Increment occurrence count for similar errors"""
        # Try to find similar error in last 24 hours
        since = timezone.now() - timedelta(hours=24)
        similar = cls.objects.filter(
            error_type=error_type,
            message=message,
            timestamp__gte=since,
            is_resolved=False
        ).first()
        
        if similar:
            similar.occurrence_count += 1
            similar.last_occurred = timezone.now()
            similar.save()
            return similar
        else:
            return cls.objects.create(
                error_type=error_type,
                message=message,
                **kwargs
            )


class SystemUptime(models.Model):
    """Track system uptime and downtime incidents"""
    
    STATUS_CHOICES = [
        ('UP', 'System Up'),
        ('DOWN', 'System Down'),
        ('MAINTENANCE', 'Maintenance'),
        ('DEGRADED', 'Degraded Performance'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    
    # Incident details (for DOWN or DEGRADED)
    incident_description = models.TextField(null=True, blank=True)
    affected_services = models.JSONField(default=list, blank=True)  # List of affected services
    root_cause = models.TextField(null=True, blank=True)
    
    # Maintenance details
    is_planned = models.BooleanField(default=False)
    scheduled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Additional metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['status', '-started_at']),
            models.Index(fields=['is_planned', '-started_at']),
        ]
    
    def __str__(self):
        return f"{self.status} - {self.started_at}"
    
    def end_period(self):
        """End current uptime/downtime period"""
        if not self.ended_at:
            self.ended_at = timezone.now()
            self.duration_seconds = int((self.ended_at - self.started_at).total_seconds())
            self.save()
    
    @classmethod
    def get_current_status(cls):
        """Get current system status"""
        current = cls.objects.filter(ended_at__isnull=True).first()
        return current.status if current else 'UP'
    
    @classmethod
    def calculate_uptime_percentage(cls, days=30):
        """Calculate uptime percentage for given period"""
        since = timezone.now() - timedelta(days=days)
        periods = cls.objects.filter(started_at__gte=since)
        
        total_seconds = days * 24 * 3600
        down_seconds = 0
        
        for period in periods:
            if period.status in ['DOWN', 'DEGRADED']:
                if period.ended_at:
                    down_seconds += period.duration_seconds or 0
                else:
                    # Ongoing downtime
                    down_seconds += int((timezone.now() - period.started_at).total_seconds())
        
        uptime_seconds = total_seconds - down_seconds
        return (uptime_seconds / total_seconds) * 100 if total_seconds > 0 else 100


class HealthCheckEndpoint(models.Model):
    """External service health check endpoints"""
    
    SERVICE_TYPE_CHOICES = [
        ('DATABASE', 'Database'),
        ('API', 'External API'),
        ('EMAIL', 'Email Service'),
        ('STORAGE', 'File Storage'),
        ('CACHE', 'Cache Service'),
        ('WEBHOOK', 'Webhook Endpoint'),
        ('CUSTOM', 'Custom Service'),
    ]
    
    name = models.CharField(max_length=200)
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPE_CHOICES)
    endpoint_url = models.URLField(max_length=500, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    check_interval_seconds = models.IntegerField(default=300)  # Check every 5 minutes
    timeout_seconds = models.IntegerField(default=30)
    
    # Status
    is_healthy = models.BooleanField(default=True)
    last_checked_at = models.DateTimeField(null=True, blank=True)
    last_success_at = models.DateTimeField(null=True, blank=True)
    last_failure_at = models.DateTimeField(null=True, blank=True)
    consecutive_failures = models.IntegerField(default=0)
    
    # Alerting
    alert_after_failures = models.IntegerField(default=3)
    alert_emails = models.JSONField(default=list, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['is_active', 'is_healthy']),
            models.Index(fields=['-last_checked_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({'Healthy' if self.is_healthy else 'Unhealthy'})"
    
    def record_check_result(self, success, duration_ms=None, error_message=None):
        """Record health check result"""
        self.last_checked_at = timezone.now()
        
        if success:
            self.is_healthy = True
            self.last_success_at = timezone.now()
            self.consecutive_failures = 0
        else:
            self.consecutive_failures += 1
            self.last_failure_at = timezone.now()
            
            if self.consecutive_failures >= self.alert_after_failures:
                self.is_healthy = False
        
        self.save()
        
        # Create check result record
        HealthCheckResult.objects.create(
            endpoint=self,
            success=success,
            duration_ms=duration_ms,
            error_message=error_message
        )


class HealthCheckResult(models.Model):
    """Results from individual health checks"""
    
    endpoint = models.ForeignKey(HealthCheckEndpoint, on_delete=models.CASCADE, related_name='check_results')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    success = models.BooleanField()
    duration_ms = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    response_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['endpoint', '-timestamp']),
            models.Index(fields=['success', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.endpoint.name} - {'Success' if self.success else 'Failed'} - {self.timestamp}"


class AlertRule(models.Model):
    """Configurable alert rules for system monitoring"""
    
    METRIC_CHOICES = [
        ('CPU', 'CPU Usage'),
        ('MEMORY', 'Memory Usage'),
        ('DISK', 'Disk Usage'),
        ('ERROR_RATE', 'Error Rate'),
        ('RESPONSE_TIME', 'Response Time'),
        ('UPTIME', 'System Uptime'),
        ('HEALTH_CHECK', 'Health Check Failure'),
    ]
    
    CONDITION_CHOICES = [
        ('GREATER_THAN', 'Greater Than'),
        ('LESS_THAN', 'Less Than'),
        ('EQUALS', 'Equals'),
    ]
    
    SEVERITY_CHOICES = [
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('CRITICAL', 'Critical'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    metric = models.CharField(max_length=50, choices=METRIC_CHOICES)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    threshold = models.FloatField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    
    # Notification settings
    is_active = models.BooleanField(default=True)
    notification_emails = models.JSONField(default=list, blank=True)
    notification_interval_minutes = models.IntegerField(default=60)  # Prevent spam
    
    # Tracking
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    trigger_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['metric', 'severity']
    
    def __str__(self):
        return f"{self.name} ({self.metric} {self.condition} {self.threshold})"
    
    def check_condition(self, value):
        """Check if alert condition is met"""
        if self.condition == 'GREATER_THAN':
            return value > self.threshold
        elif self.condition == 'LESS_THAN':
            return value < self.threshold
        elif self.condition == 'EQUALS':
            return value == self.threshold
        return False
    
    def should_notify(self):
        """Check if enough time has passed since last notification"""
        if not self.last_triggered_at:
            return True
        
        time_since = timezone.now() - self.last_triggered_at
        return time_since.total_seconds() >= (self.notification_interval_minutes * 60)
    
    def trigger_alert(self):
        """Record alert trigger"""
        self.last_triggered_at = timezone.now()
        self.trigger_count += 1
        self.save()
