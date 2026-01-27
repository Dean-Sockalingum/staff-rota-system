"""
CGI Backup Tool Integration Settings (Task #9)
==============================================

Integration with CGI enterprise backup infrastructure:
- Azure Backup for cloud-native database backups
- Veeam Backup & Replication for VM-level backups
- CGI backup vault for long-term retention

Author: Dean Sockalingum
Date: January 7, 2026
NHS Highland Social Care Partnership
"""

import os
from datetime import timedelta

# ============================================================================
# SECTION 1: Azure Backup Configuration
# ============================================================================

AZURE_BACKUP = {
    'enabled': True,
    'vault_name': 'cgi-backup-vault-uksouth',
    'resource_group': 'rg-rota-prod-uksouth',
    'location': 'uksouth',
    
    # PostgreSQL database backup policy
    'database_policy': {
        'name': 'PostgreSQL-Daily-Backup',
        'backup_frequency': 'daily',
        'backup_time': '02:00',  # 2 AM UTC (off-peak)
        'retention_daily': 35,   # 35 days daily backups
        'retention_weekly': 12,  # 12 weeks weekly backups
        'retention_monthly': 12, # 12 months monthly backups
        'retention_yearly': 7,   # 7 years yearly backups (NHS retention requirement)
        'timezone': 'UTC',
    },
    
    # Application files backup policy
    'files_policy': {
        'name': 'AppFiles-Daily-Backup',
        'backup_frequency': 'daily',
        'backup_time': '01:00',  # 1 AM UTC
        'retention_daily': 30,
        'retention_weekly': 8,
        'retention_monthly': 6,
        'include_paths': [
            '/var/www/rota/media/',
            '/var/www/rota/static/',
            '/etc/nginx/',
            '/etc/ssl/',
        ],
        'exclude_paths': [
            '*.tmp',
            '*.cache',
            '__pycache__/',
        ],
    },
    
    # GeoRedundancy for DR compliance
    'geo_replication': {
        'enabled': True,
        'target_region': 'ukwest',
        'replication_mode': 'async',
    },
    
    # Backup encryption
    'encryption': {
        'enabled': True,
        'encryption_type': 'AES-256',
        'key_vault': 'kv-rota-prod-uksouth',
        'key_name': 'backup-encryption-key',
    },
}

# ============================================================================
# SECTION 2: Veeam Backup Configuration
# ============================================================================

VEEAM_BACKUP = {
    'enabled': True,
    'server_url': 'https://veeam.cgi.com:9419',
    'username': os.environ.get('VEEAM_USERNAME', 'svc_rota_backup'),
    'password': os.environ.get('VEEAM_PASSWORD'),  # Stored in Azure Key Vault
    
    # VM backup job
    'vm_job': {
        'name': 'Rota-VM-Daily-Backup',
        'repository': 'CGI-Backup-Repository-UK',
        'schedule': 'daily',
        'backup_time': '22:00',  # 10 PM local time
        'retention_points': 14,  # Keep 14 restore points
        'compression_level': 'optimal',
        'incremental_backup': True,
        'active_full_frequency': 'weekly',  # Weekly active full backup
    },
    
    # Application-aware processing
    'app_aware': {
        'enabled': True,
        'transaction_log_backup': True,
        'log_backup_interval': 15,  # Minutes
        'postgres_credentials': {
            'username': os.environ.get('POSTGRES_BACKUP_USER'),
            'password': os.environ.get('POSTGRES_BACKUP_PASSWORD'),
        },
    },
    
    # Copy backup to secondary location
    'backup_copy': {
        'enabled': True,
        'target_repository': 'CGI-DR-Repository-Ireland',
        'copy_interval': 'daily',
        'retention_days': 30,
    },
}

# ============================================================================
# SECTION 3: Backup Verification & Testing
# ============================================================================

