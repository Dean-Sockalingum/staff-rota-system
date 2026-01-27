#!/usr/bin/env python3
"""
Complete Production Setup from Local Demo
Imports: Homes, Units, Roles, Shift Types, and Staff
"""
import os
import sys
import django

sys.path.insert(0, '/home/staff-rota-system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import CareHome, Unit, Role, ShiftType, User
from django.contrib.auth.hashers import make_password
from datetime import time

print("\n" + "="*80)
print("COMPLETE PRODUCTION SETUP FROM DEMO DATA")
print("="*80 + "\n")

# Step 1: Create Care Homes
print("Step 1: Creating Care Homes...")
homes_data = [
    {
        'name': 'HAWTHORN_HOUSE',
        'bed_capacity': 120,
        'location_address': 'Glasgow',
        'care_inspectorate_id': 'CS2003001025',
    },
    {
        'name': 'MEADOWBURN',
        'bed_capacity': 120,
        'location_address': 'Glasgow',
        'care_inspectorate_id': 'CS2018371804',
    },
    {
        'name': 'ORCHARD_GROVE',
        'bed_capacity': 120,
        'location_address': 'Maryhill, Glasgow',
        'care_inspectorate_id': 'CS2014333831',
    },
    {
        'name': 'RIVERSIDE',
        'bed_capacity': 120,
        'location_address': 'Govan, Glasgow',
        'care_inspectorate_id': 'CS2014333834',
    },
    {
        'name': 'VICTORIA_GARDENS',
        'bed_capacity': 70,
        'location_address': 'Partick, Glasgow',
        'care_inspectorate_id': 'CS2018371437',
    },
]

home_map = {}
for home_data in homes_data:
    home, created = CareHome.objects.get_or_create(
        name=home_data['name'],
        defaults=home_data
    )
    home_map[home.name] = home
    print(f"  {'✓ Created' if created else '✓ Exists'}: {home.name}")

print(f"\nTotal homes: {CareHome.objects.count()}\n")

# Step 2: Create Units for each home
print("Step 2: Creating Units...")

# Orchard Grove units (from local demo)
og_units = ['OG_BRAMLEY', 'OG_CHERRY', 'OG_GRAPE', 'OG_ORANGE', 'OG_PEACH', 'OG_PEAR', 'OG_PLUM', 'OG_STRAWBERRY', 'OG_MGMT']
mb_units = ['MB_ASTER', 'MB_CORNFLOWER', 'MB_FOXGLOVE', 'MB_HONEYSUCKLE', 'MB_BLUEBELL', 'MB_DAISY', 'MB_MGMT', 'MB_MARIGOLD', 'MB_POPPY_SRD']
hh_units = ['HH_BLUEBELL', 'HH_DAISY', 'HH_HEATHER', 'HH_IRIS', 'HH_PRIMROSE', 'HH_SNOWDROP_SRD', 'HH_THISTLE_SRD', 'HH_VIOLET', 'HH_MGMT']
rs_units = ['RS_DAFFODIL', 'RS_HEATHER', 'RS_JASMINE', 'RS_LILY', 'RS_LOTUS', 'RS_MAPLE', 'RS_ORCHID', 'RS_ROSE', 'RS_MGMT']
vg_units = ['VG_AZALEA', 'VG_CROCUS', 'VG_TULIP', 'VG_LILY', 'VG_ROSE', 'VG_MGMT']

unit_map = {}
units_config = [
    ('ORCHARD_GROVE', og_units),
    ('MEADOWBURN', mb_units),
    ('HAWTHORN_HOUSE', hh_units),
    ('RIVERSIDE', rs_units),
    ('VICTORIA_GARDENS', vg_units),
]

for home_name, units in units_config:
    home = home_map[home_name]
    for unit_name in units:
        unit, created = Unit.objects.get_or_create(
            name=unit_name,
            care_home=home,
            defaults={'is_active': True}
        )
        unit_map[unit_name] = unit
        if created:
            print(f"  ✓ {home_name}: {unit_name}")

print(f"\nTotal units: {Unit.objects.count()}\n")

# Step 3: Create Roles
print("Step 3: Creating Roles...")
roles_data = [
    {'name': 'Operations Manager', 'OM': 'OM', 'is_management': True, 'can_approve_leave': True, 'can_manage_rota': True},
    {'name': 'Service Manager', 'SM': 'SM', 'is_management': True, 'can_approve_leave': True, 'can_manage_rota': True},
    {'name': 'Social Care Assistant', 'SCA': 'SCA', 'is_management': False},
    {'name': 'Social Care Worker', 'SCW': 'SCW', 'is_management': False},
    {'name': 'Senior Social Care Worker', 'SSCW': 'SSCW', 'is_management': False},
]

role_map = {}
for role_data in roles_data:
    abbrev = role_data.pop('OM', role_data.pop('SM', role_data.pop('SCA', role_data.pop('SCW', role_data.pop('SSCW', None)))))
    role, created = Role.objects.get_or_create(name=role_data['name'], defaults=role_data)
    role_map[abbrev] = role
    print(f"  {'✓ Created' if created else '✓ Exists'}: {role.name}")

print(f"\nTotal roles: {Role.objects.count()}\n")

# Step 4: Create Shift Types
print("Step 4: Creating Shift Types...")
shift_types_data = [
    {'name': 'Day Shift', 'start_time': time(8, 0), 'end_time': time(20, 0), 'duration_hours': 12.0},
    {'name': 'Night Shift', 'start_time': time(20, 0), 'end_time': time(8, 0), 'duration_hours': 12.0},
    {'name': 'Management', 'start_time': time(9, 0), 'end_time': time(17, 0), 'duration_hours': 8.0},
]

for st_data in shift_types_data:
    st, created = ShiftType.objects.get_or_create(name=st_data['name'], defaults=st_data)
    print(f"  {'✓ Created' if created else '✓ Exists'}: {st.name}")

print(f"\nTotal shift types: {ShiftType.objects.count()}\n")

# Step 5: Create Admin User
print("Step 5: Creating Admin User...")
admin, created = User.objects.get_or_create(
    sap='000541',
    defaults={
        'first_name': 'System',
        'last_name': 'Administrator',
        'email': 'admin@facility.com',
        'is_superuser': True,
        'is_staff': True,
        'is_active': True,
        'password': make_password('Greenball99##')
    }
)
if created:
    print(f"  ✓ Created admin user: {admin.sap}")
else:
    admin.password = make_password('Greenball99##')
    admin.save()
    print(f"  ✓ Reset password for admin: {admin.sap}")

print("\n" + "="*80)
print("SETUP COMPLETE!")
print("="*80)
print(f"\n  Homes: {CareHome.objects.count()}")
print(f"  Units: {Unit.objects.count()}")
print(f"  Roles: {Role.objects.count()}")
print(f"  Shift Types: {ShiftType.objects.count()}")
print(f"  Users: {User.objects.count()}")
print(f"\n  Admin Login:")
print(f"    SAP: 000541")
print(f"    Password: Greenball99##")
print(f"\n✅ Production database is ready for staff import!\n")
