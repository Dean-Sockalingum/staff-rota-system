#!/usr/bin/env python
"""Recreate test users for HOS, IDI, SM, OM testing"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Role, Unit
from django.contrib.auth.hashers import make_password

# Get the first unit for assignment
unit = Unit.objects.first()
if not unit:
    print("❌ No units found in database!")
    exit(1)

print(f"Using unit: {unit.name} ({unit.care_home.name if unit.care_home else 'No care home'})\n")

# Check if test users exist
existing = User.objects.filter(sap__startswith='900')
if existing.exists():
    print(f"Found {existing.count()} existing test users:")
    for u in existing:
        print(f"  {u.sap}: {u.full_name} - {u.role.name}")
    print("\nDeleting existing test users...")
    existing.delete()

# Get roles
try:
    hos_role = Role.objects.get(name='HOS')
    idi_role = Role.objects.get(name='IDI')
    sm_role = Role.objects.get(name='SM')
    om_role = Role.objects.get(name='OM')
except Role.DoesNotExist as e:
    print(f"❌ Role not found: {e}")
    print("\nAvailable roles:")
    for r in Role.objects.all():
        print(f"  {r.name}: SMT={r.is_senior_management_team}, Permission={r.permission_level}")
    exit(1)

# Create test users
test_users = [
    {
        'sap': '900001',
        'first_name': 'Test',
        'last_name': 'HOS',
        'email': 'test.hos@therota.co.uk',
        'role': hos_role,
        'password': 'TestHOS123!',
    },
    {
        'sap': '900002',
        'first_name': 'Test',
        'last_name': 'IDI',
        'email': 'test.idi@therota.co.uk',
        'role': idi_role,
        'password': 'TestIDI123!',
    },
    {
        'sap': '900003',
        'first_name': 'Test',
        'last_name': 'SM',
        'email': 'test.sm@therota.co.uk',
        'role': sm_role,
        'password': 'TestSM123!',
    },
    {
        'sap': '900004',
        'first_name': 'Test',
        'last_name': 'OM',
        'email': 'test.om@therota.co.uk',
        'role': om_role,
        'password': 'TestOM123!',
    },
]

print("Creating test users...\n")
for data in test_users:
    password = data.pop('password')
    # Need to set password before creating to pass validation
    data['password'] = make_password(password)
    user = User.objects.create(
        **data,
        unit=unit,
        is_active=True,
        is_staff=False,
    )
    print(f"✅ Created {user.sap}: {user.full_name:20} | Role: {user.role.name:3} | "
          f"SMT: {user.role.is_senior_management_team} | "
          f"Can View All: {user.can_view_all_homes} | "
          f"Executive Access: {user.can_access_executive_dashboard}")

print(f"\n✅ Successfully created {len(test_users)} test users!")
print("\n=== LOGIN CREDENTIALS ===")
print("HOS: 900001 / TestHOS123!")
print("IDI: 900002 / TestIDI123!")
print("SM:  900003 / TestSM123!")
print("OM:  900004 / TestOM123!")
