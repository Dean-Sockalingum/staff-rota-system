#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User
from django.contrib.auth.hashers import make_password

sap = '000541'

print('=' * 60)
print('Checking User 000541')
print('=' * 60)

try:
    user = User.objects.get(sap=sap)
    print(f'✅ User found: {user.sap}')
    print(f'   Email: {user.email}')
    print(f'   Name: {user.first_name} {user.last_name}')
    print(f'   Role: {user.role.name if user.role else "No role"}')
    print(f'   Unit: {user.unit.name if user.unit else "No unit"}')
    print(f'   Active: {user.is_active}')
    print(f'   Staff: {user.is_staff}')
    print(f'   Superuser: {user.is_superuser}')
    
    # Update password to Greenball99##
    print('\nUpdating password to: Greenball99##')
    user.set_password('Greenball99##')
    user.is_active = True
    user.save()
    print('✅ Password updated and user activated')
    
    print(f'\nLogin credentials:')
    print(f'  Username/SAP: 000541')
    print(f'  Password: Greenball99##')
    
except User.DoesNotExist:
    print(f'❌ User with SAP {sap} not found')
    print('\nSearching for similar SAPs:')
    similar = User.objects.filter(sap__contains='541')[:5]
    for u in similar:
        print(f'  - {u.sap}: {u.first_name} {u.last_name}')
