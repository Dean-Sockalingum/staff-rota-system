#!/usr/bin/env python3
"""
Replicate Orchard Grove's exact staffing structure to other large homes.

Orchard Grove is the master template with correct:
- Unit structure (8 units + MGMT)
- Role distribution (SSCW, SSCWN, SCW, SCA, SCWN, SCAN, SM, OM)
- Shift patterns and coverage
- Staffing levels per unit

This script clones OG's structure to: Hawthorn House, Meadowburn, Riverside
"""

import os
import django
import sys
from datetime import date, timedelta
from collections import defaultdict

# Setup Django
sys.path.insert(0, '/home/staff-rota-system/2025-12-12_Multi-Home_Complete')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import Shift, User, Unit, ShiftType, Role
from scheduling.models_multi_home import CareHome

def analyze_og_structure(start_date, end_date):
    """Analyze Orchard Grove's shift structure to use as template."""
    print("=" * 80)
    print("ANALYZING ORCHARD GROVE STRUCTURE")
    print("=" * 80)
    
    og_home = CareHome.objects.get(name='ORCHARD_GROVE')
    og_shifts = Shift.objects.filter(
        unit__care_home=og_home,
        date__range=[start_date, end_date]
    ).select_related('user', 'user__role', 'unit', 'shift_type').order_by('date', 'shift_type__start_time')
    
    # Group by date, unit, role, shift_type
    structure = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))
    
    for shift in og_shifts:
        day_of_week = shift.date.strftime('%A')  # Monday, Tuesday, etc.
        unit_type = shift.unit.name  # OG_ROSE, OG_LILY, etc.
        role = shift.user.role.name if shift.user and shift.user.role else 'UNKNOWN'
        shift_type = shift.shift_type.name
        
        structure[day_of_week][unit_type][role][shift_type].append({
            'user': shift.user,
            'shift_type': shift.shift_type,
            'start_time': shift.shift_type.start_time,
            'end_time': shift.shift_type.end_time,
        })
    
    # Print summary
    print(f"\nTotal OG shifts analyzed: {og_shifts.count()}")
    print(f"Date range: {start_date} to {end_date}")
    
    print("\n--- Daily Pattern (using first date as example) ---")
    first_date = start_date
    first_day = first_date.strftime('%A')
    
    for unit_name in sorted(structure[first_day].keys()):
        print(f"\n  {unit_name}:")
        for role in sorted(structure[first_day][unit_name].keys()):
            total = sum(len(shifts) for shifts in structure[first_day][unit_name][role].values())
            print(f"    {role}: {total} shifts")
    
    return structure

def get_unit_mapping():
    """Map Orchard Grove units to equivalent units in other homes."""
    return {
        'OG_ROSE': {
            'HAWTHORN_HOUSE': 'HH_HEATHER',
            'MEADOWBURN': 'MB_DAISY',
            'RIVERSIDE': 'RS_MAPLE'
        },
        'OG_LILY': {
            'HAWTHORN_HOUSE': 'HH_THISTLE',
            'MEADOWBURN': 'MB_BUTTERCUP',
            'RIVERSIDE': 'RS_BIRCH'
        },
        'OG_DAISY': {
            'HAWTHORN_HOUSE': 'HH_BLUEBELL',
            'MEADOWBURN': 'MB_PRIMROSE',
            'RIVERSIDE': 'RS_OAK'
        },
        'OG_TULIP': {
            'HAWTHORN_HOUSE': 'HH_PRIMROSE',
            'MEADOWBURN': 'MB_BLUEBELL',
            'RIVERSIDE': 'RS_WILLOW'
        },
        'OG_ORCHID': {
            'HAWTHORN_HOUSE': 'HH_LAVENDER',
            'MEADOWBURN': 'MB_LAVENDER',
            'RIVERSIDE': 'RS_ASH'
        },
        'OG_IRIS': {
            'HAWTHORN_HOUSE': 'HH_ROSE',
            'MEADOWBURN': 'MB_ROSE',
            'RIVERSIDE': 'RS_ELM'
        },
        'OG_JASMINE': {
            'HAWTHORN_HOUSE': 'HH_SNOWDROP_SRD',
            'MEADOWBURN': 'MB_POPPY_SRD',
            'RIVERSIDE': 'RS_JASMINE'
        },
        'OG_CROCUS': {
            'HAWTHORN_HOUSE': 'HH_CROCUS',
            'MEADOWBURN': 'MB_CROCUS',
            'RIVERSIDE': 'RS_PINE'
        },
        'OG_MGMT': {
            'HAWTHORN_HOUSE': 'HH_MGMT',
            'MEADOWBURN': 'MB_MGMT',
            'RIVERSIDE': 'RS_MGMT'
        }
    }

def get_staff_pool(home_name, role_name):
    """Get available staff for a home and role."""
    home = CareHome.objects.get(name=home_name)
    staff = User.objects.filter(
        unit__care_home=home,
        role__name=role_name,
        is_active=True
    ).select_related('role', 'unit')
    return list(staff)

