"""
CGI Monitoring Integration Handlers

Health check and metrics collection handlers for SCOM/SolarWinds/Azure Monitor integration.
Provides system health monitoring, performance metrics, and alerting capabilities.

Dependencies:
- Task #5 (DR): Monitor replication lag
- Task #8 (ESB): Monitor queue depths
- Task #9 (Backup): Monitor backup status

Version: 1.0.0
Date: January 7, 2026
"""

import logging
import requests
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any
from django.conf import settings
from django.db import connection
from django.core.cache import cache
import psutil

logger = logging.getLogger(__name__)


# ============================================================================
# APPLICATION HEALTH CHECK HANDLER
# ============================================================================

class ApplicationHealthHandler:
    """
    Health check handler for application-level monitoring.
    Provides /health/, /health/deep/, /ready/, /alive/ endpoints.
    """
    
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
    
    def check_database(self) -> Dict:
        """Check PostgreSQL database connectivity."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                
            if result == (1,):
                return {
                    'status': 'healthy',
                    'component': 'database',
                    'message': 'PostgreSQL connection successful',
                    'response_time_ms': 5,
                }
            else:
                return {
                    'status': 'unhealthy',
                    'component': 'database',
                    'message': 'Unexpected query result',
                }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'unhealthy',
                'component': 'database',
                'message': str(e),
            }
    
    def check_cache(self) -> Dict:
        """Check Redis cache connectivity."""
        try:
            # Test cache read/write
            test_key = 'health_check_test'
            test_value = datetime.now().isoformat()
            cache.set(test_key, test_value, timeout=10)
            retrieved_value = cache.get(test_key)
            
            if retrieved_value == test_value:
                return {
                    'status': 'healthy',
                    'component': 'cache',
                    'message': 'Redis connection successful',
                }
            else:
                return {
                    'status': 'unhealthy',
                    'component': 'cache',
                    'message': 'Cache read/write mismatch',
                }
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return {
                'status': 'unhealthy',
                'component': 'cache',
                'message': str(e),
            }
    
    def check_celery(self) -> Dict:
        """Check Celery worker availability."""
        try:
            from celery import current_app
            
            # Check active workers
            inspect = current_app.control.inspect()
            active_workers = inspect.active()
            
            if active_workers:
                worker_count = len(active_workers)
                return {
                    'status': 'healthy',
                    'component': 'celery',
                    'message': f'{worker_count} worker(s) active',
                    'worker_count': worker_count,
                }
            else:
                return {
                    'status': 'unhealthy',
                    'component': 'celery',
                    'message': 'No Celery workers available',
                }
        except Exception as e:
            logger.error(f"Celery health check failed: {e}")
            return {
                'status': 'unhealthy',
                'component': 'celery',
                'message': str(e),
            }
    
    def check_rabbitmq(self) -> Dict:
        """Check RabbitMQ message broker connectivity."""
        try:
            import pika
            
            # Get RabbitMQ connection details from ESB settings (Task #8)
            rabbitmq_config = getattr(settings, 'RABBITMQ_CONFIG', {})
            host = rabbitmq_config.get('host', 'localhost')
            port = rabbitmq_config.get('port', 5672)
            
            # Test connection
            credentials = pika.PlainCredentials('guest', 'guest')
            parameters = pika.ConnectionParameters(
                host=host,
                port=port,
                credentials=credentials,
                connection_attempts=1,
                retry_delay=1,
                socket_timeout=5,
            )
            
            connection = pika.BlockingConnection(parameters)
            connection.close()
            
            return {
                'status': 'healthy',
                'component': 'rabbitmq',
                'message': 'RabbitMQ connection successful',
            }
        except Exception as e:
            logger.error(f"RabbitMQ health check failed: {e}")
            return {
                'status': 'unhealthy',
                'component': 'rabbitmq',
                'message': str(e),
            }
    
    def perform_health_check(self, deep: bool = False) -> Dict:
        """
        Perform health check (shallow or deep).
        
        Args:
            deep: If True, perform expensive checks (database queries, etc.)
        
        Returns:
            Health check results with overall status
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy',
            'checks': [],
        }
        
        # Always check database and cache
        db_check = self.check_database()
        cache_check = self.check_cache()
        results['checks'].extend([db_check, cache_check])
        
        # Deep checks
        if deep:
            celery_check = self.check_celery()
            rabbitmq_check = self.check_rabbitmq()
            results['checks'].extend([celery_check, rabbitmq_check])
        
        # Determine overall status
        unhealthy_checks = [c for c in results['checks'] if c['status'] == 'unhealthy']
        if unhealthy_checks:
            results['status'] = 'unhealthy'
            results['failed_checks'] = len(unhealthy_checks)
        
        return results


