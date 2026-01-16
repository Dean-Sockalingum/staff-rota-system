"""
Create Victoria Gardens SSCW shifts using 3-week rotating pattern.
SSCW are supernumerary - 2 per day (one per team member), not unit-specific.

3 Teams of 2 SSCW:
- Team A: Sun/Wed/Thu (week 1) → Mon/Tue/Wed (week 2) → Tue/Fri/Sat (week 3)
- Team B: Mon/Tue/Wed (week 1) → Tue/Fri/Sat (week 2) → Sun/Wed/Thu (week 3)
- Team C: Tue/Fri/Sat (week 1) → Sun/Wed/Thu (week 2) → Mon/Tue/Wed (week 3)
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from scheduling.models import Shift, User, CareHome, ShiftType, Unit
from datetime import datetime, timedelta
import calendar

class Command(BaseCommand):
    help = 'Create Victoria Gardens SSCW shifts using 3-week rotating pattern'

    def add_arguments(self, parser):
        parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)')
        parser.add_argument('--weeks', type=int, default=7, help='Number of weeks to create')
        parser.add_argument('--dry-run', action='store_true', help='Preview without saving')

    def handle(self, *args, **options):
        start_date_str = options.get('start-date')
        weeks = options['weeks']
        dry_run = options['dry_run']

        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        else:
            start_date = datetime(2025, 12, 15).date()

        # Get Victoria Gardens and first unit (SSCW are supernumerary, so unit doesn't matter)
        vg = CareHome.objects.get(name='VICTORIA_GARDENS')
        vg_unit = Unit.objects.filter(care_home=vg).first()
        
        # Get SSCW staff (6 total, 3 teams of 2)
        team_a = ['SSCWN1695', 'SSCWN1696']  # Rose Campbell, Michael Robertson
        team_b = ['SSCWN1697', 'SSCWN1698']  # Florence Thomson, Christopher Anderson
        team_c = ['SSCWN1699', 'SSCWN1700']  # Ivy Murray, Andrew Reid
        
        # 3-week rotation patterns
        patterns = {
            'pattern_1': [6, 2, 3],  # Sun, Wed, Thu
            'pattern_2': [0, 1, 2],  # Mon, Tue, Wed
            'pattern_3': [1, 4, 5],  # Tue, Fri, Sat
        }
        
        # Team rotation schedule
        team_schedules = {
            'team_a': ['pattern_1', 'pattern_2', 'pattern_3'],
            'team_b': ['pattern_2', 'pattern_3', 'pattern_1'],
            'team_c': ['pattern_3', 'pattern_1', 'pattern_2'],
        }
        
        # Get DAY_SENIOR shift type
        day_senior_type = ShiftType.objects.get(name='DAY_SENIOR')
        
        stats = {
            'created': 0,
            'team_a': 0,
            'team_b': 0,
            'team_c': 0,
        }
        
        with transaction.atomic():
            for week_offset in range(weeks):
                week_start = start_date + timedelta(weeks=week_offset)
                week_num = week_offset % 3  # 3-week cycle
                
                self.stdout.write(f"\n=== Week {week_offset + 1} (Cycle week {week_num + 1}) ===")
                self.stdout.write(f"Week starting: {week_start}")
                
                for day_offset in range(7):
                    current_date = week_start + timedelta(days=day_offset)
                    weekday = current_date.weekday()  # 0=Monday, 6=Sunday
                    day_name = calendar.day_name[weekday]
                    
                    # Check ALL teams - multiple teams can work same day (overlaps)
                    teams_working = []
                    all_staff = []
                    
                    # Check Team A
                    pattern_key = team_schedules['team_a'][week_num]
                    if weekday in patterns[pattern_key]:
                        teams_working.append('A')
                        all_staff.extend(team_a)
                        stats['team_a'] += 2
                    
                    # Check Team B
                    pattern_key = team_schedules['team_b'][week_num]
                    if weekday in patterns[pattern_key]:
                        teams_working.append('B')
                        all_staff.extend(team_b)
                        stats['team_b'] += 2
                    
                    # Check Team C
                    pattern_key = team_schedules['team_c'][week_num]
                    if weekday in patterns[pattern_key]:
                        teams_working.append('C')
                        all_staff.extend(team_c)
                        stats['team_c'] += 2
                    
                    if not teams_working:
                        continue
                    
                    # Create DAY_SENIOR shifts for ALL staff on scheduled teams
                    # SSCW are supernumerary, so just assign to first unit
                    for staff_sap in all_staff:
                        staff = User.objects.get(sap=staff_sap)
                        
                        if not dry_run:
                            Shift.objects.create(
                                user=staff,
                                date=current_date,
                                shift_type=day_senior_type,
                                unit=vg_unit
                            )
                        
                        stats['created'] += 1
                    
                    teams_str = '+'.join(teams_working)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  {current_date} ({day_name}): Team {teams_str} - {len(all_staff)} shifts created"
                        )
                    )
            
            if dry_run:
                self.stdout.write(self.style.WARNING("\n=== DRY RUN - No changes saved ==="))
                raise transaction.TransactionManagementError("Dry run")
        
        # Print summary
        self.stdout.write(self.style.SUCCESS(f"\n=== Summary ==="))
        self.stdout.write(f"Total DAY_SENIOR shifts created: {stats['created']}")
        self.stdout.write(f"  Team A (Rose, Michael): {stats['team_a']} shifts")
        self.stdout.write(f"  Team B (Florence, Christopher): {stats['team_b']} shifts")
        self.stdout.write(f"  Team C (Ivy, Andrew): {stats['team_c']} shifts")
