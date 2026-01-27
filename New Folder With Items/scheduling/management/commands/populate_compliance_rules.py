from django.core.management.base import BaseCommand
from scheduling.models import ComplianceRule
import json


class Command(BaseCommand):
    help = 'Populate compliance rules for UK care home regulations'

    def handle(self, *args, **options):
        self.stdout.write('Populating compliance rules...')
        
        rules = [
            # Working Time Directive (WTD)
            {
                'code': 'WTD_48_HOURS',
                'name': '48-Hour Working Week Limit',
                'category': 'WORKING_TIME',
                'description': 'Staff must not work more than an average of 48 hours per week over a 17-week reference period, unless they have opted out.',
                'severity': 'CRITICAL',
                'parameters': {
                    'max_hours_per_week': 48,
                    'reference_period_weeks': 17,
                    'allow_opt_out': True
                },
                'remediation_steps': 'Review staff schedule immediately. Redistribute shifts to bring hours within legal limit. If opt-out needed, obtain written consent.',
                'is_active': True,
            },
            {
                'code': 'WTD_REST_11_HOURS',
                'name': '11-Hour Daily Rest Period',
                'category': 'REST_PERIOD',
                'description': 'Workers are entitled to 11 consecutive hours of rest in any 24-hour period.',
                'severity': 'CRITICAL',
                'parameters': {
                    'min_rest_hours': 11,
                    'consecutive': True
                },
                'remediation_steps': 'Adjust shift patterns to ensure minimum 11-hour gap between shifts. Review rota planning process.',
                'is_active': True,
            },
            {
                'code': 'WTD_REST_24_HOURS',
                'name': '24-Hour Weekly Rest Period',
                'category': 'REST_PERIOD',
                'description': 'Workers are entitled to an uninterrupted 24-hour rest period in each 7-day period, or an uninterrupted 48-hour rest period in each 14-day period.',
                'severity': 'HIGH',
                'parameters': {
                    'min_rest_hours': 24,
                    'period_days': 7,
                    'alternative_hours': 48,
                    'alternative_period': 14
                },
                'remediation_steps': 'Ensure staff have appropriate rest days. Review weekly rota patterns.',
                'is_active': True,
            },
            {
                'code': 'WTD_BREAKS',
                'name': 'Rest Breaks During Work',
                'category': 'REST_PERIOD',
                'description': 'Workers working more than 6 hours must have at least a 20-minute uninterrupted rest break.',
                'severity': 'MEDIUM',
                'parameters': {
                    'shift_duration_threshold': 6,
                    'min_break_minutes': 20,
                    'uninterrupted': True
                },
                'remediation_steps': 'Ensure break times are scheduled and protected. Update shift documentation.',
                'is_active': True,
            },
            
            # Staffing Levels
            {
                'code': 'MIN_DAY_STAFFING',
                'name': 'Minimum Day Shift Staffing',
                'category': 'STAFFING_LEVELS',
                'description': 'Each unit must maintain minimum staffing levels during day shifts to ensure safe care delivery.',
                'severity': 'CRITICAL',
                'parameters': {
                    'min_scw_per_unit': 1,
                    'min_sca_per_unit': 1,
                    'total_min_day_staff': 17
                },
                'remediation_steps': 'Immediately arrange cover through bank staff, agency, or overtime. Escalate to senior management.',
                'is_active': True,
            },
            {
                'code': 'MIN_NIGHT_STAFFING',
                'name': 'Minimum Night Shift Staffing',
                'category': 'STAFFING_LEVELS',
                'description': 'Each unit must maintain minimum staffing levels during night shifts to ensure resident safety.',
                'severity': 'CRITICAL',
                'parameters': {
                    'min_scwn_per_unit': 1,
                    'min_scan_per_unit': 1,
                    'total_min_night_staff': 17
                },
                'remediation_steps': 'Immediately arrange night cover. Activate on-call procedures if necessary.',
                'is_active': True,
            },
            # SKILL_MIX_RATIO rule removed - ratio was unattainable and did not reflect home needs
            {
                'code': 'WEEKEND_STAFFING',
                'name': 'Weekend Staffing Levels',
                'category': 'STAFFING_LEVELS',
                'description': 'Weekend shifts must maintain the same staffing levels as weekdays to ensure consistent care.',
                'severity': 'HIGH',
                'parameters': {
                    'match_weekday_levels': True,
                    'min_percentage': 100
                },
                'remediation_steps': 'Review weekend rota. Ensure adequate staff scheduled for Saturday and Sunday.',
                'is_active': True,
            },
            
            # Annual Leave
            {
                'code': 'LEAVE_ENTITLEMENT',
                'name': 'Minimum Annual Leave Entitlement',
                'category': 'ANNUAL_LEAVE',
                'description': 'All workers are entitled to a minimum of 5.6 weeks (28 days for full-time workers) paid annual leave per year.',
                'severity': 'MEDIUM',
                'parameters': {
                    'min_weeks': 5.6,
                    'min_days_fulltime': 28,
                    'prorata_for_parttime': True
                },
                'remediation_steps': 'Review individual leave balances. Ensure all staff can take their full entitlement.',
                'is_active': True,
            },
            {
                'code': 'LEAVE_NOTICE_PERIOD',
                'name': 'Leave Request Notice Period',
                'category': 'ANNUAL_LEAVE',
                'description': 'Staff must provide adequate notice for annual leave requests to allow proper rota planning.',
                'severity': 'LOW',
                'parameters': {
                    'min_notice_days': 14,
                    'emergency_exceptions': True
                },
                'remediation_steps': 'Communicate notice requirements to staff. Update leave request policy.',
                'is_active': True,
            },
            {
                'code': 'LEAVE_COVERAGE',
                'name': 'Leave Coverage Planning',
                'category': 'ANNUAL_LEAVE',
                'description': 'Annual leave must not reduce staffing below minimum safe levels.',
                'severity': 'HIGH',
                'parameters': {
                    'check_staffing_levels': True,
                    'max_simultaneous_leave_percentage': 20
                },
                'remediation_steps': 'Review leave calendar. Stagger leave requests or arrange cover.',
                'is_active': True,
            },
            
            # Training & Certification
            {
                'code': 'MANDATORY_TRAINING',
                'name': 'Mandatory Training Compliance',
                'category': 'TRAINING',
                'description': 'All care staff must complete and maintain mandatory training requirements.',
                'severity': 'HIGH',
                'parameters': {
                    'training_types': [
                        'Safeguarding Adults',
                        'Moving and Handling',
                        'Fire Safety',
                        'First Aid',
                        'Infection Control',
                        'Medication Administration'
                    ],
                    'renewal_months': 12
                },
                'remediation_steps': 'Schedule overdue training immediately. Staff may be restricted from certain duties until compliant.',
                'is_active': True,
            },
            {
                'code': 'INDUCTION_COMPLETION',
                'name': 'Care Certificate Induction',
                'category': 'TRAINING',
                'description': 'New care staff must complete the Care Certificate within 12 weeks of starting.',
                'severity': 'MEDIUM',
                'parameters': {
                    'completion_weeks': 12,
                    'standards_count': 15
                },
                'remediation_steps': 'Assign mentor. Accelerate induction schedule. Document progress.',
                'is_active': True,
            },
            
            # Data Protection (GDPR)
            {
                'code': 'DATA_RETENTION',
                'name': 'Staff Data Retention Limits',
                'category': 'DATA_PROTECTION',
                'description': 'Personal data of former staff must not be retained longer than necessary.',
                'severity': 'MEDIUM',
                'parameters': {
                    'retention_years': 6,
                    'review_frequency_months': 12
                },
                'remediation_steps': 'Review retention schedule. Securely delete data older than retention period.',
                'is_active': True,
            },
            {
                'code': 'ACCESS_AUDIT',
                'name': 'Regular Access Log Reviews',
                'category': 'DATA_PROTECTION',
                'description': 'System access logs must be reviewed regularly to detect unauthorized access.',
                'severity': 'MEDIUM',
                'parameters': {
                    'review_frequency_days': 30,
                    'failed_login_threshold': 5
                },
                'remediation_steps': 'Investigate suspicious access patterns. Review user permissions.',
                'is_active': True,
            },
            
            # Health & Safety
            {
                'code': 'INCIDENT_REPORTING',
                'name': 'Timely Incident Reporting',
                'category': 'HEALTH_SAFETY',
                'description': 'All incidents must be reported within required timeframes.',
                'severity': 'HIGH',
                'parameters': {
                    'max_reporting_hours': 24,
                    'serious_incident_hours': 2
                },
                'remediation_steps': 'Complete incident report immediately. Notify line management and relevant authorities.',
                'is_active': True,
            },
            {
                'code': 'LONE_WORKING',
                'name': 'Lone Working Safeguards',
                'category': 'HEALTH_SAFETY',
                'description': 'Night shifts must never be staffed by a single person for safety reasons.',
                'severity': 'CRITICAL',
                'parameters': {
                    'min_staff_per_shift': 2,
                    'night_shift_requirement': True
                },
                'remediation_steps': 'Immediately arrange additional cover. Never leave single staff member on duty.',
                'is_active': True,
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for rule_data in rules:
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
        self.stdout.write(f'  Created: {created_count} rules')
        self.stdout.write(f'  Updated: {updated_count} rules')
        self.stdout.write(f'  Total: {len(rules)} rules')
        self.stdout.write('')
        
        # Display breakdown by category
        self.stdout.write('Breakdown by category:')
        from django.db.models import Count
        breakdown = ComplianceRule.objects.values('category').annotate(count=Count('id')).order_by('category')
        for item in breakdown:
            category_display = dict(ComplianceRule.RULE_CATEGORY_CHOICES).get(item['category'], item['category'])
            self.stdout.write(f'  {category_display}: {item["count"]} rules')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ Compliance rules populated successfully!'))
