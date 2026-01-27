#!/usr/bin/env python3
"""
Fix MGMT unit staff assignments.

MGMT units should only contain SM (Service Manager) and OM (Operations Manager) staff.
All care roles (SCA, SCAN, SCW, SCWN, SSCW, SSCWN) should be moved to care units.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Unit, Shift
from django.db.models import Count

print("🔧 Fixing MGMT Unit Staff Assignments")
print("=" * 60)

# Define care roles that should NOT be in MGMT units
CARE_ROLES = ['SCA', 'SCAN', 'SCW', 'SCWN', 'SSCW', 'SSCWN']
MGMT_ROLES = ['SM', 'OM']

# Get all staff currently in MGMT units who are not SM/OM
misplaced_staff = User.objects.filter(
    is_active=True,
    unit__name__icontains='MGMT',
    role__name__in=CARE_ROLES
).exclude(sap='000745').select_related('unit', 'role')

print(f"\n📋 Found {misplaced_staff.count()} care staff incorrectly assigned to MGMT units")

# Group by care home for processing
care_homes = {
    'OG': 'ORCHARD_GROVE',
    'HH': 'HAWTHORN_HOUSE', 
    'MB': 'MEADOWBURN',
    'RS': 'RIVERSIDE',
    'VG': 'VICTORIA_GARDENS'
}

fixed_count = 0
errors = 0

for staff in misplaced_staff:
    try:
        # Extract care home prefix from current MGMT unit
        current_unit = staff.unit.name
        home_prefix = current_unit.split('_')[0]  # e.g., 'HH' from 'HH_MGMT'
        
        # Find the most frequently worked care unit for this staff member based on shifts
        most_common_unit = Shift.objects.filter(
            user=staff,
            unit__name__startswith=home_prefix,
            unit__name__icontains='MGMT',
            unit__name__iexact=False  # Exclude MGMT units
        ).exclude(
            unit__name__icontains='MGMT'
        ).values('unit').annotate(
            count=Count('id')
        ).order_by('-count').first()
        
        # If found shifts in care units, use that
        if most_common_unit:
            new_unit = Unit.objects.get(id=most_common_unit['unit'])
            staff.unit = new_unit
            staff.home_unit = new_unit
            staff.save()
            print(f"  ✓ {staff.sap} {staff.first_name} {staff.last_name} ({staff.role.name}): {current_unit} → {new_unit.name}")
            fixed_count += 1
        else:
            # No shift history - assign to first available care unit in same home
            care_units = Unit.objects.filter(
                name__startswith=home_prefix
            ).exclude(
                name__icontains='MGMT'
            ).order_by('name')
            
            if care_units.exists():
                # Distribute evenly - find unit with fewest staff
                unit_with_least_staff = None
                min_staff_count = float('inf')
                
                for unit in care_units:
                    staff_count = User.objects.filter(unit=unit, is_active=True).count()
                    if staff_count < min_staff_count:
                        min_staff_count = staff_count
                        unit_with_least_staff = unit
                
                staff.unit = unit_with_least_staff
                staff.home_unit = unit_with_least_staff
                staff.save()
                print(f"  ✓ {staff.sap} {staff.first_name} {staff.last_name} ({staff.role.name}): {current_unit} → {unit_with_least_staff.name} (no shift history)")
                fixed_count += 1
            else:
                print(f"  ✗ ERROR: No care units found for {home_prefix}")
                errors += 1
                
    except Exception as e:
        print(f"  ✗ ERROR processing {staff.sap}: {e}")
        errors += 1

print(f"\n{'=' * 60}")
print(f"✅ Fixed: {fixed_count} staff")
print(f"❌ Errors: {errors}")

# Verify fix
print(f"\n{'=' * 60}")
print("📊 VERIFICATION - Staff in MGMT Units by Role:")

mgmt_staff = User.objects.filter(
    is_active=True,
    unit__name__icontains='MGMT'
).exclude(sap='000745').values(
    'role__name', 'unit__name'
).annotate(
    count=Count('sap')
).order_by('unit__name', '-count')

for item in mgmt_staff:
    role = item['role__name']
    symbol = '✓' if role in MGMT_ROLES else '✗'
    print(f"  {symbol} {item['unit__name']:15s} - {role:10s}: {item['count']:3d} staff")

# Check if any care roles remain in MGMT
remaining_care_in_mgmt = User.objects.filter(
    is_active=True,
    unit__name__icontains='MGMT',
    role__name__in=CARE_ROLES
).exclude(sap='000745').count()

print(f"\n{'=' * 60}")
if remaining_care_in_mgmt == 0:
    print("✅ SUCCESS: All MGMT units now contain only SM and OM staff")
else:
    print(f"⚠️  WARNING: {remaining_care_in_mgmt} care staff still in MGMT units")

print(f"{'=' * 60}")
