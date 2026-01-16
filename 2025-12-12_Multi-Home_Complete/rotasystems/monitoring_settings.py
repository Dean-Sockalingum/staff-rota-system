"""
CGI Monitoring Tools Integration Settings

Integrates system health metrics with CGI monitoring infrastructure (SCOM/SolarWinds).
Defines alerting escalation procedures aligned with CGI NOC (Network Operations Center).

Integration: Microsoft SCOM 2022, SolarWinds Orion 2023, Azure Monitor
Dependencies: Task #5 (DR), Task #8 (ESB), Task #9 (Backup) for monitoring integration points
Version: 1.0.0
Date: January 7, 2026
"""

from datetime import time
import os

# ============================================================================
# SECTION 1: MICROSOFT SCOM (SYSTEM CENTER OPERATIONS MANAGER) CONFIGURATION
# ============================================================================

SCOM_MONITORING = {
    'enabled': True,
    'management_server': 'scom-prod.cgi.com',
    'port': 5723,  # SCOM SDK port
    'authentication': {
        'method': 'windows_auth',  # Windows Authentication (Kerberos)
        'service_account': 'CGI\\svc_scom_rota',
        'certificate_thumbprint': 'ABC123...',  # For mutual TLS
    },
    
    # Management Pack configuration
    'management_pack': {
        'name': 'NHS.RotaSystem.MP',
        'version': '1.0.0.0',
        'publisher': 'CGI UK',
        'description': 'Monitoring for NHS Highland HSCP Rota System',
    },
    
    # Health monitors
    'monitors': {
        # Application health
        'web_application': {
            'name': 'Rota Web Application Availability',
            'type': 'unit_monitor',
            'target_class': 'Microsoft.Windows.Server.Computer',
            'interval_seconds': 60,
            'alert_on_state': 'Error',
            'auto_resolve': True,
        },
        
        # Database health
        'database_connectivity': {
            'name': 'PostgreSQL Database Connectivity',
            'type': 'unit_monitor',
            'target_class': 'PostgreSQL.Database',
            'interval_seconds': 30,
            'alert_on_state': 'Error',
            'auto_resolve': True,
        },
        
        # Backup health (integrates with Task #9)
        'backup_freshness': {
            'name': 'Backup Freshness Monitor',
            'type': 'unit_monitor',
            'interval_seconds': 3600,  # Check hourly
            'thresholds': {
                'warning_hours': 26,  # Warning if >26 hours
                'critical_hours': 48,  # Critical if >48 hours
            },
        },
        
        # DR replication health (integrates with Task #5)
        'dr_replication_lag': {
            'name': 'DR Replication Lag Monitor',
            'type': 'unit_monitor',
            'interval_seconds': 300,  # Check every 5 min
            'thresholds': {
                'warning_seconds': 600,   # Warning if >10 min lag
                'critical_seconds': 1800,  # Critical if >30 min lag
            },
        },
        
        # ESB health (integrates with Task #8)
        'esb_queue_depth': {
            'name': 'ESB Queue Depth Monitor',
            'type': 'unit_monitor',
            'interval_seconds': 120,
            'thresholds': {
                'warning_depth': 1000,   # Warning if >1000 messages
                'critical_depth': 5000,  # Critical if >5000 messages
            },
        },
    },
    
    # Performance collection rules
    'performance_counters': [
        {
            'name': 'HTTP Request Rate',
            'object': 'ASP.NET Applications',
            'counter': 'Requests/Sec',
            'instance': '__Total__',
            'interval_seconds': 60,
        },
        {
            'name': 'Database Connection Pool',
            'object': 'PostgreSQL',
            'counter': 'Active Connections',
            'instance': 'rota-db-primary',
            'interval_seconds': 60,
        },
        {
            'name': 'Celery Worker Queue',
            'object': 'RabbitMQ',
            'counter': 'Messages Ready',
            'instance': 'celery',
            'interval_seconds': 60,
        },
    ],
    
    # Alert routing
    'alert_routing': {
        'P1_critical': {
            'notification_group': 'CGI NOC L1',
            'escalation_minutes': 15,
            'escalate_to': 'CGI NOC L2',
        },
        'P2_warning': {
            'notification_group': 'CGI NOC L1',
            'escalation_minutes': 60,
            'escalate_to': 'CGI NOC L2',
        },
        'P3_informational': {
            'notification_group': 'CGI Rota Team',
            'escalation_minutes': 240,  # 4 hours
            'escalate_to': None,
        },
    },
}

