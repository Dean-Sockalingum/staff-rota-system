#!/usr/bin/env python3
"""
Fix shifts for staff who were reassigned from MGMT units to care units.
Updates shift.unit to match the staff member's current unit assignment.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Unit, Shift

print("Fixing shifts for reassigned staff...")
print("=" * 80)

# Get all MGMT units
mgmt_units = Unit.objects.filter(name__endswith='_MGMT')

total_shifts_updated = 0

for mgmt_unit in mgmt_units:
    # Find all shifts in this MGMT unit where the staff member is NOT assigned to this unit
    # (meaning they were reassigned but their shifts weren't updated)
    mismatched_shifts = Shift.objects.filter(
        unit=mgmt_unit
    ).exclude(
        user__unit=mgmt_unit
    ).select_related('user', 'user__unit')
    
    count = mismatched_shifts.count()
    if count == 0:
        print(f"\n✅ {mgmt_unit.name}: No mismatched shifts")
        continue
    
    print(f"\n{mgmt_unit.care_home.name if mgmt_unit.care_home else 'Unknown'} - {mgmt_unit.name}")
    print(f"Found {count} shifts with staff assigned to different units")
    
    # Update each shift to match the staff member's current unit
    for shift in mismatched_shifts:
        old_unit = shift.unit.name
        new_unit = shift.user.unit.name
        
        print(f"  Shift {shift.id}: {shift.user.full_name} ({shift.user.sap})")
        print(f"    Shift unit: {old_unit} → {new_unit}")
        print(f"    Date: {shift.date}, Type: {shift.shift_type}")
        
        # Update the shift's unit to match the staff's unit
        shift.unit = shift.user.unit
        shift.save()
        total_shifts_updated += 1

print("\n" + "=" * 80)
print(f"SUMMARY: Updated {total_shifts_updated} shifts")
print("=" * 80)

# Verification
print("\nVERIFICATION - Shifts in MGMT units after fix:")
print("=" * 80)

for mgmt_unit in mgmt_units:
    shifts = Shift.objects.filter(unit=mgmt_unit).select_related('user')
    mgmt_staff_count = shifts.filter(user__role__in=['SM', 'OM', 'ADMIN', 'HOS', 'IDI']).count()
    care_staff_count = shifts.exclude(user__role__in=['SM', 'OM', 'ADMIN', 'HOS', 'IDI']).count()
    
    print(f"\n{mgmt_unit.name}:")
    print(f"  Management staff shifts: {mgmt_staff_count}")
    print(f"  Care staff shifts: {care_staff_count}")
    
    if care_staff_count > 0:
        print(f"  ⚠️  WARNING: Still has {care_staff_count} care staff shifts!")
        # Show first 5 examples
        care_shifts = shifts.exclude(user__role__in=['SM', 'OM', 'ADMIN', 'HOS', 'IDI'])[:5]
        for shift in care_shifts:
            print(f"      - {shift.user.sap} {shift.user.full_name} ({shift.user.role})")
    else:
        print(f"  ✅ No care staff shifts (correct)")

print("\n✅ Complete!")