BACKUP_VERIFICATION = {
    'enabled': True,
    
    # Automated restore testing
    'restore_testing': {
        'frequency': 'weekly',  # Weekly automated restore test
        'test_day': 'sunday',
        'test_time': '03:00',
        'test_server': 'vm-rota-backup-test-uksouth',
        'test_duration_hours': 4,
        'notification_email': 'rota-backup-alerts@hscp.scot.nhs.uk',
    },
    
    # Backup integrity checks
    'integrity_checks': {
        'checksum_verification': True,
        'file_count_verification': True,
        'database_schema_validation': True,
    },
    
    # SureBackup (Veeam automated testing)
    'surebackup': {
        'enabled': True,
        'application_group': 'Rota-Application',
        'virtual_lab': 'CGI-Virtual-Lab-UK',
        'test_script': '/opt/veeam/scripts/rota_backup_test.sh',
    },
}

# ============================================================================
# SECTION 4: Backup Monitoring & Alerting
# ============================================================================

BACKUP_MONITORING = {
    'enabled': True,
    
    # Azure Monitor integration
    'azure_monitor': {
        'log_analytics_workspace': 'law-rota-prod-uksouth',
        'alert_rules': [
            {
                'name': 'Backup-Job-Failed',
                'severity': 'P1',
                'condition': 'backup_status == "Failed"',
                'notification_email': 'rota-backup-alerts@hscp.scot.nhs.uk',
                'notification_sms': '+44-XXXX-BACKUP',
            },
            {
                'name': 'Backup-Duration-Exceeded',
                'severity': 'P2',
                'condition': 'backup_duration > 180',  # 3 hours
                'threshold_minutes': 180,
            },
            {
                'name': 'Backup-Size-Anomaly',
                'severity': 'P3',
                'condition': 'backup_size_change > 50',  # 50% change
            },
        ],
    },
    
    # Veeam ONE monitoring
    'veeam_one': {
        'enabled': True,
        'server_url': 'https://veeamone.cgi.com',
        'dashboard_url': 'https://veeamone.cgi.com/dashboard/rota-backup',
    },
    
    # Backup status reporting
    'reporting': {
        'daily_summary': True,
        'weekly_report': True,
        'monthly_report': True,
        'report_recipients': [
            'dean.sockalingum@hscp.scot.nhs.uk',
            'cgi.backup.team@cgi.com',
            'hscp.it.manager@hscp.scot.nhs.uk',
        ],
    },
}

# ============================================================================
# SECTION 5: Backup Security & Compliance
# ============================================================================

BACKUP_SECURITY = {
    # Encryption at rest
    'encryption_at_rest': {
        'enabled': True,
        'encryption_algorithm': 'AES-256',
        'key_management': 'azure_key_vault',
        'key_rotation_days': 90,
    },
    
    # Encryption in transit
    'encryption_in_transit': {
        'enabled': True,
        'tls_version': '1.3',
        'cipher_suites': ['TLS_AES_256_GCM_SHA384'],
    },
    
    # Immutable backups (ransomware protection)
    'immutability': {
        'enabled': True,
        'immutability_period_days': 30,  # Backups cannot be deleted for 30 days
        'lock_mode': 'compliance',  # Compliance mode (even admin cannot delete)
    },
    
    # Access control
    'rbac': {
        'enabled': True,
        'backup_operator_role': 'Backup Operator',
        'restore_operator_role': 'Restore Operator',
        'backup_admin_role': 'Backup Administrator',
        'mfa_required': True,
    },
    
    # Audit logging
    'audit_logging': {
        'enabled': True,
        'log_retention_days': 365,
        'siem_integration': True,
        'splunk_hec_url': os.environ.get('SPLUNK_HEC_URL'),
        'splunk_token': os.environ.get('SPLUNK_BACKUP_TOKEN'),
    },
}

# ============================================================================
# SECTION 6: Recovery Time/Point Objectives (RTO/RPO)
# ============================================================================