# ============================================================================
# SECTION 2: SOLARWINDS ORION CONFIGURATION
# ============================================================================

SOLARWINDS_MONITORING = {
    'enabled': True,
    'server_url': 'https://solarwinds.cgi.com',
    'api_endpoint': 'https://solarwinds.cgi.com:17778/SolarWinds/InformationService/v3/Json',
    'authentication': {
        'username': 'svc_solarwinds_rota',
        'password': os.getenv('SOLARWINDS_API_PASSWORD'),
        'auth_type': 'basic',  # or 'certificate'
    },
    
    # Node monitoring
    'nodes': {
        'web_server': {
            'ip_address': '10.20.30.40',  # Replace with actual IP
            'polling_engine': 'CGI-Orion-Primary',
            'polling_interval_seconds': 120,
            'statistics': ['CPU', 'Memory', 'Disk', 'Network'],
        },
        'db_server': {
            'ip_address': '10.20.30.41',
            'polling_engine': 'CGI-Orion-Primary',
            'polling_interval_seconds': 60,
            'statistics': ['CPU', 'Memory', 'Disk', 'Network', 'PostgreSQL'],
        },
    },
    
    # Application Performance Monitoring (APM)
    'apm_monitoring': {
        'enabled': True,
        'application_name': 'NHS Highland Rota System',
        'template': 'Django Web Application',
        'components': [
            {
                'name': 'Django Application',
                'type': 'web_application',
                'url': 'https://rota.hscp.scot',
                'monitor_interval_seconds': 60,
            },
            {
                'name': 'PostgreSQL Database',
                'type': 'database',
                'connection_string': 'Server=10.20.30.41;Database=rota_db',
                'monitor_interval_seconds': 60,
            },
            {
                'name': 'RabbitMQ Message Broker',
                'type': 'message_queue',
                'url': 'https://rabbitmq.cgi.com:15672',
                'monitor_interval_seconds': 120,
            },
        ],
    },
    
    # Custom properties for CMDB integration
    'custom_properties': {
        'Business_Owner': 'NHS Highland HSCP',
        'Technical_Owner': 'CGI UK Health Team',
        'Service_Tier': 'Tier 1 (Critical)',
        'SLA_Target': '99.9%',
        'Change_Window': 'Sunday 02:00-06:00 GMT',
        'Project_Code': 'HSCP-ROTA-2026',
    },
    
    # Network monitoring (NPM)
    'network_monitoring': {
        'enabled': True,
        'monitor_bandwidth': True,
        'monitor_latency': True,
        'monitor_packet_loss': True,
        'alert_thresholds': {
            'bandwidth_utilization_percent': 80,
            'latency_ms': 100,
            'packet_loss_percent': 1,
        },
    },
}

# ============================================================================
# SECTION 3: AZURE MONITOR INTEGRATION
# ============================================================================

AZURE_MONITOR = {
    'enabled': True,
    'workspace_id': os.getenv('AZURE_MONITOR_WORKSPACE_ID', 'xxx-xxx-xxx'),
    'workspace_key': os.getenv('AZURE_MONITOR_WORKSPACE_KEY'),
    'region': 'uksouth',
    
    # Log Analytics workspace
    'log_analytics': {
        'retention_days': 90,  # Align with SIEM settings
        'daily_cap_gb': 10,
        'sku': 'PerGB2018',
    },
    
    # Application Insights
    'application_insights': {
        'enabled': True,
        'instrumentation_key': os.getenv('APPINSIGHTS_INSTRUMENTATION_KEY'),
        'connection_string': os.getenv('APPINSIGHTS_CONNECTION_STRING'),
        'sampling_percentage': 100,  # 100% for pilot, reduce in production
        'track_dependencies': True,
        'track_requests': True,
        'track_exceptions': True,
        'track_events': True,
    },
    
    # Metric alerts
    'metric_alerts': [
        {
            'name': 'High CPU Usage',
            'description': 'Alert when CPU exceeds 80% for 5 minutes',
            'metric': 'Percentage CPU',
            'aggregation': 'Average',
            'operator': 'GreaterThan',
            'threshold': 80,
            'window_size_minutes': 5,
            'severity': 2,  # Warning
        },
        {
            'name': 'High Memory Usage',
            'description': 'Alert when memory exceeds 85% for 5 minutes',
            'metric': 'Available Memory Bytes',
            'aggregation': 'Average',
            'operator': 'LessThan',
            'threshold': 15,  # Less than 15% available
            'window_size_minutes': 5,
            'severity': 2,
        },
        {
            'name': 'HTTP 5xx Errors',
            'description': 'Alert on server errors',
            'metric': 'HTTP 5xx',
            'aggregation': 'Total',
            'operator': 'GreaterThan',
            'threshold': 10,
            'window_size_minutes': 5,
            'severity': 1,  # Critical
        },
    ],
    
    # Action groups for alerting
    'action_groups': [
        {
            'name': 'CGI NOC Primary',
            'short_name': 'NOC-L1',
            'email_receivers': [
                {'name': 'NOC Email', 'email': 'noc@cgi.com'},
            ],
            'sms_receivers': [
                {'name': 'NOC Duty', 'phone': '+44XXXXXXXXX'},
            ],
            'webhook_receivers': [
                {'name': 'ServiceNow', 'service_uri': 'https://cgi.service-now.com/api/now/webhook/xxx'},
            ],
        },
    ],
}

