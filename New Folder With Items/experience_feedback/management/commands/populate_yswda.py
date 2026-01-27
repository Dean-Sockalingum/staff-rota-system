"""
Management command to populate sample You Said, We Did actions
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from scheduling.models import CareHome
from experience_feedback.models import YouSaidWeDidAction

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate sample You Said, We Did actions for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating You Said, We Did sample data...')
        
        # Get or create a care home
        care_home = CareHome.objects.filter(is_active=True).first()
        if not care_home:
            self.stdout.write(self.style.ERROR('No active care home found. Please create one first.'))
            return
        
        # Get first admin user for responsible_person
        admin_user = User.objects.filter(is_staff=True).first()
        
        # Sample actions
        sample_actions = [
            {
                'you_said': "I would love more vegetarian options at dinner time",
                'we_did': "We reviewed our dinner menus with our chef and now offer 2 vegetarian main course options every evening. We also introduced Meat-Free Mondays with new plant-based recipes.",
                'category': 'MEALS',
                'sentiment': 'POSITIVE',
                'status': 'COMPLETED',
                'source_type': 'INFORMAL',
                'who_said_it': 'Resident (anonymized)',
                'feedback_date': timezone.now().date() - timedelta(days=45),
                'action_taken_date': timezone.now().date() - timedelta(days=38),
                'display_on_board': True,
                'display_until': timezone.now().date() + timedelta(days=45),
            },
            {
                'you_said': "It's sometimes difficult to contact staff when I call from my room",
                'we_did': "We installed additional call points in all bedrooms and corridors. We also introduced a guaranteed 5-minute maximum response time policy.",
                'category': 'CARE_QUALITY',
                'sentiment': 'CONCERN',
                'status': 'COMPLETED',
                'source_type': 'COMPLAINT',
                'who_said_it': "Resident's daughter",
                'feedback_date': timezone.now().date() - timedelta(days=60),
                'action_taken_date': timezone.now().date() - timedelta(days=50),
                'display_on_board': True,
                'display_until': timezone.now().date() + timedelta(days=30),
            },
            {
                'you_said': "I really enjoy the morning coffee social, but would love more activities in the afternoon",
                'we_did': "We introduced afternoon tea with entertainment every Tuesday and Thursday at 2:30pm. Activities include live music, quizzes, and crafts.",
                'category': 'ACTIVITIES',
                'sentiment': 'SUGGESTION',
                'status': 'COMPLETED',
                'source_type': 'MEETING',
                'who_said_it': 'Multiple residents',
                'feedback_date': timezone.now().date() - timedelta(days=30),
                'action_taken_date': timezone.now().date() - timedelta(days=21),
                'display_on_board': True,
                'display_until': timezone.now().date() + timedelta(days=60),
            },
            {
                'you_said': "The garden could be more accessible for residents with mobility aids",
                'we_did': "We created a fully accessible paved pathway around the garden with rest benches every 10 meters. We also installed raised flower beds.",
                'category': 'ENVIRONMENT',
                'sentiment': 'CONCERN',
                'status': 'COMPLETED',
                'source_type': 'CARE_REVIEW',
                'who_said_it': 'Senior Care Assistant',
                'feedback_date': timezone.now().date() - timedelta(days=90),
                'action_taken_date': timezone.now().date() - timedelta(days=75),
                'display_on_board': True,
                'display_until': timezone.now().date() + timedelta(days=90),
            },
            {
                'you_said': "I don't always know what activities are happening each week",
                'we_did': "We now send weekly activity schedules to all family members via email, post large-print schedules on every floor, and have a 'What's On Today' board at reception.",
                'category': 'COMMUNICATION',
                'sentiment': 'CONCERN',
                'status': 'COMPLETED',
                'source_type': 'SURVEY',
                'who_said_it': 'Multiple residents and families',
                'feedback_date': timezone.now().date() - timedelta(days=20),
                'action_taken_date': timezone.now().date() - timedelta(days=14),
                'display_on_board': True,
                'display_until': timezone.now().date() + timedelta(days=60),
            },
            {
                'you_said': "The fish and chips on Fridays are brilliant, could we have them more often?",
                'we_did': "Based on popular demand, we now serve our classic fish and chips every Friday lunchtime, and added a 'Great British Seaside' themed meal once a month!",
                'category': 'MEALS',
                'sentiment': 'POSITIVE',
                'status': 'COMPLETED',
                'source_type': 'SUGGESTION_BOX',
                'who_said_it': 'Anonymous resident',
                'feedback_date': timezone.now().date() - timedelta(days=15),
                'action_taken_date': timezone.now().date() - timedelta(days=7),
                'display_on_board': True,
                'display_until': timezone.now().date() + timedelta(days=60),
            },
            {
                'you_said': "It would be nice to have more one-to-one time with carers",
                'we_did': "We introduced 'Tea & Talk Time' - 30 minutes of dedicated one-to-one time for each resident weekly with their key worker.",
                'category': 'CARE_QUALITY',
                'sentiment': 'SUGGESTION',
                'status': 'IN_PROGRESS',
                'source_type': 'MEETING',
                'who_said_it': 'Raised at Residents & Relatives meeting',
                'feedback_date': timezone.now().date() - timedelta(days=10),
                'action_taken_date': timezone.now().date() - timedelta(days=5),
                'display_on_board': True,
                'display_until': timezone.now().date() + timedelta(days=90),
            },
            {
                'you_said': "We need better lighting in the corridors during the evening",
                'we_did': "We've installed motion-sensor LED lighting in all corridors providing bright light when needed, while maintaining low-level night lights.",
                'category': 'SAFETY',
                'sentiment': 'CONCERN',
                'status': 'COMPLETED',
                'source_type': 'INFORMAL',
                'who_said_it': 'Night Shift Team',
                'feedback_date': timezone.now().date() - timedelta(days=50),
                'action_taken_date': timezone.now().date() - timedelta(days=35),
                'display_on_board': True,
                'display_until': timezone.now().date() + timedelta(days=60),
            },
        ]
        
        created_count = 0
        for action_data in sample_actions:
            # Add care home and created_by
            action_data['care_home'] = care_home
            if admin_user:
                action_data['created_by'] = admin_user
                action_data['responsible_person'] = admin_user
            
            # Create action
            action, created = YouSaidWeDidAction.objects.get_or_create(
                you_said=action_data['you_said'],
                care_home=care_home,
                defaults=action_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created: "{action.you_said[:50]}..."'))
            else:
                self.stdout.write(f'  Already exists: "{action.you_said[:50]}..."')
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully created {created_count} new You Said, We Did actions'))
        self.stdout.write(f'📊 Total actions in database: {YouSaidWeDidAction.objects.count()}')
        self.stdout.write(f'📌 Actions on notice board: {YouSaidWeDidAction.objects.filter(display_on_board=True).count()}')
        
        # Show public board URL
        self.stdout.write(self.style.SUCCESS(f'\n🌐 Public Notice Board URL:'))
        self.stdout.write(f'   /experience-feedback/public/yswda/{care_home.id}/')
