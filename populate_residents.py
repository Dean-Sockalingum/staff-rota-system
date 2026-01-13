#!/usr/bin/env python3
"""
Populate Residents for Care Homes
Create residents with varying occupancy levels (80-100%)
"""

import os
import django
import random
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import CareHome, Unit, Resident, User

# Scottish first names (male and female)
FIRST_NAMES = [
    'James', 'John', 'Robert', 'William', 'David', 'Thomas', 'Charles', 'George',
    'Mary', 'Margaret', 'Elizabeth', 'Catherine', 'Helen', 'Jean', 'Ann', 'Agnes',
    'Andrew', 'Alexander', 'Donald', 'Kenneth', 'Ian', 'Duncan', 'Angus', 'Malcolm',
    'Moira', 'Fiona', 'Isla', 'Eileen', 'Janet', 'Flora', 'Aileen', 'Sheila'
]

# Scottish surnames
LAST_NAMES = [
    'MacLeod', 'MacDonald', 'Campbell', 'Stewart', 'Robertson', 'Thomson', 'Anderson',
    'Scott', 'Murray', 'Cameron', 'Ross', 'Ferguson', 'Grant', 'Wilson', 'Brown',
    'Young', 'Mitchell', 'Watson', 'Taylor', 'Davidson', 'Clark', 'Reid', 'Morrison',
    'Smith', 'Miller', 'Fraser', 'Kennedy', 'Gordon', 'Hamilton', 'Graham', 'Johnston'
]

def get_random_dob():
    """Generate random date of birth for elderly residents (75-95 years old)"""
    today = date.today()
    age_years = random.randint(75, 95)
    age_days = random.randint(0, 364)
    dob = today - timedelta(days=(age_years * 365) + age_days)
    return dob

def get_random_admission_date():
    """Generate random admission date (within last 5 years)"""
    today = date.today()
    days_ago = random.randint(30, 1825)  # 1 month to 5 years
    return today - timedelta(days=days_ago)

def populate_home(home_name, occupancy_percentage):
    """Populate a care home with residents at specified occupancy"""
    
    home = CareHome.objects.get(name=home_name, is_active=True)
    units = Unit.objects.filter(care_home=home, is_active=True).exclude(name__contains='MGMT').order_by('name')
    
    # Calculate capacity: Victoria Gardens has 4x15 + 1x10 = 70 beds, others have 15 beds per unit
    if home_name == 'VICTORIA_GARDENS':
        total_capacity = 70  # 4 units @ 15 beds + 1 unit @ 10 beds
    else:
        total_capacity = units.count() * 15
    
    target_residents = int(total_capacity * occupancy_percentage / 100)
    
    print(f"\n{home.get_name_display()}:")
    print(f"  Units: {units.count()}")
    print(f"  Capacity: {total_capacity} beds")
    print(f"  Target Occupancy: {occupancy_percentage}% ({target_residents} residents)")
    
    # Distribute residents across units
    residents_per_unit = target_residents // units.count()
    extra_residents = target_residents % units.count()
    
    resident_count = 0
    used_ids = set()
    
    for idx, unit in enumerate(units):
        # Victoria Gardens: VG_AZALEA has 10 beds, others have 15
        if home_name == 'VICTORIA_GARDENS' and unit.name == 'VG_AZALEA':
            max_beds = 10
        else:
            max_beds = 15
        
        # Calculate how many residents for this unit
        unit_residents = min(residents_per_unit + (1 if idx < extra_residents else 0), max_beds)
        
        for room_num in range(1, unit_residents + 1):
            # Generate unique resident ID
            while True:
                resident_id = f"{home_name[:2]}{random.randint(1000, 9999)}"
                if resident_id not in used_ids:
                    used_ids.add(resident_id)
                    break
            
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            dob = get_random_dob()
            admission_date = get_random_admission_date()
            
            # Get a keyworker from this unit if available
            keyworker = User.objects.filter(
                unit=unit,
                role__name__in=['SCW', 'SCWN', 'SCA', 'SCAN'],
                is_active=True
            ).first()
            
            resident = Resident.objects.create(
                resident_id=resident_id,
                first_name=first_name,
                last_name=last_name,
                date_of_birth=dob,
                room_number=str(room_num),
                admission_date=admission_date,
                unit=unit,
                keyworker=keyworker,
                is_active=True,
                discharge_reason=''
            )
            
            resident_count += 1
    
    print(f"  ✓ Created {resident_count} residents")
    actual_occupancy = (resident_count / total_capacity) * 100
    print(f"  Actual Occupancy: {actual_occupancy:.1f}%")
    
    return resident_count

def main():
    print("=" * 70)
    print("POPULATING RESIDENTS FOR CARE HOMES")
    print("Varying occupancy levels: 80-100%")
    print("=" * 70)
    
    # Check Orchard Grove (should already have 120)
    og_count = Resident.objects.filter(
        unit__care_home__name='ORCHARD_GROVE',
        is_active=True
    ).count()
    print(f"\nOrchard Grove: Already has {og_count} residents (100% occupancy)")
    
    # Populate other homes with varying occupancy
    homes_to_populate = [
        ('HAWTHORN_HOUSE', 95),      # 95% = 114 residents (out of 120)
        ('MEADOWBURN', 88),           # 88% = 106 residents (out of 120)
        ('RIVERSIDE', 92),            # 92% = 110 residents (out of 120)
        ('VICTORIA_GARDENS', 83),     # 83% = 58 residents (out of 70: 4×15 + 1×10)
    ]
    
    total_added = 0
    for home_name, occupancy in homes_to_populate:
        count = populate_home(home_name, occupancy)
        total_added += count
    
    print("\n" + "=" * 70)
    print(f"SUMMARY:")
    print(f"  Total residents added: {total_added}")
    print(f"  Total residents across all homes: {Resident.objects.filter(is_active=True).count()}")
    print("=" * 70)
    
    # Show final breakdown
    print("\nFINAL OCCUPANCY BY HOME:")
    homes = CareHome.objects.filter(is_active=True).order_by('name')
    for home in homes:
        units = Unit.objects.filter(care_home=home, is_active=True).exclude(name__contains='MGMT')
        # Victoria Gardens: 4×15 + 1×10 = 70 beds
        if home.name == 'VICTORIA_GARDENS':
            capacity = 70
        else:
            capacity = units.count() * 15
        residents = Resident.objects.filter(unit__care_home=home, is_active=True).count()
        occupancy = (residents / capacity * 100) if capacity > 0 else 0
        print(f"  {home.get_name_display()}: {residents}/{capacity} beds ({occupancy:.1f}%)")
    
    print("\n✓ All residents successfully populated!")

if __name__ == '__main__':
    main()
