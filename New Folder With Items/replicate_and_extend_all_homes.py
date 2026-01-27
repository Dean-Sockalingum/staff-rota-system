#!/usr/bin/env python
"""
Replicate Orchard Grove staffing to 3 other 120-bed homes and extend all to 6 months.
Also create Victoria Gardens staffing (72 beds, scaled down version).

Homes to populate:
1. Orchard Grove - extend from 3 weeks to 6 months (179 staff already imported)
2. Riverside - replicate OG structure with new SAP numbers (163 staff)
3. Meadowburn - replicate OG structure with new SAP numbers (163 staff)
4. Hawthorn House - replicate OG structure with new SAP numbers (163 staff)
5. Victoria Gardens - scaled down version (98 staff)

Victoria Gardens staffing (from previous implementation):
- 6 SSCW, 4 SSCWN
- 1 SM, 1 OM
- 31 SCA, 16 SCW
- 11 SCWN, 28 SCAN
- Total: 98 staff
"""

import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.contrib.auth.hashers import make_password
from django.db import transaction
from scheduling.models import CareHome, Unit, Role, ShiftType, User, Shift

# Pre-hash password once for performance
HASHED_PASSWORD = make_password('password123')

print('=' * 80)
print('REPLICATING ORCHARD GROVE & EXTENDING ALL HOMES TO 6 MONTHS')
print('=' * 80)
print('\n📋 THIS SCRIPT WILL:')
print('  1. Extend Orchard Grove shifts from 3 weeks to 6 months')
print('  2. Replicate OG staffing to Riverside, Meadowburn, Hawthorn House')
print('  3. Create Victoria Gardens scaled staffing (72 beds)')
print('  4. Generate 6-month rotating shifts for all homes')
print('  5. Total: ~815 staff across 5 homes')
print('\n⚠️  This will take several minutes to complete.\n')

response = input('Proceed? (yes/no): ')
if response.lower() != 'yes':
    print('❌ Operation cancelled')
    exit()

# Start and end dates for 6-month period
START_DATE = datetime(2026, 1, 26).date()  # Today
END_DATE = datetime(2026, 7, 26).date()    # 6 months from today


def generate_shift_dates_6_months(shifts_per_week, team, is_night=False):
    """
    Generate 6-month rotating shift pattern based on shifts per week and team.
    Returns: List of dates for 6 months
    """
    dates = []
    current_date = START_DATE
    
    # 2 shifts/week: Same 2 days each week
    if shifts_per_week == 2:
        team_days = {
            'A': [0, 1],  # Sun, Mon
            'B': [3, 4],  # Wed, Thu
            'C': [5, 6],  # Fri, Sat
        }
        days = team_days.get(team, [0, 1])
        
        while current_date <= END_DATE:
            # Get the weekday (0=Mon, 6=Sun in Python)
            # Convert to our system (0=Sun, 1=Mon, etc.)
            weekday = (current_date.weekday() + 1) % 7
            if weekday in days:
                dates.append(current_date)
            current_date += timedelta(days=1)
    
    # 3 shifts/week: Rotating 3-day pattern over 3 weeks
    elif shifts_per_week == 3:
        patterns = {
            'A': [[0,1,2], [3,4,5], [2,3,4]],  # Team A
            'B': [[3,4,5], [2,3,4], [0,1,2]],  # Team B (offset)
            'C': [[2,3,4], [0,1,2], [3,4,5]],  # Team C (offset)
        }
        pattern = patterns.get(team, [[0,1,2], [3,4,5], [2,3,4]])
        
        week_num = 0
        while current_date <= END_DATE:
            week_pattern = pattern[week_num % 3]
            week_start = current_date
            
            for day_offset in week_pattern:
                check_date = week_start
                for _ in range(7):  # Check each day in the week
                    weekday = (check_date.weekday() + 1) % 7
                    if weekday == day_offset and check_date <= END_DATE:
                        dates.append(check_date)
                    check_date += timedelta(days=1)
            
            current_date += timedelta(days=7)
            week_num += 1
    
    # 5 shifts/week (Management): Monday-Friday every week
    elif shifts_per_week == 5:
        while current_date <= END_DATE:
            weekday = (current_date.weekday() + 1) % 7
            if weekday in [1, 2, 3, 4, 5]:  # Mon-Fri
                dates.append(current_date)
            current_date += timedelta(days=1)
    
    return sorted(list(set(dates)))


# Get references
roles = {role.name: role for role in Role.objects.all()}
shift_types = {st.name: st for st in ShiftType.objects.all()}
day_shift = shift_types['DAY_0800_2000']
night_shift = shift_types['NIGHT_2000_0800']
mgmt_shift = shift_types['MGMT_DAY']

