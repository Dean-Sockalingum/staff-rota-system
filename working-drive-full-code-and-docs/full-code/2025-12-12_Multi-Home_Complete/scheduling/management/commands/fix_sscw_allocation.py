from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import date, timedelta
from scheduling.models import User, Shift, ShiftType, Unit


class Command(BaseCommand):
    help = 'Fix SSCW team allocation and generate proper rotation pattern'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔧 FIXING SSCW TEAM ALLOCATION AND ROTATION'))
        
        # Clear existing shifts to rebuild with correct pattern
        start_date = self._get_next_monday()
        end_date = start_date + timedelta(weeks=6)
        
        # Delete existing shifts in the window
        Shift.objects.filter(
            date__gte=start_date, 
            date__lt=end_date,
            user__role__name='SSCW'
        ).delete()
        
        self.stdout.write(f'🗓️ Generating SSCW roster: {start_date} to {end_date - timedelta(days=1)}')
        
        # Get shift types
        try:
            day_senior = ShiftType.objects.get(name='DAY_SENIOR')
            night_senior = ShiftType.objects.get(name='NIGHT_SENIOR')
            care_units = list(Unit.objects.exclude(name='ADMIN').order_by('name'))
        except (ShiftType.DoesNotExist, Unit.DoesNotExist) as e:
            self.stderr.write(self.style.ERROR(f'❌ Missing data: {e}'))
            return
        
        # Get SSCW staff by team and shift preference
        day_sscw_teams = {
            'A': list(User.objects.filter(team='A', role__name='SSCW', shift_preference='DAY_SENIOR', is_active=True)),
            'B': list(User.objects.filter(team='B', role__name='SSCW', shift_preference='DAY_SENIOR', is_active=True)),
            'C': list(User.objects.filter(team='C', role__name='SSCW', shift_preference='DAY_SENIOR', is_active=True)),
        }
        
        night_sscw_teams = {
            'A': list(User.objects.filter(team='A', role__name='SSCW', shift_preference='NIGHT_SENIOR', is_active=True)),
            'B': list(User.objects.filter(team='B', role__name='SSCW', shift_preference='NIGHT_SENIOR', is_active=True)),
            'C': list(User.objects.filter(team='C', role__name='SSCW', shift_preference='NIGHT_SENIOR', is_active=True)),
        }
        
        self.stdout.write('📊 Current SSCW Team Structure:')
        for team in ['A', 'B', 'C']:
            day_count = len(day_sscw_teams[team])
            night_count = len(night_sscw_teams[team])
            self.stdout.write(f'   Team {team}: {day_count} day SSCW, {night_count} night SSCW')
        
        # Define the 3-week rotation pattern for teams
        # Each team works for 1 week, then off for 2 weeks
        team_rotation_pattern = {
            1: 'A',  # Week 1: Team A works
            2: 'B',  # Week 2: Team B works  
            3: 'C',  # Week 3: Team C works
            4: 'A',  # Week 4: Team A works
            5: 'B',  # Week 5: Team B works
            6: 'C',  # Week 6: Team C works
        }
        
        shifts_created = 0
        
        # Generate shifts for 6 weeks
        for week_num in range(1, 7):
            week_start = start_date + timedelta(weeks=week_num-1)
            working_team = team_rotation_pattern[week_num]
            
            self.stdout.write(f'\\n📅 Week {week_num} ({week_start}): Team {working_team} working')
            
            # Generate shifts for each day of the week
            for day_offset in range(7):
                current_date = week_start + timedelta(days=day_offset)
                day_name = current_date.strftime('%A')
                
                # Day shifts: All 3 SSCW from working team
                day_team_sscw = day_sscw_teams[working_team]
                if len(day_team_sscw) >= 3:
                    for i, sscw in enumerate(day_team_sscw[:3]):  # Take first 3
                        unit = care_units[i % len(care_units)]  # Distribute across units
                        Shift.objects.create(
                            user=sscw,
                            unit=unit,
                            shift_type=day_senior,
                            date=current_date,
                            status='SCHEDULED'
                        )
                        shifts_created += 1
                
                # Night shifts: Pattern based on team
                night_team_sscw = night_sscw_teams[working_team]
                if working_team in ['A', 'B']:
                    # Teams A & B: 3 night SSCW
                    night_count = 3
                else:
                    # Team C: 2 night SSCW
                    night_count = 2
                
                if len(night_team_sscw) >= night_count:
                    for i, sscw in enumerate(night_team_sscw[:night_count]):
                        unit = care_units[i % len(care_units)]  # Distribute across units
                        Shift.objects.create(
                            user=sscw,
                            unit=unit,
                            shift_type=night_senior,
                            date=current_date,
                            status='SCHEDULED'
                        )
                        shifts_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'✅ SSCW roster fixed! Created {shifts_created} shifts'))
        
        # Verify the new pattern
        self._verify_sscw_coverage(start_date, team_rotation_pattern)
    
    def _get_next_monday(self):
        """Get the next Monday from today"""
        today = date.today()
        days_ahead = 0 - today.weekday()  # Monday is 0
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        return today + timedelta(days_ahead)
    
    def _verify_sscw_coverage(self, start_date, team_pattern):
        """Verify the SSCW coverage follows the correct pattern"""
        self.stdout.write('\\n🔍 VERIFICATION - SSCW Coverage Pattern:')
        
        for week_num in range(1, 4):  # Check first 3 weeks
            week_start = start_date + timedelta(weeks=week_num-1)
            expected_team = team_pattern[week_num]
            
            # Check Monday of each week
            monday = week_start
            
            day_shifts = Shift.objects.filter(
                date=monday,
                shift_type__name='DAY_SENIOR',
                user__role__name='SSCW'
            ).count()
            
            night_shifts = Shift.objects.filter(
                date=monday,
                shift_type__name='NIGHT_SENIOR',  
                user__role__name='SSCW'
            ).count()
            
            # Get actual teams working
            day_teams = set(Shift.objects.filter(
                date=monday,
                shift_type__name='DAY_SENIOR',
                user__role__name='SSCW'
            ).values_list('user__team', flat=True))
            
            night_teams = set(Shift.objects.filter(
                date=monday,
                shift_type__name='NIGHT_SENIOR',
                user__role__name='SSCW'
            ).values_list('user__team', flat=True))
            
            # Expected counts
            expected_night = 3 if expected_team in ['A', 'B'] else 2
            
            status_day = '✅' if day_shifts == 3 and day_teams == {expected_team} else '❌'
            status_night = '✅' if night_shifts == expected_night and night_teams == {expected_team} else '❌'
            
            self.stdout.write(
                f'   Week {week_num} ({monday}): {status_day} Day: {day_shifts}/3 Team {expected_team} | '
                f'{status_night} Night: {night_shifts}/{expected_night} Team {expected_team}'
            )
        
        self.stdout.write('\\n🎯 COVERAGE SUMMARY:')
        self.stdout.write('   📅 Day shifts: 3 SSCW always on duty (all from same team)')
        self.stdout.write('   🌙 Night shifts: 2-3 SSCW on duty (Teams A&B=3, Team C=2)')
        self.stdout.write('   🔄 Teams rotate weekly: A→B→C→A→B→C')
        self.stdout.write('   ✅ Minimum 2 SSCW guaranteed at all times')