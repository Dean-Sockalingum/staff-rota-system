# Generated manually for YouSaidWeDidAction model
# Date: 2026-01-22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('scheduling', '0001_initial'),  # Assuming CareHome is in scheduling app
        ('experience_feedback', '0002_alter_satisfactionsurvey_survey_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='YouSaidWeDidAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('you_said', models.TextField(help_text='The feedback/comment from resident, family, or staff', verbose_name='You Said')),
                ('we_did', models.TextField(help_text='The action we took in response', verbose_name='We Did')),
                ('feedback_date', models.DateField(help_text='Date the feedback was received', verbose_name='Feedback Date')),
                ('category', models.CharField(choices=[('CARE', 'Care & Support'), ('FOOD', 'Food & Dining'), ('ACTIVITIES', 'Activities & Social'), ('ENVIRONMENT', 'Environment'), ('COMMUNICATION', 'Communication'), ('STAFF', 'Staffing'), ('OTHER', 'Other')], default='OTHER', help_text='Category of feedback', max_length=20, verbose_name='Category')),
                ('sentiment', models.CharField(choices=[('POSITIVE', 'Positive'), ('NEUTRAL', 'Neutral'), ('CONCERN', 'Concern/Negative')], default='NEUTRAL', help_text='Overall sentiment of the feedback', max_length=10, verbose_name='Sentiment')),
                ('status', models.CharField(choices=[('PLANNED', 'Planned'), ('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed')], default='PLANNED', help_text='Status of the action', max_length=20, verbose_name='Status')),
                ('source_type', models.CharField(blank=True, choices=[('RESIDENT', 'Resident Feedback'), ('FAMILY', 'Family Feedback'), ('STAFF', 'Staff Feedback'), ('SURVEY', 'Survey Response'), ('COMPLAINT', 'Complaint'), ('SUGGESTION_BOX', 'Suggestion Box'), ('MEETING', 'Residents/Relatives Meeting'), ('OTHER', 'Other Source')], help_text='Where the feedback came from', max_length=20, verbose_name='Source Type')),
                ('person_raised', models.CharField(blank=True, help_text='Name/description of person who raised feedback (anonymized if needed)', max_length=200, verbose_name='Raised By')),
                ('action_taken_by', models.CharField(blank=True, help_text='Who took the action (person/team/department)', max_length=200, verbose_name='Action Taken By')),
                ('action_date', models.DateField(blank=True, help_text='Date action was started', null=True, verbose_name='Action Date')),
                ('completion_date', models.DateField(blank=True, help_text='Date action was completed', null=True, verbose_name='Completion Date')),
                ('communication_details', models.TextField(blank=True, help_text='Details of how the response was communicated back', verbose_name='Communication Details')),
                ('communicated_back', models.BooleanField(default=False, help_text='Was the action communicated back to the person who raised it?', verbose_name='Communicated Back')),
                ('display_on_board', models.BooleanField(default=True, help_text='Should this be displayed on the public You Said, We Did board?', verbose_name='Display on Notice Board')),
                ('display_start_date', models.DateField(blank=True, help_text='Start date for displaying on notice board', null=True, verbose_name='Display From')),
                ('display_end_date', models.DateField(blank=True, help_text='End date for displaying on notice board', null=True, verbose_name='Display Until')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('care_home', models.ForeignKey(help_text='Care home where feedback was received', on_delete=django.db.models.deletion.CASCADE, related_name='yswda_actions', to='scheduling.carehome')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='yswda_actions_created', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'You Said, We Did Action',
                'verbose_name_plural': 'You Said, We Did Actions',
                'ordering': ['-feedback_date', '-created_at'],
                'indexes': [
                    models.Index(fields=['care_home', 'feedback_date'], name='experience__care_ho_idx'),
                    models.Index(fields=['status'], name='experience__status_idx'),
                    models.Index(fields=['display_on_board', 'display_start_date', 'display_end_date'], name='experience__display_idx'),
                ],
            },
        ),
    ]