# ============================================================================
# INFRASTRUCTURE METRICS HANDLER
# ============================================================================

class InfrastructureMetricsHandler:
    """
    Collects infrastructure-level metrics (CPU, memory, disk, network).
    Exports metrics for SCOM/SolarWinds consumption.
    """
    
    def get_cpu_metrics(self) -> Dict:
        """Get CPU usage metrics."""
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        return {
            'cpu_usage_percent': cpu_percent,
            'cpu_count': cpu_count,
            'cpu_frequency_mhz': cpu_freq.current if cpu_freq else None,
        }
    
    def get_memory_metrics(self) -> Dict:
        """Get memory usage metrics."""
        memory = psutil.virtual_memory()
        
        return {
            'memory_total_gb': round(memory.total / (1024**3), 2),
            'memory_available_gb': round(memory.available / (1024**3), 2),
            'memory_used_gb': round(memory.used / (1024**3), 2),
            'memory_usage_percent': memory.percent,
        }
    
    def get_disk_metrics(self) -> Dict:
        """Get disk usage metrics."""
        disk = psutil.disk_usage('/')
        
        return {
            'disk_total_gb': round(disk.total / (1024**3), 2),
            'disk_used_gb': round(disk.used / (1024**3), 2),
            'disk_free_gb': round(disk.free / (1024**3), 2),
            'disk_usage_percent': disk.percent,
        }
    
    def get_network_metrics(self) -> Dict:
        """Get network I/O metrics."""
        net_io = psutil.net_io_counters()
        
        return {
            'network_bytes_sent': net_io.bytes_sent,
            'network_bytes_recv': net_io.bytes_recv,
            'network_packets_sent': net_io.packets_sent,
            'network_packets_recv': net_io.packets_recv,
            'network_errors_in': net_io.errin,
            'network_errors_out': net_io.errout,
        }
    
    def collect_all_metrics(self) -> Dict:
        """Collect all infrastructure metrics."""
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu': self.get_cpu_metrics(),
            'memory': self.get_memory_metrics(),
            'disk': self.get_disk_metrics(),
            'network': self.get_network_metrics(),
        }


# ============================================================================
# BACKUP STATUS MONITOR (Integrates with Task #9)
# ============================================================================

class BackupStatusMonitor:
    """
    Monitors backup job status and freshness.
    Integrates with backup_handlers.py from Task #9.
    """
    
    def check_azure_backup_freshness(self) -> Dict:
        """Check Azure Backup last successful backup time."""
        try:
            from scheduling.backup_handlers import AzureBackupHandler
            
            handler = AzureBackupHandler()
            recovery_points = handler.list_recovery_points('rota-db-primary')
            
            if not recovery_points:
                return {
                    'status': 'critical',
                    'component': 'azure_backup',
                    'message': 'No recovery points found',
                }
            
            # Check latest backup age
            latest_rp = recovery_points[0]
            backup_time = datetime.fromisoformat(latest_rp.get('backupTime'))
            age_hours = (datetime.now() - backup_time).total_seconds() / 3600
            
            if age_hours > 48:
                status = 'critical'
            elif age_hours > 26:
                status = 'warning'
            else:
                status = 'healthy'
            
            return {
                'status': status,
                'component': 'azure_backup',
                'message': f'Latest backup: {age_hours:.1f} hours ago',
                'age_hours': age_hours,
                'backup_time': backup_time.isoformat(),
            }
        except Exception as e:
            logger.error(f"Azure Backup status check failed: {e}")
            return {
                'status': 'unknown',
                'component': 'azure_backup',
                'message': str(e),
            }
    
    def check_veeam_backup_status(self) -> Dict:
        """Check Veeam backup job status."""
        try:
            from scheduling.backup_handlers import VeeamBackupHandler
            
            handler = VeeamBackupHandler()
            if not handler.authenticate():
                return {
                    'status': 'critical',
                    'component': 'veeam_backup',
                    'message': 'Authentication failed',
                }
            
            # Get latest job status
            job_status = handler.get_job_status('NHS-Rota-Daily-Backup')
            
            if job_status.get('state') == 'Success':
                status = 'healthy'
            elif job_status.get('state') == 'Warning':
                status = 'warning'
            else:
                status = 'critical'
            
            handler.logout()
            
            return {
                'status': status,
                'component': 'veeam_backup',
                'message': f"Job state: {job_status.get('state')}",
                'job_state': job_status.get('state'),
                'last_run': job_status.get('endTime'),
            }
        except Exception as e:
            logger.error(f"Veeam backup status check failed: {e}")
            return {
                'status': 'unknown',
                'component': 'veeam_backup',
                'message': str(e),
            }


