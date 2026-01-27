#!/usr/bin/env python3
"""
Fix unit assignments for shifts in the 3 target homes to match Orchard Grove's pattern.
Currently all shifts are in one unit per home - need to distribute across units properly.
"""

import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.db import transaction
from scheduling.models import User, Shift, CareHome, Unit
from collections import defaultdict

TARGET_HOMES = ['HAWTHORN_HOUSE', 'MEADOWBURN', 'RIVERSIDE']

def analyze_current_problem():
    """Show the current unit assignment problem"""
    print("\n=== CURRENT SHIFT DISTRIBUTION ===\n")
    
    orchard = CareHome.objects.get(name='ORCHARD_GROVE')
    orchard_units = list(Unit.objects.filter(care_home=orchard).order_by('name'))
    
    print(f"ORCHARD_GROVE (Correct Pattern):")
    for unit in orchard_units:
        shift_count = Shift.objects.filter(unit=unit).count()
        staff_count = User.objects.filter(unit=unit, is_active=True).count()
        print(f"  {unit.name}: {staff_count} staff, {shift_count} shifts")
    
    for home_name in TARGET_HOMES:
        home = CareHome.objects.get(name=home_name)
        units = list(Unit.objects.filter(care_home=home).order_by('name'))
        
        print(f"\n{home_name} (Needs Fix):")
        for unit in units:
            shift_count = Shift.objects.filter(unit=unit).count()
            staff_count = User.objects.filter(unit=unit, is_active=True).count()
            if shift_count > 0 or staff_count > 0:
                status = "⚠️ " if shift_count != staff_count * 130 else ""
                print(f"  {status}{unit.name}: {staff_count} staff, {shift_count} shifts")

def fix_unit_assignments_for_home(home):
    """Reassign shifts to match staff's unit assignments"""
    print(f"\n--- Fixing {home.name} ---")
    
    # Get all shifts for this home
    all_shifts = Shift.objects.filter(
        unit__care_home=home
    ).select_related('user', 'user__unit').order_by('date', 'shift_type')
    
    print(f"  Processing {all_shifts.count()} shifts...")
    
    updates = []
    fixed_count = 0
    
    for shift in all_shifts:
        # Each shift should be in the same unit as the user
        correct_unit = shift.user.unit
        
        if shift.unit != correct_unit:
            shift.unit = correct_unit
            updates.append(shift)
            fixed_count += 1
    
    # Bulk update
    if updates:
        Shift.objects.bulk_update(updates, ['unit'], batch_size=1000)
        print(f"  ✓ Fixed {fixed_count} shifts (reassigned to correct units)")
    else:
        print(f"  ✓ All shifts already in correct units")
    
    return fixed_count

def verify_fix():
    """Verify that unit assignments are now correct"""
    print("\n=== VERIFICATION ===\n")
    
    for home_name in TARGET_HOMES:
        home = CareHome.objects.get(name=home_name)
        units = Unit.objects.filter(care_home=home).order_by('name')
        
        print(f"{home_name}:")
        total_shifts = 0
        for unit in units:
            shift_count = Shift.objects.filter(unit=unit).count()
            staff_count = User.objects.filter(unit=unit, is_active=True).count()
            total_shifts += shift_count
            if shift_count > 0 or staff_count > 0:
                print(f"  {unit.name}: {staff_count} staff, {shift_count} shifts")
        print(f"  TOTAL: {total_shifts} shifts\n")

def main():
    print("=" * 80)
    print("FIX UNIT ASSIGNMENTS FOR SHIFTS")
    print("=" * 80)
    
    # Show current problem
    analyze_current_problem()
    
    print("\n" + "=" * 80)
    print("This will reassign each shift to match the staff member's unit assignment.")
    print("=" * 80)
    
    # Check for --yes flag
    if '--yes' not in sys.argv:
        response = input("\nProceed? (yes/no): ")
        if response.lower() != 'yes':
            print("Operation cancelled.")
            return
    
    # Fix each home
    print("\n=== FIXING UNIT ASSIGNMENTS ===")
    total_fixed = 0
    
    with transaction.atomic():
        for home_name in TARGET_HOMES:
            home = CareHome.objects.get(name=home_name)
            fixed = fix_unit_assignments_for_home(home)
            total_fixed += fixed
    
    print("\n" + "=" * 80)
    print(f"✓ Fixed {total_fixed} total shift assignments!")
    print("=" * 80)
    
    # Verify
    verify_fix()

if __name__ == '__main__':
    main()
