#!/usr/bin/env python3
"""
Fix MGMT unit staff assignments - move care staff out of MGMT units.
Only Senior Managers should be in MGMT units (matching Orchard Grove pattern).
"""

import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.db import transaction
from scheduling.models import User, CareHome, Unit, Shift

TARGET_HOMES = ['HAWTHORN_HOUSE', 'MEADOWBURN', 'RIVERSIDE']

def get_target_unit_for_staff(staff, home):
    """
    Determine which non-MGMT unit to assign staff to.
    Distribute evenly across units based on role.
    """
    # Get all non-MGMT units for this home
    non_mgmt_units = list(Unit.objects.filter(
        care_home=home
    ).exclude(name__contains='MGMT').order_by('name'))
    
    if not non_mgmt_units:
        return None
    
    # Find unit with fewest staff of this role
    min_count = float('inf')
    target_unit = non_mgmt_units[0]
    
    for unit in non_mgmt_units:
        count = User.objects.filter(
            unit=unit,
            role=staff.role,
            is_active=True
        ).count()
        
        if count < min_count:
            min_count = count
            target_unit = unit
    
    return target_unit

def fix_mgmt_staff_for_home(home):
    """Move non-SM staff out of MGMT unit"""
    print(f"\n--- Fixing {home.name} ---")
    
    mgmt_unit = Unit.objects.filter(care_home=home, name__contains='MGMT').first()
    if not mgmt_unit:
        print(f"  No MGMT unit found")
        return 0
    
    # Get all non-SM staff in MGMT unit
    wrong_staff = User.objects.filter(
        unit=mgmt_unit,
        is_active=True
    ).exclude(role__name='SM').select_related('role')
    
    count = wrong_staff.count()
    print(f"  Found {count} care staff in {mgmt_unit.name} (should be 0)")
    
    if count == 0:
        print(f"  ✓ Already correct")
        return 0
    
    moved = 0
    for staff in wrong_staff:
        # Find best target unit
        target_unit = get_target_unit_for_staff(staff, home)
        
        if target_unit:
            old_unit = staff.unit.name
            staff.unit = target_unit
            staff.save()
            
            # Update all shifts for this staff to new unit
            Shift.objects.filter(user=staff).update(unit=target_unit)
            
            print(f"    Moved {staff.full_name} ({staff.role.name}) from {old_unit} to {target_unit.name}")
            moved += 1
    
    print(f"  ✓ Moved {moved} staff out of MGMT unit")
    return moved

def verify_fix():
    """Verify MGMT units only have SM staff"""
    print("\n=== VERIFICATION ===\n")
    
    for home_name in ['ORCHARD_GROVE'] + TARGET_HOMES:
        home = CareHome.objects.get(name=home_name)
        mgmt_unit = Unit.objects.filter(care_home=home, name__contains='MGMT').first()
        
        if mgmt_unit:
            staff = User.objects.filter(unit=mgmt_unit, is_active=True).select_related('role')
            sm_count = staff.filter(role__name='SM').count()
            other_count = staff.exclude(role__name='SM').count()
            
            status = "✓" if other_count == 0 else f"⚠️  {other_count} care staff"
            print(f"{home_name} - {mgmt_unit.name}: {sm_count} SM, {other_count} others [{status}]")

def main():
    print("=" * 80)
    print("FIX MGMT UNIT STAFF ASSIGNMENTS")
    print("=" * 80)
    
    print("\nThis will move care staff out of MGMT units to match Orchard Grove pattern.")
    print("Only Senior Managers (SM) should remain in MGMT units.\n")
    
    # Show current state
    verify_fix()
    
    # Check for --yes flag
    if '--yes' not in sys.argv:
        response = input("\nProceed? (yes/no): ")
        if response.lower() != 'yes':
            print("Operation cancelled.")
            return
    
    # Fix each home
    print("\n=== FIXING MGMT UNITS ===")
    total_moved = 0
    
    with transaction.atomic():
        for home_name in TARGET_HOMES:
            home = CareHome.objects.get(name=home_name)
            moved = fix_mgmt_staff_for_home(home)
            total_moved += moved
    
    print("\n" + "=" * 80)
    print(f"✓ Moved {total_moved} total staff out of MGMT units!")
    print("=" * 80)
    
    # Verify
    verify_fix()

if __name__ == '__main__':
    main()