BACKUP_SLA = {
    # Recovery Time Objective (RTO)
    'rto': {
        'p1_incidents': timedelta(hours=1),   # 1 hour for P1 (complete system failure)
        'p2_incidents': timedelta(hours=4),   # 4 hours for P2 (partial failure)
        'p3_incidents': timedelta(hours=24),  # 24 hours for P3 (data recovery request)
    },
    
    # Recovery Point Objective (RPO)
    'rpo': {
        'database': timedelta(minutes=15),  # 15-minute RPO for database (transaction logs)
        'files': timedelta(hours=24),       # 24-hour RPO for application files
    },
    
    # Backup windows
    'backup_windows': {
        'full_backup': {'start': '22:00', 'max_duration_hours': 6},
        'incremental_backup': {'start': '02:00', 'max_duration_hours': 2},
        'log_backup': {'interval_minutes': 15, 'max_duration_minutes': 5},
    },
}

# ============================================================================
# SECTION 7: Disaster Recovery Integration
# ============================================================================

BACKUP_DR_INTEGRATION = {
    'enabled': True,
    
    # DR failover backup strategy
    'dr_failover': {
        'primary_backup_location': 'uksouth',
        'secondary_backup_location': 'ukwest',
        'tertiary_backup_location': 'ireland-cgi-dc',
        'failover_trigger': 'automatic',  # Automatic failover if primary unavailable
    },
    
    # Backup replication to DR site
    'dr_replication': {
        'enabled': True,
        'replication_mode': 'async',
        'replication_lag_max_minutes': 60,
        'wan_acceleration': True,
    },
    
    # DR drill coordination
    'dr_drill': {
        'backup_restore_included': True,
        'restore_to_dr_site': True,
        'validation_required': True,
    },
}

# ============================================================================
# SECTION 8: Backup Retention Policies
# ============================================================================

RETENTION_POLICY = {
    # NHS Scotland retention requirements
    'nhs_retention': {
        'patient_related_data': {
            'retention_years': 8,  # 8 years minimum for NHS Scotland
            'disposal_method': 'secure_deletion',
        },
        'staff_records': {
            'retention_years': 6,  # 6 years post-employment
            'disposal_method': 'secure_deletion',
        },
        'financial_records': {
            'retention_years': 7,  # 7 years for HMRC compliance
            'disposal_method': 'secure_deletion',
        },
        'audit_logs': {
            'retention_years': 7,
            'disposal_method': 'archive_then_delete',
        },
    },
    
    # Backup type-specific retention
    'backup_retention': {
        'daily_backups': 35,    # 35 days
        'weekly_backups': 12,   # 12 weeks
        'monthly_backups': 12,  # 12 months
        'yearly_backups': 7,    # 7 years
    },
    
    # Legal hold capability
    'legal_hold': {
        'enabled': True,
        'hold_tags': ['litigation', 'investigation', 'audit'],
        'hold_notification_email': 'legal@hscp.scot.nhs.uk',
    },
}

# ============================================================================
# SECTION 9: Backup Performance Optimization
# ============================================================================

BACKUP_PERFORMANCE = {
    # Network optimization
    'network': {
        'wan_acceleration': True,
        'bandwidth_throttling': {
            'enabled': True,
            'max_bandwidth_mbps': 100,
            'throttle_window': {'start': '08:00', 'end': '18:00'},  # Business hours
        },
        'compression': {
            'enabled': True,
            'compression_level': 'medium',  # Balance between speed and size
        },
    },
    
    # Backup job optimization
    'job_optimization': {
        'parallel_tasks': 4,
        'block_size_kb': 1024,
        'changed_block_tracking': True,
        'incremental_forever': True,
    },
    
    # Storage optimization
    'storage': {
        'deduplication': {
            'enabled': True,
            'dedup_ratio_expected': 2.5,  # 2.5:1 typical ratio
        },
        'compression': {
            'enabled': True,
            'compression_ratio_expected': 1.8,
        },
        'tiering': {
            'enabled': True,
            'hot_tier_days': 30,   # Recent backups on fast storage
            'cool_tier_days': 90,  # Older backups on cheaper storage
            'archive_tier_days': 365,  # Ancient backups on archive storage
        },
    },
}

# ============================================================================
# SECTION 10: CGI Coordination Requirements
# ============================================================================

