#!/usr/bin/env python3
"""
Add 2 unique SSCWN staff to Riverside, Meadowburn, and Hawthorn House
to match Orchard Grove's staffing levels
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(__file__))
os.environ['DJANGO_SETTINGS_MODULE'] = 'rotasystems.settings'
django.setup()

from scheduling.models import User, Unit, Role

# Unique staff names for each home (Scottish names to match existing pattern)
new_staff = {
    'RIVERSIDE': [
        {'first': 'Orla', 'last': 'MacLeod', 'sap': '001720'},
        {'first': 'Rory', 'last': 'Ferguson', 'sap': '001721'},
    ],
    'MEADOWBURN': [
        {'first': 'Ailsa', 'last': 'MacKay', 'sap': '002720'},
        {'first': 'Callum', 'last': 'Murray', 'sap': '002721'},
    ],
    'HAWTHORN_HOUSE': [
        {'first': 'Freya', 'last': 'Campbell', 'sap': '003720'},
        {'first': 'Magnus', 'last': 'Stewart', 'sap': '003721'},
    ],
}

print("Adding 2 unique SSCWN staff to each home\n")

# Get SSCWN role
sscwn_role = Role.objects.get(name='SSCWN')

for home_name, staff_list in new_staff.items():
    print(f"\n{home_name}:")
    
    # Get units for this home
    units = Unit.objects.filter(care_home__name=home_name).exclude(name__contains='MGMT')
    unit_list = list(units)
    
    if len(unit_list) < 2:
        print(f"  ⚠️  Not enough units found for {home_name}")
        continue
    
    for i, staff_info in enumerate(staff_list):
        # Check if already exists
        if User.objects.filter(sap=staff_info['sap']).exists():
            print(f"  ✓ {staff_info['first']} {staff_info['last']} already exists")
            continue
        
        # Assign to a unit
        target_unit = unit_list[i % len(unit_list)]
        
        # Create new staff member
        new_staff_member = User.objects.create(
            sap=staff_info['sap'],
            first_name=staff_info['first'],
            last_name=staff_info['last'],
            email=f"{staff_info['first'].lower()}.{staff_info['last'].lower()}@carehome.com",
            role=sscwn_role,
            unit=target_unit,
            is_active=True,
            phone_number='01234567890',
            shift_preference='NIGHT',
            annual_leave_allowance=28,
        )
        new_staff_member.set_password('Password123')
        new_staff_member.save()
        
        print(f"  ✓ Added {new_staff_member.full_name} (SAP: {staff_info['sap']}) to {target_unit.name}")

print("\n✓ Staff additions complete")
print("\nUpdated SSCWN counts:")
for home in ['ORCHARD_GROVE', 'RIVERSIDE', 'MEADOWBURN', 'HAWTHORN_HOUSE']:
    count = User.objects.filter(unit__care_home__name=home, role__name='SSCWN', is_active=True).distinct().count()
    print(f"  {home}: {count} SSCWN")
