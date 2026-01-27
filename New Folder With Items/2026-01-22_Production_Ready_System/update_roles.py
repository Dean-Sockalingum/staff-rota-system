#!/usr/bin/env python
"""Update roles to support HOS, IDI, SM, OM equal access"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import Role

print("Updating roles...")

# Update SM role
sm = Role.objects.get(name='SM')
sm.permission_level = 'FULL'
sm.save()
print(f"✅ Updated SM: SMT={sm.is_senior_management_team}, Permission={sm.permission_level}")

# Update OM role
om = Role.objects.get(name='OM')
om.permission_level = 'FULL'
om.save()
print(f"✅ Updated OM: SMT={om.is_senior_management_team}, Permission={om.permission_level}")

# Create HOS role
hos, created = Role.objects.get_or_create(
    name='HOS',
    defaults={
        'permission_level': 'FULL',
        'is_senior_management_team': True,
        'is_management': True,
        'can_approve_leave': True,
        'can_manage_staff': True,
        'can_view_payroll': True,
    }
)
status = "Created" if created else "Already exists"
print(f"✅ {status} HOS: SMT={hos.is_senior_management_team}, Permission={hos.permission_level}")

# Create IDI role
idi, created = Role.objects.get_or_create(
    name='IDI',
    defaults={
        'permission_level': 'FULL',
        'is_senior_management_team': True,
        'is_management': True,
        'can_approve_leave': True,
        'can_manage_staff': True,
        'can_view_payroll': True,
    }
)
status = "Created" if created else "Already exists"
print(f"✅ {status} IDI: SMT={idi.is_senior_management_team}, Permission={idi.permission_level}")

print("\n=== SENIOR LEADERSHIP ROLES ===")
for r in Role.objects.filter(is_senior_management_team=True).order_by('name'):
    print(f"  {r.name}: SMT={r.is_senior_management_team}, Permission={r.permission_level}")

print("\n✅ All roles updated successfully!")
