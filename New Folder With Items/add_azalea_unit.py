#!/usr/bin/env python
"""
Add Azalea Unit to Victoria Gardens (15 beds)
This brings total to 70 beds: Rose (15) + Lily (15) + Daisy (15) + Azalea (15) + Tulip (10)
"""

import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.db import transaction
from django.contrib.auth.hashers import make_password
from scheduling.models import CareHome, Unit, Role, ShiftType, User, Shift

# Pre-hash password for performance
HASHED_PASSWORD = make_password('password123')

# Date range for 6-month implementation
START_DATE = date(2026, 1, 26)
END_DATE = date(2026, 7, 26)

print('=' * 80)
print('ADDING AZALEA UNIT TO VICTORIA GARDENS')
print('=' * 80)
print()
print('This script will:')
print('  1. Create Azalea Unit (15 beds)')
print('  2. Redistribute staff across 5 care units (Rose, Lily, Daisy, Azalea, Tulip)')
print('  3. Regenerate all shifts to ensure proper coverage')
print()

response = input('Proceed? (yes/no): ')
if response.lower() != 'yes':
    print('Cancelled.')
    exit(0)

def generate_shift_dates_6_months(shifts_per_week, team, is_night=False):
    """Generate shift dates for 6-month period using 3-week rotation"""
    dates = []
    current = START_DATE
    week_counter = 0
    
    # Define day patterns for 3-week rotation
    if shifts_per_week == 2:
        # 2 shifts/week: Same 2 days every week
        if team == 'A':
            days_in_week = [0, 1]  # Sun, Mon
        elif team == 'B':
            days_in_week = [3, 4]  # Wed, Thu
        else:  # Team C
            days_in_week = [5, 6]  # Fri, Sat
            
        while current <= END_DATE:
            weekday = current.weekday()
            # Convert to Sunday=0 system
            sunday_based = (weekday + 1) % 7
            if sunday_based in days_in_week:
                dates.append(current)
            current += timedelta(days=1)
            
    elif shifts_per_week == 3:
        # 3 shifts/week: 3-week rotating pattern
        patterns = {
            'A': [[0,1,2], [3,4,5], [2,3,4]],  # Week 1, Week 2, Week 3
            'B': [[3,4,5], [2,3,4], [0,1,2]],
            'C': [[2,3,4], [0,1,2], [3,4,5]]
        }
        team_pattern = patterns[team]
        
        while current <= END_DATE:
            weekday = current.weekday()
            sunday_based = (weekday + 1) % 7
            pattern_week = week_counter % 3
            
            if sunday_based in team_pattern[pattern_week]:
                dates.append(current)
            
            if sunday_based == 6:  # Saturday (end of week)
                week_counter += 1
                
            current += timedelta(days=1)
            
    elif shifts_per_week == 5:
        # 5 shifts/week: Monday-Friday
        while current <= END_DATE:
            if current.weekday() < 5:  # Monday=0 to Friday=4
                dates.append(current)
            current += timedelta(days=1)
    
    return sorted(dates)

