# Generated manually on 2026-01-05 to add missing User model fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0056_alter_unit_care_home'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='sms_notifications_enabled',
            field=models.BooleanField(default=True, help_text='Enable SMS notifications for urgent alerts'),
        ),
        migrations.AddField(
            model_name='user',
            name='sms_emergency_only',
            field=models.BooleanField(default=False, help_text='Only send SMS for emergency/critical alerts'),
        ),
        migrations.AddField(
            model_name='user',
            name='sms_opted_in_date',
            field=models.DateTimeField(blank=True, help_text='Date when user opted in to SMS notifications', null=True),
        ),
    ]
