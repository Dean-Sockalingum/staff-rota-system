"""
Management command to populate sample data for Module 3: Experience & Feedback.
Creates realistic satisfaction surveys, complaints, EBCD touchpoints, QoL assessments, and feedback themes.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from decimal import Decimal

from experience_feedback.models import (
    SatisfactionSurvey, Complaint, EBCDTouchpoint, 
    QualityOfLifeAssessment, FeedbackTheme
)
from scheduling.models import CareHome, User, Resident


class Command(BaseCommand):
    help = 'Populate sample data for Experience & Feedback module'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Experience & Feedback data population...'))
        
        # Get required objects
        care_homes = list(CareHome.objects.all())
        if not care_homes:
            self.stdout.write(self.style.ERROR('No care homes found. Please create care homes first.'))
            return
        
        users = list(User.objects.filter(is_active=True))
        if not users:
            self.stdout.write(self.style.ERROR('No active users found.'))
            return
        
        residents = list(Resident.objects.filter(status='ACTIVE'))
        if not residents:
            self.stdout.write(self.style.ERROR('No active residents found.'))
            return
        
        # Create satisfaction surveys
        self.create_satisfaction_surveys(care_homes, residents, users)
        
        # Create complaints
        self.create_complaints(care_homes, residents, users)
        
        # Create EBCD touchpoints
        self.create_ebcd_touchpoints(care_homes, users)
        
        # Create QoL assessments
        self.create_qol_assessments(residents, users)
        
        # Create feedback themes
        self.create_feedback_themes(care_homes, users)
        
        self.stdout.write(self.style.SUCCESS('✓ Experience & Feedback data population complete!'))

    def create_satisfaction_surveys(self, care_homes, residents, users):
        """Create 25-30 satisfaction surveys."""
        self.stdout.write('Creating satisfaction surveys...')
        
        survey_types = ['RESIDENT_ADMISSION', 'RESIDENT_ONGOING', 'FAMILY_ONGOING']
        
        respondent_names = [
            'Margaret Smith', 'John Anderson', 'Sarah Wilson', 'David Brown',
            'Emma Thompson', 'James Miller', 'Helen Davis', 'Robert Taylor',
            'Mary Johnson', 'William Clark', 'Elizabeth White', 'Thomas Harris'
        ]
        
        relationships = [
            'Daughter', 'Son', 'Spouse', 'Niece', 'Nephew',
            'Grandchild', 'Friend', 'Self (Resident)'
        ]
        
        positive_comments = [
            "The staff are wonderful and very caring. My mother is so happy here.",
            "Excellent care provided. The team goes above and beyond.",
            "Very satisfied with the quality of care and attention to detail.",
            "The home is clean, welcoming, and staff are professional.",
            "I feel reassured knowing my father is in such good hands."
        ]
        
        improvement_comments = [
            "Would like to see more varied activities offered.",
            "Communication could be improved - sometimes hard to reach staff.",
            "The food is good but could have more variety.",
            "More frequent updates on care would be appreciated.",
        ]
        
        count = 0
        for i in range(30):
            survey_type = random.choice(survey_types)
            care_home = random.choice(care_homes)
            resident = random.choice([r for r in residents if r.care_home == care_home]) if residents else None
            created_by = random.choice(users)
            
            is_anonymous = random.random() < 0.15  # 15% anonymous
            
            # Generate scores (weighted towards positive)
            quality_of_care = random.choice([3, 4, 4, 4, 5, 5, 5])
            staff_attitude = random.choice([3, 4, 4, 4, 5, 5, 5])
            communication = random.choice([3, 3, 4, 4, 4, 5, 5])
            environment = random.choice([4, 4, 4, 5, 5, 5])
            meals = random.choice([3, 3, 4, 4, 4, 5])
            activities = random.choice([2, 3, 3, 4, 4, 5])
            dignity = random.choice([4, 4, 5, 5, 5, 5])
            safety = random.choice([4, 4, 4, 5, 5, 5])
            
            # NPS based on overall satisfaction
            avg_score = (quality_of_care + staff_attitude + communication + environment + 
                        meals + activities + dignity + safety) / 8
            
            if avg_score >= 4.5:
                likelihood = random.choice([9, 10, 10])
            elif avg_score >= 4:
                likelihood = random.choice([7, 8, 9])
            elif avg_score >= 3:
                likelihood = random.choice([5, 6, 7])
            else:
                likelihood = random.choice([3, 4, 5])
            
            SatisfactionSurvey.objects.create(
                care_home=care_home,
                resident=resident,
                survey_type=survey_type,
                survey_date=timezone.now().date() - timedelta(days=random.randint(1, 90)),
                respondent_name=None if is_anonymous else random.choice(respondent_names),
                relationship_to_resident=None if is_anonymous else random.choice(relationships),
                is_anonymous=is_anonymous,
                quality_of_care=quality_of_care,
                staff_attitude=staff_attitude,
                communication=communication,
                environment_cleanliness=environment,
                meals_nutrition=meals,
                activities_engagement=activities,
                dignity_respect=dignity,
                safety_security=safety,
                likelihood_recommend=likelihood,
                what_works_well=random.choice(positive_comments) if random.random() < 0.6 else '',
                areas_for_improvement=random.choice(improvement_comments) if random.random() < 0.4 else '',
                additional_comments='Overall very pleased with the care provided.' if random.random() < 0.3 else '',
                created_by=created_by,
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} satisfaction surveys'))

    def create_complaints(self, care_homes, residents, users):
        """Create 12-15 complaints at various stages."""
        self.stdout.write('Creating complaints...')
        
        complaint_categories = [
            'CARE_QUALITY', 'STAFF_CONDUCT', 'COMMUNICATION', 'ENVIRONMENT',
            'MEALS_NUTRITION', 'SAFETY_SECURITY', 'DIGNITY_RESPECT', 'OTHER'
        ]
        
        complainant_names = [
            'Patricia Johnson', 'Michael Brown', 'Linda Wilson', 'Christopher Davis',
            'Barbara Miller', 'Daniel Anderson', 'Susan Taylor', 'Joseph White'
        ]
        
        relationships = ['Daughter', 'Son', 'Spouse', 'Niece', 'Nephew', 'Grandchild', 'Power of Attorney']
        
        complaint_descriptions = {
            'CARE_QUALITY': "Concerned about the timing of medication administration. Would like more consistency.",
            'STAFF_CONDUCT': "Staff member was abrupt when speaking to my mother. Expects better communication.",
            'COMMUNICATION': "Have not received updates on care plan review. Difficult to get through by phone.",
            'ENVIRONMENT': "Room temperature has been too cold. Heating needs adjustment.",
            'MEALS_NUTRITION': "Mother reports meals are sometimes cold. Food preferences not always accommodated.",
            'SAFETY_SECURITY': "Noticed safety rail was loose in bathroom. Requires immediate attention.",
            'DIGNITY_RESPECT': "Personal items were moved without permission. Would appreciate more respect for privacy.",
        }
        
        statuses = ['RECEIVED', 'ACKNOWLEDGED', 'INVESTIGATING', 'ACTION_PLAN', 'RESOLVED']
        severities = ['LOW', 'MEDIUM', 'HIGH']
        
        count = 0
        for i in range(15):
            category = random.choice(complaint_categories)
            care_home = random.choice(care_homes)
            resident = random.choice([r for r in residents if r.care_home == care_home]) if residents else None
            investigating_officer = random.choice(users)
            created_by = random.choice(users)
            
            severity = random.choice(severities)
            status = random.choice(statuses)
            
            days_ago = random.randint(1, 60)
            date_received = timezone.now().date() - timedelta(days=days_ago)
            
            # Acknowledgement (should be within 3 days)
            if status != 'RECEIVED':
                ack_days = random.randint(1, 5)  # Some late acknowledgements
                date_acknowledged = date_received + timedelta(days=ack_days)
            else:
                date_acknowledged = None
            
            # Resolution (if resolved)
            if status == 'RESOLVED':
                resolution_days = random.randint(10, 25)
                date_resolved = date_received + timedelta(days=resolution_days)
                resolution_details = "Issue addressed through staff training and process improvement. Complainant satisfied with outcome."
                complainant_satisfied = True
            else:
                date_resolved = None
                resolution_details = ''
                complainant_satisfied = None
            
            # Investigation notes for in-progress complaints
            if status in ['INVESTIGATING', 'ACTION_PLAN', 'RESOLVED']:
                investigation_notes = "Investigation conducted. Spoke with staff involved and reviewed care records."
                root_cause = "Process gap identified in communication protocol." if random.random() < 0.5 else None
            else:
                investigation_notes = ''
                root_cause = None
            
            Complaint.objects.create(
                care_home=care_home,
                resident=resident,
                complaint_reference=f'COMP-{care_home.id:02d}-{2025}-{(i+1):04d}',
                date_received=date_received,
                complainant_name=random.choice(complainant_names),
                complainant_relationship=random.choice(relationships),
                complaint_category=category,
                complaint_description=complaint_descriptions.get(category, 'General concern raised.'),
                desired_outcome='Would like issue addressed and prevented in future.',
                severity=severity,
                status=status,
                date_acknowledged=date_acknowledged,
                investigating_officer=investigating_officer,
                investigation_notes=investigation_notes,
                root_cause=root_cause,
                date_resolved=date_resolved,
                resolution_details=resolution_details,
                complainant_satisfied=complainant_satisfied,
                created_by=created_by,
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} complaints'))

    def create_ebcd_touchpoints(self, care_homes, users):
        """Create 10-12 EBCD touchpoints."""
        self.stdout.write('Creating EBCD touchpoints...')
        
        touchpoints = [
            {'name': 'First Contact & Inquiry', 'category': 'ADMISSION', 'importance': 5, 'impact': 'VERY_POSITIVE', 'current': 4, 'target': 5},
            {'name': 'Pre-Admission Visit', 'category': 'ADMISSION', 'importance': 5, 'impact': 'POSITIVE', 'current': 4, 'target': 5},
            {'name': 'Move-In Day', 'category': 'ADMISSION', 'importance': 5, 'impact': 'POSITIVE', 'current': 3, 'target': 4},
            {'name': 'First Week Settling In', 'category': 'SETTLING_IN', 'importance': 5, 'impact': 'NEUTRAL', 'current': 3, 'target': 4},
            {'name': 'Meeting Key Staff', 'category': 'SETTLING_IN', 'importance': 4, 'impact': 'POSITIVE', 'current': 4, 'target': 5},
            {'name': 'Daily Care Routines', 'category': 'DAILY_CARE', 'importance': 5, 'impact': 'POSITIVE', 'current': 4, 'target': 5},
            {'name': 'Meal Times', 'category': 'MEALS_SOCIAL', 'importance': 4, 'impact': 'NEUTRAL', 'current': 3, 'target': 4},
            {'name': 'Activities & Engagement', 'category': 'ACTIVITIES', 'importance': 4, 'impact': 'NEUTRAL', 'current': 3, 'target': 4},
            {'name': 'Family Visits', 'category': 'FAMILY_INTERACTION', 'importance': 5, 'impact': 'VERY_POSITIVE', 'current': 5, 'target': 5},
            {'name': 'Healthcare Appointments', 'category': 'HEALTHCARE', 'importance': 5, 'impact': 'NEUTRAL', 'current': 4, 'target': 5},
            {'name': 'Care Plan Reviews', 'category': 'REVIEWS_ASSESSMENTS', 'importance': 5, 'impact': 'POSITIVE', 'current': 4, 'target': 5},
        ]
        
        count = 0
        for tp_data in touchpoints:
            care_home = random.choice(care_homes)
            created_by = random.choice(users)
            
            EBCDTouchpoint.objects.create(
                care_home=care_home,
                touchpoint_name=tp_data['name'],
                category=tp_data['category'],
                importance_rating=tp_data['importance'],
                emotional_impact=tp_data['impact'],
                current_experience_rating=tp_data['current'],
                target_experience_rating=tp_data['target'],
                feedback_summary=f"Residents and families value {tp_data['name'].lower()} highly.",
                improvement_actions='Co-design workshop planned to develop improvements.' if tp_data['current'] < tp_data['target'] else '',
                created_by=created_by,
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} EBCD touchpoints'))

    def create_qol_assessments(self, residents, users):
        """Create 15-20 QoL assessments."""
        self.stdout.write('Creating Quality of Life assessments...')
        
        tools = ['QUALID', 'DEMQOL', 'EQ5D', 'WHOQOL_BREF']
        methods = ['DIRECT_INTERVIEW', 'PROXY_FAMILY', 'PROXY_STAFF', 'OBSERVATION']
        
        count = 0
        for i in range(20):
            resident = random.choice(residents)
            assessed_by = random.choice(users)
            tool = random.choice(tools)
            method = random.choice(methods)
            
            # Generate realistic QoL scores (weighted positive)
            physical_health = random.choice([2.5, 3.0, 3.5, 4.0, 4.0, 4.5])
            psychological = random.choice([3.0, 3.5, 4.0, 4.0, 4.5, 4.5])
            social_relationships = random.choice([3.0, 3.5, 3.5, 4.0, 4.5])
            environment = random.choice([3.5, 4.0, 4.0, 4.5, 4.5, 5.0])
            independence = random.choice([2.5, 3.0, 3.0, 3.5, 4.0])
            
            QualityOfLifeAssessment.objects.create(
                resident=resident,
                assessment_date=timezone.now().date() - timedelta(days=random.randint(1, 90)),
                assessment_tool=tool,
                assessment_method=method,
                assessed_by=assessed_by,
                physical_health_wellbeing=Decimal(str(physical_health)),
                psychological_wellbeing=Decimal(str(psychological)),
                social_relationships=Decimal(str(social_relationships)),
                environment_satisfaction=Decimal(str(environment)),
                independence_autonomy=Decimal(str(independence)),
                notes='Regular assessment conducted as part of care planning cycle.',
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} QoL assessments'))

    def create_feedback_themes(self, care_homes, users):
        """Create 6-8 feedback themes."""
        self.stdout.write('Creating feedback themes...')
        
        themes = [
            {'name': 'Staff Kindness & Compassion', 'category': 'POSITIVE', 'occurrences': 45, 'trend': 'INCREASING', 'impact': 5},
            {'name': 'Activity Variety', 'category': 'SUGGESTION', 'occurrences': 12, 'trend': 'STABLE', 'impact': 3},
            {'name': 'Communication with Families', 'category': 'CONCERN', 'occurrences': 8, 'trend': 'DECREASING', 'impact': 4},
            {'name': 'Quality of Meals', 'category': 'POSITIVE', 'occurrences': 32, 'trend': 'STABLE', 'impact': 4},
            {'name': 'Room Temperature Control', 'category': 'CONCERN', 'occurrences': 5, 'trend': 'DECREASING', 'impact': 2},
            {'name': 'Personalized Care Approach', 'category': 'POSITIVE', 'occurrences': 38, 'trend': 'INCREASING', 'impact': 5},
            {'name': 'Weekend Staffing Levels', 'category': 'SUGGESTION', 'occurrences': 6, 'trend': 'STABLE', 'impact': 3},
            {'name': 'Garden & Outdoor Access', 'category': 'POSITIVE', 'occurrences': 15, 'trend': 'INCREASING', 'impact': 4},
        ]
        
        count = 0
        for theme_data in themes:
            care_home = random.choice(care_homes)
            created_by = random.choice(users)
            
            FeedbackTheme.objects.create(
                care_home=care_home,
                theme_name=theme_data['name'],
                theme_category=theme_data['category'],
                description=f"Recurring theme identified through analysis of surveys and feedback.",
                occurrences_count=theme_data['occurrences'],
                first_occurrence=timezone.now().date() - timedelta(days=random.randint(30, 180)),
                last_occurrence=timezone.now().date() - timedelta(days=random.randint(1, 30)),
                trend_direction=theme_data['trend'],
                impact_on_satisfaction=theme_data['impact'],
                is_active=True,
                created_by=created_by,
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} feedback themes'))
