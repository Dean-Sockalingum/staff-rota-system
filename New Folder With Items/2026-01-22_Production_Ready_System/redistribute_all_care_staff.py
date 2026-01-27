#!/usr/bin/env python3
"""
Properly redistribute ALL care staff from MGMT units to care units.
Uses balanced distribution to ensure even coverage across all units.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Unit, Shift
from collections import defaultdict
import random

print("COMPREHENSIVE STAFF REDISTRIBUTION")
print("=" * 80)

# Get all MGMT units
mgmt_units = Unit.objects.filter(name__endswith='_MGMT')

total_redistributed = 0
total_shifts_updated = 0

for mgmt_unit in mgmt_units:
    # Get care staff wrongly assigned to this MGMT unit
    care_staff = User.objects.filter(
        unit=mgmt_unit,
        is_active=True
    ).exclude(
        role__name__in=['SM', 'OM', 'ADMIN', 'HOS', 'IDI']
    ).select_related('role')
    
    count = care_staff.count()
    if count == 0:
        print(f"\n✅ {mgmt_unit.name}: No care staff to redistribute")
        continue
    
    # Get care units for this home
    home = mgmt_unit.care_home
    if not home:
        print(f"\n⚠️  {mgmt_unit.name}: No home assigned, skipping")
        continue
    
    care_units = list(Unit.objects.filter(
        care_home=home,
        is_active=True
    ).exclude(
        name__endswith='_MGMT'
    ))
    
    if not care_units:
        print(f"\n⚠️  {mgmt_unit.name}: No care units found for {home.name}")
        continue
    
    print(f"\n{home.name} - {mgmt_unit.name}")
    print(f"  Care staff to redistribute: {count}")
    print(f"  Available care units: {len(care_units)}")
    
    # Group staff by role for balanced distribution
    staff_by_role = defaultdict(list)
    for staff in care_staff:
        role_name = staff.role.name if staff.role else 'UNKNOWN'
        staff_by_role[role_name].append(staff)
    
    #Redistribute each role group evenly across units
    unit_index = 0
    redistributed_count = 0
    
    for role_name, staff_list in staff_by_role.items():
        print(f"\n  Redistributing {len(staff_list)} {role_name} staff:")
        
        for staff in staff_list:
            target_unit = care_units[unit_index % len(care_units)]
            
            print(f"    {staff.sap} {staff.full_name}: {mgmt_unit.name} → {target_unit.name}")
            
            # Update staff assignment
            User.objects.filter(sap=staff.sap).update(unit=target_unit)
            
            # Update all their shifts
            shifts_updated = Shift.objects.filter(user=staff).update(unit=target_unit)
            total_shifts_updated += shifts_updated
            
            redistributed_count += 1
            unit_index += 1
    
    total_redistributed += redistributed_count
    print(f"\n  ✅ Redistributed {redistributed_count} staff from {mgmt_unit.name}")

print("\n" + "=" * 80)
print(f"SUMMARY:")
print(f"  Total staff redistributed: {total_redistributed}")
print(f"  Total shifts updated: {total_shifts_updated}")
print("=" * 80)

# Verify MGMT units
print("\nVERIFICATION - MGMT Units:")
print("=" * 80)

for mgmt_unit in mgmt_units:
    staff = User.objects.filter(unit=mgmt_unit, is_active=True).select_related('role')
    mgmt_staff = staff.filter(role__name__in=['SM', 'OM', 'ADMIN', 'HOS', 'IDI'])
    care_staff = staff.exclude(role__name__in=['SM', 'OM', 'ADMIN', 'HOS', 'IDI'])
    
    print(f"\n{mgmt_unit.name}:")
    print(f"  Management staff: {mgmt_staff.count()}")
    for s in mgmt_staff:
        print(f"    ✅ {s.sap} - {s.full_name} ({s.role.name if s.role else 'No role'})")
    
    if care_staff.count() > 0:
        print(f"  ⚠️  Care staff still present: {care_staff.count()}")
        for s in care_staff[:3]:
            print(f"    ❌ {s.sap} - {s.full_name} ({s.role.name if s.role else 'No role'})")
    else:
        print(f"  ✅ No care staff (correct)")

print("\n✅ Redistribution complete!")
