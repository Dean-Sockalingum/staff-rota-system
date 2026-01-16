import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
import django
django.setup()

from scheduling.models import User, Role

# Find the current Admin User
admin = User.objects.filter(first_name='Admin', last_name='User').first()

if admin:
    print(f'\n{"="*60}')
    print(f'ADMIN USER - CURRENT STATE')
    print(f'{"="*60}')
    print(f'SAP: {admin.sap}')
    print(f'Name: {admin.first_name} {admin.last_name}')
    print(f'Role: {admin.role}')
    print(f'is_staff: {admin.is_staff}')
    print(f'is_superuser: {admin.is_superuser}')
    
    # Check available roles
    print(f'\n{"="*60}')
    print(f'AVAILABLE ROLES')
    print(f'{"="*60}')
    roles = Role.objects.all()
    for role in roles:
        print(f'  - {role.name}: {role.get_name_display()} (is_management={role.is_management})')
    
    # Check for ADMIN role
    admin_role = Role.objects.filter(name='ADMIN').first()
    
    if admin_role:
        if admin.role != admin_role:
            print(f'\n{"="*60}')
            print(f'ASSIGNING ADMIN ROLE')
            print(f'{"="*60}')
            admin.role = admin_role
            admin.save()
            print(f'✓ Admin role assigned')
            
            admin.refresh_from_db()
            print(f'Updated role: {admin.role.get_name_display() if admin.role else None}')
        else:
            print(f'\n✓ Admin already has ADMIN role')
    else:
        print(f'\n✗ ADMIN role not found in database')
        print(f'Creating ADMIN role...')
        
        # Create ADMIN role if it doesn't exist
        admin_role = Role.objects.create(
            name='ADMIN',
            description='System Administrator with full access',
            is_management=True,
            can_approve_leave=True,
            can_manage_rota=True,
            permission_level='FULL'
        )
        print(f'✓ ADMIN role created')
        
        admin.role = admin_role
        admin.save()
        print(f'✓ ADMIN role assigned to Admin User')
else:
    print('\n✗ Admin User not found')
