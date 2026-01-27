from django.core.management.base import BaseCommand
from scheduling.models import User, ShiftType
from datetime import time
import random

class Command(BaseCommand):
    help = 'Setup shift patterns with correct times for each role type'

    def handle(self, *args, **options):
        self.stdout.write('Setting up role-specific shift patterns...')
        
        # Clear existing shift types
        ShiftType.objects.all().delete()
        
        # Create role-specific shift types with correct times
        shift_types = [
            {
                'name': 'DAY_SENIOR',
                'start_time': time(7, 45),   # 07:45
                'end_time': time(20, 15),    # 20:15
                'duration_hours': 12.5,      # 12.5 hours
                'applicable_roles': 'SSCW,SCW',
                'color_code': '#e67e22',     # Orange for day senior
            },
            {
                'name': 'DAY_ASSISTANT', 
                'start_time': time(8, 0),    # 08:00
                'end_time': time(20, 0),     # 20:00
                'duration_hours': 12.0,      # 12 hours
                'applicable_roles': 'SCA',
                'color_code': '#f39c12',     # Light orange for day assistant
            },
            {
                'name': 'NIGHT_SENIOR',
                'start_time': time(19, 45),  # 19:45
                'end_time': time(8, 15),     # 08:15 next day
                'duration_hours': 12.5,      # 12.5 hours
                'applicable_roles': 'SSCW,SCW',
                'color_code': '#2c3e50',     # Dark blue for night senior
            },
            {
                'name': 'NIGHT_ASSISTANT',
                'start_time': time(20, 0),   # 20:00
                'end_time': time(8, 0),      # 08:00 next day
                'duration_hours': 12.0,      # 12 hours
                'applicable_roles': 'SCA',
                'color_code': '#34495e',     # Medium blue for night assistant
            },
            {
                'name': 'ADMIN',
                'start_time': time(9, 0),    # 09:00
                'end_time': time(17, 0),     # 17:00
                'duration_hours': 8.0,
                'applicable_roles': 'SSCW,SCW',
                'color_code': '#95a5a6',     # Neutral grey for admin
            },
        ]
        
        for shift_data in shift_types:
            shift_type = ShiftType.objects.create(**shift_data)
            self.stdout.write(f'✅ Created: {shift_type}')
        
        self.stdout.write(f'\n📊 CORRECT SHIFT PATTERNS CONFIGURED:')
        self.stdout.write('=' * 60)
        
        for shift_type in ShiftType.objects.all():
            roles = shift_type.get_applicable_roles_list()
            self.stdout.write(f'{shift_type.get_name_display()}:')
            self.stdout.write(f'  Time: {shift_type.start_time} - {shift_type.end_time}')
            self.stdout.write(f'  Duration: {shift_type.duration_hours} hours')
            self.stdout.write(f'  Roles: {", ".join(roles)}')
            self.stdout.write('')
        
        # Update staff shift preferences to use correct shift types
        self.assign_shift_preferences()
        
        self.stdout.write(f'✅ All shift patterns updated with correct times!')

    def assign_shift_preferences(self):
        """Assign shift preferences based on role-specific shift types"""
        
        self.stdout.write(f'\n🔄 Assigning role-specific shift preferences...')
        
        care_staff = User.objects.filter(
            role__name__in=['SCW', 'SCA', 'SSCW'],
            is_active=True
        ).select_related('role')
        
        # Balance day/night preferences (roughly 60% day, 40% night)
        total_staff = care_staff.count()
        day_staff_target = int(total_staff * 0.6)
        
        # Randomly assign preferences
        staff_list = list(care_staff)
        random.shuffle(staff_list)
        
        day_count = 0
        night_count = 0
        
        for staff in staff_list:
            # Respect existing preference if already aligned with the role-specific options.
            if staff.shift_preference in ['DAY_SENIOR', 'NIGHT_SENIOR', 'DAY_ASSISTANT', 'NIGHT_ASSISTANT']:
                if staff.role.name in ['SSCW', 'SCW'] and staff.shift_preference in ['DAY_SENIOR', 'NIGHT_SENIOR']:
                    if staff.shift_preference == 'DAY_SENIOR':
                        day_count += 1
                    else:
                        night_count += 1
                    continue
                if staff.role.name == 'SCA' and staff.shift_preference in ['DAY_ASSISTANT', 'NIGHT_ASSISTANT']:
                    if staff.shift_preference == 'DAY_ASSISTANT':
                        day_count += 1
                    else:
                        night_count += 1
                    continue

            if day_count < day_staff_target:
                # Assign to day shift based on role
                if staff.role.name in ['SSCW', 'SCW']:
                    staff.shift_preference = 'DAY_SENIOR'
                else:  # SCA
                    staff.shift_preference = 'DAY_ASSISTANT'
                day_count += 1
            else:
                # Assign to night shift based on role
                if staff.role.name in ['SSCW', 'SCW']:
                    staff.shift_preference = 'NIGHT_SENIOR'
                else:  # SCA
                    staff.shift_preference = 'NIGHT_ASSISTANT'
                night_count += 1

            staff.save()
        
        # Summary by role and shift type
        self.stdout.write(f'\n📊 ROLE-SPECIFIC SHIFT ASSIGNMENTS:')
        self.stdout.write('=' * 50)
        
        for role_name in ['SSCW', 'SCW', 'SCA']:
            role_staff = care_staff.filter(role__name=role_name)
            total = role_staff.count()
            
            if role_name in ['SSCW', 'SCW']:
                day_staff = role_staff.filter(shift_preference='DAY_SENIOR').count()
                night_staff = role_staff.filter(shift_preference='NIGHT_SENIOR').count()
                day_shift = 'DAY_SENIOR (07:45-20:15)'
                night_shift = 'NIGHT_SENIOR (19:45-08:15)'
            else:  # SCA
                day_staff = role_staff.filter(shift_preference='DAY_ASSISTANT').count()
                night_staff = role_staff.filter(shift_preference='NIGHT_ASSISTANT').count()
                day_shift = 'DAY_ASSISTANT (08:00-20:00)'
                night_shift = 'NIGHT_ASSISTANT (20:00-08:00)'
            
            shifts_per_week = role_staff.first().shifts_per_week if role_staff.exists() else 0
            
            self.stdout.write(f'\n{role_name}: {total} staff')
            self.stdout.write(f'  📅 Shifts per week: {shifts_per_week}')
            self.stdout.write(f'  🌅 {day_shift}: {day_staff} ({round(day_staff/total*100,1)}%)')
            self.stdout.write(f'  🌙 {night_shift}: {night_staff} ({round(night_staff/total*100,1)}%)')
        
        self.stdout.write(f'\n🎯 SUMMARY:')
        self.stdout.write(f'Total day staff: {day_count} ({round(day_count/total_staff*100,1)}%)')
        self.stdout.write(f'Total night staff: {night_count} ({round(night_count/total_staff*100,1)}%)')