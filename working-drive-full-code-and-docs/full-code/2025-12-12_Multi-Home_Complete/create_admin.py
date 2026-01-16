#!/usr/bin/env python
"""
Create default admin user for testing
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Role, Unit, CareHome
from django.contrib.auth.hashers import make_password

# Create care homes first
homes_data = [
    ('ORCHARD_GROVE', 'Orchard Grove'),
    ('MEADOWBURN', 'Meadowburn'),
    ('HAWTHORN_HOUSE', 'Hawthorn House'),
    ('RIVERSIDE', 'Riverside'),
    ('VICTORIA_GARDENS', 'Victoria Gardens'),
]

for name_code, display_name in homes_data:
    CareHome.objects.get_or_create(
        name=name_code,
        defaults={
            'bed_capacity': 50,
            'current_occupancy': 45,
            'location_address': f'{display_name}, Glasgow',
            'postcode': 'G12 0AA',
            'care_inspectorate_id': f'CS202500{ord(name_code[0])}'
        }
    )
    print(f"✓ Care home: {display_name}")

# Create roles
roles_data = [
    ('SM', 'Service Manager', True),
    ('OM', 'Operations Manager', True),
    ('SSCW', 'Senior Support Care Worker', False),
    ('SCW', 'Support Care Worker', False),
]

for code, name, is_smt in roles_data:
    Role.objects.get_or_create(
        name=code,
        defaults={'is_senior_management_team': is_smt}
    )
    print(f"✓ Role: {name}")

# Create units
units_data = [
    ('MGMT', 'Management'),
    ('BLUE', 'Blue Unit'),
    ('GREEN', 'Green Unit'),
]

og_home = CareHome.objects.get(name='ORCHARD_GROVE')
for code, display_name in units_data:
    Unit.objects.get_or_create(
        name=code,
        defaults={
            'care_home': og_home,
            'description': display_name
        }
    )
    print(f"✓ Unit: {display_name}")

# Create admin user
sm_role = Role.objects.get(name='SM')
mgmt_unit = Unit.objects.get(name='MGMT')

admin_user = User.objects.create_superuser(
    sap='000745',
    password='password123',
    first_name='Admin',
    last_name='User',
    email='admin@example.com',
    role=sm_role,
    unit=mgmt_unit,
    home_unit=mgmt_unit,
    is_active=True,
)

print(f"\n✓ Admin user created!")
print(f"  SAP: 000745")
print(f"  Password: password123")
print(f"\nYou can now log in at: http://127.0.0.1:8000/login/")
