"""
Populate Multi-Home Production Database
Creates 5 Care Homes with Complete Staffing Structure

Care Homes:
- Orchard Grove: 120 beds (8 x 15-bed units + 1 management)
- Hawthorn House: 120 beds (8 x 15-bed units + 1 management)
- Meadowburn: 120 beds (8 x 15-bed units + 1 management)
- Riverside: 120 beds (8 x 15-bed units + 1 management)
- Victoria Gardens: 70 beds (4 x 15-bed + 1 x 10-bed + 1 management)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import Unit, Role, User
from scheduling.models_multi_home import CareHome
from django.db import transaction
from decimal import Decimal

def populate_all_homes():
    print("🚀 MULTI-HOME PRODUCTION DATA POPULATION")
    print("=" * 70)
    
    with transaction.atomic():
        # 1. Create all 5 Care Homes
        print("\n📍 Creating Care Homes...")
        care_homes_data = [
            {
                'name': 'ORCHARD_GROVE',
                'bed_capacity': 120,
                'location_address': '123 Main Street, Edinburgh, EH1 1AA',
                'postcode': 'EH1 1AA',
                'care_inspectorate_id': 'CS2021-OG-001'
            },
            {
                'name': 'HAWTHORN_HOUSE',
                'bed_capacity': 120,
                'location_address': '456 Park Lane, Edinburgh, EH2 2BB',
                'postcode': 'EH2 2BB',
                'care_inspectorate_id': 'CS2021-HH-002'
            },
            {
                'name': 'MEADOWBURN',
                'bed_capacity': 120,
                'location_address': '789 Garden Road, Edinburgh, EH3 3CC',
                'postcode': 'EH3 3CC',
                'care_inspectorate_id': 'CS2021-MB-003'
            },
            {
                'name': 'RIVERSIDE',
                'bed_capacity': 120,
                'location_address': '321 River View, Edinburgh, EH4 4DD',
                'postcode': 'EH4 4DD',
                'care_inspectorate_id': 'CS2021-RS-004'
            },
            {
                'name': 'VICTORIA_GARDENS',
                'bed_capacity': 70,
                'location_address': '654 Victoria Street, Edinburgh, EH5 5EE',
                'postcode': 'EH5 5EE',
                'care_inspectorate_id': 'CS2021-VG-005'
            },
        ]
        
        care_homes = {}
        for ch_data in care_homes_data:
            care_home, created = CareHome.objects.get_or_create(
                name=ch_data['name'],
                defaults={
                    'bed_capacity': ch_data['bed_capacity'],
                    'current_occupancy': int(ch_data['bed_capacity'] * 0.85),  # 85% occupancy
                    'location_address': ch_data['location_address'],
                    'postcode': ch_data['postcode'],
                    'care_inspectorate_id': ch_data['care_inspectorate_id'],
                    'budget_agency_monthly': Decimal('9000.00'),
                    'budget_overtime_monthly': Decimal('5000.00'),
                    'is_active': True
                }
            )
            care_homes[care_home.name] = care_home
            display_name = dict(CareHome.HOME_CHOICES).get(care_home.name, care_home.name)
            status = "Created" if created else "Exists"
            print(f"  ✓ {status}: {display_name} ({care_home.bed_capacity} beds)")
        
        # 2. Create Units for each Care Home
        print("\n🏢 Creating Care Units...")
        
        # Unit definitions matching Unit.UNIT_CHOICES
        units_by_home = {
            'ORCHARD_GROVE': [
                'OG_BRAMLEY', 'OG_CHERRY', 'OG_GRAPE', 'OG_ORANGE',
                'OG_PEACH', 'OG_PEAR', 'OG_PLUM', 'OG_STRAWBERRY', 'OG_MGMT'
            ],
            'HAWTHORN_HOUSE': [
                'HH_BLUEBELL', 'HH_DAISY', 'HH_HEATHER', 'HH_IRIS',
                'HH_PRIMROSE', 'HH_SNOWDROP_SRD', 'HH_THISTLE_SRD', 'HH_VIOLET', 'HH_MGMT'
            ],
            'MEADOWBURN': [
                'MB_ASTER', 'MB_BLUEBELL', 'MB_CORNFLOWER', 'MB_DAISY',
                'MB_FOXGLOVE', 'MB_HONEYSUCKLE', 'MB_MARIGOLD', 'MB_POPPY_SRD', 'MB_MGMT'
            ],
            'RIVERSIDE': [
                'RS_DAFFODIL', 'RS_HEATHER', 'RS_JASMINE', 'RS_LILY',
                'RS_LOTUS', 'RS_MAPLE', 'RS_ORCHID', 'RS_ROSE', 'RS_MGMT'
            ],
            'VICTORIA_GARDENS': [
                'VG_AZALEA', 'VG_CROCUS', 'VG_LILY', 'VG_ROSE', 'VG_TULIP', 'VG_MGMT'
            ]
        }
        
        all_units = {}
        unit_count = 0
        
        for home_name, unit_names in units_by_home.items():
            care_home = care_homes[home_name]
            display_home = dict(CareHome.HOME_CHOICES).get(home_name, home_name)
            
            for unit_name in unit_names:
                unit, created = Unit.objects.get_or_create(
                    name=unit_name,
                    care_home=care_home,
                    defaults={
                        'description': f'{dict(Unit.UNIT_CHOICES).get(unit_name, unit_name)} Unit',
                        'is_active': True,
                        'min_day_staff': 2 if 'MGMT' not in unit_name else 0,
                        'min_night_staff': 1 if 'MGMT' not in unit_name else 0
                    }
                )
                all_units[unit_name] = unit
                unit_count += 1
                
                if created:
                    unit_display = dict(Unit.UNIT_CHOICES).get(unit.name, unit.name)
                    print(f"  ✓ Created: {display_home} - {unit_display}")
        
        print(f"\n  📊 Total Units Created: {unit_count}")
        
        # 3. Create Staff Roles (using actual Role.ROLE_CHOICES)
        print("\n👥 Creating Staff Roles...")
        roles_data = [
            {
                'name': 'OPERATIONS_MANAGER',
                'description': 'Operations Manager - Home operations oversight',
                'is_management': True,
                'permission_level': 'FULL'
            },
            {
                'name': 'SSCW',
                'description': 'Senior Social Care Worker - Team leadership',
                'is_management': False,
                'permission_level': 'MOST'
            },
            {
                'name': 'SCW',
                'description': 'Social Care Worker - Direct care',
                'is_management': False,
                'permission_level': 'LIMITED'
            },
            {
                'name': 'SCA',
                'description': 'Social Care Assistant - Care support',
                'is_management': False,
                'permission_level': 'LIMITED'
            },
        ]
        
        roles = {}
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={
                    'description': role_data['description'],
                    'is_management': role_data['is_management'],
                    'permission_level': role_data['permission_level']
                }
            )
            roles[role.name] = role
            status = "Created" if created else "Exists"
            display_name = dict(Role.ROLE_CHOICES).get(role.name, role.name)
            print(f"  ✓ {status}: {display_name}")
        
        # 4. Create Sample Staff across all homes
        print("\n👤 Creating Sample Staff Across All Homes...")
        
        # Staff distribution per home (example structure)
        staff_data = []
        sap_counter = 542  # Start after existing users
        
        # For each care home
        for home_name, unit_names in units_by_home.items():
            display_home = dict(CareHome.HOME_CHOICES).get(home_name, home_name)
            
            # 1 OM per home (assigned to MGMT unit)
            mgmt_unit = [u for u in unit_names if 'MGMT' in u][0]
            staff_data.append({
                'sap': f'{sap_counter:06d}',
                'first_name': f'{display_home.split()[0]}',
                'last_name': 'Manager',
                'email': f'om.{home_name.lower()}@carehomes.com',
                'role': 'OPERATIONS_MANAGER',
                'home_unit': mgmt_unit,
                'password': 'Welcome123!!'
            })
            sap_counter += 1
            
            # 1 SSCW per care unit (not MGMT)
            care_units = [u for u in unit_names if 'MGMT' not in u]
            for idx, unit_name in enumerate(care_units):
                staff_data.append({
                    'sap': f'{sap_counter:06d}',
                    'first_name': f'Senior{idx+1}',
                    'last_name': dict(Unit.UNIT_CHOICES).get(unit_name, unit_name).split()[0],
                    'email': f'sscw.{unit_name.lower()}@carehomes.com',
                    'role': 'SSCW',
                    'home_unit': unit_name,
                    'password': 'Welcome123!!'
                })
                sap_counter += 1
            
            # 2 SCW per care unit
            for idx, unit_name in enumerate(care_units):
                for scw_num in range(1, 3):
                    staff_data.append({
                        'sap': f'{sap_counter:06d}',
                        'first_name': f'Worker{scw_num}',
                        'last_name': dict(Unit.UNIT_CHOICES).get(unit_name, unit_name).split()[0][:8],
                        'email': f'scw{scw_num}.{unit_name.lower()}@carehomes.com',
                        'role': 'SCW',
                        'home_unit': unit_name,
                        'password': 'Welcome123!!'
                    })
                    sap_counter += 1
            
            # 2 SCA per care unit  
            for idx, unit_name in enumerate(care_units):
                for sca_num in range(1, 3):
                    staff_data.append({
                        'sap': f'{sap_counter:06d}',
                        'first_name': f'Assistant{sca_num}',
                        'last_name': dict(Unit.UNIT_CHOICES).get(unit_name, unit_name).split()[0][:8],
                        'email': f'sca{sca_num}.{unit_name.lower()}@carehomes.com',
                        'role': 'SCA',
                        'home_unit': unit_name,
                        'password': 'Welcome123!!'
                    })
                    sap_counter += 1
        
        # Create all staff
        created_count = 0
        exists_count = 0
        
        for staff in staff_data:
            if not User.objects.filter(sap=staff['sap']).exists():
                user = User.objects.create_user(
                    sap=staff['sap'],
                    password=staff['password'],
                    first_name=staff['first_name'],
                    last_name=staff['last_name'],
                    email=staff['email'],
                    role=roles[staff['role']],
                    home_unit=all_units[staff['home_unit']],
                    unit=all_units[staff['home_unit']],
                    is_active=True,
                    annual_leave_allowance=28
                )
                created_count += 1
                if created_count <= 10:  # Show first 10
                    print(f"  ✓ Created: {user.get_full_name()} (SAP: {user.sap}, Role: {user.role}, Unit: {dict(Unit.UNIT_CHOICES).get(user.unit.name, user.unit.name)})")
            else:
                exists_count += 1
        
        if created_count > 10:
            print(f"  ✓ ... and {created_count - 10} more staff members")
        
        if exists_count > 0:
            print(f"  ✓ {exists_count} staff already existed")
        
        # Summary
        print("\n" + "=" * 70)
        print("✅ MULTI-HOME PRODUCTION DATA POPULATION COMPLETE")
        print("=" * 70)
        print(f"\n📊 Database Summary:")
        print(f"  Care Homes: {CareHome.objects.count()}")
        print(f"  Total Units: {Unit.objects.count()}")
        print(f"  Total Staff: {User.objects.count()}")
        print(f"\n📍 Care Home Breakdown:")
        
        for home in CareHome.objects.all():
            display_name = dict(CareHome.HOME_CHOICES).get(home.name, home.name)
            unit_count = home.units.count()
            staff_count = User.objects.filter(unit__care_home=home).count()
            print(f"  • {display_name}:")
            print(f"      - Beds: {home.bed_capacity}")
            print(f"      - Units: {unit_count}")
            print(f"      - Staff: {staff_count}")
        
        print(f"\n👥 Role Distribution:")
        for role in Role.objects.all():
            staff_count = User.objects.filter(role=role, is_active=True).count()
            display_name = dict(Role.ROLE_CHOICES).get(role.name, role.name)
            print(f"  • {display_name}: {staff_count}")
        
        print("\n🔐 Default Password for All Sample Staff: Welcome123!!")
        print("   (Users should change on first login)")
        print("\n🚀 Multi-Home System Ready for Production Use!")

if __name__ == '__main__':
    try:
        populate_all_homes()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
