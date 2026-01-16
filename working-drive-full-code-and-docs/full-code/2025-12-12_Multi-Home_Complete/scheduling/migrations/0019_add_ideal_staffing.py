# Generated migration to add ideal staffing fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0018_role_is_senior_management_team_alter_unit_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='ideal_day_staff',
            field=models.IntegerField(default=3, help_text='Ideal day staff count for optimal coverage'),
        ),
        migrations.AddField(
            model_name='unit',
            name='ideal_night_staff',
            field=models.IntegerField(default=2, help_text='Ideal night staff count for optimal coverage'),
        ),
    ]
