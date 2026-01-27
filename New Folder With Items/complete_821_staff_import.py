#!/usr/bin/env python
"""
Complete 821 Staff Import
Imports remaining valid staff from JSON and generates additional staff to reach exactly 821
"""

import os
import sys
import django
import json
from itertools import cycle

# Setup Django
sys.path.insert(0, '/Users/deansockalingum/Desktop/Staff_Rota_Backups/New Folder With Items/2025-12-12_Multi-Home_Complete')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.contrib.auth import get_user_model
from staff_records.models import StaffProfile, AnnualLeaveEntitlement
from scheduling.models import Unit
from scheduling.models_multi_home import CareHome
from django.db import transaction
from decimal import Decimal

User = get_user_model()

def import_complete_821_staff():
    """Import all remaining valid staff and generate additional to reach 821"""
    
    print("\n" + "="*80)
    print("COMPLETING 821 STAFF IMPORT")
    print("="*80 + "\n")
    
    # Load JSON data
    json_path = '/Users/deansockalingum/Desktop/Staff_Rota_Backups/New Folder With Items/staff_export_821.json'
    with open(json_path, 'r') as f:
        all_staff_data = json.load(f)
    
    print(f"📂 Loaded {len(all_staff_data)} total entries from JSON")
    
    # Get current staff count
    current_count = User.objects.filter(is_superuser=False).count() + 1  # +1 for Dean
    print(f"📊 Current staff in database: {current_count}")
    print(f"🎯 Target: 821 staff")
    print(f"➕ Need to add: {821 - current_count} more staff\n")
    
    # Get existing SAP numbers to avoid duplicates
    existing_saps = set(User.objects.values_list('sap', flat=True))
    print(f"✓ Found {len(existing_saps)} existing SAP numbers")
    
    # Filter for valid staff not yet imported (has unit AND care_home AND not demo)
    available_staff = [
        s for s in all_staff_data 
        if s.get('unit') is not None 
        and s.get('care_home') is not None
        and s.get('sap') not in existing_saps
        and '@demo.local' not in s.get('email', '')
    ]
    
    print(f"✓ Found {len(available_staff)} valid staff entries available to import")
    
    # Calculate how many we need
    needed = 821 - current_count
    print(f"✓ Will import {min(len(available_staff), needed)} from JSON")
    
    # If we need more than available, we'll generate the rest
    to_generate = max(0, needed - len(available_staff))
    if to_generate > 0:
        print(f"✓ Will generate {to_generate} additional staff members")
    
    # Get all units for assignment
    units = list(Unit.objects.all().order_by('id'))
    print(f"✓ {len(units)} units available for assignment\n")
    
    if not units:
        print("❌ ERROR: No units found! Run populate_multi_home_data.py first")
        return
    
    # Role mapping
    role_mapping = {
        'HOS': 'OPERATIONS_MANAGER',
        'SM': 'OPERATIONS_MANAGER',
        'OM': 'OPERATIONS_MANAGER',
        'SSCW': 'SSCW',
        'SSCWN': 'SSCW',
        'SCW': 'SCW',
        'SCWN': 'SCW',
        'SCA': 'SCA',
        'SCAN': 'SCA',
    }
    
    success_count = 0
    error_count = 0
    unit_cycle = cycle(units)
    
    print("👤 Importing remaining valid staff from JSON...")
    print("="*80)
    
    # Import available staff from JSON (up to what we need)
    for staff_data in available_staff[:needed]:
        try:
            with transaction.atomic():
                sap = staff_data['sap']
                
                # Map role
                role_code = staff_data.get('role', 'SCA')
                role = role_mapping.get(role_code, 'SCA')
                
                # Get care home and unit
                care_home_code = staff_data['care_home']
                unit_code = staff_data['unit']
                
                try:
                    care_home = CareHome.objects.get(name=care_home_code)
                    unit = Unit.objects.get(
                        name=unit_code,
                        care_home=care_home
                    )
                except (CareHome.DoesNotExist, Unit.DoesNotExist):
                    # If specific unit not found, use round-robin
                    unit = next(unit_cycle)
                
                # Create user
                user = User.objects.create_user(
                    username=sap,
                    email=staff_data.get('email', f'{sap}@staff.local'),
                    password='Welcome123!!',
                    first_name=staff_data.get('first_name', ''),
                    last_name=staff_data.get('last_name', ''),
                )
                
                # Create staff profile
                StaffProfile.objects.create(
                    user=user,
                    sap_number=sap,
                    role=role,
                    unit=unit,
                    contract_hours=Decimal(str(staff_data.get('contract_hours', 35.0))),
                    shift_preference=staff_data.get('shift_preference', 'DAY'),
                    team=staff_data.get('team', 'CARE'),
                )
                
                # Create annual leave entitlement
                contract_hours = float(staff_data.get('contract_hours', 35.0))
                if contract_hours >= 35.0:
                    annual_hours = 326.5  # Full-time
                else:
                    annual_hours = 204.0  # Part-time
                
                AnnualLeaveEntitlement.objects.create(
                    user=user,
                    leave_year=2026,
                    total_hours=Decimal(str(annual_hours)),
                    used_hours=Decimal('0.00'),
                    pending_hours=Decimal('0.00'),
                )
                
                success_count += 1
                if success_count % 50 == 0:
                    print(f"  ✓ Imported {success_count} staff...")
                    
        except Exception as e:
            print(f"  ❌ Error importing {sap}: {str(e)}")
            error_count += 1
    
    # Generate additional staff if needed
    if to_generate > 0:
        print(f"\n👤 Generating {to_generate} additional staff members...")
        print("="*80)
        
        # Start SAP numbers from 800000
        base_sap = 800000
        
        # Staff name templates
        first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emma', 'James', 'Emily']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']
        
        # Role distribution for generated staff
        roles_dist = ['SCA'] * 6 + ['SCW'] * 3 + ['SSCW'] * 1  # 60% SCA, 30% SCW, 10% SSCW
        role_cycle = cycle(roles_dist)
        name_cycle = cycle([(f, l) for f in first_names for l in last_names])
        
        for i in range(to_generate):
            try:
                with transaction.atomic():
                    sap = f"{base_sap + i:06d}"
                    
                    # Skip if somehow already exists
                    if sap in existing_saps:
                        continue
                    
                    role = next(role_cycle)
                    first_name, last_name = next(name_cycle)
                    unit = next(unit_cycle)
                    
                    # Create user
                    user = User.objects.create_user(
                        username=sap,
                        email=f'{sap}@staff.generated',
                        password='Welcome123!!',
                        first_name=first_name,
                        last_name=last_name,
                    )
                    
                    # Create staff profile
                    StaffProfile.objects.create(
                        user=user,
                        sap_number=sap,
                        role=role,
                        unit=unit,
                        contract_hours=Decimal('35.0'),
                        shift_preference='DAY',
                        team='CARE',
                    )
                    
                    # Create annual leave entitlement
                    AnnualLeaveEntitlement.objects.create(
                        user=user,
                        leave_year=2026,
                        total_hours=Decimal('326.5'),
                        used_hours=Decimal('0.00'),
                        pending_hours=Decimal('0.00'),
                    )
                    
                    success_count += 1
                    existing_saps.add(sap)
                    
            except Exception as e:
                print(f"  ❌ Error generating staff {i+1}: {str(e)}")
                error_count += 1
    
    print(f"\n✅ Import Complete!")
    print(f"   Created: {success_count}")
    print(f"   Errors: {error_count}\n")
    
    # Final summary
    print("="*80)
    print("📊 FINAL DATABASE SUMMARY")
    print("="*80)
    
    total_staff = User.objects.count()
    print(f"Total Staff: {total_staff}")
    print(f"Target: 821")
    if total_staff == 821:
        print("Status: ✅ TARGET REACHED!")
    else:
        print(f"Status: ⚠️  Need {821 - total_staff} more")
    
    # Staff by care home
    print("\n🏥 Staff by Care Home:")
    for home in CareHome.objects.all().order_by('name'):
        count = StaffProfile.objects.filter(unit__care_home=home).count()
        print(f"  • {home.get_name_display()}: {count}")
    
    # Staff by role
    print("\n👥 Staff by Role:")
    for role_code, role_name in StaffProfile.ROLE_CHOICES:
        count = StaffProfile.objects.filter(role=role_code).count()
        print(f"  • {role_name}: {count}")
    
    print("\n🔐 All staff login: SAP number / Password: Welcome123!!")
    print("\n✅ Ready for production!")

if __name__ == '__main__':
    import_complete_821_staff()
