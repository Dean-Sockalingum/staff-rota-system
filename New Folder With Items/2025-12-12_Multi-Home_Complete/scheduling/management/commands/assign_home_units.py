from django.core.management.base import BaseCommand
from scheduling.models import User, Unit, Role
import random

class Command(BaseCommand):
    help = 'Assign permanent home units to all staff based on their current allocation'

    def handle(self, *args, **options):
        self.stdout.write('🏠 Assigning permanent home units to all staff...')
        
        # Step 1: Set current unit as home unit for all existing staff
        total_assigned = 0
        for user in User.objects.filter(is_active=True, unit__isnull=False):
            user.home_unit = user.unit
            user.save()
            total_assigned += 1
        
        self.stdout.write(f'✅ Set home units for {total_assigned} staff based on current allocation')
        
        # Step 2: Display permanent home unit allocation
        self.stdout.write('\n🏠 PERMANENT HOME UNIT ALLOCATION:')
        self.stdout.write('=' * 60)
        
        for unit in Unit.objects.all().order_by('name'):
            home_staff = User.objects.filter(home_unit=unit, is_active=True)
            current_staff = User.objects.filter(unit=unit, is_active=True)
            
            self.stdout.write(f'\n🏢 {unit.get_name_display()}:')
            self.stdout.write(f'  🏠 Permanent staff: {home_staff.count()}')
            self.stdout.write(f'  📍 Currently working: {current_staff.count()}')
            
            if unit.name != 'ADMIN':
                # Show permanent home teams
                for team in ['A', 'B', 'C']:
                    team_home = home_staff.filter(team=team)
                    if team_home.exists():
                        sscw = team_home.filter(role__name='SSCW').count()
                        scw = team_home.filter(role__name='SCW').count()
                        sca = team_home.filter(role__name='SCA').count()
                        self.stdout.write(f'    🏠 Team {team} Home: {sscw} SSCW, {scw} SCW, {sca} SCA')
        
        # Step 3: Show flexibility options
        self.stdout.write('\n🔄 DEPLOYMENT FLEXIBILITY:')
        self.stdout.write('-' * 40)
        self.stdout.write('✓ Staff can be temporarily deployed to other units')
        self.stdout.write('✓ Home unit remains their permanent base')
        self.stdout.write('✓ Scheduling prioritizes home unit assignments')
        self.stdout.write('✓ Cover can be arranged by moving staff between units')
        
        # Step 4: Show example of how to redeploy staff
        self.stdout.write('\n📋 EXAMPLE REDEPLOYMENT SCENARIOS:')
        self.stdout.write('-' * 40)
        
        # Find some example staff for demonstration
        blue_staff = User.objects.filter(home_unit__name='BLUE', is_active=True).first()
        green_staff = User.objects.filter(home_unit__name='GREEN', is_active=True).first()
        
        if blue_staff and green_staff:
            self.stdout.write(f'• {blue_staff.full_name} (Home: Blue Unit) → Temporarily to Green Unit')
            self.stdout.write(f'• {green_staff.full_name} (Home: Green Unit) → Temporarily to Dementia Unit')
            self.stdout.write('• Staff can return to home units after cover period')
        
        self.stdout.write('\n🎯 MANAGEMENT BENEFITS:')
        self.stdout.write('-' * 30)
        self.stdout.write('✓ Clear permanent team structures')
        self.stdout.write('✓ Staff familiarity with their home unit')
        self.stdout.write('✓ Flexible deployment for cover needs')
        self.stdout.write('✓ Easy tracking of temporary assignments')
        self.stdout.write('✓ Staff can build relationships in home units')
        
        self.stdout.write(f'\n🏠 Permanent home units assigned successfully!')
        self.stdout.write(f'📊 Total staff with home units: {User.objects.filter(home_unit__isnull=False, is_active=True).count()}')