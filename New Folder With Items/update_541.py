import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()
from scheduling.models import User
user = User.objects.get(sap='000541')
print(f'Found: {user.sap} - {user.first_name} {user.last_name}')
print(f'Before: Staff={user.is_staff}, Superuser={user.is_superuser}')
user.is_staff = True
user.is_superuser = True
user.is_active = True
user.set_password('Greenball99##')
user.save()
print(f'After: Staff={user.is_staff}, Superuser={user.is_superuser}')
print('✅ Updated! Login with SAP: 000541, Password: Greenball99##')
