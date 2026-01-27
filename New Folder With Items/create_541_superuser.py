import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()
from scheduling.models import User, CareHome, Unit, Role

print('Creating superuser with SAP 000541...')
print()

# Get Orchard Grove management unit
og = CareHome.objects.get(name='ORCHARD_GROVE')
mgmt_unit = Unit.objects.get(care_home=og, name__contains='Mgmt')
sm_role = Role.objects.get(name='SM')  # Service Manager role

# Create the user
from django.contrib.auth.hashers import make_password

user = User.objects.create(
    sap='000541',
    email='000541@orchardgrove.care',
    first_name='Dean',
    last_name='Sockalingum',
    role=sm_role,
    unit=mgmt_unit,
    password=make_password('Greenball99##'),
    is_active=True,
    is_staff=True,
    is_superuser=True,
    shifts_per_week_override=5,
    team='A'
)

print('✅ Superuser created successfully!')
print()
print(f'   SAP: {user.sap}')
print(f'   Name: {user.first_name} {user.last_name}')
print(f'   Email: {user.email}')
print(f'   Password: Greenball99##')
print(f'   Role: {user.role.name}')
print(f'   Unit: {user.unit.name}')
print(f'   Superuser: {user.is_superuser}')
print(f'   Staff: {user.is_staff}')
print()
print('You can now login at: http://127.0.0.1:8000/login/')
print('Username: 000541')
print('Password: Greenball99##')
