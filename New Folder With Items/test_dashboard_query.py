#!/usr/bin/env python3
"""
Test what the dashboard view sees.
"""

import os
import django
import sys
from datetime import date

sys.path.insert(0, '/home/staff-rota-system/2025-12-12_Multi-Home_Complete')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import Shift
from scheduling.models_multi_home import CareHome
from django.utils import timezone

print("="*80)
print("TESTING DASHBOARD QUERY")
print("="*80)

# Mimic the dashboard query
today = timezone.now().date()
print(f"\nToday's date: {today}")

today_shifts = Shift.objects.filter(
    date=today,
    status__in=['SCHEDULED', 'CONFIRMED']
).select_related('unit', 'shift_type', 'user', 'user__role')

print(f"Total shifts today with status SCHEDULED/CONFIRMED: {today_shifts.count()}")

# Check by home
day_shift_names = ['DAY', 'DAY_SENIOR', 'DAY_ASSISTANT']
night_shift_names = ['NIGHT', 'NIGHT_SENIOR', 'NIGHT_ASSISTANT']

for home_name in ['HAWTHORN_HOUSE', 'MEADOWBURN', 'RIVERSIDE', 'ORCHARD_GROVE']:
    home = CareHome.objects.get(name=home_name)
    home_shifts_today = today_shifts.filter(unit__care_home=home)
    day_shifts_qs = home_shifts_today.filter(shift_type__name__in=day_shift_names)
    night_shifts_qs = home_shifts_today.filter(shift_type__name__in=night_shift_names)
    
    # Count SSCW
    day_sscw = 0
    for shift in day_shifts_qs:
        role_code = getattr(getattr(shift.user, 'role', None), 'name', None)
        if role_code == 'SSCW':
            day_sscw += 1
    
    night_sscwn = 0
    for shift in night_shifts_qs:
        role_code = getattr(getattr(shift.user, 'role', None), 'name', None)
        if role_code == 'SSCWN':
            night_sscwn += 1
    
    print(f"\n{home_name}:")
    print(f"  Total today: {home_shifts_today.count()}")
    print(f"  Day shifts: {day_shifts_qs.count()}")
    print(f"  Night shifts: {night_shifts_qs.count()}")
    print(f"  Day SSCW: {day_sscw}")
    print(f"  Night SSCWN: {night_sscwn}")
    
    # Check statuses
    statuses = {}
    for shift in home_shifts_today[:10]:
        statuses[shift.status] = statuses.get(shift.status, 0) + 1
    if statuses:
        print(f"  Sample statuses: {dict(statuses)}")
