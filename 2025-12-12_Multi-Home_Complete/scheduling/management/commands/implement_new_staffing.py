from django.core.management.base import BaseCommand
from scheduling.models import User, Role, Unit
from django.db import transaction
import random

class Command(BaseCommand):
    help = 'Replace all staff with new complement as specified in the staffing list'

    def handle(self, *args, **options):
        self.stdout.write('🔄 IMPLEMENTING NEW STAFFING STRUCTURE')
        self.stdout.write('=' * 60)
        
        with transaction.atomic():
            # First, get or create necessary roles
            roles = self.ensure_roles()
            units = list(Unit.objects.filter(name__in=[
                'BLUE', 'DEMENTIA', 'GRAPE', 'GREEN', 
                'ORANGE', 'PEACH', 'ROSE', 'VIOLET'
            ]))
            
            # Clear existing staff (keep admin accounts)
            self.stdout.write('🗑️ Removing existing staff...')
            User.objects.filter(role__name__in=[
                'SM', 'OM', 'SSCW', 'SCW', 'SCA'
            ]).exclude(sap__in=['ADMIN001']).delete()
            
            # Create new staff complement
            self.create_new_staff_complement(roles, units)
            
        self.stdout.write(self.style.SUCCESS('✅ New staffing structure implemented successfully!'))

    def ensure_roles(self):
        """Ensure all required roles exist"""
        # For existing role choices, map to our new requirements
        role_mappings = {
            'SM': 'OPERATIONS_MANAGER',  # Use OM for SM
            'OM': 'OPERATIONS_MANAGER',
            'SSCW': 'SSCW',
            'SCW': 'SCW', 
            'SCA': 'SCA',
            'ACT_COORD': 'SCA',  # Map to SCA
            'ACT_ASST': 'SCA',   # Map to SCA
            'SEC_ATTEND': 'SCA', # Map to SCA
        }
        
        roles = {}
        for role_key, role_choice in role_mappings.items():
            try:
                role = Role.objects.get(name=role_choice)
                roles[role_key] = role
            except Role.DoesNotExist:
                self.stdout.write(f'Warning: Role {role_choice} not found, creating with SCA')
                role = Role.objects.get(name='SCA')
                roles[role_key] = role
        
        return roles

    def create_new_staff_complement(self, roles, units):
        """Create the new staff complement"""
        teams = ['A', 'B', 'C']
        sap_counter = 1
        
        # Staff specifications: (role, count, shifts_per_week, is_night, is_supernumerary)
        staff_specs = [
            # Management
            ('SM', 1, 0, False, True),
            ('OM', 2, 0, False, True),
            
            # SSCW
            ('SSCW', 9, 3, False, True),  # Day SSCW
            ('SSCW', 8, 3, True, True),   # Night SSCW
            
            # SCW Day
            ('SCW', 9, 3, False, False),  # Day SCW - 3 shifts
            ('SCW', 18, 2, False, False), # Day SCW - 2 shifts
            
            # SCW Night  
            ('SCW', 7, 3, True, False),   # Night SCW - 3 shifts
            ('SCW', 8, 2, True, False),   # Night SCW - 2 shifts
            
            # SCA Day
            ('SCA', 11, 3, False, False), # Day SCA - 3 shifts
            ('SCA', 22, 2, False, False), # Day SCA - 2 shifts
            ('SCA', 6, 3, False, False),  # Additional Day SCA - 3 shifts
            
            # SCA Night
            ('SCA', 13, 3, True, False),  # Night SCA - 3 shifts
            ('SCA', 33, 2, True, False),  # Night SCA - 2 shifts
            ('SCA', 2, 3, True, False),   # Additional Night SCA - 3 shifts
            
            # SCA Special roles
            ('SCA', 4, 0, False, True),   # SCA - BC (Bank/Cover)
            ('SCA', 10, 3, False, False), # SCA - TL (Team Leader)
            
            # Support roles
            ('ACT_COORD', 1, 0, False, True),
            ('ACT_ASST', 1, 0, False, True),
            ('SEC_ATTEND', 3, 0, False, True),
        ]
        
        self.stdout.write('👥 Creating new staff complement...')
        
        for role_name, count, shifts_per_week, is_night, is_supernumerary in staff_specs:
            role = roles[role_name]
            
            for i in range(count):
                # Generate SAP number
                if role_name == 'SM':
                    sap = f'SM{sap_counter:03d}'
                elif role_name == 'OM':
                    sap = f'OM{sap_counter:03d}'
                elif role_name == 'SSCW':
                    suffix = 'N' if is_night else ''
                    sap = f'SSW{suffix}{sap_counter:03d}'
                elif role_name == 'SCW':
                    suffix = 'N' if is_night else ''
                    sap = f'SCW{suffix}{sap_counter:03d}'
                elif role_name == 'SCA':
                    suffix = 'N' if is_night else ''
                    sap = f'SCA{suffix}{sap_counter:03d}'
                elif role_name == 'ACT_COORD':
                    sap = f'AC{sap_counter:03d}'
                elif role_name == 'ACT_ASST':
                    sap = f'AA{sap_counter:03d}'
                elif role_name == 'SEC_ATTEND':
                    sap = f'SA{sap_counter:03d}'
                
                # Determine shift preference
                if is_night:
                    if role_name in ['SSCW', 'SCW']:
                        shift_pref = 'NIGHT_SENIOR'
                    else:
                        shift_pref = 'NIGHT_ASSISTANT'
                else:
                    if role_name in ['SSCW', 'SCW']:
                        shift_pref = 'DAY_SENIOR'
                    else:
                        shift_pref = 'DAY_ASSISTANT'
                
                # Assign team (for care staff only)
                team = teams[i % 3] if role_name in ['SSCW', 'SCW', 'SCA'] else None
                
                # Assign home unit (for SCW and SCA only)
                home_unit = units[i % len(units)] if role_name in ['SCW', 'SCA'] else None
                unit = home_unit  # Also set as working unit
                
                # Generate name
                first_names = ['John', 'Sarah', 'Michael', 'Emma', 'David', 'Lisa', 'James', 'Anna', 'Robert', 'Claire']
                last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
                
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                
                # Create user
                user = User.objects.create_user(
                    sap=sap,
                    first_name=first_name,
                    last_name=last_name,
                    role=role,
                    team=team,
                    shift_preference=shift_pref,
                    home_unit=home_unit,
                    unit=unit,
                    email=f'{sap.lower()}@hospital.com',
                    is_active=True,
                    password='staff123'
                )
                
                # Override shifts_per_week property with actual value
                if hasattr(user, '_shifts_per_week'):
                    user._shifts_per_week = shifts_per_week
                
                sap_counter += 1
        
        # Display summary
        self.display_summary()

    def display_summary(self):
        """Display summary of created staff"""
        self.stdout.write('\n📊 NEW STAFFING SUMMARY')
        self.stdout.write('=' * 50)
        
        total_staff = User.objects.filter(is_active=True).count()
        
        # Count by role
        role_counts = {}
        for role_name in ['SM', 'OM', 'SSCW', 'SCW', 'SCA', 'ACT_COORD', 'ACT_ASST', 'SEC_ATTEND']:
            count = User.objects.filter(role__name=role_name, is_active=True).count()
            if count > 0:
                role_counts[role_name] = count
        
        self.stdout.write(f'Total Active Staff: {total_staff}')
        self.stdout.write('\nBy Role:')
        for role, count in role_counts.items():
            self.stdout.write(f'  {role}: {count}')
        
        # Count by shift preference
        day_staff = User.objects.filter(
            shift_preference__in=['DAY_SENIOR', 'DAY_ASSISTANT'],
            is_active=True
        ).count()
        night_staff = User.objects.filter(
            shift_preference__in=['NIGHT_SENIOR', 'NIGHT_ASSISTANT'],
            is_active=True
        ).count()
        
        self.stdout.write(f'\nBy Shift:')
        self.stdout.write(f'  Day Staff: {day_staff}')
        self.stdout.write(f'  Night Staff: {night_staff}')
        
        # Count by team
        for team in ['A', 'B', 'C']:
            team_count = User.objects.filter(team=team, is_active=True).count()
            self.stdout.write(f'  Team {team}: {team_count}')