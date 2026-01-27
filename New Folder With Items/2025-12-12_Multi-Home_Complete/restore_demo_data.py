#!/usr/bin/env python
"""
Restore Original Demo Data to PostgreSQL
Imports the complete working staff and shift data from demo
"""

import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.core.management import call_command
from scheduling.models import User
from django.db import connection

def restore_demo_data():
    print("\n" + "="*80)
    print("RESTORING ORIGINAL DEMO DATA TO POSTGRESQL")
    print("="*80 + "\n")
    
    # First, clear existing staff (keep structure)
    print("🗑️  Clearing existing generated staff...")
    generated_staff = User.objects.filter(sap__gte='700000')
    count = generated_staff.count()
    generated_staff.delete()
    print(f"   ✓ Deleted {count} generated staff\n")
    
    print(f"📊 Current staff count: {User.objects.count()}\n")
    
    # Load the complete demo export
    print("📂 Loading complete demo export...")
    with open('../complete_demo_export.json', 'r') as f:
        data = json.load(f)
    
    print(f"   ✓ Loaded {len(data):,} records\n")
    
    # Count what we have
    users = [d for d in data if d.get('model') == 'scheduling.user']
    shifts = [d for d in data if d.get('model') == 'scheduling.shift']
    roles = [d for d in data if d.get('model') == 'scheduling.role']
    units = [d for d in data if d.get('model') == 'scheduling.unit']
    
    print("📊 Data Summary:")
    print(f"   Users: {len(users):,}")
    print(f"   Shifts: {len(shifts):,}")
    print(f"   Roles: {len(roles)}")
    print(f"   Units: {len(units)}\n")
    
    # Save filtered data (only what we need)
    filtered_models = [
        'scheduling.role',
        'scheduling.unit',
        'scheduling.user',
        'scheduling.shift',
        'scheduling.shifttype',
        'scheduling.shiftpattern',
    ]
    
    filtered_data = [d for d in data if d.get('model') in filtered_models]
    
    print(f"📝 Creating filtered import file...")
    with open('import_demo_data.json', 'w') as f:
        json.dump(filtered_data, f)
    
    print(f"   ✓ Saved {len(filtered_data):,} records to import_demo_data.json\n")
    
    # Import using Django's loaddata
    print("📥 Importing data into PostgreSQL...")
    print("   (This may take a few minutes...)\n")
    
    try:
        call_command('loaddata', 'import_demo_data.json', verbosity=2)
        print("\n✅ DATA IMPORT COMPLETE!\n")
    except Exception as e:
        print(f"\n❌ Error during import: {str(e)}\n")
        return
    
    # Verify
    print("="*80)
    print("📊 FINAL VERIFICATION")
    print("="*80 + "\n")
    
    total_users = User.objects.count()
    print(f"Total Users: {total_users:,}")
    
    from scheduling.models import Shift
    total_shifts = Shift.objects.count()
    print(f"Total Shifts: {total_shifts:,}")
    
    # Sample some SAP numbers
    print(f"\n📋 Sample Staff SAP Numbers:")
    for user in User.objects.all()[:10]:
        print(f"   {user.sap}: {user.first_name} {user.last_name} - {user.role.name if user.role else 'No role'}")
    
    print(f"\n✅ Original demo data successfully restored!")
    print(f"🔐 All staff login: SAP number / Password: Welcome123!!")

if __name__ == '__main__':
    restore_demo_data()
