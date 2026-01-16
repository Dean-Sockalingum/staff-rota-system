from django.core.management.base import BaseCommand
from scheduling.models import User, Unit, Role
import random

class Command(BaseCommand):
    help = 'Allocate existing staff to units based on minimum staffing requirements'

    def handle(self, *args, **options):
        self.stdout.write('🏢 Allocating staff to units based on minimum standards...')
        
        # Get all care units (excluding admin)
        care_units = Unit.objects.exclude(name='ADMIN').order_by('name')
        admin_unit = Unit.objects.get(name='ADMIN')
        
        # Clear existing unit assignments
        User.objects.all().update(unit=None, team=None)
        
        # Get available staff by role
        scws = list(User.objects.filter(role__name='SCW', is_active=True))
        scas = list(User.objects.filter(role__name='SCA', is_active=True))
        sscws = list(User.objects.filter(role__name='SSCW', is_active=True))
        
        # Shuffle to ensure random distribution
        random.shuffle(scws)
        random.shuffle(scas)
        random.shuffle(sscws)
        
        teams = ['A', 'B', 'C']
        scw_index = 0
        sca_index = 0
        sscw_index = 0
        
        # Allocate to each care unit
        for unit in care_units:
            self.stdout.write(f'\\n📋 Allocating staff to {unit.get_name_display()}:')
            
            # Assign 1 SSCW as unit supervisor (if available)
            if sscw_index < len(sscws):
                sscw = sscws[sscw_index]
                sscw.unit = unit
                sscw.team = 'A'  # Senior staff typically on Team A
                sscw.save()
                sscw_index += 1
                self.stdout.write(f'  ✓ SSCW: {sscw.full_name} (Team A - Unit Supervisor)')
            
            # Calculate staff needed per team for this unit
            # Standard: 2 SCW + 3 SCA per team (24 staff total = 6 SCW + 9 SCA per team × 3 teams)
            scws_per_team = 2
            scas_per_team = 3
            
            # Assign staff to 3 teams
            for team in teams:
                team_scws = []
                team_scas = []
                
                # Assign SCWs to this team
                for _ in range(scws_per_team):
                    if scw_index < len(scws):
                        scw = scws[scw_index]
                        scw.unit = unit
                        scw.team = team
                        scw.save()
                        team_scws.append(scw.full_name)
                        scw_index += 1
                
                # Assign SCAs to this team
                for _ in range(scas_per_team):
                    if sca_index < len(scas):
                        sca = scas[sca_index]
                        sca.unit = unit
                        sca.team = team
                        sca.save()
                        team_scas.append(sca.full_name)
                        sca_index += 1
                
                if team_scws or team_scas:
                    self.stdout.write(f'  ✓ Team {team}: {len(team_scws)} SCW, {len(team_scas)} SCA')
        
        # Assign remaining staff to admin unit
        remaining_staff = User.objects.filter(unit__isnull=True, is_active=True)
        for staff in remaining_staff:
            staff.unit = admin_unit
            staff.save()
        
        # Display allocation summary
        self.stdout.write('\\n📊 FINAL STAFF ALLOCATION:')
        self.stdout.write('=' * 60)
        
        for unit in Unit.objects.all().order_by('name'):
            unit_staff = User.objects.filter(unit=unit, is_active=True)
            self.stdout.write(f'\\n🏢 {unit.get_name_display()}: {unit_staff.count()} staff')
            
            # Show by role
            for role_name in ['SSCW', 'SCW', 'SCA', 'OPERATIONS_MANAGER', 'MAINTENANCE', 'KITCHEN', 'CLEANING', 'DRIVER', 'ADMIN']:
                role_count = unit_staff.filter(role__name=role_name).count()
                if role_count > 0:
                    self.stdout.write(f'  - {role_name}: {role_count}')
            
            # Show by team for care units
            if unit.name != 'ADMIN':
                for team in ['A', 'B', 'C']:
                    team_staff = unit_staff.filter(team=team)
                    if team_staff.exists():
                        scw_count = team_staff.filter(role__name='SCW').count()
                        sca_count = team_staff.filter(role__name='SCA').count()
                        sscw_count = team_staff.filter(role__name='SSCW').count()
                        self.stdout.write(f'    Team {team}: {sscw_count} SSCW, {scw_count} SCW, {sca_count} SCA')
        
        total_allocated = User.objects.filter(unit__isnull=False, is_active=True).count()
        self.stdout.write(f'\\n✅ Successfully allocated {total_allocated} staff to units!')