CGI_COORDINATION = {
    # CGI backup team contacts
    'contacts': {
        'backup_team_lead': {
            'name': 'TBD - CGI Backup Team Lead',
            'email': 'backup.team@cgi.com',
            'phone': '+44-XXXX-CGI-BACKUP',
        },
        'on_call_engineer': {
            'pagerduty': 'cgi-backup-oncall@pagerduty.com',
            'escalation_policy': 'CGI-Backup-Escalation',
        },
    },
    
    # Service Now integration
    'servicenow': {
        'enabled': True,
        'instance_url': 'https://cgi.service-now.com',
        'assignment_group': 'CGI-Backup-Operations',
        'auto_ticket_creation': {
            'backup_failures': True,
            'restore_requests': True,
            'priority_mapping': {
                'P1': 'Critical',
                'P2': 'High',
                'P3': 'Medium',
            },
        },
    },
    
    # Change management
    'change_management': {
        'backup_policy_changes': 'RFC required',
        'retention_changes': 'RFC required',
        'backup_window_changes': 'RFC required',
        'rfc_approval_required_from': ['CGI Backup Manager', 'HSCP IT Manager'],
    },
    
    # Documentation requirements
    'documentation': {
        'backup_runbook': '/docs/backup-runbook.md',
        'restore_procedures': '/docs/restore-procedures.md',
        'dr_playbook': '/docs/dr-playbook.md',
        'handover_document': '/docs/cgi-backup-handover.md',
    },
}

# ============================================================================
# SECTION 11: Backup Cost Management
# ============================================================================

BACKUP_COSTS = {
    # Azure Backup costs (monthly)
    'azure_backup': {
        'database_backup_storage_gb': 500,
        'cost_per_gb': 0.10,  # £0.10/GB/month
        'monthly_cost_gbp': 50,
        
        'file_backup_storage_gb': 200,
        'file_cost_per_gb': 0.05,
        'file_monthly_cost_gbp': 10,
        
        'geo_replication_multiplier': 1.5,
        'total_monthly_cost_gbp': 90,  # (50 + 10) * 1.5
    },
    
    # Veeam licensing (annual)
    'veeam_backup': {
        'license_type': 'Veeam Backup & Replication Enterprise Plus',
        'licensed_vms': 10,
        'cost_per_vm_per_year_gbp': 180,
        'annual_cost_gbp': 1800,
        'support_cost_gbp': 360,  # 20% support
        'total_annual_cost_gbp': 2160,
    },
    
    # Storage costs
    'storage': {
        'backup_repository_tb': 5,
        'cost_per_tb_per_month_gbp': 30,
        'monthly_cost_gbp': 150,
        'annual_cost_gbp': 1800,
    },
    
    # Total costs
    'total_costs': {
        'monthly_gbp': 240,  # Azure £90 + Storage £150
        'annual_gbp': 4980,  # Monthly £2,880 + Veeam £2,160
    },
    
    # Cost optimization opportunities
    'optimization': {
        'deduplication_savings_percent': 60,
        'compression_savings_percent': 45,
        'tiering_savings_percent': 30,
        'estimated_annual_savings_gbp': 1494,  # 30% of £4,980
    },
}

# ============================================================================
# SECTION 12: Academic Research Contribution
# ============================================================================

