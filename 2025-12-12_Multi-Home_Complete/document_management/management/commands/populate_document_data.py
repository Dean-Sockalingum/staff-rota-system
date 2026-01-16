"""
Django management command to populate sample document management data.

Creates sample documents, versions, reviews, acknowledgements, and impact assessments.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from document_management.models import (
    DocumentCategory, Document, DocumentVersion, DocumentReview,
    StaffAcknowledgement, DocumentAttachment, PolicyImpactAssessment
)
from scheduling.models import CareHome, User


class Command(BaseCommand):
    help = 'Populate sample document management data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating document management data...')
        
        # Check for care homes
        care_homes = list(CareHome.objects.all())
        if not care_homes:
            self.stdout.write(self.style.ERROR('No care homes found. Please create care homes first.'))
            return
        
        # Check for users
        users = list(User.objects.filter(is_active=True))
        if not users:
            self.stdout.write(self.style.ERROR('No active users found. Please create users first.'))
            return
        
        # Create document categories
        self.stdout.write('Creating document categories...')
        categories = self.create_categories()
        
        # Create documents
        self.stdout.write('Creating documents...')
        documents = self.create_documents(categories, care_homes, users)
        
        # Create document versions
        self.stdout.write('Creating document versions...')
        self.create_versions(documents, users)
        
        # Create document reviews
        self.stdout.write('Creating document reviews...')
        self.create_reviews(documents, users)
        
        # Create staff acknowledgements
        self.stdout.write('Creating staff acknowledgements...')
        self.create_acknowledgements(documents, users)
        
        # Create impact assessments
        self.stdout.write('Creating impact assessments...')
        self.create_impact_assessments(documents, users)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created document management data!'))
        self.stdout.write(f'  - {len(categories)} categories')
        self.stdout.write(f'  - {len(documents)} documents')
    
    def create_categories(self):
        """Create hierarchical document categories."""
        categories = []
        
        # Root categories
        clinical = DocumentCategory.objects.create(
            name='Clinical Care',
            code='CLIN',
            description='Clinical policies and procedures'
        )
        categories.append(clinical)
        
        hr = DocumentCategory.objects.create(
            name='Human Resources',
            code='HR',
            description='HR policies and procedures'
        )
        categories.append(hr)
        
        health_safety = DocumentCategory.objects.create(
            name='Health & Safety',
            code='HS',
            description='Health and safety policies'
        )
        categories.append(health_safety)
        
        quality = DocumentCategory.objects.create(
            name='Quality Management',
            code='QM',
            description='Quality management system'
        )
        categories.append(quality)
        
        # Sub-categories
        medication = DocumentCategory.objects.create(
            name='Medication Management',
            code='MED',
            description='Medication policies',
            parent=clinical
        )
        categories.append(medication)
        
        infection = DocumentCategory.objects.create(
            name='Infection Control',
            code='IC',
            description='Infection prevention and control',
            parent=clinical
        )
        categories.append(infection)
        
        recruitment = DocumentCategory.objects.create(
            name='Recruitment',
            code='REC',
            description='Recruitment and selection',
            parent=hr
        )
        categories.append(recruitment)
        
        return categories
    
    def create_documents(self, categories, care_homes, users):
        """Create sample documents."""
        documents = []
        today = timezone.now().date()
        
        # Sample document data
        doc_data = [
            {
                'code': 'POL-CLIN-001',
                'title': 'Medication Administration Policy',
                'type': 'POLICY',
                'category': next((c for c in categories if c.code == 'MED'), categories[0]),
                'status': 'PUBLISHED',
                'version': '2.1.0',
                'review_freq': 'ANNUALLY',
                'frameworks': ['HIS', 'Care Inspectorate', 'Medication'],
                'description': 'Policy governing safe medication administration procedures.'
            },
            {
                'code': 'POL-CLIN-002',
                'title': 'Infection Prevention and Control Policy',
                'type': 'POLICY',
                'category': next((c for c in categories if c.code == 'IC'), categories[0]),
                'status': 'PUBLISHED',
                'version': '3.0.0',
                'review_freq': 'ANNUALLY',
                'frameworks': ['HIS', 'Care Inspectorate', 'Health & Safety'],
                'description': 'Comprehensive infection control measures and protocols.'
            },
            {
                'code': 'PROC-CLIN-001',
                'title': 'Wound Care Procedure',
                'type': 'PROCEDURE',
                'category': next((c for c in categories if c.code == 'CLIN'), categories[0]),
                'status': 'PUBLISHED',
                'version': '1.5.0',
                'review_freq': 'BIANNUALLY',
                'frameworks': ['HIS'],
                'description': 'Step-by-step wound assessment and treatment procedure.'
            },
            {
                'code': 'POL-HR-001',
                'title': 'Recruitment and Selection Policy',
                'type': 'POLICY',
                'category': next((c for c in categories if c.code == 'REC'), categories[1]),
                'status': 'PUBLISHED',
                'version': '1.2.0',
                'review_freq': 'ANNUALLY',
                'frameworks': ['SSSC', 'GDPR'],
                'description': 'Policy for fair and compliant recruitment processes.'
            },
            {
                'code': 'POL-HR-002',
                'title': 'Whistleblowing Policy',
                'type': 'POLICY',
                'category': next((c for c in categories if c.code == 'HR'), categories[1]),
                'status': 'PUBLISHED',
                'version': '1.0.0',
                'review_freq': 'BIANNUALLY',
                'frameworks': ['SSSC', 'Care Inspectorate'],
                'description': 'Policy to protect staff who raise concerns.'
            },
            {
                'code': 'POL-HS-001',
                'title': 'Fire Safety Policy',
                'type': 'POLICY',
                'category': next((c for c in categories if c.code == 'HS'), categories[2]),
                'status': 'PUBLISHED',
                'version': '2.0.0',
                'review_freq': 'ANNUALLY',
                'frameworks': ['Fire Safety', 'Health & Safety'],
                'description': 'Fire prevention, detection, and evacuation procedures.'
            },
            {
                'code': 'POL-HS-002',
                'title': 'Manual Handling Policy',
                'type': 'POLICY',
                'category': next((c for c in categories if c.code == 'HS'), categories[2]),
                'status': 'PUBLISHED',
                'version': '1.3.0',
                'review_freq': 'ANNUALLY',
                'frameworks': ['Health & Safety'],
                'description': 'Safe manual handling and moving procedures.'
            },
            {
                'code': 'POL-QM-001',
                'title': 'Complaint Handling Policy',
                'type': 'POLICY',
                'category': next((c for c in categories if c.code == 'QM'), categories[3]),
                'status': 'PUBLISHED',
                'version': '1.1.0',
                'review_freq': 'ANNUALLY',
                'frameworks': ['Care Inspectorate', 'HIS'],
                'description': 'Policy for managing and resolving complaints effectively.'
            },
            {
                'code': 'FORM-CLIN-001',
                'title': 'Medication Administration Record (MAR)',
                'type': 'FORM',
                'category': next((c for c in categories if c.code == 'MED'), categories[0]),
                'status': 'PUBLISHED',
                'version': '1.0.0',
                'review_freq': 'BIANNUALLY',
                'frameworks': ['Medication'],
                'description': 'Standard MAR chart for recording medication administration.'
            },
            {
                'code': 'POL-CLIN-003',
                'title': 'Safeguarding Adults Policy',
                'type': 'POLICY',
                'category': next((c for c in categories if c.code == 'CLIN'), categories[0]),
                'status': 'DRAFT',
                'version': '2.0.0',
                'review_freq': 'ANNUALLY',
                'frameworks': ['Care Inspectorate', 'SSSC'],
                'description': 'Policy to protect vulnerable adults from abuse.'
            },
        ]
        
        for data in doc_data:
            # Randomize review dates
            if data['status'] == 'DRAFT':
                next_review = today + timedelta(days=random.randint(30, 90))
            else:
                # Some overdue, some due soon, some current
                days_offset = random.choice([-45, -30, -15, 15, 30, 60, 120, 180, 300])
                next_review = today + timedelta(days=days_offset)
            
            doc = Document.objects.create(
                document_code=data['code'],
                title=data['title'],
                description=data['description'],
                document_type=data['type'],
                category=data['category'],
                status=data['status'],
                current_version_number=data['version'],
                last_version_date=today - timedelta(days=random.randint(1, 180)),
                review_frequency=data['review_freq'],
                next_review_date=next_review,
                compliance_frameworks=data['frameworks'],
                owner=random.choice(users),
                approved_by=random.choice(users) if data['status'] in ['APPROVED', 'PUBLISHED'] else None,
                care_home=random.choice([None, None, random.choice(care_homes)])  # 2/3 org-wide
            )
            documents.append(doc)
        
        return documents
    
    def create_versions(self, documents, users):
        """Create version history for documents."""
        today = timezone.now().date()
        
        # Create 2-4 versions for some documents
        versioned_docs = random.sample(documents, min(5, len(documents)))
        
        for doc in versioned_docs:
            # Parse version number
            parts = doc.current_version_number.split('.')
            major, minor = int(parts[0]), int(parts[1])
            
            # Create previous versions
            version_count = random.randint(2, 4)
            for i in range(version_count):
                if i == version_count - 1:
                    # Current version
                    version_num = doc.current_version_number
                    change_type = 'MAJOR' if minor == 0 else 'MINOR'
                else:
                    # Previous version
                    if i == 0:
                        version_num = f"{major - 1}.2.0"
                        change_type = 'REVIEW'
                    elif i == 1:
                        version_num = f"{major}.0.0"
                        change_type = 'MAJOR'
                    else:
                        version_num = f"{major}.{minor - 1}.0"
                        change_type = 'MINOR'
                
                DocumentVersion.objects.create(
                    document=doc,
                    version_number=version_num,
                    change_type=change_type,
                    summary_of_changes=self.get_version_summary(change_type),
                    detailed_changes=self.get_detailed_changes(change_type),
                    created_by=random.choice(users),
                    created_at=timezone.now() - timedelta(days=random.randint(30 * i, 30 * (i + 1)))
                )
    
    def get_version_summary(self, change_type):
        """Get sample version change summary."""
        summaries = {
            'MAJOR': [
                'Complete policy restructure to align with new Care Inspectorate standards',
                'Major update incorporating new regulatory requirements',
                'Significant revisions following audit findings'
            ],
            'MINOR': [
                'Updated contact details and references',
                'Clarified procedures based on staff feedback',
                'Minor wording improvements for clarity'
            ],
            'CORRECTION': [
                'Fixed typographical errors',
                'Corrected reference numbers',
                'Updated hyperlinks'
            ],
            'REVIEW': [
                'Scheduled review completed - no changes required',
                'Annual review completed - policy remains current',
                'Reviewed and reaffirmed without changes'
            ]
        }
        return random.choice(summaries.get(change_type, ['Version update']))
    
    def get_detailed_changes(self, change_type):
        """Get detailed change description."""
        if change_type == 'MAJOR':
            return 'Extensive revisions to sections 3, 4, and 5. Added new appendices A and B. Updated all compliance framework references.'
        elif change_type == 'MINOR':
            return 'Updated section 2.3 for clarity. Revised contact information in appendix C.'
        elif change_type == 'CORRECTION':
            return 'Corrected spelling errors on pages 4, 7, and 12. Fixed broken hyperlinks.'
        else:
            return 'Policy reviewed against current practice and regulations. No substantive changes required.'
    
    def create_reviews(self, documents, users):
        """Create document reviews."""
        today = timezone.now().date()
        
        for doc in documents:
            # Create 1-3 reviews per document
            review_count = random.randint(1, 3)
            
            for i in range(review_count):
                # Determine review status
                scheduled_date = today - timedelta(days=random.randint(365 - (i * 180), 365 - (i * 180) + 30))
                
                if i == 0:  # Most recent review
                    if doc.is_overdue_for_review():
                        status = 'PENDING'
                        completed_date = None
                        outcome = None
                    else:
                        status = 'COMPLETED'
                        completed_date = scheduled_date + timedelta(days=random.randint(1, 10))
                        outcome = random.choice(['NO_CHANGES', 'MINOR_UPDATES', 'NO_CHANGES'])
                else:
                    status = 'COMPLETED'
                    completed_date = scheduled_date + timedelta(days=random.randint(1, 14))
                    outcome = random.choice(['NO_CHANGES', 'MINOR_UPDATES', 'MAJOR_REVISION'])
                
                DocumentReview.objects.create(
                    document=doc,
                    review_type=random.choice(['SCHEDULED', 'SCHEDULED', 'AD_HOC']),
                    status=status,
                    reviewer=random.choice(users),
                    scheduled_date=scheduled_date,
                    completed_date=completed_date,
                    outcome=outcome,
                    notes=self.get_review_notes(outcome) if outcome else ''
                )
    
    def get_review_notes(self, outcome):
        """Get sample review notes."""
        notes = {
            'NO_CHANGES': 'Policy reviewed and remains current. No changes required.',
            'MINOR_UPDATES': 'Minor wording clarifications made. Updated references to current standards.',
            'MAJOR_REVISION': 'Significant updates required to align with new regulatory guidance.',
            'ARCHIVED': 'Policy superseded by new combined policy document.'
        }
        return notes.get(outcome, '')
    
    def create_acknowledgements(self, documents, users):
        """Create staff acknowledgements."""
        today = timezone.now().date()
        
        # Only published documents require acknowledgement
        published_docs = [d for d in documents if d.status == 'PUBLISHED']
        
        for doc in published_docs:
            # Each published doc needs acknowledgement from 60-90% of staff
            acknowledgement_rate = random.randint(60, 90) / 100
            staff_count = int(len(users) * acknowledgement_rate)
            selected_staff = random.sample(users, min(staff_count, len(users)))
            
            for staff in selected_staff:
                # 80% have acknowledged, 20% pending/overdue
                has_acknowledged = random.random() < 0.8
                requires_quiz = random.choice([True, False])
                
                deadline = today + timedelta(days=random.randint(-30, 30))
                
                ack = StaffAcknowledgement.objects.create(
                    document=doc,
                    staff_member=staff,
                    acknowledgement_deadline=deadline,
                    requires_quiz=requires_quiz
                )
                
                if has_acknowledged:
                    ack.acknowledged_at = today - timedelta(days=random.randint(1, 30))
                    
                    if requires_quiz:
                        ack.quiz_score = random.randint(75, 100)
                        ack.quiz_passed = ack.quiz_score >= 80
                    
                    ack.save()
    
    def create_impact_assessments(self, documents, users):
        """Create policy impact assessments."""
        today = timezone.now().date()
        
        # Only POLICY documents need impact assessments
        policies = [d for d in documents if d.document_type == 'POLICY' and d.status == 'PUBLISHED']
        
        for policy in random.sample(policies, min(5, len(policies))):
            # Create 1-2 impact assessments per policy
            assessment_count = random.randint(1, 2)
            
            for _ in range(assessment_count):
                assessment_type = random.choice(['EQUALITY', 'QUALITY', 'PRIVACY'])
                impact_level = random.choice(['NONE', 'LOW', 'LOW', 'MEDIUM', 'HIGH'])
                
                PolicyImpactAssessment.objects.create(
                    document=policy,
                    assessment_type=assessment_type,
                    impact_level=impact_level,
                    assessed_by=random.choice(users),
                    assessment_date=today - timedelta(days=random.randint(1, 180)),
                    review_date=today + timedelta(days=random.randint(180, 365)),
                    findings=self.get_assessment_findings(assessment_type, impact_level),
                    recommendations=self.get_recommendations(impact_level),
                    actions_required=self.get_actions(impact_level) if impact_level in ['MEDIUM', 'HIGH'] else '',
                    status='COMPLETED'
                )
    
    def get_assessment_findings(self, assessment_type, impact_level):
        """Get sample assessment findings."""
        if assessment_type == 'EQUALITY':
            if impact_level in ['NONE', 'LOW']:
                return 'No adverse impact identified on protected characteristics. Policy promotes equality.'
            else:
                return 'Some potential impact on accessibility for staff with disabilities. Requires reasonable adjustments.'
        elif assessment_type == 'QUALITY':
            if impact_level in ['NONE', 'LOW']:
                return 'Policy supports high-quality care delivery. Aligned with HIS standards.'
            else:
                return 'Significant positive impact on care quality. Requires robust implementation and monitoring.'
        else:  # PRIVACY
            if impact_level in ['NONE', 'LOW']:
                return 'Minimal personal data processing. GDPR compliant.'
            else:
                return 'Involves processing of sensitive personal data. Enhanced safeguards required.'
    
    def get_recommendations(self, impact_level):
        """Get sample recommendations."""
        if impact_level in ['NONE', 'LOW']:
            return 'Continue monitoring during routine policy reviews.'
        elif impact_level == 'MEDIUM':
            return 'Implement additional safeguards. Review quarterly for first year.'
        else:
            return 'Develop detailed action plan. Seek external advice. Monitor monthly.'
    
    def get_actions(self, impact_level):
        """Get required actions."""
        if impact_level == 'MEDIUM':
            return '1. Update training materials\n2. Consult with affected stakeholders\n3. Review after 6 months'
        else:
            return '1. Engage equality specialist\n2. Develop mitigation plan\n3. Monthly monitoring\n4. External audit'
