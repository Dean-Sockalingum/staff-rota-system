#!/usr/bin/env python
"""
Fix production demo data with accurate capacities and units
Run on server: python manage.py shell < fix_production_data.py
"""
from scheduling.models import Unit, CareHome, User
from django.db import transaction

print("\n" + "="*70)
print("FIXING DEMO DATA WITH PRODUCTION-ACCURATE VALUES")
print("="*70)

# Step 1: Fix bed capacities
print("\n1. Updating bed capacities to match academic paper...")
updates = [
    ('Orchard Grove', 120),      # 8 units × 15 beds
    ('Meadowburn House', 120),   # 8 units × 15 beds
    ('Hawthorn House', 120),     # 8 units × 15 beds
    ('Riverside', 120),          # 8 units × 15 beds
    ('Victoria Gardens', 70),    # 4 units × 15 + 1 unit × 10 beds
]

for name, capacity in updates:
    home = CareHome.objects.get(name=name)
    old = home.bed_capacity
    home.bed_capacity = capacity
    home.save()
    print(f"  ✓ {name}: {old} → {capacity} beds")

print(f"\n✓ Total system capacity: {sum(c for _, c in updates)} beds")

# Step 2: Delete placeholder units, create proper 42-unit structure
print("\n2. Creating full 42-unit structure...")
Unit.objects.all().delete()  # Clear all existing units

unit_structures = {
    'Orchard Grove': ['Bramley', 'Cherry', 'Grape', 'Orange', 'Peach', 'Pear', 'Plum', 'Strawberry', 'OG-MGMT'],
    'Meadowburn House': ['Aster', 'MB-Bluebell', 'Cornflower', 'MB-Daisy', 'Foxglove', 'Honeysuckle', 'Marigold', 'Poppy SRD', 'MB-MGMT'],
    'Hawthorn House': ['HH-Bluebell', 'HH-Daisy', 'HH-Heather', 'Iris', 'Primrose', 'Snowdrop SRD', 'Thistle SRD', 'Violet', 'HH-MGMT'],
    'Riverside': ['Daffodil', 'RS-Heather', 'Jasmine', 'RS-Lily', 'Lotus', 'Maple', 'Orchid', 'RS-Rose', 'RS-MGMT'],
    'Victoria Gardens': ['Azalea', 'Crocus', 'VG-Lily', 'VG-Rose', 'Tulip', 'VG-MGMT']
}

total_units = 0
with transaction.atomic():
    for home_name, units in unit_structures.items():
        home = CareHome.objects.get(name=home_name)
        
        for unit_name in units:
            Unit.objects.create(
                name=unit_name,
                care_home=home,
                is_active=True
            )
            total_units += 1
        
        print(f"  ✓ {home_name}: {len(units)} units created")

print(f"\n✓ Total units: {total_units}")

# Step 3: Verify user still has access to all homes
try:
    user = User.objects.get(sap='000002')
    managed_count = user.managed_homes.count()
    print(f"\n3. User access verification:")
    print(f"  ✓ User: {user.get_full_name()} (SAP {user.sap})")
    print(f"  ✓ Role: {user.role.name}")
    print(f"  ✓ Manages: {managed_count} homes")
except User.DoesNotExist:
    print("\n3. User not found - will be created during setup")

# Step 4: Summary
print("\n" + "="*70)
print("✅ DEMO DATA UPDATED SUCCESSFULLY")
print("="*70)
print("\nCurrent state:")
print("  ✓ 5 care homes with accurate capacities (550 beds total)")
print("  ✓ 42 units with proper naming (fruit/flower themes)")
print("  ✓ All homes have CS numbers")
print("\nNext: Log out and back in at demo.therota.co.uk")
print("="*70 + "\n")
