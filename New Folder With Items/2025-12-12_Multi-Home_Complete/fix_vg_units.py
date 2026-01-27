#!/usr/bin/env python
"""Fix Victoria Gardens units - remove duplicate MGMT and ensure Azalea exists"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, '/home/staff-rota-system/2025-12-12_Multi-Home_Complete')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import Unit
from scheduling.models_multi_home import CareHome

print("=" * 60)
print("VICTORIA GARDENS UNIT FIX")
print("=" * 60)

# Get Victoria Gardens
vg = CareHome.objects.get(name='VICTORIA_GARDENS')

# List current units
current_units = Unit.objects.filter(name__startswith='VG_').order_by('name')
print(f"\nCurrent VG units ({current_units.count()} total):")
for unit in current_units:
    print(f"  - {unit.name} (ID: {unit.id})")

# Check for duplicate MGMT units
mgmt_units = Unit.objects.filter(name='VG_MGMT')
print(f"\nFound {mgmt_units.count()} VG_MGMT units:")
for unit in mgmt_units:
    print(f"  - ID: {unit.id}, Care Home: {unit.care_home.name if unit.care_home else 'None'}")

# If there are duplicates, keep the first one and delete others
if mgmt_units.count() > 1:
    print("\nRemoving duplicate MGMT units...")
    keep_unit = mgmt_units.first()
    duplicates = mgmt_units.exclude(id=keep_unit.id)
    for dup in duplicates:
        print(f"  Deleting duplicate VG_MGMT (ID: {dup.id})")
        dup.delete()
    print("✓ Duplicate MGMT units removed")

# Check if Azalea exists
azalea_exists = Unit.objects.filter(name='VG_AZALEA').exists()
print(f"\nVG_AZALEA exists: {azalea_exists}")

if not azalea_exists:
    print("Creating VG_AZALEA unit...")
    azalea = Unit.objects.create(
        name='VG_AZALEA',
        care_home=vg,
        is_active=True,
        min_day_staff=2,
        min_night_staff=1,
        ideal_day_staff=3,
        ideal_night_staff=2
    )
    print(f"✓ Created {azalea.name} for {azalea.care_home.name}")

# Final verification
final_units = Unit.objects.filter(name__startswith='VG_').order_by('name')
print(f"\n{'=' * 60}")
print(f"FINAL: Victoria Gardens has {final_units.count()} units:")
for unit in final_units:
    print(f"  - {unit.name}")
print("=" * 60)
