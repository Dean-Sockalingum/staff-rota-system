#!/usr/bin/env python3
"""
Import complete demo data to production PostgreSQL
Handles schema differences between SQLite and PostgreSQL
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

import json
from django.db import transaction
from scheduling.models import (
    CareHome, Unit, ShiftType, Role, User, Shift
)
from django.contrib.auth.hashers import make_password

print("\n" + "="*80)
print("IMPORTING COMPLETE DEMO DATA TO PRODUCTION")
print("="*80 + "\n")

# Load the JSON export
with open('complete_demo_export.json', 'r') as f:
    data = json.load(f)

print(f"Loaded {len(data)} objects from export\n")

# Group by model
by_model = {}
for obj in data:
    model = obj['model']
    if model not in by_model:
        by_model[model] = []
    by_model[model].append(obj)

print("Objects by model:")
for model, objects in by_model.items():
    print(f"  {model:30} {len(objects):6} objects")
print()

# Import in correct order to handle dependencies
print("="*80)
print("IMPORTING...")
print("="*80 + "\n")

with transaction.atomic():
    # 1. Care Homes
    if 'scheduling.carehome' in by_model:
        print(f"Importing {len(by_model['scheduling.carehome'])} Care Homes...")
        for obj in by_model['scheduling.carehome']:
            fields = obj['fields']
            CareHome.objects.update_or_create(
                id=obj['pk'],
                defaults={
                    'name': fields['name'],
                    'capacity': fields.get('capacity', 120),
                    'address': fields.get('address', ''),
                    'phone': fields.get('phone', ''),
                    'current_occupancy': fields.get('current_occupancy', 0),
                }
            )
        print(f"✓ {CareHome.objects.count()} Care Homes imported\n")
    
    # 2. Units
    if 'scheduling.unit' in by_model:
        print(f"Importing {len(by_model['scheduling.unit'])} Units...")
        for obj in by_model['scheduling.unit']:
            fields = obj['fields']
            Unit.objects.update_or_create(
                id=obj['pk'],
                defaults={
                    'name': fields['name'],
                    'care_home_id': fields['care_home'],
                    'capacity': fields.get('capacity', 15),
                    'current_occupancy': fields.get('current_occupancy', 0),
                }
            )
        print(f"✓ {Unit.objects.count()} Units imported\n")
    
    # 3. Shift Types
    if 'scheduling.shifttype' in by_model:
        print(f"Importing {len(by_model['scheduling.shifttype'])} Shift Types...")
        for obj in by_model['scheduling.shifttype']:
            fields = obj['fields']
            ShiftType.objects.update_or_create(
                id=obj['pk'],
                defaults={
                    'name': fields['name'],
                    'start_time': fields['start_time'],
                    'end_time': fields['end_time'],
                    'duration_hours': fields.get('duration_hours', 12),
                    'color': fields.get('color', '#007bff'),
                }
            )
        print(f"✓ {ShiftType.objects.count()} Shift Types imported\n")
    
    # 4. Roles
    if 'scheduling.role' in by_model:
        print(f"Importing {len(by_model['scheduling.role'])} Roles...")
        for obj in by_model['scheduling.role']:
            fields = obj['fields']
            Role.objects.update_or_create(
                id=obj['pk'],
                defaults={
                    'name': fields['name'],
                    'is_senior': fields.get('is_senior', False),
                    'permissions_level': fields.get('permissions_level', 1),
                }
            )
        print(f"✓ {Role.objects.count()} Roles imported\n")
    
    # 5. Users/Staff
    if 'scheduling.user' in by_model:
        print(f"Importing {len(by_model['scheduling.user'])} Users (this may take a few minutes)...")
        count = 0
        for obj in by_model['scheduling.user']:
            fields = obj['fields']
            
            # Handle team field (might be too long for production schema)
            team_value = fields.get('team', '')
            if team_value and len(team_value) > 1:
                team_value = team_value[0]  # Take first character only
            
            User.objects.update_or_create(
                sap=obj['pk'],
                defaults={
                    'username': fields.get('username', obj['pk']),
                    'email': fields.get('email', f"{obj['pk']}@example.com"),
                    'first_name': fields.get('first_name', ''),
                    'last_name': fields.get('last_name', ''),
                    'password': fields.get('password', make_password(obj['pk'])),
                    'is_active': fields.get('is_active', True),
                    'is_staff': fields.get('is_staff', False),
                    'is_superuser': fields.get('is_superuser', False),
                    'role_id': fields.get('role'),
                    'unit_id': fields.get('unit'),
                    'team': team_value,
                    'phone': fields.get('phone', ''),
                    'contract_hours': fields.get('contract_hours', 35.0),
                }
            )
            count += 1
            if count % 100 == 0:
                print(f"  {count} users imported...")
        
        print(f"✓ {User.objects.count()} Users imported\n")
    
    # 6. Shifts
    if 'scheduling.shift' in by_model:
        print(f"Importing {len(by_model['scheduling.shift'])} Shifts (this will take several minutes)...")
        count = 0
        for obj in by_model['scheduling.shift']:
            fields = obj['fields']
            
            Shift.objects.update_or_create(
                id=obj['pk'],
                defaults={
                    'user_id': fields.get('user'),
                    'unit_id': fields.get('unit'),
                    'shift_type_id': fields.get('shift_type'),
                    'date': fields.get('date'),
                    'start_time': fields.get('start_time'),
                    'end_time': fields.get('end_time'),
                    'duration_hours': fields.get('duration_hours', 12),
                    'is_published': fields.get('is_published', True),
                    'notes': fields.get('notes', ''),
                    'shift_classification': fields.get('shift_classification', 'STANDARD'),
                }
            )
            count += 1
            if count % 1000 == 0:
                print(f"  {count} shifts imported...")
        
        print(f"✓ {Shift.objects.count()} Shifts imported\n")

print("="*80)
print("IMPORT COMPLETE!")
print("="*80 + "\n")

# Final verification
print("Final counts:")
print(f"  Care Homes:  {CareHome.objects.count()}")
print(f"  Units:       {Unit.objects.count()}")
print(f"  Shift Types: {ShiftType.objects.count()}")
print(f"  Roles:       {Role.objects.count()}")
print(f"  Users:       {User.objects.count()}")
print(f"  Shifts:      {Shift.objects.count():,}")
print()
print("✓ Production database ready for demo!\n")
