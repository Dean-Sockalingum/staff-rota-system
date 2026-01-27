"""
Create Production Staff for All 5 Homes
Date: January 8, 2026
Purpose: Allocate 821 staff across 5 homes with proper SAP numbers and unit assignments

STAFFING BREAKDOWN (from Academic Paper):
- Total: 821 staff across 5 homes
- Average per home: ~164 staff
- Roles: SCA (60%), SCW (25%), SSCW (10%), OM/SM/Admin (5%)

SHIFT TYPES:
- Day Shift: 08:00-20:00 (12h) - SCA, SCW, SSCW
- Night Shift: 20:00-08:00 (12h) - SCA, SCW, SSCW  
- Management: 09:00-17:00 (8h) - OM, SM, Admin, HR
"""

import os
import sys
import django

sys.path.insert(0, '/home/staff-rota-system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Unit, Role, CareHome
from django.contrib.auth.hashers import make_password

print("\n" + "="*80)
print("CREATING PRODUCTION STAFF - 821 TOTAL ACROSS 5 HOMES")
print("="*80 + "\n")

# Define staffing structure per home
HOME_STAFFING = {
    'Orchard Grove': {
        'code': 'OG',
        'sap_start': 10000,
        'care_units': ['Bramley', 'Cherry', 'Grape', 'Orange', 'Peach', 'Pear', 'Plum', 'Strawberry'],
        'mgmt_unit': 'OG-MGMT',
        'staff_per_care_unit': 18,  # 8 units × 18 = 144 care staff
        'mgmt_staff': 20  # OM, SM, Admin, HR
    },
    'Meadowburn House': {
        'code': 'MB',
        'sap_start': 20000,
        'care_units': ['Aster', 'Cornflower', 'Foxglove', 'Honeysuckle', 'MB-Bluebell', 'MB-Daisy', 'Marigold', 'Poppy SRD'],
        'mgmt_unit': 'MB-MGMT',
        'staff_per_care_unit': 18,
        'mgmt_staff': 20
    },
    'Hawthorn House': {
        'code': 'HH',
        'sap_start': 30000,
        'care_units': ['HH-Bluebell', 'HH-Daisy', 'HH-Heather', 'Iris', 'Primrose', 'Snowdrop SRD', 'Thistle SRD', 'Violet'],
        'mgmt_unit': 'HH-MGMT',
        'staff_per_care_unit': 18,
        'mgmt_staff': 20
    },
    'Riverside': {
        'code': 'RS',
        'sap_start': 40000,
        'care_units': ['Daffodil', 'Jasmine', 'Lotus', 'Maple', 'Orchid', 'RS-Heather', 'RS-Lily', 'RS-Rose'],
        'mgmt_unit': 'RS-MGMT',
        'staff_per_care_unit': 18,
        'mgmt_staff': 20
    },
    'Victoria Gardens': {
        'code': 'VG',
        'sap_start': 50000,
        'care_units': ['Azalea', 'Crocus', 'Tulip', 'VG-Lily', 'VG-Rose'],
        'mgmt_unit': 'VG-MGMT',
        'staff_per_care_unit': 22,  # 5 units × 22 = 110 care staff (smaller home, more staff per unit)
        'mgmt_staff': 15
    }
}

# Role distribution per care unit (18 staff)
UNIT_ROLE_DISTRIBUTION = [
    ('Social Care Assistant', 11),   # 60% - Social Care Assistants
    ('Social Care Worker', 5),       # 28% - Social Care Workers  
    ('Senior Social Care Worker', 2) # 12% - Senior Social Care Workers
]

# Management roles
MGMT_ROLES = [
    ('Operations Manager', 2),  # Operations Managers
    ('Service Manager', 1),     # Service Manager
    ('IDI Team', 1)             # Admin/Support staff
]

def create_staff_for_home(home_name, config):
    """Create all staff for one care home"""
    print(f"\n📍 {home_name}")
    print("-" * 80)
    
    try:
        care_home = CareHome.objects.get(name=home_name)
    except CareHome.DoesNotExist:
        print(f"  ❌ CareHome '{home_name}' not found - skipping")
        return 0
    
    sap_counter = config['sap_start']
    total_created = 0
    
    # Create care staff for each unit
    for unit_name in config['care_units']:
        try:
            unit = Unit.objects.get(name=unit_name, care_home=care_home)
        except Unit.DoesNotExist:
            print(f"  ⚠️  Unit '{unit_name}' not found - skipping")
            continue
        
        unit_staff_created = 0
        
        for role_name, count in UNIT_ROLE_DISTRIBUTION:
            try:
                role = Role.objects.get(name=role_name)
            except Role.DoesNotExist:
                print(f"  ⚠️  Role '{role_name}' not found - skipping")
                continue
            
            for i in range(count):
                sap = f"{sap_counter:06d}"
                
                user, created = User.objects.get_or_create(
                    sap=sap,
                    defaults={
                        'first_name': role_name.split()[0],  # e.g., "Social" from "Social Care Assistant"
                        'last_name': f"Staff {sap_counter - config['sap_start']:03d}",
                        'email': f"{sap.lower()}@staffrota.local",
                        'role': role,
                        'unit': unit,
                        'is_active': True,
                        'password': make_password('staffRota2026TQM!')
                    }
                )
                
                if created:
                    unit_staff_created += 1
                    total_created += 1
                
                sap_counter += 1
        
        print(f"  ✓ {unit_name:20} → {unit_staff_created} staff")
    
    # Create management staff
    try:
        mgmt_unit = Unit.objects.get(name=config['mgmt_unit'], care_home=care_home)
    except Unit.DoesNotExist:
        print(f"  ⚠️  Management unit '{config['mgmt_unit']}' not found")
        return total_created
    
    mgmt_created = 0
    for role_name, count in MGMT_ROLES:
        try:
            role = Role.objects.get(name=role_name)
        except Role.DoesNotExist:
            # Create role if it doesn't exist
            role = Role.objects.create(
                name=role_name,
                is_management=True if role_name in ['OM', 'SM'] else False
            )
        
        for i in range(count):
            sap = f"{sap_counter:06d}"
            
            user, created = User.objects.get_or_create(
                sap=sap,
                defaults={
                    'first_name': role_name.split()[0] if ' ' in role_name else role_name,
                    'last_name': f"Manager {sap_counter - config['sap_start']:03d}",
                    'email': f"{sap.lower()}@staffrota.local",
                    'role': role,
                    'unit': mgmt_unit,
                    'is_active': True,
                    'password': make_password('staffRota2026TQM!')
                }
            )
            
            if created:
                mgmt_created += 1
                total_created += 1
            
            sap_counter += 1
    
    print(f"  ✓ {config['mgmt_unit']:20} → {mgmt_created} management staff")
    print(f"  📊 Total for {home_name}: {total_created} staff created")
    
    return total_created

# Process all homes
print("Creating staff for all 5 care homes...")
grand_total = 0

for home_name, config in HOME_STAFFING.items():
    created = create_staff_for_home(home_name, config)
    grand_total += created

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"  Total staff created: {grand_total}")
print(f"  Total users in system: {User.objects.count()}")
print(f"  Staff by home:")

for home_name in HOME_STAFFING.keys():
    try:
        care_home = CareHome.objects.get(name=home_name)
        count = User.objects.filter(unit__care_home=care_home, is_active=True).count()
        print(f"    • {home_name:20} {count} staff")
    except CareHome.DoesNotExist:
        print(f"    • {home_name:20} (not found)")

print(f"\n✅ Staff allocation complete!\n")
