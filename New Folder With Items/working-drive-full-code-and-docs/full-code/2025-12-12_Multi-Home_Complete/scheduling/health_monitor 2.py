"""
System Health Monitoring Service
Collects and analyzes system health metrics
"""
import psutil
import time
from django.db import connection
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import requests
from .models_health_monitoring import (
    SystemHealthMetric, PerformanceLog, ErrorLog,
    SystemUptime, HealthCheckEndpoint, AlertRule
)


class HealthMonitor:
    """Main health monitoring service"""
    
    def __init__(self):
        self.start_time = time.time()
    
    def collect_all_metrics(self):
        """Collect all system health metrics"""
        metrics = []
        
        # System metrics
        metrics.append(self.collect_cpu_metric())
        metrics.append(self.collect_memory_metric())
        metrics.append(self.collect_disk_metric())
        
        # Database metrics
        db_metric = self.collect_database_metric()
        if db_metric:
            metrics.append(db_metric)
        
        # Application metrics
        metrics.append(self.collect_response_time_metric())
        metrics.append(self.collect_error_rate_metric())
        metrics.append(self.collect_active_users_metric())
        
        return [m for m in metrics if m]
    
    def collect_cpu_metric(self):
        """Collect CPU usage metric"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            metric = SystemHealthMetric.objects.create(
                metric_type='CPU',
                value=cpu_percent,
                unit='percent',
                threshold_warning=75.0,
                threshold_critical=90.0
            )
            metric.update_status()
            metric.save()
            return metric
        except Exception as e:
            ErrorLog.increment_occurrence(
                error_type='EXCEPTION',
                severity='ERROR',
                message=f"Failed to collect CPU metric: {str(e)}"
            )
            return None
    
    def collect_memory_metric(self):
        """Collect memory usage metric"""
        try:
            memory = psutil.virtual_memory()
            metric = SystemHealthMetric.objects.create(
                metric_type='MEMORY',
                value=memory.percent,
                unit='percent',
                threshold_warning=80.0,
                threshold_critical=95.0,
                metadata={
                    'total_mb': round(memory.total / 1024 / 1024, 2),
                    'available_mb': round(memory.available / 1024 / 1024, 2),
                    'used_mb': round(memory.used / 1024 / 1024, 2),
                }
            )
            metric.update_status()
            metric.save()
            return metric
        except Exception as e:
            ErrorLog.increment_occurrence(
                error_type='EXCEPTION',
                severity='ERROR',
                message=f"Failed to collect memory metric: {str(e)}"
            )
            return None
    
    def collect_disk_metric(self):
        """Collect disk usage metric"""
        try:
            disk = psutil.disk_usage('/')
            metric = SystemHealthMetric.objects.create(
                metric_type='DISK',
                value=disk.percent,
                unit='percent',
                threshold_warning=85.0,
                threshold_critical=95.0,
                metadata={
                    'total_gb': round(disk.total / 1024 / 1024 / 1024, 2),
                    'used_gb': round(disk.used / 1024 / 1024 / 1024, 2),
                    'free_gb': round(disk.free / 1024 / 1024 / 1024, 2),
                }
            )
            metric.update_status()
            metric.save()
            return metric
        except Exception as e:
            ErrorLog.increment_occurrence(
                error_type='EXCEPTION',
                severity='ERROR',
                message=f"Failed to collect disk metric: {str(e)}"
            )
            return None
    
    def collect_database_metric(self):
        """Collect database performance metric"""
        try:
            start = time.time()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            duration_ms = (time.time() - start) * 1000
            
            metric = SystemHealthMetric.objects.create(
                metric_type='DATABASE',
                value=duration_ms,
                unit='ms',
                threshold_warning=100.0,
                threshold_critical=500.0,
                metadata={
                    'connection_count': len(connection.queries),
                }
            )
            metric.update_status()
            metric.save()
            return metric
        except Exception as e:
            ErrorLog.increment_occurrence(
                error_type='DATABASE_ERROR',
                severity='CRITICAL',
                message=f"Database health check failed: {str(e)}"
            )
            return None
    
    def collect_response_time_metric(self):
        """Collect average response time from recent performance logs"""
        try:
            one_hour_ago = timezone.now() - timedelta(hours=1)
            logs = PerformanceLog.objects.filter(
                log_type='HTTP',
                timestamp__gte=one_hour_ago
            )
            
            if logs.exists():
                avg_duration = logs.aggregate(avg=models.Avg('duration_ms'))['avg'] or 0
            else:
                avg_duration = 0
            
            metric = SystemHealthMetric.objects.create(
                metric_type='RESPONSE_TIME',
                value=avg_duration,
                unit='ms',
                threshold_warning=300.0,
                threshold_critical=1000.0,
                metadata={
                    'request_count': logs.count(),
                    'period': '1 hour',
                }
            )
            metric.update_status()
            metric.save()
            return metric
        except Exception as e:
            ErrorLog.increment_occurrence(
                error_type='EXCEPTION',
                severity='ERROR',
                message=f"Failed to collect response time metric: {str(e)}"
            )
            return None
    
    def collect_error_rate_metric(self):
        """Collect error rate from recent error logs"""
        try:
            one_hour_ago = timezone.now() - timedelta(hours=1)
            
            # Count errors in last hour
            error_count = ErrorLog.objects.filter(
                timestamp__gte=one_hour_ago,
                severity__in=['ERROR', 'CRITICAL']
            ).count()
            
            # Count total requests
            request_count = PerformanceLog.objects.filter(
                log_type='HTTP',
                timestamp__gte=one_hour_ago
            ).count()
            
            # Calculate error rate as percentage
            if request_count > 0:
                error_rate = (error_count / request_count) * 100
            else:
                error_rate = 0
            
            metric = SystemHealthMetric.objects.create(
                metric_type='ERROR_RATE',
                value=error_rate,
                unit='percent',
                threshold_warning=5.0,
                threshold_critical=10.0,
                metadata={
                    'error_count': error_count,
                    'request_count': request_count,
                    'period': '1 hour',
                }
            )
            metric.update_status()
            metric.save()
            return metric
        except Exception as e:
            ErrorLog.increment_occurrence(
                error_type='EXCEPTION',
                severity='ERROR',
                message=f"Failed to collect error rate metric: {str(e)}"
            )
            return None
    
    def collect_active_users_metric(self):
        """Collect active user count from cache or sessions"""
        try:
            # Try to get from cache
            active_count = cache.get('active_users_count', 0)
            
            metric = SystemHealthMetric.objects.create(
                metric_type='ACTIVE_USERS',
                value=active_count,
                unit='count',
                metadata={
                    'source': 'cache',
                    'period': 'current',
                }
            )
            return metric
        except Exception as e:
            ErrorLog.increment_occurrence(
                error_type='EXCEPTION',
                severity='WARNING',
                message=f"Failed to collect active users metric: {str(e)}"
            )
            return None
    
    def check_external_services(self):
        """Check health of external service endpoints"""
        endpoints = HealthCheckEndpoint.objects.filter(is_active=True)
        results = []
        
        for endpoint in endpoints:
            # Check if it's time to run check
            if endpoint.last_checked_at:
                time_since_check = (timezone.now() - endpoint.last_checked_at).total_seconds()
                if time_since_check < endpoint.check_interval_seconds:
                    continue
            
            result = self._check_endpoint(endpoint)
            results.append(result)
        
        return results
    
    def _check_endpoint(self, endpoint):
        """Perform health check on single endpoint"""
        start = time.time()
        success = False
        error_message = None
        status_code = None
        
        try:
            if endpoint.service_type == 'DATABASE':
                # Database check
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                success = True
            
            elif endpoint.endpoint_url:
                # HTTP endpoint check
                response = requests.get(
                    endpoint.endpoint_url,
                    timeout=endpoint.timeout_seconds
                )
                status_code = response.status_code
                success = 200 <= status_code < 400
            
            else:
                success = True  # No specific check, assume healthy
        
        except requests.Timeout:
            error_message = f"Request timeout after {endpoint.timeout_seconds}s"
        except requests.RequestException as e:
            error_message = f"Request failed: {str(e)}"
        except Exception as e:
            error_message = f"Health check failed: {str(e)}"
        
        duration_ms = int((time.time() - start) * 1000)
        endpoint.record_check_result(success, duration_ms, error_message)
        
        return {
            'endpoint': endpoint.name,
            'success': success,
            'duration_ms': duration_ms,
            'error_message': error_message,
        }
    
    def check_alert_rules(self):
        """Check all active alert rules and trigger if needed"""
        rules = AlertRule.objects.filter(is_active=True)
        triggered_alerts = []
        
        for rule in rules:
            value = self._get_current_metric_value(rule.metric)
            if value is not None and rule.check_condition(value):
                if rule.should_notify():
                    rule.trigger_alert()
                    triggered_alerts.append({
                        'rule': rule.name,
                        'metric': rule.metric,
                        'value': value,
                        'threshold': rule.threshold,
                        'severity': rule.severity,
                    })
        
        return triggered_alerts
    
    def _get_current_metric_value(self, metric_type):
        """Get most recent value for metric type"""
        try:
            metric = SystemHealthMetric.objects.filter(
                metric_type=metric_type
            ).order_by('-timestamp').first()
            return metric.value if metric else None
        except:
            return None
    
    def get_system_status(self):
        """Get overall system health status"""
        # Get recent metrics (last 5 minutes)
        recent_metrics = SystemHealthMetric.objects.filter(
            timestamp__gte=timezone.now() - timedelta(minutes=5)
        )
        
        # Count by status
        status_counts = {
            'HEALTHY': recent_metrics.filter(status='HEALTHY').count(),
            'WARNING': recent_metrics.filter(status='WARNING').count(),
            'CRITICAL': recent_metrics.filter(status='CRITICAL').count(),
        }
        
        # Determine overall status
        if status_counts['CRITICAL'] > 0:
            overall_status = 'CRITICAL'
        elif status_counts['WARNING'] > 0:
            overall_status = 'WARNING'
        else:
            overall_status = 'HEALTHY'
        
        # Get uptime info
        uptime_percentage = SystemUptime.calculate_uptime_percentage(days=30)
        
        return {
            'status': overall_status,
            'status_counts': status_counts,
            'uptime_percentage_30d': round(uptime_percentage, 2),
            'current_uptime_status': SystemUptime.get_current_status(),
            'metrics_count': recent_metrics.count(),
            'timestamp': timezone.now(),
        }
    
    def get_performance_summary(self, hours=24):
        """Get performance summary for given period"""
        since = timezone.now() - timedelta(hours=hours)
        
        # HTTP performance
        http_logs = PerformanceLog.objects.filter(
            log_type='HTTP',
            timestamp__gte=since
        )
        
        # Database performance
        db_logs = PerformanceLog.objects.filter(
            log_type='DATABASE',
            timestamp__gte=since
        )
        
        return {
            'period_hours': hours,
            'http': {
                'total_requests': http_logs.count(),
                'avg_duration_ms': http_logs.aggregate(avg=models.Avg('duration_ms'))['avg'] or 0,
                'max_duration_ms': http_logs.aggregate(max=models.Max('duration_ms'))['max'] or 0,
                'slow_requests': http_logs.filter(duration_ms__gte=500).count(),
            },
            'database': {
                'total_queries': db_logs.count(),
                'avg_duration_ms': db_logs.aggregate(avg=models.Avg('duration_ms'))['avg'] or 0,
                'slow_queries': db_logs.filter(duration_ms__gte=1000).count(),
            },
        }
    
    def get_error_summary(self, hours=24):
        """Get error summary for given period"""
        since = timezone.now() - timedelta(hours=hours)
        
        errors = ErrorLog.objects.filter(timestamp__gte=since)
        
        return {
            'period_hours': hours,
            'total_errors': errors.count(),
            'by_severity': {
                'CRITICAL': errors.filter(severity='CRITICAL').count(),
                'ERROR': errors.filter(severity='ERROR').count(),
                'WARNING': errors.filter(severity='WARNING').count(),
            },
            'by_type': dict(
                errors.values('error_type').annotate(count=models.Count('id')).values_list('error_type', 'count')
            ),
            'unresolved': errors.filter(is_resolved=False).count(),
            'top_errors': list(
                errors.values('message', 'error_type').annotate(
                    count=models.Sum('occurrence_count')
                ).order_by('-count')[:5]
            ),
        }


# Import here to avoid circular import
from django.db import models
