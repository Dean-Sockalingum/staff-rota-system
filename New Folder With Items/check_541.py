import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()
from scheduling.models import User

# Check for user 000541
print('Checking for SAP 000541...')
if User.objects.filter(sap='000541').exists():
    user = User.objects.get(sap='000541')
    print(f'Found: {user.sap} - {user.first_name} {user.last_name}')
else:
    print('❌ User with SAP 000541 does NOT exist')
    print()
    print('Orchard Grove staff SAP range:')
    og_users = User.objects.filter(sap__startswith='000').order_by('sap')
    if og_users.exists():
        print(f'  First: {og_users.first().sap}')
        print(f'  Last: {og_users.last().sap}')
        print(f'  Total: {og_users.count()}')
        print()
        print('First 10 users:')
        for u in og_users[:10]:
            print(f'  {u.sap}: {u.first_name} {u.last_name} - {u.role.name if u.role else "No role"}')
    else:
        print('  No users found with SAP starting with 000')