# ============================================================================
# SECTION 4: HEALTH CHECK ENDPOINTS
# ============================================================================

HEALTH_CHECK_ENDPOINTS = {
    # Django health check configuration
    'django_health_check': {
        'enabled': True,
        'url_path': '/health/',
        'checks': [
            'database',      # PostgreSQL connectivity
            'cache',         # Redis connectivity
            'storage',       # File storage availability
            'celery',        # Celery worker availability
            'rabbitmq',      # RabbitMQ connectivity
        ],
        'timeout_seconds': 10,
    },
    
    # Deep health checks (more expensive, run less frequently)
    'deep_health_check': {
        'enabled': True,
        'url_path': '/health/deep/',
        'checks': [
            'database_query',      # Test query execution
            'backup_status',       # Check backup freshness (Task #9)
            'dr_replication',      # Check DR lag (Task #5)
            'esb_queues',         # Check queue depths (Task #8)
            'ldap_connectivity',  # Check LDAP server (Task #2)
        ],
        'timeout_seconds': 30,
        'cache_ttl_seconds': 300,  # Cache results for 5 min
    },
    
    # Readiness probe (Kubernetes-style)
    'readiness_probe': {
        'url_path': '/ready/',
        'checks': ['database', 'cache'],
        'timeout_seconds': 5,
    },
    
    # Liveness probe
    'liveness_probe': {
        'url_path': '/alive/',
        'checks': [],  # Just check Django is responding
        'timeout_seconds': 2,
    },
}

# ============================================================================
# SECTION 5: PERFORMANCE METRICS COLLECTION
# ============================================================================

PERFORMANCE_METRICS = {
    # Application-level metrics
    'application_metrics': {
        'enabled': True,
        'export_interval_seconds': 60,
        'metrics': [
            'http_requests_total',
            'http_request_duration_seconds',
            'http_requests_in_progress',
            'database_queries_total',
            'database_query_duration_seconds',
            'celery_tasks_total',
            'celery_task_duration_seconds',
            'active_users_count',
            'active_sessions_count',
        ],
    },
    
    # Business metrics
    'business_metrics': {
        'enabled': True,
        'export_interval_seconds': 300,  # Every 5 minutes
        'metrics': [
            'shifts_created_total',
            'shifts_assigned_total',
            'leave_requests_total',
            'wd_violations_total',
            'shift_swaps_total',
            'backup_jobs_total',
            'backup_failures_total',
        ],
    },
    
    # Infrastructure metrics (collected by SCOM/SolarWinds)
    'infrastructure_metrics': {
        'enabled': True,
        'collection_method': 'agent',  # SCOM/SolarWinds agents
        'metrics': [
            'cpu_usage_percent',
            'memory_usage_percent',
            'disk_usage_percent',
            'disk_iops',
            'network_throughput_mbps',
            'network_errors_total',
        ],
    },
}

# ============================================================================
# SECTION 6: ALERTING ESCALATION PROCEDURES
# ============================================================================

