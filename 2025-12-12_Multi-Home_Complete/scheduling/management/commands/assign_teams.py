from django.core.management.base import BaseCommand
from scheduling.models import User
import random

class Command(BaseCommand):
    help = 'Assign staff to balanced teams (A, B, C) for day and night shifts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all existing team assignments before reassigning'
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Resetting all team assignments...')
            User.objects.all().update(team=None)

        self.stdout.write('🎯 ASSIGNING STAFF TO BALANCED TEAMS')
        self.stdout.write('=' * 50)

        # Get staff by shift and role
        day_staff = {
            'SCW': list(User.objects.filter(role__name='SCW', shift_preference='DAY_SENIOR', is_active=True)),
            'SCA': list(User.objects.filter(role__name='SCA', shift_preference='DAY_ASSISTANT', is_active=True)),
            'SSCW': list(User.objects.filter(role__name='SSCW', shift_preference='DAY_SENIOR', is_active=True))
        }

        night_staff = {
            'SCW': list(User.objects.filter(role__name='SCW', shift_preference='NIGHT_SENIOR', is_active=True)),
            'SCA': list(User.objects.filter(role__name='SCA', shift_preference='NIGHT_ASSISTANT', is_active=True)),
            'SSCW': list(User.objects.filter(role__name='SSCW', shift_preference='NIGHT_SENIOR', is_active=True))
        }

        # Assign day staff
        self.stdout.write('\n📅 ASSIGNING DAY SHIFT TEAMS:')
        self._assign_teams(day_staff, 'Day')

        # Assign night staff
        self.stdout.write('\n🌙 ASSIGNING NIGHT SHIFT TEAMS:')
        self._assign_teams(night_staff, 'Night')

        # Print summary
        self.stdout.write('\n📊 TEAM ASSIGNMENT SUMMARY:')
        self._print_summary()

        self.stdout.write(self.style.SUCCESS('\n✅ Team assignments completed!'))

    def _assign_teams(self, staff_dict, shift_name):
        """Assign staff to teams in a balanced way"""
        teams = ['A', 'B', 'C']
        
        for role_name, staff_list in staff_dict.items():
            if not staff_list:
                continue
                
            # Shuffle for random distribution
            random.shuffle(staff_list)
            
            # Calculate base allocation per team
            total_staff = len(staff_list)
            base_per_team = total_staff // 3
            remainder = total_staff % 3
            
            self.stdout.write(f'   {role_name}: {total_staff} staff → {base_per_team} per team (+{remainder} extra)')
            
            staff_index = 0
            
            # Assign base allocation to each team
            for i, team in enumerate(teams):
                # Calculate how many for this team (handle remainder)
                team_size = base_per_team + (1 if i < remainder else 0)
                
                team_staff = []
                for _ in range(team_size):
                    if staff_index < len(staff_list):
                        staff = staff_list[staff_index]
                        staff.team = team
                        staff.save()
                        team_staff.append(staff)
                        staff_index += 1
                
                self.stdout.write(f'     Team {team}: {len(team_staff)} {role_name}')
                for staff_member in team_staff:
                    self.stdout.write(f'       - {staff_member.sap} ({staff_member.first_name} {staff_member.last_name})')

    def _print_summary(self):
        """Print overall team summary"""
        teams = ['A', 'B', 'C']
        
        self.stdout.write('-' * 60)
        
        for shift_type in ['DAY', 'NIGHT']:
            self.stdout.write(f'\n{shift_type} SHIFT TEAMS:')
            
            for team in teams:
                if shift_type == 'DAY':
                    scw_count = User.objects.filter(
                        team=team, 
                        role__name='SCW', 
                        shift_preference='DAY_SENIOR',
                        is_active=True
                    ).count()
                    sca_count = User.objects.filter(
                        team=team, 
                        role__name='SCA', 
                        shift_preference='DAY_ASSISTANT',
                        is_active=True
                    ).count()
                    sscw_count = User.objects.filter(
                        team=team, 
                        role__name='SSCW', 
                        shift_preference='DAY_SENIOR',
                        is_active=True
                    ).count()
                else:
                    scw_count = User.objects.filter(
                        team=team, 
                        role__name='SCW', 
                        shift_preference='NIGHT_SENIOR',
                        is_active=True
                    ).count()
                    sca_count = User.objects.filter(
                        team=team, 
                        role__name='SCA', 
                        shift_preference='NIGHT_ASSISTANT',
                        is_active=True
                    ).count()
                    sscw_count = User.objects.filter(
                        team=team, 
                        role__name='SSCW', 
                        shift_preference='NIGHT_SENIOR',
                        is_active=True
                    ).count()
                
                total = scw_count + sca_count + sscw_count
                self.stdout.write(f'  Team {team}: {total} total (SCW: {scw_count}, SCA: {sca_count}, SSCW: {sscw_count})')