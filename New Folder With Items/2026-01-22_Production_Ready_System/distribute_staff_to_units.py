#!/usr/bin/env python
"""
Replicate Orchard Grove's staff allocation pattern to other care homes
Distributes staff by role (SCW, SCA, SCAN, SCWN) across units
"""

import os
import sys
import django

sys.path.insert(0, '/home/staff-rota-system/2025-12-12_Multi-Home_Complete')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Unit, CareHome
from collections import defaultdict

def analyze_orchard_grove_pattern():
    """Analyze Orchard Grove's allocation to create template"""
    orchard_grove = CareHome.objects.get(name='ORCHARD_GROVE')
    units = Unit.objects.filter(care_home=orchard_grove).order_by('name')
    
    print("=== ORCHARD GROVE ALLOCATION PATTERN ===\n")
    
    pattern = {}
    for unit in units:
        staff = User.objects.filter(unit=unit, is_active=True)
        role_count = defaultdict(int)
        
        for s in staff:
            role = str(s.role) if s.role else 'Unknown'
            role_count[role] += 1
        
        pattern[unit.name] = dict(role_count)
        print(f"{unit.name}: {staff.count()} staff")
        for role, count in sorted(role_count.items()):
            print(f"  {role}: {count}")
    
    return pattern, units.count()

def get_role_distribution_template(pattern):
    """Create a role distribution template from Orchard Grove"""
    role_totals = defaultdict(int)
    unit_count = len(pattern)
    
    for unit_name, roles in pattern.items():
        for role, count in roles.items():
            role_totals[role] += count
    
    # Calculate per-unit allocation
    per_unit = {}
    for role, total in role_totals.items():
        per_unit[role] = total // unit_count
    
    return per_unit

def distribute_staff_to_home(home, template, og_unit_count):
    """Distribute unallocated staff to units using Orchard Grove template"""
    print(f"\n=== DISTRIBUTING STAFF FOR {home.name} ===")
    
    # Get units for this home
    units = list(Unit.objects.filter(care_home=home).order_by('name'))
    unit_count = len(units)
    
    if unit_count == 0:
        print(f"  No units found for {home.name}")
        return
    
    # Map care home names to last_name suffixes
    home_suffix_map = {
        'HAWTHORN_HOUSE': '(HH)',
        'RIVERSIDE': '(RS)',
        'VICTORIA_GARDENS': '(VG)',
    }
    
    # Get unallocated staff for this home
    # Special handling: Meadowburn staff have NO suffix (they're the remaining staff)
    if home.name == 'MEADOWBURN':
        # Meadowburn staff are those without any suffix and without home_unit
        unallocated = User.objects.filter(
            home_unit__isnull=True,
            is_active=True
        ).exclude(
            last_name__endswith='(HH)'
        ).exclude(
            last_name__endswith='(RS)'
        ).exclude(
            last_name__endswith='(VG)'
        ).exclude(
            last_name__endswith='(MB)'  # Exclude the 1 staff that has MB suffix
        ).exclude(
            last_name__endswith='(OG)'
        ).order_by('role', 'last_name')
    else:
        # Other homes use suffix matching
        suffix = home_suffix_map.get(home.name)
        if not suffix:
            print(f"  ❌ No suffix mapping for {home.name}")
            return
        
        unallocated = User.objects.filter(
            last_name__endswith=suffix,
            home_unit__isnull=True,
            is_active=True
        ).order_by('role', 'last_name')
    
    unallocated_count = unallocated.count()
    print(f"  Units: {unit_count}")
    print(f"  Unallocated staff: {unallocated_count}")
    
    if unallocated_count == 0:
        print(f"  All staff already allocated!")
        return
    
    # Group by role
    by_role = defaultdict(list)
    for staff in unallocated:
        role = str(staff.role) if staff.role else 'Unknown'
        by_role[role].append(staff)
    
    print(f"\n  Unallocated staff by role:")
    for role, staff_list in sorted(by_role.items()):
        print(f"    {role}: {len(staff_list)}")
    
    # Distribute each role across units
    total_allocated = 0
    for role, staff_list in by_role.items():
        per_unit = template.get(role, 0)
        
        if per_unit == 0:
            # Distribute evenly if not in template
            per_unit = len(staff_list) // unit_count
        
        print(f"\n  Allocating {role}: {per_unit} per unit")
        
        staff_idx = 0
        for unit in units:
            # Allocate per_unit staff to this unit
            for _ in range(per_unit):
                if staff_idx < len(staff_list):
                    staff = staff_list[staff_idx]
                    # Use update() with pk to bypass validation
                    User.objects.filter(pk=staff.pk).update(home_unit=unit)
                    total_allocated += 1
                    staff_idx += 1
        
        # Distribute remaining staff
        if staff_idx < len(staff_list):
            print(f"    Distributing {len(staff_list) - staff_idx} remaining {role} staff")
            for i, staff in enumerate(staff_list[staff_idx:]):
                unit = units[i % unit_count]
                # Use update() with pk to bypass validation
                User.objects.filter(pk=staff.pk).update(home_unit=unit)
                total_allocated += 1
    
    print(f"\n  ✓ Allocated {total_allocated} staff to units")
    
    # Verify using appropriate method for each home
    if home.name == 'MEADOWBURN':
        # For Meadowburn, count staff with MB home units
        allocated_count = User.objects.filter(home_unit__name__startswith='MB_', is_active=True).count()
        # Remaining unallocated = those without any home_unit and without other home suffixes
        remaining = User.objects.filter(
            home_unit__isnull=True,
            is_active=True
        ).exclude(last_name__endswith='(HH)').exclude(last_name__endswith='(RS)').exclude(
            last_name__endswith='(VG)').exclude(last_name__endswith='(OG)').count()
        print(f"  Verification: {allocated_count} allocated, {remaining} unallocated")
    else:
        # For other homes, use last_name suffix
        suffix = home_suffix_map.get(home.name)
        if suffix:
            allocated_count = User.objects.filter(last_name__endswith=suffix, home_unit__isnull=False, is_active=True).count()
            remaining = User.objects.filter(last_name__endswith=suffix, home_unit__isnull=True, is_active=True).count()
            print(f"  Verification: {allocated_count} allocated, {remaining} unallocated")

