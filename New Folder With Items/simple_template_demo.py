"""
SIMPLE DEMO: New Care Home Setup Using Template
================================================

This demonstrates using the STAFFING_SETUP_TEMPLATE.md to create a new home.

We'll create a SMALL demo home (similar to Victoria Gardens):
- 5 care units
- ~50 staff (scaled down version)  
- 3-month schedule

Total setup time: ~30 seconds
"""

import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.db import transaction
from django.contrib.auth.hashers import make_password
from scheduling.models import CareHome, Unit, Role, ShiftType, User, Shift

print("=" * 70)
print("  STAFFING TEMPLATE DEMO")
print("  Creating a new care home using the template...")
print("=" * 70)
print()

# Configuration based on Template B (Medium Home - Victoria Gardens style)
HOME_NAME = "TEMPLATE_DEMO"
START_SAP = 950000
START_DATE = date.today()
END_DATE = START_DATE + timedelta(days=90)  # 3 months for demo

# Get roles
om_role = Role.objects.get(name='OM')
sm_role = Role.objects.get(name='SM')
sscw_role = Role.objects.get(name='SSCW')
sscwn_role = Role.objects.get(name='SSCWN')
scw_role = Role.objects.get(name='SCW')
scwn_role = Role.objects.get(name='SCWN')
sca_role = Role.objects.get(name='SCA')
scan_role = Role.objects.get(name='SCAN')

# Get shift types
day_shift = ShiftType.objects.get(name='DAY_0800_2000')
night_shift = ShiftType.objects.get(name='NIGHT_2000_0800')
mgmt_shift = ShiftType.objects.get(name='MGMT_DAY')