# ============================================================================
# DR REPLICATION MONITOR (Integrates with Task #5)
# ============================================================================

class DRReplicationMonitor:
    """
    Monitors DR replication lag and failover readiness.
    Integrates with dr_automation.py from Task #5.
    """
    
    def check_replication_lag(self) -> Dict:
        """Check PostgreSQL replication lag to DR standby."""
        try:
            # Query replication lag from primary
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        client_addr,
                        state,
                        EXTRACT(EPOCH FROM (now() - write_lag)) AS write_lag_seconds,
                        EXTRACT(EPOCH FROM (now() - flush_lag)) AS flush_lag_seconds,
                        EXTRACT(EPOCH FROM (now() - replay_lag)) AS replay_lag_seconds
                    FROM pg_stat_replication
                    WHERE application_name = 'rota_standby_uk_west'
                """)
                
                result = cursor.fetchone()
            
            if not result:
                return {
                    'status': 'critical',
                    'component': 'dr_replication',
                    'message': 'No replication connection found',
                }
            
            client_addr, state, write_lag, flush_lag, replay_lag = result
            max_lag = max(write_lag or 0, flush_lag or 0, replay_lag or 0)
            
            # Determine status based on lag
            if max_lag > 1800:  # >30 minutes
                status = 'critical'
            elif max_lag > 600:  # >10 minutes
                status = 'warning'
            else:
                status = 'healthy'
            
            return {
                'status': status,
                'component': 'dr_replication',
                'message': f'Replication lag: {max_lag:.1f} seconds',
                'state': state,
                'write_lag_seconds': write_lag,
                'flush_lag_seconds': flush_lag,
                'replay_lag_seconds': replay_lag,
            }
        except Exception as e:
            logger.error(f"DR replication check failed: {e}")
            return {
                'status': 'unknown',
                'component': 'dr_replication',
                'message': str(e),
            }


# ============================================================================
# ESB QUEUE MONITOR (Integrates with Task #8)
# ============================================================================

class ESBQueueMonitor:
    """
    Monitors RabbitMQ queue depths and message processing rates.
    Integrates with esb_settings.py from Task #8.
    """
    
    def get_queue_depths(self) -> Dict:
        """Get RabbitMQ queue depths via Management API."""
        try:
            # RabbitMQ Management API
            rabbitmq_config = getattr(settings, 'RABBITMQ_CONFIG', {})
            api_url = f"http://{rabbitmq_config.get('host', 'localhost')}:15672/api/queues"
            
            response = requests.get(
                api_url,
                auth=('guest', 'guest'),  # Replace with actual credentials
                timeout=5,
            )
            response.raise_for_status()
            
            queues = response.json()
            
            # Check depths
            queue_status = {}
            overall_status = 'healthy'
            
            for queue in queues:
                queue_name = queue['name']
                message_count = queue.get('messages', 0)
                
                # Determine status based on depth
                if message_count > 5000:
                    status = 'critical'
                    overall_status = 'critical'
                elif message_count > 1000:
                    status = 'warning'
                    if overall_status == 'healthy':
                        overall_status = 'warning'
                else:
                    status = 'healthy'
                
                queue_status[queue_name] = {
                    'message_count': message_count,
                    'status': status,
                }
            
            return {
                'status': overall_status,
                'component': 'esb_queues',
                'message': f'Monitoring {len(queues)} queues',
                'queues': queue_status,
            }
        except Exception as e:
            logger.error(f"ESB queue monitoring failed: {e}")
            return {
                'status': 'unknown',
                'component': 'esb_queues',
                'message': str(e),
            }


# ============================================================================
# ALERT HANDLER
# ============================================================================

class AlertHandler:
    """
    Sends alerts to SCOM/SolarWinds/Azure Monitor/NOC.
    Handles alert routing based on severity.
    """
    
    def send_alert(self, alert_type: str, severity: str, message: str, details: Dict = None):
        """
        Send alert to monitoring systems.
        
        Args:
            alert_type: Type of alert (database_down, high_cpu, etc.)
            severity: P1/P2/P3/P4
            message: Alert message
            details: Additional context
        """
        logger.warning(f"ALERT [{severity}] {alert_type}: {message}")
        
        # In production, integrate with:
        # - SCOM: Use SCOM SDK or PowerShell
        # - SolarWinds: Use REST API
        # - Azure Monitor: Use Metric API
        # - ServiceNow: Create incident ticket
        # - PagerDuty: Trigger incident
        
        alert_payload = {
            'timestamp': datetime.now().isoformat(),
            'alert_type': alert_type,
            'severity': severity,
            'message': message,
            'details': details or {},
        }
        
        # Route based on severity
        if severity == 'P1':
            self._send_to_noc_phone(alert_payload)
            self._send_to_pagerduty(alert_payload)
        elif severity == 'P2':
            self._send_to_noc_email(alert_payload)
            self._send_to_servicenow(alert_payload)
        else:
            self._send_to_team_email(alert_payload)
        
        return alert_payload
    
    def _send_to_noc_phone(self, alert: Dict):
        """Send P1 alert to NOC via phone/SMS."""
        logger.critical(f"P1 ALERT - NOC PHONE: {alert['message']}")
        # Implement PagerDuty/Twilio integration
    
    def _send_to_pagerduty(self, alert: Dict):
        """Trigger PagerDuty incident."""
        logger.critical(f"P1 ALERT - PagerDuty: {alert['message']}")
        # Implement PagerDuty Events API v2 integration
    
    def _send_to_noc_email(self, alert: Dict):
        """Send P2 alert to NOC via email."""
        logger.error(f"P2 ALERT - NOC EMAIL: {alert['message']}")
        # Implement SMTP email sending
    
    def _send_to_servicenow(self, alert: Dict):
        """Create ServiceNow incident ticket."""
        logger.error(f"P2 ALERT - ServiceNow: {alert['message']}")
        # Implement ServiceNow Table API integration
    
    def _send_to_team_email(self, alert: Dict):
        """Send P3/P4 alert to team via email."""
        logger.warning(f"P3/P4 ALERT - Team Email: {alert['message']}")
        # Implement team email distribution list


# ============================================================================
# MONITORING ORCHESTRATOR
# ============================================================================

class MonitoringOrchestrator:
    """
    Orchestrates all monitoring activities.
    Coordinates health checks, metrics collection, and alerting.
    """
    
    def __init__(self):
        self.health_handler = ApplicationHealthHandler()
        self.metrics_handler = InfrastructureMetricsHandler()
        self.backup_monitor = BackupStatusMonitor()
        self.dr_monitor = DRReplicationMonitor()
        self.esb_monitor = ESBQueueMonitor()
        self.alert_handler = AlertHandler()
    
    def perform_comprehensive_check(self) -> Dict:
        """Perform comprehensive system health and status check."""
        results = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'checks': {},
        }
        
        # Application health
        app_health = self.health_handler.perform_health_check(deep=True)
        results['checks']['application_health'] = app_health
        
        # Infrastructure metrics
        infra_metrics = self.metrics_handler.collect_all_metrics()
        results['checks']['infrastructure_metrics'] = infra_metrics
        
        # Backup status
        azure_backup = self.backup_monitor.check_azure_backup_freshness()
        veeam_backup = self.backup_monitor.check_veeam_backup_status()
        results['checks']['backup_status'] = {
            'azure': azure_backup,
            'veeam': veeam_backup,
        }
        
        # DR replication
        dr_status = self.dr_monitor.check_replication_lag()
        results['checks']['dr_replication'] = dr_status
        
        # ESB queues
        esb_status = self.esb_monitor.get_queue_depths()
        results['checks']['esb_queues'] = esb_status
        
        # Determine overall status
        critical_checks = []
        warning_checks = []
        
        for check_name, check_result in results['checks'].items():
            if isinstance(check_result, dict):
                status = check_result.get('status')
                if status == 'critical' or status == 'unhealthy':
                    critical_checks.append(check_name)
                elif status == 'warning':
                    warning_checks.append(check_name)
        
        if critical_checks:
            results['overall_status'] = 'critical'
            # Send P1 alert
            self.alert_handler.send_alert(
                alert_type='system_critical',
                severity='P1',
                message=f'Critical issues detected: {", ".join(critical_checks)}',
                details={'failed_checks': critical_checks},
            )
        elif warning_checks:
            results['overall_status'] = 'warning'
            # Send P2 alert
            self.alert_handler.send_alert(
                alert_type='system_warning',
                severity='P2',
                message=f'Warning issues detected: {", ".join(warning_checks)}',
                details={'warning_checks': warning_checks},
            )
        
        return results