with transaction.atomic():
    print('\n' + '=' * 80)
    print('STEP 1: CREATE AZALEA UNIT')
    print('=' * 80)
    
    vg = CareHome.objects.get(name='VICTORIA_GARDENS')
    
    # Check if Azalea already exists
    if Unit.objects.filter(care_home=vg, name='VICTORIA_GARDENS_Azalea').exists():
        print('⚠️  Azalea unit already exists')
        azalea = Unit.objects.get(care_home=vg, name='VICTORIA_GARDENS_Azalea')
    else:
        azalea = Unit.objects.create(
            care_home=vg,
            name='VICTORIA_GARDENS_Azalea',
            description='Azalea Unit at Victoria Gardens (15 beds)',
            is_active=True
        )
        print(f'✅ Created Azalea Unit (15 beds)')
    
    print('\n' + '=' * 80)
    print('STEP 2: DELETE ALL VG SHIFTS AND REDISTRIBUTE STAFF')
    print('=' * 80)
    
    # Delete all existing shifts
    shift_count = Shift.objects.filter(user__unit__care_home=vg).count()
    Shift.objects.filter(user__unit__care_home=vg).delete()
    print(f'✅ Deleted {shift_count:,} existing shifts')
    
    # Get all current staff
    all_staff = list(User.objects.filter(unit__care_home=vg).exclude(unit__name__contains='Mgmt'))
    mgmt_staff = list(User.objects.filter(unit__care_home=vg, unit__name__contains='Mgmt'))
    
    print(f'✅ Found {len(all_staff)} care staff + {len(mgmt_staff)} management')
    
    # Get all care units
    units = {
        'Rose': Unit.objects.get(care_home=vg, name='VICTORIA_GARDENS_Rose'),
        'Lily': Unit.objects.get(care_home=vg, name='VICTORIA_GARDENS_Lily'),
        'Daisy': Unit.objects.get(care_home=vg, name='VICTORIA_GARDENS_Daisy'),
        'Azalea': azalea,
        'Tulip': Unit.objects.get(care_home=vg, name='VICTORIA_GARDENS_Tulip')
    }
    
    # Redistribute staff evenly across 5 units
    # Group by role first
    by_role = {}
    for staff in all_staff:
        role = staff.role.name
        if role not in by_role:
            by_role[role] = []
        by_role[role].append(staff)
    
    print('\nRedistributing staff by role:')
    unit_list = ['Rose', 'Lily', 'Daisy', 'Azalea', 'Tulip']
    
    for role, staff_list in by_role.items():
        print(f'  {role}: {len(staff_list)} staff')
        # Distribute evenly
        for idx, staff in enumerate(staff_list):
            unit_name = unit_list[idx % 5]
            staff.unit = units[unit_name]
            staff.save(update_fields=['unit'])
    
    # Verify distribution
    print('\nStaff distribution by unit:')
    for unit_name in unit_list:
        count = User.objects.filter(unit=units[unit_name]).count()
        print(f'  {unit_name}: {count} staff')
    
    print('\n' + '=' * 80)
    print('STEP 3: REGENERATE ALL 6-MONTH SHIFTS')
    print('=' * 80)
    
    # Get roles and shift types
    shift_types = {st.name: st for st in ShiftType.objects.all()}
    day_shift = shift_types['DAY_0800_2000']
    night_shift = shift_types['NIGHT_2000_0800']
    mgmt_shift = shift_types['MGMT_DAY']
    
    shifts_to_create = []
    
    # Generate shifts for all staff (care + management)
    for user in all_staff + mgmt_staff:
        # Determine shift type based on role
        if user.role.name in ['SM', 'OM']:
            shift_type = mgmt_shift
            is_night = False
        elif user.role.name in ['SCWN', 'SCAN', 'SSCWN']:
            shift_type = night_shift
            is_night = True
        else:
            shift_type = day_shift
            is_night = False
        
        # Generate dates
        shifts_per_week = user.shifts_per_week_override or 3
        shift_dates = generate_shift_dates_6_months(shifts_per_week, user.team, is_night)
        
        for shift_date in shift_dates:
            shifts_to_create.append(Shift(
                user=user,
                unit=user.unit,
                shift_type=shift_type,
                date=shift_date,
                status='SCHEDULED'
            ))
    
    Shift.objects.bulk_create(shifts_to_create)
    print(f'✅ Created {len(shifts_to_create):,} shifts for 6-month period')
    
    print('\n' + '=' * 80)
    print('✅ AZALEA UNIT ADDITION COMPLETE')
    print('=' * 80)
    
    # Final verification
    print('\nFinal verification:')
    print(f'  Total beds: 70 (Rose 15 + Lily 15 + Daisy 15 + Azalea 15 + Tulip 10)')
    print(f'  Total care units: 5')
    print(f'  Total staff: {User.objects.filter(unit__care_home=vg).count()}')
    print(f'  Total shifts: {Shift.objects.filter(user__unit__care_home=vg).count():,}')
    
    # Check sample date compliance
    sample_date = date(2026, 2, 15)
    day_shifts = Shift.objects.filter(
        user__unit__care_home=vg,
        date=sample_date,
        shift_type=day_shift
    )
    night_shifts = Shift.objects.filter(
        user__unit__care_home=vg,
        date=sample_date,
        shift_type=night_shift
    )
    
    day_sscw = day_shifts.filter(user__role__name='SSCW').count()
    night_sscwn = night_shifts.filter(user__role__name='SSCWN').count()
    
    print(f'\nSample date ({sample_date}) staffing:')
    print(f'  Day shift: {day_shifts.count()} staff (SSCW supernumerary: {day_sscw})')
    print(f'  Night shift: {night_shifts.count()} staff (SSCWN supernumerary: {night_sscwn})')
    
    # Check per-unit staffing
    print(f'\nPer-unit staffing on {sample_date}:')
    for unit_name in unit_list:
        unit = units[unit_name]
        day_count = Shift.objects.filter(unit=unit, date=sample_date, shift_type=day_shift).count()
        night_count = Shift.objects.filter(unit=unit, date=sample_date, shift_type=night_shift).count()
        print(f'  {unit_name:10s}: Day={day_count}, Night={night_count}')
    
    print('\n' + '=' * 80)
    print('All changes committed successfully!')
    print('=' * 80)
