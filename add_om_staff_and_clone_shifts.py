#!/usr/bin/env python3
"""
1. Add 2 OM staff to Orchard Grove
2. Generate their Mon-Fri shifts for full year 2025
3. Clone all Orchard shifts to other 3 homes
"""

import os
import django
import sys
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.db import transaction
from scheduling.models import User, Shift, CareHome, Role, ShiftType
from collections import defaultdict

TARGET_HOMES = ['HAWTHORN_HOUSE', 'MEADOWBURN', 'RIVERSIDE']

def add_om_staff_to_orchard():
    """Add 2 OM staff to Orchard Grove"""
    print("\n=== ADDING OM STAFF TO ORCHARD GROVE ===\n")
    
    orchard = CareHome.objects.get(name='ORCHARD_GROVE')
    orchard_unit = orchard.units.first()
    om_role = Role.objects.get(name='OM')
    
    # Check if already exist
    existing_om = User.objects.filter(
        unit__care_home=orchard,
        role=om_role,
        is_active=True
    ).count()
    
    if existing_om >= 2:
        print(f"✓ Orchard already has {existing_om} OM staff")
        return
    
    # Create 2 OM staff
    om_staff = [
        {
            'first_name': 'Ailsa',
            'last_name': 'Kelly (OG)',
            'sap': '990181',
            'email': 'ailsa.kelly.og@orchard.com',
        },
        {
            'first_name': 'Angus',
            'last_name': 'MacKenzie (OG)',
            'sap': '990182',
            'email': 'angus.mackenzie.og@orchard.com',
        }
    ]
    
    created_count = 0
    for om_data in om_staff:
        # Check if this SAP exists
        if not User.objects.filter(sap=om_data['sap']).exists():
            user = User.objects.create(
                email=om_data['email'],
                first_name=om_data['first_name'],
                last_name=om_data['last_name'],
                sap=om_data['sap'],
                role=om_role,
                unit=orchard_unit,
                is_active=True,
                is_staff=False,
            )
            user.set_password('Welcome123!')
            user.save()
            created_count += 1
            print(f"✓ Created: {user.full_name} (SAP: {user.sap})")
        else:
            print(f"  Already exists: {om_data['first_name']} {om_data['last_name']} (SAP: {om_data['sap']})")
    
    print(f"\n✓ Created {created_count} new OM staff for Orchard Grove")

def generate_om_shifts_for_orchard():
    """Generate Mon-Fri shifts for OM staff in Orchard Grove for full 2025"""
    print("\n=== GENERATING OM SHIFTS FOR ORCHARD GROVE ===\n")
    
    orchard = CareHome.objects.get(name='ORCHARD_GROVE')
    orchard_unit = orchard.units.first()
    om_role = Role.objects.get(name='OM')
    admin_shift_type = ShiftType.objects.get(name='ADMIN')
    
    # Get OM staff
    om_staff = list(User.objects.filter(
        unit__care_home=orchard,
        role=om_role,
        is_active=True
    ))
    
    if not om_staff:
        print("❌ No OM staff found in Orchard Grove!")
        return 0
    
    print(f"Found {len(om_staff)} OM staff:")
    for om in om_staff:
        print(f"  - {om.full_name}")
    
    # Check if OM shifts already exist
    existing_om_shifts = Shift.objects.filter(
        user__in=om_staff,
        unit__care_home=orchard
    ).count()
    
    if existing_om_shifts > 0:
        print(f"\n✓ OM shifts already exist ({existing_om_shifts} shifts)")
        return existing_om_shifts
    
    # Generate shifts for full year 2025 (Mon-Fri only)
    start_date = date(2025, 1, 1)
    end_date = date(2025, 12, 31)
    
    new_shifts = []
    current_date = start_date
    
    while current_date <= end_date:
        # Only Mon-Fri (0=Mon, 4=Fri)
        if current_date.weekday() < 5:
            # Both OMs work every weekday
            for om_user in om_staff:
                new_shift = Shift(
                    user=om_user,
                    unit=orchard_unit,
                    shift_type=admin_shift_type,
                    date=current_date,
                    status='CONFIRMED',
                    shift_classification='REGULAR',
                )
                new_shifts.append(new_shift)
        
        current_date += timedelta(days=1)
    
    # Bulk create
    if new_shifts:
        Shift.objects.bulk_create(new_shifts, batch_size=500)
        print(f"\n✓ Created {len(new_shifts)} OM shifts (Mon-Fri throughout 2025)")
    
    return len(new_shifts)

