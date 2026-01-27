#!/usr/bin/env python3
"""
Create test vacancy records for HOS dashboard demonstration
"""

import os
import sys
import django
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(__file__))
os.environ['DJANGO_SETTINGS_MODULE'] = 'rotasystems.settings'
django.setup()

from scheduling.models import User
from staff_records.models import StaffProfile

print("Creating test vacancy records...\n")

today = date(2025, 12, 19)

# Define test vacancies across different homes and roles
test_vacancies = [
    # Orchard Grove - 3 vacancies
    {'home': 'ORCHARD_GROVE', 'role': 'SCA', 'days_ago': 45, 'hours': 37.5},  # HIGH severity
    {'home': 'ORCHARD_GROVE', 'role': 'SCAN', 'days_ago': 20, 'hours': 40},  # MEDIUM severity
    {'home': 'ORCHARD_GROVE', 'role': 'SCW', 'days_ahead': -10, 'hours': 37.5},  # Upcoming leaver
    
    # Riverside - 2 vacancies
    {'home': 'RIVERSIDE', 'role': 'SCA', 'days_ago': 60, 'hours': 40},  # HIGH severity
    {'home': 'RIVERSIDE', 'role': 'SSCW', 'days_ago': 8, 'hours': 37.5},  # LOW severity
    
    # Meadowburn - 3 vacancies
    {'home': 'MEADOWBURN', 'role': 'SCAN', 'days_ago': 35, 'hours': 40},  # HIGH severity
    {'home': 'MEADOWBURN', 'role': 'SCW', 'days_ago': 15, 'hours': 37.5},  # MEDIUM severity
    {'home': 'MEADOWBURN', 'role': 'SCA', 'days_ahead': -5, 'hours': 40},  # Upcoming leaver
    
    # Hawthorn House - 2 vacancies
    {'home': 'HAWTHORN_HOUSE', 'role': 'SCWN', 'days_ago': 50, 'hours': 40},  # HIGH severity
    {'home': 'HAWTHORN_HOUSE', 'role': 'SCA', 'days_ahead': -15, 'hours': 37.5},  # Upcoming leaver
    
    # Victoria Gardens - 2 vacancies
    {'home': 'VICTORIA_GARDENS', 'role': 'SCW', 'days_ago': 25, 'hours': 40},  # MEDIUM severity
    {'home': 'VICTORIA_GARDENS', 'role': 'SCA', 'days_ahead': -20, 'hours': 37.5},  # Upcoming leaver
]

created = 0
skipped = 0

for vacancy_data in test_vacancies:
    home_name = vacancy_data['home']
    role_name = vacancy_data['role']
    
    # Calculate end date
    if 'days_ago' in vacancy_data:
        end_date = today - timedelta(days=vacancy_data['days_ago'])
        status_desc = f"Left {vacancy_data['days_ago']} days ago"
    else:
        end_date = today + timedelta(days=abs(vacancy_data['days_ahead']))
        status_desc = f"Leaving in {abs(vacancy_data['days_ahead'])} days"
    
    # Find a staff member from this home and role
    user = User.objects.filter(
        unit__care_home__name=home_name,
        role__name=role_name,
        is_active=True
    ).exclude(
        staff_profile__employment_status='LEAVER'
    ).first()
    
    if not user:
        print(f"  ⚠️  No available {role_name} staff in {home_name}")
        skipped += 1
        continue
    
    # Get or create profile
    profile, _ = StaffProfile.objects.get_or_create(user=user)
    
    # Mark as leaver
    profile.employment_status = 'LEAVER'
    profile.end_date = end_date
    profile.save()
    
    # Update user's shifts_per_week
    user.shifts_per_week_override = vacancy_data['hours']
    user.save()
    
    print(f"  ✓ {home_name}: {user.full_name} ({role_name}) - {status_desc}")
    print(f"    End date: {end_date}, Hours/week: {vacancy_data['hours']}")
    created += 1

print(f"\n✓ Created {created} test vacancy records")
if skipped > 0:
    print(f"  Skipped {skipped} (no suitable staff found)")

print("\nVacancy summary by home:")
from django.db.models import Count
vacancies_by_home = StaffProfile.objects.filter(
    employment_status='LEAVER',
    end_date__isnull=False
).values('user__unit__care_home__name').annotate(count=Count('id'))

for v in vacancies_by_home:
    home = v['user__unit__care_home__name']
    count = v['count']
    print(f"  {home}: {count} vacancies")