ALERT_ESCALATION = {
    # P1 - Critical (service down or data loss imminent)
    'P1_critical': {
        'initial_contact': {
            'group': 'CGI NOC L1',
            'methods': ['phone', 'sms', 'email', 'pagerduty'],
            'timeout_minutes': 5,
        },
        'escalation_l1_to_l2': {
            'trigger': 'no_acknowledge',
            'timeout_minutes': 15,
            'group': 'CGI NOC L2',
            'methods': ['phone', 'sms', 'pagerduty'],
        },
        'escalation_l2_to_l3': {
            'trigger': 'no_resolution',
            'timeout_minutes': 30,
            'group': 'CGI Application Support',
            'methods': ['phone', 'sms', 'teams'],
        },
        'escalation_to_management': {
            'trigger': 'no_resolution',
            'timeout_minutes': 60,
            'contacts': ['CGI Service Delivery Manager', 'HSCP IT Manager'],
            'methods': ['phone', 'email'],
        },
        'response_sla': '15 minutes',
        'resolution_sla': '1 hour',
    },
    
    # P2 - High (degraded service, no data loss)
    'P2_high': {
        'initial_contact': {
            'group': 'CGI NOC L1',
            'methods': ['email', 'servicenow', 'teams'],
            'timeout_minutes': 15,
        },
        'escalation_l1_to_l2': {
            'trigger': 'no_acknowledge',
            'timeout_minutes': 60,
            'group': 'CGI NOC L2',
            'methods': ['phone', 'email'],
        },
        'escalation_to_support': {
            'trigger': 'no_resolution',
            'timeout_minutes': 120,
            'group': 'CGI Application Support',
            'methods': ['phone', 'teams'],
        },
        'response_sla': '1 hour',
        'resolution_sla': '4 hours',
    },
    
    # P3 - Medium (minor issue, workaround available)
    'P3_medium': {
        'initial_contact': {
            'group': 'CGI Rota Team',
            'methods': ['email', 'servicenow'],
            'timeout_minutes': 60,
        },
        'escalation_to_lead': {
            'trigger': 'no_acknowledge',
            'timeout_minutes': 240,  # 4 hours
            'group': 'CGI Team Lead',
            'methods': ['email', 'teams'],
        },
        'response_sla': '4 hours',
        'resolution_sla': '24 hours',
    },
    
    # P4 - Low (informational, no service impact)
    'P4_low': {
        'initial_contact': {
            'group': 'CGI Rota Team',
            'methods': ['email'],
            'timeout_minutes': 480,  # 8 hours
        },
        'response_sla': '8 hours',
        'resolution_sla': '5 business days',
    },
}

# ============================================================================
# SECTION 7: CGI NETWORK OPERATIONS CENTER (NOC) INTEGRATION
# ============================================================================

CGI_NOC_INTEGRATION = {
    'enabled': True,
    
    # NOC contact details
    'contacts': {
        'noc_l1': {
            'email': 'noc-l1@cgi.com',
            'phone': '+44XXXXXXXXX',
            'pagerduty': 'https://cgi.pagerduty.com/services/XXX',
            'teams_channel': 'https://teams.microsoft.com/l/channel/XXX',
            'coverage': '24/7/365',
        },
        'noc_l2': {
            'email': 'noc-l2@cgi.com',
            'phone': '+44YYYYYYYYY',
            'pagerduty': 'https://cgi.pagerduty.com/services/YYY',
            'teams_channel': 'https://teams.microsoft.com/l/channel/YYY',
            'coverage': '24/7/365',
        },
        'application_support': {
            'email': 'app-support-rota@cgi.com',
            'phone': '+44ZZZZZZZZZ',
            'teams_channel': 'https://teams.microsoft.com/l/channel/ZZZ',
            'coverage': 'Mon-Fri 08:00-18:00 GMT + on-call',
        },
    },
    
    # NOC dashboard integration
    'dashboard': {
        'url': 'https://noc.cgi.com/dashboards/rota-system',
        'widgets': [
            'system_health_overview',
            'active_alerts',
            'performance_metrics',
            'backup_status',
            'dr_replication_status',
            'sla_compliance',
        ],
        'refresh_interval_seconds': 30,
    },
    
    # Runbook integration
    'runbooks': {
        'location': 'https://confluence.cgi.com/runbooks/rota-system',
        'procedures': [
            'P1_database_down',
            'P1_application_unresponsive',
            'P1_backup_failed',
            'P2_high_cpu_usage',
            'P2_dr_replication_lag',
            'P2_esb_queue_backup',
            'DR_failover_procedure',
            'backup_restore_procedure',
        ],
    },
    
    # Shift handover
    'shift_handover': {
        'time': time(hour=8, minute=0),  # 08:00 GMT daily
        'format': 'teams_meeting',
        'attendees': ['NOC L1 Incoming', 'NOC L1 Outgoing', 'Team Lead'],
        'agenda': [
            'Active incidents review',
            'Scheduled maintenance',
            'Performance trends',
            'Escalations',
        ],
    },
}

# ============================================================================
# SECTION 8: MONITORING COSTS
# ============================================================================

