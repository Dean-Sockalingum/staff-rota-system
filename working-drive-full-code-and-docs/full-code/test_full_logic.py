#!/usr/bin/env python3
import os
import sys
import django
from collections import defaultdict

sys.path.insert(0, '/Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete')
os.chdir('/Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import Shift, Unit
from datetime import date

start_date = date(2026, 1, 4)

# Test with HAWTHORN_HOUSE
selected_home = 'HAWTHORN_HOUSE'
day_care_roles = {'SCW', 'SCA'}

print(f'=== TESTING {selected_home} ===\n')

# Get units (mimicking view logic)
units = Unit.objects.filter(is_active=True, care_home__name=selected_home)
all_unit_names = sorted([unit.name for unit in units])
print(f'Units for {selected_home}: {all_unit_names}\n')

# Get shifts
shifts_query = Shift.objects.filter(
    date=start_date,
    unit__care_home__name=selected_home
).select_related('user', 'unit', 'shift_type')

day_shifts = [s for s in shifts_query if s.shift_type.name in ['DAY', 'EARLY', 'LATE', 'LONG_DAY']]
print(f'Day shifts: {len(day_shifts)}')

day_care = [
    s for s in day_shifts
    if getattr(getattr(s.user, 'role', None), 'name', '') in day_care_roles
]
print(f'Day care shifts: {len(day_care)}\n')

# Group by unit (mimicking view logic)
day_care_by_unit = defaultdict(list)
for shift in day_care:
    unit_name = shift.unit.name if shift.unit else 'Unknown'
    day_care_by_unit[unit_name].append(shift)

print(f'day_care_by_unit dictionary:')
for unit_name in sorted(day_care_by_unit.keys()):
    print(f'  {unit_name}: {len(day_care_by_unit[unit_name])} shifts')

# Create sorted version (mimicking view logic)
day_care_by_unit_sorted = {}
for unit_name in all_unit_names:
    if unit_name in day_care_by_unit:
        day_care_by_unit_sorted[unit_name] = day_care_by_unit[unit_name]
    else:
        day_care_by_unit_sorted[unit_name] = []

print(f'\nday_care_by_unit_sorted (should be passed to template):')
for unit_name, shifts in day_care_by_unit_sorted.items():
    print(f'  {unit_name}: {len(shifts)} shifts')
    if shifts:
        print(f'    Sample: {shifts[0].user.full_name}')
