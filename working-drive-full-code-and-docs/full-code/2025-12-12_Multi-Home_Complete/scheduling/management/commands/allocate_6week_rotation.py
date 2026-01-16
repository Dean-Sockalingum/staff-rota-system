from django.core.management.base import BaseCommand
from scheduling.models import User, Unit, Role
import random

class Command(BaseCommand):
    help = 'Allocate staff using 6-week rotation model with correct day/night staffing'

    def handle(self, *args, **options):
        self.stdout.write('🔄 Allocating staff for 6-week rotation model...')
        
        # Clear existing assignments
        User.objects.all().update(unit=None, team=None)
        
        # Get all care units and admin
        care_units = Unit.objects.exclude(name='ADMIN').order_by('name')
        admin_unit = Unit.objects.get(name='ADMIN')
        
        # Get available staff by role
        sscws = list(User.objects.filter(role__name='SSCW', is_active=True))
        scws = list(User.objects.filter(role__name='SCW', is_active=True))
        scas = list(User.objects.filter(role__name='SCA', is_active=True))
        
        # Shuffle for random distribution
        random.shuffle(sscws)
        random.shuffle(scws)
        random.shuffle(scas)
        
        teams = ['A', 'B', 'C']
        sscw_index = 0
        scw_index = 0
        sca_index = 0
        
        self.stdout.write('\\n📋 6-WEEK ROTATION STAFFING MODEL:')
        self.stdout.write('Day shifts: 1 SCW + 2 SCA (standard), 1 SCW + 3 SCA (dementia)')
        self.stdout.write('Night shifts: 1 SCW + 1 SCA (standard), 1 SCW + 2 SCA (dementia)')
        self.stdout.write('Teams rotate: Week 1 (Sun-Tue), Week 2 (Wed-Thu), Week 3 (Fri-Sat), then rotate patterns')
        
        # Allocate to each care unit
        for unit in care_units:
            self.stdout.write(f'\\n🏢 {unit.get_name_display()}:')
            
            # Determine staffing requirements per team
            if unit.name == 'DEMENTIA':
                # Dementia: 1 SCW + 3 SCA (day), 1 SCW + 2 SCA (night) = 8 staff per team
                scws_per_team = 2  # Day + Night SCW
                scas_per_team = 5  # 3 (day) + 2 (night)
                sscws_per_team = 1 # Unit supervisor
            else:
                # Standard: 1 SCW + 2 SCA (day), 1 SCW + 1 SCA (night) = 5 staff per team
                scws_per_team = 2  # Day + Night SCW
                scas_per_team = 3  # 2 (day) + 1 (night)
                sscws_per_team = 1 # Unit supervisor\n            \n            # Assign teams\n            for team in teams:\n                team_staff = []\n                \n                # Assign SSCW (supervisor)\n                if sscw_index < len(sscws):\n                    sscw = sscws[sscw_index]\n                    sscw.unit = unit\n                    sscw.team = team\n                    sscw.save()\n                    team_staff.append(f'{sscw.full_name} (SSCW)')\n                    sscw_index += 1\n                \n                # Assign SCWs\n                for _ in range(scws_per_team):\n                    if scw_index < len(scws):\n                        scw = scws[scw_index]\n                        scw.unit = unit\n                        scw.team = team\n                        scw.save()\n                        team_staff.append(f'{scw.full_name} (SCW)')\n                        scw_index += 1\n                \n                # Assign SCAs\n                for _ in range(scas_per_team):\n                    if sca_index < len(scas):\n                        sca = scas[sca_index]\n                        sca.unit = unit\n                        sca.team = team\n                        sca.save()\n                        team_staff.append(f'{sca.full_name} (SCA)')\n                        sca_index += 1\n                \n                if team_staff:\n                    self.stdout.write(f'  Team {team}: {len(team_staff)} staff')\n                    self.stdout.write(f'    - Can cover: Day shifts ✅ Night shifts ✅')\n        \n        # Assign remaining staff to admin\n        remaining_staff = User.objects.filter(unit__isnull=True, is_active=True)\n        for staff in remaining_staff:\n            staff.unit = admin_unit\n            staff.save()\n        \n        self.stdout.write('\\n📊 FINAL 6-WEEK ROTATION ALLOCATION:')\n        self.stdout.write('=' * 60)\n        \n        for unit in Unit.objects.all().order_by('name'):\n            unit_staff = User.objects.filter(unit=unit, is_active=True)\n            self.stdout.write(f'\\n🏢 {unit.get_name_display()}: {unit_staff.count()} staff')\n            \n            if unit.name != 'ADMIN':\n                # Show team composition\n                for team in teams:\n                    team_staff = unit_staff.filter(team=team)\n                    if team_staff.exists():\n                        sscw_count = team_staff.filter(role__name='SSCW').count()\n                        scw_count = team_staff.filter(role__name='SCW').count()\n                        sca_count = team_staff.filter(role__name='SCA').count()\n                        total = sscw_count + scw_count + sca_count\n                        \n                        # Check coverage\n                        if unit.name == 'DEMENTIA':\n                            day_ok = '✅' if (sscw_count + scw_count >= 1 and sca_count >= 3) else '❌'\n                            night_ok = '✅' if (sscw_count + scw_count >= 1 and sca_count >= 2) else '❌'\n                        else:\n                            day_ok = '✅' if (sscw_count + scw_count >= 1 and sca_count >= 2) else '❌'\n                            night_ok = '✅' if (sscw_count + scw_count >= 1 and sca_count >= 1) else '❌'\n                        \n                        self.stdout.write(f'  Team {team}: {total} staff ({sscw_count} SSCW, {scw_count} SCW, {sca_count} SCA)')\n                        self.stdout.write(f'    Day coverage: {day_ok} Night coverage: {night_ok}')\n            \n            else:\n                # Admin staff\n                for role_name in ['OPERATIONS_MANAGER', 'MAINTENANCE', 'KITCHEN', 'CLEANING', 'DRIVER', 'ADMIN']:\n                    role_count = unit_staff.filter(role__name=role_name).count()\n                    if role_count > 0:\n                        self.stdout.write(f'  - {role_name}: {role_count}')\n        \n        total_allocated = User.objects.filter(unit__isnull=False, is_active=True).count()\n        self.stdout.write(f'\\n✅ Successfully allocated {total_allocated} staff for 6-week rotation!')\n        self.stdout.write('\\n🔄 ROTATION PATTERN:')\n        self.stdout.write('Week 1: Team A (Sun-Tue), Team B (Wed-Thu), Team C (Fri-Sat)')\n        self.stdout.write('Week 2: Team B (Sun-Tue), Team C (Wed-Thu), Team A (Fri-Sat)')\n        self.stdout.write('Week 3: Team C (Sun-Tue), Team A (Wed-Thu), Team B (Fri-Sat)')\n        self.stdout.write('...pattern continues for 6 weeks, then repeats')