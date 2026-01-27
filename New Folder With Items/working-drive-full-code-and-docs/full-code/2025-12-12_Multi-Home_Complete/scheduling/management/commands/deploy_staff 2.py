from django.core.management.base import BaseCommand
from scheduling.models import User, Unit, Role
from django.db.models import Q, F
import random

class Command(BaseCommand):
    help = 'Demonstrate temporary staff deployment between units while maintaining home unit assignments'

    def add_arguments(self, parser):
        parser.add_argument(
            '--from-unit',
            type=str,
            help='Source unit name (e.g., BLUE, GREEN, DEMENTIA)',
        )
        parser.add_argument(
            '--to-unit', 
            type=str,
            help='Destination unit name (e.g., BLUE, GREEN, DEMENTIA)',
        )
        parser.add_argument(
            '--role',
            type=str,
            help='Role to deploy (SCW, SCA, SSCW)',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=1,
            help='Number of staff to deploy (default: 1)',
        )
        parser.add_argument(
            '--return-home',
            action='store_true',
            help='Return all temporarily deployed staff to their home units',
        )

    def handle(self, *args, **options):
        if options['return_home']:
            self.return_staff_home()
            return
            
        if not options['from_unit'] or not options['to_unit']:
            self.show_deployment_status()
            return
            
        self.deploy_staff(
            options['from_unit'],
            options['to_unit'], 
            options['role'],
            options['count']
        )

    def show_deployment_status(self):
        """Show current deployment status and available options"""
        self.stdout.write('🏠 CURRENT DEPLOYMENT STATUS')
        self.stdout.write('=' * 60)
        
        deployed_count = 0
        for unit in Unit.objects.exclude(name='ADMIN').order_by('name'):
            home_staff = User.objects.filter(home_unit=unit, is_active=True)
            current_staff = User.objects.filter(unit=unit, is_active=True)
            
            # Find staff temporarily deployed elsewhere
            deployed_away = home_staff.exclude(unit=unit)
            deployed_to_here = current_staff.exclude(home_unit=unit)
            
            self.stdout.write(f'\n🏢 {unit.get_name_display()}:')
            self.stdout.write(f'  🏠 Home staff: {home_staff.count()}')
            self.stdout.write(f'  📍 Currently here: {current_staff.count()}')
            
            if deployed_away.exists():
                self.stdout.write(f'  ↗️  Staff deployed elsewhere: {deployed_away.count()}')
                for staff in deployed_away:
                    self.stdout.write(f'    • {staff.full_name} ({staff.role.name}) → {staff.unit.get_name_display()}')
                    deployed_count += 1
            
            if deployed_to_here.exists():
                self.stdout.write(f'  ↘️  Temporary staff here: {deployed_to_here.count()}')
                for staff in deployed_to_here:
                    self.stdout.write(f'    • {staff.full_name} ({staff.role.name}) from {staff.home_unit.get_name_display()}')
        
        if deployed_count == 0:
            self.stdout.write('\n✅ All staff currently working in their home units')
        else:
            self.stdout.write(f'\n📊 {deployed_count} staff currently deployed away from home units')
        
        self.stdout.write('\n📋 USAGE EXAMPLES:')
        self.stdout.write('-' * 40)
        self.stdout.write('Deploy 1 SCW from Blue to Green:')
        self.stdout.write('  python manage.py deploy_staff --from-unit BLUE --to-unit GREEN --role SCW')
        self.stdout.write('\nDeploy 2 SCA from Dementia to Rose:')
        self.stdout.write('  python manage.py deploy_staff --from-unit DEMENTIA --to-unit ROSE --role SCA --count 2')
        self.stdout.write('\nReturn all staff to home units:')
        self.stdout.write('  python manage.py deploy_staff --return-home')

    def deploy_staff(self, from_unit_name, to_unit_name, role_name, count):
        """Deploy staff from one unit to another"""
        try:
            from_unit = Unit.objects.get(name=from_unit_name.upper())
            to_unit = Unit.objects.get(name=to_unit_name.upper())
        except Unit.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f'Unit not found: {e}'))
            return
        
        # Find available staff to deploy
        available_staff = User.objects.filter(
            home_unit=from_unit,
            unit=from_unit,  # Currently working in their home unit
            is_active=True
        )
        
        if role_name:
            available_staff = available_staff.filter(role__name=role_name.upper())
        
        if available_staff.count() < count:
            self.stdout.write(self.style.WARNING(
                f'Only {available_staff.count()} {role_name or "staff"} available in {from_unit.get_name_display()}, '
                f'but {count} requested'
            ))
            count = available_staff.count()
        
        if count == 0:
            self.stdout.write(self.style.ERROR('No suitable staff available for deployment'))
            return
        
        # Deploy the staff
        staff_to_deploy = available_staff[:count]
        deployed_names = []
        
        for staff in staff_to_deploy:
            staff.unit = to_unit
            staff.save()
            deployed_names.append(f'{staff.full_name} ({staff.role.name})')
        
        self.stdout.write(f'\n🚀 DEPLOYMENT SUCCESSFUL!')
        self.stdout.write('=' * 40)
        self.stdout.write(f'From: {from_unit.get_name_display()}')
        self.stdout.write(f'To: {to_unit.get_name_display()}')
        self.stdout.write(f'Staff deployed: {count}')
        self.stdout.write('\nDeployed staff:')
        for name in deployed_names:
            self.stdout.write(f'  • {name}')
        
        # Show updated unit status
        self.stdout.write(f'\n📊 UPDATED UNIT STATUS:')
        self.stdout.write(f'{from_unit.get_name_display()}: {User.objects.filter(unit=from_unit, is_active=True).count()} current staff')
        self.stdout.write(f'{to_unit.get_name_display()}: {User.objects.filter(unit=to_unit, is_active=True).count()} current staff')

    def return_staff_home(self):
        """Return all temporarily deployed staff to their home units"""
        deployed_staff = User.objects.filter(is_active=True).exclude(unit=F('home_unit'))
        
        if not deployed_staff.exists():
            self.stdout.write('✅ All staff are already working in their home units')
            return
        
        count = deployed_staff.count()
        returned_staff = []
        
        for staff in deployed_staff:
            original_unit = staff.unit.get_name_display() if staff.unit else 'Unknown'
            staff.unit = staff.home_unit
            staff.save()
            returned_staff.append(f'{staff.full_name} → {staff.home_unit.get_name_display()} (from {original_unit})')
        
        self.stdout.write(f'\n🏠 STAFF RETURNED HOME')
        self.stdout.write('=' * 40)
        self.stdout.write(f'Total staff returned: {count}')
        self.stdout.write('\nReturned staff:')
        for staff_info in returned_staff:
            self.stdout.write(f'  • {staff_info}')
        
        self.stdout.write('\n✅ All staff have returned to their home units!')