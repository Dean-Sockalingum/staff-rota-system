#!/usr/bin/env python3
"""
Fast import of complete demo data - uses bulk operations for speed
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import CareHome, Unit, Role, ShiftType, User, Shift
from django.contrib.auth.hashers import make_password
from django.db import transaction

print('='*80)
print('FAST IMPORT OF PRODUCTION DATA')
print('='*80)

# Load data
print('\n📂 Loading complete_demo_export.json...')
with open('complete_demo_export.json', 'r') as f:
    data = json.load(f)

# Separate by model type
homes_data = [d for d in data if d.get('model') == 'scheduling.carehome']
units_data = [d for d in data if d.get('model') == 'scheduling.unit']
roles_data = [d for d in data if d.get('model') == 'scheduling.role']
shift_types_data = [d for d in data if d.get('model') == 'scheduling.shifttype']
users_data = [d for d in data if d.get('model') == 'scheduling.user']
shifts_data = [d for d in data if d.get('model') == 'scheduling.shift']

print(f'\n📊 Data loaded:')
print(f'  • Care Homes: {len(homes_data)}')
print(f'  • Units: {len(units_data)}')
print(f'  • Roles: {len(roles_data)}')
print(f'  • Shift Types: {len(shift_types_data)}')
print(f'  • Users: {len(users_data):,}')
print(f'  • Shifts: {len(shifts_data):,}')

response = input('\n⚠️  Clear existing data and import? (yes/no): ')
if response.lower() != 'yes':
    print('❌ Import cancelled')
    exit()

print('\n🗑️  Clearing existing data...')
with transaction.atomic():
    Shift.objects.all().delete()
    User.objects.all().delete()
    Unit.objects.all().delete()
    ShiftType.objects.all().delete()
    Role.objects.all().delete()
    CareHome.objects.all().delete()
print('✅ Data cleared')

print('\n📥 Importing with bulk operations...\n')

# 1. Care Homes
print('1️⃣  Care Homes...')
homes_to_create = []
for item in homes_data:
    fields = item['fields']
    homes_to_create.append(CareHome(
        id=item['pk'],
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
    ))
CareHome.objects.bulk_create(homes_to_create)
home_map = {h.id: h for h in CareHome.objects.all()}
print(f'✅ {len(home_map)} care homes')

# 2. Units
print('2️⃣  Units...')
units_to_create = []
for item in units_data:
    fields = item['fields']
    units_to_create.append(Unit(
        id=item['pk'],
        care_home=home_map[fields['care_home']],
        name=fields['name'],
        description=fields.get('description', ''),
        is_active=fields.get('is_active', True)
    ))
Unit.objects.bulk_create(units_to_create)
unit_map = {u.id: u for u in Unit.objects.all()}
print(f'✅ {len(unit_map)} units')

# 3. Roles
print('3️⃣  Roles...')
roles_to_create = []
for item in roles_data:
    fields = item['fields']
    roles_to_create.append(Role(
        id=item['pk'],
        name=fields['name'],
        description=fields.get('description', ''),
        is_management=fields.get('is_management', False),
        is_senior_management_team=fields.get('is_senior_management_team', False),
        can_approve_leave=fields.get('can_approve_leave', False),
        can_manage_rota=fields.get('can_manage_rota', False)
    ))
Role.objects.bulk_create(roles_to_create)
role_map = {r.id: r for r in Role.objects.all()}
print(f'✅ {len(role_map)} roles')

# 4. Shift Types
print('4️⃣  Shift Types...')
shift_types_to_create = []
for item in shift_types_data:
    fields = item['fields']
    shift_types_to_create.append(ShiftType(
        id=item['pk'],
        name=fields['name'],
        start_time=fields.get('start_time'),
        end_time=fields.get('end_time'),
        duration_hours=fields.get('duration_hours', 12.0),
        color_code=fields.get('color_code', '#007bff'),
        is_active=fields.get('is_active', True)
    ))
ShiftType.objects.bulk_create(shift_types_to_create)
shift_type_map = {st.id: st for st in ShiftType.objects.all()}
print(f'✅ {len(shift_type_map)} shift types')

# 5. Users - in batches
print(f'5️⃣  Users ({len(users_data):,} total)...')
users_to_create = []
batch_size = 500

for i, item in enumerate(users_data, 1):
    pk = item['pk']
    fields = item['fields']
    
    unit = unit_map.get(fields.get('unit')) if fields.get('unit') else None
    role = role_map.get(fields.get('role')) if fields.get('role') else None
    
    # Fix email
    email = fields.get('email', f'{pk}@example.com')
    if '_' in email or '@' not in email:
        email = f'{pk}@example.com'
    
    users_to_create.append(User(
        sap=pk,
        email=email,
        first_name=fields.get('first_name', ''),
        last_name=fields.get('last_name', ''),
        password=make_password('password123'),
        unit=unit,
        role=role,
        is_active=fields.get('is_active', True),
        is_staff=fields.get('is_staff', False),
        is_superuser=fields.get('is_superuser', False)
    ))
    
    if len(users_to_create) >= batch_size:
        User.objects.bulk_create(users_to_create, ignore_conflicts=True)
        print(f'  Progress: {i:,}/{len(users_data):,} ({i/len(users_data)*100:.1f}%)')
        users_to_create = []

if users_to_create:
    User.objects.bulk_create(users_to_create, ignore_conflicts=True)

user_map = {u.sap: u for u in User.objects.all()}
print(f'✅ {len(user_map):,} users')

# 6. Shifts - in batches
print(f'6️⃣  Shifts ({len(shifts_data):,} total - this will take a few minutes)...')
shifts_to_create = []
batch_size = 5000
skipped = 0

for i, item in enumerate(shifts_data, 1):
    fields = item['fields']
    
    user = user_map.get(fields['user'])
    unit = unit_map.get(fields['unit'])
    shift_type = shift_type_map.get(fields['shift_type'])
    
    if not user or not unit or not shift_type:
        skipped += 1
        continue
    
    shifts_to_create.append(Shift(
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
    ))
    
    if len(shifts_to_create) >= batch_size:
        Shift.objects.bulk_create(shifts_to_create, ignore_conflicts=True)
        print(f'  Progress: {i:,}/{len(shifts_data):,} ({i/len(shifts_data)*100:.1f}%)')
        shifts_to_create = []

if shifts_to_create:
    Shift.objects.bulk_create(shifts_to_create, ignore_conflicts=True)

print(f'✅ {Shift.objects.count():,} shifts (skipped {skipped} invalid)')

# Summary
print('\n' + '='*80)
print('✅ IMPORT COMPLETE!')
print('='*80)
print(f'\n📊 DATABASE:')
print(f'  • Care Homes: {CareHome.objects.count()}')
print(f'  • Units: {Unit.objects.count()}')
print(f'  • Roles: {Role.objects.count()}')
print(f'  • Shift Types: {ShiftType.objects.count()}')
print(f'  • Users: {User.objects.count():,}')
print(f'  • Shifts: {Shift.objects.count():,}')

# Orchard Grove stats
print('\n🍊 ORCHARD GROVE:')
og_home = CareHome.objects.filter(name='ORCHARD_GROVE').first()
if og_home:
    og_staff = User.objects.filter(unit__care_home=og_home)
    og_shifts = Shift.objects.filter(user__unit__care_home=og_home)
    print(f'  • Staff: {og_staff.count()}')
    print(f'  • Shifts: {og_shifts.count():,}')
    print(f'  • Units: {og_home.units.count()}')
    
print('\n✅ All production data imported!')
print('🔑 Password for all users: password123')
