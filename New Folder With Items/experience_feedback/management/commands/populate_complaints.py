"""
Management command to populate sample complaints with investigation stages and stakeholders.
Demonstrates the enhanced complaint workflow.

Usage:
    python manage.py populate_complaints
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from experience_feedback.models import (
    Complaint,
    ComplaintInvestigationStage,
    ComplaintStakeholder,
    ComplaintSeverity,
    ComplaintStatus,
)
from scheduling.models import CareHome, Resident, User


class Command(BaseCommand):
    help = 'Populate sample complaints with investigation workflow data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Populating sample complaints...'))
        
        # Get necessary data
        try:
            care_home = CareHome.objects.first()
            if not care_home:
                self.stdout.write(self.style.ERROR('No care homes found. Please create a care home first.'))
                return
            
            resident = Resident.objects.filter(unit__care_home=care_home).first()
            investigator = User.objects.filter(is_staff=True).first()
            
            if not investigator:
                self.stdout.write(self.style.ERROR('No staff users found for investigation assignment.'))
                return
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error fetching data: {e}'))
            return
        
        # Sample complaints
        complaints_data = [
            {
                'reference': 'COMP-2026-001',
                'category': 'CARE_QUALITY',
                'severity': ComplaintSeverity.HIGH,
                'status': ComplaintStatus.INVESTIGATING,
                'complainant': 'Margaret Henderson',
                'relationship': 'Daughter',
                'description': 'Mother reports not receiving her morning medication on time for the past three days. She has diabetes and this is critical for her health.',
                'outcome': 'Ensure medication is administered on time every day and improve handover procedures.',
                'days_ago': 5,
            },
            {
                'reference': 'COMP-2026-002',
                'category': 'STAFF_CONDUCT',
                'severity': ComplaintSeverity.MEDIUM,
                'status': ComplaintStatus.ACKNOWLEDGED,
                'complainant': 'John MacLeod',
                'relationship': 'Son',
                'description': 'During a recent visit, I observed a care worker speaking to my father in a dismissive tone when he asked for help.',
                'outcome': 'Staff to receive training on dignity and respect, and implement better supervision.',
                'days_ago': 2,
            },
            {
                'reference': 'COMP-2026-003',
                'category': 'ENVIRONMENT',
                'severity': ComplaintSeverity.LOW,
                'status': ComplaintStatus.RESOLVED,
                'complainant': 'Patricia Campbell',
                'relationship': 'Resident',
                'description': 'The heating in the common room has been inconsistent. Sometimes it is too cold, other times too hot.',
                'outcome': 'Maintenance to check and repair heating system controls.',
                'days_ago': 14,
            },
            {
                'reference': 'COMP-2026-004',
                'category': 'MEALS',
                'severity': ComplaintSeverity.MEDIUM,
                'status': ComplaintStatus.INVESTIGATING,
                'complainant': 'Robert Fraser',
                'relationship': 'Family Member',
                'description': 'My aunt has special dietary requirements for her diabetes, but has been served regular desserts twice this week.',
                'outcome': 'Review dietary requirements system and ensure kitchen staff are properly informed.',
                'days_ago': 3,
            },
            {
                'reference': 'COMP-2026-005',
                'category': 'SAFETY',
                'severity': ComplaintSeverity.CRITICAL,
                'status': ComplaintStatus.INVESTIGATING,
                'complainant': 'Elizabeth Murray',
                'relationship': 'Daughter',
                'description': 'My mother fell in the bathroom. The call bell was out of reach and she was on the floor for 15 minutes before being found.',
                'outcome': 'Immediate review of call bell positioning and increase frequency of welfare checks.',
                'days_ago': 1,
            },
        ]
        
        created_count = 0
        
        for data in complaints_data:
            # Check if complaint already exists
            if Complaint.objects.filter(complaint_reference=data['reference']).exists():
                self.stdout.write(self.style.WARNING(f"Complaint {data['reference']} already exists, skipping..."))
                continue
            
            received_date = timezone.now().date() - timedelta(days=data['days_ago'])
            
            # Create complaint
            complaint = Complaint.objects.create(
                complaint_reference=data['reference'],
                care_home=care_home,
                complainant_name=data['complainant'],
                complainant_relationship=data['relationship'],
                complainant_contact='01234 567890',
                resident=resident,
                date_received=received_date,
                complaint_category=data['category'],
                severity=data['severity'],
                complaint_description=data['description'],
                desired_outcome=data['outcome'],
                status=data['status'],
                investigating_officer=investigator,
                created_by=investigator,
            )
            
            # Set target and actual dates
            if data['severity'] == ComplaintSeverity.CRITICAL:
                target_days = 7
            elif data['severity'] == ComplaintSeverity.HIGH:
                target_days = 14
            else:
                target_days = 20
            
            complaint.target_resolution_date = received_date + timedelta(days=target_days)
            
            if data['status'] in [ComplaintStatus.ACKNOWLEDGED, ComplaintStatus.INVESTIGATING, ComplaintStatus.RESOLVED]:
                complaint.date_acknowledged = received_date + timedelta(days=1)
            
            if data['status'] == ComplaintStatus.RESOLVED:
                complaint.actual_resolution_date = received_date + timedelta(days=target_days - 2)
                complaint.resolution_details = "Issue resolved through improved procedures and staff training."
                complaint.complainant_satisfied = True
            
            complaint.save()
            
            # Add investigation stages for complaints that are being investigated
            if data['status'] in [ComplaintStatus.INVESTIGATING, ComplaintStatus.RESOLVED]:
                stages = [
                    {
                        'name': 'INITIAL_REVIEW',
                        'status': 'COMPLETED',
                        'findings': 'Complaint logged and categorized. Initial assessment completed.',
                        'order': 1,
                        'days_offset': 1,
                    },
                    {
                        'name': 'EVIDENCE_GATHERING',
                        'status': 'COMPLETED' if data['status'] == ComplaintStatus.RESOLVED else 'IN_PROGRESS',
                        'findings': 'Reviewed care records, medication charts, and staff logs.' if data['status'] == ComplaintStatus.RESOLVED else 'Currently gathering documentation and evidence.',
                        'order': 2,
                        'days_offset': 2,
                    },
                    {
                        'name': 'STAFF_INTERVIEWS',
                        'status': 'COMPLETED' if data['status'] == ComplaintStatus.RESOLVED else 'PENDING',
                        'findings': 'Interviewed staff on duty. Identified gaps in procedure.' if data['status'] == ComplaintStatus.RESOLVED else '',
                        'order': 3,
                        'days_offset': 4,
                    },
                    {
                        'name': 'ROOT_CAUSE_ANALYSIS',
                        'status': 'COMPLETED' if data['status'] == ComplaintStatus.RESOLVED else 'PENDING',
                        'findings': 'Root cause identified: inadequate handover procedure.' if data['status'] == ComplaintStatus.RESOLVED else '',
                        'order': 4,
                        'days_offset': 6,
                    },
                    {
                        'name': 'ACTION_PLAN',
                        'status': 'COMPLETED' if data['status'] == ComplaintStatus.RESOLVED else 'PENDING',
                        'findings': 'Action plan developed with improvements.' if data['status'] == ComplaintStatus.RESOLVED else '',
                        'order': 5,
                        'days_offset': 8,
                    },
                ]
                
                for stage_data in stages:
                    ComplaintInvestigationStage.objects.create(
                        complaint=complaint,
                        stage_name=stage_data['name'],
                        assigned_to=investigator,
                        status=stage_data['status'],
                        start_date=received_date + timedelta(days=stage_data['days_offset']),
                        target_completion=received_date + timedelta(days=stage_data['days_offset'] + 2),
                        actual_completion=received_date + timedelta(days=stage_data['days_offset'] + 1) if stage_data['status'] == 'COMPLETED' else None,
                        findings=stage_data['findings'],
                        sequence_order=stage_data['order'],
                    )
            
            # Add stakeholders
            stakeholders = [
                {
                    'type': 'COMPLAINANT',
                    'name': data['complainant'],
                    'role': data['relationship'],
                    'involvement': 'Raised the complaint',
                    'requires_update': True,
                },
                {
                    'type': 'CARE_MANAGER',
                    'name': f'{care_home.name} Manager',
                    'role': 'Care Home Manager',
                    'involvement': 'Overseeing investigation and resolution',
                    'requires_update': False,
                },
            ]
            
            if resident:
                stakeholders.append({
                    'type': 'RESIDENT',
                    'name': f'{resident.first_name} {resident.last_name}',
                    'role': 'Resident',
                    'involvement': 'Subject of the complaint',
                    'requires_update': True,
                })
            
            for stakeholder_data in stakeholders:
                ComplaintStakeholder.objects.create(
                    complaint=complaint,
                    stakeholder_type=stakeholder_data['type'],
                    name=stakeholder_data['name'],
                    role_title=stakeholder_data['role'],
                    contact_details='01234 567890',
                    involvement_description=stakeholder_data['involvement'],
                    date_contacted=received_date + timedelta(days=1),
                    requires_update=stakeholder_data['requires_update'],
                    update_frequency='WEEKLY',
                    created_by=investigator,
                )
            
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f'✅ Created complaint: {data["reference"]} - {data["complainant"]}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully created {created_count} new complaints with investigation workflow data'))
        self.stdout.write(self.style.SUCCESS(f'📊 Total complaints in database: {Complaint.objects.count()}'))
