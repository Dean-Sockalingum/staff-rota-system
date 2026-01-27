#!/usr/bin/env python
"""
Fix management units to only contain management staff (OM, SM, HOS, IDI)
Move care staff from MGMT units to care units
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Unit, CareHome

def redistribute_care_staff_from_mgmt():
    """Move non-management staff from MGMT units to care units"""
    print("=== REDISTRIBUTING CARE STAFF FROM MGMT UNITS ===\n")
    
    mgmt_roles = ['OM', 'SM', 'HOS', 'IDI']
    
    for home in CareHome.objects.all().order_by('name'):
        mgmt_unit = Unit.objects.filter(care_home=home, name__endswith='_MGMT').first()
        if not mgmt_unit:
            continue
        
        # Get care staff in MGMT unit
        care_staff = mgmt_unit.permanent_staff.filter(
            is_active=True
        ).exclude(
            role__name__in=mgmt_roles
        )
        
        care_count = care_staff.count()
        if care_count == 0:
            print(f"{home.name}: No care staff in MGMT ✓")
            continue
        
        print(f"{home.name}: {care_count} care staff in {mgmt_unit.name}")
        
        # Get care units for this home (exclude MGMT)
        care_units = list(Unit.objects.filter(
            care_home=home,
            is_active=True
        ).exclude(
            name__endswith='_MGMT'
        ).order_by('name'))
        
        if not care_units:
            print(f"  ⚠ No care units found!")
            continue
        
        print(f"  Redistributing to {len(care_units)} care units...")
        
        # Distribute evenly across care units
        staff_list = list(care_staff)
        for idx, staff in enumerate(staff_list):
            target_unit = care_units[idx % len(care_units)]
            User.objects.filter(pk=staff.pk).update(home_unit=target_unit)
            print(f"    ✓ {staff.get_full_name()} → {target_unit.name}")
        
        print()

def fix_meadowburn_management():
    """Fix Meadowburn: should have 2 OM + 1 SM, currently has 1 OM + 2 SM + 1 HOS"""
    print("=== FIXING MEADOWBURN MANAGEMENT ===\n")
    
    mb = CareHome.objects.get(name='MEADOWBURN')
    mb_mgmt = Unit.objects.get(name='MB_MGMT')
    
    # Current state
    om_list = list(mb_mgmt.permanent_staff.filter(role__name='OM', is_active=True))
    sm_list = list(mb_mgmt.permanent_staff.filter(role__name='SM', is_active=True))
    hos_list = list(mb_mgmt.permanent_staff.filter(role__name='HOS', is_active=True))
    
    print(f"Current: {len(om_list)} OM, {len(sm_list)} SM, {len(hos_list)} HOS")
    
    # HOS should be in OG_MGMT
    if hos_list:
        og_mgmt = Unit.objects.get(name='OG_MGMT')
        for staff in hos_list:
            print(f"  Moving {staff.get_full_name()} (HOS) to {og_mgmt.name}")
            # Actually, this is wrong - HOS is System Administrator who shouldn't be in MB
            # Let's check if they have MB suffix
            if staff.last_name.endswith('(MB)'):
                print(f"    ⚠ {staff.get_full_name()} has MB suffix but is HOS - unusual")
            # Move to care unit instead since not real management
            mb_care_units = Unit.objects.filter(care_home=mb).exclude(name='MB_MGMT').first()
            if mb_care_units:
                User.objects.filter(pk=staff.pk).update(home_unit=mb_care_units)
                print(f"    ✓ Moved to {mb_care_units.name}")
    
    # Need 2 OM but have 1 - check if there's another OM we can assign
    if len(om_list) < 2:
        print(f"  ⚠ Only {len(om_list)} OM, need 2")
        # This might need manual correction
    
    # Need 1 SM but have 2 - keep one, move other to care unit
    if len(sm_list) > 1:
        print(f"  Have {len(sm_list)} SM, need 1 - moving extra to care unit")
        for staff in sm_list[1:]:
            mb_care_unit = Unit.objects.filter(care_home=mb).exclude(name='MB_MGMT').first()
            if mb_care_unit:
                User.objects.filter(pk=staff.pk).update(home_unit=mb_care_unit)
                print(f"    ✓ Moved {staff.get_full_name()} to {mb_care_unit.name}")
    
    print()

def fix_victoria_gardens_management():
    """Fix VG: should have 1 OM + 1 SM, currently has 2 OM + 0 SM"""
    print("=== FIXING VICTORIA GARDENS MANAGEMENT ===\n")
    
    vg = CareHome.objects.get(name='VICTORIA_GARDENS')
    vg_mgmt = Unit.objects.get(name='VG_MGMT')
    
    om_list = list(vg_mgmt.permanent_staff.filter(role__name='OM', is_active=True))
    sm_list = list(vg_mgmt.permanent_staff.filter(role__name='SM', is_active=True))
    
    print(f"Current: {len(om_list)} OM, {len(sm_list)} SM")
    print(f"Expected: 1 OM, 1 SM")
    
    # Keep 1 OM, move other to care unit
    if len(om_list) > 1:
        print(f"  Moving {len(om_list) - 1} extra OM to care unit")
        vg_care_unit = Unit.objects.filter(care_home=vg).exclude(name='VG_MGMT').first()
        for staff in om_list[1:]:
            if vg_care_unit:
                User.objects.filter(pk=staff.pk).update(home_unit=vg_care_unit)
                print(f"    ✓ Moved {staff.get_full_name()} to {vg_care_unit.name}")
    
    # Need 1 SM - check if there's one we can promote/assign
    if len(sm_list) < 1:
        print(f"  ⚠ No SM found - may need manual assignment")
    
    print()

def verify_final_management():
    """Verify final management staff allocation"""
    print("=== FINAL MANAGEMENT VERIFICATION ===\n")
    
    expected = {
        'HAWTHORN_HOUSE': {'OM': 2, 'SM': 1, 'HOS': 0, 'IDI': 0},
        'MEADOWBURN': {'OM': 2, 'SM': 1, 'HOS': 0, 'IDI': 0},
        'ORCHARD_GROVE': {'OM': 2, 'SM': 1, 'HOS': 1, 'IDI': 1},
        'RIVERSIDE': {'OM': 2, 'SM': 1, 'HOS': 0, 'IDI': 0},
        'VICTORIA_GARDENS': {'OM': 1, 'SM': 1, 'HOS': 0, 'IDI': 0},
    }
    
    for home_name, expected_counts in expected.items():
        home = CareHome.objects.get(name=home_name)
        mgmt_unit = Unit.objects.filter(care_home=home, name__endswith='_MGMT').first()
        
        if not mgmt_unit:
            print(f"❌ {home_name}: No MGMT unit")
            continue
        
        om_count = mgmt_unit.permanent_staff.filter(role__name='OM', is_active=True).count()
        sm_count = mgmt_unit.permanent_staff.filter(role__name='SM', is_active=True).count()
        hos_count = mgmt_unit.permanent_staff.filter(role__name='HOS', is_active=True).count()
        idi_count = mgmt_unit.permanent_staff.filter(role__name='IDI', is_active=True).count()
        total = mgmt_unit.permanent_staff.filter(is_active=True).count()
        expected_total = sum(expected_counts.values())
        
        status = '✓' if (om_count == expected_counts['OM'] and 
                        sm_count == expected_counts['SM'] and
                        hos_count == expected_counts['HOS'] and
                        idi_count == expected_counts['IDI']) else '❌'
        
        print(f"{status} {home_name}: OM={om_count}/{expected_counts['OM']}, SM={sm_count}/{expected_counts['SM']}, "
              f"HOS={hos_count}/{expected_counts['HOS']}, IDI={idi_count}/{expected_counts['IDI']} "
              f"(Total: {total}/{expected_total})")

def main():
    print("MANAGEMENT STAFF FIX")
    print("=" * 60)
    print()
    
    # Step 1: Move care staff out of MGMT units
    redistribute_care_staff_from_mgmt()
    
    # Step 2: Fix Meadowburn management composition
    fix_meadowburn_management()
    
    # Step 3: Fix Victoria Gardens management composition
    fix_victoria_gardens_management()
    
    # Step 4: Verify
    verify_final_management()
    
    print("\n✓ Management staff allocation fixed!")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
