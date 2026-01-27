#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User
from django.contrib.auth.hashers import make_password

# Check if user with SAP 000541 exists
try:
    user = User.objects.get(sap='000541')
    print(f'✅ Found user: {user.sap}')
    print(f'   Name: {user.first_name} {user.last_name}')
    print(f'   Email: {user.email}')
    print(f'   Role: {user.role.name if user.role else "No role"}')
    print(f'   Active: {user.is_active}')
    print(f'   Staff: {user.is_staff}')
    print(f'   Superuser: {user.is_superuser}')
    print()
    
    # Update to make superuser with the password they want
    print('Making 000541 a superuser with password "Greenball99##"...')
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.set_password('Greenball99##')
    user.save()
    
    print('✅ Updated successfully!')
    print(f'   Username: {user.sap}')
    print(f'   Password: Greenball99##')
    print(f'   Staff: {user.is_staff}')
    print(f'   Superuser: {user.is_superuser}')
    print()
    print('You can now login at: http://127.0.0.1:8000/login/')
    
except User.DoesNotExist:
    print('❌ User with SAP 000541 does not exist')
    print('\nLet me check what SAP numbers exist for Orchard Grove:')
    og_users = User.objects.filter(sap__startswith='000').order_by('sap')[:10]
    print(f'\nFirst 10 Orchard Grove users:')
    for u in og_users:
        print(f'  {u.sap}: {u.first_name} {u.last_name} ({u.role.name if u.role else "No role"})')
