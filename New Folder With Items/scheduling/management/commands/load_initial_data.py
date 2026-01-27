from django.core.management.base import BaseCommand
from django.utils import timezone
from scheduling.models import Role, Unit, ShiftType, User
from datetime import time

class Command(BaseCommand):
    help = 'Load initial data for the staff rota system'

    def handle(self, *args, **options):
        self.stdout.write('Loading initial data...')
        
        # Create Roles with 6-week rotation staffing requirements
        # Only roles that work rota schedules
        roles = [
            # Management roles (Operations Manager handles all manager responsibilities)
            {'name': 'OPERATIONS_MANAGER', 'is_management': True, 'can_approve_leave': True, 'can_manage_rota': True, 'required_headcount': 1},
            {'name': 'SSCW', 'is_management': True, 'can_approve_leave': True, 'can_manage_rota': True, 'required_headcount': 24},  # 1 per unit × 8 units × 3 teams
            
            # Core care roles calculated for 6-week rotation
            # SCW: (7 units × 2 shifts × 1 SCW) + (1 dementia × 2 shifts × 1 SCW) = 16 SCW per day × 3 teams = 48 SCW
            {'name': 'SCW', 'is_management': False, 'can_approve_leave': False, 'can_manage_rota': False, 'required_headcount': 48},
            
            # SCA: Standard units (7 × 2 × 1.5 avg) + Dementia (1 × 2 × 2.5 avg) = 26 SCA per day × 3 teams = 78 SCA  
            {'name': 'SCA', 'is_management': False, 'can_approve_leave': False, 'can_manage_rota': False, 'required_headcount': 78},
        ]
        
        for role_data in roles:
            role, created = Role.objects.get_or_create(name=role_data['name'], defaults=role_data)
            if created:
                self.stdout.write(f'Created role: {role.get_name_display()}')
        
        # Create Units - 8 Care Units with correct staffing minimums
        units_data = [
            # Dementia unit with enhanced staffing (1 SCW + 3 SCA days, 1 SCW + 2 SCA nights)
            {'name': 'DEMENTIA', 'min_day_staff': 4, 'min_night_staff': 3, 'min_weekend_staff': 4},
            
            # Standard residential care units (1 SCW + 2 SCA days, 1 SCW + 1 SCA nights)
            {'name': 'BLUE', 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'GREEN', 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'ROSE', 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'VIOLET', 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'ORANGE', 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'PEACH', 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'GRAPE', 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            
            # Administrative area
            {'name': 'ADMIN', 'min_day_staff': 1, 'min_night_staff': 0, 'min_weekend_staff': 0},
        ]
        
        for unit_data in units_data:
            unit, created = Unit.objects.get_or_create(name=unit_data['name'], defaults=unit_data)
            if created:
                self.stdout.write(f'Created unit: {unit.get_name_display()}')
        
                # Create Shift Types with 15-minute handover for SCW
        shift_types = [
            # Senior Care Worker shifts (with 15-min handover)
            {'name': 'LONG_DAY', 'start_time': '07:45', 'end_time': '20:15', 'color_code': '#28a745', 'duration_hours': 12.5},
            {'name': 'NIGHT', 'start_time': '19:45', 'end_time': '08:15', 'color_code': '#17a2b8', 'duration_hours': 12.5},
            
            # Senior Care Assistant shifts (standard 12 hours)
            {'name': 'DAY', 'start_time': '08:00', 'end_time': '20:00', 'color_code': '#fd7e14', 'duration_hours': 12.0},
            {'name': 'EARLY', 'start_time': '08:00', 'end_time': '20:00', 'color_code': '#6f42c1', 'duration_hours': 12.0},
            
            # Admin and other shifts
            {'name': 'LATE', 'start_time': '09:00', 'end_time': '17:00', 'color_code': '#ffc107', 'duration_hours': 8.0},
            {'name': 'ON_CALL', 'start_time': '09:00', 'end_time': '17:00', 'color_code': '#20c997', 'duration_hours': 8.0},
        ]
        
        for shift_data in shift_types:
            shift, created = ShiftType.objects.get_or_create(name=shift_data['name'], defaults=shift_data)
            if created:
                self.stdout.write(f'Created shift type: {shift.get_name_display()}')
        
        # Create sample admin user
        admin_role = Role.objects.get(name='ADMIN')
        admin_user, created = User.objects.get_or_create(
            sap='ADMIN001',
            defaults={
                'first_name': 'System',
                'last_name': 'Administrator',
                'email': 'admin@staffrota.com',
                'role': admin_role,
                'is_staff': True,
                'is_superuser': True,
                'annual_leave_allowance': 28,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('Created admin user: ADMIN001 (password: admin123)')
        
        # Create sample manager user
        manager_role = Role.objects.get(name='OPERATIONS_MANAGER')
        manager_user, created = User.objects.get_or_create(
            sap='MGR001',
            defaults={
                'first_name': 'John',
                'last_name': 'Manager',
                'email': 'manager@staffrota.com',
                'role': manager_role,
                'is_staff': True,
                'annual_leave_allowance': 28,
            }
        )
        if created:
            manager_user.set_password('manager123')
            manager_user.save()
            self.stdout.write('Created manager user: MGR001 (password: manager123)')
        
        # Create sample staff users
        scw_role = Role.objects.get(name='SCW')
        sca_role = Role.objects.get(name='SCA')
        
        staff_users = [
            {'sap': 'SCW001', 'first_name': 'Alice', 'last_name': 'Johnson', 'email': 'alice@staffrota.com', 'role': scw_role},
            {'sap': 'SCW002', 'first_name': 'Bob', 'last_name': 'Smith', 'email': 'bob@staffrota.com', 'role': scw_role},
            {'sap': 'SCA001', 'first_name': 'Carol', 'last_name': 'Brown', 'email': 'carol@staffrota.com', 'role': sca_role},
            {'sap': 'SCA002', 'first_name': 'David', 'last_name': 'Wilson', 'email': 'david@staffrota.com', 'role': sca_role},
        ]
        
        for staff_data in staff_users:
            user, created = User.objects.get_or_create(
                sap=staff_data['sap'],
                defaults={**staff_data, 'annual_leave_allowance': 28}
            )
            if created:
                user.set_password('staff123')
                user.save()
                self.stdout.write(f'Created staff user: {user.sap} (password: staff123)')
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded initial data!'))