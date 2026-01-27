from collections import defaultdict, deque
from datetime import date, timedelta
import random

from django.core.management.base import BaseCommand
from django.db import transaction

from scheduling.models import Shift, ShiftType, Unit, User

class Command(BaseCommand):
    help = 'Generate a six-week rota that satisfies unit staffing rules and weekly admin days.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--start-date',
            type=str,
            help='Optional ISO date (YYYY-MM-DD). Defaults to the upcoming Monday.'
        )

    def handle(self, *args, **options):
        start_date = self._resolve_start_date(options.get('start_date'))
        end_date = start_date + timedelta(weeks=6)

        self.stdout.write(self.style.SUCCESS('--- GENERATING 6-WEEK ROTA ---'))
        self.stdout.write(f'🗓️  Period: {start_date} ➜ {end_date - timedelta(days=1)}')

        # Purge existing shifts in the window so we regenerate from a clean slate.
        Shift.objects.filter(date__gte=start_date, date__lt=end_date).delete()
        self.stdout.write('🧹 Cleared existing shifts for the selected window.')

        try:
            shift_types = {
                'DAY_SENIOR': ShiftType.objects.get(name='DAY_SENIOR'),
                'DAY_ASSISTANT': ShiftType.objects.get(name='DAY_ASSISTANT'),
                'NIGHT_SENIOR': ShiftType.objects.get(name='NIGHT_SENIOR'),
                'NIGHT_ASSISTANT': ShiftType.objects.get(name='NIGHT_ASSISTANT'),
                'ADMIN': ShiftType.objects.get(name='ADMIN'),
            }
            admin_unit = Unit.objects.get(name='ADMIN')
            care_units = list(Unit.objects.exclude(name='ADMIN').order_by('name'))
        except (ShiftType.DoesNotExist, Unit.DoesNotExist) as exc:
            self.stderr.write(self.style.ERROR(f'❌ Missing prerequisite data: {exc}'))
            return

        all_scw_staff = list(
            User.objects.filter(is_active=True, role__name__in=['SCW', 'SSCW']).exclude(role__name__icontains='Relief')
        )
        sca_staff = list(
            User.objects.filter(is_active=True, role__name='SCA').exclude(role__name__icontains='Relief')
        )

        if not all_scw_staff or not sca_staff:
            self.stderr.write(self.style.ERROR('❌ Unable to build rota: no active SCW/SCA staff found.'))
            return

        scw_staff = [staff for staff in all_scw_staff if staff.role.name == 'SCW']
        sscw_staff = [staff for staff in all_scw_staff if staff.role.name == 'SSCW']

        day_scw_staff = [staff for staff in scw_staff if staff.shift_preference == 'DAY_SENIOR']
        night_scw_staff = [staff for staff in scw_staff if staff.shift_preference == 'NIGHT_SENIOR']
        unassigned_scw = [staff for staff in scw_staff if staff.shift_preference not in ['DAY_SENIOR', 'NIGHT_SENIOR']]

        day_sscw_staff = [staff for staff in sscw_staff if staff.shift_preference == 'DAY_SENIOR']
        night_sscw_staff = [staff for staff in sscw_staff if staff.shift_preference == 'NIGHT_SENIOR']
        unassigned_sscw = [staff for staff in sscw_staff if staff.shift_preference not in ['DAY_SENIOR', 'NIGHT_SENIOR']]

        day_sca_staff = [staff for staff in sca_staff if staff.shift_preference == 'DAY_ASSISTANT']
        night_sca_staff = [staff for staff in sca_staff if staff.shift_preference == 'NIGHT_ASSISTANT']
        unassigned_sca = [staff for staff in sca_staff if staff.shift_preference not in ['DAY_ASSISTANT', 'NIGHT_ASSISTANT']]

        if unassigned_scw:
            self.stderr.write(self.style.WARNING(f'⚠️  {len(unassigned_scw)} SCW have no day/night preference. Defaulting them to day shifts.'))
            day_scw_staff.extend(unassigned_scw)

        if unassigned_sscw:
            self.stderr.write(self.style.WARNING(f'⚠️  {len(unassigned_sscw)} SSCW have no day/night preference. Defaulting them to day-duty.'))
            day_sscw_staff.extend(unassigned_sscw)

        if unassigned_sca:
            self.stderr.write(self.style.WARNING(f'⚠️  {len(unassigned_sca)} SCA have no day/night preference. Defaulting them to day shifts.'))
            day_sca_staff.extend(unassigned_sca)

        if not day_scw_staff or not night_scw_staff:
            self.stderr.write(self.style.WARNING('⚠️  Insufficient SCW distribution across day/night preferences. Expect coverage warnings.'))

        if not day_sscw_staff or not night_sscw_staff:
            self.stderr.write(self.style.WARNING('⚠️  Insufficient SSCW distribution across day/night preferences. Duty cover may be short.'))

        if not day_sca_staff or not night_sca_staff:
            self.stderr.write(self.style.WARNING('⚠️  Insufficient SCA distribution across day/night preferences. Expect coverage warnings.'))

        self.stdout.write(
            f'✅ Staff pool ➜ Day SCW: {len(day_scw_staff)} | Night SCW: {len(night_scw_staff)} | '
            f'Day SSCW: {len(day_sscw_staff)} | Night SSCW: {len(night_sscw_staff)} | '
            f'Day SCA: {len(day_sca_staff)} | Night SCA: {len(night_sca_staff)} | Units: {len(care_units)}'
        )

        admin_plan = self._plan_admin_days(start_date, day_scw_staff)
        sscw_admin_plan = self._plan_admin_days(start_date, sscw_staff)

        for admin_date, staff_list in sscw_admin_plan.items():
            admin_plan[admin_date].extend(staff_list)

        total_admin_allocations = sum(len(staff) for staff in admin_plan.values())
        sscw_admin_total = sum(len(staff) for staff in sscw_admin_plan.values())
        self.stdout.write(
            f'🗃️  Planned admin days ➜ Total: {total_admin_allocations} | SSCW-specific: {sscw_admin_total}'
        )

        self.day_sscw_pool = deque(day_sscw_staff)
        self.night_sscw_pool = deque(night_sscw_staff)
        self.start_date = start_date  # Store for 6-week SCA pattern calculation

        total_shifts_created = 0

        # 3-WEEK ROTATION IMPLEMENTATION  
        # Teams work specific days that rotate every week in a 3-week cycle
        
        # Define the 3-day worker patterns (SCW/SSCW) - DAY SHIFTS
        self.scw_patterns = {
            1: {'A': [0, 1, 2], 'B': [4, 5, 6], 'C': [2, 3, 4]},  # Week 1: A=Sun,Mon,Tue | B=Thu,Fri,Sat | C=Tue,Wed,Thu
            2: {'A': [4, 5, 6], 'B': [2, 3, 4], 'C': [0, 1, 2]},  # Week 2: A=Thu,Fri,Sat | B=Tue,Wed,Thu | C=Sun,Mon,Tue
            3: {'A': [2, 3, 4], 'B': [0, 1, 2], 'C': [4, 5, 6]}   # Week 3: A=Tue,Wed,Thu | B=Sun,Mon,Tue | C=Thu,Fri,Sat
        }
        
        # Define the 2-day worker patterns (SCA) - DAY SHIFTS (Wednesday is always off)
        self.sca_patterns = {
            1: {'A': [0, 4], 'B': [1, 2], 'C': [5, 6]},  # Week 1: A=Sun,Thu | B=Mon,Tue | C=Fri,Sat
            2: {'A': [1, 2], 'B': [5, 6], 'C': [0, 4]},  # Week 2: A=Mon,Tue | B=Fri,Sat | C=Sun,Thu
            3: {'A': [5, 6], 'B': [0, 4], 'C': [1, 2]}   # Week 3: A=Fri,Sat | B=Sun,Thu | C=Mon,Tue
        }
        
        # Define the 3-day worker patterns (SCW/SSCW) - NIGHT SHIFTS
        self.night_scw_patterns = {
            1: {'A': [0, 1, 2], 'B': [4, 5, 6], 'C': [2, 3, 4]},  # Week 1: A=Sun,Mon,Tue | B=Thu,Fri,Sat | C=Tue,Wed,Thu
            2: {'A': [4, 5, 6], 'B': [2, 3, 4], 'C': [0, 1, 2]},  # Week 2: A=Thu,Fri,Sat | B=Tue,Wed,Thu | C=Sun,Mon,Tue
            3: {'A': [2, 3, 4], 'B': [0, 1, 2], 'C': [4, 5, 6]}   # Week 3: A=Tue,Wed,Thu | B=Sun,Mon,Tue | C=Thu,Fri,Sat
        }
        
        # Define the 2-day worker patterns (SCA) - NIGHT SHIFTS
        self.night_sca_patterns = {
            1: {'A': [5, 6], 'B': [2, 3], 'C': [0, 1]},  # Week 1: A=Fri,Sat | B=Tue,Wed | C=Sun,Mon
            2: {'A': [2, 3], 'B': [0, 1], 'C': [5, 6]},  # Week 2: A=Tue,Wed | B=Sun,Mon | C=Fri,Sat
            3: {'A': [0, 1], 'B': [5, 6], 'C': [2, 3]}   # Week 3: A=Sun,Mon | B=Fri,Sat | C=Tue,Wed
        }
        
        # SSCW UNIT MANAGEMENT ASSIGNMENTS
        # Each SSCW is assigned to manage a specific unit following the 3-week rotation
        self.sscw_unit_assignments = {
            'day': {
                'A': [('DEMENTIA', 'SSW001'), ('BLUE', 'SSW002'), ('VIOLET', 'SSW003')],
                'B': [('ROSE', 'SSW004'), ('GRAPE', 'SSW005'), ('PEACH', 'SSW006')],
                'C': [('ORANGE', 'SSW007'), ('GREEN', 'SSW008')],  # Removed LEAVE COVER for consistency
            },
            'night': {
                'A': [('DEMENTIA', 'SSW009'), ('BLUE', 'SSW010')],
                'B': [('ROSE', 'SSW011'), ('GRAPE', 'SSW012')],
                'C': [('ORANGE', 'SSW013'), ('GREEN', 'SSW014')],  # No LEAVE COVER for night shifts
            }
        }
        
        # UNIT-TEAM ALLOCATION SETUP
        # Define team priority order for each unit (all teams can work any unit, but with priorities)
        # This ensures every unit gets coverage even when preferred teams aren't working
        self.unit_team_allocation = {
            'day': {
                'BLUE': ['A', 'B', 'C'],      # Primary: A,B; Backup: C
                'DEMENTIA': ['A', 'C', 'B'],  # Primary: A,C; Backup: B
                'GRAPE': ['B', 'C', 'A'],     # Primary: B,C; Backup: A
                'GREEN': ['A', 'B', 'C'],     # Primary: A,B; Backup: C
                'ORANGE': ['B', 'C', 'A'],    # Primary: B,C; Backup: A
                'PEACH': ['A', 'C', 'B'],     # Primary: A,C; Backup: B
                'ROSE': ['A', 'B', 'C'],      # Primary: A,B; Backup: C
                'VIOLET': ['B', 'C', 'A']     # Primary: B,C; Backup: A
            },
            'night': {
                'BLUE': ['A', 'C', 'B'],      # Primary: A,C; Backup: B (different from day)
                'DEMENTIA': ['B', 'C', 'A'],  # Primary: B,C; Backup: A
                'GRAPE': ['A', 'B', 'C'],     # Primary: A,B; Backup: C
                'GREEN': ['A', 'C', 'B'],     # Primary: A,C; Backup: B
                'ORANGE': ['A', 'B', 'C'],    # Primary: A,B; Backup: C
                'PEACH': ['B', 'C', 'A'],     # Primary: B,C; Backup: A
                'ROSE': ['A', 'C', 'B'],      # Primary: A,C; Backup: B
                'VIOLET': ['A', 'B', 'C']     # Primary: A,B; Backup: C
            }
        }
        
        def get_team_working_days(team, week_number, worker_type, shift_period='day'):
            """Get which days of the week a team works based on the 3-week rotation"""
            pattern_week = ((week_number - 1) % 3) + 1
            
            if shift_period == 'night':
                if worker_type == 'SCA':
                    return self.night_sca_patterns[pattern_week][team]
                else:  # SCW/SSCW night shifts
                    return self.night_scw_patterns[pattern_week][team]
            else:  # day shifts (default)
                if worker_type == 'SCA':
                    return self.sca_patterns[pattern_week][team]
                else:  # SCW/SSCW day shifts
                    return self.scw_patterns[pattern_week][team]

        with transaction.atomic():
            for week_index in range(6):
                week_number = week_index + 1
                week_start = start_date + timedelta(weeks=week_index)
                pattern_week = ((week_number - 1) % 3) + 1
                
                # Show which days each team works this week
                team_schedules = {}
                day_names = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
                
                for team in ['A', 'B', 'C']:
                    day_scw_days = get_team_working_days(team, week_number, 'SCW', 'day')
                    day_sca_days = get_team_working_days(team, week_number, 'SCA', 'day')
                    night_scw_days = get_team_working_days(team, week_number, 'SCW', 'night')
                    night_sca_days = get_team_working_days(team, week_number, 'SCA', 'night')
                    team_schedules[team] = {
                        'day_scw_days': day_scw_days, 'day_sca_days': day_sca_days,
                        'night_scw_days': night_scw_days, 'night_sca_days': night_sca_days
                    }
                
                self.stdout.write(self.style.HTTP_INFO(
                    f'\n--- WEEK {week_number} ➜ {week_start} | 3-Week Rotation (Pattern {pattern_week}) ---'
                ))
                for team in ['A', 'B', 'C']:
                    day_scw_names = [day_names[d] for d in team_schedules[team]['day_scw_days']]
                    day_sca_names = [day_names[d] for d in team_schedules[team]['day_sca_days']]
                    night_scw_names = [day_names[d] for d in team_schedules[team]['night_scw_days']]
                    night_sca_names = [day_names[d] for d in team_schedules[team]['night_sca_days']]
                    self.stdout.write(f'Team {team}: Day SCW/SSCW={day_scw_names} | Day SCA={day_sca_names}')
                    self.stdout.write(f'          Night SCW/SSCW={night_scw_names} | Night SCA={night_sca_names}')

                # Teams work specific days based on their 3-week rotation pattern
                weekly_shift_counts = defaultdict(int)
                team_day_sscw_pools = {
                    'A': deque([s for s in day_sscw_staff if s.team == 'A']),
                    'B': deque([s for s in day_sscw_staff if s.team == 'B']),
                    'C': deque([s for s in day_sscw_staff if s.team == 'C'])
                }
                team_night_sscw_pools = {
                    'A': deque([s for s in night_sscw_staff if s.team == 'A']),
                    'B': deque([s for s in night_sscw_staff if s.team == 'B']),
                    'C': deque([s for s in night_sscw_staff if s.team == 'C'])
                }

                # Generate shifts for each day of the week
                for day_offset in range(7):
                    current_date = week_start + timedelta(days=day_offset)
                    busy_today = set()

                    # Assign admin days (from pre-planned admin schedule)
                    if current_date in admin_plan:
                        for scw in admin_plan[current_date]:
                            if weekly_shift_counts[scw.sap] >= 3:
                                continue

                            Shift.objects.create(
                                user=scw,
                                unit=admin_unit,
                                shift_type=shift_types['ADMIN'],
                                date=current_date,
                                status='SCHEDULED',
                            )
                            weekly_shift_counts[scw.sap] += 1
                            busy_today.add(scw.sap)
                            total_shifts_created += 1

                    # Determine which teams are working today for day and night shifts
                    day_of_week = (current_date.weekday() + 1) % 7  # Convert to 0=Sunday format
                    
                    working_teams_day = []
                    working_teams_night = []
                    
                    for team in ['A', 'B', 'C']:
                        # Day shift teams (existing logic)
                        scw_days = get_team_working_days(team, week_number, 'SCW', 'day')
                        if day_of_week in scw_days:
                            working_teams_day.append(team)
                        
                        # Night shift teams (new specific patterns)
                        night_scw_days = get_team_working_days(team, week_number, 'SCW', 'night')
                        if day_of_week in night_scw_days:
                            working_teams_night.append(team)
                    
                    # Assign SSCW based on specific unit management assignments
                    total_shifts_created += self._assign_sscw_managers(
                        current_date, 'day', working_teams_day, week_number,
                        team_day_sscw_pools, weekly_shift_counts, busy_today, 
                        shift_types['DAY_SENIOR'], care_units
                    )
                    
                    total_shifts_created += self._assign_sscw_managers(
                        current_date, 'night', working_teams_night, week_number,
                        team_night_sscw_pools, weekly_shift_counts, busy_today,
                        shift_types['NIGHT_SENIOR'], care_units
                    )

                    # Assign regular care staff coverage based on team working days
                    total_shifts_created += self._assign_day_based_coverage(
                        current_date, 'day', care_units, working_teams_day, week_number,
                        day_scw_staff, day_sca_staff, weekly_shift_counts, busy_today, shift_types
                    )
                    total_shifts_created += self._assign_day_based_coverage(
                        current_date, 'night', care_units, working_teams_night, week_number,
                        night_scw_staff, night_sca_staff, weekly_shift_counts, busy_today, shift_types
                    )

                # End-of-week validation: Ensure minimum shift requirements are met for all teams
                for team in ['A', 'B', 'C']:
                    team_day_scw = [s for s in day_scw_staff if s.team == team]
                    team_night_scw = [s for s in night_scw_staff if s.team == team]
                    team_day_sca = [s for s in day_sca_staff if s.team == team]
                    team_night_sca = [s for s in night_sca_staff if s.team == team]
                    
                    total_shifts_created += self._ensure_minimum_shifts_team(
                        week_start,
                        team_day_scw + team_night_scw,
                        team_day_sca + team_night_sca,
                        weekly_shift_counts,
                        shift_types,
                        care_units,
                    )

        self.stdout.write(self.style.SUCCESS(f'\n✅ Rota generation complete. Total shifts created: {total_shifts_created}'))
        self._validate_sscw_admin(start_date, end_date, sscw_staff)
        self._print_first_week_summary(start_date)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _resolve_start_date(self, supplied):
        if supplied:
            return date.fromisoformat(supplied)

        today = date.today()
        return today + timedelta(days=-today.weekday())

    def _get_sca_day_pattern_schedule(self, staff_index, current_date, start_date):
        """
        Implements 6-week rotation pattern for SCA day shifts:
        Week 1: Sunday + Thursday
        Week 2: Monday + Tuesday  
        Week 3: Friday + Saturday
        Week 4: Sunday + Thursday
        Week 5: Monday + Tuesday
        Week 6: Friday + Saturday
        
        Staff are distributed across 3 starting points (33% each)
        """
        # Calculate which week we're in (0-5) and day of week (0=Monday, 6=Sunday)
        days_since_start = (current_date - start_date).days
        week_number = days_since_start // 7
        day_of_week = current_date.weekday()  # 0=Monday, 6=Sunday
        
        # Determine which pattern week this staff member should follow
        # Distribute staff across 3 starting points
        staff_start_week = staff_index % 3
        pattern_week = (week_number + staff_start_week) % 6
        
        # Define the 6-week pattern (True = working day)
        pattern = {
            0: {6: True, 3: True},  # Week 1: Sunday(6) + Thursday(3)
            1: {0: True, 1: True},  # Week 2: Monday(0) + Tuesday(1)
            2: {4: True, 5: True},  # Week 3: Friday(4) + Saturday(5)
            3: {6: True, 3: True},  # Week 4: Sunday(6) + Thursday(3)
            4: {0: True, 1: True},  # Week 5: Monday(0) + Tuesday(1)
            5: {4: True, 5: True},  # Week 6: Friday(4) + Saturday(5)
        }
        
        return pattern[pattern_week].get(day_of_week, False)

    def _assign_unit_period(
        self,
        current_date,
        period,
        units,
        scw_staff,
        sca_staff,
        weekly_shift_counts,
        busy_today,
        shift_types,
    ):
        scw_shift_key = 'DAY_SENIOR' if period == 'day' else 'NIGHT_SENIOR'
        sca_shift_key = 'DAY_ASSISTANT' if period == 'day' else 'NIGHT_ASSISTANT'
        shifts_created = 0

        for unit in units:
            requirements = self._unit_requirements(unit)[period]

            # Allocate SCWs first - prioritize those with fewer shifts this week.
            scw_available = [
                staff for staff in scw_staff
                if weekly_shift_counts[staff.sap] < 3 and staff.sap not in busy_today
            ]
            # Sort by current shift count (ascending) to prioritize those with fewer shifts
            scw_available.sort(key=lambda x: weekly_shift_counts[x.sap])

            selected_scw = scw_available[:requirements['SCW']]
            scw_shortfall = requirements['SCW'] - len(selected_scw)

            for staff in selected_scw:
                Shift.objects.create(
                    user=staff,
                    unit=unit,
                    shift_type=shift_types[scw_shift_key],
                    date=current_date,
                    status='SCHEDULED',
                )
                weekly_shift_counts[staff.sap] += 1
                busy_today.add(staff.sap)
                shifts_created += 1

            # For day shifts, use 6-week SCA pattern; for nights use existing logic
            if period == 'day':
                # Get all SCA staff for this unit (not busy today)
                sca_available = [
                    staff for staff in sca_staff
                    if staff.sap not in busy_today
                ]
                
                # Filter SCA based on 6-week pattern schedule
                pattern_sca = []
                for staff in sca_available:
                    staff_index = sca_staff.index(staff)
                    if self._get_sca_day_pattern_schedule(staff_index, current_date, self.start_date):
                        pattern_sca.append(staff)
                
                # Select required number of SCA
                selected_sca = pattern_sca[:requirements['SCA']]
                
            else:
                # Night shifts: use existing logic - prioritize those with fewer shifts this week
                sca_available = [
                    staff for staff in sca_staff
                    if weekly_shift_counts[staff.sap] < 2 and staff.sap not in busy_today
                ]
                # Sort by current shift count (ascending) to prioritize those with fewer shifts
                sca_available.sort(key=lambda x: weekly_shift_counts[x.sap])
                selected_sca = sca_available[:requirements['SCA']]

            # Handle SCW shortfall by using SCA as cover
            cover_count = 0
            if scw_shortfall > 0:
                # For day shifts, get pattern-based SCA for cover; for nights use existing logic
                if period == 'day':
                    sca_for_cover = [
                        staff for staff in sca_staff
                        if staff.sap not in busy_today and staff not in selected_sca
                    ]
                    # Apply pattern filter for day cover
                    pattern_cover_sca = []
                    for staff in sca_for_cover:
                        staff_index = sca_staff.index(staff)
                        if self._get_sca_day_pattern_schedule(staff_index, current_date, self.start_date):
                            pattern_cover_sca.append(staff)
                    
                    cover_count = min(scw_shortfall, len(pattern_cover_sca))
                    sca_cover = pattern_cover_sca[:cover_count]
                else:
                    # Night shifts: use existing logic
                    sca_for_cover = [
                        staff for staff in sca_staff
                        if weekly_shift_counts[staff.sap] < 2 and staff.sap not in busy_today
                    ]
                    cover_count = min(scw_shortfall, len(sca_for_cover))
                    sca_cover = sca_for_cover[:cover_count]
                
                for staff in sca_cover:
                    Shift.objects.create(
                        user=staff,
                        unit=unit,
                        shift_type=shift_types[scw_shift_key],
                        date=current_date,
                        status='SCHEDULED',
                    )
                    weekly_shift_counts[staff.sap] += 1
                    busy_today.add(staff.sap)
                    shifts_created += 1
                
                if cover_count > 0:
                    self.stdout.write(
                        f'ℹ️  {current_date} {period.upper()} {unit.name}: used {cover_count} SCA to backfill SCW duty.'
                    )

            if scw_shortfall - cover_count > 0:
                self.stderr.write(
                    self.style.WARNING(
                        f'⚠️  {current_date} {period.upper()} {unit.name}: missing {scw_shortfall - cover_count} SCW'
                    )
                )

            # Check if we have enough SCA for the unit requirements
            if len(selected_sca) < requirements['SCA']:
                self.stderr.write(
                    self.style.WARNING(
                        f'⚠️  {current_date} {period.upper()} {unit.name}: missing {requirements["SCA"] - len(selected_sca)} SCA'
                    )
                )

            for staff in selected_sca:
                Shift.objects.create(
                    user=staff,
                    unit=unit,
                    shift_type=shift_types[sca_shift_key],
                    date=current_date,
                    status='SCHEDULED',
                )
                weekly_shift_counts[staff.sap] += 1
                busy_today.add(staff.sap)
                shifts_created += 1

        return shifts_created

    def _plan_admin_days(self, start_date, staff_list):
        plan = defaultdict(list)

        for index, staff in enumerate(staff_list):
            for slot in range(3):
                week_index = min(slot * 2 + (index % 2), 5)
                week_start = start_date + timedelta(weeks=week_index)
                day_offset = ((index // 2) + slot) % 5  # keep within Monday-Friday
                admin_date = week_start + timedelta(days=day_offset)
                plan[admin_date].append(staff)

        return plan

    def _unit_requirements(self, unit):
        """
        Returns staffing requirements based on Standard Work Patterns Sept 2024
        Each unit requires minimum staff levels as per official guidance
        """
        unit_name = unit.name.upper()
        
        # Standard pattern for most care units
        if unit_name in ['PEACH', 'ROSE', 'VIOLET', 'BLUE', 'GREEN', 'ORANGE', 'GRAPE']:
            return {
                'day': {'SCW': 1, 'SCA': 2},    # 1 SCW + 2 SCA for day shifts
                'night': {'SCW': 1, 'SCA': 1},  # 1 SCW + 1 SCA for night shifts
            }
        
        # Dementia unit requires higher staffing levels
        elif unit_name == 'DEMENTIA':
            return {
                'day': {'SCW': 1, 'SCA': 3},    # 1 SCW + 3 SCA for day shifts  
                'night': {'SCW': 1, 'SCA': 2},  # 1 SCW + 2 SCA for night shifts
            }
        
        # Default for any other units
        else:
            return {
                'day': {'SCW': 1, 'SCA': 2},
                'night': {'SCW': 1, 'SCA': 1},
            }

    def _assign_supernumerary(
        self,
        current_date,
        period,
        shift_type,
        weekly_shift_counts,
        busy_today,
        unit,
        pool,
        required_count=1,
    ):
        if not pool:
            return 0

        assigned = 0
        rotations = len(pool)

        while rotations and assigned < required_count:
            staff = pool[0]
            if weekly_shift_counts[staff.sap] < 3 and staff.sap not in busy_today:
                Shift.objects.create(
                    user=staff,
                    unit=unit,
                    shift_type=shift_type,
                    date=current_date,
                    status='SCHEDULED',
                )
                weekly_shift_counts[staff.sap] += 1
                busy_today.add(staff.sap)
                assigned += 1

            pool.rotate(-1)
            rotations -= 1

        if assigned < required_count:
            self.stderr.write(
                self.style.WARNING(
                    f'⚠️  {current_date} {period.upper()} SUPERNUMERARY: only {assigned}/{required_count} SSCW available for duty.'
                )
            )

        return assigned

    def _validate_sscw_admin(self, start_date, end_date, sscw_staff):
        if not sscw_staff:
            return

        shortfalls = []

        for staff in sscw_staff:
            admin_count = Shift.objects.filter(
                user=staff,
                date__gte=start_date,
                date__lt=end_date,
                shift_type__name='ADMIN',
            ).count()
            if admin_count < 3:
                shortfalls.append((staff, admin_count))

        if shortfalls:
            for staff, count in shortfalls:
                display_name = getattr(staff, 'get_full_name', None)
                if callable(display_name):
                    name = display_name()
                else:
                    name = getattr(staff, 'first_name', '') or str(staff)

                self.stderr.write(
                    self.style.WARNING(
                        f'⚠️  SSCW {name} assigned {count}/3 admin days for the rota window.'
                    )
                )
        else:
            self.stdout.write(self.style.SUCCESS('✅ All SSCW have at least 3 admin days allocated.'))

    def _print_first_week_summary(self, start_date):
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('📊  FIRST WEEK COVERAGE CHECK')
        self.stdout.write('=' * 60)

        for offset in range(7):
            current_date = start_date + timedelta(days=offset)
            day_name = current_date.strftime('%A')

            day_scw = Shift.objects.filter(
                date=current_date,
                shift_type__name='DAY_SENIOR',
            ).count()
            day_sca = Shift.objects.filter(
                date=current_date,
                shift_type__name='DAY_ASSISTANT',
            ).count()
            night_scw = Shift.objects.filter(
                date=current_date,
                shift_type__name='NIGHT_SENIOR',
            ).count()
            night_sca = Shift.objects.filter(
                date=current_date,
                shift_type__name='NIGHT_ASSISTANT',
            ).count()

            self.stdout.write(
                f'- {day_name}: Day ➜ SCW {day_scw}/8 | SCA {day_sca}/17   ·   Night ➜ SCW {night_scw}/8 | SCA {night_sca}/9'
            )

    def _ensure_minimum_shifts(self, week_start, scw_staff, sca_staff, weekly_shift_counts, shift_types, care_units):
        """Ensure all staff get their minimum required shifts for the week"""
        shifts_added = 0
        week_end = week_start + timedelta(days=6)
        
        # Check SCW/SSCW staff (should have 3 shifts)
        for staff in scw_staff:
            current_count = weekly_shift_counts[staff.sap]
            if current_count < 3:
                needed = 3 - current_count
                shifts_added += self._add_makeup_shifts(
                    staff, needed, week_start, week_end, shift_types, care_units, 'SCW'
                )
                
        # Check SCA staff (should have 2 shifts)  
        for staff in sca_staff:
            current_count = weekly_shift_counts[staff.sap]
            if current_count < 2:
                needed = 2 - current_count
                shifts_added += self._add_makeup_shifts(
                    staff, needed, week_start, week_end, shift_types, care_units, 'SCA'
                )
                
        if shifts_added > 0:
            self.stdout.write(f'ℹ️  Added {shifts_added} makeup shifts to meet minimum requirements')
            
        return shifts_added

    def _add_pattern_makeup_shifts(self, staff, needed_count, week_start, week_end, shift_types, care_units, role_type, week_number):
        """Add makeup shifts that respect the 3-week rotation pattern"""
        shifts_added = 0
        
        # Get the team's working days for this week
        def get_team_working_days_local(team, week_number, worker_type, shift_period='day'):
            pattern_week = ((week_number - 1) % 3) + 1
            
            if shift_period == 'night':
                if worker_type == 'SCA':
                    return self.night_sca_patterns[pattern_week][team]
                else:  # SCW/SSCW night shifts
                    return self.night_scw_patterns[pattern_week][team]
            else:  # day shifts (default)
                if worker_type == 'SCA':
                    return self.sca_patterns[pattern_week][team]
                else:  # SCW/SSCW day shifts
                    return self.scw_patterns[pattern_week][team]
        
        # Determine the shift period based on staff preference
        if role_type == 'SCW' and staff.shift_preference == 'NIGHT_SENIOR':
            shift_period = 'night'
        elif role_type == 'SCA' and staff.shift_preference == 'NIGHT_ASSISTANT':
            shift_period = 'night'
        else:
            shift_period = 'day'
        
        team_working_days = get_team_working_days_local(staff.team, week_number, role_type, shift_period)
        
        # Determine shift type based on role and preference
        if role_type == 'SCW':
            if staff.shift_preference == 'NIGHT_SENIOR':
                shift_type = shift_types['NIGHT_SENIOR']
            else:
                shift_type = shift_types['DAY_SENIOR']
        else:  # SCA
            if staff.shift_preference == 'NIGHT_ASSISTANT':
                shift_type = shift_types['NIGHT_ASSISTANT']
            else:
                shift_type = shift_types['DAY_ASSISTANT']
        
        # Only add shifts on days when the team is supposed to work
        for day_offset in range(7):
            if shifts_added >= needed_count:
                break
                
            current_date = week_start + timedelta(days=day_offset)
            day_of_week = (current_date.weekday() + 1) % 7  # Convert to 0=Sunday format
            
            # Check if this day is in the team's working pattern
            if day_of_week not in team_working_days:
                continue
                
            # For SCA, skip Wednesdays (day 3)
            if role_type == 'SCA' and day_of_week == 3:
                continue
            
            # Check if staff already has a shift on this day
            existing_shift = Shift.objects.filter(
                user=staff,
                date=current_date
            ).exists()
            
            if not existing_shift:
                # Add a makeup shift - use their home unit if available, otherwise first care unit
                unit = staff.unit if staff.unit and staff.unit in care_units else (care_units[0] if care_units else Unit.objects.filter(is_active=True).first())
                
                if unit:  # Only create if we have a valid unit
                    Shift.objects.create(
                        user=staff,
                        unit=unit,
                        shift_type=shift_type,
                        date=current_date,
                        status='SCHEDULED',
                    )
                    shifts_added += 1
                    
        return shifts_added
        
    def _add_makeup_shifts(self, staff, needed_count, week_start, week_end, shift_types, care_units, staff_type):
        """Add makeup shifts for staff who are under their minimum"""
        shifts_added = 0
        
        # Determine appropriate shift type based on staff preference and type
        if staff_type == 'SCW':
            # Check if preference contains 'DAY' or default to day shifts
            if staff.shift_preference and 'DAY' in staff.shift_preference:
                shift_type = shift_types['DAY_SENIOR']
            elif staff.shift_preference and 'NIGHT' in staff.shift_preference:
                shift_type = shift_types['NIGHT_SENIOR']
            else:
                shift_type = shift_types['DAY_SENIOR']  # Default to day
        else:  # SCA
            if staff.shift_preference and 'DAY' in staff.shift_preference:
                shift_type = shift_types['DAY_ASSISTANT']  
            elif staff.shift_preference and 'NIGHT' in staff.shift_preference:
                shift_type = shift_types['NIGHT_ASSISTANT']
            else:
                shift_type = shift_types['DAY_ASSISTANT']  # Default to day
        
        # Find available days in the week for this staff member
        for day_offset in range(7):
            if shifts_added >= needed_count:
                break
                
            current_date = week_start + timedelta(days=day_offset)
            
            # Check if staff already has a shift on this day
            existing_shift = Shift.objects.filter(
                user=staff,
                date=current_date
            ).exists()
            
            if not existing_shift:
                # Add a makeup shift - use their home unit if available, otherwise first care unit
                unit = staff.unit if staff.unit and staff.unit in care_units else (care_units[0] if care_units else Unit.objects.filter(is_active=True).first())
                
                if unit:  # Only create if we have a valid unit
                    Shift.objects.create(
                        user=staff,
                        unit=unit,
                        shift_type=shift_type,
                        date=current_date,
                        status='SCHEDULED',
                    )
                    shifts_added += 1
                    
        return shifts_added

    # ------------------------------------------------------------------
    # 6-Pattern rotation methods
    # ------------------------------------------------------------------

    def _assign_team_supernumerary(
        self,
        current_date,
        period,
        shift_type,
        weekly_shift_counts,
        busy_today,
        unit,
        pool,
        required_count=1,
        team=None
    ):
        """Assign SSCW supervision for a specific team"""
        if not pool:
            return 0

        assigned = 0
        
        # Convert deque to list for easier iteration
        pool_list = list(pool)
        
        for staff in pool_list:
            if assigned >= required_count:
                break
                
            if weekly_shift_counts[staff.sap] < 3 and staff.sap not in busy_today:
                Shift.objects.create(
                    user=staff,
                    unit=unit,
                    shift_type=shift_type,
                    date=current_date,
                    status='SCHEDULED',
                )
                weekly_shift_counts[staff.sap] += 1
                busy_today.add(staff.sap)
                assigned += 1

        return assigned

    def _assign_sscw_managers(
        self,
        current_date,
        period,
        working_teams,
        week_number,
        team_sscw_pools,
        weekly_shift_counts,
        busy_today,
        shift_type,
        care_units,
    ):
        """Assign SSCW to specific units based on the management structure"""
        shifts_created = 0
        day_of_week = (current_date.weekday() + 1) % 7  # Convert to 0=Sunday format
        
        # Get the pattern week (1, 2, or 3)
        pattern_week = ((week_number - 1) % 3) + 1
        
        for team in working_teams:
            # Check if this team should be working today based on SCW patterns
            if period == 'day':
                team_days = self.scw_patterns[pattern_week][team]
            else:
                team_days = self.night_scw_patterns[pattern_week][team]
            
            if day_of_week not in team_days:
                continue  # This team is not working today
            
            # Get SSCW assignments for this team and period
            team_assignments = self.sscw_unit_assignments[period].get(team, [])
            
            for unit_name, preferred_sap in team_assignments:
                # Find the unit object
                unit = None
                for care_unit in care_units:
                    if care_unit.name.upper() == unit_name.upper():
                        unit = care_unit
                        break
                
                if not unit:
                    continue
                
                # Get the team's SSCW pool
                team_pool = team_sscw_pools.get(team, [])
                if not team_pool:
                    continue
                
                # Try to assign the preferred SSCW first, then any available SSCW from the team
                assigned = False
                
                # Check if preferred SSCW is available
                for staff in team_pool:
                    if (staff.sap == preferred_sap and 
                        weekly_shift_counts[staff.sap] < 3 and 
                        staff.sap not in busy_today):
                        
                        # Check if this is an admin day (Tuesday for most SSCW)
                        is_admin_day = day_of_week == 2  # Tuesday = 2
                        
                        if is_admin_day and period == 'day':
                            # Skip admin assignment for now, handle regular unit duty
                            pass
                        
                        # Assign to their managed unit
                        Shift.objects.create(
                            user=staff,
                            unit=unit,
                            shift_type=shift_type,
                            date=current_date,
                            status='SCHEDULED',
                        )
                        
                        weekly_shift_counts[staff.sap] += 1
                        busy_today.add(staff.sap)
                        shifts_created += 1
                        assigned = True
                        break
                
                # If preferred SSCW not available, try any available SSCW from the team
                if not assigned:
                    for staff in team_pool:
                        if (weekly_shift_counts[staff.sap] < 3 and 
                            staff.sap not in busy_today):
                            
                            Shift.objects.create(
                                user=staff,
                                unit=unit,
                                shift_type=shift_type,
                                date=current_date,
                                status='SCHEDULED',
                            )
                            
                            weekly_shift_counts[staff.sap] += 1
                            busy_today.add(staff.sap)
                            shifts_created += 1
                            assigned = True
                            break
        
        return shifts_created

    def _assign_day_based_coverage(
        self,
        current_date,
        period,
        units,
        working_teams,
        week_number,
        scw_staff,
        sca_staff,
        weekly_shift_counts,
        busy_today,
        shift_types,
    ):
        """Assign unit coverage based on dedicated team-unit allocation"""
        scw_shift_key = 'DAY_SENIOR' if period == 'day' else 'NIGHT_SENIOR'
        sca_shift_key = 'DAY_ASSISTANT' if period == 'day' else 'NIGHT_ASSISTANT'
        shifts_created = 0
        
        day_of_week = (current_date.weekday() + 1) % 7  # Convert to 0=Sunday format
        
        # Check if SCA should work today for DAY shifts (not Wednesdays for day shifts only)
        sca_working_day_today = day_of_week != 3 if period == 'day' else True  # Wednesday = 3, but night shifts always work
        
        for unit in units:
            requirements = self._unit_requirements(unit)[period]
            
            # Get priority-ordered teams for this unit
            unit_teams_priority = self.unit_team_allocation[period].get(unit.name.upper(), ['A', 'B', 'C'])
            
            # Select working teams in priority order (prefer first 2, but use 3rd if needed)
            active_teams = []
            for team in unit_teams_priority:
                if team in working_teams:
                    active_teams.append(team)
                    if len(active_teams) >= 2:  # Prefer top 2 teams when possible
                        break
            
            # If we still don't have enough active teams, use any remaining working teams
            if len(active_teams) < 2:
                for team in working_teams:
                    if team not in active_teams:
                        active_teams.append(team)
                        if len(active_teams) >= 2:
                            break
            
            if not active_teams:
                # Fallback: use any available team from working teams
                active_teams = working_teams[:1] if working_teams else []
            
            if not active_teams:
                self.stderr.write(
                    self.style.WARNING(
                        f'⚠️  {current_date} {period.upper()} {unit.name}: no teams working today'
                    )
                )
                continue
            
            # Track assignments for this unit
            unit_scw_assigned = 0
            unit_sca_assigned = 0
            
            # Distribute required staff across active teams for this unit
            num_active_teams = len(active_teams)
            
            for team_idx, team in enumerate(active_teams):
                # Get team-specific staff
                team_scw = [s for s in scw_staff if s.team == team]
                team_sca = [s for s in sca_staff if s.team == team]
                
                # Calculate how many SCW from this team should work this unit
                base_scw_per_team = requirements['SCW'] // num_active_teams
                extra_scw = 1 if team_idx < (requirements['SCW'] % num_active_teams) else 0
                team_scw_target = base_scw_per_team + extra_scw
                
                # Calculate SCA target based on patterns and day rules
                team_sca_target = 0
                if period == 'day':
                    # For day shifts: check Wednesday rule AND team patterns
                    if sca_working_day_today:
                        # Check if this team's SCA should work today
                        pattern_week = ((week_number - 1) % 3) + 1
                        sca_days = self.sca_patterns[pattern_week][team]
                        if day_of_week in sca_days:
                            base_sca_per_team = requirements['SCA'] // num_active_teams
                            extra_sca = 1 if team_idx < (requirements['SCA'] % num_active_teams) else 0
                            team_sca_target = base_sca_per_team + extra_sca
                else:
                    # For night shifts: use night-specific SCA patterns
                    pattern_week = ((week_number - 1) % 3) + 1
                    night_sca_days = self.night_sca_patterns[pattern_week][team]
                    if day_of_week in night_sca_days:
                        base_sca_per_team = requirements['SCA'] // num_active_teams
                        extra_sca = 1 if team_idx < (requirements['SCA'] % num_active_teams) else 0
                        team_sca_target = base_sca_per_team + extra_sca
                
                # Assign SCW from this team
                scw_available = [
                    staff for staff in team_scw
                    if weekly_shift_counts[staff.sap] < 3 and staff.sap not in busy_today
                ]
                scw_available.sort(key=lambda x: weekly_shift_counts[x.sap])
                
                team_scw_assigned = min(team_scw_target, len(scw_available))
                for i in range(team_scw_assigned):
                    staff = scw_available[i]
                    Shift.objects.create(
                        user=staff,
                        unit=unit,
                        shift_type=shift_types[scw_shift_key],
                        date=current_date,
                        status='SCHEDULED',
                    )
                    weekly_shift_counts[staff.sap] += 1
                    busy_today.add(staff.sap)
                    shifts_created += 1
                    unit_scw_assigned += 1
                
                # Assign SCA from this team (with 6-week pattern logic for day shifts)
                if period == 'day':
                    # Use 6-week pattern for day SCA
                    sca_available = [
                        staff for staff in team_sca
                        if staff.sap not in busy_today
                    ]
                    
                    # Apply 6-week pattern filter
                    pattern_sca = []
                    for staff in sca_available:
                        if hasattr(self, 'start_date'):
                            # Use the team SCA staff list index for pattern calculation
                            team_sca_index = team_sca.index(staff) if staff in team_sca else 0
                            if self._get_sca_day_pattern_schedule(team_sca_index, current_date, self.start_date):
                                pattern_sca.append(staff)
                    
                    team_sca_assigned = min(team_sca_target, len(pattern_sca))
                    selected_sca = pattern_sca[:team_sca_assigned]
                else:
                    # Night shifts: use existing logic
                    sca_available = [
                        staff for staff in team_sca
                        if weekly_shift_counts[staff.sap] < 2 and staff.sap not in busy_today
                    ]
                    sca_available.sort(key=lambda x: weekly_shift_counts[x.sap])
                    
                    team_sca_assigned = min(team_sca_target, len(sca_available))
                    selected_sca = sca_available[:team_sca_assigned]
                
                for staff in selected_sca:
                    Shift.objects.create(
                        user=staff,
                        unit=unit,
                        shift_type=shift_types[sca_shift_key],
                        date=current_date,
                        status='SCHEDULED',
                    )
                    weekly_shift_counts[staff.sap] += 1
                    busy_today.add(staff.sap)
                    shifts_created += 1
                    unit_sca_assigned += 1
            
            # Check for shortfalls and try to fill with pattern-compliant makeup shifts
            scw_shortfall = requirements['SCW'] - unit_scw_assigned
            sca_shortfall = requirements['SCA'] - unit_sca_assigned
            
            # Try to fill SCW shortfalls with available staff from any team
            if scw_shortfall > 0:
                all_available_scw = [
                    staff for staff in scw_staff
                    if weekly_shift_counts[staff.sap] < 3 and staff.sap not in busy_today
                ]
                all_available_scw.sort(key=lambda x: weekly_shift_counts[x.sap])
                
                filled_scw = min(scw_shortfall, len(all_available_scw))
                for i in range(filled_scw):
                    staff = all_available_scw[i]
                    Shift.objects.create(
                        user=staff,
                        unit=unit,
                        shift_type=shift_types[scw_shift_key],
                        date=current_date,
                        status='SCHEDULED',
                    )
                    weekly_shift_counts[staff.sap] += 1
                    busy_today.add(staff.sap)
                    shifts_created += 1
                    unit_scw_assigned += 1
                
                remaining_scw_shortfall = scw_shortfall - filled_scw
                if remaining_scw_shortfall > 0:
                    self.stderr.write(
                        self.style.WARNING(
                            f'⚠️  {current_date} {period.upper()} {unit.name}: missing {remaining_scw_shortfall} SCW'
                        )
                    )
            
            # Try to fill SCA shortfalls with pattern-compliant staff
            if sca_shortfall > 0:
                if period == 'day':
                    # For day shifts: use 6-week pattern
                    all_available_sca = [
                        staff for staff in sca_staff
                        if staff.sap not in busy_today
                    ]
                    
                    # Apply 6-week pattern filter
                    pattern_available_sca = []
                    for staff in all_available_sca:
                        if hasattr(self, 'start_date'):
                            staff_index = sca_staff.index(staff) if staff in sca_staff else 0
                            if self._get_sca_day_pattern_schedule(staff_index, current_date, self.start_date):
                                pattern_available_sca.append(staff)
                    
                    filled_sca = min(sca_shortfall, len(pattern_available_sca))
                    for i in range(filled_sca):
                        staff = pattern_available_sca[i]
                        Shift.objects.create(
                            user=staff,
                            unit=unit,
                            shift_type=shift_types[sca_shift_key],
                            date=current_date,
                            status='SCHEDULED',
                        )
                        weekly_shift_counts[staff.sap] += 1
                        busy_today.add(staff.sap)
                        shifts_created += 1
                        unit_sca_assigned += 1
                else:
                    # For night shifts: use available staff with <2 shifts
                    all_available_sca = [
                        staff for staff in sca_staff
                        if weekly_shift_counts[staff.sap] < 2 and staff.sap not in busy_today
                    ]
                    all_available_sca.sort(key=lambda x: weekly_shift_counts[x.sap])
                    
                    filled_sca = min(sca_shortfall, len(all_available_sca))
                    for i in range(filled_sca):
                        staff = all_available_sca[i]
                        Shift.objects.create(
                            user=staff,
                            unit=unit,
                            shift_type=shift_types[sca_shift_key],
                            date=current_date,
                            status='SCHEDULED',
                        )
                        weekly_shift_counts[staff.sap] += 1
                        busy_today.add(staff.sap)
                        shifts_created += 1
                        unit_sca_assigned += 1
                
                remaining_sca_shortfall = requirements['SCA'] - unit_sca_assigned
                if remaining_sca_shortfall > 0:
                    self.stderr.write(
                        self.style.WARNING(
                            f'⚠️  {current_date} {period.upper()} {unit.name}: missing {remaining_sca_shortfall} SCA'
                        )
                    )

        return shifts_created

    def _assign_supernumerary_team(
        self,
        current_date,
        period,
        shift_type,
        weekly_shift_counts,
        busy_today,
        unit,
        pool,
        required_count=1,
    ):
        """Team-based version of _assign_supernumerary - uses all available team SSCW"""
        if not pool:
            return 0

        assigned = 0
        
        # Convert deque to list for easier iteration
        pool_list = list(pool)
        
        for staff in pool_list:
            if assigned >= required_count:
                break
                
            if weekly_shift_counts[staff.sap] < 3 and staff.sap not in busy_today:
                Shift.objects.create(
                    user=staff,
                    unit=unit,
                    shift_type=shift_type,
                    date=current_date,
                    status='SCHEDULED',
                )
                weekly_shift_counts[staff.sap] += 1
                busy_today.add(staff.sap)
                assigned += 1

        return assigned

    def _assign_unit_period_team(
        self,
        current_date,
        period,
        units,
        scw_staff,
        sca_staff,
        weekly_shift_counts,
        busy_today,
        shift_types,
    ):
        """Team-based version of _assign_unit_period - only uses active team staff"""
        scw_shift_key = 'DAY_SENIOR' if period == 'day' else 'NIGHT_SENIOR'
        sca_shift_key = 'DAY_ASSISTANT' if period == 'day' else 'NIGHT_ASSISTANT'
        shifts_created = 0

        for unit in units:
            requirements = self._unit_requirements(unit)[period]

            # Allocate SCWs first - prioritize those with fewer shifts this week.
            scw_available = [
                staff for staff in scw_staff
                if weekly_shift_counts[staff.sap] < 3 and staff.sap not in busy_today
            ]
            # Sort by current shift count (ascending) to prioritize those with fewer shifts
            scw_available.sort(key=lambda x: weekly_shift_counts[x.sap])

            selected_scw = scw_available[:requirements['SCW']]
            scw_shortfall = requirements['SCW'] - len(selected_scw)

            for staff in selected_scw:
                Shift.objects.create(
                    user=staff,
                    unit=unit,
                    shift_type=shift_types[scw_shift_key],
                    date=current_date,
                    status='SCHEDULED',
                )
                weekly_shift_counts[staff.sap] += 1
                busy_today.add(staff.sap)
                shifts_created += 1

            # For day shifts, use 6-week SCA pattern; for nights use existing logic
            if period == 'day':
                # Get all SCA staff for this unit (not busy today)
                sca_available = [
                    staff for staff in sca_staff
                    if staff.sap not in busy_today
                ]
                
                # Filter SCA based on 6-week pattern schedule
                pattern_sca = []
                for staff in sca_available:
                    staff_index = sca_staff.index(staff)
                    if self._get_sca_day_pattern_schedule(staff_index, current_date, self.start_date):
                        pattern_sca.append(staff)
                
                # Select required number of SCA
                selected_sca = pattern_sca[:requirements['SCA']]
                
            else:
                # Night shifts: use existing logic - prioritize those with fewer shifts this week
                sca_available = [
                    staff for staff in sca_staff
                    if weekly_shift_counts[staff.sap] < 2 and staff.sap not in busy_today
                ]
                # Sort by current shift count (ascending) to prioritize those with fewer shifts
                sca_available.sort(key=lambda x: weekly_shift_counts[x.sap])
                selected_sca = sca_available[:requirements['SCA']]

            # Handle SCW shortfall by using SCA as cover
            cover_count = 0
            if scw_shortfall > 0:
                # For day shifts, get pattern-based SCA for cover; for nights use existing logic
                if period == 'day':
                    sca_for_cover = [
                        staff for staff in sca_staff
                        if staff.sap not in busy_today and staff not in selected_sca
                    ]
                    # Apply pattern filter for day cover
                    pattern_cover_sca = []
                    for staff in sca_for_cover:
                        staff_index = sca_staff.index(staff)
                        if self._get_sca_day_pattern_schedule(staff_index, current_date, self.start_date):
                            pattern_cover_sca.append(staff)
                    
                    cover_count = min(scw_shortfall, len(pattern_cover_sca))
                    sca_cover = pattern_cover_sca[:cover_count]
                else:
                    # Night shifts: use existing logic
                    sca_for_cover = [
                        staff for staff in sca_staff
                        if weekly_shift_counts[staff.sap] < 2 and staff.sap not in busy_today
                    ]
                    cover_count = min(scw_shortfall, len(sca_for_cover))
                    sca_cover = sca_for_cover[:cover_count]
                
                for staff in sca_cover:
                    Shift.objects.create(
                        user=staff,
                        unit=unit,
                        shift_type=shift_types[scw_shift_key],
                        date=current_date,
                        status='SCHEDULED',
                    )
                    weekly_shift_counts[staff.sap] += 1
                    busy_today.add(staff.sap)
                    shifts_created += 1
                
                if cover_count > 0:
                    self.stdout.write(
                        f'ℹ️  {current_date} {period.upper()} {unit.name}: used {cover_count} SCA to backfill SCW duty.'
                    )

            if scw_shortfall - cover_count > 0:
                self.stderr.write(
                    self.style.WARNING(
                        f'⚠️  {current_date} {period.upper()} {unit.name}: missing {scw_shortfall - cover_count} SCW'
                    )
                )

            # Check if we have enough SCA for the unit requirements
            if len(selected_sca) < requirements['SCA']:
                self.stderr.write(
                    self.style.WARNING(
                        f'⚠️  {current_date} {period.upper()} {unit.name}: missing {requirements["SCA"] - len(selected_sca)} SCA'
                    )
                )

            for staff in selected_sca:
                Shift.objects.create(
                    user=staff,
                    unit=unit,
                    shift_type=shift_types[sca_shift_key],
                    date=current_date,
                    status='SCHEDULED',
                )
                weekly_shift_counts[staff.sap] += 1
                busy_today.add(staff.sap)
                shifts_created += 1

        return shifts_created

    def _ensure_minimum_shifts_team(self, week_start, scw_staff, sca_staff, weekly_shift_counts, shift_types, care_units):
        """Team-based version of _ensure_minimum_shifts - respects 3-week rotation pattern"""
        shifts_added = 0
        week_end = week_start + timedelta(days=6)
        
        # Calculate which week we're in for pattern matching
        weeks_since_start = (week_start - self.start_date).days // 7 + 1
        
        # Check SCW staff (3 shifts minimum) - only add on their designated days
        for staff in scw_staff:
            current_count = weekly_shift_counts[staff.sap]
            if current_count < 3:
                needed = 3 - current_count
                added = self._add_pattern_makeup_shifts(staff, needed, week_start, week_end, shift_types, care_units, 'SCW', weeks_since_start)
                shifts_added += added
                weekly_shift_counts[staff.sap] += added
                
        # Check SCA staff (2 shifts minimum) - only add on their designated days  
        for staff in sca_staff:
            current_count = weekly_shift_counts[staff.sap]
            if current_count < 2:
                needed = 2 - current_count
                added = self._add_pattern_makeup_shifts(staff, needed, week_start, week_end, shift_types, care_units, 'SCA', weeks_since_start)
                shifts_added += added
                weekly_shift_counts[staff.sap] += added
                
        if shifts_added > 0:
            self.stdout.write(f'ℹ️  Added {shifts_added} pattern-compliant makeup shifts to meet minimum requirements')
            
        return shifts_added