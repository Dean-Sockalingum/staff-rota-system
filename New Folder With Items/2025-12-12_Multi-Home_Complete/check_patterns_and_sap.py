#!/usr/bin/env python3
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Unit, CareHome

# Target homes for standardization
target_homes = ['HAWTHORN_HOUSE', 'MEADOWBURN', 'RIVERSIDE', 'ORCHARD_GROVE']

print("="*80)
print("SHIFT PATTERN AND SAP ALIGNMENT CHECK")
print("="*80)

for home_name in target_homes:
    try:
        home = CareHome.objects.get(name=home_name)
        units = Unit.objects.filter(care_home=home)
        
        # Get active staff with shift patterns
        staff_with_patterns = User.objects.filter(
            unit__in=units,
            is_active=True
        ).select_related('unit', 'role').order_by('sap')
        
        # Count staff with and without patterns
        with_pattern = [s for s in staff_with_patterns if s.shift_pattern and s.shift_pattern.strip()]
        without_pattern = [s for s in staff_with_patterns if not s.shift_pattern or not s.shift_pattern.strip()]
        
        print(f"\n{home.get_name_display()}:")
        print(f"  Total active staff: {staff_with_patterns.count()}")
        print(f"  With shift pattern: {len(with_pattern)}")
        print(f"  Without shift pattern: {len(without_pattern)}")
        
        if without_pattern:
            print(f"\n  Missing patterns (first 10):")
            for staff in without_pattern[:10]:
                print(f"    SAP {staff.sap}: {staff.first_name} {staff.last_name} | {staff.role.get_name_display()} | Unit: {staff.unit.name}")
        
        # Show SAP range
        sap_numbers = [s.sap for s in staff_with_patterns]
        print(f"\n  SAP range: {min(sap_numbers)} to {max(sap_numbers)}")
        
        # Show pattern distribution for those who have patterns
        if with_pattern:
            pattern_counts = {}
            for staff in with_pattern:
                pattern = staff.shift_pattern
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
            
            print(f"\n  Pattern distribution:")
            for pattern, count in sorted(pattern_counts.items()):
                print(f"    {pattern}: {count} staff")
                
    except CareHome.DoesNotExist:
        print(f"\n{home_name}: NOT FOUND")

print("\n" + "="*80)
print("COMPARING ORCHARD GROVE PATTERNS TO OTHER HOMES")
print("="*80)

# Get OG staff with patterns as reference
og_home = CareHome.objects.get(name='ORCHARD_GROVE')
og_units = Unit.objects.filter(care_home=og_home)
og_staff = User.objects.filter(
    unit__in=og_units,
    is_active=True
).select_related('role', 'unit').order_by('sap')

print(f"\nOrchard Grove Pattern Structure (First 20 staff):")
for staff in og_staff[:20]:
    pattern = staff.shift_pattern or "NONE"
    print(f"  SAP {staff.sap}: {staff.role.name:8} | Pattern: {pattern:20} | Unit: {staff.unit.name}")
