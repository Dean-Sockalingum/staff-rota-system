# Generated manually on 2026-01-05 to add missing User model fields
# NOTE: sms_* fields already added in 0002_sms_notifications (merged at 0031)
# This migration intentionally left empty to preserve migration sequence

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0056_alter_unit_care_home'),
    ]

    operations = [
        # Empty - sms_notifications_enabled, sms_emergency_only, and sms_opted_in_date
        # already exist from 0002_sms_notifications migration (merged at 0031_merge_20251230_0908)
    ]
