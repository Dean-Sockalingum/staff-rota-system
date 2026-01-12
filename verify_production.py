#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, '/home/staff-rota-system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')

import django
django.setup()

from scheduling.models import User, CareHome, Unit, ShiftType

print("\n" + "="*60)
print("PRODUCTION DATABASE VERIFICATION")
print("="*60 + "\n")

# Check admin user
try:
    admin = User.objects.get(sap='000541')
    print(f"✓ Admin User: {admin.first_name} {admin.last_name}")
    print(f"  SAP: {admin.sap}")
    print(f"  Email: {admin.email}")
    print(f"  Superuser: {admin.is_superuser}")
    print(f"  Active: {admin.is_active}")
except User.DoesNotExist:
    print("✗ Admin user (SAP 000541) NOT FOUND")

print("\nDatabase Counts:")
print(f"  Homes: {CareHome.objects.count()}")
print(f"  Units: {Unit.objects.count()}")
print(f"  Shift Types: {ShiftType.objects.count()}")
print(f"  Total Users: {User.objects.count()}")

print("\nStaff Distribution by Home:")
for home in CareHome.objects.all().order_by('name'):
    count = User.objects.filter(home_unit__care_home=home).exclude(sap='000541').count()
    print(f"  {home.name}: {count} staff")

active_staff = User.objects.filter(is_active=True).exclude(sap='000541').count()
print(f"\nTotal Active Staff: {active_staff}")

print("\n" + "="*60)
print("READY FOR DEMO")
print("="*60)
print("\nLogin Credentials:")
print("  URL: https://demo.therota.co.uk")
print("  SAP: 000541")
print("  Password: Greenball99##")
print()
