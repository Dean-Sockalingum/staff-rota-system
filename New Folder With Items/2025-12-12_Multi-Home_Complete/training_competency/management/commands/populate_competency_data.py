"""
Management command to populate training_competency module with realistic sample data

Usage: python manage.py populate_competency_data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from training_competency.models import (
    CompetencyFramework,
    RoleCompetencyRequirement,
    CompetencyAssessment,
    TrainingMatrix,
    LearningPathway,
    PathwayCompetency,
    PathwayTraining,
    StaffLearningPlan
)
from scheduling.models import User, Role, TrainingCourse, CareHome


class Command(BaseCommand):
    help = 'Populate training_competency module with sample data for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data population...'))
        
        # Clear existing data
        self.stdout.write('Clearing existing competency data...')
        StaffLearningPlan.objects.all().delete()
        PathwayTraining.objects.all().delete()
        PathwayCompetency.objects.all().delete()
        LearningPathway.objects.all().delete()
        TrainingMatrix.objects.all().delete()
        CompetencyAssessment.objects.all().delete()
        RoleCompetencyRequirement.objects.all().delete()
        CompetencyFramework.objects.all().delete()
        
        # Get or create sample data
        users = list(User.objects.filter(is_active=True)[:10])
        if not users:
            self.stdout.write(self.style.ERROR('Need at least one user in database'))
            return
        
        # Get existing roles from the system
        # Prefer actual roles: SM, OM, SSCW, SCW, SCA
        # Fall back to any existing roles if those don't exist
        preferred_roles = ['SM', 'OM', 'SSCW', 'SCW', 'SCA']
        roles = list(Role.objects.filter(name__in=preferred_roles).order_by('name'))
        
        if not roles:
            self.stdout.write(self.style.WARNING('Preferred roles (SM, OM, SSCW, SCW, SCA) not found. Using existing roles...'))
            roles = list(Role.objects.all()[:5])
        
        if not roles:
            self.stdout.write(self.style.ERROR('No roles found in database. Please create roles first.'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Found {len(roles)} roles: {", ".join([r.name for r in roles])}'))
        
        training_courses = list(TrainingCourse.objects.all()[:15])
        care_homes = list(CareHome.objects.all()[:3])
        
        # Create Competency Frameworks
        self.stdout.write('Creating competency frameworks...')
        competencies = []
        
        # Clinical Competencies
        clinical_comps = [
            {
                'code': 'CLIN-001',
                'title': 'Medication Administration',
                'description': 'Safe administration of medications following the 5 rights principle',
                'assessment_criteria': 'Demonstrates correct technique, verifies patient identity, documents accurately',
                'evidence_required': 'Direct observation, medication records, competency assessment',
                'review_frequency_months': 12
            },
            {
                'code': 'CLIN-002',
                'title': 'Wound Care Management',
                'description': 'Assessment and treatment of wounds using evidence-based practices',
                'assessment_criteria': 'Accurate assessment, appropriate dressing selection, infection control',
                'evidence_required': 'Care plans, wound photographs, supervisor observation',
                'review_frequency_months': 12
            },
            {
                'code': 'CLIN-003',
                'title': 'Vital Signs Monitoring',
                'description': 'Accurate measurement and interpretation of vital signs',
                'assessment_criteria': 'Correct technique, accurate recording, recognizes abnormalities',
                'evidence_required': 'Competency assessment, clinical records',
                'review_frequency_months': 24
            },
            {
                'code': 'CLIN-004',
                'title': 'Infection Prevention & Control',
                'description': 'Application of infection control principles in clinical practice',
                'assessment_criteria': 'Hand hygiene compliance, PPE use, environmental cleaning',
                'evidence_required': 'Observation, audit results, certificates',
                'review_frequency_months': 12
            },
        ]
        
        for comp_data in clinical_comps:
            comp = CompetencyFramework.objects.create(
                competency_type='CLINICAL',
                **comp_data
            )
            if training_courses:
                comp.linked_training_courses.add(*random.sample(training_courses, min(2, len(training_courses))))
            competencies.append(comp)
        
        # Technical Competencies
        technical_comps = [
            {
                'code': 'TECH-001',
                'title': 'Electronic Care Records',
                'description': 'Proficient use of electronic care record systems',
                'assessment_criteria': 'Accurate data entry, report generation, system navigation',
                'evidence_required': 'System logs, supervisor observation, test scenarios',
                'review_frequency_months': 24
            },
            {
                'code': 'TECH-002',
                'title': 'Medical Equipment Operation',
                'description': 'Safe operation of medical equipment and devices',
                'assessment_criteria': 'Correct setup, operation, maintenance, troubleshooting',
                'evidence_required': 'Practical assessment, maintenance logs',
                'review_frequency_months': 12
            },
            {
                'code': 'TECH-003',
                'title': 'Data Protection & Confidentiality',
                'description': 'Understanding and application of data protection principles',
                'assessment_criteria': 'GDPR compliance, secure information handling, breach prevention',
                'evidence_required': 'E-learning certificate, scenario testing',
                'review_frequency_months': 12
            },
        ]
        
        for comp_data in technical_comps:
            comp = CompetencyFramework.objects.create(
                competency_type='TECHNICAL',
                **comp_data
            )
            if training_courses:
                comp.linked_training_courses.add(*random.sample(training_courses, min(2, len(training_courses))))
            competencies.append(comp)
        
        # Behavioral Competencies
        behavioral_comps = [
            {
                'code': 'BEH-001',
                'title': 'Person-Centered Care',
                'description': 'Delivers care focused on individual preferences and needs',
                'assessment_criteria': 'Demonstrates respect, involves residents in decisions, tailors care',
                'evidence_required': '360 feedback, care plan reviews, observations',
                'review_frequency_months': 24
            },
            {
                'code': 'BEH-002',
                'title': 'Effective Communication',
                'description': 'Clear and professional communication with residents, families, and colleagues',
                'assessment_criteria': 'Active listening, clarity, empathy, appropriate tone',
                'evidence_required': 'Peer feedback, resident satisfaction surveys',
                'review_frequency_months': 24
            },
            {
                'code': 'BEH-003',
                'title': 'Teamwork & Collaboration',
                'description': 'Works effectively as part of a multidisciplinary team',
                'assessment_criteria': 'Supports colleagues, shares information, resolves conflicts',
                'evidence_required': 'Team feedback, supervisor observation',
                'review_frequency_months': 24
            },
        ]
        
        for comp_data in behavioral_comps:
            comp = CompetencyFramework.objects.create(
                competency_type='BEHAVIORAL',
                **comp_data
            )
            competencies.append(comp)
        
        # Leadership Competencies
        leadership_comps = [
            {
                'code': 'LEAD-001',
                'title': 'Team Leadership',
                'description': 'Leads and motivates a team to achieve objectives',
                'assessment_criteria': 'Delegation, performance management, team development',
                'evidence_required': 'Team performance metrics, 360 feedback, supervision records',
                'review_frequency_months': 24
            },
            {
                'code': 'LEAD-002',
                'title': 'Quality Improvement',
                'description': 'Identifies and implements quality improvement initiatives',
                'assessment_criteria': 'Uses PDSA cycles, data analysis, stakeholder engagement',
                'evidence_required': 'QI project documentation, outcomes data',
                'review_frequency_months': 24
            },
        ]
        
        for comp_data in leadership_comps:
            comp = CompetencyFramework.objects.create(
                competency_type='LEADERSHIP',
                **comp_data
            )
            if training_courses:
                comp.linked_training_courses.add(*random.sample(training_courses, min(1, len(training_courses))))
            competencies.append(comp)
        
        # Digital Competencies
        digital_comps = [
            {
                'code': 'DIG-001',
                'title': 'Digital Literacy',
                'description': 'Basic competence with digital tools and technology',
                'assessment_criteria': 'Email, document creation, internet navigation, online safety',
                'evidence_required': 'E-learning completion, practical assessment',
                'review_frequency_months': 36
            },
        ]
        
        for comp_data in digital_comps:
            comp = CompetencyFramework.objects.create(
                competency_type='DIGITAL',
                **comp_data
            )
            competencies.append(comp)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(competencies)} competency frameworks'))
        
        # Create Role-Competency Requirements
        self.stdout.write('Creating role-competency requirements...')
        requirements = []
        for role in roles:
            # Each role requires different competencies
            role_comps = random.sample(competencies, min(8, len(competencies)))
            for comp in role_comps:
                is_mandatory = random.choice([True, True, False])  # 66% mandatory
                required_level = random.choice(['WORKING', 'PROFICIENT', 'EXPERT'])
                req = RoleCompetencyRequirement.objects.create(
                    role=role,
                    competency=comp,
                    required_level=required_level,
                    is_mandatory=is_mandatory
                )
                requirements.append(req)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(requirements)} role-competency requirements'))
        
        # Create Competency Assessments
        self.stdout.write('Creating competency assessments...')
        assessments = []
        assessors = users[:3]  # First 3 users are assessors
        
        for user in users[3:]:  # Remaining users get assessed
            if not user.role:
                continue
            
            # Get competencies for this user's role
            role_requirements = RoleCompetencyRequirement.objects.filter(role=user.role)
            
            for req in role_requirements[:random.randint(5, 10)]:
                # Create assessment
                assessment_date = timezone.now().date() - timedelta(days=random.randint(0, 365))
                achieved_level = random.choice(['AWARENESS', 'WORKING', 'PROFICIENT', 'EXPERT'])
                outcome = random.choice(['COMPETENT', 'COMPETENT', 'HIGHLY_COMPETENT', 'IN_PROGRESS', 'NOT_YET_COMPETENT'])
                
                assessment = CompetencyAssessment.objects.create(
                    staff_member=user,
                    competency=req.competency,
                    assessor=random.choice(assessors),
                    assessment_date=assessment_date,
                    achieved_level=achieved_level,
                    outcome=outcome,
                    assessment_method=random.choice(['DIRECT_OBSERVATION', 'SIMULATION', 'PORTFOLIO', 'WRITTEN_TEST']),
                    evidence_submitted=f'Assessment evidence for {req.competency.code}',
                    next_review_date=assessment_date + timedelta(days=req.competency.review_frequency_months * 30) if outcome == 'COMPETENT' else None
                )
                assessments.append(assessment)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(assessments)} competency assessments'))
        
        # Create Training Matrix
        if training_courses and care_homes:
            self.stdout.write('Creating training matrix entries...')
            matrix_entries = []
            for role in roles:
                for course in random.sample(training_courses, min(5, len(training_courses))):
                    requirement_type = random.choice(['MANDATORY', 'ESSENTIAL', 'RECOMMENDED', 'OPTIONAL'])
                    entry = TrainingMatrix.objects.create(
                        role=role,
                        training_course=course,
                        care_home=random.choice(care_homes) if random.random() > 0.5 else None,
                        requirement_type=requirement_type,
                        priority_order=random.randint(1, 10)
                    )
                    matrix_entries.append(entry)
            
            self.stdout.write(self.style.SUCCESS(f'Created {len(matrix_entries)} training matrix entries'))
        
        # Create Learning Pathways
        self.stdout.write('Creating learning pathways...')
        pathways = []
        
        # Full career progression: SCA (New Staff) → SCW → SSCW → OM → SM
        pathway_data = [
            {
                'title': 'SCA to SCW Progression',
                'description': 'First step in career progression from Social Care Assistant to Social Care Worker. Requires demonstrated competency in all foundational care skills, effective communication, and person-centered care approaches. Minimum 12 months experience required.',
                'from_role': next((r for r in roles if r.name == 'SCA'), roles[0] if roles else None),
                'to_role': next((r for r in roles if r.name == 'SCW'), roles[1] if len(roles) > 1 else None),
                'estimated_duration_months': 12,
                'total_learning_hours': 120,
            },
            {
                'title': 'SCW to SSCW Progression',
                'description': 'Second step in career progression from Social Care Worker to Senior Social Care Worker. Requires mastery of advanced clinical skills, leadership capabilities, and quality improvement expertise. Minimum 18 months experience as SCW required.',
                'from_role': next((r for r in roles if r.name == 'SCW'), roles[1] if len(roles) > 1 else None),
                'to_role': next((r for r in roles if r.name == 'SSCW'), roles[2] if len(roles) > 2 else None),
                'estimated_duration_months': 18,
                'total_learning_hours': 180,
            },
            {
                'title': 'SSCW to OM Progression',
                'description': 'Third step in career progression from Senior Social Care Worker to Operational Manager. Requires demonstrated leadership, team management, quality improvement, and operational management competencies. Minimum 24 months experience as SSCW required.',
                'from_role': next((r for r in roles if r.name == 'SSCW'), roles[2] if len(roles) > 2 else None),
                'to_role': next((r for r in roles if r.name == 'OM'), roles[3] if len(roles) > 3 else None),
                'estimated_duration_months': 24,
                'total_learning_hours': 240,
            },
            {
                'title': 'OM to SM Progression',
                'description': 'Final step in career progression from Operational Manager to Service Manager. Requires strategic leadership, service-wide quality improvement, and comprehensive service management competencies. Minimum 24 months experience as OM required.',
                'from_role': next((r for r in roles if r.name == 'OM'), roles[3] if len(roles) > 3 else None),
                'to_role': next((r for r in roles if r.name == 'SM'), roles[4] if len(roles) > 4 else None),
                'estimated_duration_months': 24,
                'total_learning_hours': 240,
            },
            {
                'title': 'New SCA Induction Pathway',
                'description': 'Comprehensive induction pathway for new Social Care Assistants (entry level staff) covering all essential competencies required for safe and effective care delivery. SSSC registration required.',
                'from_role': next((r for r in roles if r.name == 'SCA'), roles[0] if roles else None),
                'to_role': next((r for r in roles if r.name == 'SCA'), roles[0] if roles else None),
                'estimated_duration_months': 6,
                'total_learning_hours': 60,
            },
        ]
        
        for pathway_info in pathway_data:
            if pathway_info['from_role'] and pathway_info['to_role']:
                pathway = LearningPathway.objects.create(
                    owner=users[0],
                    status='ACTIVE',
                    **pathway_info
                )
                pathways.append(pathway)
                
                # Add competencies to pathway
                pathway_comps = random.sample(competencies, min(6, len(competencies)))
                for i, comp in enumerate(pathway_comps):
                    PathwayCompetency.objects.create(
                        pathway=pathway,
                        competency=comp,
                        sequence_order=i + 1,
                        required_level=random.choice(['WORKING', 'PROFICIENT'])
                    )
                
                # Add training to pathway
                if training_courses:
                    pathway_training = random.sample(training_courses, min(4, len(training_courses)))
                    for i, course in enumerate(pathway_training):
                        PathwayTraining.objects.create(
                            pathway=pathway,
                            training_course=course,
                            sequence_order=i + 1,
                            is_mandatory=i < 2  # First 2 are mandatory
                        )
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(pathways)} learning pathways'))
        
        # Create Staff Learning Plans
        self.stdout.write('Creating staff learning plans...')
        learning_plans = []
        
        for user in users[3:7]:  # Some users enrolled in pathways
            if not user.role or not pathways:
                continue
            
            # Find pathway from user's current role
            user_pathways = [p for p in pathways if p.from_role == user.role]
            if user_pathways:
                pathway = random.choice(user_pathways)
                enrollment_date = timezone.now().date() - timedelta(days=random.randint(30, 180))
                status = random.choice(['PLANNED', 'IN_PROGRESS', 'IN_PROGRESS', 'COMPLETED'])
                
                if status == 'COMPLETED':
                    percent_complete = 100
                    actual_completion = enrollment_date + timedelta(days=pathway.estimated_duration_months * 30)
                elif status == 'IN_PROGRESS':
                    percent_complete = random.randint(25, 85)
                    actual_completion = None
                else:
                    percent_complete = 0
                    actual_completion = None
                
                plan = StaffLearningPlan.objects.create(
                    staff_member=user,
                    pathway=pathway,
                    enrollment_date=enrollment_date,
                    status=status,
                    percent_complete=percent_complete,
                    target_completion_date=enrollment_date + timedelta(days=pathway.estimated_duration_months * 30),
                    actual_completion_date=actual_completion,
                    mentor=random.choice(users[:3]),
                    line_manager=random.choice(users[:3])
                )
                learning_plans.append(plan)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(learning_plans)} staff learning plans'))
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n=== Data Population Complete ==='))
        self.stdout.write(self.style.SUCCESS(f'Competency Frameworks: {len(competencies)}'))
        self.stdout.write(self.style.SUCCESS(f'Role Requirements: {len(requirements)}'))
        self.stdout.write(self.style.SUCCESS(f'Assessments: {len(assessments)}'))
        self.stdout.write(self.style.SUCCESS(f'Learning Pathways: {len(pathways)}'))
        self.stdout.write(self.style.SUCCESS(f'Learning Plans: {len(learning_plans)}'))
        self.stdout.write(self.style.SUCCESS('\nYou can now access the Training & Competency UI at /training-competency/'))
