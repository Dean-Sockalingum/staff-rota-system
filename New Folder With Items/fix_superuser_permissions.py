#!/usr/bin/env python
"""Fix superuser permissions for Pattern Overview access"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Role

# Get the superuser
user = User.objects.get(sap='000541')
print(f'User: {user.get_full_name()}')
print(f'Current Role: {user.role.name if user.role else "None"}')

# Get or create Director role with full permissions
role, created = Role.objects.get_or_create(
    name='Director',
    defaults={
        'can_view_rota': True,
        'can_manage_rota': True,
        'can_approve_leave': True,
        'can_manage_staff': True,
        'is_management': True,
    }
)

# Update permissions if role exists
if not created:
    role.can_view_rota = True
    role.can_manage_rota = True
    role.can_approve_leave = True
    role.can_manage_staff = True
    role.is_management = True
    role.save()

# Assign role to user
user.role = role
user.save()

print(f'\n✓ Updated Role: {role.name}')
print(f'✓ Permissions:')
print(f'  - can_view_rota: {role.can_view_rota}')
print(f'  - can_manage_rota: {role.can_manage_rota}')
print(f'  - can_approve_leave: {role.can_approve_leave}')
print(f'  - can_manage_staff: {role.can_manage_staff}')
print(f'  - is_management: {role.is_management}')
print()
print('✅ You can now access Pattern Overview!')
print('📍 Navigate to: http://127.0.0.1:8000/pattern-overview/')
print('📍 Or click this link from your browser')
