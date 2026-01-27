#!/usr/bin/env python3
"""
Import Staff from JSON Export to Production Database
Updated to match production schema
"""
import os
import sys
import json
import django

sys.path.insert(0, '/home/staff-rota-system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import CareHome, Unit, Role, User
from django.contrib.auth.hashers import make_password

print("\n" + "="*80)
print("IMPORTING STAFF TO PRODUCTION")
print("="*80 + "\n")

# Load staff data
with open('/home/staff-rota-system/staff_export_821.json', 'r') as f:
    staff_data = json.load(f)

print(f"Loaded {len(staff_data)} staff records from export\n")

# Get existing units and roles
units = {unit.name: unit for unit in Unit.objects.all()}
roles = {role.name: role for role in Role.objects.all()}

# Create role mapping from abbreviations to full names
role_mapping = {
    'OM': 'Operations Manager',
    'SM': 'Service Manager',
    'SCA': 'Social Care Assistant',
    'SCW': 'Social Care Worker',
    'SSCW': 'Senior Social Care Worker',
    'SCAN': 'Social Care Assistant',  # Night variant - map to SCA
    'SCWN': 'Social Care Worker',     # Night variant - map to SCW
    'SSCWN': 'Senior Social Care Worker',  # Night variant - map to SSCW
}

print(f"Found {len(units)} units in production")
print(f"Found {len(roles)} roles in production\n")

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
    print(f"\n{home_name}:")
    print(f"  Target: {target_count} staff")
    
    # Filter staff for this home
    home_staff = [s for s in staff_data if s['care_home'] == home_name and s['sap'] != '000541']
    home_staff = home_staff[:target_count]
    
    for staff in home_staff:
        try:
            # Check if user exists
            if User.objects.filter(sap=staff['sap']).exists():
                skipped_count += 1
                continue
            
            # Get unit
            unit = units.get(staff['unit'])
            if not unit:
                print(f"    ⚠️ Unit not found: {staff['unit']} for SAP {staff['sap']}")
                error_count += 1
                continue
            
            # Get role - map abbreviation to full name
            role_abbrev = staff['role']
            role_full_name = role_mapping.get(role_abbrev)
            if not role_full_name:
                print(f"    ⚠️ Unknown role abbreviation: {role_abbrev} for SAP {staff['sap']}")
                error_count += 1
                continue
            
            role = roles.get(role_full_name)
            if not role:
                print(f"    ⚠️ Role not found: {role_full_name} for SAP {staff['sap']}")
                error_count += 1
                continue
            
            # Get home
            home = unit.care_home
            
            # Create user
            user = User.objects.create(
                sap=staff['sap'],
                first_name=staff['first_name'],
                last_name=staff['last_name'],
                email=staff['email'],
                password=make_password(f"{staff['last_name']}{staff['sap'][-4:]}"),
                role=role,
                home_unit=unit,  # Production uses home_unit instead of care_home
                unit=unit,       # Also set the unit field
                contracted_hours_per_week=staff['contract_hours'],
                prefers_day_shifts=True,
                prefers_night_shifts=False,
                max_consecutive_shifts=5,
                min_hours_between_shifts=11,
                is_active=True,
                is_staff=False,
                is_superuser=False
            )
            created_count += 1
            
        except Exception as e:
            print(f"    ❌ Error creating {staff['sap']}: {e}")
            error_count += 1
    
    actual_count = User.objects.filter(home_unit__care_home__name=home_name).exclude(sap='000541').count()
    print(f"  ✓ Created: {actual_count} staff")

print("\n" + "="*80)
print("IMPORT COMPLETE")
print("="*80)
print(f"\n  Created: {created_count}")
print(f"  Skipped (already exist): {skipped_count}")
print(f"  Errors: {error_count}")
print(f"  Total in database: {User.objects.count()}")
print("\n")
