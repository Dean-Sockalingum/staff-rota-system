#!/usr/bin/env python3
"""
Add 2 SSCWN staff to Riverside, Meadowburn, and Hawthorn House
to match Orchard Grove's staffing levels
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(__file__))
os.environ['DJANGO_SETTINGS_MODULE'] = 'rotasystems.settings'
django.setup()

from scheduling.models import User, Unit

# Source staff from Orchard Grove (the last 2 SSCWN)
source_saps = ['000720', '000721']  # Ruth Tyler, Sarah Clark

# Target homes
target_homes = ['RIVERSIDE', 'MEADOWBURN', 'HAWTHORN_HOUSE']

print("Adding 2 SSCWN staff to each home to match Orchard Grove\n")

for home_name in target_homes:
    print(f"\n{home_name}:")
    
    # Get units for this home
    units = Unit.objects.filter(care_home__name=home_name).exclude(name__contains='MGMT')
    unit_list = list(units)
    
    if len(unit_list) < 2:
        print(f"  ⚠️  Not enough units found for {home_name}")
        continue
    
    for i, sap in enumerate(source_saps):
        # Get source staff
        source_staff = User.objects.get(sap=sap)
        
        # Create new SAP (increment by 1000 for each home)
        home_offset = {'RIVERSIDE': 1000, 'MEADOWBURN': 2000, 'HAWTHORN_HOUSE': 3000}
        new_sap = str(int(sap) + home_offset[home_name])
        
        # Check if already exists
        if User.objects.filter(sap=new_sap).exists():
            print(f"  ✓ {source_staff.full_name} already exists as {new_sap}")
            continue
        
        # Assign to a unit
        target_unit = unit_list[i % len(unit_list)]
        
        # Clone the staff member
        new_staff = User.objects.create(
            sap=new_sap,
            first_name=source_staff.first_name,
            last_name=source_staff.last_name,
            email=f"{source_staff.first_name.lower()}.{source_staff.last_name.lower()}.{home_name.lower()}@carehome.com",
            role=source_staff.role,
            unit=target_unit,
            is_active=True,
            phone_number=source_staff.phone_number,
            shift_preference=source_staff.shift_preference,
            annual_leave_allowance=source_staff.annual_leave_allowance,
        )
        new_staff.set_password('Password123')
        new_staff.save()
        
        print(f"  ✓ Added {new_staff.full_name} (SAP: {new_sap}) to {target_unit.name}")

print("\n✓ Staff additions complete")
print("\nUpdated staff counts:")
for home in ['ORCHARD_GROVE'] + target_homes:
    count = User.objects.filter(unit__care_home__name=home, role__name='SSCWN', is_active=True).distinct().count()
    print(f"  {home}: {count} SSCWN")
