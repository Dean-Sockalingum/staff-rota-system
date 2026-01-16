from django.core.management.base import BaseCommand
from scheduling.models import User, Role, Unit


class Command(BaseCommand):
    help = 'Import supernumerary staff (SSCW, SSCWN, SM, OM)'

    def handle(self, *args, **options):
        self.stdout.write('Importing supernumerary staff...')
        
        # Supernumerary staff data
        staff_data = [
            # SSCW - Day shift supernumerary
            {'role': 'SSCW', 'first': 'Joe', 'last': 'Brogan', 'sap': 'SSCW0001', 'hours': 35, 'shifts_per_week': 3, 'unit': 'DEMENTIA', 'team': 'A'},
            {'role': 'SSCW', 'first': 'Jack', 'last': 'Barnes', 'sap': 'SSCW0002', 'hours': 35, 'shifts_per_week': 3, 'unit': 'BLUE', 'team': 'A'},
            {'role': 'SSCW', 'first': 'Morag', 'last': 'Henderson', 'sap': 'SSCW0003', 'hours': 35, 'shifts_per_week': 3, 'unit': 'VIOLET', 'team': 'A'},
            {'role': 'SSCW', 'first': 'Diane', 'last': 'Smith', 'sap': 'SSCW0004', 'hours': 35, 'shifts_per_week': 3, 'unit': 'ROSE', 'team': 'B'},
            {'role': 'SSCW', 'first': 'Juliet', 'last': 'Johnson', 'sap': 'SSCW0005', 'hours': 35, 'shifts_per_week': 3, 'unit': 'GRAPE', 'team': 'B'},
            {'role': 'SSCW', 'first': 'Chloe', 'last': 'Agnew', 'sap': 'SSCW0006', 'hours': 35, 'shifts_per_week': 3, 'unit': 'PEACH', 'team': 'B'},
            {'role': 'SSCW', 'first': 'Agnes', 'last': 'Spragg', 'sap': 'SSCW0007', 'hours': 35, 'shifts_per_week': 3, 'unit': 'ORANGE', 'team': 'C'},
            {'role': 'SSCW', 'first': 'Margaret', 'last': 'Thatcher', 'sap': 'SSCW0008', 'hours': 35, 'shifts_per_week': 3, 'unit': 'GREEN', 'team': 'C'},
            {'role': 'SSCW', 'first': 'Jennifer', 'last': 'Ortez', 'sap': 'SSCW0009', 'hours': 35, 'shifts_per_week': 3, 'unit': 'DEMENTIA', 'team': 'C'},
            
            # SSCWN - Night shift supernumerary
            {'role': 'SSCWN', 'first': 'Ian', 'last': 'Brown', 'sap': 'SSCWN0001', 'hours': 35, 'shifts_per_week': 3, 'unit': 'DEMENTIA', 'team': 'A'},
            {'role': 'SSCWN', 'first': 'John', 'last': 'Dollan', 'sap': 'SSCWN0002', 'hours': 35, 'shifts_per_week': 3, 'unit': 'BLUE', 'team': 'A'},
            {'role': 'SSCWN', 'first': 'Elaine', 'last': 'Martinez', 'sap': 'SSCWN0003', 'hours': 35, 'shifts_per_week': 3, 'unit': 'VIOLET', 'team': 'A'},
            {'role': 'SSCWN', 'first': 'Wendy', 'last': 'Campbell', 'sap': 'SSCWN0004', 'hours': 35, 'shifts_per_week': 3, 'unit': 'ROSE', 'team': 'B'},
            {'role': 'SSCWN', 'first': 'Nicole', 'last': 'Stewart', 'sap': 'SSCWN0005', 'hours': 35, 'shifts_per_week': 3, 'unit': 'GRAPE', 'team': 'B'},
            {'role': 'SSCWN', 'first': 'Evelyn', 'last': 'Henderson', 'sap': 'SSCWN0006', 'hours': 35, 'shifts_per_week': 3, 'unit': 'PEACH', 'team': 'B'},
            {'role': 'SSCWN', 'first': 'Ruth', 'last': 'Tyler', 'sap': 'SSCWN0007', 'hours': 35, 'shifts_per_week': 3, 'unit': 'ORANGE', 'team': 'C'},
            {'role': 'SSCWN', 'first': 'Sarah', 'last': 'Clark', 'sap': 'SSCWN0008', 'hours': 35, 'shifts_per_week': 3, 'unit': 'GREEN', 'team': 'C'},
            
            # Management - SM and OM (Mon-Fri)
            {'role': 'SM', 'first': 'Les', 'last': 'Dorson', 'sap': 'SM0001', 'hours': 35, 'shifts_per_week': 5, 'unit': 'MGMT', 'team': 'MGMT'},
            {'role': 'OM', 'first': 'Jessie', 'last': 'Jones', 'sap': 'OM0002', 'hours': 35, 'shifts_per_week': 5, 'unit': 'MGMT', 'team': 'MGMT'},
            {'role': 'OM', 'first': 'Wyn', 'last': 'Thomas', 'sap': 'OM0001', 'hours': 35, 'shifts_per_week': 5, 'unit': 'MGMT', 'team': 'MGMT'},
        ]
        
        # Unit mapping
        unit_map = {
            'DEMENTIA': 'DEMENTIA',
            'BLUE': 'BLUE',
            'VIOLET': 'VIOLET',
            'ROSE': 'ROSE',
            'GRAPE': 'GRAPE',
            'PEACH': 'PEACH',
            'ORANGE': 'ORANGE',
            'GREEN': 'GREEN',
            'MGMT': 'MGMT',
        }
        
        # Ensure all roles exist
        roles_to_create = {
            'SSCW': {'is_management': False, 'can_approve_leave': False, 'can_manage_rota': False, 'color_code': '#FFFF99'},
            'SSCWN': {'is_management': False, 'can_approve_leave': False, 'can_manage_rota': False, 'color_code': '#FFFF99'},
            'SM': {'is_management': True, 'can_approve_leave': True, 'can_manage_rota': True, 'color_code': '#FFB6C1'},
            'OM': {'is_management': True, 'can_approve_leave': True, 'can_manage_rota': True, 'color_code': '#FFB6C1'},
        }
        
        for role_name, role_attrs in roles_to_create.items():
            Role.objects.get_or_create(
                name=role_name,
                defaults=role_attrs
            )
        
        created_count = 0
        updated_count = 0
        
        for data in staff_data:
            role = Role.objects.get(name=data['role'])
            unit = Unit.objects.get(name=unit_map[data['unit']])
            
            # Determine shift preference based on role
            if data['role'] == 'SSCW':
                shift_preference = 'DAY_SENIOR'
            elif data['role'] == 'SSCWN':
                shift_preference = 'NIGHT_SENIOR'
            elif data['role'] in ['SM', 'OM']:
                shift_preference = 'DAY_SENIOR'  # Management works day shifts
            else:
                shift_preference = 'DAY_SENIOR'
            
            # Create or update user
            user, created = User.objects.update_or_create(
                sap=data['sap'],
                defaults={
                    'first_name': data['first'],
                    'last_name': data['last'],
                    'email': f"{data['first'].lower()}.{data['last'].lower()}@staffrota.com",
                    'role': role,
                    'unit': unit,
                    'home_unit': unit,
                    'team': data['team'],
                    'shift_preference': shift_preference,
                    'shifts_per_week_override': data['shifts_per_week'],
                    'is_active': True,
                    'is_staff': True,  # Supernumerary staff
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
                created_count += 1
                self.stdout.write(f'  ✓ Created: {user.first_name} {user.last_name} ({user.sap}) - {role.name}')
            else:
                updated_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Supernumerary import complete!\n'
            f'Created: {created_count} staff\n'
            f'Updated: {updated_count} staff\n'
            f'Total: {created_count + updated_count} supernumerary staff'
        ))
