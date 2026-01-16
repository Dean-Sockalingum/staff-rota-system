"""
Create Victoria Gardens SCA DAY_ASSISTANT shifts using 3-week rotating patterns.

Based on image: 31 SCA staff
- Multiple 35-hour patterns (3 days/week)
- Multiple 24-hour patterns (2 days/week)
- Some marked as "vacancy"
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from scheduling.models import Shift, User, CareHome, ShiftType, Unit
from datetime import datetime, timedelta
import calendar

class Command(BaseCommand):
    help = 'Create Victoria Gardens SCA shifts using 3-week rotating pattern'

    def add_arguments(self, parser):
        parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)')
        parser.add_argument('--weeks', type=int, default=7, help='Number of weeks to create')
        parser.add_argument('--dry-run', action='store_true', help='Preview without saving')

    def handle(self, *args, **options):
        start_date_str = options.get('start_date')
        weeks = options['weeks']
        dry_run = options['dry_run']

        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        else:
            start_date = datetime(2025, 12, 15).date()

        # Get Victoria Gardens
        vg = CareHome.objects.get(name='VICTORIA_GARDENS')
        units = list(Unit.objects.filter(care_home=vg).order_by('name'))
        
        # Get all SCA staff - will assign patterns based on image
        # 35-hour patterns (3 days/week)
        patterns_35hr = {
            # Sun/Wed/Thu → Mon/Tue/Wed → Wed/Fri/Sat
            'SSCWN1717': [[6,2,3], [0,1,2], [2,4,5]],  # Lily Mitchell
            'SSCWN1718': [[6,2,3], [0,1,2], [2,4,5]],  # Malcolm Hunter
            
            # Mon/Tue/Wed → Thu/Fri/Sat → Sun/Wed/Thu
            'SSCWN1719': [[0,1,2], [3,4,5], [6,2,3]],  # Ruby Bell
            'SSCWN1720': [[0,1,2], [3,4,5], [6,2,3]],  # Derek Watson
            
            # Wed/Fri/Sat → Sun/Wed/Thu → Mon/Tue/Wed
            'SSCWN1721': [[2,4,5], [6,2,3], [0,1,2]],  # Amber Gordon
            
            # Mon/Tue/Wed → Thu/Fri/Sat → Sun/Wed/Thu
            'SSCWN1723': [[0,1,2], [3,4,5], [6,2,3]],  # Crystal Cameron
            
            # Wed/Fri/Sat → Sun/Wed/Thu → Mon/Tue/Wed
            'SSCWN1724': [[2,4,5], [6,2,3], [0,1,2]],  # Trevor Shaw
            
            # Sun/Wed/Thu → Mon/Tue/Wed → Wed/Fri/Sat
            'SSCWN1725': [[6,2,3], [0,1,2], [2,4,5]],  # Jade Hughes
            
            # Mon/Tue/Wed → Thu/Fri/Sat → Sun/Wed/Thu
            'SSCWN1726': [[0,1,2], [3,4,5], [6,2,3]],  # Ian Ellis
            
            # Sun/Wed/Thu → Mon/Tue/Wed → Wed/Fri/Sat
            'SSCWN1728': [[6,2,3], [0,1,2], [2,4,5]],  # Adrian Chapman
            
            # Wed/Fri/Sat → Sun/Wed/Thu → Mon/Tue/Wed
            'SSCWN1729': [[2,4,5], [6,2,3], [0,1,2]],  # Opal Coleman
            
            # Sun/Wed/Thu → Mon/Tue/Wed → Wed/Fri/Sat
            'SSCWN1730': [[6,2,3], [0,1,2], [2,4,5]],  # Stuart Foster
            
            # Wed/Fri/Sat → Sun/Wed/Thu → Mon/Tue/Wed
            'SSCWN1731': [[2,4,5], [6,2,3], [0,1,2]],  # Coral Gray
        }
        
        # 24-hour patterns (2 days/week)
        patterns_24hr = {
            # Fri/Sat → Sun/Thu → Mon/Tue
            'SSCWN1733': [[4,5], [6,3], [0,1]],  # Autumn Howard
            
            # Sun/Thu → Mon/Tue → Fri/Sat
            'SSCWN1734': [[6,3], [0,1], [4,5]],  # Philip Marshall
            
            # Fri/Sat → Sun/Thu → Mon/Tue
            'SSCWN1735': [[4,5], [6,3], [0,1]],  # Summer Mason
            
            # Mon/Tue → Fri/Sat → Sun/Thu
            'SSCWN1736': [[0,1], [4,5], [6,3]],  # Barry Palmer
            
            # Fri/Sat → Sun/Thu → Mon/Tue
            'SSCWN1738': [[4,5], [6,3], [0,1]],  # Nigel Simpson
            
            # Sun/Thu → Mon/Tue → Fri/Sat
            'SSCWN1739': [[6,3], [0,1], [4,5]],  # May Stevens
            
            # Fri/Sat → Sun/Thu → Mon/Tue
            'SSCWN1740': [[4,5], [6,3], [0,1]],  # Robin Webb
            
            # Sun/Thu → Mon/Tue → Fri/Sat
            'SSCWN1741': [[6,3], [0,1], [4,5]],  # June Wells
            
            # Mon/Tue → Fri/Sat → Sun/Thu
            'SSCWN1742': [[0,1], [4,5], [6,3]],  # Gerald West
            
            # Fri/Sat → Sun/Thu → Mon/Tue
            'SSCWN1743': [[4,5], [6,3], [0,1]],  # Dawn Woods
            
            # Mon/Tue → Fri/Sat → Sun/Thu
            'SSCWN1744': [[0,1], [4,5], [6,3]],  # Roger Barnes
            
            # Fri/Sat → Sun/Thu → Mon/Tue
            'SSCWN1745': [[4,5], [6,3], [0,1]],  # Faith Fisher
            
            # Sun/Thu → Mon/Tue → Fri/Sat
            'SSCWN1746': [[6,3], [0,1], [4,5]],  # Clive Harper
            
            # Mon/Tue → Fri/Sat → Sun/Thu
            'SSCWN1747': [[0,1], [4,5], [6,3]],  # Hope Hayes
        }
        
        # Combine patterns - skip vacancy positions (SSCWN1722, 1727, 1732, 1737)
        all_patterns = {**patterns_35hr, **patterns_24hr}
        
        # Get DAY_ASSISTANT shift type
        day_assistant_type = ShiftType.objects.get(name='DAY_ASSISTANT')
        
        stats = {
            'created': 0,
            'per_staff': {}
        }
        
        for sap in all_patterns.keys():
            stats['per_staff'][sap] = 0
        
        with transaction.atomic():
            for week_offset in range(weeks):
                week_start = start_date + timedelta(weeks=week_offset)
                week_num = week_offset % 3  # 3-week cycle
                
                self.stdout.write(f"\n=== Week {week_offset + 1} (Cycle week {week_num + 1}) ===")
                
                for day_offset in range(7):
                    current_date = week_start + timedelta(days=day_offset)
                    weekday = current_date.weekday()
                    day_name = calendar.day_name[weekday]
                    
                    daily_staff = []
                    
                    # Check each SCA staff member for this day
                    for sap in all_patterns.keys():
                        pattern = all_patterns[sap]
                        working_days = pattern[week_num]
                        
                        if weekday in working_days:
                            daily_staff.append(sap)
                    
                    if not daily_staff:
                        continue
                    
                    # Create shifts for staff working this day
                    for idx, sap in enumerate(daily_staff):
                        staff = User.objects.get(sap=sap)
                        unit = units[idx % len(units)]
                        
                        if not dry_run:
                            Shift.objects.create(
                                user=staff,
                                date=current_date,
                                shift_type=day_assistant_type,
                                unit=unit
                            )
                        
                        stats['created'] += 1
                        stats['per_staff'][sap] += 1
            
            if dry_run:
                self.stdout.write(self.style.WARNING("\n=== DRY RUN - No changes saved ==="))
                raise transaction.TransactionManagementError("Dry run")
        
        # Print summary
        self.stdout.write(self.style.SUCCESS(f"\n=== Summary ==="))
        self.stdout.write(f"Total DAY_ASSISTANT (SCA) shifts created: {stats['created']}")
        self.stdout.write(f"\n35-hour contracts (3 days/week): {len(patterns_35hr)} staff")
        self.stdout.write(f"24-hour contracts (2 days/week): {len(patterns_24hr)} staff")
        self.stdout.write(f"Vacancies (not assigned): 7 positions")
