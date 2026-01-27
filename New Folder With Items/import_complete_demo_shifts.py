#!/usr/bin/env python3
"""
Import complete demo data with all staff and shift allocations from production
Source: complete_demo_export.json (exported from https://demo.therota.co.uk/rota/)
"""
import os
import django
import json
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import CareHome, Unit, Role, ShiftType, User, Shift
from django.contrib.auth.hashers import make_password

print('=' * 80)
print('IMPORTING COMPLETE DEMO DATA WITH SHIFTS')
print('=' * 80)

# Load the complete demo export
print('\n📂 Loading complete_demo_export.json...')
with open('complete_demo_export.json', 'r') as f:
    data = json.load(f)

# Count records
models = {}
for item in data:
    model = item.get('model', 'unknown')
    models[model] = models.get(model, 0) + 1

print('\n📊 DATA TO IMPORT:')
for model, count in sorted(models.items()):
    print(f'  • {model}: {count:,} records')

# Confirm import
print('\n⚠️  WARNING: This will clear existing data and import all production data.')
response = input('Continue? (yes/no): ')
if response.lower() != 'yes':
    print('❌ Import cancelled')
    exit()

# Clear existing data
print('\n🗑️  Clearing existing data...')
Shift.objects.all().delete()
User.objects.all().delete()
Unit.objects.all().delete()
ShiftType.objects.all().delete()
Role.objects.all().delete()
CareHome.objects.all().delete()
print('✅ Existing data cleared')

# Import in order of dependencies
print('\n📥 IMPORTING DATA...\n')

# 1. Care Homes
print('1️⃣  Importing Care Homes...')
homes_data = [d for d in data if d.get('model') == 'scheduling.carehome']
home_map = {}
for item in homes_data:
    pk = item['pk']
    fields = item['fields']
    home = CareHome.objects.create(
        id=pk,
        name=fields['name'],
        bed_capacity=fields.get('bed_capacity', 0),
        current_occupancy=fields.get('current_occupancy', 0),
        location_address=fields.get('location_address', ''),
        postcode=fields.get('postcode', ''),
        care_inspectorate_id=fields.get('care_inspectorate_id', ''),
        registration_number=fields.get('registration_number', ''),
        main_phone=fields.get('main_phone', ''),
        main_email=fields.get('main_email', ''),
        is_active=fields.get('is_active', True)
    )
    home_map[pk] = home
print(f'✅ Imported {len(home_map)} care homes')

# 2. Units
print('2️⃣  Importing Units...')
units_data = [d for d in data if d.get('model') == 'scheduling.unit']
unit_map = {}
for item in units_data:
    pk = item['pk']
    fields = item['fields']
    unit = Unit.objects.create(
        id=pk,
        care_home=home_map[fields['care_home']],
        name=fields['name'],
        description=fields.get('description', ''),
        is_active=fields.get('is_active', True)
    )
    unit_map[pk] = unit
print(f'✅ Imported {len(unit_map)} units')

# 3. Roles
print('3️⃣  Importing Roles...')
roles_data = [d for d in data if d.get('model') == 'scheduling.role']
role_map = {}
for item in roles_data:
    pk = item['pk']
    fields = item['fields']
    role = Role.objects.create(
        id=pk,
        name=fields['name'],
        description=fields.get('description', ''),
        is_management=fields.get('is_management', False),
        is_senior_management_team=fields.get('is_senior_management_team', False),
        can_approve_leave=fields.get('can_approve_leave', False),
        can_manage_rota=fields.get('can_manage_rota', False)
    )
    role_map[pk] = role
print(f'✅ Imported {len(role_map)} roles')

# 4. Shift Types
print('4️⃣  Importing Shift Types...')
shift_types_data = [d for d in data if d.get('model') == 'scheduling.shifttype']
shift_type_map = {}
for item in shift_types_data:
    pk = item['pk']
    fields = item['fields']
    shift_type = ShiftType.objects.create(
        id=pk,
        name=fields['name'],
        start_time=fields.get('start_time'),
        end_time=fields.get('end_time'),
        duration_hours=fields.get('duration_hours', 12.0),
        color_code=fields.get('color_code', '#007bff'),
        is_active=fields.get('is_active', True)
    )
    shift_type_map[pk] = shift_type
print(f'✅ Imported {len(shift_type_map)} shift types')