def replicate_to_home(og_structure, target_home_name, start_date, end_date, dry_run=True):
    """Replicate OG structure to a target home."""
    print("\n" + "=" * 80)
    print(f"REPLICATING TO {target_home_name}")
    print("=" * 80)
    
    target_home = CareHome.objects.get(name=target_home_name)
    unit_mapping = get_unit_mapping()
    
    # Delete existing shifts for this home in the date range
    if not dry_run:
        deleted = Shift.objects.filter(
            unit__care_home=target_home,
            date__range=[start_date, end_date]
        ).delete()
        print(f"Deleted {deleted[0]} existing shifts")
    else:
        existing_count = Shift.objects.filter(
            unit__care_home=target_home,
            date__range=[start_date, end_date]
        ).count()
        print(f"Would delete {existing_count} existing shifts")
    
    # Build staff pools by role
    staff_pools = {}
    for role in ['SSCW', 'SSCWN', 'SCW', 'SCA', 'SCWN', 'SCAN', 'SM', 'OM']:
        staff_pools[role] = get_staff_pool(target_home_name, role)
        print(f"  {role}: {len(staff_pools[role])} staff available")
    
    # Track staff assignment rotation
    staff_rotation_index = {role: 0 for role in staff_pools.keys()}
    
    shifts_to_create = []
    current_date = start_date
    
    while current_date <= end_date:
        day_of_week = current_date.strftime('%A')
        
        if day_of_week not in og_structure:
            print(f"  WARNING: No pattern for {day_of_week}")
            current_date += timedelta(days=1)
            continue
        
        # For each OG unit, replicate to target unit
        for og_unit_name, roles_data in og_structure[day_of_week].items():
            # Get target unit name
            if og_unit_name not in unit_mapping:
                print(f"  WARNING: No mapping for {og_unit_name}")
                continue
            
            target_unit_name = unit_mapping[og_unit_name].get(target_home_name)
            if not target_unit_name:
                continue
            
            try:
                target_unit = Unit.objects.get(name=target_unit_name, care_home=target_home)
            except Unit.DoesNotExist:
                print(f"  ERROR: Unit {target_unit_name} not found")
                continue
            
            # For each role in this unit
            for role_name, shift_types_data in roles_data.items():
                if role_name not in staff_pools:
                    print(f"  WARNING: No staff pool for {role_name}")
                    continue
                
                if not staff_pools[role_name]:
                    print(f"  WARNING: No {role_name} staff available for {target_home_name}")
                    continue
                
                # For each shift type
                for shift_type_name, og_shifts in shift_types_data.items():
                    num_shifts = len(og_shifts)
                    
                    for i in range(num_shifts):
                        # Round-robin assign staff
                        staff_index = staff_rotation_index[role_name] % len(staff_pools[role_name])
                        assigned_staff = staff_pools[role_name][staff_index]
                        staff_rotation_index[role_name] += 1
                        
                        # Get shift type
                        shift_type = og_shifts[i]['shift_type']
                        
                        # Create shift
                        shift = Shift(
                            user=assigned_staff,
                            unit=target_unit,
                            shift_type=shift_type,
                            date=current_date
                        )
                        
                        shifts_to_create.append(shift)
        
        current_date += timedelta(days=1)
    
    print(f"\nTotal shifts to create: {len(shifts_to_create)}")
    
    if not dry_run:
        Shift.objects.bulk_create(shifts_to_create, batch_size=500)
        print(f"✅ Created {len(shifts_to_create)} shifts for {target_home_name}")
    else:
        print(f"🔍 DRY RUN: Would create {len(shifts_to_create)} shifts for {target_home_name}")
    
    # Summary by role
    role_counts = defaultdict(int)
    for shift in shifts_to_create:
        role_counts[shift.user.role.name] += 1
    
    print("\n--- Shifts by Role ---")
    for role, count in sorted(role_counts.items()):
        print(f"  {role}: {count}")
    
    return len(shifts_to_create)

def main():
    print("\n" + "=" * 80)
    print("ORCHARD GROVE STRUCTURE REPLICATION TOOL")
    print("=" * 80)
    
    # Date range for replication
    start_date = date(2026, 1, 11)
    end_date = date(2026, 3, 31)
    
    print(f"\nDate range: {start_date} to {end_date}")
    print(f"Total days: {(end_date - start_date).days + 1}")
    
    # Step 1: Analyze Orchard Grove
    og_structure = analyze_og_structure(start_date, end_date)
    
    # Step 2: Replicate to each home (DRY RUN first)
    print("\n" + "=" * 80)
    print("DRY RUN MODE - No changes will be made")
    print("=" * 80)
    
    for target_home in ['HAWTHORN_HOUSE', 'MEADOWBURN', 'RIVERSIDE']:
        replicate_to_home(og_structure, target_home, start_date, end_date, dry_run=True)
    
    # Ask for confirmation
    print("\n" + "=" * 80)
    print("REVIEW COMPLETE")
    print("=" * 80)
    response = input("\nProceed with actual replication? (yes/no): ")
    
    if response.lower() == 'yes':
        print("\n" + "=" * 80)
        print("EXECUTING REPLICATION")
        print("=" * 80)
        
        total_created = 0
        for target_home in ['HAWTHORN_HOUSE', 'MEADOWBURN', 'RIVERSIDE']:
            count = replicate_to_home(og_structure, target_home, start_date, end_date, dry_run=False)
            total_created += count
        
        print("\n" + "=" * 80)
        print("✅ REPLICATION COMPLETE")
        print("=" * 80)
        print(f"Total shifts created: {total_created}")
        print("\nAll 3 large homes now have identical structure to Orchard Grove!")
        print("Please restart the Gunicorn service to see changes.")
    else:
        print("\n❌ Replication cancelled")

if __name__ == '__main__':
    main()
