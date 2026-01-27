#!/usr/bin/env python3
"""
Clone Orchard Grove staffing model to other 120-bed homes
All 120-bed homes should have identical staffing structure to Orchard Grove
"""

import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import CareHome, Unit, User, Role, Shift
from django.db.models import Count

# Scottish first names
FIRST_NAMES = [
    'James', 'John', 'Robert', 'William', 'David', 'Thomas', 'Charles', 'George',
    'Mary', 'Margaret', 'Elizabeth', 'Catherine', 'Helen', 'Jean', 'Ann', 'Agnes',
    'Andrew', 'Alexander', 'Donald', 'Kenneth', 'Ian', 'Duncan', 'Angus', 'Malcolm',
    'Moira', 'Fiona', 'Isla', 'Eileen', 'Janet', 'Flora', 'Aileen', 'Sheila',
    'Colin', 'Stuart', 'Ewan', 'Fraser', 'Gordon', 'Bruce', 'Neil', 'Craig',
    'Alison', 'Catriona', 'Kirsty', 'Nicola', 'Rachel', 'Sarah', 'Laura', 'Emma'
]

LAST_NAMES = [
    'MacLeod', 'MacDonald', 'Campbell', 'Stewart', 'Robertson', 'Thomson', 'Anderson',
    'Scott', 'Murray', 'Cameron', 'Ross', 'Ferguson', 'Grant', 'Wilson', 'Brown',
    'Young', 'Mitchell', 'Watson', 'Taylor', 'Davidson', 'Clark', 'Reid', 'Morrison',
    'Smith', 'Miller', 'Fraser', 'Kennedy', 'Gordon', 'Hamilton', 'Graham', 'Johnston',
    'Wallace', 'Bell', 'Russell', 'Hunter', 'Duncan', 'Simpson', 'Kerr', 'Paterson'
]

def get_orchard_grove_structure():
    """Analyze Orchard Grove's staffing structure"""
    og = CareHome.objects.get(name='ORCHARD_GROVE')
    og_units = Unit.objects.filter(care_home=og, is_active=True).exclude(name__contains='MGMT').order_by('name')
    
    print("\n" + "="*70)
    print("ORCHARD GROVE STAFFING STRUCTURE (Master Template)")
    print("="*70)
    
    # Get staffing by role
    og_staff = User.objects.filter(
        unit__care_home=og,
        is_active=True,
        unit__is_active=True
    ).exclude(unit__name__contains='MGMT')
    
    role_breakdown = og_staff.values('role__name').annotate(count=Count('sap')).order_by('-count')
    
    print(f"\nTotal Staff: {og_staff.count()}")
    print(f"Total Care Units: {og_units.count()}")
    print("\nRole Breakdown:")
    for role in role_breakdown:
        print(f"  {role['role__name']}: {role['count']}")
    
    # Get staff distribution per unit
    print("\nStaff per Unit:")
    for unit in og_units:
        unit_staff = og_staff.filter(unit=unit)
        print(f"  {unit.name}: {unit_staff.count()} staff")
        role_dist = unit_staff.values('role__name').annotate(count=Count('sap')).order_by('role__name')
        for rd in role_dist:
            print(f"    - {rd['role__name']}: {rd['count']}")
    
    return {
        'total_staff': og_staff.count(),
        'units': list(og_units),
        'role_breakdown': {r['role__name']: r['count'] for r in role_breakdown},
        'unit_distribution': {
            unit.name: {
                'total': og_staff.filter(unit=unit).count(),
                'roles': {
                    rd['role__name']: rd['count'] 
                    for rd in og_staff.filter(unit=unit).values('role__name').annotate(count=Count('sap'))
                }
            }
            for unit in og_units
        }
    }