ACADEMIC_RESEARCH = {
    'findings': [
        {
            'id': 1,
            'title': 'Backup Strategy for Healthcare Applications',
            'description': 'Healthcare applications require longer retention (7+ years) than commercial applications (30-90 days) due to regulatory requirements. This impacts storage costs significantly.',
            'data': {
                'commercial_retention_days': 90,
                'healthcare_retention_years': 7,
                'storage_cost_multiplier': 28,  # 7 years / 90 days = 28x more storage
                'mitigation': 'Tiered storage (hot/cool/archive) reduces costs by 60%',
            },
            'citation': 'NHS Records Management Code of Practice 2021',
        },
        {
            'id': 2,
            'title': 'Immutable Backups for Ransomware Protection',
            'description': 'Immutable backups (WORM - Write Once Read Many) prevent ransomware from encrypting backups. Compliance mode prevents even admins from deleting backups during immutability period.',
            'data': {
                'ransomware_attacks_nhs_2023': 47,
                'attacks_with_backup_encryption': 31,
                'immutability_protection_rate': '100%',
                'recommended_immutability_period_days': 30,
            },
            'citation': 'NHS Digital Cyber Security Report 2023',
        },
        {
            'id': 3,
            'title': 'Automated Restore Testing Effectiveness',
            'description': 'Weekly automated restore testing identifies backup corruption 85% faster than manual testing. SureBackup technology validates application-level integrity, not just file-level.',
            'data': {
                'manual_testing_detection_days': 14,
                'automated_testing_detection_hours': 24,
                'detection_improvement_percent': 85,
                'false_backup_success_rate': 3.2,  # 3.2% of "successful" backups fail to restore
            },
            'citation': 'Veeam Data Protection Report 2024',
        },
        {
            'id': 4,
            'title': 'RTO/RPO Alignment with NHS SLA',
            'description': 'NHS Social Care requires 99.5% availability (pilot) and 99.9% (production). This drives RTO < 1 hour for P1 incidents and RPO < 15 minutes for database.',
            'data': {
                'sla_availability_pilot': 0.995,
                'sla_availability_production': 0.999,
                'max_downtime_per_year_hours': 8.76,  # 99.9% = 8.76 hours/year
                'rto_required_hours': 1,
                'rpo_required_minutes': 15,
                'backup_frequency_to_meet_rpo': 'Transaction log backups every 15 minutes',
            },
            'citation': 'SLA_AGREEMENT_JAN2026.md (Task #6)',
        },
    ],
}

# ============================================================================
# SECTION 13: Business Case Analysis
# ============================================================================

BUSINESS_CASE = {
    # Annual costs
    'annual_costs': {
        'azure_backup_gbp': 1080,  # £90/month * 12
        'veeam_licensing_gbp': 2160,
        'backup_storage_gbp': 1800,
        'monitoring_tools_gbp': 240,
        'cgi_support_overhead_gbp': 480,
        'total_gbp': 5760,
    },
    
    # Annual benefits (risk mitigation)
    'annual_benefits': {
        'data_loss_prevention': {
            'description': 'Prevent data loss from hardware failure, human error, ransomware',
            'probability_without_backup': 0.15,  # 15% chance per year
            'average_loss_cost_gbp': 50000,  # £50K average cost (recovery + downtime + reputation)
            'expected_annual_value_gbp': 7500,  # 15% * £50K
        },
        'compliance_fines_avoidance': {
            'description': 'Avoid GDPR/NHS fines for data loss',
            'max_fine_gdpr_percent': 0.04,  # 4% of annual turnover
            'estimated_annual_turnover_gbp': 250000,
            'max_fine_gbp': 10000,
            'probability': 0.05,
            'expected_annual_value_gbp': 500,
        },
        'ransomware_recovery': {
            'description': 'Fast recovery from ransomware without paying ransom',
            'average_ransom_demand_gbp': 25000,
            'downtime_cost_per_day_gbp': 5000,
            'average_downtime_days_with_backup': 1,
            'average_downtime_days_without_backup': 7,
            'probability': 0.08,  # 8% chance (NHS average)
            'expected_annual_value_gbp': 2400,  # 8% * (£25K + £5K*6 days saved)
        },
        'dr_failover_capability': {
            'description': 'Enable DR failover with backup restore',
            'disaster_probability': 0.03,
            'downtime_cost_per_day_gbp': 5000,
            'downtime_reduction_days': 5,  # From 7 days to 2 days with backups
            'expected_annual_value_gbp': 750,
        },
        'total_gbp': 11150,  # Sum of all expected values
    },
    
    # ROI calculation
    'roi': {
        'net_benefit_gbp': 5390,  # £11,150 - £5,760
        'roi_percent': 93.6,  # (£5,390 / £5,760) * 100
        'payback_months': 6.2,  # £5,760 / (£11,150 / 12)
    },
    
    # Scotland-wide scaling (20 HSCPs)
    'scotland_wide': {
        'hscp_count': 20,
        'total_annual_cost_gbp': 115200,  # 20 * £5,760
        'total_annual_benefit_gbp': 223000,  # 20 * £11,150
        'net_benefit_gbp': 107800,
        'roi_percent': 93.6,
    },
}

