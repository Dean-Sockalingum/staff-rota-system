#!/usr/bin/env python
"""
Redistribute staff for Meadowburn and Victoria Gardens
- Victoria Gardens: 98 staff across 6 units
- Meadowburn: 178 staff across 9 units
"""

import os
import sys
import django
from collections import defaultdict

# Setup Django environment
sys.path.insert(0, '/home/staff-rota-system/2025-12-12_Multi-Home_Complete')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Unit
from scheduling.models_multi_home import CareHome

print("=" * 70)
print("REDISTRIBUTING MEADOWBURN AND VICTORIA GARDENS STAFF")
print("=" * 70)

# Step 1: Clear incorrect allocations
print("\nStep 1: Clearing current MB and VG allocations...")
mb_cleared = User.objects.filter(home_unit__name__startswith='MB_').update(home_unit=None)
vg_cleared = User.objects.filter(home_unit__name__startswith='VG_').update(home_unit=None)
print(f"  Cleared {mb_cleared} Meadowburn staff")
print(f"  Cleared {vg_cleared} Victoria Gardens staff")

# Step 2: Get all unallocated staff (excluding HH, RS, OG)
print("\nStep 2: Finding unallocated staff...")
unallocated = User.objects.filter(
    is_active=True,
    home_unit__isnull=True
).exclude(
    last_name__endswith='(HH)'
).exclude(
    last_name__endswith='(RS)'
).exclude(
    last_name__endswith='(OG)'
).order_by('sap', 'last_name')

total_unallocated = unallocated.count()
print(f"  Total unallocated: {total_unallocated}")
print(f"  Expected: 98 (VG) + 178 (MB) = 276")

# Step 3: Split staff - first 98 to VG, remaining to MB
print("\nStep 3: Splitting staff...")
vg_staff = list(unallocated[:98])
mb_staff = list(unallocated[98:276])  # Take next 178

print(f"  Victoria Gardens: {len(vg_staff)} staff")
print(f"  Meadowburn: {len(mb_staff)} staff")

# Get units
vg_units = list(Unit.objects.filter(name__startswith='VG_').exclude(name='VG_MGMT').order_by('name'))
mb_units = list(Unit.objects.filter(name__startswith='MB_').exclude(name='MB_MGMT').order_by('name'))

print(f"\n  VG units: {len(vg_units)} care units")
print(f"  MB units: {len(mb_units)} care units")

# Step 4: Distribute VG staff
print("\nStep 4: Distributing Victoria Gardens staff...")

# Group VG staff by role
vg_by_role = defaultdict(list)
for staff in vg_staff:
    role = str(staff.role) if staff.role else 'Unknown'
    vg_by_role[role].append(staff)

print(f"  Roles found: {dict((k, len(v)) for k, v in vg_by_role.items())}")

# Distribute evenly across 5 care units
vg_allocated = 0
for role, staff_list in sorted(vg_by_role.items()):
    per_unit = len(staff_list) // len(vg_units)
    print(f"  {role}: {per_unit} per unit")
    
    staff_idx = 0
    for unit in vg_units:
        for _ in range(per_unit):
            if staff_idx < len(staff_list):
                User.objects.filter(pk=staff_list[staff_idx].pk).update(home_unit=unit)
                vg_allocated += 1
                staff_idx += 1
    
    # Distribute remaining
    if staff_idx < len(staff_list):
        for i, staff in enumerate(staff_list[staff_idx:]):
            unit = vg_units[i % len(vg_units)]
            User.objects.filter(pk=staff.pk).update(home_unit=unit)
            vg_allocated += 1

print(f"  ✓ Allocated {vg_allocated} VG staff")

# Step 5: Distribute MB staff
print("\nStep 5: Distributing Meadowburn staff...")

# Group MB staff by role
mb_by_role = defaultdict(list)
for staff in mb_staff:
    role = str(staff.role) if staff.role else 'Unknown'
    mb_by_role[role].append(staff)

print(f"  Roles found: {dict((k, len(v)) for k, v in mb_by_role.items())}")

# Distribute evenly across 8 care units
mb_allocated = 0
for role, staff_list in sorted(mb_by_role.items()):
    per_unit = len(staff_list) // len(mb_units)
    print(f"  {role}: {per_unit} per unit")
    
    staff_idx = 0
    for unit in mb_units:
        for _ in range(per_unit):
            if staff_idx < len(staff_list):
                User.objects.filter(pk=staff_list[staff_idx].pk).update(home_unit=unit)
                mb_allocated += 1
                staff_idx += 1
    
    # Distribute remaining
    if staff_idx < len(staff_list):
        for i, staff in enumerate(staff_list[staff_idx:]):
            unit = mb_units[i % len(mb_units)]
            User.objects.filter(pk=staff.pk).update(home_unit=unit)
            mb_allocated += 1

print(f"  ✓ Allocated {mb_allocated} MB staff")

# Step 6: Verification
print("\n" + "=" * 70)
print("VERIFICATION")
print("=" * 70)

vg_final = User.objects.filter(home_unit__name__startswith='VG_', is_active=True).count()
mb_final = User.objects.filter(home_unit__name__startswith='MB_', is_active=True).count()

print(f"Victoria Gardens: {vg_final} staff allocated (target: 98)")
print(f"Meadowburn: {mb_final} staff allocated (target: 178)")

if vg_final == 98 and mb_final == 178:
    print("\n✓ SUCCESS! Staff correctly distributed")
else:
    print(f"\n⚠ Warning: Counts don't match targets")
    print(f"  VG: {vg_final} vs 98 (diff: {vg_final - 98})")
    print(f"  MB: {mb_final} vs 178 (diff: {mb_final - 178})")
