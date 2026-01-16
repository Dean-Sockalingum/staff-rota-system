from django.core.management.base import BaseCommand
from django.db import transaction
from scheduling.models import User, Shift, ShiftType, Unit
from datetime import date, timedelta
import random
from collections import defaultdict


class Command(BaseCommand):
    help = 'Fix team balance and implement proper 3-team staggered rotation with 2-3 shifts per person per week'

    def add_arguments(self, parser):
        parser.add_argument(
            '--start-date',
            type=str,
            default='2025-10-13',
            help='Start date for the roster (YYYY-MM-DD format)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes'
        )

    def handle(self, *args, **options):
        start_date = date.fromisoformat(options['start_date'])
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.SUCCESS('🔧 IMPLEMENTING STAGGERED 3-TEAM ROTATION SYSTEM'))
        self.stdout.write('=' * 60)
        
        with transaction.atomic():
            # Step 1: Rebalance teams
            self.rebalance_teams(dry_run)
            
            # Step 2: Clear existing shifts
            if not dry_run:
                self.clear_shifts(start_date)
            
                        # Step 3: Generate proper staggered rotation roster
            self.generate_staggered_rotation_roster(start_date, dry_run)
            
        if dry_run:
            self.stdout.write(self.style.WARNING('\n🔍 DRY RUN - No changes made'))
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ Staggered team rotation implemented!'))

    def rebalance_teams(self, dry_run):
        """Rebalance teams to have equal distribution (exclude SSCW - they have fixed assignments)"""
        self.stdout.write('\n📊 REBALANCING TEAMS')
        self.stdout.write('-' * 30)
        
        # Get all active care staff (exclude SSCW as they have fixed unit assignments)
        all_staff = list(User.objects.filter(
            role__name__in=['SCW', 'SCA'],  # Exclude SSCW
            is_active=True,
            team__in=['A', 'B', 'C']
        ).order_by('sap'))
        
        # Separate by shift preference
        day_staff = [s for s in all_staff if s.shift_preference in ['DAY_SENIOR', 'DAY_ASSISTANT']]
        night_staff = [s for s in all_staff if s.shift_preference in ['NIGHT_SENIOR', 'NIGHT_ASSISTANT']]
        
        self.stdout.write(f'Staff to rebalance: {len(all_staff)} ({len(day_staff)} day, {len(night_staff)} night)')
        self.stdout.write('Note: SSCW excluded from rebalancing (fixed unit assignments)')
        
        # Calculate target sizes
        day_per_team = len(day_staff) // 3
        night_per_team = len(night_staff) // 3
        
        self.stdout.write(f'Target per team: {day_per_team} day staff, {night_per_team} night staff')
        
        # Randomly shuffle and assign to teams
        random.shuffle(day_staff)
        random.shuffle(night_staff)
        
        team_assignments = {'A': [], 'B': [], 'C': []}
        
        # Assign day staff
        for i, staff in enumerate(day_staff):
            team = ['A', 'B', 'C'][i % 3]
            team_assignments[team].append(staff)
            if not dry_run:
                staff.team = team
                staff.save()
        
        # Assign night staff
        for i, staff in enumerate(night_staff):
            team = ['A', 'B', 'C'][i % 3]
            team_assignments[team].append(staff)
            if not dry_run:
                staff.team = team
                staff.save()
        
        # Report new distribution
        for team in ['A', 'B', 'C']:
            team_staff = team_assignments[team]
            day_count = len([s for s in team_staff if s.shift_preference in ['DAY_SENIOR', 'DAY_ASSISTANT']])
            night_count = len([s for s in team_staff if s.shift_preference in ['NIGHT_SENIOR', 'NIGHT_ASSISTANT']])
            total = len(team_staff)
            
            # Add SSCW counts to the totals
            sscw_day = User.objects.filter(role__name='SSCW', team=team, shift_preference='DAY_SENIOR', is_active=True).count()
            sscw_night = User.objects.filter(role__name='SSCW', team=team, shift_preference='NIGHT_SENIOR', is_active=True).count()
            
            self.stdout.write(f'Team {team}: {total + sscw_day + sscw_night} staff ({day_count + sscw_day} day, {night_count + sscw_night} night)')
        
        # Ensure SSCW have correct distribution
        if not dry_run:
            self.fix_sscw_distribution()

    def fix_sscw_distribution(self):
        """Ensure SSCW are distributed correctly: Day=3 per team, Night=A&B=3, C=2"""
        self.stdout.write('\n🔧 FIXING SSCW DISTRIBUTION')
        self.stdout.write('-' * 30)
        
        # Get all SSCW and redistribute properly
        all_day_sscw = list(User.objects.filter(
            role__name='SSCW',
            shift_preference='DAY_SENIOR',
            is_active=True
        ).order_by('sap'))

        all_night_sscw = list(User.objects.filter(
            role__name='SSCW',
            shift_preference='NIGHT_SENIOR',
            is_active=True
        ).order_by('sap'))

        # Redistribute day SSCW: exactly 3 per team
        for i, sscw in enumerate(all_day_sscw):
            team = ['A', 'B', 'C'][i % 3]
            sscw.team = team
            sscw.save()

        # Redistribute night SSCW: A=3, B=3, C=2
        night_team_pattern = ['A', 'A', 'A', 'B', 'B', 'B', 'C', 'C']
        for i, sscw in enumerate(all_night_sscw):
            team = night_team_pattern[i] if i < len(night_team_pattern) else 'C'
            sscw.team = team
            sscw.save()
        
        self.stdout.write(f'Fixed distribution: {len(all_day_sscw)} day SSCW, {len(all_night_sscw)} night SSCW')

    def clear_shifts(self, start_date):
        """Clear existing shifts from start date onwards"""
        self.stdout.write('\n🗑️ CLEARING EXISTING SHIFTS')
        self.stdout.write('-' * 30)
        
        end_date = start_date + timedelta(weeks=6, days=-1)
        shifts_deleted = Shift.objects.filter(date__range=[start_date, end_date]).count()
        Shift.objects.filter(date__range=[start_date, end_date]).delete()
        self.stdout.write(f'Deleted {shifts_deleted} shifts from {start_date} to {end_date}')

    def generate_staggered_rotation_roster(self, start_date, dry_run):
        """Generate 6-week staggered rotation roster where all teams work every week"""
        self.stdout.write('\n🔄 GENERATING STAGGERED ROTATION ROSTER')
        self.stdout.write('-' * 40)
        
        # Get shift types and units
        shift_types = {
            'DAY_SENIOR': ShiftType.objects.get(name='DAY_SENIOR'),
            'DAY_ASSISTANT': ShiftType.objects.get(name='DAY_ASSISTANT'),
            'NIGHT_SENIOR': ShiftType.objects.get(name='NIGHT_SENIOR'),
            'NIGHT_ASSISTANT': ShiftType.objects.get(name='NIGHT_ASSISTANT'),
        }
        
        care_units = list(Unit.objects.filter(
            name__in=['BLUE', 'DEMENTIA', 'GRAPE', 'GREEN', 'ORANGE', 'PEACH', 'ROSE', 'VIOLET']
        ))
        
        # Unit to SSCW assignments
        unit_sscw_assignments = {
            'DEMENTIA': {'day': 'A', 'night': 'A'},
            'BLUE': {'day': 'A', 'night': 'A'}, 
            'VIOLET': {'day': 'A', 'night': 'A'},
            'ROSE': {'day': 'B', 'night': 'B'},
            'GRAPE': {'day': 'B', 'night': 'B'},
            'PEACH': {'day': 'B', 'night': 'B'},
            'ORANGE': {'day': 'C', 'night': 'C'},
            'GREEN': {'day': 'C', 'night': 'C'},
        }
        
        # SSCW Day rotation patterns (3 SSCW per team, all teams work different days each week)
        sscw_day_patterns = {
            'A': {  # Team A pattern
                0: [0, 1],      # Week 1: Sun, Mon (Tue=Admin)
                1: [4, 5, 6],   # Week 2: Thu, Fri, Sat
                2: [2, 3],      # Week 3: Tue, Wed (Thu=Admin)
            },
            'B': {  # Team B pattern
                0: [4, 5, 6],   # Week 1: Thu, Fri, Sat
                1: [2, 3],      # Week 2: Tue, Wed (Thu=Admin)
                2: [0, 1],      # Week 3: Sun, Mon (Tue=Admin)
            },
            'C': {  # Team C pattern
                0: [2, 3],      # Week 1: Tue, Wed (Thu=Admin)
                1: [0, 1],      # Week 2: Sun, Mon (Tue=Admin)
                2: [4, 5, 6],   # Week 3: Thu, Fri, Sat
            }
        }
        
        # SSCW Night rotation patterns (8 night SSCW total: Teams A&B have 3 each, Team C has 2)
        sscw_night_patterns = {
            'A': {  # Team A night pattern (3 SSCW)
                0: [0, 1],      # Week 1: Sun, Mon (Tue=Admin)
                1: [4, 5, 6],   # Week 2: Thu, Fri, Sat
                2: [2, 3],      # Week 3: Tue, Wed (Thu=Admin)
            },
            'B': {  # Team B night pattern (3 SSCW)
                0: [4, 5, 6],   # Week 1: Thu, Fri, Sat
                1: [2, 3],      # Week 2: Tue, Wed (Thu=Admin)
                2: [0, 1],      # Week 3: Sun, Mon (Tue=Admin)
            },
            'C': {  # Team C night pattern (2 SSCW only)
                0: [2, 3],      # Week 1: Tue, Wed (Thu=Admin)
                1: [0, 1],      # Week 2: Sun, Mon (Tue=Admin)
                2: [4, 5, 6],   # Week 3: Thu, Fri, Sat
            }
        }
        
        # Regular staff patterns
        # 3-shift day patterns (SCW)
        day_3shift_patterns = {
            'A': {  # Sunday + Monday + Tuesday pattern
                0: [0, 1, 2],   # Week 1: Sun, Mon, Tue
                1: [4, 5, 6],   # Week 2: Thu, Fri, Sat  
                2: [2, 3, 4],   # Week 3: Tue, Wed, Thu
            },
            'B': {  # Thursday + Friday + Saturday pattern
                0: [4, 5, 6],   # Week 1: Thu, Fri, Sat
                1: [2, 3, 4],   # Week 2: Tue, Wed, Thu
                2: [0, 1, 2],   # Week 3: Sun, Mon, Tue
            },
            'C': {  # Tuesday + Wednesday + Thursday pattern
                0: [2, 3, 4],   # Week 1: Tue, Wed, Thu
                1: [0, 1, 2],   # Week 2: Sun, Mon, Tue
                2: [4, 5, 6],   # Week 3: Thu, Fri, Sat
            }
        }
        
        # 2-shift day patterns (SCA)
        day_2shift_patterns = {
            'A': {  # Sunday + Thursday pattern
                0: [0, 4],      # Week 1: Sun, Thu
                1: [1, 2],      # Week 2: Mon, Tue
                2: [5, 6],      # Week 3: Fri, Sat
            },
            'B': {  # Monday + Tuesday pattern
                0: [1, 2],      # Week 1: Mon, Tue
                1: [5, 6],      # Week 2: Fri, Sat
                2: [0, 4],      # Week 3: Sun, Thu
            },
            'C': {  # Friday + Saturday pattern
                0: [5, 6],      # Week 1: Fri, Sat
                1: [0, 4],      # Week 2: Sun, Thu
                2: [1, 2],      # Week 3: Mon, Tue
            }
        }
        
        # 3-shift night patterns (SCW) 
        night_3shift_patterns = {
            'A': {  # Sunday + Monday + Tuesday pattern
                0: [0, 1, 2],   # Week 1: Sun, Mon, Tue
                1: [4, 5, 6],   # Week 2: Thu, Fri, Sat
                2: [2, 3, 4],   # Week 3: Tue, Wed, Thu
            },
            'B': {  # Thursday + Friday + Saturday pattern
                0: [4, 5, 6],   # Week 1: Thu, Fri, Sat
                1: [2, 3, 4],   # Week 2: Tue, Wed, Thu
                2: [0, 1, 2],   # Week 3: Sun, Mon, Tue
            },
            'C': {  # Tuesday + Wednesday + Thursday pattern
                0: [2, 3, 4],   # Week 1: Tue, Wed, Thu
                1: [0, 1, 2],   # Week 2: Sun, Mon, Tue
                2: [4, 5, 6],   # Week 3: Thu, Fri, Sat
            }
        }
        
        # 2-shift night patterns (SCA)
        night_2shift_patterns = {
            'A': {  # Friday + Saturday pattern
                0: [5, 6],      # Week 1: Fri, Sat
                1: [2, 3],      # Week 2: Tue, Wed
                2: [0, 1],      # Week 3: Sun, Mon
            },
            'B': {  # Tuesday + Wednesday pattern
                0: [2, 3],      # Week 1: Tue, Wed
                1: [0, 1],      # Week 2: Sun, Mon
                2: [5, 6],      # Week 3: Fri, Sat
            },
            'C': {  # Sunday + Monday pattern
                0: [0, 1],      # Week 1: Sun, Mon
                1: [5, 6],      # Week 2: Fri, Sat
                2: [2, 3],      # Week 3: Tue, Wed
            }
        }
        
        if not dry_run:
            shifts_created = 0
            
            for week_num in range(6):
                week_start = start_date + timedelta(weeks=week_num)
                pattern_week = week_num % 3  # 3-week pattern
                
                self.stdout.write(f'Week {week_num + 1} (Pattern Week {pattern_week + 1}):')
                
                # Generate shifts for each day of the week
                for day_offset in range(7):
                    current_date = week_start + timedelta(days=day_offset)
                    day_of_week = day_offset  # 0=Sunday, 1=Monday, etc.
                    
                    # Create daily shifts for all units
                    shifts_created += self.create_staggered_daily_shifts(
                        current_date, day_of_week, pattern_week,
                        shift_types, care_units, unit_sscw_assignments,
                        sscw_day_patterns, sscw_night_patterns, 
                        day_3shift_patterns, day_2shift_patterns,
                        night_3shift_patterns, night_2shift_patterns
                    )
            
            self.stdout.write(f'Created {shifts_created} shifts over 6 weeks with staggered patterns')
        else:
            self.stdout.write('Would create staggered rotation patterns:')
            self.stdout.write('• All teams work every week in staggered patterns')
            self.stdout.write('• Day SSCW: 3 per team (9 total daily) - all teams work different days')
            self.stdout.write('• Night SSCW: Team A&B=3 each, Team C=2 (8 total nightly)')
            self.stdout.write('• SCW Day: 3 shifts (Sun+Mon+Tue / Thu+Fri+Sat / Tue+Wed+Thu patterns)')
            self.stdout.write('• SCW Night: 3 shifts (similar to day but night hours)')
            self.stdout.write('• SCA Day: 2 shifts (Sun+Thu / Mon+Tue / Fri+Sat patterns)')
            self.stdout.write('• SCA Night: 2 shifts (Fri+Sat / Tue+Wed / Sun+Mon patterns)')

    def create_staggered_daily_shifts(self, current_date, day_of_week, pattern_week,
                                    shift_types, care_units, unit_sscw_assignments,
                                    sscw_day_patterns, sscw_night_patterns,
                                    day_3shift_patterns, day_2shift_patterns,
                                    night_3shift_patterns, night_2shift_patterns):
        """Create shifts for a specific day following staggered patterns"""
        shifts_created = 0
        
        # Create SSCW shifts first (3 per team for day, night varies by team)
        # Day SSCW: All 3 teams work each day but on different patterns
        for team in ['A', 'B', 'C']:
            if day_of_week in sscw_day_patterns[team][pattern_week]:
                # Get ALL 3 day SSCW from this team
                day_sscw_list = list(User.objects.filter(
                    role__name='SSCW',
                    team=team,
                    shift_preference='DAY_SENIOR',
                    is_active=True
                ))
                
                # Get units assigned to this team
                team_units = [unit for unit in care_units 
                            if unit_sscw_assignments[unit.name]['day'] == team]
                
                # Assign ALL 3 SSCW (cycle through units if needed)
                for i, sscw in enumerate(day_sscw_list):
                    # Cycle through available units
                    unit = team_units[i % len(team_units)] if team_units else care_units[0]
                    
                    if not Shift.objects.filter(
                        user=sscw, date=current_date, shift_type=shift_types['DAY_SENIOR']
                    ).exists():
                        Shift.objects.create(
                            user=sscw,
                            date=current_date,
                            shift_type=shift_types['DAY_SENIOR'],
                            unit=unit
                        )
                        shifts_created += 1
        
        # Night SSCW: Teams A&B have 3 each, Team C has 2
        for team in ['A', 'B', 'C']:
            if day_of_week in sscw_night_patterns[team][pattern_week]:
                # All available night SSCW from this team
                night_sscw_list = list(User.objects.filter(
                    role__name='SSCW',
                    team=team,
                    shift_preference='NIGHT_SENIOR',
                    is_active=True
                ))
                
                # Get units assigned to this team for night
                team_units = [unit for unit in care_units 
                            if unit_sscw_assignments[unit.name]['night'] == team]
                
                # Assign ALL night SSCW from this team (cycle through units if needed)
                for i, sscw in enumerate(night_sscw_list):
                    # Cycle through available units
                    unit = team_units[i % len(team_units)] if team_units else care_units[0]
                    
                    if not Shift.objects.filter(
                        user=sscw, date=current_date, shift_type=shift_types['NIGHT_SENIOR']
                    ).exists():
                        Shift.objects.create(
                            user=sscw,
                            date=current_date,
                            shift_type=shift_types['NIGHT_SENIOR'],
                            unit=unit
                        )
                        shifts_created += 1
        
        # Now allocate SCW and SCA for all units
        for unit in care_units:
            unit_name = unit.name
            
            # Determine staffing requirements per unit
            if unit_name == 'DEMENTIA':
                day_scw_needed = 1
                day_sca_needed = 3
                night_scw_needed = 1
                night_sca_needed = 2
            else:
                day_scw_needed = 1
                day_sca_needed = 2
                night_scw_needed = 1
                night_sca_needed = 1
        
            # Day SCW and SCA shifts for each team
            for team in ['A', 'B', 'C']:
                # Day SCW (3-shift pattern)
                if day_of_week in day_3shift_patterns[team][pattern_week]:
                    available_scw = list(User.objects.filter(
                        role__name='SCW',
                        team=team,
                        shift_preference='DAY_SENIOR',
                        is_active=True
                    ).exclude(
                        sap__in=Shift.objects.filter(
                            date=current_date,
                            shift_type=shift_types['DAY_SENIOR']
                        ).values_list('user__sap', flat=True)
                    ))
                    
                    # Check if this unit still needs SCW
                    if not Shift.objects.filter(
                        date=current_date,
                        shift_type=shift_types['DAY_SENIOR'],
                        unit=unit,
                        user__role__name='SCW'
                    ).exists():
                        if available_scw:
                            Shift.objects.create(
                                user=available_scw[0],
                                date=current_date,
                                shift_type=shift_types['DAY_SENIOR'],
                                unit=unit
                            )
                            shifts_created += 1
                
                # Day SCA (2-shift pattern)
                if day_of_week in day_2shift_patterns[team][pattern_week]:
                    available_sca = list(User.objects.filter(
                        role__name='SCA',
                        team=team,
                        shift_preference='DAY_ASSISTANT',
                        is_active=True
                    ).exclude(
                        sap__in=Shift.objects.filter(
                            date=current_date,
                            shift_type=shift_types['DAY_ASSISTANT']
                        ).values_list('user__sap', flat=True)
                    ))
                    
                    # Allocate SCA to this unit if needed
                    current_sca_count = Shift.objects.filter(
                        date=current_date,
                        shift_type=shift_types['DAY_ASSISTANT'],
                        unit=unit,
                        user__role__name='SCA'
                    ).count()
                    
                    sca_still_needed = day_sca_needed - current_sca_count
                    allocated = 0
                    for _ in range(sca_still_needed):
                        if allocated < len(available_sca):
                            if not Shift.objects.filter(
                                user=available_sca[allocated], date=current_date, shift_type=shift_types['DAY_ASSISTANT']
                            ).exists():
                                Shift.objects.create(
                                    user=available_sca[allocated],
                                    date=current_date,
                                    shift_type=shift_types['DAY_ASSISTANT'],
                                    unit=unit
                                )
                                shifts_created += 1
                            allocated += 1
                
                # Night SCW (3-shift pattern)
                if day_of_week in night_3shift_patterns[team][pattern_week]:
                    available_night_scw = list(User.objects.filter(
                        role__name='SCW',
                        team=team,
                        shift_preference='NIGHT_SENIOR',
                        is_active=True
                    ).exclude(
                        sap__in=Shift.objects.filter(
                            date=current_date,
                            shift_type=shift_types['NIGHT_SENIOR']
                        ).values_list('user__sap', flat=True)
                    ))
                    
                    # Check if this unit still needs night SCW
                    if not Shift.objects.filter(
                        date=current_date,
                        shift_type=shift_types['NIGHT_SENIOR'],
                        unit=unit,
                        user__role__name='SCW'
                    ).exists():
                        if available_night_scw:
                            Shift.objects.create(
                                user=available_night_scw[0],
                                date=current_date,
                                shift_type=shift_types['NIGHT_SENIOR'],
                                unit=unit
                            )
                            shifts_created += 1
                
                # Night SCA (2-shift pattern)
                if day_of_week in night_2shift_patterns[team][pattern_week]:
                    available_night_sca = list(User.objects.filter(
                        role__name='SCA',
                        team=team,
                        shift_preference='NIGHT_ASSISTANT',
                        is_active=True
                    ).exclude(
                        sap__in=Shift.objects.filter(
                            date=current_date,
                            shift_type=shift_types['NIGHT_ASSISTANT']
                        ).values_list('user__sap', flat=True)
                    ))
                    
                    # Allocate night SCA to this unit if needed
                    current_night_sca_count = Shift.objects.filter(
                        date=current_date,
                        shift_type=shift_types['NIGHT_ASSISTANT'],
                        unit=unit,
                        user__role__name='SCA'
                    ).count()
                    
                    sca_still_needed = night_sca_needed - current_night_sca_count
                    allocated = 0
                    for _ in range(sca_still_needed):
                        if allocated < len(available_night_sca):
                            if not Shift.objects.filter(
                                user=available_night_sca[allocated], date=current_date, shift_type=shift_types['NIGHT_ASSISTANT']
                            ).exists():
                                Shift.objects.create(
                                    user=available_night_sca[allocated],
                                    date=current_date,
                                    shift_type=shift_types['NIGHT_ASSISTANT'],
                                    unit=unit
                                )
                                shifts_created += 1
                            allocated += 1
        
        return shifts_created