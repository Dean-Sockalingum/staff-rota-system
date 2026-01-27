import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
import django
django.setup()

from scheduling.models import User

# Find the current Admin User
admin = User.objects.filter(first_name='Admin', last_name='User').first()

if admin:
    print(f'\n{"="*60}')
    print(f'ADMIN USER STATUS - BEFORE FIX')
    print(f'{"="*60}')
    print(f'SAP: {admin.sap}')
    print(f'Name: {admin.first_name} {admin.last_name}')
    print(f'Email: {admin.email}')
    print(f'Role: {admin.role}')
    print(f'is_staff: {admin.is_staff}')
    print(f'is_superuser: {admin.is_superuser}')
    print(f'is_active: {admin.is_active}')
    
    # Fix permissions
    if not admin.is_staff or not admin.is_superuser:
        print(f'\n{"="*60}')
        print(f'FIXING ADMIN PERMISSIONS...')
        print(f'{"="*60}')
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()
        print(f'✓ Admin permissions updated')
        
        # Verify
        admin.refresh_from_db()
        print(f'\n{"="*60}')
        print(f'ADMIN USER STATUS - AFTER FIX')
        print(f'{"="*60}')
        print(f'is_staff: {admin.is_staff}')
        print(f'is_superuser: {admin.is_superuser}')
        print(f'is_active: {admin.is_active}')
    else:
        print(f'\n✓ Admin already has correct permissions')
else:
    print('\n✗ Admin User not found')
    print('\nSearching for all users with "Admin" in name...')
    admins = User.objects.filter(first_name__icontains='admin')
    for user in admins:
        print(f'  - {user.sap}: {user.first_name} {user.last_name} (is_superuser={user.is_superuser})')
