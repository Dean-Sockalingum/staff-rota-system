"""
SIEM Logging Handlers for Staff Rota System
===========================================

Custom logging handlers for forwarding logs to CGI Splunk and ELK/Logstash infrastructure.

Features:
- Dual SIEM platform support (Splunk HEC + Logstash)
- Structured JSON logging with mandatory fields
- Automatic retry with exponential backoff
- Local buffering during network outages
- Correlation ID injection for request tracking
- Security event enrichment
- Performance: Async logging to avoid blocking requests

Author: Staff Rota Development Team
Date: January 2026
"""

import logging
import json
import time
import socket
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List
from queue import Queue, Full
from threading import Thread, Lock
import hashlib

# SIEM platform libraries (graceful import failure for dev environments)
try:
    import logstash
    LOGSTASH_AVAILABLE = True
except ImportError:
    LOGSTASH_AVAILABLE = False
    logging.warning("python-logstash not installed. ELK integration disabled.")

try:
    from splunk_hec_handler import SplunkHecHandler
    SPLUNK_AVAILABLE = True
except ImportError:
    # Alternative: Manual HTTP Event Collector implementation
    try:
        import requests
        SPLUNK_AVAILABLE = True
    except ImportError:
        SPLUNK_AVAILABLE = False
        logging.warning("splunk-sdk not installed. Splunk integration disabled.")

from django.conf import settings
from rotasystems import siem_settings


