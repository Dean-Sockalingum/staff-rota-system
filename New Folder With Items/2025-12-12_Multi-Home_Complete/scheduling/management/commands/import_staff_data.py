from django.core.management.base import BaseCommand
from scheduling.models import User, Role, Unit
from datetime import datetime

class Command(BaseCommand):
    help = 'Import staff data including managers and SSCWs'

    def handle(self, *args, **options):
        self.stdout.write('Importing staff data...')
        
        # Get or create roles
        sscw_role, _ = Role.objects.get_or_create(name='SSCW', defaults={'is_management': True})
        sm_role, _ = Role.objects.get_or_create(name='SM', defaults={'is_management': True})
        om_role, _ = Role.objects.get_or_create(name='OM', defaults={'is_management': True})
        
        # Get or create units
        dementia_unit, _ = Unit.objects.get_or_create(name='DEMENTIA', defaults={'is_active': True})
        blue_unit, _ = Unit.objects.get_or_create(name='BLUE', defaults={'is_active': True})
        violet_unit, _ = Unit.objects.get_or_create(name='VIOLET', defaults={'is_active': True})
        rose_unit, _ = Unit.objects.get_or_create(name='ROSE', defaults={'is_active': True})
        grape_unit, _ = Unit.objects.get_or_create(name='GRAPE', defaults={'is_active': True})
        peach_unit, _ = Unit.objects.get_or_create(name='PEACH', defaults={'is_active': True})
        orange_unit, _ = Unit.objects.get_or_create(name='ORANGE', defaults={'is_active': True})
        green_unit, _ = Unit.objects.get_or_create(name='GREEN', defaults={'is_active': True})
        mgmt_unit, _ = Unit.objects.get_or_create(name='MGMT', defaults={'is_active': True})
        
        unit_map = {
            'DEMENTIA': dementia_unit,
            'BLUE': blue_unit,
            'VIOLET': violet_unit,
            'ROSE': rose_unit,
            'GRAPE': grape_unit,
            'PEACH': peach_unit,
            'ORANGE': orange_unit,
            'GREEN': green_unit,
            'MGMT': mgmt_unit,
        }
        
        # Staff data
        staff_data = [
            # SSCWs (Day)
            {'role': 'SSCW', 'first': 'Joe', 'last': 'Brogan', 'sap': 'SSCW0001', 'unit': 'DEMENTIA', 'team': '1', 'shifts_per_week': 3, 'shift_pref': 'DAY_SENIOR'},
            {'role': 'SSCW', 'first': 'Jack', 'last': 'Barnes', 'sap': 'SSCW0002', 'unit': 'BLUE', 'team': '1', 'shifts_per_week': 3, 'shift_pref': 'DAY_SENIOR'},
            {'role': 'SSCW', 'first': 'Morag', 'last': 'Henderson', 'sap': 'SSCW0003', 'unit': 'VIOLET', 'team': '1', 'shifts_per_week': 3, 'shift_pref': 'DAY_SENIOR'},
            {'role': 'SSCW', 'first': 'Diane', 'last': 'Smith', 'sap': 'SSCW0004', 'unit': 'ROSE', 'team': '2', 'shifts_per_week': 3, 'shift_pref': 'DAY_SENIOR'},
            {'role': 'SSCW', 'first': 'Juliet', 'last': 'Johnson', 'sap': 'SSCW0005', 'unit': 'GRAPE', 'team': '2', 'shifts_per_week': 3, 'shift_pref': 'DAY_SENIOR'},
            {'role': 'SSCW', 'first': 'Chloe', 'last': 'Agnew', 'sap': 'SSCW0006', 'unit': 'PEACH', 'team': '2', 'shifts_per_week': 3, 'shift_pref': 'DAY_SENIOR'},
            {'role': 'SSCW', 'first': 'Agnes', 'last': 'Spragg', 'sap': 'SSCW0007', 'unit': 'ORANGE', 'team': '3', 'shifts_per_week': 3, 'shift_pref': 'DAY_SENIOR'},
            {'role': 'SSCW', 'first': 'Margaret', 'last': 'Thatcher', 'sap': 'SSCW0008', 'unit': 'GREEN', 'team': '3', 'shifts_per_week': 3, 'shift_pref': 'DAY_SENIOR'},
            {'role': 'SSCW', 'first': 'Jennifer', 'last': 'Ortez', 'sap': 'SSCW0009', 'unit': 'DEMENTIA', 'team': '3', 'shifts_per_week': 3, 'shift_pref': 'DAY_SENIOR'},
            
            # SSCWs (Night)
            {'role': 'SSCW', 'first': 'Ian', 'last': 'Brown', 'sap': 'SSCWN0001', 'unit': 'DEMENTIA', 'team': '1', 'shifts_per_week': 3, 'shift_pref': 'NIGHT_SENIOR'},
            {'role': 'SSCW', 'first': 'John', 'last': 'Dollan', 'sap': 'SSCWN0002', 'unit': 'BLUE', 'team': '1', 'shifts_per_week': 3, 'shift_pref': 'NIGHT_SENIOR'},
            {'role': 'SSCW', 'first': 'Elaine', 'last': 'Martinez', 'sap': 'SSCWN0003', 'unit': 'VIOLET', 'team': '1', 'shifts_per_week': 3, 'shift_pref': 'NIGHT_SENIOR'},
            {'role': 'SSCW', 'first': 'Wendy', 'last': 'Campbell', 'sap': 'SSCWN0004', 'unit': 'ROSE', 'team': '2', 'shifts_per_week': 3, 'shift_pref': 'NIGHT_SENIOR'},
            {'role': 'SSCW', 'first': 'Nicole', 'last': 'Stewart', 'sap': 'SSCWN0005', 'unit': 'GRAPE', 'team': '2', 'shifts_per_week': 3, 'shift_pref': 'NIGHT_SENIOR'},
            {'role': 'SSCW', 'first': 'Evelyn', 'last': 'Henderson', 'sap': 'SSCWN0006', 'unit': 'PEACH', 'team': '2', 'shifts_per_week': 3, 'shift_pref': 'NIGHT_SENIOR'},
            {'role': 'SSCW', 'first': 'Ruth', 'last': 'Tyler', 'sap': 'SSCWN0007', 'unit': 'ORANGE', 'team': '3', 'shifts_per_week': 3, 'shift_pref': 'NIGHT_SENIOR'},
            {'role': 'SSCW', 'first': 'Sarah', 'last': 'Clark', 'sap': 'SSCWN0008', 'unit': 'GREEN', 'team': '3', 'shifts_per_week': 3, 'shift_pref': 'NIGHT_SENIOR'},
            
            # Managers (Supernumerary - 5 shifts per week)
            {'role': 'SM', 'first': 'Les', 'last': 'Dorson', 'sap': 'SM0001', 'unit': 'MGMT', 'team': None, 'shifts_per_week': 5, 'shift_pref': 'DAY_SENIOR'},
            {'role': 'OM', 'first': 'Jessie', 'last': 'Jones', 'sap': 'OM0002', 'unit': 'MGMT', 'team': None, 'shifts_per_week': 5, 'shift_pref': 'DAY_SENIOR'},
            {'role': 'OM', 'first': 'Wyn', 'last': 'Thomas', 'sap': 'OM0001', 'unit': 'MGMT', 'team': None, 'shifts_per_week': 5, 'shift_pref': 'DAY_SENIOR'},
        ]
        
        role_map = {
            'SSCW': sscw_role,
            'SM': sm_role,
            'OM': om_role,
        }
        
        created_count = 0
        updated_count = 0
        
        for data in staff_data:
            sap = data['sap']
            role = role_map[data['role']]
            unit = unit_map[data['unit']]
            
            user, created = User.objects.update_or_create(
                sap=sap,
                defaults={
                    'first_name': data['first'],
                    'last_name': data['last'],
                    'email': f"{data['first'].lower()}.{data['last'].lower()}@staffrota.com",
                    'role': role,
                    'unit': unit,
                    'home_unit': unit,
                    'team': data['team'],
                    'shift_preference': data['shift_pref'],
                    'shifts_per_week_override': data['shifts_per_week'],
                    'is_active': True,
                    'is_staff': role.is_management,
                }
            )
            
            # Set default password
            user.set_password('password123')
            user.save()
            
            if created:
                created_count += 1
                self.stdout.write(f'  ✓ Created: {user.full_name} ({sap}) - {role.get_name_display()}')
            else:
                updated_count += 1
                self.stdout.write(f'  ↻ Updated: {user.full_name} ({sap}) - {role.get_name_display()}')
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Import complete!'))
        self.stdout.write(self.style.SUCCESS(f'   Created: {created_count} staff'))
        self.stdout.write(self.style.SUCCESS(f'   Updated: {updated_count} staff'))
        self.stdout.write(self.style.SUCCESS(f'   Total: {created_count + updated_count} staff'))
