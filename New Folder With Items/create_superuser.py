#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.contrib.auth import get_user_model
from scheduling.models import Role

User = get_user_model()

# Create Director role if it doesn't exist
director_role, created = Role.objects.get_or_create(
    name='Director',
    defaults={'description': 'Director - Full system access'}
)
if created:
    print('✓ Created Director role')

# Check if user already exists
if User.objects.filter(sap='000541').exists():
    print('⚠ User with SAP 000541 already exists. Updating password...')
    user = User.objects.get(sap='000541')
    user.set_password('Greenball99##')
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print('✓ Password updated')
else:
    # Create superuser
    user = User.objects.create_superuser(
        sap='000541',
        email='dean@orchardgrove.com',
        password='Greenball99##',
        first_name='Dean',
        last_name='Sockalingum',
        role=director_role
    )
    print('✓ Superuser created')

print(f'\n✅ Login credentials ready:')
print(f'   SAP: {user.sap}')
print(f'   Email: {user.email}')
print(f'   Name: {user.get_full_name()}')
print(f'   Role: {user.role.name if user.role else "None"}')
print(f'   Superuser: {user.is_superuser}')
print(f'\n🌐 Login at: http://127.0.0.1:8000/login/')
