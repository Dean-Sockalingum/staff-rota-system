import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
import django
django.setup()

from scheduling.models import User
from django.contrib.auth import authenticate

u = User.objects.get(sap='ADMIN001')
print(f'SAP: {u.sap}')
print(f'First Name: {u.first_name}')
print(f'Last Name: {u.last_name}')
print(f'is_staff: {u.is_staff}')
print(f'is_superuser: {u.is_superuser}')
print(f'is_active: {u.is_active}')
print(f'Role: {u.role}')
print(f'Password check for "admin123": {u.check_password("admin123")}')

# Test authentication
auth_user = authenticate(username='ADMIN001', password='admin123')
print(f'\nAuthentication result: {auth_user}')
if not auth_user:
    print('Authentication FAILED')
else:
    print('Authentication SUCCESS')
