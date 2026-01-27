# Generated manually on 2026-01-19 10:15
# Migration to add is_overtime field to Shift model for PostgreSQL

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0061_create_staffcertification_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='shift',
            name='is_overtime',
            field=models.BooleanField(
                default=False,
                db_index=True,
                help_text='True if this is an overtime shift (beyond contracted hours)'
            ),
        ),
    ]