with transaction.atomic():
    print("[1/4] Creating care home and units...")
    
    # Create care home
    home = CareHome.objects.create(
        name=HOME_NAME,
        bed_capacity=75,  # 5 units × 15 beds
        care_inspectorate_id=f"CS{START_SAP}"  # Unique ID
    )
    print(f"  ✅ Created {HOME_NAME} (75 beds)")
    
    # Create management unit
    mgmt_unit = Unit.objects.create(
        care_home=home,
        name=f"{HOME_NAME}_Mgmt"
    )
    print(f"  ✅ Created management unit")
    
    # Create 5 care units
    units = []
    unit_names = ['Jasmine', 'Lavender', 'Magnolia', 'Orchid', 'Poppy']
    for unit_name in unit_names:
        unit = Unit.objects.create(
            care_home=home,
            name=f"{HOME_NAME}_{unit_name}"
        )
        units.append(unit)
        print(f"  ✅ Created {unit.name}")
    
    print(f"\n[2/4] Creating staff...")
    
    staff_list = []
    sap_counter = START_SAP
    
    # Management: 1 OM + 1 SM
    for role_name, role in [('OM', om_role), ('SM', sm_role)]:
        user = User.objects.create(
            sap=f"{sap_counter:06d}",
            email=f"{sap_counter}@template.demo",
            first_name="Demo",
            last_name=role_name,
            role=role,
            unit=mgmt_unit,
            password=make_password('Demo123##'),
            is_active=True,
            shifts_per_week_override=5,
            team='A'
        )
        staff_list.append(user)
        sap_counter += 1
    
    print(f"  ✅ Created 2 management staff")
    
    # Per-unit staff (simplified for demo - 10 staff per unit)
    teams = ['A', 'B', 'C']
    for unit_idx, unit in enumerate(units):
        # 1 SSCW, 1 SSCWN (supervisors)
        for role in [sscw_role, sscwn_role]:
            user = User.objects.create(
                sap=f"{sap_counter:06d}",
                email=f"{sap_counter}@template.demo",
                first_name=f"Supervisor",
                last_name=f"U{unit_idx+1}",
                role=role,
                unit=unit,
                password=make_password('Demo123##'),
                is_active=True,
                shifts_per_week_override=3,  # 35-hour contract
                team='A'
            )
            staff_list.append(user)
            sap_counter += 1
        
        # 4 care staff (2 day, 2 night) - mix of 24hr and 35hr contracts
        for i, role in enumerate([scw_role, sca_role, scwn_role, scan_role]):
            shifts_per_week = 2 if i % 2 == 0 else 3  # Alternate contracts
            team = teams[i % 3]
            
            user = User.objects.create(
                sap=f"{sap_counter:06d}",
                email=f"{sap_counter}@template.demo",
                first_name=f"Staff{role.name}",
                last_name=f"U{unit_idx+1}_{i+1}",
                role=role,
                unit=unit,
                password=make_password('Demo123##'),
                is_active=True,
                shifts_per_week_override=shifts_per_week,
                team=team
            )
            staff_list.append(user)
            sap_counter += 1
    
    print(f"  ✅ Created {len(staff_list) - 2} unit staff (5 units × 6 staff)")
    print(f"  📊 Total staff: {len(staff_list)}")
    
    print(f"\n[3/4] Generating 3-month shift schedules...")
    
    shifts_created = 0
    for user in staff_list:
        # Determine shift type
        if user.role in [om_role, sm_role]:
            shift_type = mgmt_shift
            is_night = False
        elif user.role in [sscwn_role, scwn_role, scan_role]:
            shift_type = night_shift
            is_night = True
        else:
            shift_type = day_shift
            is_night = False
        
        # Generate dates (simplified pattern for demo)
        current = START_DATE
        while current <= END_DATE:
            # Management: Mon-Fri
            if user.shifts_per_week_override == 5:
                if current.weekday() < 5:
                    Shift.objects.create(
                        user=user,
                        unit=user.unit,
                        shift_type=shift_type,
                        date=current,
                        status='SCHEDULED'
                    )
                    shifts_created += 1
            # 2 shifts/week: Sun & Wed
            elif user.shifts_per_week_override == 2:
                if current.weekday() in [6, 2]:  # Sun, Wed
                    Shift.objects.create(
                        user=user,
                        unit=user.unit,
                        shift_type=shift_type,
                        date=current,
                        status='SCHEDULED'
                    )
                    shifts_created += 1
            # 3 shifts/week: Mon, Wed, Fri
            elif user.shifts_per_week_override == 3:
                if current.weekday() in [0, 2, 4]:  # Mon, Wed, Fri
                    Shift.objects.create(
                        user=user,
                        unit=user.unit,
                        shift_type=shift_type,
                        date=current,
                        status='SCHEDULED'
                    )
                    shifts_created += 1
            
            current += timedelta(days=1)
    
    print(f"  ✅ Created {shifts_created:,} shifts")
    
    print(f"\n[4/4] Verifying coverage...")
    
    # Check a sample date
    sample_date = START_DATE + timedelta(days=14)
    day_shifts_count = Shift.objects.filter(
        unit__care_home=home,
        date=sample_date,
        shift_type__name__in=['DAY_0800_2000', 'MGMT_DAY']
    ).exclude(user__role__in=[sscw_role]).count()
    
    night_shifts_count = Shift.objects.filter(
        unit__care_home=home,
        date=sample_date,
        shift_type__name='NIGHT_2000_0800'
    ).exclude(user__role__in=[sscwn_role]).count()
    
    sscw_day = Shift.objects.filter(
        unit__care_home=home,
        date=sample_date,
        user__role=sscw_role
    ).count()
    
    sscwn_night = Shift.objects.filter(
        unit__care_home=home,
        date=sample_date,
        user__role=sscwn_role
    ).count()
    
    print(f"\n  Sample date: {sample_date}")
    print(f"  Day shifts: {day_shifts_count} staff + {sscw_day} SSCW supervisors")
    print(f"  Night shifts: {night_shifts_count} staff + {sscwn_night} SSCWN supervisors")

print("\n" + "=" * 70)
print("  ✅ DEMO COMPLETE!")
print("=" * 70)
print(f"\n📊 Summary:")
print(f"  Home: {HOME_NAME}")
print(f"  Staff: {len(staff_list)}")
print(f"  Units: 5 care units + 1 management")
print(f"  Shifts (3 months): {shifts_created:,}")
print()
print(f"🔑 Login credentials:")
print(f"  Any SAP: {START_SAP:06d} - {sap_counter-1:06d}")
print(f"  Password: Demo123##")
print()
print(f"🌐 View at: http://127.0.0.1:8000/")
print()
print(f"⚠️  To remove demo data:")
print(f"  CareHome.objects.filter(name='{HOME_NAME}').delete()")
print()