class StructuredLogFormatter(logging.Formatter):
    """
    Custom log formatter that produces structured JSON logs with mandatory SIEM fields.
    
    Includes:
    - Timestamp (ISO 8601)
    - Severity level
    - Component/logger name
    - Message
    - Correlation ID (from request context)
    - Exception details (stack trace, type, message)
    - Security context (user, IP, auth method)
    """
    
    def __init__(self):
        super().__init__()
        self.hostname = socket.gethostname()
        
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as structured JSON.
        
        Args:
            record: Python logging.LogRecord instance
            
        Returns:
            JSON string with all SIEM mandatory fields
        """
        # Build base log structure with mandatory fields
        log_data = {
            'timestamp': datetime.utcfromtimestamp(record.created).isoformat() + 'Z',
            'severity': record.levelname,
            'component': record.name,
            'message': record.getMessage(),
            'hostname': self.hostname,
            'environment': getattr(settings, 'ENVIRONMENT', 'production'),
        }
        
        # Add correlation ID if available (from middleware)
        if hasattr(record, 'correlation_id'):
            log_data['correlation_id'] = record.correlation_id
        else:
            # Generate correlation ID from thread/process info
            log_data['correlation_id'] = self._generate_correlation_id(record)
        
        # Add event type if specified
        if hasattr(record, 'event_type'):
            log_data['event_type'] = record.event_type
        else:
            log_data['event_type'] = self._infer_event_type(record)
        
        # Add optional fields if available
        optional_fields = [
            'user_id', 'username', 'session_id', 'ip_address', 'user_agent',
            'request_method', 'request_path', 'request_params', 'response_code',
            'response_time_ms', 'care_home', 'unit', 'affected_records',
            'auth_method', 'permission_required', 'permission_granted', 'role',
        ]
        
        for field in optional_fields:
            if hasattr(record, field):
                log_data[field] = getattr(record, field)
        
        # Add exception information if present
        if record.exc_info:
            log_data['error_type'] = record.exc_info[0].__name__
            log_data['error_message'] = str(record.exc_info[1])
            log_data['stack_trace'] = self.formatException(record.exc_info)
        
        # Add SQL query info if present (for slow query logging)
        if hasattr(record, 'sql_query'):
            log_data['sql_query'] = self._sanitize_sql(record.sql_query)
            log_data['query_duration_ms'] = getattr(record, 'query_duration_ms', None)
        
        # Add security context if present
        if hasattr(record, 'threat_indicators'):
            log_data['threat_indicators'] = record.threat_indicators
            log_data['severity'] = 'CRITICAL'  # Escalate security threats
        
        # Add compliance fields if present
        compliance_fields = ['data_subject', 'legal_basis', 'retention_period', 'audit_trail_id']
        for field in compliance_fields:
            if hasattr(record, field):
                log_data[field] = getattr(record, field)
        
        return json.dumps(log_data)
    
    def _generate_correlation_id(self, record: logging.LogRecord) -> str:
        """Generate unique correlation ID from record metadata."""
        correlation_input = f"{record.created}-{record.thread}-{record.process}"
        return hashlib.md5(correlation_input.encode()).hexdigest()[:16]
    
    def _infer_event_type(self, record: logging.LogRecord) -> str:
        """Infer event type from logger name and message."""
        logger_name = record.name.lower()
        message = record.getMessage().lower()
        
        # Map logger names to event types
        if 'auth' in logger_name or 'login' in message:
            return 'authentication'
        elif 'permission' in logger_name or 'access denied' in message:
            return 'authorization'
        elif 'django.db' in logger_name or 'sql' in message:
            return 'database_query'
        elif 'security' in logger_name or 'attack' in message:
            return 'security_incident'
        elif record.levelname in ('ERROR', 'CRITICAL'):
            return 'application_error'
        else:
            return 'system_event'
    
    def _sanitize_sql(self, sql_query: str) -> str:
        """
        Sanitize SQL query to remove sensitive data before logging.
        
        Replaces literal values with placeholders to prevent PII leakage.
        """
        # Simple sanitization: Replace string literals
        import re
        sanitized = re.sub(r"'[^']*'", "'***'", sql_query)
        sanitized = re.sub(r'\b\d{4,}\b', '***', sanitized)  # Replace long numbers (SAP, etc.)
        return sanitized[:1000]  # Truncate to prevent huge logs


class SplunkHECHandler(logging.Handler):
    """
    Custom logging handler for Splunk HTTP Event Collector (HEC).
    
    Sends structured JSON logs to CGI Splunk infrastructure via HEC REST API.
    Includes retry logic, buffering, and automatic failover.
    """
    
    def __init__(self):
        super().__init__()
        self.enabled = siem_settings.SIEM_ENABLED.get('splunk', False)
        
        if not self.enabled:
            return
        
        if not SPLUNK_AVAILABLE:
            logging.error("Splunk integration enabled but splunk-sdk/requests not installed")
            self.enabled = False
            return
        
        # Splunk HEC configuration
        self.config = siem_settings.SPLUNK_CONFIG
        self.hec_url = f"{self.config['protocol']}://{self.config['host']}:{self.config['port']}/services/collector/event"
        self.headers = {
            'Authorization': f"Splunk {self.config['token']}",
            'Content-Type': 'application/json',
        }
        
        # Buffer for network outage resilience
        self.buffer = Queue(maxsize=self.config['queue_size'])
        self.lock = Lock()
        
        # Start background thread for async log forwarding
        self.flush_thread = Thread(target=self._flush_worker, daemon=True)
        self.flush_thread.start()
        
        logging.info(f"Splunk HEC handler initialized: {self.config['host']}:{self.config['port']}")
    
    def emit(self, record: logging.LogRecord):
        """
        Emit log record to Splunk HEC.
        
        Args:
            record: Python logging.LogRecord instance
        """
        if not self.enabled:
            return
        
        try:
            # Format record as JSON
            log_message = self.format(record)
            log_data = json.loads(log_message)
            
            # Build Splunk HEC event format
            splunk_event = {
                'time': record.created,
                'host': socket.gethostname(),
                'source': 'staff_rota_system',
                'sourcetype': self.config['sourcetype'],
                'index': self.config['index'],
                'event': log_data,
            }
            
            # Add to buffer (non-blocking)
            try:
                self.buffer.put_nowait(splunk_event)
            except Full:
                # Buffer full - drop oldest event and log warning
                logging.warning("Splunk HEC buffer full. Dropping oldest event.")
                try:
                    self.buffer.get_nowait()
                    self.buffer.put_nowait(splunk_event)
                except Exception as e:
                    logging.error(f"Failed to rotate Splunk buffer: {e}")
        
        except Exception as e:
            # Never let logging errors crash the application
            logging.error(f"Splunk HEC handler error: {e}")
            self.handleError(record)
    
    def _flush_worker(self):
        """
        Background thread that flushes buffered logs to Splunk HEC.
        
        Runs every flush_interval seconds, sends batched events.
        """
        import requests
        
        while True:
            try:
                time.sleep(self.config['flush_interval'])
                
                # Collect batch of events from buffer
                events = []
                while not self.buffer.empty() and len(events) < 100:
                    try:
                        events.append(self.buffer.get_nowait())
                    except Exception:
                        break
                
                if not events:
                    continue
                
                # Send batch to Splunk HEC
                self._send_batch(events)
            
            except Exception as e:
                logging.error(f"Splunk flush worker error: {e}")
                time.sleep(60)  # Back off on errors
    
    def _send_batch(self, events: List[Dict[str, Any]]):
        """
        Send batch of events to Splunk HEC with retry logic.
        
        Args:
            events: List of Splunk HEC event dictionaries
        """
        import requests
        
        retry_count = 0
        backoff = 1
        
        while retry_count < self.config['retry_count']:
            try:
                # Send batch as newline-delimited JSON
                payload = '\n'.join([json.dumps(event) for event in events])
                
                response = requests.post(
                    self.hec_url,
                    headers=self.headers,
                    data=payload,
                    timeout=self.config['timeout'],
                    verify=self.config['verify_ssl'],
                )
                
                if response.status_code == 200:
                    logging.debug(f"Sent {len(events)} events to Splunk HEC")
                    return
                else:
                    logging.warning(f"Splunk HEC error {response.status_code}: {response.text}")
                    retry_count += 1
                    time.sleep(backoff)
                    backoff *= self.config['retry_backoff']
            
            except requests.exceptions.RequestException as e:
                logging.warning(f"Splunk HEC connection error: {e}")
                retry_count += 1
                time.sleep(backoff)
                backoff *= self.config['retry_backoff']
        
        # Failed after retries - put events back in buffer
        logging.error(f"Failed to send {len(events)} events to Splunk after {retry_count} retries")
        for event in events:
            try:
                self.buffer.put_nowait(event)
            except Full:
                logging.warning("Splunk buffer full, dropping event")
                break


class LogstashHandler(logging.Handler):
    """
    Custom logging handler for ELK (Elasticsearch, Logstash, Kibana) stack.
    
    Sends structured JSON logs to CGI Logstash infrastructure via TCP/UDP.
    """
    
    def __init__(self):
        super().__init__()
        self.enabled = siem_settings.SIEM_ENABLED.get('elk', False)
        
        if not self.enabled:
            return
        
        if not LOGSTASH_AVAILABLE:
            logging.error("ELK integration enabled but python-logstash not installed")
            self.enabled = False
            return
        
        # Logstash configuration
        self.config = siem_settings.ELK_CONFIG
        
        # Initialize python-logstash handler
        try:
            if self.config['protocol'] == 'tcp':
                self.logstash_handler = logstash.TCPLogstashHandler(
                    host=self.config['host'],
                    port=self.config['port'],
                    version=self.config['version'],
                    message_type=self.config['message_type'],
                    tags=self.config['tags'],
                )
            else:  # UDP
                self.logstash_handler = logstash.UDPLogstashHandler(
                    host=self.config['host'],
                    port=self.config['port'],
                    version=self.config['version'],
                    message_type=self.config['message_type'],
                    tags=self.config['tags'],
                )
            
            logging.info(f"Logstash handler initialized: {self.config['host']}:{self.config['port']}")
        
        except Exception as e:
            logging.error(f"Failed to initialize Logstash handler: {e}")
            self.enabled = False
    
    def emit(self, record: logging.LogRecord):
        """
        Emit log record to Logstash.
        
        Args:
            record: Python logging.LogRecord instance
        """
        if not self.enabled:
            return
        
        try:
            # Add ELK-specific fields
            record.index_pattern = self.config['index_pattern']
            record.doc_type = self.config['doc_type']
            
            # Forward to python-logstash handler
            self.logstash_handler.emit(record)
        
        except Exception as e:
            logging.error(f"Logstash handler error: {e}")
            self.handleError(record)


class SIEMLogger:
    """
    High-level SIEM logging interface for application code.
    
    Usage:
        from rotasystems.siem_logging import siem_logger
        
        siem_logger.log_authentication(
            username='admin',
            success=True,
            ip_address='192.168.1.100',
            auth_method='SAML',
        )
        
        siem_logger.log_data_access(
            user_id=123,
            event_type='export_data',
            records=500,
            care_home='Oakridge Manor',
        )
        
        siem_logger.log_security_incident(
            incident_type='sql_injection_attempt',
            severity='P1',
            threat_indicators=['malicious_payload', 'attack_pattern_detected'],
        )
    """
    
    def __init__(self):
        self.logger = logging.getLogger('siem')
        self.logger.setLevel(logging.INFO)
    
    def log_authentication(self, username: str, success: bool, **kwargs):
        """
        Log authentication event.
        
        Args:
            username: User attempting authentication
            success: Whether authentication succeeded
            **kwargs: Additional context (ip_address, auth_method, mfa_status, etc.)
        """
        event_type = 'login_success' if success else 'login_failure'
        severity = logging.INFO if success else logging.WARNING
        
        extra = {
            'event_type': event_type,
            'username': username,
            **kwargs,
        }
        
        message = f"Authentication {'succeeded' if success else 'failed'} for user {username}"
        self.logger.log(severity, message, extra=extra)
    
    def log_authorization(self, user_id: int, permission: str, granted: bool, **kwargs):
        """
        Log authorization check.
        
        Args:
            user_id: User ID requesting access
            permission: Permission being checked
            granted: Whether permission was granted
            **kwargs: Additional context (resource, action, role, etc.)
        """
        event_type = 'access_granted' if granted else 'access_denied'
        severity = logging.INFO if granted else logging.WARNING
        
        extra = {
            'event_type': event_type,
            'user_id': user_id,
            'permission_required': permission,
            'permission_granted': granted,
            **kwargs,
        }
        
        message = f"Access {'granted' if granted else 'denied'} for user {user_id} to {permission}"
        self.logger.log(severity, message, extra=extra)
    
    def log_data_access(self, user_id: int, event_type: str, **kwargs):
        """
        Log data access event.
        
        Args:
            user_id: User accessing data
            event_type: Type of access (record_view, search_query, export_data, etc.)
            **kwargs: Additional context (care_home, unit, affected_records, etc.)
        """
        extra = {
            'event_type': event_type,
            'user_id': user_id,
            **kwargs,
        }
        
        message = f"Data access: {event_type} by user {user_id}"
        self.logger.info(message, extra=extra)
    
    def log_data_modification(self, user_id: int, event_type: str, **kwargs):
        """
        Log data modification event.
        
        Args:
            user_id: User modifying data
            event_type: Type of modification (create, update, delete, bulk_update, etc.)
            **kwargs: Additional context (model, record_ids, changes, etc.)
        """
        extra = {
            'event_type': event_type,
            'user_id': user_id,
            **kwargs,
        }
        
        message = f"Data modification: {event_type} by user {user_id}"
        self.logger.info(message, extra=extra)
    
    def log_security_incident(self, incident_type: str, severity: str, **kwargs):
        """
        Log security incident.
        
        Args:
            incident_type: Type of security incident (sql_injection, xss, etc.)
            severity: Incident severity (P1, P2, P3, P4)
            **kwargs: Additional context (threat_indicators, ip_address, etc.)
        """
        extra = {
            'event_type': incident_type,
            'incident_severity': severity,
            **kwargs,
        }
        
        message = f"SECURITY INCIDENT [{severity}]: {incident_type}"
        self.logger.critical(message, extra=extra)
        
        # Trigger automated escalation for P1/P2 incidents
        if severity in ('P1', 'P2'):
            self._trigger_escalation(incident_type, severity, kwargs)
    
    def log_system_health(self, event_type: str, **kwargs):
        """
        Log system health event.
        
        Args:
            event_type: Type of health event (server_start, health_check, resource_usage, etc.)
            **kwargs: Additional context (cpu_percent, memory_percent, disk_percent, etc.)
        """
        extra = {
            'event_type': event_type,
            **kwargs,
        }
        
        message = f"System health: {event_type}"
        self.logger.info(message, extra=extra)
    
    def log_performance(self, event_type: str, **kwargs):
        """
        Log performance metric.
        
        Args:
            event_type: Type of performance event (slow_query, high_latency, etc.)
            **kwargs: Additional context (duration_ms, query, endpoint, etc.)
        """
        extra = {
            'event_type': event_type,
            **kwargs,
        }
        
        message = f"Performance: {event_type}"
        self.logger.warning(message, extra=extra)
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """
        Log application error with full context.
        
        Args:
            error: Exception instance
            context: Additional context dictionary
        """
        extra = {
            'event_type': 'unhandled_exception',
            'error_type': type(error).__name__,
            'error_message': str(error),
            **(context or {}),
        }
        
        message = f"Application error: {type(error).__name__}"
        self.logger.error(message, exc_info=error, extra=extra)
    
    def _trigger_escalation(self, incident_type: str, severity: str, context: Dict[str, Any]):
        """
        Trigger automated escalation for high-severity incidents.
        
        Args:
            incident_type: Type of security incident
            severity: Incident severity (P1 or P2)
            context: Incident context dictionary
        """
        try:
            from rotasystems.siem_itsm import create_incident_ticket
            
            # Create ITSM ticket
            ticket_id = create_incident_ticket(
                incident_type=incident_type,
                severity=severity,
                context=context,
            )
            
            logging.info(f"Created ITSM ticket {ticket_id} for {severity} incident: {incident_type}")
        
        except Exception as e:
            logging.error(f"Failed to trigger escalation: {e}")


# Global SIEM logger instance
siem_logger = SIEMLogger()


def configure_siem_logging():
    """
    Configure Django logging to use SIEM handlers.
    
    Call this from Django settings.py or apps.py ready() method.
    """
    # Get root logger
    root_logger = logging.getLogger()
    
    # Create structured formatter
    formatter = StructuredLogFormatter()
    
    # Add Splunk handler if enabled
    if siem_settings.SIEM_ENABLED.get('splunk', False):
        splunk_handler = SplunkHECHandler()
        splunk_handler.setFormatter(formatter)
        splunk_handler.setLevel(logging.INFO)
        root_logger.addHandler(splunk_handler)
        logging.info("Splunk SIEM handler configured")
    
    # Add Logstash handler if enabled
    if siem_settings.SIEM_ENABLED.get('elk', False):
        logstash_handler = LogstashHandler()
        logstash_handler.setFormatter(formatter)
        logstash_handler.setLevel(logging.INFO)
        root_logger.addHandler(logstash_handler)
        logging.info("Logstash SIEM handler configured")
    
    # Configure SIEM logger
    siem_log = logging.getLogger('siem')
    siem_log.setLevel(logging.INFO)
    siem_log.propagate = True  # Also send to root handlers
    
    logging.info("SIEM logging configured successfully")
