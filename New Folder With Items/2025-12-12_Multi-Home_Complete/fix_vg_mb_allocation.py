#!/usr/bin/env python
"""
Fix Victoria Gardens and Meadowburn staff allocation.
VG should have 98 staff across 6 care units.
MB should have 178 staff across 9 units.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'staff_rota_system.settings')
django.setup()

from scheduling.models import User, Unit, CareHome

def main():
    print("VICTORIA GARDENS & MEADOWBURN STAFF ALLOCATION FIX")
    print("=" * 60)
    
    # Get care homes
    vg = CareHome.objects.get(name='VICTORIA_GARDENS')
    mb = CareHome.objects.get(name='MEADOWBURN')
    
    # Get units (excluding MGMT)
    vg_units = list(Unit.objects.filter(
        care_home=vg, 
        name__startswith='VG_'
    ).exclude(name__contains='MGMT').order_by('name'))
    
    mb_units = list(Unit.objects.filter(
        care_home=mb,
        name__startswith='MB_'
    ).exclude(name__contains='MGMT').order_by('name'))
    
    print(f"\nVictoria Gardens: {len(vg_units)} care units")
    for u in vg_units:
        print(f"  {u.name}")
    
    print(f"\nMeadowburn: {len(mb_units)} care units")
    for u in mb_units:
        print(f"  {u.name}")
    
    # Get all unallocated staff without home suffixes (HH, RS, OG)
    # These are the 283 staff that need to be split between VG (98) and MB (178)
    unallocated = User.objects.filter(
        home_unit__isnull=True,
        is_active=True
    ).exclude(
        last_name__endswith='(HH)'
    ).exclude(
        last_name__endswith='(RS)'
    ).exclude(
        last_name__endswith='(OG)'
    ).order_by('last_name', 'first_name')
    
    total_unallocated = unallocated.count()
    print(f"\nTotal unallocated staff to distribute: {total_unallocated}")
    print(f"  Target: 98 to VG, {total_unallocated - 98} to MB")
    
    # First 98 staff go to Victoria Gardens (6 units = ~16 per unit)
    vg_staff = list(unallocated[:98])
    mb_staff = list(unallocated[98:])
    
    print(f"\nAllocating {len(vg_staff)} staff to Victoria Gardens...")
    staff_per_vg_unit = len(vg_staff) // len(vg_units)
    print(f"  ~{staff_per_vg_unit} staff per unit")
    
    vg_idx = 0
    for i, unit in enumerate(vg_units):
        # Allocate staff_per_vg_unit to this unit, plus 1 extra for first few units
        count = staff_per_vg_unit + (1 if i < (len(vg_staff) % len(vg_units)) else 0)
        for _ in range(count):
            if vg_idx < len(vg_staff):
                staff = vg_staff[vg_idx]
                User.objects.filter(pk=staff.pk).update(home_unit=unit)
                vg_idx += 1
        print(f"    {unit.name}: {count} staff")
    
    print(f"\nAllocating {len(mb_staff)} staff to Meadowburn...")
    staff_per_mb_unit = len(mb_staff) // len(mb_units)
    print(f"  ~{staff_per_mb_unit} staff per unit")
    
    mb_idx = 0
    for i, unit in enumerate(mb_units):
        # Allocate staff_per_mb_unit to this unit, plus 1 extra for first few units
        count = staff_per_mb_unit + (1 if i < (len(mb_staff) % len(mb_units)) else 0)
        for _ in range(count):
            if mb_idx < len(mb_staff):
                staff = mb_staff[mb_idx]
                User.objects.filter(pk=staff.pk).update(home_unit=unit)
                mb_idx += 1
        print(f"    {unit.name}: {count} staff")
    
    # Verification
    print(f"\n\n=== VERIFICATION ===")
    vg_allocated = User.objects.filter(home_unit__care_home=vg, is_active=True).count()
    mb_allocated = User.objects.filter(home_unit__care_home=mb, is_active=True).count()
    
    print(f"VICTORIA_GARDENS: {vg_allocated} staff allocated")
    print(f"MEADOWBURN: {mb_allocated} staff allocated")
    
    remaining = User.objects.filter(
        home_unit__isnull=True,
        is_active=True
    ).exclude(
        last_name__endswith='(HH)'
    ).exclude(
        last_name__endswith='(RS)'
    ).exclude(
        last_name__endswith='(OG)'
    ).count()
    
    print(f"Remaining unallocated: {remaining}")
    print("\n✓ Complete!")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
