# Generated migration for Task 22: SMS Integration
# Adds SMS notification preferences to User model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0001_initial'),  # Update with actual latest migration
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='sms_notifications_enabled',
            field=models.BooleanField(
                default=False,
                help_text='Enable SMS notifications for urgent alerts'
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='sms_emergency_only',
            field=models.BooleanField(
                default=False,
                help_text='Only send SMS for emergency/critical alerts'
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='sms_opted_in_date',
            field=models.DateTimeField(
                null=True,
                blank=True,
                help_text='Date when user opted in to SMS notifications'
            ),
        ),
    ]
