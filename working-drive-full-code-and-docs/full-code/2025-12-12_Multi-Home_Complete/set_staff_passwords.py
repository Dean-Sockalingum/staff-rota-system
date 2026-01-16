#!/usr/bin/env python3
"""
Set default passwords for all staff members.

Default passwords:
- Admin users: 'admin123'
- All other staff: 'password123'
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')

import django
django.setup()

from scheduling.models import User

def set_default_passwords():
    """Set default password for all active users."""
    
    # Admin users
    admin_users = User.objects.filter(sap__startswith='ADMIN')
    admin_count = 0
    for user in admin_users:
        user.set_password('admin123')
        user.save(update_fields=['password'])
        admin_count += 1
        print(f"✓ Set admin password for {user.sap}: {user.first_name} {user.last_name}")
    
    print(f"\n{'='*60}")
    print(f"Admin users updated: {admin_count}")
    print(f"{'='*60}\n")
    
    # Regular staff - all active users
    regular_users = User.objects.filter(is_active=True).exclude(sap__startswith='ADMIN')
    
    # Count users needing password update
    no_password = regular_users.filter(password='').count()
    unusable_password = sum(1 for u in regular_users if not u.has_usable_password())
    
    print(f"Regular staff analysis:")
    print(f"  Total active staff: {regular_users.count()}")
    print(f"  Users with empty password: {no_password}")
    print(f"  Users with unusable password: {unusable_password}")
    print(f"  Total needing update: {unusable_password}\n")
    
    updated_count = 0
    for user in regular_users:
        user.set_password('password123')
        user.save(update_fields=['password'])
        updated_count += 1
        
        if updated_count <= 10:
            print(f"✓ Set password for {user.sap}: {user.first_name} {user.last_name} ({user.role.name if user.role else 'No role'})")
        elif updated_count % 100 == 0:
            print(f"  ... {updated_count} users processed ...")
    
    print(f"\n{'='*60}")
    print(f"Regular staff updated: {updated_count}")
    print(f"{'='*60}\n")
    
    # Verify passwords work
    print("Verification:")
    test_user = User.objects.filter(is_active=True).exclude(sap__startswith='ADMIN').first()
    if test_user:
        print(f"  Testing {test_user.sap}: {test_user.first_name} {test_user.last_name}")
        print(f"  Password check for 'password123': {test_user.check_password('password123')}")
    
    admin_test = User.objects.filter(sap='ADMIN001').first()
    if admin_test:
        print(f"  Testing {admin_test.sap}")
        print(f"  Password check for 'admin123': {admin_test.check_password('admin123')}")
    
    print(f"\n{'='*60}")
    print("SUMMARY:")
    print(f"  Admin users (password: admin123): {admin_count}")
    print(f"  Regular staff (password: password123): {updated_count}")
    print(f"  Total users updated: {admin_count + updated_count}")
    print(f"{'='*60}")

if __name__ == '__main__':
    set_default_passwords()
