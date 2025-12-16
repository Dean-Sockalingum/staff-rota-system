"""
Enhanced compliance rules with training and incident tracking
Run this to add additional compliance rules
"""
from django.core.management.base import BaseCommand
from scheduling.models import ComplianceRule
import json


class Command(BaseCommand):
    help = 'Add enhanced compliance rules for training and incident tracking'

    def handle(self, *args, **options):
        self.stdout.write('Adding enhanced compliance rules...\n')
        
        enhanced_rules = [
            # Enhanced Training Rules
            {
                'code': 'TRAINING_EXPIRY_WARNING',
                'name': 'Training Certification Expiry Warning',
                'category': 'TRAINING',
                'description': 'Alert when staff training certifications are due to expire within 30 days.',
                'severity': 'MEDIUM',
                'parameters': {
                    'warning_days': 30,
                    'check_types': ['Safeguarding', 'Fire Safety', 'First Aid', 'Moving & Handling'],
                },
                'remediation_steps': 'Schedule renewal training immediately. Book refresher courses for affected staff.',
                'is_active': True,
            },
            {
                'code': 'TRAINING_COMPLETION_RATE',
                'name': 'Team Training Completion Rate',
                'category': 'TRAINING',
                'description': 'Ensure at least 95% of team members have completed mandatory training.',
                'severity': 'HIGH',
                'parameters': {
                    'min_completion_rate': 95,
                    'mandatory_courses': [
                        'Safeguarding Adults',
                        'Fire Safety',
                        'Infection Control',
                    ],
                },
                'remediation_steps': 'Identify staff with incomplete training. Schedule training sessions.',
                'is_active': True,
            },
            {
                'code': 'SUPERVISION_RATIO',
                'name': 'New Staff Supervision Requirements',
                'category': 'TRAINING',
                'description': 'New staff must work supervised shifts during probation period (first 12 weeks).',
                'severity': 'HIGH',
                'parameters': {
                    'probation_weeks': 12,
                    'min_supervision_percentage': 80,
                },
                'remediation_steps': 'Ensure new staff are scheduled with experienced supervisors.',
                'is_active': True,
            },
            
            # Incident Reporting Rules
            {
                'code': 'INCIDENT_FOLLOW_UP',
                'name': 'Incident Investigation Follow-up',
                'category': 'HEALTH_SAFETY',
                'description': 'All incidents must have follow-up investigation completed within 7 days.',
                'severity': 'HIGH',
                'parameters': {
                    'max_days_investigation': 7,
                    'require_witness_statements': True,
                },
                'remediation_steps': 'Complete investigation immediately. Gather witness statements and documentation.',
                'is_active': True,
            },
            {
                'code': 'SERIOUS_INCIDENT_NOTIFICATION',
                'name': 'Serious Incident External Notification',
                'category': 'HEALTH_SAFETY',
                'description': 'Serious incidents (injuries, safeguarding concerns) must be reported to CQC/authorities within required timeframes.',
                'severity': 'CRITICAL',
                'parameters': {
                    'notification_hours': 24,
                    'serious_categories': ['Major Injury', 'Death', 'Safeguarding Alert', 'Medication Error'],
                },
                'remediation_steps': 'Notify CQC and relevant authorities immediately. Complete statutory notifications.',
                'is_active': True,
            },
            {
                'code': 'INCIDENT_TREND_ANALYSIS',
                'name': 'Incident Pattern Monitoring',
                'category': 'HEALTH_SAFETY',
                'description': 'Monitor for recurring incident patterns (3+ similar incidents in 30 days).',
                'severity': 'MEDIUM',
                'parameters': {
                    'threshold_count': 3,
                    'period_days': 30,
                    'pattern_types': ['Falls', 'Medication Errors', 'Challenging Behaviour'],
                },
                'remediation_steps': 'Investigate root cause. Implement preventive measures. Review risk assessments.',
                'is_active': True,
            },
            
            # Medication Safety Rules
            {
                'code': 'MEDICATION_COMPETENCY',
                'name': 'Medication Administration Competency',
                'category': 'TRAINING',
                'description': 'Only staff with valid medication administration training may administer medications.',
                'severity': 'CRITICAL',
                'parameters': {
                    'required_certification': 'Medication Administration',
                    'annual_reassessment': True,
                },
                'remediation_steps': 'Remove medication duties from non-certified staff. Schedule competency training.',
                'is_active': True,
            },
            {
                'code': 'MEDICATION_ERROR_REPORTING',
                'name': 'Medication Error Reporting Compliance',
                'category': 'HEALTH_SAFETY',
                'description': 'All medication errors must be reported immediately and investigated.',
                'severity': 'CRITICAL',
                'parameters': {
                    'immediate_reporting': True,
                    'require_incident_form': True,
                    'notify_gp': True,
                },
                'remediation_steps': 'Complete incident report. Notify GP. Review medication procedures.',
                'is_active': True,
            },
            
            # Safeguarding Rules
            {
                'code': 'SAFEGUARDING_ALERT_RESPONSE',
                'name': 'Safeguarding Alert Response Time',
                'category': 'HEALTH_SAFETY',
                'description': 'Safeguarding concerns must be escalated to safeguarding lead within 2 hours.',
                'severity': 'CRITICAL',
                'parameters': {
                    'max_response_hours': 2,
                    'require_local_authority_notification': True,
                },
                'remediation_steps': 'Escalate immediately. Contact safeguarding lead and local authority.',
                'is_active': True,
            },
            {
                'code': 'SAFEGUARDING_TRAINING_LEVEL',
                'name': 'Safeguarding Training Levels',
                'category': 'TRAINING',
                'description': 'All staff must have appropriate level safeguarding training (Level 2 for care staff, Level 3 for managers).',
                'severity': 'HIGH',
                'parameters': {
                    'care_staff_level': 2,
                    'management_level': 3,
                    'renewal_years': 2,
                },
                'remediation_steps': 'Arrange safeguarding training at appropriate level. Update training records.',
                'is_active': True,
            },
            
            # Documentation & Records
            {
                'code': 'CARE_PLAN_REVIEW',
                'name': 'Care Plan Review Frequency',
                'category': 'DATA_PROTECTION',
                'description': 'Care plans must be reviewed and updated at least every 6 months or when needs change.',
                'severity': 'MEDIUM',
                'parameters': {
                    'review_frequency_months': 6,
                    'trigger_on_change': True,
                },
                'remediation_steps': 'Schedule care plan reviews. Update documentation.',
                'is_active': True,
            },
            {
                'code': 'STAFF_FILE_COMPLIANCE',
                'name': 'Staff Employment File Compliance',
                'category': 'DATA_PROTECTION',
                'description': 'Staff files must contain all required documentation (DBS, references, qualifications, etc.).',
                'severity': 'HIGH',
                'parameters': {
                    'required_documents': ['DBS Certificate', 'Right to Work', 'Qualifications', 'References (2)', 'ID'],
                    'dbs_renewal_years': 3,
                },
                'remediation_steps': 'Review staff files. Obtain missing documentation. Update DBS certificates.',
                'is_active': True,
            },
            
            # Infection Control
            {
                'code': 'INFECTION_CONTROL_OUTBREAK',
                'name': 'Infection Outbreak Management',
                'category': 'HEALTH_SAFETY',
                'description': 'Monitor for infection outbreaks (3+ cases of same infection in 7 days).',
                'severity': 'CRITICAL',
                'parameters': {
                    'threshold_cases': 3,
                    'period_days': 7,
                    'notify_hpa': True,
                },
                'remediation_steps': 'Activate outbreak procedures. Notify HPU. Implement enhanced infection control.',
                'is_active': True,
            },
            {
                'code': 'INFECTION_CONTROL_TRAINING',
                'name': 'Infection Control Training Currency',
                'category': 'TRAINING',
                'description': 'All care staff must have current infection control training (annual refresh).',
                'severity': 'HIGH',
                'parameters': {
                    'renewal_months': 12,
                    'covid_specific': True,
                },
                'remediation_steps': 'Schedule infection control training. Include COVID-19 protocols.',
                'is_active': True,
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for rule_data in enhanced_rules:
            # Convert parameters dict to JSON string
            rule_data['parameters'] = json.dumps(rule_data['parameters'])
            
            rule, created = ComplianceRule.objects.update_or_create(
                code=rule_data['code'],
                defaults=rule_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {rule.name}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'⟳ Updated: {rule.name}'))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Summary:'))
        self.stdout.write(f'  New rules created: {created_count}')
        self.stdout.write(f'  Existing rules updated: {updated_count}')
        self.stdout.write(f'  Total enhanced rules: {len(enhanced_rules)}')
        self.stdout.write('')
        
        # Display total rules by category
        self.stdout.write('Total rules by category:')
        from django.db.models import Count
        breakdown = ComplianceRule.objects.values('category').annotate(count=Count('id')).order_by('category')
        for item in breakdown:
            category_display = dict(ComplianceRule.RULE_CATEGORY_CHOICES).get(item['category'], item['category'])
            self.stdout.write(f'  {category_display}: {item["count"]} rules')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ Enhanced compliance rules added successfully!'))
