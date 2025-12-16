from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from scheduling.models import User, Shift, ShiftType
import json


class Command(BaseCommand):
    help = 'Generate shifts based on 3-week rotation patterns for all teams'

    def add_arguments(self, parser):
        parser.add_argument(
            '--start-date',
            type=str,
            help='Start date for shift generation (YYYY-MM-DD). Defaults to next Monday.',
        )
        parser.add_argument(
            '--weeks',
            type=int,
            default=12,
            help='Number of weeks to generate (default: 12)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing shifts before generating new ones',
        )

    def handle(self, *args, **options):
        if options['clear']:
            count = Shift.objects.all().count()
            Shift.objects.all().delete()
            self.stdout.write(f'✓ Cleared {count} existing shifts')

        # Determine start date (default to next Monday)
        if options['start_date']:
            start_date = datetime.strptime(options['start_date'], '%Y-%m-%d').date()
        else:
            today = timezone.now().date()
            days_until_monday = (7 - today.weekday()) % 7
            if days_until_monday == 0:
                days_until_monday = 7
            start_date = today + timedelta(days=days_until_monday)

        self.stdout.write(f'Generating shifts starting from {start_date}')
        self.stdout.write(f'Number of weeks: {options["weeks"]}')

        # Get shift types
        try:
            day_senior_shift = ShiftType.objects.get(name='DAY_SENIOR')
            day_assistant_shift = ShiftType.objects.get(name='DAY_ASSISTANT')
            night_senior_shift = ShiftType.objects.get(name='NIGHT_SENIOR')
            night_assistant_shift = ShiftType.objects.get(name='NIGHT_ASSISTANT')
        except ShiftType.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f'Shift types not found: {e}'))
            return

        # Define 3-week rotation patterns for each team
        # Pattern format: week number (0-2), day of week (0=Monday, 6=Sunday)
        # Team 1 Day pattern: Week1=[Sun,Mon,Tue], Week2=[Wed,Thu,Fri], Week3=[Mon,Tue,Wed]
        team_patterns = {
            '1': {
                'day': [
                    # Week 1: SUN(6), MON(0), TUE(1)
                    [(0, 6), (0, 0), (0, 1)],
                    # Week 2: WED(2), THU(3), FRI(4)
                    [(1, 2), (1, 3), (1, 4)],
                    # Week 3: MON(0), TUE(1), WED(2)
                    [(2, 0), (2, 1), (2, 2)],
                ],
                'night': [
                    # Same as day shift
                    [(0, 6), (0, 0), (0, 1)],
                    [(1, 2), (1, 3), (1, 4)],
                    [(2, 0), (2, 1), (2, 2)],
                ]
            },
            '2': {
                'day': [
                    # Week 1: WED(2), THU(3), FRI(4)
                    [(0, 2), (0, 3), (0, 4)],
                    # Week 2: MON(0), TUE(1), WED(2)
                    [(1, 0), (1, 1), (1, 2)],
                    # Week 3: SUN(6), MON(0), TUE(1)
                    [(2, 6), (2, 0), (2, 1)],
                ],
                'night': [
                    # Same as day shift
                    [(0, 2), (0, 3), (0, 4)],
                    [(1, 0), (1, 1), (1, 2)],
                    [(2, 6), (2, 0), (2, 1)],
                ]
            },
            '3': {
                'day': [
                    # Week 1: MON(0), TUE(1), WED(2)
                    [(0, 0), (0, 1), (0, 2)],
                    # Week 2: SUN(6), MON(0), TUE(1)
                    [(1, 6), (1, 0), (1, 1)],
                    # Week 3: WED(2), THU(3), FRI(4)
                    [(2, 2), (2, 3), (2, 4)],
                ],
                'night': [
                    # Same as day shift
                    [(0, 0), (0, 1), (0, 2)],
                    [(1, 6), (1, 0), (1, 1)],
                    [(2, 2), (2, 3), (2, 4)],
                ]
            }
        }

        shifts_created = 0
        total_weeks = options['weeks']

        # Generate shifts for each team
        for team in ['1', '2', '3']:
            # Day shift staff
            day_staff = User.objects.filter(
                team=team,
                shift_preference__in=['DAY_SENIOR', 'DAY_ASSISTANT'],
                is_staff=False
            )
            
            # Night shift staff
            night_staff = User.objects.filter(
                team=team,
                shift_preference__in=['NIGHT_SENIOR', 'NIGHT_ASSISTANT'],
                is_staff=False
            )

            self.stdout.write(f'\nTeam {team}: {day_staff.count()} day staff, {night_staff.count()} night staff')

            # Generate shifts for each week
            for week_num in range(total_weeks):
                pattern_week = week_num % 3  # Which week in the 3-week pattern
                week_start = start_date + timedelta(weeks=week_num)

                # Process day shift staff
                for staff in day_staff:
                    shifts_per_week = staff.shifts_per_week_override or 3
                    pattern = team_patterns[team]['day']
                    
                    # Determine shift type based on role - SCW uses DAY_SENIOR, SCA uses DAY_ASSISTANT
                    shift_type = day_senior_shift if staff.role.name == 'SCW' else day_assistant_shift
                    
                    # Get the days for this pattern week (limit to shifts_per_week)
                    work_days = pattern[pattern_week][:shifts_per_week]
                    
                    for week_in_pattern, day_of_week in work_days:
                        # Calculate the actual date
                        if week_in_pattern == pattern_week:
                            shift_date = week_start + timedelta(days=day_of_week)
                            
                            # Create shift
                            Shift.objects.create(
                                user=staff,
                                date=shift_date,
                                unit=staff.home_unit,
                                shift_type=shift_type,
                                status='SCHEDULED'
                            )
                            shifts_created += 1

                # Process night shift staff
                for staff in night_staff:
                    shifts_per_week = staff.shifts_per_week_override or 3
                    pattern = team_patterns[team]['night']
                    
                    # Determine shift type based on role - SCWN uses NIGHT_SENIOR, SCAN uses NIGHT_ASSISTANT
                    shift_type = night_senior_shift if staff.role.name == 'SCWN' else night_assistant_shift
                    
                    # Get the days for this pattern week (limit to shifts_per_week)
                    work_days = pattern[pattern_week][:shifts_per_week]
                    
                    for week_in_pattern, day_of_week in work_days:
                        # Calculate the actual date
                        if week_in_pattern == pattern_week:
                            shift_date = week_start + timedelta(days=day_of_week)
                            
                            # Create shift
                            Shift.objects.create(
                                user=staff,
                                date=shift_date,
                                unit=staff.home_unit,
                                shift_type=shift_type,
                                status='SCHEDULED'
                            )
                            shifts_created += 1

        end_date = start_date + timedelta(weeks=total_weeks) - timedelta(days=1)
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Shift generation complete!\n'
            f'Created: {shifts_created} shifts\n'
            f'Period: {start_date} to {end_date} ({total_weeks} weeks)\n'
            f'Pattern: 3-week rotation repeating {total_weeks // 3} times'
        ))
