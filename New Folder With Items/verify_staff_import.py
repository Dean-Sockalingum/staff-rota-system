import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User
from scheduling.models_multi_home import CareHome

print('✅ STAFF IMPORT SUMMARY')
print('=' * 60)
print(f'Total Staff: {User.objects.count()}')
print(f'\nStaff by Care Home:')
for home in CareHome.objects.all():
    count = User.objects.filter(unit__care_home=home, is_active=True).count()
    display = dict(CareHome.HOME_CHOICES).get(home.name, home.name)
    print(f'  • {display}: {count}')

print(f'\nSample Staff (First 10 with 6-digit SAP):')
for user in User.objects.filter(is_active=True).exclude(sap='000541').order_by('sap')[:10]:
    print(f'  {user.sap}: {user.get_full_name()} - {user.role.name} - Unit: {user.unit.get_name_display() if user.unit else "No Unit"}')

print(f'\n🔐 All staff can login with:')
print(f'   Username: Their 6-digit SAP number (e.g., 000001)')
print(f'   Password: Welcome123!!')
