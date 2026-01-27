# Generated manually on 2026-01-22 to create HOS, SM, IDI roles

from django.db import migrations


def create_senior_leadership_roles(apps, schema_editor):
    """Create the HOS, SM, and IDI roles if they don't exist"""
    Role = apps.get_model('scheduling', 'Role')
    
    # Define the senior leadership roles to create
    senior_roles = [
        {
            'name': 'HOS',
            'description': 'Head of Service - Strategic oversight across all 5 care homes',
            'is_management': True,
            'is_senior_management_team': True,
            'can_approve_leave': True,
            'can_manage_rota': True,
            'permission_level': 'FULL',
            'color_code': '#9b59b6',  # Purple
            'required_headcount': 1
        },
        {
            'name': 'IDI',
            'description': 'Improvement, Development & Innovation Manager - Portfolio-wide quality improvement',
            'is_management': True,
            'is_senior_management_team': True,
            'can_approve_leave': True,
            'can_manage_rota': True,
            'permission_level': 'FULL',
            'color_code': '#e67e22',  # Dark Orange
            'required_headcount': 1
        },
        {
            'name': 'SM',
            'description': 'Service Manager - Quality and compliance management across all homes',
            'is_management': True,
            'is_senior_management_team': True,
            'can_approve_leave': True,
            'can_manage_rota': True,
            'permission_level': 'FULL',
            'color_code': '#3498db',  # Blue
            'required_headcount': 5
        },
        {
            'name': 'OM',
            'description': 'Operations Manager - Day-to-day management across all homes',
            'is_management': True,
            'is_senior_management_team': True,
            'can_approve_leave': True,
            'can_manage_rota': True,
            'permission_level': 'FULL',
            'color_code': '#2ecc71',  # Green
            'required_headcount': 9
        },
    ]
    
    # Create each role if it doesn't exist
    for role_data in senior_roles:
        Role.objects.get_or_create(
            name=role_data['name'],
            defaults=role_data
        )
    
    # Update OPERATIONS_MANAGER to OM if it exists
    try:
        old_om = Role.objects.get(name='OPERATIONS_MANAGER')
        # Get the new OM role
        new_om, created = Role.objects.get_or_create(
            name='OM',
            defaults={
                'description': old_om.description or 'Operations Manager - Day-to-day management across all homes',
                'is_management': True,
                'is_senior_management_team': True,
                'can_approve_leave': True,
                'can_manage_rota': True,
                'permission_level': 'FULL',
                'color_code': old_om.color_code,
                'required_headcount': old_om.required_headcount
            }
        )
        # Migrate users from old OPERATIONS_MANAGER to new OM
        User = apps.get_model('scheduling', 'User')
        User.objects.filter(role=old_om).update(role=new_om)
        # Delete old role
        old_om.delete()
    except Role.DoesNotExist:
        pass  # No old OPERATIONS_MANAGER role to migrate


def reverse_migration(apps, schema_editor):
    """Remove the senior leadership roles"""
    Role = apps.get_model('scheduling', 'Role')
    Role.objects.filter(name__in=['HOS', 'IDI', 'SM', 'OM']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0064_add_senior_leadership_roles'),
    ]

    operations = [
        migrations.RunPython(create_senior_leadership_roles, reverse_migration),
    ]