total_users_created = 0
total_shifts_created = 0

with transaction.atomic():
    
    # ========================================================================
    # 1. EXTEND ORCHARD GROVE TO 6 MONTHS
    # ========================================================================
    print('\n' + '=' * 80)
    print('STEP 1: EXTENDING ORCHARD GROVE TO 6 MONTHS')
    print('=' * 80)
    
    orchard_grove = CareHome.objects.get(name='ORCHARD_GROVE')
    og_users = User.objects.filter(unit__care_home=orchard_grove)
    
    print(f'\n📊 Found {og_users.count()} existing Orchard Grove staff')
    print(f'   Deleting existing {Shift.objects.filter(user__unit__care_home=orchard_grove).count()} shifts...')
    
    # Delete existing OG shifts (will regenerate for 6 months)
    Shift.objects.filter(user__unit__care_home=orchard_grove).delete()
    
    print('   Generating 6-month shifts for all staff...')
    og_shifts = 0
    
    for user in og_users:
        # Determine shift type based on role
        if user.role.name in ['SCWN', 'SCAN', 'SSCWN']:
            shift_type = night_shift
            is_night = True
        elif user.role.name in ['SM', 'OM']:
            shift_type = mgmt_shift
            is_night = False
        else:
            shift_type = day_shift
            is_night = False
        
        # Get shifts per week (use override if set, else default by role)
        if user.shifts_per_week_override:
            shifts_per_week = user.shifts_per_week_override
        elif user.role.name in ['SM', 'OM']:
            shifts_per_week = 5
        elif user.role.name in ['SSCW', 'SSCWN']:
            shifts_per_week = 3
        else:
            # For SCW, SCA, SCWN, SCAN - vary between 2 and 3
            shifts_per_week = 2 if int(user.sap) % 2 == 0 else 3
        
        # Determine team (A, B, or C) - distribute evenly
        team = ['A', 'B', 'C'][int(user.sap) % 3]
        
        # Generate shift dates
        shift_dates = generate_shift_dates_6_months(shifts_per_week, team, is_night)
        
        # Create shifts
        for date in shift_dates:
            Shift.objects.create(
                user=user,
                unit=user.unit,
                shift_type=shift_type,
                date=date,
                status='SCHEDULED'
            )
            og_shifts += 1
    
    total_shifts_created += og_shifts
    print(f'   ✅ Orchard Grove: {og_users.count()} staff, {og_shifts} shifts (6 months)')
    
    
    # ========================================================================
    # 2. REPLICATE TO RIVERSIDE, MEADOWBURN, HAWTHORN HOUSE
    # ========================================================================
    print('\n' + '=' * 80)
    print('STEP 2: REPLICATING TO 3 OTHER 120-BED HOMES')
    print('=' * 80)
    
    replication_homes = [
        {'name': 'RIVERSIDE', 'sap_start': 100000},
        {'name': 'MEADOWBURN', 'sap_start': 200000},
        {'name': 'HAWTHORN_HOUSE', 'sap_start': 300000},
    ]
    
    for home_info in replication_homes:
        print(f'\n📥 Creating {home_info["name"]} staff...')
        
        home = CareHome.objects.get(name=home_info['name'])
        sap_counter = home_info['sap_start']
        home_users = 0
        home_shifts = 0
        
        # Delete any existing users and shifts for this home
        Shift.objects.filter(user__unit__care_home=home).delete()
        User.objects.filter(unit__care_home=home).delete()
        
        # Replicate each Orchard Grove user
        for og_user in og_users:
            # Create corresponding unit name
            og_unit_name = og_user.unit.name
            new_unit_name = og_unit_name.replace('ORCHARD_GROVE', home_info['name'])
            new_unit = Unit.objects.get(name=new_unit_name, care_home=home)
            
            # Create new user with incremented SAP
            new_sap = str(sap_counter).zfill(6)
            # Clean home name for email (remove underscores)
            email_domain = home_info['name'].lower().replace('_', '')
            new_user = User.objects.create(
                sap=new_sap,
                first_name=og_user.first_name,
                last_name=f"{og_user.last_name} ({home_info['name'][:2]})",
                email=f"{new_sap}@{email_domain}.care",
                password=HASHED_PASSWORD,
                role=og_user.role,
                unit=new_unit,
                is_active=True,
                shifts_per_week_override=og_user.shifts_per_week_override,
            )
            sap_counter += 1
            home_users += 1
            
            # Determine shift type and shifts per week (same logic as OG)
            if new_user.role.name in ['SCWN', 'SCAN', 'SSCWN']:
                shift_type = night_shift
                is_night = True
            elif new_user.role.name in ['SM', 'OM']:
                shift_type = mgmt_shift
                is_night = False
            else:
                shift_type = day_shift
                is_night = False
            
            if new_user.shifts_per_week_override:
                shifts_per_week = new_user.shifts_per_week_override
            elif new_user.role.name in ['SM', 'OM']:
                shifts_per_week = 5
            elif new_user.role.name in ['SSCW', 'SSCWN']:
                shifts_per_week = 3
            else:
                shifts_per_week = 2 if int(new_user.sap) % 2 == 0 else 3
            
            team = ['A', 'B', 'C'][int(new_user.sap) % 3]
            
            # Generate 6-month shifts
            shift_dates = generate_shift_dates_6_months(shifts_per_week, team, is_night)
            
            for date in shift_dates:
                Shift.objects.create(
                    user=new_user,
                    unit=new_unit,
                    shift_type=shift_type,
                    date=date,
                    status='SCHEDULED'
                )
                home_shifts += 1
        
        total_users_created += home_users
        total_shifts_created += home_shifts
        print(f'   ✅ {home_info["name"]}: {home_users} staff, {home_shifts} shifts (6 months)')
    
    
    # ========================================================================
    # 3. CREATE VICTORIA GARDENS (72 BEDS, SCALED DOWN)
    # ========================================================================
    print('\n' + '=' * 80)
    print('STEP 3: CREATING VICTORIA GARDENS (SCALED 72-BED HOME)')
    print('=' * 80)
    
    victoria = CareHome.objects.get(name='VICTORIA_GARDENS')
    vg_sap_start = 400000
    vg_users = 0
    vg_shifts = 0
    
    # Delete any existing VG users and shifts
    Shift.objects.filter(user__unit__care_home=victoria).delete()
    User.objects.filter(unit__care_home=victoria).delete()
    
    # Create VG units if they don't exist (smaller home - 4 care units + 1 mgmt)
    if Unit.objects.filter(care_home=victoria).count() == 0:
        print('   Creating Victoria Gardens units...')
        vg_unit_names = ['Rose', 'Lily', 'Daisy', 'Tulip', 'Mgmt']
        for unit_name in vg_unit_names:
            Unit.objects.create(
                care_home=victoria,
                name=f'VICTORIA_GARDENS_{unit_name}',
                description=f'{unit_name} Unit at Victoria Gardens',
                is_active=True
            )
        print(f'   ✅ Created {len(vg_unit_names)} units for Victoria Gardens')
    
    # Victoria Gardens has fewer units (estimate 4-5 care units vs OG's 8)
    # Get VG units
    vg_units = list(Unit.objects.filter(care_home=victoria).exclude(name__contains='Mgmt'))
    vg_mgmt_unit = Unit.objects.get(name__contains='Mgmt', care_home=victoria)
    
    print(f'\n   Victoria Gardens has {len(vg_units)} care units')
    
    # Victoria Gardens staffing breakdown (from doc):
    # - 6 SSCW, 4 SSCWN (managers)
    # - 1 SM, 1 OM (management)
    # - 31 SCA, 16 SCW (day staff)
    # - 11 SCWN, 28 SCAN (night staff)
    
    # Create management staff
    print('   Creating management staff...')
    mgmt_staff = [
        {'role': 'SM', 'shifts_per_week': 5},
        {'role': 'OM', 'shifts_per_week': 5},
    ]
    
    for staff_data in mgmt_staff:
        user = User.objects.create(
            sap=str(vg_sap_start).zfill(6),
            first_name='VG',
            last_name=f'{staff_data["role"]} {vg_sap_start}',
            email=f'{vg_sap_start}@victoriagardens.care',
            password=HASHED_PASSWORD,
            role=roles[staff_data['role']],
            unit=vg_mgmt_unit,
            is_active=True,
        )
        vg_sap_start += 1
        vg_users += 1
        
        # Generate shifts
        shift_dates = generate_shift_dates_6_months(staff_data['shifts_per_week'], 'A')
        for date in shift_dates:
            Shift.objects.create(
                user=user,
                unit=vg_mgmt_unit,
                shift_type=mgmt_shift,
                date=date,
                status='SCHEDULED'
            )
            vg_shifts += 1
    
    # Create unit staff (distribute across available units)
    print('   Creating unit staff...')
    
    # SSCW managers (6 day managers distributed across units)
    for i in range(min(6, len(vg_units))):
        unit = vg_units[i % len(vg_units)]
        user = User.objects.create(
            sap=str(vg_sap_start).zfill(6),
            first_name='VG',
            last_name=f'SSCW Mgr {vg_sap_start}',
            email=f'{vg_sap_start}@victoriagardens.care',
            password=HASHED_PASSWORD,
            role=roles['SSCW'],
            unit=unit,
            is_active=True,
        )
        vg_sap_start += 1
        vg_users += 1
        
        shift_dates = generate_shift_dates_6_months(3, 'A')
        for date in shift_dates:
            Shift.objects.create(
                user=user,
                unit=unit,
                shift_type=day_shift,
                date=date,
                status='SCHEDULED'
            )
            vg_shifts += 1
    
    # SSCWN managers (4 night managers)
    for i in range(min(4, len(vg_units))):
        unit = vg_units[i % len(vg_units)]
        user = User.objects.create(
            sap=str(vg_sap_start).zfill(6),
            first_name='VG',
            last_name=f'SSCWN Mgr {vg_sap_start}',
            email=f'{vg_sap_start}@victoriagardens.care',
            password=HASHED_PASSWORD,
            role=roles['SSCWN'],
            unit=unit,
            is_active=True,
        )
        vg_sap_start += 1
        vg_users += 1
        
        shift_dates = generate_shift_dates_6_months(3, 'A', is_night=True)
        for date in shift_dates:
            Shift.objects.create(
                user=user,
                unit=unit,
                shift_type=night_shift,
                date=date,
                status='SCHEDULED'
            )
            vg_shifts += 1
    
    # Day staff: 31 SCA + 16 SCW = 47 day staff
    day_staff_roles = [
        {'role': 'SCA', 'count': 31},
        {'role': 'SCW', 'count': 16},
    ]
    
    for role_data in day_staff_roles:
        for i in range(role_data['count']):
            unit = vg_units[i % len(vg_units)]
            team = ['A', 'B', 'C'][i % 3]
            shifts_per_week = 2 if i % 2 == 0 else 3
            
            user = User.objects.create(
                sap=str(vg_sap_start).zfill(6),
                first_name='VG',
                last_name=f'{role_data["role"]} {vg_sap_start}',
                email=f'{vg_sap_start}@victoriagardens.care',
                password=HASHED_PASSWORD,
                role=roles[role_data['role']],
                unit=unit,
                is_active=True,
            )
            vg_sap_start += 1
            vg_users += 1
            
            shift_dates = generate_shift_dates_6_months(shifts_per_week, team)
            for date in shift_dates:
                Shift.objects.create(
                    user=user,
                    unit=unit,
                    shift_type=day_shift,
                    date=date,
                    status='SCHEDULED'
                )
                vg_shifts += 1
    
    # Night staff: 28 SCAN + 11 SCWN = 39 night staff
    night_staff_roles = [
        {'role': 'SCAN', 'count': 28},
        {'role': 'SCWN', 'count': 11},
    ]
    
    for role_data in night_staff_roles:
        for i in range(role_data['count']):
            unit = vg_units[i % len(vg_units)]
            team = ['A', 'B', 'C'][i % 3]
            shifts_per_week = 2 if i % 2 == 0 else 3
            
            user = User.objects.create(
                sap=str(vg_sap_start).zfill(6),
                first_name='VG',
                last_name=f'{role_data["role"]} {vg_sap_start}',
                email=f'{vg_sap_start}@victoriagardens.care',
                password=HASHED_PASSWORD,
                role=roles[role_data['role']],
                unit=unit,
                is_active=True,
            )
            vg_sap_start += 1
            vg_users += 1
            
            shift_dates = generate_shift_dates_6_months(shifts_per_week, team, is_night=True)
            for date in shift_dates:
                Shift.objects.create(
                    user=user,
                    unit=unit,
                    shift_type=night_shift,
                    date=date,
                    status='SCHEDULED'
                )
                vg_shifts += 1
    
    total_users_created += vg_users
    total_shifts_created += vg_shifts
    print(f'   ✅ Victoria Gardens: {vg_users} staff, {vg_shifts} shifts (6 months)')


print('\n' + '=' * 80)
print('✅ COMPLETE: ALL HOMES POPULATED WITH 6-MONTH ROTAS')
print('=' * 80)

# Final verification
print('\n📊 FINAL SUMMARY:')
for home in CareHome.objects.all():
    staff_count = User.objects.filter(unit__care_home=home).count()
    shift_count = Shift.objects.filter(user__unit__care_home=home).count()
    print(f'   {home.name:20s}: {staff_count:3d} staff, {shift_count:6,d} shifts')

print(f'\n   NEW STAFF CREATED: {total_users_created}')
print(f'   NEW SHIFTS CREATED: {total_shifts_created:,}')
print(f'   TOTAL STAFF: {User.objects.count()}')
print(f'   TOTAL SHIFTS: {Shift.objects.count():,}')
print(f'\n   Date Range: {START_DATE} to {END_DATE}')

print('\n' + '=' * 80)
print('✅ ALL HOMES NOW HAVE 6-MONTH ROTAS')
print('=' * 80)
