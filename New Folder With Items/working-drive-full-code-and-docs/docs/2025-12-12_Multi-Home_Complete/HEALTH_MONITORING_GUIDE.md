# System Health Monitoring Guide

## Overview

The System Health Monitoring system provides comprehensive real-time monitoring of application health, performance metrics, error tracking, and uptime statistics. This enables proactive identification of issues before they impact users.

## Features

### 1. Health Metrics Dashboard
- Real-time system resource monitoring (CPU, Memory, Disk)
- Database performance tracking
- Application response time monitoring
- Error rate tracking
- Active user count
- Visual status indicators (Healthy/Warning/Critical)

### 2. Performance Logging
- HTTP request tracking with duration metrics
- Database query performance analysis
- Background task monitoring
- Report generation timing
- Slow endpoint detection
- Resource usage tracking (CPU, memory per request)

### 3. Error Management
- Centralized error logging
- Error categorization by type and severity
- Duplicate error detection and occurrence tracking
- Error resolution workflow
- Stack trace preservation
- Contextual information (user, endpoint, IP)

### 4. Uptime Tracking
- System uptime/downtime monitoring
- Incident tracking and documentation
- Planned maintenance scheduling
- Root cause analysis
- Uptime percentage calculations (1/7/30 days)
- Affected services tracking

### 5. External Service Health Checks
- Configurable health check endpoints
- Automated periodic checking
- Timeout and retry management
- Success rate tracking
- Alert on consecutive failures

### 6. Alerting System
- Configurable alert rules based on metrics
- Threshold-based triggers
- Email notifications
- Alert history and tracking
- Notification rate limiting (prevent spam)

## Architecture

### Models

#### SystemHealthMetric
Stores real-time health metric data points:
- **Metric Types**: CPU, MEMORY, DISK, DATABASE, RESPONSE_TIME, ERROR_RATE, ACTIVE_USERS
- **Status Levels**: HEALTHY, WARNING, CRITICAL
- **Thresholds**: Configurable warning and critical thresholds
- **Metadata**: Additional context in JSON format

#### PerformanceLog
Detailed performance logging:
- **Log Types**: HTTP, DATABASE, TASK, REPORT
- **Metrics**: Duration (ms), status code, resource usage
- **Context**: Endpoint, user, IP address, user agent
- **Query Tracking**: SQL query text and count

#### ErrorLog
Centralized error tracking:
- **Severity**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Error Types**: EXCEPTION, HTTP_ERROR, DATABASE_ERROR, VALIDATION_ERROR, etc.
- **Resolution**: Workflow for marking errors as resolved
- **Occurrence Tracking**: Automatic duplicate detection and counting

#### SystemUptime
Uptime/downtime period tracking:
- **Status**: UP, DOWN, MAINTENANCE, DEGRADED
- **Incident Details**: Description, affected services, root cause
- **Planned Maintenance**: Scheduling and tracking
- **Duration Tracking**: Automatic calculation

#### HealthCheckEndpoint
External service health monitoring:
- **Service Types**: DATABASE, API, EMAIL, STORAGE, CACHE, WEBHOOK, CUSTOM
- **Check Configuration**: Interval, timeout, retry settings
- **Status Tracking**: Last check time, consecutive failures
- **Alerting**: Configurable failure threshold

#### AlertRule
Configurable monitoring alerts:
- **Metrics**: All health metric types
- **Conditions**: GREATER_THAN, LESS_THAN, EQUALS
- **Severity**: INFO, WARNING, CRITICAL
- **Notifications**: Email alerts with rate limiting

### Service Layer

#### HealthMonitor Class
Main monitoring service providing:

**Metric Collection**:
```python
from scheduling.health_monitor import HealthMonitor

monitor = HealthMonitor()
metrics = monitor.collect_all_metrics()  # Collect all system metrics
```

**External Service Checks**:
```python
results = monitor.check_external_services()  # Check all configured endpoints
```

**Alert Rule Checking**:
```python
triggered = monitor.check_alert_rules()  # Check and trigger alerts
```

**Status Summary**:
```python
status = monitor.get_system_status()  # Get overall health status
```

**Performance Analysis**:
```python
perf = monitor.get_performance_summary(hours=24)  # Get performance stats
```

**Error Analysis**:
```python
errors = monitor.get_error_summary(hours=24)  # Get error statistics
```

## Usage

### Accessing the Dashboard

Navigate to `/health/` to view the main health monitoring dashboard.

**Dashboard Sections**:
1. **System Status Overview**: Current health status with color coding
2. **Latest Metrics**: Most recent values for all metric types
3. **Health Checks**: Status of external service endpoints
4. **Recent Errors**: Latest unresolved errors
5. **Uptime Statistics**: 7-day and 30-day uptime percentages
6. **Performance Summary**: Request counts and average response times

### Viewing Performance Logs

Navigate to `/health/performance/` to view detailed performance logs.

