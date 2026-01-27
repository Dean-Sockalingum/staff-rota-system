"""
Management command to populate Policy & Procedures sample data
Creates 15 realistic Scottish care home policies with versions, acknowledgements, reviews, and compliance checks
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal

from policies_procedures.models import (
    Policy, PolicyVersion, PolicyAcknowledgement, PolicyReview,
    Procedure, ProcedureStep, PolicyComplianceCheck, AuditTrail
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate sample policies and procedures data for Scottish care home'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating Policies & Procedures sample data...')
        
        # Get or create sample users
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                admin_user = User.objects.create_user('admin', 'admin@example.com', 'admin123')
                admin_user.is_staff = True
                admin_user.is_superuser = True
                admin_user.save()
        except:
            admin_user = User.objects.first()
        
        staff_users = list(User.objects.filter(is_staff=True)[:5])
        if not staff_users:
            staff_users = [admin_user]
        
        # Policy data - 15 Scottish care home policies
        policies_data = [
            {
                'policy_number': 'POL-001',
                'title': 'Safeguarding Adults Policy',
                'category': 'safeguarding',
                'summary': 'This policy outlines procedures for protecting adults at risk from abuse, harm, and neglect in accordance with the Adult Support and Protection (Scotland) Act 2007.',
                'keywords': 'safeguarding, adult protection, abuse prevention, ASPA',
                'regulatory_framework': 'Adult Support and Protection (Scotland) Act 2007, Care Inspectorate Standards',
                'review_frequency_months': 12,
                'is_mandatory': True,
                'department': 'Safeguarding',
            },
            {
                'policy_number': 'POL-002',
                'title': 'Infection Prevention & Control Policy',
                'category': 'infection_control',
                'summary': 'Comprehensive infection prevention and control policy aligned with Health Protection Scotland guidelines and COVID-19 protocols.',
                'keywords': 'infection control, IPC, hand hygiene, PPE, COVID-19',
                'regulatory_framework': 'Health Protection Scotland Guidelines, Care Inspectorate Standard 5.10',
                'review_frequency_months': 6,
                'is_mandatory': True,
                'department': 'Clinical Services',
            },
            {
                'policy_number': 'POL-003',
                'title': 'Medication Management Policy',
                'category': 'clinical',
                'summary': 'Safe administration, storage, and disposal of medications in line with NICE guidelines and Care Inspectorate standards.',
                'keywords': 'medication, MAR charts, controlled drugs, administration',
                'regulatory_framework': 'NICE Guidelines NG5, Care Inspectorate Standard 4.11',
                'review_frequency_months': 12,
                'is_mandatory': True,
                'department': 'Clinical Services',
            },
            {
                'policy_number': 'POL-004',
                'title': 'Falls Prevention Policy',
                'category': 'health_safety',
                'summary': 'Proactive approach to reducing falls risk through assessment, environmental safety, and care planning.',
                'keywords': 'falls, risk assessment, mobility, safety',
                'regulatory_framework': 'Scottish Patient Safety Programme, Care Inspectorate Standard 4.11',
                'review_frequency_months': 12,
                'is_mandatory': True,
                'department': 'Clinical Services',
            },
            {
                'policy_number': 'POL-005',
                'title': 'Dignity & Respect Policy',
                'category': 'quality',
                'summary': 'Ensuring person-centered care that respects individual rights, choices, and dignity in line with Health & Social Care Standards.',
                'keywords': 'dignity, respect, person-centered, rights, choices',
                'regulatory_framework': 'Health & Social Care Standards 2017, Care Inspectorate',
                'review_frequency_months': 24,
                'is_mandatory': True,
                'department': 'Quality Assurance',
            },
            {
                'policy_number': 'POL-006',
                'title': 'Whistleblowing Policy',
                'category': 'hr',
                'summary': 'Protected disclosure procedure enabling staff to raise concerns about malpractice or wrongdoing safely.',
                'keywords': 'whistleblowing, disclosure, concerns, reporting',
                'regulatory_framework': 'Public Interest Disclosure Act 1998, Care Inspectorate Standard 4.24',
                'review_frequency_months': 24,
                'is_mandatory': True,
                'department': 'Human Resources',
            },
            {
                'policy_number': 'POL-007',
                'title': 'Health & Safety Policy',
                'category': 'health_safety',
                'summary': 'Comprehensive health and safety policy meeting HSE requirements and protecting residents, staff, and visitors.',
                'keywords': 'health and safety, HSE, risk assessment, COSHH',
                'regulatory_framework': 'Health and Safety at Work Act 1974, Management of Health and Safety at Work Regulations 1999',
                'review_frequency_months': 12,
                'is_mandatory': True,
                'department': 'Health & Safety',
            },
            {
                'policy_number': 'POL-008',
                'title': 'Fire Safety Policy',
                'category': 'health_safety',
                'summary': 'Fire prevention, detection, and evacuation procedures compliant with Scottish Fire & Rescue Service standards.',
                'keywords': 'fire safety, evacuation, PEEP, fire drills',
                'regulatory_framework': 'Fire (Scotland) Act 2005, Care Inspectorate Standard 4.11',
                'review_frequency_months': 12,
                'is_mandatory': True,
                'department': 'Health & Safety',
            },
            {
                'policy_number': 'POL-009',
                'title': 'Food Safety & Nutrition Policy',
                'category': 'operational',
                'summary': 'Safe food handling, dietary planning, and nutritional support meeting Food Standards Scotland requirements.',
                'keywords': 'food safety, nutrition, catering, hydration, HACCP',
                'regulatory_framework': 'Food Hygiene (Scotland) Regulations 2006, Care Inspectorate Standard 4.11',
                'review_frequency_months': 12,
                'is_mandatory': True,
                'department': 'Catering Services',
            },
            {
                'policy_number': 'POL-010',
                'title': 'Equality & Diversity Policy',
                'category': 'hr',
                'summary': 'Commitment to equality, diversity, and inclusion in line with Equality Act 2010 and Public Sector Equality Duty.',
                'keywords': 'equality, diversity, inclusion, protected characteristics',
                'regulatory_framework': 'Equality Act 2010, Public Sector Equality Duty (Scotland)',
                'review_frequency_months': 24,
                'is_mandatory': True,
                'department': 'Human Resources',
            },
            {
                'policy_number': 'POL-011',
                'title': 'End of Life Care Policy',
                'category': 'clinical',
                'summary': 'Compassionate end of life care aligned with Scottish Palliative Care Guidelines and care home best practice.',
                'keywords': 'palliative care, end of life, death, bereavement, dignity',
                'regulatory_framework': 'Scottish Palliative Care Guidelines, Care Inspectorate Standard 4.11',
                'review_frequency_months': 12,
                'is_mandatory': False,
                'department': 'Clinical Services',
            },
            {
                'policy_number': 'POL-012',
                'title': 'Moving & Handling Policy',
                'category': 'health_safety',
                'summary': 'Safe manual handling practices protecting staff and residents from injury during transfers and repositioning.',
                'keywords': 'manual handling, hoists, transfers, mobility, risk assessment',
                'regulatory_framework': 'Manual Handling Operations Regulations 1992, HSE Guidelines',
                'review_frequency_months': 12,
                'is_mandatory': True,
                'department': 'Health & Safety',
            },
            {
                'policy_number': 'POL-013',
                'title': 'GDPR & Data Protection Policy',
                'category': 'it_data',
                'summary': 'Data protection and privacy policy ensuring GDPR compliance and safeguarding resident information.',
                'keywords': 'GDPR, data protection, privacy, confidentiality, ICO',
                'regulatory_framework': 'UK GDPR 2018, Data Protection Act 2018, ICO Guidelines',
                'review_frequency_months': 12,
                'is_mandatory': True,
                'department': 'Information Governance',
            },
            {
                'policy_number': 'POL-014',
                'title': 'Complaints Handling Policy',
                'category': 'quality',
                'summary': 'Fair and transparent complaints process meeting Scottish Public Services Ombudsman model complaints handling procedure.',
                'keywords': 'complaints, feedback, resolution, SPSO, concerns',
                'regulatory_framework': 'SPSO Model Complaints Handling Procedure, Care Inspectorate Standard 4.8',
                'review_frequency_months': 24,
                'is_mandatory': True,
                'department': 'Quality Assurance',
            },
            {
                'policy_number': 'POL-015',
                'title': 'Visiting & Family Engagement Policy',
                'category': 'operational',
                'summary': 'Welcoming visiting arrangements and family involvement in care planning, including post-COVID protocols.',
                'keywords': 'visiting, families, relatives, engagement, communication',
                'regulatory_framework': 'Health & Social Care Standards 2017, Care Inspectorate Guidance',
                'review_frequency_months': 6,
                'is_mandatory': False,
                'department': 'Operations',
            },
        ]
        
        # Create policies
        created_policies = []
        for idx, policy_data in enumerate(policies_data, 1):
            effective_date = timezone.now().date() - timedelta(days=180 - idx*5)
            next_review_date = effective_date + timedelta(days=policy_data['review_frequency_months'] * 30)
            
            # Vary status for realism
            if idx <= 12:
                status = 'active'
            elif idx == 13:
                status = 'under_review'
            elif idx == 14:
                status = 'draft'
            else:
                status = 'active'
            
            policy = Policy.objects.create(
                policy_number=policy_data['policy_number'],
                title=policy_data['title'],
                category=policy_data['category'],
                summary=policy_data['summary'],
                keywords=policy_data['keywords'],
                regulatory_framework=policy_data['regulatory_framework'],
                effective_date=effective_date,
                next_review_date=next_review_date,
                review_frequency_months=policy_data['review_frequency_months'],
                status=status,
                version=Decimal('1.0'),
                owner=admin_user,
                department=policy_data['department'],
                is_mandatory=policy_data['is_mandatory'],
            )
            created_policies.append(policy)
            
            # Create version history (1-2 versions per policy)
            PolicyVersion.objects.create(
                policy=policy,
                version_number=Decimal('1.0'),
                change_summary='Initial policy creation',
                created_by=admin_user,
                created_date=effective_date,
                is_current=True,
                approval_date=effective_date,
                approved_by=admin_user,
            )
            
            # Some policies get version 1.1
            if idx in [1, 2, 3, 7, 13]:
                version_date = effective_date + timedelta(days=90)
                PolicyVersion.objects.create(
                    policy=policy,
                    version_number=Decimal('1.1'),
                    change_summary='Updated to reflect new regulatory guidance' if idx != 13 else 'Minor clarifications and formatting improvements',
                    created_by=admin_user,
                    created_date=version_date,
                    is_current=False,
                    approval_date=version_date if idx != 13 else None,
                    approved_by=admin_user if idx != 13 else None,
                )
            
            # Create acknowledgements (2-5 staff per mandatory policy)
            if policy.is_mandatory:
                num_acks = min(len(staff_users), 3 + idx % 3)
                for i in range(num_acks):
                    if i < len(staff_users):
                        ack_date = effective_date + timedelta(days=i*7 + idx)
                        PolicyAcknowledgement.objects.create(
                            policy=policy,
                            staff_member=staff_users[i],
                            acknowledged_date=timezone.make_aware(timezone.datetime.combine(ack_date, timezone.datetime.min.time())),
                            signature=staff_users[i].get_full_name() or staff_users[i].username,
                            ip_address='192.168.1.100',
                            acknowledgement_method='digital',
                            comments='Read and understood' if i % 3 == 0 else '',
                        )
            
            # Create reviews (1 review per policy, some completed)
            review_date = effective_date + timedelta(days=120)
            review = PolicyReview.objects.create(
                policy=policy,
                reviewer=admin_user,
                review_date=review_date,
                review_outcome='no_changes' if idx <= 8 else 'minor_updates',
                recommendations=f'Policy remains current and fit for purpose. Next review due {next_review_date}.' if idx <= 8 else 'Recommend minor updates to reflect latest regulatory guidance.',
                next_review_date=next_review_date,
            )
            
            # Complete most reviews
            if idx <= 10:
                review.completed_by = admin_user
                review.completion_date = review_date + timedelta(days=2)
                review.save()
            
            # Create compliance checks (1-2 per policy)
            if idx <= 12:
                compliance_date = effective_date + timedelta(days=150)
                PolicyComplianceCheck.objects.create(
                    policy=policy,
                    check_date=compliance_date,
                    checker=admin_user,
                    compliance_status='fully_compliant' if idx <= 8 else 'partially_compliant' if idx <= 10 else 'non_compliant',
                    findings=f'Compliance audit conducted on {compliance_date}. Policy implementation reviewed across all care areas.' + 
                             (' All requirements met.' if idx <= 8 else ' Minor gaps identified in documentation.' if idx <= 10 else ' Training gaps identified.'),
                    actions_required='' if idx <= 8 else 'Update staff training matrix' if idx <= 10 else 'Schedule refresher training for all care staff',
                    due_date=compliance_date + timedelta(days=30) if idx > 8 else None,
                    completed=True if idx <= 8 else False,
                )
            
            # Create sample procedures for key policies
            if idx in [2, 3, 4, 8, 12]:  # IPC, Medication, Falls, Fire, Moving & Handling
                procedure_titles = {
                    2: 'Hand Hygiene Procedure',
                    3: 'Controlled Drug Administration Procedure',
                    4: 'Falls Risk Assessment Procedure',
                    8: 'Fire Evacuation Procedure',
                    12: 'Hoist Transfer Procedure',
                }
                
                procedure = Procedure.objects.create(
                    title=procedure_titles[idx],
                    procedure_number=f'PROC-{idx:03d}',
                    policy=policy,
                    steps=f'Step-by-step procedure for {procedure_titles[idx].lower()}.',
                    equipment_required='Standard PPE and equipment as specified' if idx == 2 else 'Hoist, sling, transfer board' if idx == 12 else 'As required',
                    safety_notes='Follow all safety protocols. Report any incidents immediately.',
                    updated_by=admin_user,
                )
                
                # Add procedure steps
                steps_data = {
                    2: ['Wet hands with water', 'Apply soap', 'Lather for 20 seconds', 'Rinse thoroughly', 'Dry with paper towel'],
                    3: ['Verify resident identity', 'Check medication against MAR chart', 'Administer medication', 'Observe resident', 'Document administration', 'Return controlled drugs to locked storage'],
                    4: ['Review resident history', 'Complete falls risk assessment tool', 'Identify environmental hazards', 'Develop prevention care plan', 'Review mobility aids'],
                    8: ['Sound fire alarm', 'Call 999', 'Evacuate residents using PEEP', 'Close fire doors', 'Assemble at muster point', 'Account for all residents and staff'],
                    12: ['Explain procedure to resident', 'Check hoist for defects', 'Select correct sling size', 'Position sling', 'Attach to hoist', 'Perform lift smoothly', 'Lower resident safely'],
                }
                
                for step_num, step_desc in enumerate(steps_data.get(idx, []), 1):
                    ProcedureStep.objects.create(
                        procedure=procedure,
                        step_number=step_num,
                        description=step_desc,
                        critical_point=True if step_num in [1, 3, 6] else False,
                        evidence_required=f'Sign-off required on completion of step {step_num}' if step_num in [3, 6] else '',
                    )
            
            # Create audit trail entries
            AuditTrail.objects.create(
                policy=policy,
                action_type='created',
                performed_by=admin_user,
                timestamp=timezone.make_aware(timezone.datetime.combine(effective_date, timezone.datetime.min.time())),
                details=f'Policy {policy.policy_number} created and published',
            )
            
            self.stdout.write(self.style.SUCCESS(f'✓ Created {policy.policy_number}: {policy.title}'))
        
        # Summary statistics
        total_policies = Policy.objects.count()
        total_versions = PolicyVersion.objects.count()
        total_acknowledgements = PolicyAcknowledgement.objects.count()
        total_reviews = PolicyReview.objects.count()
        total_procedures = Procedure.objects.count()
        total_compliance = PolicyComplianceCheck.objects.count()
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('POLICIES & PROCEDURES DATA POPULATION COMPLETE'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS(f'Policies Created: {total_policies}'))
        self.stdout.write(self.style.SUCCESS(f'Policy Versions: {total_versions}'))
        self.stdout.write(self.style.SUCCESS(f'Staff Acknowledgements: {total_acknowledgements}'))
        self.stdout.write(self.style.SUCCESS(f'Policy Reviews: {total_reviews}'))
        self.stdout.write(self.style.SUCCESS(f'Procedures: {total_procedures}'))
        self.stdout.write(self.style.SUCCESS(f'Compliance Checks: {total_compliance}'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))
