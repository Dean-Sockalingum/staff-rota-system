#!/usr/bin/env python
"""
Fix unit structure and management staff allocation
- Ensure each home has correct number of units (8 care + 1 mgmt, except VG with 5 care + 1 mgmt)
- Move management staff to MGMT units
- Remove duplicate VICTORIA_MGMT unit
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Unit, CareHome

def fix_victoria_gardens_units():
    """Remove duplicate management unit and ensure 6 units total"""
    print("=== FIXING VICTORIA GARDENS UNITS ===\n")
    
    vg = CareHome.objects.get(name='VICTORIA_GARDENS')
    vg_units = Unit.objects.filter(care_home=vg)
    
    print(f"Current VG units: {vg_units.count()}")
    for unit in vg_units:
        print(f"  - {unit.name}")
    
    # Check if VICTORIA_MGMT exists and has no staff
    victoria_mgmt = Unit.objects.filter(name='VICTORIA_MGMT').first()
    if victoria_mgmt:
        staff_count = victoria_mgmt.permanent_staff.filter(is_active=True).count()
        print(f"\nVICTORIA_MGMT has {staff_count} staff")
        if staff_count == 0:
            print("  Deleting duplicate VICTORIA_MGMT unit...")
            victoria_mgmt.delete()
            print("  ✓ Deleted")
        else:
            print("  ⚠ Has staff - moving them to VG_MGMT first")
            vg_mgmt = Unit.objects.get(name='VG_MGMT')
            victoria_mgmt.permanent_staff.all().update(home_unit=vg_mgmt)
            print(f"  Moved {staff_count} staff to VG_MGMT")
            victoria_mgmt.delete()
            print("  ✓ Deleted")
    
    print(f"\nFinal VG units: {Unit.objects.filter(care_home=vg).count()}")

def assign_management_to_mgmt_units():
    """Move all management staff (OM, SM, HOS, IDI) to their home's MGMT unit"""
    print("\n=== ASSIGNING MANAGEMENT STAFF TO MGMT UNITS ===\n")
    
    # Home suffix to MGMT unit mapping
    home_mgmt_map = {
        '(HH)': 'HH_MGMT',
        '(MB)': 'MB_MGMT',
        '(RS)': 'RS_MGMT',
        '(VG)': 'VG_MGMT',
    }
    
    mgmt_roles = ['OM', 'SM', 'HOS', 'IDI']
    
    for role_name in mgmt_roles:
        staff_list = User.objects.filter(role__name=role_name, is_active=True)
        print(f"{role_name}: {staff_list.count()} staff")
        
        for staff in staff_list:
            # Determine which home this staff belongs to
            target_mgmt_unit = None
            
            # Check by last_name suffix
            for suffix, mgmt_unit_name in home_mgmt_map.items():
                if staff.last_name.endswith(suffix):
                    target_mgmt_unit = Unit.objects.get(name=mgmt_unit_name)
                    break
            
            # If no suffix, check current home_unit's care_home
            if not target_mgmt_unit and staff.home_unit and staff.home_unit.care_home:
                care_home_name = staff.home_unit.care_home.name
                mgmt_unit_name = f"{care_home_name.split('_')[0]}_MGMT"
                if care_home_name == 'HAWTHORN_HOUSE':
                    mgmt_unit_name = 'HH_MGMT'
                elif care_home_name == 'MEADOWBURN':
                    mgmt_unit_name = 'MB_MGMT'
                elif care_home_name == 'RIVERSIDE':
                    mgmt_unit_name = 'RS_MGMT'
                elif care_home_name == 'VICTORIA_GARDENS':
                    mgmt_unit_name = 'VG_MGMT'
                elif care_home_name == 'ORCHARD_GROVE':
                    mgmt_unit_name = 'OG_MGMT'
                
                try:
                    target_mgmt_unit = Unit.objects.get(name=mgmt_unit_name)
                except Unit.DoesNotExist:
                    pass
            
            # Default to OG_MGMT for HOS and IDI if no home identified
            if not target_mgmt_unit and role_name in ['HOS', 'IDI']:
                target_mgmt_unit = Unit.objects.get(name='OG_MGMT')
            
            if target_mgmt_unit:
                old_unit = staff.home_unit
                if old_unit != target_mgmt_unit:
                    User.objects.filter(pk=staff.pk).update(home_unit=target_mgmt_unit)
                    print(f"  ✓ {staff.get_full_name()}: {old_unit} → {target_mgmt_unit.name}")
                else:
                    print(f"  - {staff.get_full_name()}: already in {target_mgmt_unit.name}")
            else:
                print(f"  ⚠ {staff.get_full_name()}: Could not determine MGMT unit")
        print()

def verify_final_state():
    """Verify all homes have correct unit counts and staff distribution"""
    print("=== FINAL VERIFICATION ===\n")
    
    expected = {
        'HAWTHORN_HOUSE': 9,
        'MEADOWBURN': 9,
        'ORCHARD_GROVE': 9,
        'RIVERSIDE': 9,
        'VICTORIA_GARDENS': 6,
    }
    
    for home in CareHome.objects.all().order_by('name'):
        units = Unit.objects.filter(care_home=home, is_active=True)
        unit_count = units.count()
        staff_count = User.objects.filter(home_unit__care_home=home, is_active=True).count()
        
        expected_units = expected.get(home.name, '?')
        status = '✓' if unit_count == expected_units else '❌'
        
        print(f"{status} {home.name}: {unit_count}/{expected_units} units, {staff_count} staff")
        
        # Show MGMT unit staff count
        mgmt_unit = units.filter(name__endswith='_MGMT').first()
        if mgmt_unit:
            mgmt_staff = mgmt_unit.permanent_staff.filter(is_active=True).count()
            print(f"    MGMT unit: {mgmt_staff} staff")

def main():
    print("UNIT STRUCTURE AND MANAGEMENT FIX")
    print("=" * 60)
    print()
    
    # Step 1: Fix Victoria Gardens duplicate unit
    fix_victoria_gardens_units()
    
    # Step 2: Assign management staff to MGMT units
    assign_management_to_mgmt_units()
    
    # Step 3: Verify
    verify_final_state()
    
    print("\n✓ Unit structure and management allocation fixed!")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
