from django.core.management.base import BaseCommand
from scheduling.models import User, Shift, ShiftType
from datetime import date, timedelta
from django.db import transaction


class Command(BaseCommand):
    help = 'Generate shifts for supernumerary staff with individual 3-week rotation patterns'

    def add_arguments(self, parser):
        parser.add_argument('--weeks', type=int, default=12, help='Number of weeks to generate')
        parser.add_argument('--start-date', type=str, default='2025-12-01', help='Start date (YYYY-MM-DD)')
        parser.add_argument('--clear', action='store_true', help='Clear existing supernumerary shifts before generating')

    def handle(self, *args, **options):
        weeks = options['weeks']
        start_date_str = options['start_date']
        clear_existing = options['clear']
        
        # Parse start date and adjust to Sunday
        start_date = date.fromisoformat(start_date_str)
        days_since_sunday = start_date.weekday() + 1 if start_date.weekday() != 6 else 0
        start_date = start_date - timedelta(days=days_since_sunday)
        
        self.stdout.write(f'Starting from: {start_date} ({start_date.strftime("%A")})')
        
        # Get shift types
        day_senior = ShiftType.objects.get(name='DAY_SENIOR')
        night_senior = ShiftType.objects.get(name='NIGHT_SENIOR')
        
        # Clear existing supernumerary shifts if requested
        if clear_existing:
            deleted_count = Shift.objects.filter(
                user__role__name__in=['SSCW', 'SSCWN', 'SM', 'OM'],
                user__is_staff=True
            ).count()
            Shift.objects.filter(
                user__role__name__in=['SSCW', 'SSCWN', 'SM', 'OM'],
                user__is_staff=True
            ).delete()
            self.stdout.write(f'✓ Cleared {deleted_count} existing supernumerary shifts')
        
        # Individual 3-week rotation patterns for each staff member
        # Day indices: 0=Sun, 1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat
        # Format: 'SAP': {'week1': [days], 'week2': [days], 'week3': [days]}
        
        # SUPERNUMERARY DAY PATTERNS (SSCW):
        # Team 1: Sun Mon Tue | Wed Thu Fri | Tue Wed Thu
        # Team 2: Wed Thu Fri | Tue Wed Thu | Sun Mon Tue
        # Team 3: Tue Wed Thu | Sun Mon Tue | Wed Thu Fri
        
        # SUPERNUMERARY NIGHT PATTERNS (SSCWN):
        # Team 1: Sun Mon Tue | Wed Thu Fri | Tue Wed Thu
        # Team 2: Wed Thu Fri | Tue Wed Thu | Sun Mon Tue (note: different from spreadsheet which shows Mon for Week2)
        # Team 3: Tue Wed Thu | Sun Mon Tue | Wed Thu Fri
        
        # MANAGEMENT PATTERNS (SM, OM):
        # All management: Mon-Fri every week
        
        staff_patterns = {
            # SSCW - Day Supernumerary
            'SSCW0001': {'week1': [0, 1, 2], 'week2': [3, 4, 5], 'week3': [2, 3, 4]},  # Joe Brogan
            'SSCW0002': {'week1': [0, 1, 2], 'week2': [3, 4, 5], 'week3': [2, 3, 4]},  # Jack Barnes
            'SSCW0003': {'week1': [0, 1, 2], 'week2': [3, 4, 5], 'week3': [2, 3, 4]},  # Morag Henderson
            'SSCW0004': {'week1': [3, 4, 5], 'week2': [2, 3, 4], 'week3': [0, 1, 2]},  # Diane Smith
            'SSCW0005': {'week1': [3, 4, 5], 'week2': [2, 3, 4], 'week3': [0, 1, 2]},  # Juliet Johnson
            'SSCW0006': {'week1': [3, 4, 5], 'week2': [2, 3, 4], 'week3': [0, 1, 2]},  # Chloe Agnew
            'SSCW0007': {'week1': [2, 3, 4], 'week2': [0, 1, 2], 'week3': [3, 4, 5]},  # Agnes Spragg
            'SSCW0008': {'week1': [2, 3, 4], 'week2': [0, 1, 2], 'week3': [3, 4, 5]},  # Margaret Thatcher
            'SSCW0009': {'week1': [2, 3, 4], 'week2': [0, 1, 2], 'week3': [3, 4, 5]},  # Jennifer Ortez
            
            # SSCWN - Night Supernumerary
            'SSCWN0001': {'week1': [0, 1, 2], 'week2': [3, 4, 5], 'week3': [2, 3, 4]},  # Ian Brown
            'SSCWN0002': {'week1': [0, 1, 2], 'week2': [3, 4, 5], 'week3': [2, 3, 4]},  # John Dollan
            'SSCWN0003': {'week1': [0, 1, 2], 'week2': [3, 4, 5], 'week3': [2, 3, 4]},  # Elaine Martinez
            'SSCWN0004': {'week1': [3, 4, 5], 'week2': [1, 2, 3], 'week3': [0, 1, 2]},  # Wendy Campbell (note: Week2 starts Mon)
            'SSCWN0005': {'week1': [3, 4, 5], 'week2': [1, 2, 3], 'week3': [0, 1, 2]},  # Nicole Stewart
            'SSCWN0006': {'week1': [3, 4, 5], 'week2': [1, 2, 3], 'week3': [0, 1, 2]},  # Evelyn Henderson
            'SSCWN0007': {'week1': [2, 3, 4], 'week2': [0, 1, 2], 'week3': [3, 4, 5]},  # Ruth Tyler
            'SSCWN0008': {'week1': [2, 3, 4], 'week2': [0, 1, 2], 'week3': [3, 4, 5]},  # Sarah Clark
            
            # Management - Mon to Fri every week
            'SM0001': {'week1': [1, 2, 3, 4, 5], 'week2': [1, 2, 3, 4, 5], 'week3': [1, 2, 3, 4, 5]},  # Les Dorson
            'OM0001': {'week1': [1, 2, 3, 4, 5], 'week2': [1, 2, 3, 4, 5], 'week3': [1, 2, 3, 4, 5]},  # Wyn Thomas
            'OM0002': {'week1': [1, 2, 3, 4, 5], 'week2': [1, 2, 3, 4, 5], 'week3': [1, 2, 3, 4, 5]},  # Jessie Jones
        }
        
        # Get all supernumerary staff users
        sscw_users = {u.sap: u for u in User.objects.filter(role__name='SSCW', is_staff=True)}
        sscwn_users = {u.sap: u for u in User.objects.filter(role__name='SSCWN', is_staff=True)}
        sm_users = {u.sap: u for u in User.objects.filter(role__name='SM', is_staff=True)}
        om_users = {u.sap: u for u in User.objects.filter(role__name='OM', is_staff=True)}
        all_users = {**sscw_users, **sscwn_users, **sm_users, **om_users}
        
        total_shifts = 0
        sscw_shift_count = 0
        sscwn_shift_count = 0
        mgmt_shift_count = 0
        
        with transaction.atomic():
            # Process each staff member
            for sap, pattern in staff_patterns.items():
                if sap not in all_users:
                    self.stdout.write(self.style.WARNING(f'Warning: {sap} not found in database'))
                    continue
                
                user = all_users[sap]
                
                # Determine shift type based on role
                if user.role.name == 'SSCW':
                    shift_type = day_senior
                elif user.role.name == 'SSCWN':
                    shift_type = night_senior
                elif user.role.name in ['SM', 'OM']:
                    shift_type = day_senior
                else:
                    continue
                
                # Generate shifts for the specified number of weeks
                for week_num in range(weeks):
                    # Determine which week in the 3-week cycle (0, 1, or 2)
                    cycle_week = week_num % 3
                    week_key = f'week{cycle_week + 1}'
                    work_days = pattern[week_key]
                    
                    # Create shifts for this week
                    for day_offset in work_days:
                        shift_date = start_date + timedelta(days=(week_num * 7) + day_offset)
                        
                        Shift.objects.create(
                            user=user,
                            unit=user.home_unit,
                            shift_type=shift_type,
                            date=shift_date
                        )
                        total_shifts += 1
                        
                        if user.role.name == 'SSCW':
                            sscw_shift_count += 1
                        elif user.role.name == 'SSCWN':
                            sscwn_shift_count += 1
                        else:
                            mgmt_shift_count += 1
        
        # Calculate end date
        end_date = start_date + timedelta(days=(weeks * 7) - 1)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Created {total_shifts} supernumerary shifts over {weeks} weeks\n'
                f'   SSCW (day): {sscw_shift_count}\n'
                f'   SSCWN (night): {sscwn_shift_count}\n'
                f'   Management: {mgmt_shift_count}\n'
                f'   Date range: {start_date} to {end_date}'
            )
        )
