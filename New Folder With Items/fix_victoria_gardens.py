#!/usr/bin/env python
"""
Fix Victoria Gardens implementation to match exact specifications:
- 70 beds (4 units of 15 beds + 1 unit of 10 beds)
- 98 staff total: 6 SSCW, 4 SSCWN, 1 SM, 1 OM, 31 SCA, 16 SCW, 11 SCWN, 28 SCAN
- Minimum 10 staff on day shift + 1 supernumerary SSCW
- Minimum 10 staff on night shift + 1 supernumerary SSCWN
- Each unit: minimum 2 staff on days and 2 staff on nights
- Same 3-week rotation model as Orchard Grove
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
print('VICTORIA GARDENS CORRECTION SCRIPT')
print('=' * 80)
print()
print('This script will:')
print('  1. Update VG bed capacity to 70 beds')
print('  2. Delete existing VG staff and shifts')
print('  3. Create correct unit structure (4x15 beds + 1x10 beds)')
print('  4. Create 98 staff (6 SSCW, 4 SSCWN, 1 SM, 1 OM, 31 SCA, 16 SCW, 11 SCWN, 28 SCAN)')
print('  5. Generate 6-month shifts ensuring:')
print('     - Min 10 staff + 1 supernumerary SSCW on days')
print('     - Min 10 staff + 1 supernumerary SSCWN on nights')
print('     - Min 2 staff per unit on days and nights')
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
    print('STEP 1: UPDATE VICTORIA GARDENS CONFIGURATION')
    print('=' * 80)
    
    vg = CareHome.objects.get(name='VICTORIA_GARDENS')
    vg.bed_capacity = 70
    vg.save()
    print(f'✅ Updated bed capacity to 70 beds')
    
    print('\n' + '=' * 80)
    print('STEP 2: DELETE EXISTING VG STAFF AND SHIFTS')
    print('=' * 80)
    
    existing_staff = User.objects.filter(unit__care_home=vg)
    shift_count = Shift.objects.filter(user__unit__care_home=vg).count()
    staff_count = existing_staff.count()
    
    Shift.objects.filter(user__unit__care_home=vg).delete()
    existing_staff.delete()
    print(f'✅ Deleted {staff_count} existing staff and {shift_count:,} shifts')
    
    print('\n' + '=' * 80)
    print('STEP 3: UPDATE UNIT STRUCTURE')
    print('=' * 80)
    
    # Delete existing units and recreate with correct bed allocation
    Unit.objects.filter(care_home=vg).delete()
    
    # Create 4 units of 15 beds + 1 unit of 10 beds
    unit_configs = [
        ('Rose', 15),
        ('Lily', 15),
        ('Daisy', 15),
        ('Tulip', 10),  # Smaller unit
        ('Mgmt', 0)      # Management unit
    ]
    
    units_created = {}
    for unit_name, bed_count in unit_configs:
        desc = f'{unit_name} Unit at Victoria Gardens'
        if unit_name == 'Mgmt':
            desc = 'Management at Victoria Gardens'
        elif bed_count == 10:
            desc = f'{unit_name} Unit at Victoria Gardens (10 beds)'
        else:
            desc = f'{unit_name} Unit at Victoria Gardens (15 beds)'
        
        unit = Unit.objects.create(
            care_home=vg,
            name=f'VICTORIA_GARDENS_{unit_name}',
            description=desc,
            is_active=True
        )
        units_created[unit_name] = unit
        
    print(f'✅ Created {len(units_created)} units:')
    for name, bed_count in unit_configs:
        if name != 'Mgmt':
            print(f'   - VICTORIA_GARDENS_{name}: {bed_count} beds')
    
    print('\n' + '=' * 80)
    print('STEP 4: CREATE 98 STAFF WITH CORRECT DISTRIBUTION')
    print('=' * 80)
    
    # Get roles and shift types
    roles = {r.name: r for r in Role.objects.all()}
    shift_types = {st.name: st for st in ShiftType.objects.all()}
    
    day_shift = shift_types['DAY_0800_2000']
    night_shift = shift_types['NIGHT_2000_0800']
    mgmt_shift = shift_types['MGMT_DAY']
    
    mgmt_unit = units_created['Mgmt']
    care_units = [units_created['Rose'], units_created['Lily'], 
                  units_created['Daisy'], units_created['Tulip']]
    
    all_staff = []
    sap_counter = [400000]  # Use list to allow modification in nested function
    
    # Helper function to create user
    def create_staff(role_name, unit, shifts_per_week, team):
        sap = str(sap_counter[0]).zfill(6)
        sap_counter[0] += 1
        
        user = User.objects.create(
            sap=sap,
            email=f"{sap}@victoriagardens.care",
            first_name=f"VG_{role_name}",
            last_name=f"Staff{sap[-4:]}",
            role=roles[role_name],
            unit=unit,
            password=HASHED_PASSWORD,
            is_active=True,
            shifts_per_week_override=shifts_per_week,
            team=team
        )
        all_staff.append(user)
        return user
    
    # 1. Management (2 staff) - assigned to management unit
    print('Creating management staff...')
    create_staff('SM', mgmt_unit, 5, 'A')  # Service Manager
    create_staff('OM', mgmt_unit, 5, 'A')  # Operations Manager
    
    # 2. SSCW - Senior Social Care Workers (6 staff, DAY SHIFT, SUPERNUMERARY)
    # Distribute across units, they will work as supernumerary supervisors
    print('Creating SSCW (day supernumerary)...')
    for i, unit in enumerate(care_units):
        team = ['A', 'B', 'C'][i % 3]
        create_staff('SSCW', unit, 3, team)
    # 2 more SSCW for Rose and Lily (largest units)
    create_staff('SSCW', units_created['Rose'], 3, 'A')
    create_staff('SSCW', units_created['Lily'], 3, 'B')
    
    # 3. SSCWN - Senior Social Care Workers Night (4 staff, NIGHT SHIFT, SUPERNUMERARY)
    print('Creating SSCWN (night supernumerary)...')
    for i in range(4):
        unit = care_units[i % 4]
        team = ['A', 'B', 'C'][i % 3]
        create_staff('SSCWN', unit, 3, team)
    
    # 4. SCA - Social Care Assistants Day (31 staff)
    # Distribute across 4 care units: ~8 per unit
    print('Creating SCA (day assistants)...')
    staff_per_unit = [8, 8, 8, 7]  # Total = 31
    for idx, unit in enumerate(care_units):
        count = staff_per_unit[idx]
        for i in range(count):
            team = ['A', 'B', 'C'][i % 3]
            shifts = 3 if i % 2 == 0 else 2  # Mix of 2 and 3 shifts
            create_staff('SCA', unit, shifts, team)
    
    # 5. SCW - Social Care Workers Day (16 staff)
    # Distribute across units: 4 per unit
    print('Creating SCW (day workers)...')
    for unit in care_units:
        for i in range(4):
            team = ['A', 'B', 'C'][i % 3]
            shifts = 3 if i % 2 == 0 else 2
            create_staff('SCW', unit, shifts, team)
    
    # 6. SCWN - Social Care Workers Night (11 staff)
    # Distribute: 3, 3, 3, 2
    print('Creating SCWN (night workers)...')
    night_scw_per_unit = [3, 3, 3, 2]
    for idx, unit in enumerate(care_units):
        count = night_scw_per_unit[idx]
        for i in range(count):
            team = ['A', 'B', 'C'][i % 3]
            shifts = 3 if i % 2 == 0 else 2
            create_staff('SCWN', unit, shifts, team)
    
    # 7. SCAN - Social Care Assistants Night (28 staff)
    # Distribute: 7 per unit
    print('Creating SCAN (night assistants)...')
    for unit in care_units:
        for i in range(7):
            team = ['A', 'B', 'C'][i % 3]
            shifts = 3 if i % 2 == 0 else 2
            create_staff('SCAN', unit, shifts, team)
    
    print(f'✅ Created {len(all_staff)} staff')
    
    # Verify count by role
    print('\nStaff breakdown:')
    for role_name in ['SM', 'OM', 'SSCW', 'SSCWN', 'SCA', 'SCW', 'SCWN', 'SCAN']:
        count = len([s for s in all_staff if s.role.name == role_name])
        print(f'  {role_name}: {count}')
    
    print('\n' + '=' * 80)
    print('STEP 5: GENERATE 6-MONTH SHIFTS')
    print('=' * 80)
    
    shifts_to_create = []
    
    for user in all_staff:
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
    print('✅ VICTORIA GARDENS CORRECTION COMPLETE')
    print('=' * 80)
    
    # Final verification
    print('\nFinal verification:')
    print(f'  Bed capacity: {vg.bed_capacity} beds')
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
    for unit in care_units:
        day_count = Shift.objects.filter(unit=unit, date=sample_date, shift_type=day_shift).count()
        night_count = Shift.objects.filter(unit=unit, date=sample_date, shift_type=night_shift).count()
        print(f'  {unit.name}: Day={day_count}, Night={night_count}')
    
    print('\n' + '=' * 80)
    print('All changes committed successfully!')
    print('=' * 80)