**Filters Available**:
- Log Type: HTTP, DATABASE, TASK, REPORT
- Time Period: Last 1/6/12/24 hours
- Minimum Duration: Filter slow requests
- Pagination: 50 per page

**Statistics Shown**:
- Average duration
- Maximum duration
- Minimum duration
- Total count
- Slow endpoints (for HTTP logs)

### Managing Errors

Navigate to `/health/errors/` to view and manage errors.

**Filters**:
- Severity: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Error Type: EXCEPTION, HTTP_ERROR, etc.
- Resolution Status: Resolved/Unresolved
- Time Period: Customizable

**Error Resolution Workflow**:
1. Click on error to view details
2. Review stack trace and context
3. Add resolution notes
4. Mark as resolved

**Error Statistics**:
- Total errors by period
- Unresolved count
- Critical error count
- Errors by type
- Top occurring errors

### Monitoring Uptime

Navigate to `/health/uptime/` to view uptime history.

**Information Displayed**:
- Current system status
- Uptime percentages (1/7/30 days)
- Incident history
- Downtime duration
- Planned maintenance events

**Incident Details**:
- Start and end times
- Duration
- Status (DOWN, DEGRADED, MAINTENANCE)
- Affected services
- Root cause analysis
- Planned vs unplanned

### Managing Health Checks

Navigate to `/health/checks/` to manage external service health checks.

**Available Actions**:
- View all configured endpoints
- See success rates
- View recent check results
- Manually trigger health check

**Creating Health Check**:
```python
from scheduling.models_health_monitoring import HealthCheckEndpoint

endpoint = HealthCheckEndpoint.objects.create(
    name='External HR API',
    service_type='API',
    endpoint_url='https://hr-api.example.com/health',
    check_interval_seconds=300,  # Check every 5 minutes
    timeout_seconds=30,
    alert_after_failures=3,
    alert_emails=['admin@example.com']
)
```

### Configuring Alert Rules

Navigate to `/health/alerts/` to manage alert rules.

**Creating Alert Rule**:
```python
from scheduling.models_health_monitoring import AlertRule

rule = AlertRule.objects.create(
    name='High CPU Alert',
    description='Alert when CPU usage exceeds 90%',
    metric='CPU',
    condition='GREATER_THAN',
    threshold=90.0,
    severity='CRITICAL',
    notification_emails=['ops@example.com'],
    notification_interval_minutes=60,  # Don't spam
    is_active=True
)
```

**Alert Metrics**:
- CPU, MEMORY, DISK usage
- ERROR_RATE
- RESPONSE_TIME
- UPTIME percentage
- HEALTH_CHECK failures

**Alert Conditions**:
- GREATER_THAN: Trigger when metric exceeds threshold
- LESS_THAN: Trigger when metric falls below threshold
- EQUALS: Trigger when metric equals threshold

## API Endpoints

### Collect Metrics Now
`POST /health/collect-now/`

Manually trigger immediate metric collection.

**Response**:
```json
{
    "status": "success",
    "metrics_collected": 7,
    "services_checked": 3,
    "alerts_triggered": 1,
    "timestamp": "2025-12-30T10:00:00Z"
}
```

### Health Metrics API
`GET /health/metrics/api/?type=CPU&hours=24`

Get time-series data for specific metric type.

**Parameters**:
- `type`: Metric type (CPU, MEMORY, etc.)
- `hours`: Time period (default: 24)

**Response**:
```json
{
    "metric_type": "CPU",
    "period_hours": 24,
    "data": [
        {
            "timestamp": "2025-12-30T09:00:00Z",
            "value": 45.2,
            "status": "HEALTHY",
            "unit": "percent"
        }
    ]
}
```

### System Info API
`GET /health/system-info/`

Get system information and current resource usage.

**Response**:
```json
{
    "system": {
        "platform": "Darwin",
        "platform_release": "23.0.0",
        "architecture": "arm64",
        "processor": "Apple M1",
        "python_version": "3.14.0",
        "django_version": "5.1.4"
    },
    "resources": {
        "cpu_count": 8,
        "cpu_percent": 25.5,
        "memory_total_mb": 16384,
        "memory_available_mb": 8192,
        "memory_percent": 50.0,
        "disk_total_gb": 500,
        "disk_used_gb": 250,
        "disk_percent": 50.0
    }
}
```

### Run Health Check
`POST /health/checks/<endpoint_id>/run/`

Manually trigger health check for specific endpoint.

**Response**:
```json
{
    "status": "success",
    "result": {
        "endpoint": "External HR API",
        "success": true,
        "duration_ms": 125,
        "error_message": null
    },
    "endpoint_status": "healthy"
}
```

## Automated Monitoring

### Setting Up Periodic Collection

To enable automated metric collection, set up a scheduled task (cron job or Django management command):

