# Generated manually on 2026-01-19 10:22
# Migration to create StaffCertification table for PostgreSQL

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0062_add_is_overtime_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaffCertification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('certification_type', models.CharField(choices=[
                    ('FIRST_AID', 'First Aid'),
                    ('MANUAL_HANDLING', 'Manual Handling'),
                    ('FIRE_SAFETY', 'Fire Safety'),
                    ('FOOD_HYGIENE', 'Food Hygiene'),
                    ('MEDICATION', 'Medication Administration'),
                    ('SAFEGUARDING', 'Safeguarding'),
                    ('INFECTION_CONTROL', 'Infection Control'),
                    ('DEMENTIA_CARE', 'Dementia Care'),
                    ('PALLIATIVE_CARE', 'Palliative Care'),
                    ('PVG', 'PVG Scheme'),
                    ('SSSC', 'SSSC Registration'),
                    ('OTHER', 'Other'),
                ], max_length=50)),
                ('certification_name', models.CharField(max_length=200)),
                ('issue_date', models.DateField()),
                ('expiry_date', models.DateField()),
                ('renewal_date', models.DateField(blank=True, help_text='Expected renewal date', null=True)),
                ('issuing_body', models.CharField(blank=True, max_length=200)),
                ('certificate_number', models.CharField(blank=True, max_length=100)),
                ('status', models.CharField(choices=[
                    ('VALID', 'Valid'),
                    ('EXPIRING_SOON', 'Expiring Soon'),
                    ('EXPIRED', 'Expired'),
                    ('PENDING', 'Pending Renewal'),
                ], default='VALID', max_length=20)),
                ('certificate_file', models.FileField(blank=True, null=True, upload_to='certificates/')),
                ('days_before_expiry_alert', models.IntegerField(default=30, help_text='Days before expiry to send alert')),
                ('alert_sent', models.BooleanField(default=False)),
                ('alert_sent_at', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_certifications', to=settings.AUTH_USER_MODEL)),
                ('staff_member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Staff Certification',
                'verbose_name_plural': 'Staff Certifications',
                'ordering': ['expiry_date'],
                'indexes': [
                    models.Index(fields=['staff_member', 'expiry_date'], name='scheduling_staff_member_expiry_idx'),
                    models.Index(fields=['certification_type', 'status'], name='scheduling_cert_type_status_idx'),
                    models.Index(fields=['expiry_date', 'status'], name='scheduling_expiry_status_idx'),
                ],
            },
        ),
    ]
