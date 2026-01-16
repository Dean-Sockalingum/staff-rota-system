from django.core.management.base import BaseCommand
from scheduling.models import User, Shift, ShiftType, Unit
from datetime import date, timedelta
from django.db import transaction


class Command(BaseCommand):
    help = 'Generate shifts for day care staff (SCW and SCA) using individual 3-week patterns from spreadsheet'

    def add_arguments(self, parser):
        parser.add_argument(
            '--weeks',
            type=int,
            default=12,
            help='Number of weeks to generate shifts for'
        )
        parser.add_argument(
            '--start-date',
            type=str,
            default='2025-11-23',
            help='Start date in YYYY-MM-DD format (must be a Sunday)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing SCW/SCA shifts before generating new ones'
        )

    def handle(self, *args, **options):
        weeks = options['weeks']
        start_date_str = options['start_date']
        clear = options['clear']
        
        # Parse start date and ensure it's a Sunday
        start_date = date.fromisoformat(start_date_str)
        if start_date.weekday() != 6:  # 6 = Sunday
            self.stdout.write(self.style.ERROR(f'Start date must be a Sunday! {start_date} is a {start_date.strftime("%A")}'))
            return
        
        self.stdout.write(f'Starting from: {start_date} ({start_date.strftime("%A")})')
        
        # Get shift types
        day_senior = ShiftType.objects.get(name='DAY_SENIOR')
        day_assistant = ShiftType.objects.get(name='DAY_ASSISTANT')
        
        # Clear existing shifts if requested
        if clear:
            deleted_count = Shift.objects.filter(
                user__role__name__in=['SCW', 'SCA'],
                user__is_staff=False
            ).delete()[0]
            self.stdout.write(f'✓ Cleared {deleted_count} existing SCW/SCA shifts')
        
        # Individual staff patterns from spreadsheet
        # Format: SAP -> [week1_days, week2_days, week3_days]
        # Days: 0=Sun, 1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat
        STAFF_PATTERNS = {
            # TEAM A (1) - 35hr staff: Mon/Tue/Wed → Wed/Fri/Sat → Sun/Wed/Thu
            'SCW1051': [[1,2,3], [3,5,6], [0,3,4]],
            'SCW1052': [[1,2,3], [3,5,6], [0,3,4]],
            'SCW1053': [[1,2,3], [3,5,6], [0,3,4]],
            'SCA1060': [[1,2,3], [3,5,6], [0,3,4]],
            'SCA1061': [[1,2,3], [3,5,6], [0,3,4]],
            'SCA1062': [[1,2,3], [3,5,6], [0,3,4]],
            'SCA1063': [[1,2,3], [3,5,6], [0,3,4]],
            'SCA1064': [[1,2,3], [3,5,6], [0,3,4]],
            'SCA1065': [[1,2,3], [3,5,6], [0,3,4]],
            'SCA1066': [[1,2,3], [3,5,6], [0,3,4]],
            'SCA1067': [[1,2,3], [3,5,6], [0,3,4]],
            'SCA1068': [[1,2,3], [3,5,6], [0,3,4]],
            'SCA1069': [[1,2,3], [3,5,6], [0,3,4]],
            
            # TEAM A (1) - 24hr staff: Mon/Tue → Fri/Sat → Sun/Thu
            'SCW1054': [[1,2], [5,6], [0,4]],
            'SCW1055': [[1,2], [5,6], [0,4]],
            'SCW1056': [[1,2], [5,6], [0,4]],
            'SCW1057': [[1,2], [5,6], [0,4]],
            'SCW1058': [[1,2], [5,6], [0,4]],
            'SCW1059': [[1,2], [5,6], [0,4]],
            'SCA1079': [[1,2], [5,6], [0,4]],
            'SCA1072': [[1,2], [5,6], [0,4]],
            'SCA1073': [[1,2], [5,6], [0,4]],
            'SCA1074': [[1,2], [5,6], [0,4]],
            'SCA1075': [[1,2], [5,6], [0,4]],
            'SCA1076': [[1,2], [5,6], [0,4]],
            'SCA1077': [[1,2], [5,6], [0,4]],
            'SCA1078': [[1,2], [5,6], [0,4]],
            
            # TEAM B (2) - 35hr staff: Wed/Fri/Sat → Sun/Wed/Thu → Mon/Tue/Wed
            'SCW1001': [[3,5,6], [0,3,4], [1,2,3]],
            'SCW1002': [[3,5,6], [0,3,4], [1,2,3]],
            'SCW1003': [[3,5,6], [0,3,4], [1,2,3]],
            'SCA1010': [[3,5,6], [0,3,4], [1,2,3]],
            'SCA1011': [[3,5,6], [0,3,4], [1,2,3]],
            'SCA1012': [[3,5,6], [0,3,4], [1,2,3]],
            'SCA1013': [[3,5,6], [0,3,4], [1,2,3]],
            'SCA1014': [[3,5,6], [0,3,4], [1,2,3]],
            'SCA1015': [[3,5,6], [0,3,4], [1,2,3]],
            'SCA1016': [[3,5,6], [0,3,4], [1,2,3]],
            'SCA1017': [[3,5,6], [0,3,4], [1,2,3]],
            'SCA1018': [[3,5,6], [0,3,4], [1,2,3]],
            'SCA1071': [[3,5,6], [0,3,4], [1,2,3]],
            
            # TEAM B (2) - 24hr staff: Fri/Sat → Sun/Thu → Mon/Tue
            'SCW1004': [[5,6], [0,4], [1,2]],
            'SCW1005': [[5,6], [0,4], [1,2]],
            'SCW1006': [[5,6], [0,4], [1,2]],
            'SCW1007': [[5,6], [0,4], [1,2]],
            'SCW1008': [[5,6], [0,4], [1,2]],
            'SCW1009': [[5,6], [0,4], [1,2]],
            'SCA1019': [[5,6], [0,4], [1,2]],
            'SCA1020': [[5,6], [0,4], [1,2]],
            'SCA1021': [[5,6], [0,4], [1,2]],
            'SCA1022': [[5,6], [0,4], [1,2]],
            'SCA1023': [[5,6], [0,4], [1,2]],
            'SCA1024': [[5,6], [0,4], [1,2]],
            'SCA1025': [[5,6], [0,4], [1,2]],
            'SCA1071': [[3,5,6], [0,3,4], [1,2,3]],  # 35hr
            
            # TEAM C (3) - 35hr staff: Sun/Wed/Thu → Mon/Tue/Wed → Wed/Fri/Sat
            'SCW1026': [[0,3,4], [1,2,3], [3,5,6]],
            'SCW1027': [[0,3,4], [1,2,3], [3,5,6]],
            'SCW1028': [[0,3,4], [1,2,3], [3,5,6]],
            'SCA1035': [[0,3,4], [1,2,3], [3,5,6]],
            'SCA1036': [[0,3,4], [1,2,3], [3,5,6]],
            'SCA1037': [[0,3,4], [1,2,3], [3,5,6]],
            'SCA1038': [[0,3,4], [1,2,3], [3,5,6]],
            'SCA1039': [[0,3,4], [1,2,3], [3,5,6]],
            'SCA1040': [[0,3,4], [1,2,3], [3,5,6]],
            'SCA1041': [[0,3,4], [1,2,3], [3,5,6]],
            'SCA1042': [[0,3,4], [1,2,3], [3,5,6]],
            'SCA1043': [[0,3,4], [1,2,3], [3,5,6]],
            'SCA1070': [[0,3,4], [1,2,3], [3,5,6]],
            
            # TEAM C (3) - 24hr staff: Sun/Thu → Mon/Tue → Fri/Sat
            'SCW1029': [[0,4], [1,2], [5,6]],
            'SCW1030': [[0,4], [1,2], [5,6]],
            'SCW1031': [[0,4], [1,2], [5,6]],
            'SCW1032': [[0,4], [1,2], [5,6]],
            'SCW1033': [[0,4], [1,2], [5,6]],
            'SCW1034': [[0,4], [1,2], [5,6]],
            'SCA1044': [[0,4], [1,2], [5,6]],
            'SCA1045': [[0,4], [1,2], [5,6]],
            'SCA1046': [[0,4], [1,2], [5,6]],
            'SCA1047': [[0,4], [1,2], [5,6]],
            'SCA1048': [[0,4], [1,2], [5,6]],
            'SCA1049': [[0,4], [1,2], [5,6]],
            'SCA1050': [[0,4], [1,2], [5,6]],
        }
        
        # Get all day care staff
        day_care_staff = User.objects.filter(
            role__name__in=['SCW', 'SCA'],
            is_staff=False,
            is_active=True
        ).select_related('role', 'home_unit')
        
        shifts_created = 0
        staff_with_shifts = set()
        
        with transaction.atomic():
            for staff in day_care_staff:
                # Get pattern for this staff member
                if staff.sap not in STAFF_PATTERNS:
                    self.stdout.write(self.style.WARNING(f'⚠ No pattern defined for {staff.sap} ({staff.full_name})'))
                    continue
                
                pattern = STAFF_PATTERNS[staff.sap]
                
                # Determine shift type based on role
                shift_type = day_senior if staff.role.name == 'SCW' else day_assistant
                
                # Generate shifts for the specified number of weeks
                for week_num in range(weeks):
                    # Determine which week of the 3-week pattern we're in
                    pattern_week = week_num % 3
                    week_days = pattern[pattern_week]
                    
                    # Get the Sunday of this week
                    week_start = start_date + timedelta(weeks=week_num)
                    
                    # Create shifts for each day in the pattern
                    for day_offset in week_days:
                        shift_date = week_start + timedelta(days=day_offset)
                        
                        Shift.objects.create(
                            user=staff,
                            date=shift_date,
                            shift_type=shift_type,
                            unit=staff.home_unit,
                            status='SCHEDULED'
                        )
                        shifts_created += 1
                    
                staff_with_shifts.add(staff.sap)
        
        # Report
        end_date = start_date + timedelta(weeks=weeks) - timedelta(days=1)
        self.stdout.write(self.style.SUCCESS(f'\n✅ Created {shifts_created} shifts for {len(staff_with_shifts)} staff over {weeks} weeks'))
        self.stdout.write(f'Date range: {start_date} to {end_date}')
        
        # Summary by role
        scw_count = len([s for s in staff_with_shifts if s.startswith('SCW')])
        sca_count = len([s for s in staff_with_shifts if s.startswith('SCA')])
        self.stdout.write(f'Staff: {scw_count} SCW + {sca_count} SCA')
        
        # Check for staff without patterns
        all_staff_saps = set(day_care_staff.values_list('sap', flat=True))
        missing_patterns = all_staff_saps - staff_with_shifts
        if missing_patterns:
            self.stdout.write(self.style.WARNING(f'\n⚠ {len(missing_patterns)} staff without patterns:'))
            for sap in sorted(missing_patterns):
                staff_obj = day_care_staff.get(sap=sap)
                self.stdout.write(f'   - {sap}: {staff_obj.full_name} (Team {staff_obj.team})')