def clone_to_home(target_home_name, og_structure):
    """Clone Orchard Grove structure to target home"""
    
    print(f"\n" + "="*70)
    print(f"CLONING TO {target_home_name}")
    print("="*70)
    
    target_home = CareHome.objects.get(name=target_home_name)
    target_units = list(Unit.objects.filter(
        care_home=target_home, 
        is_active=True
    ).exclude(name__contains='MGMT').order_by('name'))
    
    if len(target_units) != len(og_structure['units']):
        print(f"ERROR: Unit count mismatch! OG has {len(og_structure['units'])}, {target_home_name} has {len(target_units)}")
        return 0
    
    # Delete existing staff (except management)
    existing_staff = User.objects.filter(
        unit__care_home=target_home,
        is_active=True
    ).exclude(unit__name__contains='MGMT')
    
    print(f"Deleting {existing_staff.count()} existing staff...")
    existing_staff.delete()
    
    # Track used SAP numbers
    existing_saps = set(User.objects.values_list('sap', flat=True))
    used_names = set()
    
    created_count = 0
    
    # Clone staff for each unit
    for og_unit, target_unit in zip(og_structure['units'], target_units):
        unit_name_map = {
            'OG_PEACH': target_unit.name,
            'OG_ORANGE': target_unit.name,
            'OG_PEAR': target_unit.name,
            'OG_APPLE': target_unit.name,
            'OG_PLUM': target_unit.name,
            'OG_CHERRY': target_unit.name,
            'OG_APRICOT': target_unit.name,
            'OG_GRAPE': target_unit.name
        }
        
        print(f"\n  Cloning {og_unit.name} → {target_unit.name}")
        
        # Get OG staff for this unit
        og_unit_staff = User.objects.filter(
            unit__name=og_unit.name,
            unit__care_home__name='ORCHARD_GROVE',
            is_active=True
        ).select_related('role')
        
        for og_staff in og_unit_staff:
            # Generate unique SAP
            while True:
                sap = f"{random.randint(100000, 999999):06d}"
                if sap not in existing_saps:
                    existing_saps.add(sap)
                    break
            
            # Generate unique name
            while True:
                first_name = random.choice(FIRST_NAMES)
                last_name = random.choice(LAST_NAMES)
                full_name = f"{first_name} {last_name}"
                if full_name not in used_names:
                    used_names.add(full_name)
                    break
            
            # Create cloned staff member
            new_staff = User.objects.create(
                sap=sap,
                first_name=first_name,
                last_name=last_name,
                email=f"{sap}@tempmail.com",
                password='pbkdf2_sha256$870000$dummy$dummy',  # Dummy hashed password
                role=og_staff.role,
                unit=target_unit,
                is_active=True,
                is_staff=False,
                annual_leave_allowance=og_staff.annual_leave_allowance,
                annual_leave_used=0,
                annual_leave_year_start=og_staff.annual_leave_year_start,
                team=og_staff.team,
                shift_preference=og_staff.shift_preference,
                shifts_per_week_override=og_staff.shifts_per_week_override
            )
            new_staff.set_password('Staffrota2026TQM')
            new_staff.save()
            
            # Clone first 3 weeks of shifts (repeating pattern)
            # Get earliest date for this staff member
            first_shift = Shift.objects.filter(user=og_staff).order_by('date').first()
            if first_shift:
                from datetime import timedelta
                end_date = first_shift.date + timedelta(days=21)  # 3 weeks
                og_shifts = Shift.objects.filter(
                    user=og_staff,
                    date__gte=first_shift.date,
                    date__lt=end_date
                )
                
                shifts_to_create = []
                for og_shift in og_shifts:
                    shifts_to_create.append(Shift(
                        user=new_staff,
                        unit=target_unit,
                        shift_type=og_shift.shift_type,
                        date=og_shift.date,
                        status=og_shift.status,
                        shift_classification=og_shift.shift_classification,
                        shift_pattern=og_shift.shift_pattern,
                        custom_start_time=og_shift.custom_start_time,
                        custom_end_time=og_shift.custom_end_time,
                        notes=og_shift.notes
                    ))
                
                # Bulk create shifts
                if shifts_to_create:
                    Shift.objects.bulk_create(shifts_to_create, ignore_conflicts=True)
            
            created_count += 1
        
        unit_count = og_unit_staff.count()
        print(f"    ✓ Created {unit_count} staff with shifts")
    
    print(f"\n✓ Total staff cloned to {target_home_name}: {created_count}")
    
    # Verify
    final_count = User.objects.filter(
        unit__care_home=target_home,
        is_active=True
    ).exclude(unit__name__contains='MGMT').count()
    
    print(f"  Final staff count: {final_count}")
    print(f"  Expected: {og_structure['total_staff']}")
    
    if final_count == og_structure['total_staff']:
        print(f"  ✓ MATCH!")
    else:
        print(f"  ✗ MISMATCH!")
    
    return created_count

def main():
    print("="*70)
    print("CLONING ORCHARD GROVE STAFFING MODEL")
    print("Target: All 120-bed homes (Hawthorn House, Meadowburn, Riverside)")
    print("="*70)
    
    # Get Orchard Grove structure
    og_structure = get_orchard_grove_structure()
    
    # Clone to each 120-bed home
    homes_to_clone = [
        'HAWTHORN_HOUSE',
        'MEADOWBURN',
        'RIVERSIDE'
    ]
    
    total_cloned = 0
    for home in homes_to_clone:
        count = clone_to_home(home, og_structure)
        total_cloned += count
    
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    print(f"Total staff cloned: {total_cloned}")
    print(f"Total shifts cloned: {Shift.objects.count()}")
    
    # Show final breakdown
    print("\nFinal Staff Count by Home:")
    all_homes = CareHome.objects.filter(is_active=True).order_by('name')
    for home in all_homes:
        staff_count = User.objects.filter(
            unit__care_home=home,
            is_active=True
        ).exclude(unit__name__contains='MGMT').count()
        print(f"  {home.get_name_display()}: {staff_count} staff")
    
    print("\n✓ Cloning complete!")

if __name__ == '__main__':
    main()
