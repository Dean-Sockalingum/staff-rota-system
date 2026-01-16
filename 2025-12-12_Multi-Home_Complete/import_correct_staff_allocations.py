#!/usr/bin/env python3
"""
Import correct staff allocations from staff_export_821.json and update database.
This will correct all unit assignments and then update associated shifts.
"""

import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Unit, CareHome, Role, Shift
from django.db import transaction

print("Loading staff_export_821.json...")
with open('/Users/deansockalingum/Desktop/Staff_Rota_Backups/staff_export_821.json', 'r') as f:
    staff_data = json.load(f)

print(f"Found {len(staff_data)} staff records")

# Count current state
current_staff = User.objects.filter(is_active=True).count()
print(f"Current active staff in database: {current_staff}")

updates_made = 0
staff_not_found = []
staff_updated = []

print("\nUpdating staff unit assignments...")
print("=" * 80)

with transaction.atomic():
    for record in staff_data:
        sap = record.get('sap')
        unit_name = record.get('unit')
        care_home_name = record.get('care_home')
        is_active = record.get('is_active', True)
        role_name = record.get('role')
        
        if not sap:
            continue
            
        try:
            # Get the user
            user = User.objects.get(sap=sap)
            
            # Get the correct unit
            if unit_name:
                unit = Unit.objects.filter(name=unit_name).first()
                if not unit:
                    print(f"  ⚠️  Unit {unit_name} not found for {sap}")
                    continue
            else:
                unit = None
            
            # Check if update needed
            old_unit = user.unit.name if user.unit else 'None'
            
            if user.unit != unit or user.is_active != is_active:
                user.unit = unit
                user.is_active = is_active
                
                # Use update to bypass validation
                User.objects.filter(sap=sap).update(unit=unit, is_active=is_active)
                
                staff_updated.append({
                    'sap': sap,
                    'name': user.full_name,
                    'old_unit': old_unit,
                    'new_unit': unit_name,
                    'role': role_name
                })
                updates_made += 1
                
                if updates_made <= 20:
                    print(f"  {sap} {user.full_name} ({role_name}): {old_unit} → {unit_name}")
        
        except User.DoesNotExist:
            staff_not_found.append(sap)
            if len(staff_not_found) <= 10:
                print(f"  ⚠️  Staff {sap} not found in database")

print("\n" + "=" * 80)
print(f"SUMMARY:")
print(f"  Staff records processed: {len(staff_data)}")
print(f"  Staff updated: {updates_made}")
print(f"  Staff not found: {len(staff_not_found)}")
print("=" * 80)

# Now update shifts to match new unit assignments
print("\nUpdating shifts to match new unit assignments...")
print("=" * 80)

shifts_updated = 0
for staff_info in staff_updated:
    sap = staff_info['sap']
    new_unit_name = staff_info['new_unit']
    
    if not new_unit_name:
        continue
    
    try:
        user = User.objects.get(sap=sap)
        new_unit = Unit.objects.get(name=new_unit_name)
        
        # Update all future shifts for this user to be in their correct unit
        user_shifts = Shift.objects.filter(user=user).exclude(unit=new_unit)
        count = user_shifts.count()
        
        if count > 0:
            user_shifts.update(unit=new_unit)
            shifts_updated += count
            
            if shifts_updated <= 50:
                print(f"  {sap}: Updated {count} shifts to {new_unit_name}")
    
    except Exception as e:
        print(f"  ⚠️  Error updating shifts for {sap}: {e}")

print("\n" + "=" * 80)
print(f"SHIFT UPDATE SUMMARY:")
print(f"  Total shifts updated: {shifts_updated}")
print("=" * 80)

# Verify MGMT units now only have SM/OM
print("\nVerifying MGMT units...")
mgmt_units = Unit.objects.filter(name__endswith='_MGMT')
for unit in mgmt_units:
    care_staff = User.objects.filter(unit=unit, is_active=True).exclude(
        role__name__in=['SM', 'OM', 'ADMIN', 'HOS', 'IDI']
    )
    count = care_staff.count()
    
    if count > 0:
        print(f"  ⚠️  {unit.name}: Still has {count} care staff")
        for staff in care_staff[:3]:
            print(f"      - {staff.sap} {staff.full_name} ({staff.role.name if staff.role else 'No role'})")
    else:
        mgmt_count = User.objects.filter(unit=unit, is_active=True).count()
        print(f"  ✅ {unit.name}: {mgmt_count} management staff only")

print("\n✅ Import complete!")
