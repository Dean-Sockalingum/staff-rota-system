#!/usr/bin/env python3
"""
Move all supernumerary staff (SM, OM) to MGMT units.
These staff work Mon-Fri and should be in MGMT units, not care units.
"""

import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.db import transaction
from scheduling.models import User, CareHome, Unit, Shift

ALL_HOMES = ['ORCHARD_GROVE', 'HAWTHORN_HOUSE', 'MEADOWBURN', 'RIVERSIDE']
SUPERNUMERARY_ROLES = ['SM', 'OM']

def show_current_state():
    """Show where supernumerary staff are currently"""
    print("\n=== CURRENT SUPERNUMERARY STAFF LOCATIONS ===\n")
    
    for home_name in ALL_HOMES:
        home = CareHome.objects.get(name=home_name)
        mgmt_unit = Unit.objects.filter(care_home=home, name__contains='MGMT').first()
        
        print(f"{home_name}:")
        
        for role in SUPERNUMERARY_ROLES:
            staff = User.objects.filter(
                unit__care_home=home,
                role__name=role,
                is_active=True
            ).select_related('unit')
            
            for s in staff:
                in_mgmt = "✓" if s.unit == mgmt_unit else "⚠️ "
                print(f"  {in_mgmt}{role}: {s.full_name} in {s.unit.name}")
        print()

def move_supernumerary_staff_to_mgmt(home):
    """Move all SM and OM staff to MGMT unit"""
    print(f"\n--- Moving {home.name} supernumerary staff ---")
    
    # Get MGMT unit
    mgmt_unit = Unit.objects.filter(care_home=home, name__contains='MGMT').first()
    if not mgmt_unit:
        print(f"  ❌ No MGMT unit found for {home.name}")
        return 0
    
    moved = 0
    
    for role in SUPERNUMERARY_ROLES:
        staff = User.objects.filter(
            unit__care_home=home,
            role__name=role,
            is_active=True
        ).select_related('unit')
        
        for s in staff:
            if s.unit != mgmt_unit:
                old_unit = s.unit.name
                s.unit = mgmt_unit
                s.save()
                
                # Move all their shifts to MGMT unit
                shift_count = Shift.objects.filter(user=s).update(unit=mgmt_unit)
                
                print(f"  Moved {s.full_name} ({role}) from {old_unit} to {mgmt_unit.name} ({shift_count} shifts)")
                moved += 1
            else:
                print(f"  ✓ {s.full_name} ({role}) already in {mgmt_unit.name}")
    
    return moved

def verify_fix():
    """Verify all supernumerary staff are in MGMT units"""
    print("\n=== VERIFICATION ===\n")
    
    for home_name in ALL_HOMES:
        home = CareHome.objects.get(name=home_name)
        mgmt_unit = Unit.objects.filter(care_home=home, name__contains='MGMT').first()
        
        if mgmt_unit:
            staff = User.objects.filter(unit=mgmt_unit, is_active=True).select_related('role')
            sm_count = staff.filter(role__name='SM').count()
            om_count = staff.filter(role__name='OM').count()
            other_count = staff.exclude(role__name__in=['SM', 'OM']).count()
            
            status = "✓" if other_count == 0 else f"⚠️  {other_count} care staff"
            print(f"{home_name} - {mgmt_unit.name}: {sm_count} SM, {om_count} OM [{status}]")

def main():
    print("=" * 80)
    print("MOVE SUPERNUMERARY STAFF TO MGMT UNITS")
    print("=" * 80)
    
    print("\nThis will move all SM and OM staff to MGMT units.")
    print("These are supernumerary staff who work Mon-Fri.\n")
    
    # Show current state
    show_current_state()
    
    # Check for --yes flag
    if '--yes' not in sys.argv:
        response = input("\nProceed? (yes/no): ")
        if response.lower() != 'yes':
            print("Operation cancelled.")
            return
    
    # Fix each home
    print("\n=== MOVING STAFF TO MGMT UNITS ===")
    total_moved = 0
    
    with transaction.atomic():
        for home_name in ALL_HOMES:
            home = CareHome.objects.get(name=home_name)
            moved = move_supernumerary_staff_to_mgmt(home)
            total_moved += moved
    
    print("\n" + "=" * 80)
    print(f"✓ Moved {total_moved} total staff to MGMT units!")
    print("=" * 80)
    
    # Verify
    verify_fix()

if __name__ == '__main__':
    main()