def build_staff_mapping(orchard, target_home):
    """Map Orchard Grove staff to equivalent staff in target home by role"""
    mapping = {}
    
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
    
    for staff in orchard_staff:
        orchard_staff_by_role[staff.role.name].append(staff)
    
    for staff in target_staff:
        target_staff_by_role[staff.role.name].append(staff)
    
    # Map staff 1-to-1 by role and position
    for role_name, orchard_list in orchard_staff_by_role.items():
        target_list = target_staff_by_role.get(role_name, [])
        
        for idx, orchard_user in enumerate(orchard_list):
            if idx < len(target_list):
                mapping[orchard_user.pk] = target_list[idx]
            else:
                print(f"  ⚠️  No equivalent {role_name} at position {idx+1} in {target_home.name}")
    
    return mapping

def clone_shifts_to_home(orchard, target_home):
    """Clone all Orchard Grove shifts to target home"""
    print(f"\n--- Cloning to {target_home.name} ---")
    
    staff_mapping = build_staff_mapping(orchard, target_home)
    print(f"  Mapped {len(staff_mapping)} staff members")
    
    target_unit = target_home.units.first()
    if not target_unit:
        print(f"  ❌ No unit found for {target_home.name}")
        return 0
    
    orchard_shifts = Shift.objects.filter(
        unit__care_home=orchard
    ).select_related('user', 'shift_type').order_by('date')
    
    print(f"  Cloning {orchard_shifts.count()} Orchard shifts...")
    
    new_shifts = []
    skipped = 0
    
    for orchard_shift in orchard_shifts:
        target_user = staff_mapping.get(orchard_shift.user_id)
        
        if not target_user:
            skipped += 1
            continue
        
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
        if count > 0:
            print(f"Deleting {count} shifts for {home_name}...")
            Shift.objects.filter(unit__care_home=home).delete()
    
    print("\n✓ Target home shifts deleted. Orchard Grove preserved.")

def show_comparison():
    """Show shift counts for comparison"""
    print("\n=== SHIFT COUNT COMPARISON ===\n")
    
    orchard = CareHome.objects.get(name='ORCHARD_GROVE')
    
    # Dec 16 example
    target_date = date(2025, 12, 16)
    orchard_count = Shift.objects.filter(unit__care_home=orchard, date=target_date).count()
    print(f"Dec 16, 2025:")
    print(f"  ORCHARD_GROVE (MASTER): {orchard_count} shifts")
    
    for home_name in TARGET_HOMES:
        home = CareHome.objects.get(name=home_name)
        count = Shift.objects.filter(unit__care_home=home, date=target_date).count()
        status = "✓" if count == orchard_count else f"⚠️  {count}"
        print(f"  {home_name}: {count} shifts [{status}]")

def main():
    print("=" * 80)
    print("ADD OM STAFF & CLONE ORCHARD GROVE SHIFTS")
    print("=" * 80)
    
    orchard = CareHome.objects.get(name='ORCHARD_GROVE')
    
    print("\nThis script will:")
    print("1. Add 2 OM staff to Orchard Grove")
    print("2. Generate Mon-Fri ADMIN shifts for OM staff (full 2025)")
    print("3. Delete shifts from Hawthorn, Meadowburn, Riverside")
    print("4. Clone ALL Orchard shifts to those 3 homes")
    
    # Check for --yes flag
    if '--yes' not in sys.argv:
        response = input("\nProceed? (yes/no): ")
        if response.lower() != 'yes':
            print("Operation cancelled.")
            return
    
    with transaction.atomic():
        # Step 1: Add OM staff to Orchard
        add_om_staff_to_orchard()
        
        # Step 2: Generate OM shifts
        om_shifts_created = generate_om_shifts_for_orchard()
        
        # Step 3: Delete target home shifts
        delete_target_home_shifts()
        
        # Step 4: Clone to each target home
        print("\n=== CLONING ORCHARD SHIFTS ===")
        total_created = 0
        
        for home_name in TARGET_HOMES:
            target_home = CareHome.objects.get(name=home_name)
            created = clone_shifts_to_home(orchard, target_home)
            total_created += created
    
    print("\n" + "=" * 80)
    print(f"✓ SUCCESS!")
    print(f"  - Created {om_shifts_created} OM shifts in Orchard Grove")
    print(f"  - Cloned {total_created} total shifts to other 3 homes")
    print("=" * 80)
    
    show_comparison()

if __name__ == '__main__':
    main()
