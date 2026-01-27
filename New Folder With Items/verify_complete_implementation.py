#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import CareHome, Unit, User, Shift, ShiftType
from django.db.models import Count
from datetime import date

print('=' * 80)
print('COMPLETE 5-HOME IMPLEMENTATION VERIFICATION')
print('=' * 80)
print()

# Get all homes
homes = CareHome.objects.all().order_by('name')

print('SUMMARY BY HOME:')
print('-' * 80)
for home in homes:
    staff_count = User.objects.filter(unit__care_home=home).count()
    shift_count = Shift.objects.filter(user__unit__care_home=home).count()
    
    # Get shift date range
    shifts = Shift.objects.filter(user__unit__care_home=home)
    if shifts.exists():
        min_date = shifts.order_by('date').first().date
        max_date = shifts.order_by('-date').first().date
        date_range = f'{min_date} to {max_date}'
    else:
        date_range = 'NO SHIFTS'
    
    print(f'{home.name:20s}: {home.bed_capacity:3d} beds, {staff_count:3d} staff, {shift_count:6,d} shifts ({date_range})')

print()
print(f'TOTAL STAFF:  {User.objects.count()}')
print(f'TOTAL SHIFTS: {Shift.objects.count():,}')
print()

# Victoria Gardens detailed breakdown
print('=' * 80)
print('VICTORIA GARDENS DETAILED VERIFICATION')
print('=' * 80)
vg = CareHome.objects.get(name='VICTORIA_GARDENS')

print(f'\nBed capacity: {vg.bed_capacity} beds')
print('\nUnits:')
units = Unit.objects.filter(care_home=vg).order_by('name')
for unit in units:
    staff_count = User.objects.filter(unit=unit).count()
    bed_info = unit.description.split('(')[1].split(')')[0] if '(' in unit.description else 'Mgmt'
    print(f'  {unit.name:30s}: {staff_count:2d} staff ({bed_info})')

print('\nStaff by Role:')
vg_staff = User.objects.filter(unit__care_home=vg)
role_counts = vg_staff.values('role__name').annotate(count=Count('role')).order_by('role__name')
for rc in role_counts:
    print(f'  {rc["role__name"]:10s}: {rc["count"]:2d}')
print(f'  {"TOTAL":10s}: {vg_staff.count():2d}')

# Compliance check for sample dates
print('\n' + '=' * 80)
print('COMPLIANCE CHECK - SAMPLE DATES')
print('=' * 80)

day_shift = ShiftType.objects.get(name='DAY_0800_2000')
night_shift = ShiftType.objects.get(name='NIGHT_2000_0800')

sample_dates = [date(2026, 2, 15), date(2026, 3, 15), date(2026, 5, 15)]

for check_date in sample_dates:
    print(f'\n{check_date}:')
    print('-' * 80)
    
    for home in homes:
        day_shifts = Shift.objects.filter(user__unit__care_home=home, date=check_date, shift_type=day_shift)
        night_shifts = Shift.objects.filter(user__unit__care_home=home, date=check_date, shift_type=night_shift)
        
        day_sscw = day_shifts.filter(user__role__name='SSCW').count()
        night_sscwn = night_shifts.filter(user__role__name='SSCWN').count()
        
        # Compliance requirements
        if home.name == 'VICTORIA_GARDENS':
            min_day = 10
            min_night = 10
            min_super = 1
        else:
            min_day = 17
            min_night = 17
            min_super = 2
        
        day_status = '✅' if day_shifts.count() >= min_day and day_sscw >= min_super else '❌'
        night_status = '✅' if night_shifts.count() >= min_night and night_sscwn >= min_super else '❌'
        
        print(f'{home.name:20s}: Day {day_status} {day_shifts.count():2d}/{min_day} (SSCW: {day_sscw}), Night {night_status} {night_shifts.count():2d}/{min_night} (SSCWN: {night_sscwn})')

# Per-unit staffing check for VG
print('\n' + '=' * 80)
print('VICTORIA GARDENS PER-UNIT STAFFING CHECK')
print('=' * 80)

care_units = Unit.objects.filter(care_home=vg).exclude(name__contains='Mgmt')
check_date = date(2026, 2, 15)

print(f'\nDate: {check_date}')
print('Requirement: Minimum 2 staff per unit on days, 2 per unit on nights')
print('-' * 80)

for unit in care_units:
    day_count = Shift.objects.filter(unit=unit, date=check_date, shift_type=day_shift).count()
    night_count = Shift.objects.filter(unit=unit, date=check_date, shift_type=night_shift).count()
    
    day_status = '✅' if day_count >= 2 else '❌'
    night_status = '✅' if night_count >= 2 else '❌'
    
    print(f'{unit.name:30s}: Day {day_status} {day_count:2d}/2, Night {night_status} {night_count:2d}/2')

print('\n' + '=' * 80)
print('✅ VERIFICATION COMPLETE')
print('=' * 80)
