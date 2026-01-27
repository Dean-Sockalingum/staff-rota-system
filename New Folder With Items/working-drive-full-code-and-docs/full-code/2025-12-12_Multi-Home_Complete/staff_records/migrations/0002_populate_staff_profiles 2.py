from django.db import migrations


def create_profiles(apps, schema_editor):
    User = apps.get_model('scheduling', 'User')
    StaffProfile = apps.get_model('staff_records', 'StaffProfile')

    for user in User.objects.all():
        StaffProfile.objects.get_or_create(user=user)


def reverse_profiles(apps, schema_editor):
    # No-op: keep generated profiles.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('staff_records', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_profiles, reverse_profiles),
    ]
