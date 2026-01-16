#!/usr/bin/env python3
"""
Clone Orchard Grove shifts to the other 3 standardized homes.
Orchard Grove has the correct pattern - we'll replicate it exactly.
"""

import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.db import transaction
from scheduling.models import User, Shift, CareHome
from collections import defaultdict

# Orchard Grove is the master, clone to these 3 homes
TARGET_HOMES = ['HAWTHORN_HOUSE', 'MEADOWBURN', 'RIVERSIDE']

def analyze_current_state():
    """Show current shift counts"""
    print("\n=== CURRENT SHIFT COUNTS (Dec 2025) ===\n")
    
    orchard = CareHome.objects.get(name='ORCHARD_GROVE')
    orchard_dec = Shift.objects.filter(
        unit__care_home=orchard,
        date__year=2025,
        date__month=12
    ).count()
    print(f"ORCHARD_GROVE (MASTER): {orchard_dec} shifts in Dec 2025")
    
    for home_name in TARGET_HOMES:
        home = CareHome.objects.get(name=home_name)
        dec_shifts = Shift.objects.filter(
            unit__care_home=home,
            date__year=2025,
            date__month=12
        ).count()
        print(f"{home_name}: {dec_shifts} shifts in Dec 2025")
    
    # Show specific date comparison
    print("\n=== Dec 16, 2025 Comparison (Example) ===")
    target = date(2025, 12, 16)
    
    orchard_count = Shift.objects.filter(unit__care_home=orchard, date=target).count()
    print(f"ORCHARD_GROVE (MASTER): {orchard_count} shifts")
    
    for home_name in TARGET_HOMES:
        home = CareHome.objects.get(name=home_name)
        count = Shift.objects.filter(unit__care_home=home, date=target).count()
        diff = count - orchard_count
        status = "✓" if diff == 0 else f"⚠️  {diff:+d}"
        print(f"{home_name}: {count} shifts [{status}]")

def build_staff_mapping(orchard, target_home):
    """
    Map Orchard Grove staff to equivalent staff in target home by role.
    Returns dict: {orchard_user_id: target_user}
    """
    mapping = {}
    
    # Get all active staff from both homes, grouped by role
    orchard_staff_by_role = defaultdict(list)
    target_staff_by_role = defaultdict(list)
    
    orchard_staff = User.objects.filter(
        unit__care_home=orchard,
        is_active=True
    ).select_related('role').order_by('role__name', 'first_name', 'last_name')
    
    target_staff = User.objects.filter(
        unit__care_home=target_home,
        is_active=True
    ).select_related('role').order_by('role__name', 'first_name', 'last_name')
    
    # Group by role
    for staff in orchard_staff:
        orchard_staff_by_role[staff.role.name].append(staff)
    
    for staff in target_staff:
        target_staff_by_role[staff.role.name].append(staff)
    
    # Map staff 1-to-1 by role and position
    for role_name, orchard_list in orchard_staff_by_role.items():
        target_list = target_staff_by_role.get(role_name, [])
        
        # Map position-by-position
        for idx, orchard_user in enumerate(orchard_list):
            if idx < len(target_list):
                mapping[orchard_user.id] = target_list[idx]
            else:
                print(f"  ⚠️  No equivalent {role_name} at position {idx+1} in {target_home.name}")
    
    return mapping

def clone_shifts_to_home(orchard, target_home):
    """Clone all Orchard Grove shifts to target home"""
    print(f"\n--- Cloning to {target_home.name} ---")
    
    # Build staff mapping
    print("  Building staff mapping...")
    staff_mapping = build_staff_mapping(orchard, target_home)
    print(f"  Mapped {len(staff_mapping)} staff members")
    
    # Get target home's unit
    target_unit = target_home.units.first()
    if not target_unit:
        print(f"  ❌ No unit found for {target_home.name}")
        return 0
    
    # Get all Orchard shifts
    orchard_shifts = Shift.objects.filter(
        unit__care_home=orchard
    ).select_related('user', 'shift_type').order_by('date')
    
    print(f"  Found {orchard_shifts.count()} Orchard shifts to clone")
    
    # Clone shifts
    new_shifts = []
    skipped = 0
    
    for orchard_shift in orchard_shifts:
        # Map the user
        target_user = staff_mapping.get(orchard_shift.user_id)
        
        if not target_user:
            skipped += 1
            continue
        
        # Create equivalent shift
        new_shift = Shift(
            user=target_user,
            unit=target_unit,
            shift_type=orchard_shift.shift_type,
            date=orchard_shift.date,
            status=orchard_shift.status,
            custom_start_time=orchard_shift.custom_start_time,
            custom_end_time=orchard_shift.custom_end_time,
            notes=orchard_shift.notes,
            shift_pattern=orchard_shift.shift_pattern,
            shift_classification=orchard_shift.shift_classification,
        )
        new_shifts.append(new_shift)
    
    # Bulk create
    if new_shifts:
        Shift.objects.bulk_create(new_shifts, batch_size=1000)
        print(f"  ✓ Created {len(new_shifts)} shifts")
        if skipped > 0:
            print(f"  ⚠️  Skipped {skipped} shifts (no matching staff)")
    
    return len(new_shifts)

def delete_target_home_shifts():
    """Delete existing shifts for the 3 target homes"""
    print("\n=== DELETING EXISTING SHIFTS (Target Homes Only) ===\n")
    
    for home_name in TARGET_HOMES:
        home = CareHome.objects.get(name=home_name)
        count = Shift.objects.filter(unit__care_home=home).count()
        print(f"Deleting {count} shifts for {home_name}...")
        Shift.objects.filter(unit__care_home=home).delete()
    
    print("\n✓ Target home shifts deleted. Orchard Grove preserved.")

def main():
    print("=" * 80)
    print("CLONE ORCHARD GROVE SHIFTS TO OTHER HOMES")
    print("=" * 80)
    
    # Show current state
    analyze_current_state()
    
    # Get homes
    orchard = CareHome.objects.get(name='ORCHARD_GROVE')
    
    # Ask for confirmation
    print("\n" + "=" * 80)
    print("This will:")
    print("1. DELETE all shifts for Hawthorn, Meadowburn, and Riverside")
    print("2. KEEP Orchard Grove shifts (master pattern)")
    print("3. CLONE Orchard shifts to the other 3 homes")
    print("=" * 80)
    response = input("\nProceed? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Operation cancelled.")
        return
    
    # Execute cloning
    with transaction.atomic():
        # Delete target home shifts
        delete_target_home_shifts()
        
        # Clone to each target home
        print("\n=== CLONING ORCHARD SHIFTS ===")
        total_created = 0
        
        for home_name in TARGET_HOMES:
            target_home = CareHome.objects.get(name=home_name)
            created = clone_shifts_to_home(orchard, target_home)
            total_created += created
    
    print("\n" + "=" * 80)
    print(f"✓ Successfully cloned {total_created} total shifts!")
    print("=" * 80)
    
    # Show final state
    print("\n=== FINAL STATE ===\n")
    target = date(2025, 12, 16)
    
    orchard_count = Shift.objects.filter(unit__care_home=orchard, date=target).count()
    print(f"ORCHARD_GROVE (MASTER): {orchard_count} shifts on {target}")
    
    for home_name in TARGET_HOMES:
        home = CareHome.objects.get(name=home_name)
        count = Shift.objects.filter(unit__care_home=home, date=target).count()
        status = "✓" if count == orchard_count else f"⚠️  {count}"
        print(f"{home_name}: {count} shifts [{status}]")

if __name__ == '__main__':
    main()