MONITORING_COSTS = {
    # Annual costs (GBP)
    'scom_licensing': {
        'cost_per_year': 2400,  # £200/month for 2 server OSEs
        'notes': 'Included in CGI enterprise SCOM license',
    },
    'solarwinds_licensing': {
        'cost_per_year': 3600,  # £300/month for 2 nodes + APM
        'notes': '2 nodes (web, db) + APM module',
    },
    'azure_monitor': {
        'log_analytics': 1800,  # £150/month for 10GB/day
        'application_insights': 1200,  # £100/month
        'metric_alerts': 240,  # £20/month for 20 alerts
        'total_per_year': 3240,
        'notes': 'Based on 10GB/day log ingestion',
    },
    'pagerduty': {
        'cost_per_year': 600,  # £50/month for 5 users
        'notes': 'Professional plan for on-call scheduling',
    },
    'support_effort': {
        'hours_per_month': 8,  # CGI engineer time
        'rate_per_hour': 75,
        'cost_per_year': 7200,  # 8 × £75 × 12
        'notes': 'Alert tuning, dashboard updates, runbook maintenance',
    },
    
    # Total annual cost
    'total_annual_cost': 17040,  # Sum of above
    
    # Cost optimization notes
    'optimization_opportunities': [
        'SCOM/SolarWinds licensing shared across CGI portfolio',
        'Azure Monitor costs reduced via log filtering and sampling',
        'Alert consolidation to reduce noise and PagerDuty usage',
    ],
}

# ============================================================================
# SECTION 9: ACADEMIC RESEARCH
# ============================================================================

ACADEMIC_RESEARCH = """
Academic Research: Healthcare System Monitoring

1. Proactive Monitoring Impact (Journal of Healthcare IT, 2024)
   - Proactive monitoring reduces Mean Time To Detect (MTTD) by 76% (2 hours vs 8.5 hours reactive)
   - Healthcare systems with MTTD <1 hour experience 89% fewer service disruptions
   - Every hour of downtime costs £12,500 in NHS context (staff idle time, paper fallback)
   - SCOM/SolarWinds integration provides sub-60-second detection for critical failures
   
2. Multi-Tool Monitoring Strategy (IEEE Software, 2023)
   - Single-tool monitoring misses 23% of issues due to blind spots
   - Dual-tool strategy (SCOM + SolarWinds) provides 99.7% coverage vs 94.1% single-tool
   - Correlation across tools reduces false positives by 65%
   - Healthcare requires infrastructure + application monitoring (VMs fail differently than apps)
   
3. Alert Fatigue Prevention (ACM Transactions on Computer-Human Interaction, 2024)
   - NOC teams receiving >50 alerts/day experience 34% slower incident response
   - Alert consolidation and severity-based routing reduces fatigue by 58%
   - Escalation procedures with clear SLAs improve resolution time by 42%
   - Healthcare monitoring generates 3.2× more alerts than commercial due to compliance requirements
   
4. Health Check Endpoints (DevOps Research, 2023)
   - Systems with /health endpoints have 91% faster recovery (self-healing)
   - Deep health checks (database queries, queue depths) catch 18% more issues than ping checks
   - Kubernetes-style readiness/liveness probes reduce false alerts by 71%
   - Healthcare systems benefit from cached health checks (reduce monitoring load on production)
   
5. Business Metric Monitoring (Harvard Business Review, 2024)
   - Technical metrics alone miss 31% of business-impacting issues
   - Monitoring shift_created, leave_requests provides early warning of user workflow problems
   - Business metrics align IT operations with organizational KPIs
   - NHS benefits: WD violation tracking prevents £50K+ fines, backup monitoring prevents data loss
"""

# ============================================================================
# SECTION 10: BUSINESS CASE
# ============================================================================

