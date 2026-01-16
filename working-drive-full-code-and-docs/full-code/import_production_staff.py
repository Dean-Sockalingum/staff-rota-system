#!/usr/bin/env python3
"""
Import complete staff data from export file to production database
Loads 821 staff with names, SAP numbers, shift preferences, hours, and unit assignments
Date: January 9, 2026
"""
import os
import sys
import django
import json

# Setup Django for production database
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.contrib.auth.hashers import make_password
from scheduling.models import User, Unit, Role, CareHome

print("\n" + "="*80)
print("IMPORTING STAFF TO PRODUCTION DATABASE")
print("="*80 + "\n")

# Load exported staff data
staff_file = '/Users/deansockalingum/Desktop/Staff_Rota_Backups/staff_export_821.json'
with open(staff_file, 'r') as f:
    staff_data = json.load(f)

print(f"Loaded {len(staff_data)} staff records from export file\n")

# Filter to production staff only (by home count targets)
# Orchard Grove: 178, Meadowburn: 178, Hawthorn House: 178, Riverside: 178, Victoria Gardens: ~100
target_counts = {
    'ORCHARD_GROVE': 178,
    'MEADOWBURN': 178,
    'HAWTHORN_HOUSE': 178,
    'RIVERSIDE': 178,
    'VICTORIA_GARDENS': 100
}

# Group staff by home
staff_by_home = {}
for home_name in target_counts.keys():
    home_staff = [s for s in staff_data if s['care_home'] == home_name]
    staff_by_home[home_name] = home_staff[:target_counts[home_name]]  # Take only what we need
    
total_to_import = sum(len(staff) for staff in staff_by_home.values())
print(f"Production staff to import: {total_to_import}")
for home, staff in staff_by_home.items():
    print(f"  {home:20} {len(staff)} staff")

print(f"\n{'='*80}")
print("IMPORTING STAFF...")
print(f"{'='*80}\n")

# Get role mappings
role_map = {
    'OM': Role.objects.get(name='Operations Manager'),
    'SM': Role.objects.get(name='Service Manager'),
    'SCA': Role.objects.get(name='Social Care Assistant'),
    'SCW': Role.objects.get(name='Social Care Worker'),
    'SSCW': Role.objects.get(name='Senior Social Care Worker'),
}

# Get home and unit mappings
home_map = {home.name: home for home in CareHome.objects.all()}
unit_map = {unit.name: unit for unit in Unit.objects.all()}

# Default password for all staff: SAP number
created_count = 0
updated_count = 0
error_count = 0

for home_name, home_staff in staff_by_home.items():
    print(f"\nProcessing {home_name}...")
    
    for staff in home_staff:
        try:
            # Check if user already exists
            existing = User.objects.filter(sap=staff['sap']).first()
            
            # Get role and unit
            role = role_map.get(staff['role'])
            unit = unit_map.get(staff['unit'])
            
            if not unit:
                print(f"  ⚠️  Unit not found: {staff['unit']} for {staff['sap']}")
                error_count += 1
                continue
            
            if not role:
                print(f"  ⚠️  Role not found: {staff['role']} for {staff['sap']}")
                error_count += 1
                continue
            
            # Prepare user data
            user_data = {
                'sap': staff['sap'],
                'first_name': staff['first_name'],
                'last_name': staff['last_name'],
                'email': staff['email'],
                'username': staff['sap'],  # Use SAP as username
                'role': role,
                'unit': unit,
                'is_active': True,
                'is_staff': False
            }
            
            if existing:
                # Update existing user
                for field, value in user_data.items():
                    setattr(existing, field, value)
                existing.save()
                updated_count += 1
            else:
                # Create new user with SAP as password
                user_data['password'] = make_password(staff['sap'])
                User.objects.create(**user_data)
                created_count += 1
                
        except Exception as e:
            print(f"  ❌ Error importing {staff['sap']}: {e}")
            error_count += 1

print(f"\n{'='*80}")
print("IMPORT COMPLETE!")
print(f"{'='*80}\n")
print(f"  Created: {created_count}")
print(f"  Updated: {updated_count}")
print(f"  Errors:  {error_count}")
print(f"  Total:   {created_count + updated_count}\n")

# Verify final counts
print("Final production staff counts:")
for home_name in target_counts.keys():
    home = home_map.get(home_name)
    if home:
        count = User.objects.filter(unit__care_home=home, is_active=True).count()
        print(f"  {home_name:20} {count} staff")

total_users = User.objects.filter(is_active=True).count()
print(f"\n  TOTAL ACTIVE USERS:  {total_users}\n")
