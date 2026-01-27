"""
Reallocate Victoria Gardens SSCW staff using 3-week rotating pattern.

3 Teams of 2 SSCW:
- Team A: Sun/Wed/Thu (week 1) → Mon/Tue/Wed (week 2) → Tue/Fri/Sat (week 3)
- Team B: Mon/Tue/Wed (week 1) → Tue/Fri/Sat (week 2) → Sun/Wed/Thu (week 3)
- Team C: Tue/Fri/Sat (week 1) → Sun/Wed/Thu (week 2) → Mon/Tue/Wed (week 3)
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from scheduling.models import Shift, User, CareHome, ShiftType
from datetime import datetime, timedelta
import calendar

class Command(BaseCommand):
    help = 'Reallocate Victoria Gardens SSCW shifts using 3-week rotating pattern'

    def add_arguments(self, parser):
        parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)')
        parser.add_argument('--weeks', type=int, default=7, help='Number of weeks to allocate')
        parser.add_argument('--dry-run', action='store_true', help='Preview changes without saving')

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
        
        # Get SSCW staff (6 total, 3 teams of 2)
        team_a = ['SSCWN1695', 'SSCWN1696']  # Rose Campbell, Michael Robertson
        team_b = ['SSCWN1697', 'SSCWN1698']  # Florence Thomson, Christopher Anderson
        team_c = ['SSCWN1699', 'SSCWN1700']  # Ivy Murray, Andrew Reid
        
        # 3-week rotation patterns
        patterns = {
            'pattern_1': [6, 2, 3],  # Sun, Wed, Thu (weekday numbers: 6=Sunday, 2=Wednesday, 3=Thursday)
            'pattern_2': [0, 1, 2],  # Mon, Tue, Wed
            'pattern_3': [1, 4, 5],  # Tue, Fri, Sat
        }
        
        # Team rotation schedule (which pattern each team follows each week)
        team_schedules = {
            'team_a': ['pattern_1', 'pattern_2', 'pattern_3'],  # Week 1, 2, 3
            'team_b': ['pattern_2', 'pattern_3', 'pattern_1'],
            'team_c': ['pattern_3', 'pattern_1', 'pattern_2'],
        }
        
        # Get DAY_SENIOR shift type
        day_senior_type = ShiftType.objects.get(name='DAY_SENIOR')
        
        stats = {
            'total_shifts': 0,
            'allocated': 0,
            'team_a': 0,
            'team_b': 0,
            'team_c': 0,
        }
        
        with transaction.atomic():
            for week_offset in range(weeks):
                week_start = start_date + timedelta(weeks=week_offset)
                week_num = week_offset % 3  # 3-week cycle
                
                self.stdout.write(f"\n=== Week {week_offset + 1} (Pattern cycle week {week_num + 1}) ===")
                self.stdout.write(f"Week starting: {week_start}")
                
                for day_offset in range(7):
                    current_date = week_start + timedelta(days=day_offset)
                    weekday = current_date.weekday()  # 0=Monday, 6=Sunday
                    day_name = calendar.day_name[weekday]
                    
                    # Determine which team works this day
                    team_working = None
                    staff_pool = []
                    
                    # Check Team A schedule
                    pattern_key = team_schedules['team_a'][week_num]
                    if weekday in patterns[pattern_key]:
                        team_working = 'A'
                        staff_pool = team_a
                    
                    # Check Team B schedule
                    pattern_key = team_schedules['team_b'][week_num]
                    if weekday in patterns[pattern_key]:
                        team_working = 'B'
                        staff_pool = team_b
                    
                    # Check Team C schedule
                    pattern_key = team_schedules['team_c'][week_num]
                    if weekday in patterns[pattern_key]:
                        team_working = 'C'
                        staff_pool = team_c
                    
                    if not team_working:
                        continue
                    
                    # Get DAY_SENIOR shifts for this date (order by unit for consistent assignment)
                    all_shifts = Shift.objects.filter(
                        unit__care_home=vg,
                        date=current_date,
                        shift_type=day_senior_type
                    ).select_related('user', 'unit').order_by('unit__name')
                    
                    if not all_shifts.exists():
                        continue
                    
                    stats['total_shifts'] += all_shifts.count()
                    
                    if team_working == 'A':
                        stats['team_a'] += 2  # 2 team members
                    elif team_working == 'B':
                        stats['team_b'] += 2
                    else:
                        stats['team_c'] += 2
                    
                    # SSCW are supernumerary - only need 2 shifts per day (one per team member)
                    # Assign first 2 shifts to the 2 team members, clear the rest
                    allocated_count = 0
                    for idx, shift in enumerate(all_shifts):
                        if idx < 2:  # Only allocate first 2 shifts
                            staff_sap = staff_pool[idx]  # Assign to team member
                            staff = User.objects.get(sap=staff_sap)
                            
                            if not dry_run:
                                shift.user = staff
                                shift.save()
                            
                            allocated_count += 1
                            stats['allocated'] += 1
                        else:
                            # Extra shifts - clear assignment (SSCW are supernumerary, don't need per-unit)
                            if not dry_run:
                                shift.user = None
                                shift.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  {current_date} ({day_name}): Team {team_working} - {allocated_count} shifts allocated"
                        )
                    )
            
            if dry_run:
                self.stdout.write(self.style.WARNING("\n=== DRY RUN - No changes saved ==="))
                raise transaction.TransactionManagementError("Dry run - rolling back")
        
        # Print summary
        self.stdout.write(self.style.SUCCESS(f"\n=== Summary ==="))
        self.stdout.write(f"Total DAY_SENIOR shifts: {stats['total_shifts']}")
        self.stdout.write(f"Allocated: {stats['allocated']}")
        self.stdout.write(f"  Team A (Rose, Michael): {stats['team_a']} shifts")
        self.stdout.write(f"  Team B (Florence, Christopher): {stats['team_b']} shifts")
        self.stdout.write(f"  Team C (Ivy, Andrew): {stats['team_c']} shifts")
