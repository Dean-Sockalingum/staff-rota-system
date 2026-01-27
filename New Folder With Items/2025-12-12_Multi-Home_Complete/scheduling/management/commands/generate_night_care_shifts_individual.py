from django.core.management.base import BaseCommand
from scheduling.models import User, Shift, ShiftType, Unit
from datetime import date, timedelta
from django.db import transaction


class Command(BaseCommand):
    help = 'Generate night care shifts (SCWN and SCAN) with individual 3-week rotation patterns for each staff member'

    def add_arguments(self, parser):
        parser.add_argument('--weeks', type=int, default=12, help='Number of weeks to generate')
        parser.add_argument('--start-date', type=str, default='2025-12-01', help='Start date (YYYY-MM-DD)')
        parser.add_argument('--clear', action='store_true', help='Clear existing SCWN/SCAN shifts before generating')

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
        night_senior = ShiftType.objects.get(name='NIGHT_SENIOR')
        night_assistant = ShiftType.objects.get(name='NIGHT_ASSISTANT')
        
        # Clear existing shifts if requested
        if clear_existing:
            deleted_count = Shift.objects.filter(
                user__role__name__in=['SCWN', 'SCAN'],
                user__is_staff=False
            ).count()
            Shift.objects.filter(
                user__role__name__in=['SCWN', 'SCAN'],
                user__is_staff=False
            ).delete()
            self.stdout.write(f'✓ Cleared {deleted_count} existing SCWN/SCAN shifts')
        
        # Individual 3-week rotation patterns for each staff member
        # Day indices: 0=Sun, 1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat
        # Format: 'SAP': {'week1': [days], 'week2': [days], 'week3': [days]}
        
        # NIGHT PATTERNS (different from day shift):
        # Team 1 35hr: Sun Mon Tue | Thu Fri Sat | Tue Wed Thu
        # Team 1 24hr: Sun Mon | Fri Sat | Wed Thu
        # Team 2 35hr: Thu Fri Sat | Tue Wed Thu | Sun Mon Tue
        # Team 2 24hr: Fri Sat | Wed Thu | Sun Mon
        # Team 3 35hr: Tue Wed Thu | Sun Mon Tue | Thu Fri Sat
        # Team 3 24hr: Wed Thu | Sun Mon | Fri Sat
        
        staff_patterns = {
            # Team 1 - SCWN 35hr
            'SCW1080': {'week1': [0, 1, 2], 'week2': [4, 5, 6], 'week3': [2, 3, 4]},
            'SCW1081': {'week1': [0, 1, 2], 'week2': [4, 5, 6], 'week3': [2, 3, 4]},
            # Team 1 - SCWN 24hr
            'SCW1082': {'week1': [0, 1], 'week2': [5, 6], 'week3': [3, 4]},
            'SCW1083': {'week1': [0, 1], 'week2': [5, 6], 'week3': [3, 4]},
            # Team 1 - SCAN 35hr
            'SCA1084': {'week1': [0, 1, 2], 'week2': [4, 5, 6], 'week3': [2, 3, 4]},
            'SCA1085': {'week1': [0, 1, 2], 'week2': [4, 5, 6], 'week3': [2, 3, 4]},
            'SCA1086': {'week1': [0, 1, 2], 'week2': [4, 5, 6], 'week3': [2, 3, 4]},
            'SCA1087': {'week1': [0, 1, 2], 'week2': [4, 5, 6], 'week3': [2, 3, 4]},
            'SCA1088': {'week1': [0, 1, 2], 'week2': [4, 5, 6], 'week3': [2, 3, 4]},
            'SCA1090': {'week1': [0, 1, 2], 'week2': [4, 5, 6], 'week3': [2, 3, 4]},
            'SCA1091': {'week1': [0, 1, 2], 'week2': [4, 5, 6], 'week3': [2, 3, 4]},
            'SCA1092': {'week1': [0, 1, 2], 'week2': [4, 5, 6], 'week3': [2, 3, 4]},
            'SCA1093': {'week1': [0, 1, 2], 'week2': [4, 5, 6], 'week3': [2, 3, 4]},
            'SCA1094': {'week1': [0, 1, 2], 'week2': [4, 5, 6], 'week3': [2, 3, 4]},
            'SCA1095': {'week1': [0, 1, 2], 'week2': [4, 5, 6], 'week3': [2, 3, 4]},
            # Team 1 - SCAN 24hr
            'SCA1096': {'week1': [0, 1], 'week2': [5, 6], 'week3': [3, 4]},
            'SCA1097': {'week1': [0, 1], 'week2': [5, 6], 'week3': [3, 4]},
            'SCA1098': {'week1': [0, 1], 'week2': [5, 6], 'week3': [3, 4]},
            'SCA1099': {'week1': [0, 1], 'week2': [5, 6], 'week3': [3, 4]},
            'SCA1100': {'week1': [0, 1], 'week2': [5, 6], 'week3': [3, 4]},
            'SCA1101': {'week1': [0, 1], 'week2': [5, 6], 'week3': [3, 4]},
            'SCA1102': {'week1': [0, 1], 'week2': [5, 6], 'week3': [3, 4]},
            'SCA1103': {'week1': [0, 1], 'week2': [5, 6], 'week3': [3, 4]},
            'SCA1104': {'week1': [0, 1], 'week2': [5, 6], 'week3': [3, 4]},
            'SCA1105': {'week1': [0, 1], 'week2': [5, 6], 'week3': [3, 4]},
            'SCA1106': {'week1': [0, 1], 'week2': [5, 6], 'week3': [3, 4]},
            'SCA1107': {'week1': [0, 1], 'week2': [5, 6], 'week3': [3, 4]},
            
            # Team 2 - SCWN 35hr
            'SCW1108': {'week1': [4, 5, 6], 'week2': [2, 3, 4], 'week3': [0, 1, 2]},
            'SCW1109': {'week1': [4, 5, 6], 'week2': [2, 3, 4], 'week3': [0, 1, 2]},
            # Team 2 - SCWN 24hr
            'SCW1110': {'week1': [5, 6], 'week2': [3, 4], 'week3': [0, 1]},
            'SCW1111': {'week1': [5, 6], 'week2': [3, 4], 'week3': [0, 1]},
            # Team 2 - SCAN 35hr
            'SCA1112': {'week1': [4, 5, 6], 'week2': [2, 3, 4], 'week3': [0, 1, 2]},
            'SCA1113': {'week1': [4, 5, 6], 'week2': [2, 3, 4], 'week3': [0, 1, 2]},
            'SCA1114': {'week1': [4, 5, 6], 'week2': [2, 3, 4], 'week3': [0, 1, 2]},
            'SCA1115': {'week1': [4, 5, 6], 'week2': [2, 3, 4], 'week3': [0, 1, 2]},
            'SCA1116': {'week1': [4, 5, 6], 'week2': [2, 3, 4], 'week3': [0, 1, 2]},
            'SCA1117': {'week1': [4, 5, 6], 'week2': [2, 3, 4], 'week3': [0, 1, 2]},
            'SCA1118': {'week1': [4, 5, 6], 'week2': [2, 3, 4], 'week3': [0, 1, 2]},
            'SCA1119': {'week1': [4, 5, 6], 'week2': [2, 3, 4], 'week3': [0, 1, 2]},
            'SCA1120': {'week1': [4, 5, 6], 'week2': [2, 3, 4], 'week3': [0, 1, 2]},
            'SCA1121': {'week1': [4, 5, 6], 'week2': [2, 3, 4], 'week3': [0, 1, 2]},
            'SCA1122': {'week1': [4, 5, 6], 'week2': [2, 3, 4], 'week3': [0, 1, 2]},
            # Team 2 - SCAN 24hr
            'SCA1123': {'week1': [5, 6], 'week2': [3, 4], 'week3': [0, 1]},
            'SCA1124': {'week1': [5, 6], 'week2': [3, 4], 'week3': [0, 1]},
            'SCA1125': {'week1': [5, 6], 'week2': [3, 4], 'week3': [0, 1]},
            'SCA1126': {'week1': [5, 6], 'week2': [3, 4], 'week3': [0, 1]},
            'SCA1127': {'week1': [5, 6], 'week2': [3, 4], 'week3': [0, 1]},
            'SCA1128': {'week1': [5, 6], 'week2': [3, 4], 'week3': [0, 1]},
            'SCA1129': {'week1': [5, 6], 'week2': [3, 4], 'week3': [0, 1]},
            'SCA1130': {'week1': [5, 6], 'week2': [3, 4], 'week3': [0, 1]},
            'SCA1131': {'week1': [5, 6], 'week2': [3, 4], 'week3': [0, 1]},
            'SCA1132': {'week1': [5, 6], 'week2': [3, 4], 'week3': [0, 1]},
            'SCA1133': {'week1': [5, 6], 'week2': [3, 4], 'week3': [0, 1]},
            'SCA1134': {'week1': [5, 6], 'week2': [3, 4], 'week3': [0, 1]},
            
            # Team 3 - SCWN 35hr
            'SCW1135': {'week1': [2, 3, 4], 'week2': [0, 1, 2], 'week3': [4, 5, 6]},
            'SCW1136': {'week1': [2, 3, 4], 'week2': [0, 1, 2], 'week3': [4, 5, 6]},
            # Team 3 - SCWN 24hr
            'SCW1137': {'week1': [3, 4], 'week2': [0, 1], 'week3': [5, 6]},
            'SCW1138': {'week1': [3, 4], 'week2': [0, 1], 'week3': [5, 6]},
            'SCW1139': {'week1': [3, 4], 'week2': [0, 1], 'week3': [5, 6]},
            'SCW1140': {'week1': [3, 4], 'week2': [0, 1], 'week3': [5, 6]},
            # Team 3 - SCAN 35hr
            'SCA1141': {'week1': [2, 3, 4], 'week2': [0, 1, 2], 'week3': [4, 5, 6]},
            'SCA1142': {'week1': [2, 3, 4], 'week2': [0, 1, 2], 'week3': [4, 5, 6]},
            'SCA1143': {'week1': [2, 3, 4], 'week2': [0, 1, 2], 'week3': [4, 5, 6]},
            'SCA1144': {'week1': [2, 3, 4], 'week2': [0, 1, 2], 'week3': [4, 5, 6]},
            'SCA1145': {'week1': [2, 3, 4], 'week2': [0, 1, 2], 'week3': [4, 5, 6]},
            'SCA1146': {'week1': [2, 3, 4], 'week2': [0, 1, 2], 'week3': [4, 5, 6]},
            'SCA1147': {'week1': [2, 3, 4], 'week2': [0, 1, 2], 'week3': [4, 5, 6]},
            'SCA1148': {'week1': [2, 3, 4], 'week2': [0, 1, 2], 'week3': [4, 5, 6]},
            'SCA1149': {'week1': [2, 3, 4], 'week2': [0, 1, 2], 'week3': [4, 5, 6]},
            'SCA1150': {'week1': [2, 3, 4], 'week2': [0, 1, 2], 'week3': [4, 5, 6]},
            'SCA1151': {'week1': [2, 3, 4], 'week2': [0, 1, 2], 'week3': [4, 5, 6]},
            'SCA1152': {'week1': [2, 3, 4], 'week2': [0, 1, 2], 'week3': [4, 5, 6]},
            # Team 3 - SCAN 24hr
            'SCA1153': {'week1': [3, 4], 'week2': [0, 1], 'week3': [5, 6]},
            'SCA1154': {'week1': [3, 4], 'week2': [0, 1], 'week3': [5, 6]},
            'SCA1155': {'week1': [3, 4], 'week2': [0, 1], 'week3': [5, 6]},
            'SCA1156': {'week1': [3, 4], 'week2': [0, 1], 'week3': [5, 6]},
            'SCA1157': {'week1': [3, 4], 'week2': [0, 1], 'week3': [5, 6]},
            'SCA1158': {'week1': [3, 4], 'week2': [0, 1], 'week3': [5, 6]},
            'SCA1159': {'week1': [3, 4], 'week2': [0, 1], 'week3': [5, 6]},
            'SCA1160': {'week1': [3, 4], 'week2': [0, 1], 'week3': [5, 6]},
            'SCA1161': {'week1': [3, 4], 'week2': [0, 1], 'week3': [5, 6]},
        }
        
        # Get all night care staff users
        scwn_users = {
            u.sap: u for u in User.objects.filter(role__name='SCWN', is_staff=False)
        }
        scan_users = {
            u.sap: u for u in User.objects.filter(role__name='SCAN', is_staff=False)
        }
        all_users = {**scwn_users, **scan_users}
        
        total_shifts = 0
        scwn_shift_count = 0
        scan_shift_count = 0
        
        with transaction.atomic():
            # Process each staff member
            for sap, pattern in staff_patterns.items():
                if sap not in all_users:
                    self.stdout.write(self.style.WARNING(f'Warning: {sap} not found in database'))
                    continue
                
                user = all_users[sap]
                is_scwn = user.role.name == 'SCWN'
                shift_type = night_senior if is_scwn else night_assistant
                
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
                        if is_scwn:
                            scwn_shift_count += 1
                        else:
                            scan_shift_count += 1
        
        # Calculate end date
        end_date = start_date + timedelta(days=(weeks * 7) - 1)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Created {total_shifts} shifts for {len(scwn_users)} SCWN + {len(scan_users)} SCAN staff over {weeks} weeks\n'
                f'   SCWN shifts: {scwn_shift_count}\n'
                f'   SCAN shifts: {scan_shift_count}\n'
                f'   Date range: {start_date} to {end_date}'
            )
        )
