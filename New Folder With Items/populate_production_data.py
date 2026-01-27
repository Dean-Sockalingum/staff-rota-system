"""
Populate PostgreSQL Production Database with Essential Data
Creates Care Homes, Units, Roles, and Sample Staff
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import Unit, Role, User
from scheduling.models_multi_home import CareHome
from django.db import transaction

def populate_data():
    print("🚀 Starting Production Data Population")
    print("=" * 60)
    
    with transaction.atomic():
        # 1. Create Care Home
        print("\n📍 Creating Care Home...")
        care_home, created = CareHome.objects.get_or_create(
            name="ORCHARD_GROVE",
            defaults={
                'bed_capacity': 60,
                'current_occupancy': 45,
                'location_address': '123 Main Street, Edinburgh',
                'postcode': 'EH1 1AA',
                'care_inspectorate_id': 'CS2021123456',
                'is_active': True
            }
        )
        display_name = dict(CareHome.HOME_CHOICES).get(care_home.name, care_home.name)
        if created:
            print(f"  ✓ Created: {display_name}")
        else:
            print(f"  ✓ Exists: {display_name}")
        
        # 2. Create Units
        print("\n🏢 Creating Care Units...")
        units_data = [
            {'name': 'OG_BRAMLEY', 'description': 'Bramley Wing'},
            {'name': 'OG_CHERRY', 'description': 'Cherry Wing'},
            {'name': 'OG_GRAPE', 'description': 'Grape Wing'},
            {'name': 'OG_ORANGE', 'description': 'Orange Wing'},
            {'name': 'OG_PEACH', 'description': 'Peach Wing - Dementia Care'},
            {'name': 'OG_PEAR', 'description': 'Pear Wing'},
            {'name': 'OG_PLUM', 'description': 'Plum Wing'},
            {'name': 'OG_STRAWBERRY', 'description': 'Strawberry Wing'},
            {'name': 'OG_MGMT', 'description': 'Orchard Grove Management'},
        ]
        
        units = {}
        for unit_data in units_data:
            unit, created = Unit.objects.get_or_create(
                name=unit_data['name'],
                care_home=care_home,
                defaults={
                    'description': unit_data['description'],
                    'is_active': True,
                    'min_day_staff': 2,
                    'min_night_staff': 1
                }
            )
            units[unit.name] = unit
            display_name = dict(Unit.UNIT_CHOICES).get(unit.name, unit.name)
            status = "Created" if created else "Exists"
            print(f"  ✓ {status}: {display_name}")
        
        # 3. Create Roles
        print("\n👥 Creating Staff Roles...")
        roles_data = [
            {'name': 'Director', 'is_management': True, 'description': 'Director - Full system access'},
            {'name': 'Service Manager', 'is_management': True, 'description': 'Service Manager - Care home management'},
            {'name': 'Operations Manager', 'is_management': True, 'description': 'Operations Manager - Operational oversight'},
            {'name': 'Senior Carer', 'is_management': False, 'description': 'Senior Carer - Supervisory care role'},
            {'name': 'Carer', 'is_management': False, 'description': 'Carer - Direct care staff'},
            {'name': 'Registered Nurse', 'is_management': False, 'description': 'Registered Nurse - Clinical care'},
            {'name': 'Activities Coordinator', 'is_management': False, 'description': 'Activities Coordinator'},
            {'name': 'Domestic Staff', 'is_management': False, 'description': 'Domestic and housekeeping staff'},
        ]
        
        roles = {}
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={
                    'is_management': role_data['is_management'],
                    'description': role_data['description']
                }
            )
            roles[role.name] = role
            status = "Created" if created else "Exists"
            mgmt = "Management" if role.is_management else "Staff"
            print(f"  ✓ {status}: {role.name} ({mgmt})")
        
        # 4. Shift Types already exist from migrations - skip creation
        print("\n🕒 Shift Types (already in database via migrations)")
        
        # 5. Create Sample Staff (excluding superuser Dean)
        print("\n👤 Creating Sample Staff...")
        sample_staff = [
            {
                'sap': '000542',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'email': 'sjohnson@orchardgrove.com',
                'role': 'Service Manager',
                'home_unit': 'OG_BRAMLEY',
                'password': 'Welcome123!!'
            },
            {
                'sap': '000543',
                'first_name': 'Michael',
                'last_name': 'Chen',
                'email': 'mchen@orchardgrove.com',
                'role': 'Operations Manager',
                'home_unit': 'OG_MGMT',
                'password': 'Welcome123!!'
            },
            {
                'sap': '000544',
                'first_name': 'Emma',
                'last_name': 'Wilson',
                'email': 'ewilson@orchardgrove.com',
                'role': 'Senior Carer',
                'home_unit': 'OG_CHERRY',
                'password': 'Welcome123!!'
            },
            {
                'sap': '000545',
                'first_name': 'James',
                'last_name': 'Brown',
                'email': 'jbrown@orchardgrove.com',
                'role': 'Carer',
                'home_unit': 'OG_GRAPE',
                'password': 'Welcome123!!'
            },
            {
                'sap': '000546',
                'first_name': 'Olivia',
                'last_name': 'Taylor',
                'email': 'otaylor@orchardgrove.com',
                'role': 'Registered Nurse',
                'home_unit': 'OG_ORANGE',
                'password': 'Welcome123!!'
            },
            {
                'sap': '000547',
                'first_name': 'David',
                'last_name': 'Anderson',
                'email': 'danderson@orchardgrove.com',
                'role': 'Senior Carer',
                'home_unit': 'OG_PEACH',
                'password': 'Welcome123!!'
            },
            {
                'sap': '000548',
                'first_name': 'Sophie',
                'last_name': 'Martin',
                'email': 'smartin@orchardgrove.com',
                'role': 'Carer',
                'home_unit': 'OG_PEAR',
                'password': 'Welcome123!!'
            },
            {
                'sap': '000549',
                'first_name': 'Robert',
                'last_name': 'Thompson',
                'email': 'rthompson@orchardgrove.com',
                'role': 'Activities Coordinator',
                'home_unit': 'OG_PLUM',
                'password': 'Welcome123!!'
            },
            {
                'sap': '000550',
                'first_name': 'Lucy',
                'last_name': 'Fraser',
                'email': 'lfraser@orchardgrove.com',
                'role': 'Carer',
                'home_unit': 'OG_STRAWBERRY',
                'password': 'Welcome123!!'
            },
        ]
        
        for staff_data in sample_staff:
            if not User.objects.filter(sap=staff_data['sap']).exists():
                # Use create_user to properly handle password hashing
                user = User.objects.create_user(
                    sap=staff_data['sap'],
                    password=staff_data['password'],
                    first_name=staff_data['first_name'],
                    last_name=staff_data['last_name'],
                    email=staff_data['email'],
                    role=roles[staff_data['role']],
                    home_unit=units[staff_data['home_unit']],
                    unit=units[staff_data['home_unit']],
                    is_active=True,
                    annual_leave_allowance=28
                )
                print(f"  ✓ Created: {user.get_full_name()} (SAP: {user.sap}, Role: {user.role.name})")
            else:
                print(f"  ✓ Exists: {staff_data['first_name']} {staff_data['last_name']} (SAP: {staff_data['sap']})")
        
        # Summary
        print("\n" + "=" * 60)
        print("✅ PRODUCTION DATA POPULATION COMPLETE")
        print("=" * 60)
        print(f"\n📊 Database Summary:")
        print(f"  Care Homes: {CareHome.objects.count()}")
        print(f"  Units: {Unit.objects.count()}")
        print(f"  Roles: {Role.objects.count()}")
        print(f"  Staff: {User.objects.count()}")
        print("\n🔐 Default Password for Sample Staff: Welcome123!!")
        print("   (Users should change on first login)")
        print("\n🚀 System is ready for use!")

if __name__ == '__main__':
    try:
        populate_data()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
