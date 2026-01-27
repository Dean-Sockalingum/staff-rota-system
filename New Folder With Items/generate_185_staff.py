#!/usr/bin/env python
"""
Generate 185 New Staff to Reach 821 Total
Simple generation of clean staff records with valid data
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Unit, Role
from staff_records.models import StaffProfile
from django.db import transaction
from datetime import date
from itertools import cycle

def generate_185_staff():
    print("\n" + "="*80)
    print("GENERATING 185 NEW STAFF TO REACH 821 TOTAL")
    print("="*80 + "\n")
    
    # Get current count
    current_count = User.objects.count()
    print(f"📊 Current staff in database: {current_count}")
    print(f"🎯 Target: 821 staff")
    print(f"➕ Need to add: {821 - current_count} more staff\n")
    
    needed = 821 - current_count
    
    # Get all units
    units = list(Unit.objects.all().order_by('id'))
    print(f"✓ {len(units)} units available")
    
    # Get roles
    roles = {}
    for role in Role.objects.all():
        roles[role.name] = role
    print(f"✓ {len(roles)} roles loaded\n")
    
    # Staff templates
    first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emma', 'James', 'Emily', 'Robert', 'Linda',
                   'William', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica', 'Thomas', 'Karen', 'Christopher', 'Lisa']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
                  'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin']
    
    # Role distribution (60% SCA, 25% SCW, 12% SSCW, 3% OM)
    role_dist = (['SCA'] * 60) + (['SCW'] * 25) + (['SSCW'] * 12) + (['OPERATIONS_MANAGER'] * 3)
    
    unit_cycle = cycle(units)
    role_cycle = cycle(role_dist)
    name_cycle = cycle([(f, l) for f in first_names for l in last_names])
    
    # Get existing SAPs
    existing_saps = set(User.objects.values_list('sap', flat=True))
    
    # Start SAP from 700000
    base_sap = 700000
    created_count = 0
    error_count = 0
    
    print(f"👤 Generating {needed} new staff members...")
    print("="*80)
    
    for i in range(needed):
        try:
            with transaction.atomic():
                # Generate unique SAP
                sap = f"{base_sap + i:06d}"
                while sap in existing_saps:
                    base_sap += 1
                    sap = f"{base_sap + i:06d}"
                
                # Get role, name, unit
                role_name = next(role_cycle)
                role = roles[role_name]
                first_name, last_name = next(name_cycle)
                unit = next(unit_cycle)
                
                # Create user
                user = User.objects.create_user(
                    sap=sap,
                    password='Welcome123!!',
                    first_name=first_name,
                    last_name=last_name,
                    email=f'{sap}@staffrota.local',
                    role=role,
                    unit=unit,
                    home_unit=unit,
                    is_active=True,
                    annual_leave_allowance=28,
                    is_staff=False,
                    is_superuser=False
                )
                
                # Create staff profile  
                StaffProfile.objects.create(
                    user=user,
                    employee_number=sap,
                    date_of_birth=date(1985, 1, 1),
                    hire_date=date(2024, 1, 1),
                    job_title=role.get_name_display(),
                    department='Care Services',
                    emergency_contact_name='Emergency Contact',
                    emergency_contact_phone='07000000000',
                )
                
                created_count += 1
                existing_saps.add(sap)
                
                if created_count % 50 == 0:
                    print(f"  ✓ Generated {created_count} staff...")
                    
        except Exception as e:
            print(f"  ❌ Error generating staff {i+1}: {str(e)}")
            error_count += 1
    
    print(f"\n✅ Generation Complete!")
    print(f"   Created: {created_count}")
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
    elif total_staff < 821:
        print(f"Status: ⚠️  Need {821 - total_staff} more")
    else:
        print(f"Status: ⚠️  Have {total_staff - 821} too many")
    
    # Staff by role
    print("\n👥 Staff by Role:")
    for role in Role.objects.all():
        count = User.objects.filter(role=role).count()
        print(f"  • {role.get_name_display()}: {count}")
    
    print("\n🔐 All staff login: SAP number / Password: Welcome123!!")
    print("\n✅ Ready for production!")

if __name__ == '__main__':
    generate_185_staff()