# 5. Users (Staff)
print('5️⃣  Importing Staff (Users)...')
users_data = [d for d in data if d.get('model') == 'scheduling.user']
user_map = {}
for i, item in enumerate(users_data, 1):
    pk = item['pk']
    fields = item['fields']
    
    # Get unit (some users may not have units)
    unit = None
    if fields.get('unit'):
        unit = unit_map.get(fields['unit'])
    
    # Get role
    role = None
    if fields.get('role'):
        role = role_map.get(fields['role'])
    
    # Fix email - replace underscores and ensure valid format
    email = fields.get('email', f'{pk}@example.com')
    if '_' in email or '@' not in email:
        email = f'{pk}@example.com'
    
    user = User.objects.create(
        sap=pk,
        email=email,
        first_name=fields.get('first_name', ''),
        last_name=fields.get('last_name', ''),
        password=make_password('password123'),  # Default password
        unit=unit,
        role=role,
        is_active=fields.get('is_active', True),
        is_staff=fields.get('is_staff', False),
        is_superuser=fields.get('is_superuser', False)
    )
    user_map[pk] = user
    
    if i % 500 == 0:
        print(f'  Progress: {i}/{len(users_data)} staff imported...')

print(f'✅ Imported {len(user_map)} staff members')

# 6. Shifts
print('6️⃣  Importing Shifts (this may take a while)...')
shifts_data = [d for d in data if d.get('model') == 'scheduling.shift']
print(f'  Total shifts to import: {len(shifts_data):,}')

shifts_to_create = []
batch_size = 1000

for i, item in enumerate(shifts_data, 1):
    fields = item['fields']
    
    # Get user
    user = user_map.get(fields['user'])
    if not user:
        continue  # Skip if user not found
    
    # Get unit
    unit = unit_map.get(fields['unit'])
    if not unit:
        continue  # Skip if unit not found
    
    # Get shift type
    shift_type = shift_type_map.get(fields['shift_type'])
    if not shift_type:
        continue  # Skip if shift type not found
    
    shift = Shift(
        user=user,
        unit=unit,
        shift_type=shift_type,
        date=fields['date'],
        status=fields.get('status', 'SCHEDULED'),
        shift_classification=fields.get('shift_classification', 'REGULAR'),
        shift_pattern=fields.get('shift_pattern', 'DAY_0800_2000'),
        custom_start_time=fields.get('custom_start_time'),
        custom_end_time=fields.get('custom_end_time'),
        agency_company=fields.get('agency_company'),
        agency_staff_name=fields.get('agency_staff_name', ''),
        agency_hourly_rate=fields.get('agency_hourly_rate'),
        notes=fields.get('notes')
    )
    
    shifts_to_create.append(shift)
    
    # Bulk create in batches
    if len(shifts_to_create) >= batch_size:
        Shift.objects.bulk_create(shifts_to_create)
        print(f'  Progress: {i:,}/{len(shifts_data):,} shifts imported... ({i/len(shifts_data)*100:.1f}%)')
        shifts_to_create = []

# Create remaining shifts
if shifts_to_create:
    Shift.objects.bulk_create(shifts_to_create)

print(f'✅ Imported {Shift.objects.count():,} shifts')

# Summary
print('\n' + '=' * 80)
print('✅ IMPORT COMPLETE!')
print('=' * 80)
print('\n📊 FINAL DATABASE STATE:')
print(f'  • Care Homes: {CareHome.objects.count()}')
print(f'  • Units: {Unit.objects.count()}')
print(f'  • Roles: {Role.objects.count()}')
print(f'  • Shift Types: {ShiftType.objects.count()}')
print(f'  • Staff (Users): {User.objects.count():,}')
print(f'  • Shifts: {Shift.objects.count():,}')

# Show Orchard Grove stats
print('\n🍊 ORCHARD GROVE STATS:')
og_home = CareHome.objects.filter(name='ORCHARD_GROVE').first()
if og_home:
    og_staff = User.objects.filter(unit__care_home=og_home)
    og_shifts = Shift.objects.filter(user__unit__care_home=og_home)
    print(f'  • Staff: {og_staff.count()}')
    print(f'  • Shifts: {og_shifts.count():,}')
    print(f'  • Units: {og_home.units.count()}')
    
    print('\n  Units:')
    for unit in og_home.units.all().order_by('name'):
        unit_staff = User.objects.filter(unit=unit).count()
        unit_shifts = Shift.objects.filter(unit=unit).count()
        print(f'    • {unit.name}: {unit_staff} staff, {unit_shifts:,} shifts')

print('\n✅ All production data has been imported!')
print('🔑 Default password for all users: password123')
print('🌐 You can now run the server and view the complete rotas')