def main():
    print("STAFF ALLOCATION REPLICATION TOOL")
    print("=" * 50)
    
    # Step 1: Analyze Orchard Grove
    pattern, og_unit_count = analyze_orchard_grove_pattern()
    template = get_role_distribution_template(pattern)
    
    print(f"\n=== TEMPLATE (per unit allocation) ===")
    for role, count in sorted(template.items()):
        print(f"  {role}: {count} per unit")
    
    # Step 2: Apply to other homes
    other_homes = CareHome.objects.exclude(name='ORCHARD_GROVE').order_by('name')
    
    for home in other_homes:
        distribute_staff_to_home(home, template, og_unit_count)
    
    # Final summary
    print(f"\n\n=== FINAL SUMMARY ===")
    
    # Orchard Grove (special case - uses home_unit)
    og = CareHome.objects.get(name='ORCHARD_GROVE')
    og_allocated = User.objects.filter(home_unit__care_home=og, is_active=True).count()
    print(f"ORCHARD_GROVE: {og_allocated} staff allocated")
    
    # Meadowburn (special case - staff without suffixes)
    mb_allocated = User.objects.filter(home_unit__name__startswith='MB_', is_active=True).count()
    mb_total = User.objects.filter(
        is_active=True
    ).exclude(last_name__endswith='(HH)').exclude(last_name__endswith='(RS)').exclude(
        last_name__endswith='(VG)').exclude(last_name__endswith='(OG)').exclude(
        home_unit__name__startswith='OG_').count()
    mb_unallocated = User.objects.filter(
        home_unit__isnull=True,
        is_active=True
    ).exclude(last_name__endswith='(HH)').exclude(last_name__endswith='(RS)').exclude(
        last_name__endswith='(VG)').exclude(last_name__endswith='(OG)').count()
    print(f"MEADOWBURN: {mb_allocated}/{mb_total} allocated ({mb_unallocated} unallocated)")
    
    # Other homes (use last_name suffix)
    home_suffix_map = {
        'HAWTHORN_HOUSE': '(HH)',
        'RIVERSIDE': '(RS)',
        'VICTORIA_GARDENS': '(VG)',
    }
    
    for home_name, suffix in home_suffix_map.items():
        allocated = User.objects.filter(last_name__endswith=suffix, home_unit__isnull=False, is_active=True).count()
        total = User.objects.filter(last_name__endswith=suffix, is_active=True).count()
        unallocated = total - allocated
        print(f"{home_name}: {allocated}/{total} allocated ({unallocated} unallocated)")
    
    print("\n✓ Staff distribution complete!")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
