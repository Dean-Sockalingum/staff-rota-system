from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from scheduling.models import User, Shift, ShiftType
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Generate night care shifts based on individual staff patterns from spreadsheet'

    # Individual 3-week patterns for all 81 night care staff
    # Format: [[week1_days], [week2_days], [week3_days]] where 0=Sun, 1=Mon, ..., 6=Sat
    # Team 1: 26 staff (13×35hr + 13×24hr)
    # Team 2: 28 staff (13×35hr + 15×24hr) - Gemma SCA1107 works Fri/Sat with Team 2!
    # Team 3: 27 staff (14×35hr + 13×24hr)
    STAFF_PATTERNS = {
        # ===== TEAM 1 =====
        # Team 1 35hr (13 staff): Sun/Mon/Tue → Thu/Fri/Sat → Tue/Wed/Thu
        'SCW1080': [[0,1,2], [4,5,6], [2,3,4]],  # Jack Henderson
        'SCW1081': [[0,1,2], [4,5,6], [2,3,4]],  # Karen Watson
        'SCA1084': [[0,1,2], [4,5,6], [2,3,4]],  # Olivia Jones
        'SCA1085': [[0,1,2], [4,5,6], [2,3,4]],  # Peter Johnson
        'SCA1086': [[0,1,2], [4,5,6], [2,3,4]],  # Quinn Oboe
        'SCA1087': [[0,1,2], [4,5,6], [2,3,4]],  # Rachel Griffin
        'SCA1088': [[0,1,2], [4,5,6], [2,3,4]],  # Noah Coleman
        'SCA1090': [[0,1,2], [4,5,6], [2,3,4]],  # Sam Foster
        'SCA1091': [[0,1,2], [4,5,6], [2,3,4]],  # Tina Bailey
        'SCA1092': [[0,1,2], [4,5,6], [2,3,4]],  # Uma Reed
        'SCA1093': [[0,1,2], [4,5,6], [2,3,4]],  # Victor Kelly
        'SCA1094': [[0,1,2], [4,5,6], [2,3,4]],  # Nora Howard
        'SCA1095': [[0,1,2], [4,5,6], [2,3,4]],  # Nora Gotyo
        
        # Team 1 24hr (13 staff): Sun/Mon → Fri/Sat → Wed/Thu
        'SCW1082': [[0,1], [5,6], [3,4]],  # Liam Brooks
        'SCW1083': [[0,1], [5,6], [3,4]],  # Mia Bryant
        'SCA1096': [[0,1], [5,6], [3,4]],  # Wendy Barnes
        'SCA1097': [[0,1], [5,6], [3,4]],  # Xander Ross
        'SCA1098': [[0,1], [5,6], [3,4]],  # Yara Henderson
        'SCA1099': [[0,1], [5,6], [3,4]],  # Zoe Peterson
        'SCA1100': [[0,1], [5,6], [3,4]],  # Aaron Cook
        'SCA1101': [[0,1], [5,6], [3,4]],  # Bella Price
        'SCA1102': [[0,1], [5,6], [3,4]],  # Ben Nevis
        'SCA1103': [[0,1], [5,6], [3,4]],  # Chloe Earlie
        'SCA1104': [[0,1], [5,6], [3,4]],  # Daniel Cohen
        'SCA1105': [[0,1], [5,6], [3,4]],  # Ella Fitzgerald
        'SCA1106': [[0,1], [5,6], [3,4]],  # Finn Barr
        
        # ===== TEAM 2 =====
        # Team 2 35hr (13 staff): Thu/Fri/Sat → Tue/Wed/Thu → Sun/Mon/Tue
        'SCW1110': [[4,5,6], [2,3,4], [0,1,2]],  # JoJo McArthur
        'SCW1111': [[4,5,6], [2,3,4], [0,1,2]],  # Pedro Wallace
        'SCA1114': [[4,5,6], [2,3,4], [0,1,2]],  # Ethan Hawke
        'SCA1115': [[4,5,6], [2,3,4], [0,1,2]],  # Fiona Bruce
        'SCA1116': [[4,5,6], [2,3,4], [0,1,2]],  # George Harrison
        'SCA1117': [[4,5,6], [2,3,4], [0,1,2]],  # Hannah Barbera
        'SCA1118': [[4,5,6], [2,3,4], [0,1,2]],  # Mark Lewis
        'SCA1119': [[4,5,6], [2,3,4], [0,1,2]],  # Isaac Robinson
        'SCA1120': [[4,5,6], [2,3,4], [0,1,2]],  # Julia Walker
        'SCA1121': [[4,5,6], [2,3,4], [0,1,2]],  # Kyle Young
        'SCA1122': [[4,5,6], [2,3,4], [0,1,2]],  # Luna Allen
        'SCA1123': [[4,5,6], [2,3,4], [0,1,2]],  # Oscar Wright
        'SCA1124': [[4,5,6], [2,3,4], [0,1,2]],  # Piper Scott
        
        # Team 2 24hr (14 staff): Fri/Sat → Wed/Thu → Sun/Mon
        'SCW1108': [[5,6], [3,4], [0,1]],  # Blessing Oghoa
        'SCW1109': [[5,6], [3,4], [0,1]],  # Peace Sibbald
        'SCA1107': [[5,6], [3,4], [0,1]],  # Gemma Arthur (Team 3 in import, Team 2 pattern!)
        'SCA1112': [[5,6], [3,4], [0,1]],  # Caleb King
        'SCA1113': [[5,6], [3,4], [0,1]],  # Diana Doors
        'SCA1125': [[5,6], [3,4], [0,1]],  # Ryan Torres
        'SCA1126': [[5,6], [3,4], [0,1]],  # Nathan Nguyen
        'SCA1127': [[5,6], [3,4], [0,1]],  # Sophia Hill
        'SCA1128': [[5,6], [3,4], [0,1]],  # Tyler Green
        'SCA1129': [[5,6], [3,4], [0,1]],  # Ursula Adams
        'SCA1130': [[5,6], [3,4], [0,1]],  # Vincent Baker
        'SCA1131': [[5,6], [3,4], [0,1]],  # Willow Nelson
        'SCA1132': [[5,6], [3,4], [0,1]],  # Wyatt Earp
        'SCA1133': [[5,6], [3,4], [0,1]],  # Xenia Warrior
        'SCA1134': [[5,6], [3,4], [0,1]],  # Jacqui Swan
        
        # ===== TEAM 3 =====
        # Team 3 35hr (14 staff): Tue/Wed/Thu → Sun/Mon/Tue → Thu/Fri/Sat
        'SCW1135': [[2,3,4], [0,1,2], [4,5,6]],  # Harry Hall
        'SCW1136': [[2,3,4], [0,1,2], [4,5,6]],  # Isabel Rivera
        'SCA1141': [[2,3,4], [0,1,2], [4,5,6]],  # Poppy Saeed
        'SCA1142': [[2,3,4], [0,1,2], [4,5,6]],  # Quentin Tarant
        'SCA1143': [[2,3,4], [0,1,2], [4,5,6]],  # Ruby Rubia
        'SCA1144': [[2,3,4], [0,1,2], [4,5,6]],  # Sebastian Coen
        'SCA1145': [[2,3,4], [0,1,2], [4,5,6]],  # Taylor Swifty
        'SCA1146': [[2,3,4], [0,1,2], [4,5,6]],  # Janice Evans
        'SCA1147': [[2,3,4], [0,1,2], [4,5,6]],  # Victor Turner
        'SCA1148': [[2,3,4], [0,1,2], [4,5,6]],  # Zoe Cooper
        'SCA1149': [[2,3,4], [0,1,2], [4,5,6]],  # Adam Phillips
        'SCA1150': [[2,3,4], [0,1,2], [4,5,6]],  # Beth Aimes
        'SCA1151': [[2,3,4], [0,1,2], [4,5,6]],  # Natasha Kaplinski
        'SCA1152': [[2,3,4], [0,1,2], [4,5,6]],  # Abby Rhodes
        
        # Team 3 24hr (14 staff): Tue/Wed → Sun/Mon → Fri/Sat
        'SCW1137': [[2,3], [0,1], [5,6]],  # Jacob Campbell
        'SCW1138': [[2,3], [0,1], [5,6]],  # Katie Mitchell
        'SCW1139': [[2,3], [0,1], [5,6]],  # Leo Carter
        'SCW1140': [[2,3], [0,1], [5,6]],  # Megan Roberts
        'SCA1153': [[2,3], [0,1], [5,6]],  # David Morris
        'SCA1154': [[2,3], [0,1], [5,6]],  # Emily Rogers
        'SCA1155': [[2,3], [0,1], [5,6]],  # Frank Cox
        'SCA1156': [[2,3], [0,1], [5,6]],  # Grace Ward
        'SCA1157': [[2,3], [0,1], [5,6]],  # Henry Gray
        'SCA1158': [[2,3], [0,1], [5,6]],  # Ivy Bell
        'SCA1159': [[2,3], [0,1], [5,6]],  # Angela Ripton
        'SCA1160': [[2,3], [0,1], [5,6]],  # Kyle Son Ji
        'SCA1161': [[2,3], [0,1], [5,6]],  # Precious Richards
    }

    def add_arguments(self, parser):
        parser.add_argument(
            '--start-date',
            type=str,
            default='2025-11-23',
            help='Start date for shift generation (YYYY-MM-DD)'
        )
        parser.add_argument(
            '--weeks',
            type=int,
            default=12,
            help='Number of weeks to generate shifts for'
        )

    def handle(self, *args, **options):
        start_date = datetime.strptime(options['start_date'], '%Y-%m-%d').date()
        weeks = options['weeks']
        
        self.stdout.write(f"Generating night care shifts from {start_date} for {weeks} weeks...")

        try:
            # Get shift types
            night_senior = ShiftType.objects.get(name='NIGHT_SENIOR')
            night_assistant = ShiftType.objects.get(name='NIGHT_ASSISTANT')
            
            # Get all night care staff (SCWN and SCAN)
            night_staff = User.objects.filter(
                role__name__in=['SCWN', 'SCAN']
            ).exclude(is_staff=True).select_related('role')

            stats = {
                'total_shifts': 0,
                'staff_processed': 0,
                'scwn_shifts': 0,
                'scan_shifts': 0,
            }

            with transaction.atomic():
                # Delete existing night shifts in the date range
                end_date = start_date + timedelta(weeks=weeks)
                Shift.objects.filter(
                    shift_type__in=[night_senior, night_assistant],
                    date__gte=start_date,
                    date__lt=end_date
                ).delete()

                # Process each staff member
                for staff in night_staff:
                    sap_number = staff.sap
                    
                    if sap_number not in self.STAFF_PATTERNS:
                        self.stdout.write(
                            self.style.WARNING(f"No pattern found for {sap_number} ({staff.get_full_name()})")
                        )
                        continue

                    pattern = self.STAFF_PATTERNS[sap_number]
                    
                    # Determine shift type based on role
                    shift_type = night_senior if staff.role.name == 'SCWN' else night_assistant
                    
                    # Generate shifts for each week
                    current_date = start_date
                    week_number = 0
                    
                    while current_date < end_date:
                        # Get pattern for current week (cycle through 3-week pattern)
                        week_pattern = pattern[week_number % 3]
                        
                        # Generate shifts for this week
                        for day_offset in range(7):
                            shift_date = current_date + timedelta(days=day_offset)
                            
                            if shift_date >= end_date:
                                break
                            
                            weekday = shift_date.weekday()
                            # Convert Monday=0 to Sunday=0 format
                            weekday_sunday_zero = (weekday + 1) % 7
                            
                            if weekday_sunday_zero in week_pattern:
                                Shift.objects.create(
                                    user=staff,
                                    shift_type=shift_type,
                                    date=shift_date,
                                    unit=staff.unit
                                )
                                stats['total_shifts'] += 1
                                
                                if shift_type == night_senior:
                                    stats['scwn_shifts'] += 1
                                else:
                                    stats['scan_shifts'] += 1
                        
                        current_date += timedelta(weeks=1)
                        week_number += 1
                    
                    stats['staff_processed'] += 1

            self.stdout.write(self.style.SUCCESS(f"\n✓ Night shift generation complete!"))
            self.stdout.write(f"  Staff processed: {stats['staff_processed']}")
            self.stdout.write(f"  Total shifts: {stats['total_shifts']}")
            self.stdout.write(f"  SCWN shifts: {stats['scwn_shifts']}")
            self.stdout.write(f"  SCAN shifts: {stats['scan_shifts']}")

        except ShiftType.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f"Shift type not found: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
            raise
