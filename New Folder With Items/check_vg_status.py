#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import CareHome, Unit, User, Role, Shift, ShiftType
from django.db.models import Count
from datetime import date

vg = CareHome.objects.get(name='VICTORIA_GARDENS')
print('=' * 70)
print('VICTORIA GARDENS CURRENT STATE')
print('=' * 70)
print(f'Bed Capacity: {vg.bed_capacity} beds')
print()

# Units
print('UNITS:')
units = Unit.objects.filter(care_home=vg).order_by('name')
for unit in units:
    staff_count = User.objects.filter(unit=unit).count()
    print(f'  {unit.name}: {staff_count} staff')
print(f'Total Units: {units.count()}')
print()

# Staff by Role
print('STAFF BY ROLE:')
staff = User.objects.filter(unit__care_home=vg)
role_counts = staff.values('role__name').annotate(count=Count('role')).order_by('role__name')
total_staff = staff.count()
for rc in role_counts:
    print(f'  {rc["role__name"]}: {rc["count"]}')
print(f'Total Staff: {total_staff}')
print()

# Shifts
shift_count = Shift.objects.filter(user__unit__care_home=vg).count()
print(f'Total Shifts: {shift_count:,}')
print()

# Sample day staffing check
check_date = date(2026, 2, 15)
day_shift = ShiftType.objects.get(name='DAY_0800_2000')
night_shift = ShiftType.objects.get(name='NIGHT_2000_0800')

day_shifts = Shift.objects.filter(user__unit__care_home=vg, date=check_date, shift_type=day_shift)
night_shifts = Shift.objects.filter(user__unit__care_home=vg, date=check_date, shift_type=night_shift)

print(f'Sample Date: {check_date}')
print(f'  Day shift: {day_shifts.count()} staff')
day_sscw = day_shifts.filter(user__role__name='SSCW').count()
print(f'    - SSCW (supernumerary): {day_sscw}')

print(f'  Night shift: {night_shifts.count()} staff')
night_sscwn = night_shifts.filter(user__role__name='SSCWN').count()
print(f'    - SSCWN (supernumerary): {night_sscwn}')
print()

# Check unit-level staffing
print('UNIT STAFFING ON SAMPLE DATE:')
for unit in units:
    if 'Mgmt' not in unit.name:
        day_in_unit = Shift.objects.filter(unit=unit, date=check_date, shift_type=day_shift).count()
        night_in_unit = Shift.objects.filter(unit=unit, date=check_date, shift_type=night_shift).count()
        print(f'  {unit.name}: Day={day_in_unit}, Night={night_in_unit}')
