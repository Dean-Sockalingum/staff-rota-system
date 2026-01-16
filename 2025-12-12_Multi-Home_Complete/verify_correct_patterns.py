#!/usr/bin/env python3
"""
Verify that shifts match the correct Orchard Grove patterns.
"""

import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Shift, CareHome

print("="*80)
print("PATTERN VERIFICATION - Checking shifts match Orchard Grove patterns")
print("="*80)
print()

# Test date - Week 1 starting Sunday Dec 22, 2025
test_week_start = datetime(2025, 12, 22).date()  # Sunday
days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

# Get Orchard Grove
og = CareHome.objects.get(name='ORCHARD_GROVE')

# Check SSCW (Senior Support Care Workers Day)
print("SSCW (Senior Support Care Workers Day) - Expected Week 1 patterns:")
print("  Group 1 (first 3): Sun, Mon, Tue")
print("  Group 2 (next 3): Tue, Wed, Thu")
print("  Group 3 (last 3): Thu, Fri, Sat")
print()

sscw_staff = User.objects.filter(
    unit__care_home=og,
    role__name='SSCW',
    is_active=True
).order_by('sap')[:9]

for idx, staff in enumerate(sscw_staff):
    group = (idx // 3) + 1
    shifts_week1 = Shift.objects.filter(
        user=staff,
        date__gte=test_week_start,
        date__lt=test_week_start + timedelta(days=7)
    ).order_by('date')
    
    work_days = [days[shift.date.weekday() % 7] for shift in shifts_week1]
    print(f"  {staff.first_name} {staff.last_name} (Group {group}): {', '.join(work_days)}")

print()
print("-"*80)
print()

# Check SCAN 35hrs (Support Care Assistant Night 35hrs)
print("SCAN 35hrs (Support Care Assistant Night 35hrs) - Expected Week 1 patterns:")
print("  Group 1 (first 11): Sun, Mon, Tue")
print("  Group 2 (next 12): Thu, Fri, Sat")
print("  Group 3 (last 12): Tue, Wed, Thu")
print()

scan35_staff = User.objects.filter(
    unit__care_home=og,
    role__name='SCAN',
    is_active=True
).order_by('sap')[:35]

for idx, staff in enumerate(scan35_staff):
    if idx < 11:
        group = 1
    elif idx < 23:
        group = 2
    else:
        group = 3
        
    shifts_week1 = Shift.objects.filter(
        user=staff,
        date__gte=test_week_start,
        date__lt=test_week_start + timedelta(days=7)
    ).order_by('date')
    
    work_days = [days[shift.date.weekday() % 7] for shift in shifts_week1]
    print(f"  {staff.first_name} {staff.last_name} (Group {group}): {', '.join(work_days)}")

print()
print("-"*80)
print()

# Check SCAN 24hrs (Support Care Assistant Night 24hrs)
print("SCAN 24hrs (Support Care Assistant Night 24hrs) - Expected Week 1 patterns:")
print("  Group 1 (first 12): Sun, Mon")
print("  Group 2 (next 12): Thu, Fri")
print("  Group 3 (last 8): Tue, Wed")
print()

scan24_staff = User.objects.filter(
    unit__care_home=og,
    role__name='SCAN',
    is_active=True
).order_by('sap')[35:67]  # Staff 36-67 should be 24hrs

for idx, staff in enumerate(scan24_staff):
    if idx < 12:
        group = 1
    elif idx < 24:
        group = 2
    else:
        group = 3
        
    shifts_week1 = Shift.objects.filter(
        user=staff,
        date__gte=test_week_start,
        date__lt=test_week_start + timedelta(days=7)
    ).order_by('date')
    
    work_days = [days[shift.date.weekday() % 7] for shift in shifts_week1]
    print(f"  {staff.first_name} {staff.last_name} (Group {group}): {', '.join(work_days)}")

print()
print("-"*80)
print()

# Check SM/OM (Service/Operations Managers)
print("SM/OM (Service/Operations Managers) - Expected all weeks: Mon-Fri")
print()

managers = User.objects.filter(
    unit__care_home=og,
    role__name__in=['SM', 'OM'],
    is_active=True
).order_by('sap')

for staff in managers:
    shifts_week1 = Shift.objects.filter(
        user=staff,
        date__gte=test_week_start,
        date__lt=test_week_start + timedelta(days=7)
    ).order_by('date')
    
    work_days = [days[shift.date.weekday() % 7] for shift in shifts_week1]
    print(f"  {staff.first_name} {staff.last_name}: {', '.join(work_days)}")

print()
print("="*80)
print("Verification complete! Check if patterns match your spreadsheets.")
print("="*80)