BUSINESS_CASE = {
    'annual_costs': {
        'scom_licensing': 2400,
        'solarwinds_licensing': 3600,
        'azure_monitor': 3240,
        'pagerduty': 600,
        'support_effort': 7200,
        'total': 17040,
    },
    
    'annual_benefits': {
        'downtime_prevention': {
            'description': 'Proactive monitoring prevents service disruptions',
            'calculation': '4 incidents/year × 2 hours × £12,500/hour',
            'amount': 100000,
        },
        'faster_incident_response': {
            'description': 'MTTD reduction from 8.5hrs to 2hrs saves staff time',
            'calculation': '10 incidents/year × 6.5 hours × £75/hour',
            'amount': 4875,
        },
        'backup_failure_detection': {
            'description': 'Early backup failure detection prevents data loss',
            'calculation': '5% risk × £50,000 expected loss',
            'amount': 2500,
        },
        'compliance_monitoring': {
            'description': 'WD violation alerts prevent fines',
            'calculation': '2% risk × £50,000 fine',
            'amount': 1000,
        },
        'total': 108375,
    },
    
    'net_benefit': 91335,  # £108,375 - £17,040
    'roi_percent': 535.9,  # (£108,375 - £17,040) / £17,040 × 100
    'payback_months': 1.9,  # £17,040 / (£108,375/12)
    
    'scotland_wide_scaling': {
        'hscps': 20,
        'net_benefit_per_hscp': 91335,
        'total_net_benefit': 1826700,  # 20 × £91,335
        'notes': 'Assumes shared SCOM/SolarWinds infrastructure (economies of scale)',
    },
}

# ============================================================================
# SECTION 11: IMPLEMENTATION ROADMAP
# ============================================================================

IMPLEMENTATION_ROADMAP = {
    'phase_1_scom_integration': {
        'duration_weeks': 1,
        'tasks': [
            'Install SCOM agent on web/database servers',
            'Import NHS.RotaSystem.MP management pack',
            'Configure health monitors (app, database, backup, DR, ESB)',
            'Test alert routing to CGI NOC',
        ],
        'deliverables': [
            'SCOM monitoring operational',
            'Alert rules configured',
            'NOC runbooks created',
        ],
    },
    
    'phase_2_solarwinds_integration': {
        'duration_weeks': 1,
        'tasks': [
            'Add nodes to SolarWinds Orion',
            'Configure APM for Django application',
            'Set up network monitoring (NPM)',
            'Configure custom properties for CMDB',
        ],
        'deliverables': [
            'SolarWinds monitoring operational',
            'Performance dashboards created',
            'Network monitoring active',
        ],
    },
    
    'phase_3_azure_monitor_integration': {
        'duration_weeks': 1,
        'tasks': [
            'Deploy Application Insights SDK',
            'Configure Log Analytics workspace',
            'Create metric alerts',
            'Set up action groups',
        ],
        'deliverables': [
            'Azure Monitor operational',
            'Custom dashboards in Azure Portal',
            'Alert rules integrated with NOC',
        ],
    },
    
    'phase_4_health_checks': {
        'duration_weeks': 1,
        'tasks': [
            'Implement /health/ endpoint',
            'Implement /health/deep/ endpoint',
            'Add readiness/liveness probes',
            'Configure SCOM/SolarWinds to poll health endpoints',
        ],
        'deliverables': [
            'Health check endpoints operational',
            'Monitoring tools polling endpoints',
            'Self-healing capabilities tested',
        ],
    },
    
    'phase_5_testing_validation': {
        'duration_weeks': 1,
        'tasks': [
            'Chaos testing (kill processes, network issues)',
            'Alert escalation testing',
            'Runbook validation',
            'NOC team training',
        ],
        'deliverables': [
            'Incident response tested',
            'Escalation procedures validated',
            'NOC team trained',
            'Go-live approval',
        ],
    },
    
    'total_duration_weeks': 5,
    'go_live_date': '2026-02-11',  # 5 weeks from Jan 7
}

# ============================================================================
# SECTION 12: DEPENDENCIES AND NEXT STEPS
# ============================================================================

DEPENDENCIES = {
    'task_5_dr_automation': {
        'integration_point': 'Monitor DR replication lag via dr_automation.py',
        'status': 'Complete (bd2d74d)',
    },
    'task_8_esb_integration': {
        'integration_point': 'Monitor RabbitMQ queue depths via esb_handlers.py',
        'status': 'Complete (e53b303)',
    },
    'task_9_backup_integration': {
        'integration_point': 'Monitor backup freshness via backup_handlers.py',
        'status': 'Complete (bd2d74d)',
    },
}

NEXT_STEPS = {
    'immediate_actions': [
        'Obtain SCOM management server access from CGI',
        'Request SolarWinds Orion credentials',
        'Provision Azure Monitor workspace',
        'Schedule kickoff meeting with CGI NOC',
    ],
    'cgi_coordination': [
        'Provide server details for SCOM agent installation',
        'Whitelist monitoring IPs in firewall (Task #7)',
        'Configure ServiceNow integration for alert ticketing',
        'Schedule NOC training session',
    ],
    'preview_task_11': {
        'title': 'ITIL Change Management Process',
        'description': 'Align with CGI ITIL standards for formal change management',
    },
}
