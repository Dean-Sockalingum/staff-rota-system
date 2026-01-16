from django.core.management.base import BaseCommand
from scheduling.models import User, Shift, ShiftType, Unit
from datetime import date, timedelta
from django.db import transaction


class Command(BaseCommand):
    help = 'Generate day care shifts (SCW and SCA) with individual 3-week rotation patterns for each staff member'

    def add_arguments(self, parser):
        parser.add_argument('--weeks', type=int, default=12, help='Number of weeks to generate')
        parser.add_argument('--start-date', type=str, default='2025-12-01', help='Start date (YYYY-MM-DD)')
        parser.add_argument('--clear', action='store_true', help='Clear existing SCW/SCA shifts before generating')

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
        day_assistant = ShiftType.objects.get(name='DAY_ASSISTANT')
        
        # Clear existing shifts if requested
        if clear_existing:
            deleted_count = Shift.objects.filter(
                user__role__name__in=['SCW', 'SCA'],
                user__is_staff=False
            ).count()
            Shift.objects.filter(
                user__role__name__in=['SCW', 'SCA'],
                user__is_staff=False
            ).delete()
            self.stdout.write(f'✓ Cleared {deleted_count} existing SCW/SCA shifts')
        
        # Individual 3-week rotation patterns for each staff member
        # Day indices: 0=Sun, 1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat
        # Format: 'SAP': {'week1': [days], 'week2': [days], 'week3': [days]}
        
        staff_patterns = {
            # Team B - SCW 3-shift (35hr): Wed Fri Sat | Sun Wed Thu | Mon Tue Wed
            'SCW1001': {'week1': [3, 5, 6], 'week2': [0, 3, 4], 'week3': [1, 2, 3]},  # Alice Smith
            'SCW1002': {'week1': [3, 5, 6], 'week2': [0, 3, 4], 'week3': [1, 2, 3]},  # Bob Johnson
            'SCW1003': {'week1': [3, 5, 6], 'week2': [0, 3, 4], 'week3': [1, 2, 3]},  # Carol Williams
            # Team B - SCW 2-shift (24hr): Fri Sat | Sun Thu | Mon Tue
            'SCW1004': {'week1': [5, 6], 'week2': [0, 4], 'week3': [1, 2]},  # David Brown
            'SCW1005': {'week1': [5, 6], 'week2': [0, 4], 'week3': [1, 2]},  # Emily Jones
            'SCW1006': {'week1': [5, 6], 'week2': [0, 4], 'week3': [1, 2]},  # Frank Garcia
            'SCW1007': {'week1': [5, 6], 'week2': [0, 4], 'week3': [1, 2]},  # Grace Miller
            'SCW1008': {'week1': [5, 6], 'week2': [0, 4], 'week3': [1, 2]},  # Henry Davis
            'SCW1009': {'week1': [5, 6], 'week2': [0, 4], 'week3': [1, 2]},  # Ivy Rodriguez
            # Team B - SCA 3-shift (35hr): Wed Fri Sat | Sun Wed Thu | Mon Tue Wed
            'SCA1010': {'week1': [3, 5, 6], 'week2': [0, 3, 4], 'week3': [1, 2, 3]},  # Jack Martinez
            'SCA1011': {'week1': [3, 5, 6], 'week2': [0, 3, 4], 'week3': [1, 2, 3]},  # Karen Hernandez
            'SCA1012': {'week1': [3, 5, 6], 'week2': [0, 3, 4], 'week3': [1, 2, 3]},  # Liam Lopez
            'SCA1013': {'week1': [3, 5, 6], 'week2': [0, 3, 4], 'week3': [1, 2, 3]},  # Mia Gonzalez
            'SCA1014': {'week1': [3, 5, 6], 'week2': [0, 3, 4], 'week3': [1, 2, 3]},  # Noah Wilson
            'SCA1015': {'week1': [3, 5, 6], 'week2': [0, 3, 4], 'week3': [1, 2, 3]},  # Olivia Anderson
            'SCA1016': {'week1': [3, 5, 6], 'week2': [0, 3, 4], 'week3': [1, 2, 3]},  # Peter Thomas
            'SCA1017': {'week1': [3, 5, 6], 'week2': [0, 3, 4], 'week3': [1, 2, 3]},  # Quinn Taylor
            'SCA1018': {'week1': [3, 5, 6], 'week2': [0, 3, 4], 'week3': [1, 2, 3]},  # Rachel Moore
            # Team B - SCA 2-shift (24hr): Fri Sat | Sun Thu | Mon Tue
            'SCA1019': {'week1': [5, 6], 'week2': [0, 4], 'week3': [1, 2]},  # Sam Jackson
            'SCA1020': {'week1': [5, 6], 'week2': [0, 4], 'week3': [1, 2]},  # Tina Martin
            'SCA1021': {'week1': [5, 6], 'week2': [0, 4], 'week3': [1, 2]},  # Uma Lee
            'SCA1022': {'week1': [5, 6], 'week2': [0, 4], 'week3': [1, 2]},  # Victor Perez
            'SCA1023': {'week1': [5, 6], 'week2': [0, 4], 'week3': [1, 2]},  # Wendy Thompson
            'SCA1024': {'week1': [5, 6], 'week2': [0, 4], 'week3': [1, 2]},  # Xander White
            'SCA1025': {'week1': [5, 6], 'week2': [0, 4], 'week3': [1, 2]},  # Yara Harris
            
            # Team C - SCW 3-shift (35hr): Sun Wed Thu | Mon Tue Wed | Wed Fri Sat
            'SCW1026': {'week1': [0, 3, 4], 'week2': [1, 2, 3], 'week3': [3, 5, 6]},  # Zoe Sanchez
            'SCW1027': {'week1': [0, 3, 4], 'week2': [1, 2, 3], 'week3': [3, 5, 6]},  # Aaron Clark
            'SCW1028': {'week1': [0, 3, 4], 'week2': [1, 2, 3], 'week3': [3, 5, 6]},  # Bella Ramirezz
            # Team C - SCW 2-shift (24hr): Sun Thu | Mon Tue | Fri Sat
            'SCW1029': {'week1': [0, 4], 'week2': [1, 2], 'week3': [5, 6]},  # Caleb Lewis
            'SCW1030': {'week1': [0, 4], 'week2': [1, 2], 'week3': [5, 6]},  # Diana Robinson
            'SCW1031': {'week1': [0, 4], 'week2': [1, 2], 'week3': [5, 6]},  # Ethan Walker
            'SCW1032': {'week1': [0, 4], 'week2': [1, 2], 'week3': [5, 6]},  # Fiona Young
            'SCW1033': {'week1': [0, 4], 'week2': [1, 2], 'week3': [5, 6]},  # George Allen
            'SCW1034': {'week1': [0, 4], 'week2': [1, 2], 'week3': [5, 6]},  # Hannah King
            # Team C - SCA 3-shift (35hr): Sun Wed Thu | Mon Tue Wed | Wed Fri Sat
            'SCA1035': {'week1': [0, 3, 4], 'week2': [1, 2, 3], 'week3': [3, 5, 6]},  # Isaac Wright
            'SCA1036': {'week1': [0, 3, 4], 'week2': [1, 2, 3], 'week3': [3, 5, 6]},  # Julia Scott
            'SCA1037': {'week1': [0, 3, 4], 'week2': [1, 2, 3], 'week3': [3, 5, 6]},  # Kyle Torres
            'SCA1038': {'week1': [0, 3, 4], 'week2': [1, 2, 3], 'week3': [3, 5, 6]},  # Luna Nguyen
            'SCA1039': {'week1': [0, 3, 4], 'week2': [1, 2, 3], 'week3': [3, 5, 6]},  # Mark Hill
            'SCA1040': {'week1': [0, 3, 4], 'week2': [1, 2, 3], 'week3': [3, 5, 6]},  # Nora Green
            'SCA1041': {'week1': [0, 3, 4], 'week2': [1, 2, 3], 'week3': [3, 5, 6]},  # Oscar Adams
            'SCA1042': {'week1': [0, 3, 4], 'week2': [1, 2, 3], 'week3': [3, 5, 6]},  # Piper Baker
            'SCA1043': {'week1': [0, 3, 4], 'week2': [1, 2, 3], 'week3': [3, 5, 6]},  # Ryan Nelson
            # Team C - SCA 2-shift (24hr): Sun Thu | Mon Tue | Fri Sat
            'SCA1044': {'week1': [0, 4], 'week2': [1, 2], 'week3': [5, 6]},  # Sophia Hall
            'SCA1045': {'week1': [0, 4], 'week2': [1, 2], 'week3': [5, 6]},  # Tyler Rivera
            'SCA1046': {'week1': [0, 4], 'week2': [1, 2], 'week3': [5, 6]},  # Ursula Campbell
            'SCA1047': {'week1': [0, 4], 'week2': [1, 2], 'week3': [5, 6]},  # Vincent Mitchell
            'SCA1048': {'week1': [0, 4], 'week2': [1, 2], 'week3': [5, 6]},  # Willow Carter
            'SCA1049': {'week1': [0, 4], 'week2': [1, 2], 'week3': [5, 6]},  # Wyatt Roberts
            'SCA1050': {'week1': [0, 4], 'week2': [1, 2], 'week3': [5, 6]},  # Xenia Phillips
            
            # Team A - SCW 3-shift (35hr): Mon Tue Wed | Wed Fri Sat | Sun Wed Thu
            'SCW1051': {'week1': [1, 2, 3], 'week2': [3, 5, 6], 'week3': [0, 3, 4]},  # Yvonne Evans
            'SCW1052': {'week1': [1, 2, 3], 'week2': [3, 5, 6], 'week3': [0, 3, 4]},  # Zachary Turner
            'SCW1053': {'week1': [1, 2, 3], 'week2': [3, 5, 6], 'week3': [0, 3, 4]},  # Abigail Cooper
            # Team A - SCW 2-shift (24hr): Mon Tue | Fri Sat | Sun Thu
            'SCW1054': {'week1': [1, 2], 'week2': [5, 6], 'week3': [0, 4]},  # Ben Morris
            'SCW1055': {'week1': [1, 2], 'week2': [5, 6], 'week3': [0, 4]},  # Chloe Rogers
            'SCW1056': {'week1': [1, 2], 'week2': [5, 6], 'week3': [0, 4]},  # Daniel Cox
            'SCW1057': {'week1': [1, 2], 'week2': [5, 6], 'week3': [0, 4]},  # Ella Ward
            'SCW1058': {'week1': [1, 2], 'week2': [5, 6], 'week3': [0, 4]},  # Finn Gray
            'SCW1059': {'week1': [1, 2], 'week2': [5, 6], 'week3': [0, 4]},  # Gemma Bell
            # Team A - SCA 3-shift (35hr): Mon Tue Wed | Wed Fri Sat | Sun Wed Thu
            'SCA1060': {'week1': [1, 2, 3], 'week2': [3, 5, 6], 'week3': [0, 3, 4]},  # Harry Coleman
            'SCA1061': {'week1': [1, 2, 3], 'week2': [3, 5, 6], 'week3': [0, 3, 4]},  # Isabel Foster
            'SCA1062': {'week1': [1, 2, 3], 'week2': [3, 5, 6], 'week3': [0, 3, 4]},  # Jacob Bailey
            'SCA1063': {'week1': [1, 2, 3], 'week2': [3, 5, 6], 'week3': [0, 3, 4]},  # Katie Reed
            'SCA1064': {'week1': [1, 2, 3], 'week2': [3, 5, 6], 'week3': [0, 3, 4]},  # Leo Kelly
            'SCA1065': {'week1': [1, 2, 3], 'week2': [3, 5, 6], 'week3': [0, 3, 4]},  # Megan Howard
            'SCA1066': {'week1': [1, 2, 3], 'week2': [3, 5, 6], 'week3': [0, 3, 4]},  # Nathan Peterson
            'SCA1067': {'week1': [1, 2, 3], 'week2': [3, 5, 6], 'week3': [0, 3, 4]},  # Poppy Cook
            'SCA1068': {'week1': [1, 2, 3], 'week2': [3, 5, 6], 'week3': [0, 3, 4]},  # Quentin Price
            'SCA1069': {'week1': [1, 2, 3], 'week2': [3, 5, 6], 'week3': [0, 3, 4]},  # Ruby Barnes
            'SCA1070': {'week1': [1, 2, 3], 'week2': [3, 5, 6], 'week3': [0, 3, 4]},  # Sebastian Ross
            'SCA1071': {'week1': [1, 2, 3], 'week2': [3, 5, 6], 'week3': [0, 3, 4]},  # Taylor Henderson
            # Team A - SCA 2-shift (24hr): Mon Tue | Fri Sat | Sun Thu
            'SCA1079': {'week1': [1, 2], 'week2': [5, 6], 'week3': [0, 4]},  # Janice Henderson
            'SCA1072': {'week1': [1, 2], 'week2': [5, 6], 'week3': [0, 4]},  # Victor Watson
            'SCA1073': {'week1': [1, 2], 'week2': [5, 6], 'week3': [0, 4]},  # Zoe Brooks
            'SCA1074': {'week1': [1, 2], 'week2': [5, 6], 'week3': [0, 4]},  # Adam Bryant
            'SCA1075': {'week1': [1, 2], 'week2': [5, 6], 'week3': [0, 4]},  # Beth Griffin
            'SCA1076': {'week1': [1, 2], 'week2': [5, 6], 'week3': [0, 4]},  # Natasha Jones
            'SCA1077': {'week1': [1, 2], 'week2': [5, 6], 'week3': [0, 4]},  # Abby Johnson
            'SCA1078': {'week1': [1, 2], 'week2': [5, 6], 'week3': [0, 4]},  # Kyle Oboe
        }
        
        # Get all day care staff
        day_care_staff = User.objects.filter(
            role__name__in=['SCW', 'SCA'],
            is_staff=False
        ).select_related('role', 'home_unit')
        
        shifts_created = 0
        scw_shifts = 0
        sca_shifts = 0
        
        with transaction.atomic():
            for user in day_care_staff:
                # Get this staff member's pattern
                pattern = staff_patterns.get(user.sap)
                if not pattern:
                    self.stdout.write(self.style.WARNING(f'⚠ No pattern found for {user.sap} - {user.full_name}'))
                    continue
                
                # Determine shift type based on role
                if user.role.name == 'SCW':
                    shift_type = day_senior
                else:  # SCA
                    shift_type = day_assistant
                
                # Generate shifts for each week
                for week_num in range(weeks):
                    week_start = start_date + timedelta(weeks=week_num)
                    
                    # Determine which pattern week to use (cycles through 3 weeks)
                    pattern_week = (week_num % 3) + 1
                    pattern_key = f'week{pattern_week}'
                    work_days = pattern[pattern_key]
                    
                    # Create shifts for this week's work days
                    for day_offset in work_days:
                        shift_date = week_start + timedelta(days=day_offset)
                        
                        Shift.objects.create(
                            user=user,
                            date=shift_date,
                            shift_type=shift_type,
                            unit=user.home_unit
                        )
                        shifts_created += 1
                        
                        if user.role.name == 'SCW':
                            scw_shifts += 1
                        else:
                            sca_shifts += 1
        
        # Summary
        scw_count = User.objects.filter(role__name='SCW', is_staff=False).count()
        sca_count = User.objects.filter(role__name='SCA', is_staff=False).count()
        
        end_date = start_date + timedelta(weeks=weeks) - timedelta(days=1)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Created {shifts_created} shifts for {scw_count} SCW + {sca_count} SCA staff over {weeks} weeks\n'
                f'   SCW shifts: {scw_shifts}\n'
                f'   SCA shifts: {sca_shifts}\n'
                f'   Date range: {start_date} to {end_date}'
            )
        )
