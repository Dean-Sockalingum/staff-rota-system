#!/usr/bin/env python3
"""
Import Staff - Minimal Version
Only uses fields that exist in production User model
"""
import os
import sys
import json
import django

sys.path.insert(0, '/home/staff-rota-system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import Unit, Role, User
from django.contrib.auth.hashers import make_password

print("\n" + "="*80)
print("IMPORTING STAFF TO PRODUCTION (MINIMAL FIELDS)")
print("="*80 + "\n")

# Load staff data
with open('/home/staff-rota-system/staff_export_821.json', 'r') as f:
    staff_data = json.load(f)

print(f"Loaded {len(staff_data)} staff records\n")

# Get existing units and roles
units = {unit.name: unit for unit in Unit.objects.all()}
roles = {role.name: role for role in Role.objects.all()}

# Role mapping
role_mapping = {
    'OM': 'Operations Manager',
    'SM': 'Service Manager',
    'SCA': 'Social Care Assistant',
    'SCW': 'Social Care Worker',
    'SSCW': 'Senior Social Care Worker',
    'SCAN': 'Social Care Assistant',
    'SCWN': 'Social Care Worker',
    'SSCWN': 'Senior Social Care Worker',
}

# Import staff by home
homes_to_import = {
    'ORCHARD_GROVE': 180,
    'MEADOWBURN': 179,
    'HAWTHORN_HOUSE': 178,
    'RIVERSIDE': 178,
    'VICTORIA_GARDENS': 98
}

created_count = 0
skipped_count = 0
error_count = 0

for home_name, target_count in homes_to_import.items():
    print(f"\n{home_name}: (target {target_count})")
    
    # Filter staff for this home
    home_staff = [s for s in staff_data if s['care_home'] == home_name and s['sap'] != '000541']
    home_staff = home_staff[:target_count]
    
    for staff in home_staff:
        try:
            # Skip if exists
            if User.objects.filter(sap=staff['sap']).exists():
                skipped_count += 1
                continue
            
            # Get unit
            unit = units.get(staff['unit'])
            if not unit:
                error_count += 1
                continue
            
            # Get role
            role_abbrev = staff['role']
            role_full_name = role_mapping.get(role_abbrev)
            if not role_full_name:
                error_count += 1
                continue
            
            role = roles.get(role_full_name)
            if not role:
                error_count += 1
                continue
            
            # Create user with ONLY fields that exist
            user = User.objects.create(
                sap=staff['sap'],
                first_name=staff['first_name'],
                last_name=staff['last_name'],
                email=staff['email'],
                password=make_password(f"{staff['last_name']}{staff['sap'][-4:]}"),
                role=role,
                home_unit=unit,
                unit=unit,
                team=staff.get('team', 'A'),
                shift_preference=staff.get('shift_preference'),
                is_active=True,
                is_staff=False,
                is_superuser=False
            )
            created_count += 1
            
        except Exception as e:
            print(f"  ❌ Error {staff['sap']}: {str(e)[:100]}")
            error_count += 1
    
    actual_count = User.objects.filter(home_unit__care_home__name=home_name).exclude(sap='000541').count()
    print(f"  ✓ {actual_count} staff in database")

print("\n" + "="*80)
print(f"Created: {created_count} | Skipped: {skipped_count} | Errors: {error_count}")
print(f"Total users: {User.objects.count()}")
print("="*80 + "\n")
