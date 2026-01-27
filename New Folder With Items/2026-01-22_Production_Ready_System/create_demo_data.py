#!/usr/bin/env python
"""
Create demo data for testing the staff rota system
This creates 5 care homes with units and basic data structure
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import CareHome, Unit, User, Role
from django.utils import timezone

def create_demo_data():
    """Create demo care homes and units"""
    
    print("Creating demo data...")
    
    # Get the roles
    try:
        hos_role = Role.objects.get(name='HOS')
        idi_role = Role.objects.get(name='IDI')
        sm_role = Role.objects.get(name='SM')
        om_role = Role.objects.get(name='OM')
    except Role.DoesNotExist:
        print("❌ Roles not found. Run migrations first.")
        return
    
    # Create 5 care homes (using actual model fields)
    care_homes_data = [
        {
            'name': 'ORCHARD_GROVE',
            'location_address': '123 Orchard Grove, Glasgow',
            'postcode': 'G1 1AA',
            'care_inspectorate_id': 'CS2020123456',
            'bed_capacity': 45,
            'current_occupancy': 38,
        },
        {
            'name': 'MEADOWBURN',
            'location_address': '456 Meadowburn Avenue, Glasgow',
            'postcode': 'G2 2BB',
            'care_inspectorate_id': 'CS2020234567',
            'bed_capacity': 38,
            'current_occupancy': 32,
        },
        {
            'name': 'HAWTHORN_HOUSE',
            'location_address': '789 Hawthorn Lane, Glasgow',
            'postcode': 'G3 3CC',
            'care_inspectorate_id': 'CS2020345678',
            'bed_capacity': 42,
            'current_occupancy': 35,
        },
        {
            'name': 'RIVERSIDE',
            'location_address': '321 Riverside Street, Glasgow',
            'postcode': 'G4 4DD',
            'care_inspectorate_id': 'CS2020456789',
            'bed_capacity': 35,
            'current_occupancy': 30,
        },
        {
            'name': 'VICTORIA_GARDENS',
            'location_address': '654 Victoria Drive, Glasgow',
            'postcode': 'G5 5EE',
            'care_inspectorate_id': 'CS2020567890',
            'bed_capacity': 40,
            'current_occupancy': 36,
        },
    ]
    
    care_homes = []
    for ch_data in care_homes_data:
        ch, created = CareHome.objects.get_or_create(
            name=ch_data['name'],
            defaults=ch_data
        )
        care_homes.append(ch)
        status = "✅ Created" if created else "ℹ️  Already exists"
        print(f"{status}: {ch.get_name_display()}")  # Use get_name_display() for choices field
    
    # Create units for each care home using predefined unit codes
    print("\nCreating units...")
    
    # Map care homes to their unit codes from the model
    unit_codes_map = {
        'ORCHARD_GROVE': [
            ('OG_BRAMLEY', 'Bramley'),
            ('OG_CHERRY', 'Cherry'),
            ('OG_GRAPE', 'Grape'),
        ],
        'MEADOWBURN': [
            ('MB_ASTER', 'Aster'),
            ('MB_BLUEBELL', 'Bluebell'),
            ('MB_CORNFLOWER', 'Cornflower'),
        ],
        'HAWTHORN_HOUSE': [
            ('HH_BLUEBELL', 'Bluebell'),
            ('HH_DAISY', 'Daisy'),
            ('HH_HEATHER', 'Heather'),
        ],
        'RIVERSIDE': [
            ('RS_ALDER', 'Alder'),
            ('RS_BIRCH', 'Birch'),
            ('RS_CEDAR', 'Cedar'),
        ],
        'VICTORIA_GARDENS': [
            ('VG_ROSE', 'Rose'),
            ('VG_DAFFODIL', 'Daffodil'),
            ('VG_LILY', 'Lily'),
        ],
    }
    
    for ch in care_homes:
        units_for_home = unit_codes_map.get(ch.name, [])
        for unit_code, unit_display_name in units_for_home:
            unit, created = Unit.objects.get_or_create(
                care_home=ch,
                name=unit_code,
            )
            if created:
                print(f"  ✅ Created unit: {ch.get_name_display()} - {unit_display_name}")
    
    # Assign test users to units
    print("\nAssigning test users to units...")
    test_users = User.objects.filter(sap__startswith='900')
    
    if test_users.exists():
        # Assign HOS user to first home
        hos_user = test_users.filter(role__name='HOS').first()
        if hos_user:
            first_unit = Unit.objects.filter(care_home=care_homes[0]).first()
            if first_unit:
                hos_user.unit = first_unit
                hos_user.save()
                print(f"  ✅ Assigned {hos_user.full_name} (HOS) to {first_unit.name}")
        
        # Assign other test users to different homes
        other_users = test_users.exclude(role__name='HOS')
        units = list(Unit.objects.all()[:len(other_users)])
        
        for user, unit in zip(other_users, units):
            user.unit = unit
            user.save()
            print(f"  ✅ Assigned {user.full_name} ({user.role.name}) to {unit.name}")
    
    # Summary
    print("\n" + "="*60)
    print("Demo Data Creation Complete!")
    print("="*60)
    print(f"Care Homes: {CareHome.objects.count()}")
    print(f"Units: {Unit.objects.count()}")
    print(f"Test Users: {test_users.count()}")
    print("\n✅ You can now test the system with:")
    print("   python manage.py runserver")
    print("   Login with: 900001 / TestHOS123!")

if __name__ == '__main__':
    create_demo_data()
