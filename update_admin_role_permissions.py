import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
import django
django.setup()

from scheduling.models import User, Role

# Get ADMIN role
admin_role = Role.objects.filter(name='ADMIN').first()

if admin_role:
    print(f'\n{"="*60}')
    print(f'ADMIN ROLE - CURRENT PERMISSIONS')
    print(f'{"="*60}')
    print(f'Name: {admin_role.get_name_display()}')
    print(f'is_management: {admin_role.is_management}')
    print(f'is_senior_management_team: {admin_role.is_senior_management_team}')
    print(f'can_approve_leave: {admin_role.can_approve_leave}')
    print(f'can_manage_rota: {admin_role.can_manage_rota}')
    print(f'permission_level: {admin_role.permission_level}')
    
    # Update to ensure full permissions
    if not admin_role.is_management or not admin_role.is_senior_management_team:
        print(f'\n{"="*60}')
        print(f'UPDATING ADMIN ROLE PERMISSIONS')
        print(f'{"="*60}')
        
        admin_role.is_management = True
        admin_role.is_senior_management_team = True
        admin_role.can_approve_leave = True
        admin_role.can_manage_rota = True
        admin_role.permission_level = 'FULL'
        admin_role.save()
        
        print(f'✓ ADMIN role updated with full permissions')
        
        # Refresh
        admin_role.refresh_from_db()
        print(f'\nUpdated permissions:')
        print(f'  is_management: {admin_role.is_management}')
        print(f'  is_senior_management_team: {admin_role.is_senior_management_team}')
    else:
        print(f'\n✓ ADMIN role already has full permissions')
    
    # Check Admin User
    admin_user = User.objects.filter(role=admin_role).first()
    if admin_user:
        print(f'\n{"="*60}')
        print(f'ADMIN USER WITH THIS ROLE')
        print(f'{"="*60}')
        print(f'SAP: {admin_user.sap}')
        print(f'Name: {admin_user.first_name} {admin_user.last_name}')
        print(f'Role: {admin_user.role.get_name_display()}')
        print(f'is_superuser: {admin_user.is_superuser}')
        print(f'is_staff: {admin_user.is_staff}')
else:
    print('\n✗ ADMIN role not found')