**Management Command** (create in `scheduling/management/commands/`):
```python
from django.core.management.base import BaseCommand
from scheduling.health_monitor import HealthMonitor

class Command(BaseCommand):
    help = 'Collect system health metrics'
    
    def handle(self, *args, **options):
        monitor = HealthMonitor()
        
        # Collect metrics
        metrics = monitor.collect_all_metrics()
        self.stdout.write(f'Collected {len(metrics)} metrics')
        
        # Check services
        results = monitor.check_external_services()
        self.stdout.write(f'Checked {len(results)} services')
        
        # Check alerts
        alerts = monitor.check_alert_rules()
        if alerts:
            self.stdout.write(f'Triggered {len(alerts)} alerts')
```

**Cron Job** (run every 5 minutes):
```bash
*/5 * * * * cd /path/to/project && python3 manage.py collect_health_metrics
```

## Middleware Integration

### Performance Logging Middleware

Add to `settings.py` to automatically log all HTTP requests:

```python
# scheduling/middleware.py
import time
from django.utils import timezone
from .models_health_monitoring import PerformanceLog

class PerformanceLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Start timing
        start = time.time()
        
        # Process request
        response = self.get_response(request)
        
        # Calculate duration
        duration_ms = int((time.time() - start) * 1000)
        
        # Log performance
        PerformanceLog.objects.create(
            log_type='HTTP',
            endpoint=request.path,
            method=request.method,
            duration_ms=duration_ms,
            status_code=response.status_code,
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            user=request.user if request.user.is_authenticated else None
        )
        
        return response
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

# Add to MIDDLEWARE in settings.py
MIDDLEWARE = [
    # ... other middleware
    'scheduling.middleware.PerformanceLoggingMiddleware',
]
```

### Error Logging Integration

Integrate with Django's logging framework:

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'health_monitor': {
            'level': 'ERROR',
            'class': 'scheduling.logging_handlers.HealthMonitorHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['health_monitor'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# scheduling/logging_handlers.py
import logging
from .models_health_monitoring import ErrorLog

class HealthMonitorHandler(logging.Handler):
    def emit(self, record):
        try:
            ErrorLog.increment_occurrence(
                error_type='EXCEPTION',
                severity=record.levelname,
                message=record.getMessage(),
                stack_trace=self.format(record) if record.exc_info else None
            )
        except Exception:
            self.handleError(record)
```

## Best Practices

### 1. Metric Collection Frequency
- **System Metrics**: Every 5 minutes
- **Database Metrics**: Every 5-10 minutes
- **External Services**: Based on SLA (5-15 minutes)
- **Performance Logs**: Real-time (via middleware)

### 2. Data Retention
Set up periodic cleanup to prevent database bloat:

```python
# Cleanup old metrics (keep 30 days)
from datetime import timedelta
from django.utils import timezone

cutoff = timezone.now() - timedelta(days=30)
SystemHealthMetric.objects.filter(timestamp__lt=cutoff).delete()
PerformanceLog.objects.filter(timestamp__lt=cutoff).delete()

# Keep errors longer (90 days)
cutoff = timezone.now() - timedelta(days=90)
ErrorLog.objects.filter(timestamp__lt=cutoff, is_resolved=True).delete()
```

### 3. Alert Configuration
- Set reasonable thresholds to avoid alert fatigue
- Use notification intervals to prevent spam
- Configure different severity levels appropriately
- Test alerts before production deployment

### 4. Performance Optimization
- Index on timestamp fields for fast queries
- Use aggregation for statistics
- Implement pagination for large result sets
- Cache frequently accessed metrics

### 5. Security Considerations
- Restrict health dashboard to admin users only
- Sanitize error messages to avoid exposing sensitive data
- Use HTTPS for all health check endpoints
- Implement IP whitelisting for monitoring APIs

## Troubleshooting

### High CPU/Memory Usage
1. Check recent metrics: `/health/metrics/api/?type=CPU`
2. Review slow endpoints: `/health/performance/?min_duration=1000`
3. Analyze database queries: Filter by `log_type=DATABASE`
4. Check for error spikes: `/health/errors/`

### Frequent Errors
1. View error logs: `/health/errors/`
2. Group by error type to identify patterns
3. Review stack traces for root cause
4. Check if errors correlate with deployments or load spikes

### Service Downtime
1. Check uptime history: `/health/uptime/`
2. Review health check failures: `/health/checks/`
3. Examine error logs during downtime period
4. Document incident details and root cause

### Slow Response Times
1. Check performance logs: `/health/performance/`
2. Identify slow endpoints with filters
3. Review database query performance
4. Analyze resource usage during slow periods

## Dependencies

Required Python packages:
- `psutil`: System resource monitoring
- `requests`: HTTP health checks
- Django 5.1.4+

Install dependencies:
```bash
pip install psutil requests
```

## Migration

Migration created: `0045_alertrule_errorlog_healthcheckendpoint_systemuptime_and_more.py`

Apply migration:
```bash
python manage.py migrate scheduling
```

## Related Documentation

- [Performance Optimization Guide](PERFORMANCE_GUIDE.md)
- [Error Handling Best Practices](ERROR_HANDLING.md)
- [Monitoring and Alerting](MONITORING.md)
- [Production Deployment](DEPLOYMENT.md)
