from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff_records', '0002_populate_staff_profiles'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sicknessrecord',
            old_name='sickness_start',
            new_name='first_working_day',
        ),
        migrations.RenameField(
            model_name='sicknessrecord',
            old_name='sickness_end',
            new_name='estimated_return_to_work',
        ),
        migrations.AddField(
            model_name='sicknessrecord',
            name='absence_percentage_12m',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name='sicknessrecord',
            name='actual_last_working_day',
            field=models.DateField(blank=True, help_text='Confirmed last day of sickness absence when known.', null=True),
        ),
        migrations.AddField(
            model_name='sicknessrecord',
            name='separate_sickness_count_12m',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='sicknessrecord',
            name='total_working_days_sick',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='sicknessrecord',
            name='trigger_outcome',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='sicknessrecord',
            name='trigger_reached',
            field=models.BooleanField(default=False),
        ),
    ]