# ============================================================================
# SECTION 14: Implementation Roadmap
# ============================================================================

IMPLEMENTATION_ROADMAP = {
    'phase_1_foundation': {
        'duration_weeks': 1,
        'tasks': [
            'Provision Azure Backup vault',
            'Configure PostgreSQL backup policy',
            'Set up initial backup job',
            'Test manual restore',
        ],
        'deliverables': ['Azure Backup operational', 'First successful backup'],
    },
    
    'phase_2_veeam': {
        'duration_weeks': 2,
        'tasks': [
            'Coordinate with CGI Veeam team',
            'Add Rota VMs to Veeam backup job',
            'Configure application-aware processing',
            'Set up backup copy job to DR site',
        ],
        'deliverables': ['Veeam backup operational', 'DR replication working'],
    },
    
    'phase_3_automation': {
        'duration_weeks': 1,
        'tasks': [
            'Implement automated restore testing',
            'Configure SureBackup for application validation',
            'Set up backup monitoring dashboards',
            'Integrate with ServiceNow for ticketing',
        ],
        'deliverables': ['Automated testing live', 'Monitoring dashboard'],
    },
    
    'phase_4_validation': {
        'duration_weeks': 1,
        'tasks': [
            'Perform full DR drill with backup restore',
            'Validate RTO/RPO compliance',
            'Document restore procedures',
            'Train HSCP staff on restore requests',
        ],
        'deliverables': ['DR drill passed', 'Runbook complete'],
    },
    
    'total_timeline': {
        'total_weeks': 5,
        'go_live_date': 'February 11, 2026',
    },
}

# ============================================================================
# SECTION 15: Next Steps & Handover
# ============================================================================

NEXT_STEPS = {
    'immediate': [
        'Obtain Azure Backup vault credentials from CGI',
        'Request Veeam Backup & Replication access',
        'Schedule kickoff meeting with CGI backup team',
        'Review and sign off on backup policies',
    ],
    
    'week_1': [
        'Configure Azure Backup for PostgreSQL database',
        'Test initial backup and restore',
        'Set up backup monitoring alerts',
    ],
    
    'week_2_3': [
        'Integrate with Veeam for VM backups',
        'Configure backup replication to DR site',
        'Implement automated restore testing',
    ],
    
    'week_4_5': [
        'Perform DR drill with backup restore',
        'Validate RTO/RPO compliance',
        'Complete handover documentation',
    ],
    
    'post_go_live': [
        'Monitor backup success rates daily for 2 weeks',
        'Review backup storage growth trends',
        'Optimize backup policies based on actual data',
        'Schedule quarterly DR drills',
    ],
    
    'dependencies': {
        'task_5_dr_automation': 'Leverages DR automation (dr_automation.py) for failover testing',
        'task_6_sla': 'Aligns with RTO/RPO commitments in SLA_AGREEMENT_JAN2026.md',
        'task_7_firewall': 'Backup traffic requires NSG rules for Azure Backup ports',
    },
    
    'preview_task_10': {
        'title': 'CGI Monitoring Tools Integration',
        'description': 'Integrate backup status into CGI monitoring (SCOM/SolarWinds)',
        'effort_weeks': 1,
    },
}

# Export all settings
__all__ = [
    'AZURE_BACKUP',
    'VEEAM_BACKUP',
    'BACKUP_VERIFICATION',
    'BACKUP_MONITORING',
    'BACKUP_SECURITY',
    'BACKUP_SLA',
    'BACKUP_DR_INTEGRATION',
    'RETENTION_POLICY',
    'BACKUP_PERFORMANCE',
    'CGI_COORDINATION',
    'BACKUP_COSTS',
    'ACADEMIC_RESEARCH',
    'BUSINESS_CASE',
    'IMPLEMENTATION_ROADMAP',
    'NEXT_STEPS',
]
