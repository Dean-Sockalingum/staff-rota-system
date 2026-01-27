#!/usr/bin/env python3
"""
Check SCAN 24hrs Week 1 pattern starting from first Sunday (Dec 21, 2025)
"""

import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Shift, CareHome

# Jan 4, 2026 is Sunday - the first Sunday and start of Week 1
first_sunday = datetime(2026, 1, 4).date()

days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

og = CareHome.objects.get(name='ORCHARD_GROVE')

print("="*80)
print(f"SCAN 24hrs Week 1 Verification (Starting Sunday {first_sunday})")
print("="*80)
print()
print("Expected patterns based on your spreadsheet:")
print("  Group 1 (first 12 staff): Sun, Mon")
print("  Group 2 (next 12 staff): Thu, Fri") 
print("  Group 3 (last 8 staff): Tue, Wed")
print()
print("-"*80)
print()

scan_staff = User.objects.filter(
    unit__care_home=og,
    role__name='SCAN',
    is_active=True
).order_by('sap')[35:67]  # SCAN 24hrs staff

for idx, staff in enumerate(scan_staff):
    if idx < 12:
        group = 1
        expected = "Sun, Mon"
    elif idx < 24:
        group = 2
        expected = "Thu, Fri"
    else:
        group = 3
        expected = "Tue, Wed"
    
    shifts = Shift.objects.filter(
        user=staff,
        date__gte=first_sunday,
        date__lt=first_sunday + timedelta(days=7)
    ).order_by('date')
    
    # Convert Python weekday (0=Mon, 6=Sun) to our day names (0=Sun, 1=Mon...)
    work_days = [days[(shift.date.weekday() + 1) % 7] for shift in shifts]
    actual = ', '.join(work_days) if work_days else "NO SHIFTS"
    match = "✓" if actual == expected else "✗"
    
    print(f"{match} Group {group} - {staff.first_name} {staff.last_name}: {actual} (expected: {expected})")

print()
print("="*80)
