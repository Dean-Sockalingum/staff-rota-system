#!/usr/bin/env python3
"""
Fix staff assignments - move care staff OUT of MGMT units and into appropriate care units.
MGMT units should only contain SM/OM staff who work Mon-Fri 9-5.
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Unit

def redistribute_staff():
    """Move care staff from MGMT units to care units, distributing evenly"""
    
    mgmt_units = Unit.objects.filter(name__endswith='_MGMT').order_by('care_home__name')
    
    total_reassigned = 0
    
    for mgmt_unit in mgmt_units:
        home = mgmt_unit.care_home
        print(f"\n{'='*80}")
        print(f"{home.name} - {mgmt_unit.name}")
        print('='*80)
        
        # Get all care units in this home (exclude MGMT)
        care_units = Unit.objects.filter(
            care_home=home
        ).exclude(
            name__endswith='_MGMT'
        ).order_by('name')
        
        if not care_units.exists():
            print(f"⚠️  No care units found for {home.name}")
            continue
        
        # Get non-management staff assigned to MGMT unit
        misplaced_staff = User.objects.filter(
            unit=mgmt_unit
        ).exclude(
            role__name__in=['SM', 'OM', 'ADMIN', 'HOS', 'IDI']
        ).order_by('sap')
        
        if not misplaced_staff.exists():
            print(f"✅ No issues - all staff correctly assigned")
            continue
        
        print(f"\nFound {misplaced_staff.count()} care staff in MGMT unit")
        print(f"Available care units: {care_units.count()}")
        
        # Distribute staff evenly across care units
        care_unit_list = list(care_units)
        unit_index = 0
        
        for staff in misplaced_staff:
            # Round-robin assignment
            target_unit = care_unit_list[unit_index % len(care_unit_list)]
            
            print(f"  Moving: {staff.sap} {staff.full_name} ({staff.role})")
            print(f"    FROM: {mgmt_unit.name}")
            print(f"    TO:   {target_unit.name}")
            
            # Update using queryset to bypass validation
            User.objects.filter(sap=staff.sap).update(unit=target_unit)
            
            total_reassigned += 1
            unit_index += 1
    
    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print('='*80)
    print(f"Total staff reassigned: {total_reassigned}")
    
    # Verify MGMT units now only have management staff
    print(f"\n{'='*80}")
    print("VERIFICATION - MGMT Units After Fix")
    print('='*80)
    
    for mgmt_unit in Unit.objects.filter(name__endswith='_MGMT').order_by('care_home__name'):
        all_staff = User.objects.filter(unit=mgmt_unit)
        mgmt_staff = all_staff.filter(role__name__in=['SM', 'OM', 'ADMIN', 'HOS', 'IDI'])
        care_staff = all_staff.exclude(role__name__in=['SM', 'OM', 'ADMIN', 'HOS', 'IDI'])
        
        print(f"\n{mgmt_unit.care_home.name} - {mgmt_unit.name}:")
        print(f"  Management staff (SM/OM): {mgmt_staff.count()}")
        if mgmt_staff.exists():
            for s in mgmt_staff:
                print(f"    ✅ {s.sap} - {s.full_name} ({s.role})")
        
        if care_staff.exists():
            print(f"  ⚠️  Care staff still here: {care_staff.count()}")
        else:
            print(f"  ✅ No care staff (correct)")

if __name__ == '__main__':
    print("Fixing MGMT unit staff assignments...")
    redistribute_staff()
    print("\n✅ Complete!")
