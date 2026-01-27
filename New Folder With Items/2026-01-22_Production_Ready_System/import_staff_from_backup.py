#!/usr/bin/env python3
"""
Import staff data from production backup database.
Adapts old unit names to new prefixed structure (OG_, HH_, MB_, RS_, VG_).
"""

import sqlite3
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Role, Unit, CareHome
from django.db import transaction
from django.contrib.auth.hashers import make_password

# Unit name mapping from old to new
UNIT_MAPPING = {
    # Orchard Grove
    'BRAMLEY': 'OG_BRAMLEY',
    'CHERRY': 'OG_CHERRY',
    'GRAPE': 'OG_GRAPE',
    'ORANGE': 'OG_ORANGE',
    'PEACH': 'OG_PEACH',
    'PEAR': 'OG_PEAR',
    'PLUM': 'OG_PLUM',
    'STRAWBERRY': 'OG_STRAWBERRY',
    'OG_MGMT': 'OG_MGMT',
    'MGMT': 'OG_MGMT',  # Default MGMT to OG
}

def get_care_home_from_unit_name(unit_name):
    """Determine care home from unit name prefix"""
    if unit_name.startswith('OG_'):
        return 'ORCHARD_GROVE'
    elif unit_name.startswith('HH_'):
        return 'HAWTHORN_HOUSE'
    elif unit_name.startswith('MB_'):
        return 'MEADOWBURN'
    elif unit_name.startswith('RS_'):
        return 'RIVERSIDE'
    elif unit_name.startswith('VG_'):
        return 'VICTORIA_GARDENS'
    else:
        # Default to Orchard Grove for unmapped units
        return 'ORCHARD_GROVE'

def main():
    print("\n" + "="*70)
    print("IMPORTING STAFF DATA FROM PRODUCTION BACKUP")
    print("="*70)
    
    backup_db = 'db_demo.sqlite3'
    
    if not os.path.exists(backup_db):
        print(f"\n❌ Backup database not found: {backup_db}")
        return
    
    # Connect to backup database
    conn = sqlite3.connect(backup_db)
    cursor = conn.cursor()
    
    # Get staff data
    cursor.execute('''
        SELECT 
            u.sap,
            u.first_name,
            u.last_name,
            u.email,
            r.name as role_name,
            unit.name as unit_name,
            u.is_active,
            u.annual_leave_allowance,
            u.phone_number
        FROM scheduling_user u
        LEFT JOIN scheduling_role r ON u.role_id = r.id
        LEFT JOIN scheduling_unit unit ON u.unit_id = unit.id
        WHERE u.sap != '000745'
        ORDER BY u.sap
    ''')
    
    staff_data = cursor.fetchall()
    conn.close()
    
    print(f"\n📊 Found {len(staff_data)} staff members in backup")
    
    # Get current database objects
    roles = {r.name: r for r in Role.objects.all()}
    units = {u.name: u for u in Unit.objects.all()}
    care_homes = {ch.name: ch for ch in CareHome.objects.all()}
    
    created = 0
    updated = 0
    skipped = 0
    errors = []
    
    print("\n🔄 Importing staff...")
    
    with transaction.atomic():
        for row in staff_data:
            sap, first_name, last_name, email, role_name, unit_name, is_active, leave_allowance, phone = row
            
            try:
                # Map role
                role = roles.get(role_name)
                if not role:
                    print(f"  ⚠️  Unknown role '{role_name}' for SAP {sap}, using default")
                    role = roles.get('SCW')  # Default role
                
                # Map unit - try exact match first, then mapping
                unit = units.get(unit_name)
                if not unit and unit_name in UNIT_MAPPING:
                    mapped_unit_name = UNIT_MAPPING[unit_name]
                    unit = units.get(mapped_unit_name)
                
                if not unit:
                    # Assign to a default unit in Orchard Grove
                    unit = units.get('OG_BRAMLEY')
                    if not unit:
                        print(f"  ⚠️  No default unit available for SAP {sap}")
                        skipped += 1
                        continue
                
                # Fix email - replace underscores with hyphens for domain part
                clean_email = email
                if email and '@' in str(email):
                    user_part, domain_part = str(email).split('@', 1)
                    domain_part = domain_part.replace('_', '-')  # Replace underscores in domain
                    clean_email = f'{user_part}@{domain_part}'
                else:
                    clean_email = f'{sap}@staffrota.com'
                
                # Create or update user
                user, was_created = User.objects.update_or_create(
                    sap=sap,
                    defaults={
                        'first_name': first_name or '',
                        'last_name': last_name or '',
                        'email': clean_email,
                        'role': role,
                        'unit': unit,
                        'home_unit': unit,
                        'is_active': bool(is_active),
                        'annual_leave_allowance': leave_allowance or 28,
                        'phone_number': phone or '',
                        'password': make_password('password123'),  # Hash password
                    }
                )
                
                if was_created:
                    created += 1
                    if created % 50 == 0:
                        print(f"  ✅ Created {created} staff...")
                else:
                    updated += 1
            
            except Exception as e:
                errors.append(f"SAP {sap}: {str(e)}")
                skipped += 1
    
    print("\n" + "="*70)
    print("IMPORT COMPLETE")
    print("="*70)
    print(f"\n📊 Summary:")
    print(f"  • Created: {created}")
    print(f"  • Updated: {updated}")
    print(f"  • Skipped: {skipped}")
    print(f"  • Errors: {len(errors)}")
    
    if errors:
        print(f"\n⚠️  Errors:")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")
    
    # Final verification
    total_staff = User.objects.filter(is_active=True).exclude(sap='000745').count()
    print(f"\n✅ Total active staff in database: {total_staff}")
    print(f"\n🔐 All staff passwords set to: password123")
    print("\n" + "="*70)

if __name__ == '__main__':
    main()
