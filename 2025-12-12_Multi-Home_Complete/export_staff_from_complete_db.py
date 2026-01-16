#!/usr/bin/env python3
"""
Export staff data from complete database to create production-accurate staff list
Date: January 9, 2026
"""
import os
import sys
import django
import json

# Setup Django to use the COMPLETE database
sys.path.insert(0, '/Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Unit, Role, CareHome

print("\n" + "="*80)
print("EXPORTING STAFF DATA FROM COMPLETE DATABASE (821 staff)")
print("="*80 + "\n")

# Get all active staff
staff_list = User.objects.filter(is_active=True).select_related('unit', 'role', 'unit__care_home').order_by('sap')

total_staff = staff_list.count()
print(f"Total active staff: {total_staff}\n")

# Group by home
staff_by_home = {}
for home in CareHome.objects.all():
    home_staff = staff_list.filter(unit__care_home=home)
    staff_by_home[home.name] = home_staff.count()
    print(f"  {home.name:20} {home_staff.count()} staff")

print(f"\n{'='*80}")
print("EXPORTING STAFF DATA...")
print(f"{'='*80}\n")

# Export format: SAP, First Name, Last Name, Email, Role, Unit, Care Home
export_data = []

for user in staff_list:
    export_data.append({
        'sap': user.sap,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'role': user.role.name if user.role else None,
        'unit': user.unit.name if user.unit else None,
        'care_home': user.unit.care_home.name if user.unit and user.unit.care_home else None,
        'is_active': user.is_active,
        'contract_hours': getattr(user, 'contract_hours', 35.0),
        'shift_preference': getattr(user, 'shift_preference', None),
        'team': getattr(user, 'team', None)
    })

# Save to JSON file
output_file = '/Users/deansockalingum/Desktop/Staff_Rota_Backups/staff_export_821.json'
with open(output_file, 'w') as f:
    json.dump(export_data, f, indent=2)

print(f"✅ Exported {len(export_data)} staff records to:")
print(f"   {output_file}\n")

# Show sample
print("Sample staff records:")
print(f"{'SAP':8} | {'Name':30} | {'Role':25} | {'Unit':20} | {'Home':20}")
print("-" * 110)
for staff in export_data[:10]:
    name = f"{staff['first_name']} {staff['last_name']}"
    print(f"{staff['sap']:8} | {name:30} | {staff['role'] or 'NO ROLE':25} | {staff['unit'] or 'NO UNIT':20} | {staff['care_home'] or 'NO HOME':20}")

print(f"\n✅ Export complete!\n")
