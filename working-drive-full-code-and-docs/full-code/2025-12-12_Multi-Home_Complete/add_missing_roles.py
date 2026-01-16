#!/usr/bin/env python
"""
Add missing roles to the database
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import Role

def add_missing_roles():
    """Add SCAN, SCWN, SSCWN, HOS, SM roles that are missing"""
    
    roles_to_create = [
        {
            'name': 'SM',
            'description': 'Service Manager',
            'is_management': True,
            'is_senior_management_team': True,
            'can_approve_leave': True,
            'can_manage_rota': True,
            'permission_level': 'FULL',
            'color_code': '#e74c3c',  # Red
        },
        {
            'name': 'OM',
            'description': 'Operations Manager',
            'is_management': True,
            'is_senior_management_team': True,
            'can_approve_leave': True,
            'can_manage_rota': True,
            'permission_level': 'FULL',
            'color_code': '#e67e22',  # Dark Orange
        },
        {
            'name': 'SSCW',
            'description': 'Senior Social Care Worker (Day)',
            'is_management': False,
            'can_approve_leave': False,
            'can_manage_rota': False,
            'permission_level': 'MOST',
            'color_code': '#3498db',  # Blue
        },
        {
            'name': 'SSCWN',
            'description': 'Senior Social Care Worker (Night)',
            'is_management': False,
            'can_approve_leave': False,
            'can_manage_rota': False,
            'permission_level': 'MOST',
            'color_code': '#9b59b6',  # Purple
        },
        {
            'name': 'SCW',
            'description': 'Social Care Worker (Day)',
            'is_management': False,
            'can_approve_leave': False,
            'can_manage_rota': False,
            'permission_level': 'LIMITED',
            'color_code': '#2ecc71',  # Green
        },
        {
            'name': 'SCWN',
            'description': 'Social Care Worker (Night)',
            'is_management': False,
            'can_approve_leave': False,
            'can_manage_rota': False,
            'permission_level': 'LIMITED',
            'color_code': '#2ecc71',  # Green
        },
        {
            'name': 'SCA',
            'description': 'Social Care Assistant (Day)',
            'is_management': False,
            'can_approve_leave': False,
            'can_manage_rota': False,
            'permission_level': 'LIMITED',
            'color_code': '#f39c12',  # Orange
        },
        {
            'name': 'SCAN',
            'description': 'Social Care Assistant (Night)',
            'is_management': False,
            'can_approve_leave': False,
            'can_manage_rota': False,
            'permission_level': 'LIMITED',
            'color_code': '#f39c12',  # Orange
        },
        {
            'name': 'HOS',
            'description': 'Head of Service',
            'is_management': True,
            'is_senior_management_team': True,
            'can_approve_leave': True,
            'can_manage_rota': True,
            'permission_level': 'FULL',
            'color_code': '#e74c3c',  # Red
        },
        {
            'name': 'Admin',
            'description': 'System Administrator',
            'is_management': True,
            'is_senior_management_team': True,
            'can_approve_leave': True,
            'can_manage_rota': True,
            'permission_level': 'FULL',
            'color_code': '#e74c3c',  # Red
        },
    ]
    
    print("\n" + "=" * 70)
    print("ADDING MISSING ROLES")
    print("=" * 70 + "\n")
    
    created_count = 0
    updated_count = 0
    
    for role_data in roles_to_create:
        role, created = Role.objects.get_or_create(
            name=role_data['name'],
            defaults=role_data
        )
        
        if created:
            print(f"✅ Created role: {role.name} - {role.description}")
            created_count += 1
        else:
            # Update existing role
            for key, value in role_data.items():
                if key != 'name':
                    setattr(role, key, value)
            role.save()
            print(f"🔄 Updated role: {role.name} - {role.description}")
            updated_count += 1
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70 + "\n")
    print(f"✅ Created: {created_count}")
    print(f"🔄 Updated: {updated_count}")
    
    print("\n📊 All roles in database:")
    for role in Role.objects.all().order_by('name'):
        mgmt_icon = "👔" if role.is_management else "👤"
        print(f"  {mgmt_icon} {role.name}: {role.description} (Permission: {role.permission_level})")
    
    print("\n" + "=" * 70 + "\n")

if __name__ == '__main__':
    add_missing_roles()
