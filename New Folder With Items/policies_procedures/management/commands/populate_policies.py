"""
Management command to populate initial policies and templates for Module 5

This command creates:
- Sample policy categories
- Policy templates
- Initial organizational policies
- Sample procedures
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from policies_procedures.models import (
    Policy, PolicyVersion, PolicyAcknowledgement,
    PolicyReview, Procedure, ProcedureStep,
    PolicyComplianceCheck, AuditTrail
)
from scheduling.models import Home, Unit, Role
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Populate initial policies and procedures for TQM Module 5'

    def handle(self, *args, **options):
        self.stdout.write('Populating Module 5: Policies & Procedures...')
        
        # Get or create admin user
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.ERROR('No admin user found. Please create an admin user first.'))
            return
        
        # Sample Policy Categories
        categories = [
            {
                'name': 'Clinical Care',
                'policies': [
                    'Medication Management Policy',
                    'Falls Prevention & Management',
                    'Nutrition & Hydration Policy',
                    'End of Life Care Policy',
                ]
            },
            {
                'name': 'Health & Safety',
                'policies': [
                    'Fire Safety Policy',
                    'Infection Prevention & Control',
                    'Manual Handling Policy',
                    'Accident & Incident Reporting',
                ]
            },
            {
                'name': 'Safeguarding',
                'policies': [
                    'Adult Support & Protection',
                    'Whistleblowing Policy',
                    'CCTV & Surveillance Policy',
                ]
            },
            {
                'name': 'Operational',
                'policies': [
                    'Admission & Discharge Policy',
                    'Visiting Policy',
                    'Complaints Management',
                    'Record Keeping & Confidentiality',
                ]
            },
            {
                'name': 'Human Resources',
                'policies': [
                    'Recruitment & Selection',
                    'Induction & Probation',
                    'Supervision & Appraisal',
                    'Disciplinary & Grievance',
                ]
            },
        ]
        
        policy_count = 0
        
        for cat_data in categories:
            category_name = cat_data['name']
            
            for policy_title in cat_data['policies']:
                # Create policy reference number
                ref_num = f"POL-{policy_count+1:04d}"
                
                policy, created = Policy.objects.get_or_create(
                    reference_number=ref_num,
                    defaults={
                        'title': policy_title,
                        'category': category_name,
                        'status': 'active',
                        'version': '1.0',
                        'effective_date': date.today(),
                        'next_review_date': date.today() + timedelta(days=365),
                        'review_frequency_months': 12,
                        'owner': admin_user,
                        'created_by': admin_user,
                        'scope': 'organization',
                        'regulatory_framework': 'Health & Social Care Standards',
                        'care_inspectorate_theme': 'Care & Support',
                        'mandatory_acknowledgement': True,
                    }
                )
                
                if created:
                    policy_count += 1
                    self.stdout.write(self.style.SUCCESS(f'Created policy: {policy_title}'))
                    
                    # Create initial version
                    PolicyVersion.objects.create(
                        policy=policy,
                        version_number='1.0',
                        created_by=admin_user,
                        change_summary='Initial policy creation',
                        effective_date=date.today()
                    )
        
        self.stdout.write(self.style.SUCCESS(f'\nCreated {policy_count} policies across {len(categories)} categories'))
        self.stdout.write(self.style.SUCCESS('\nModule 5 sample data populated successfully!'))
