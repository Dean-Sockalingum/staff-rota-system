"""
Interactive Setup Wizard for Staff Rota System

This command provides a guided walkthrough for first-time setup, helping users:
1. Configure basic settings
2. Create admin account
3. Set up organizational structure (units, roles, shift types)
4. Import initial staff data
5. Generate first rotas

Usage:
    python3 manage.py setup_wizard
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from scheduling.models import Role, Unit, ShiftType, User
from staff_records.models import StaffProfile, AnnualLeaveEntitlement
from datetime import date, timedelta
from decimal import Decimal
import sys
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Interactive setup wizard for first-time configuration'

    def __init__(self):
        super().__init__()
        self.config = {}
        
    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-confirm',
            action='store_true',
            help='Skip confirmation prompts (use defaults)'
        )
        parser.add_argument(
            '--quick',
            action='store_true',
            help='Quick setup with minimal prompts'
        )

    def handle(self, *args, **options):
        self.skip_confirm = options.get('skip_confirm', False)
        self.quick_mode = options.get('quick', False)
        
        # Welcome screen
        self.print_welcome()
        
        if not self.skip_confirm:
            proceed = input("\nWould you like to proceed with setup? (yes/no): ").lower()
            if proceed not in ['yes', 'y']:
                self.stdout.write(self.style.WARNING('Setup cancelled.'))
                return
        
        try:
            # Step 1: Check existing configuration
            self.step_check_existing()
            
            # Step 2: Create/verify admin account
            self.step_admin_account()
            
            # Step 3: Configure organizational structure
            self.step_org_structure()
            
            # Step 4: Configure shift types
            self.step_shift_types()
            
            # Step 5: Import staff options
            self.step_staff_import()
            
            # Step 6: Generate initial rotas
            self.step_initial_rotas()
            
            # Step 7: Summary and next steps
            self.step_summary()
            
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\n\nSetup interrupted by user.'))
            sys.exit(1)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n\n❌ Setup failed: {str(e)}'))
            raise

    def print_welcome(self):
        """Display welcome screen"""
        welcome = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║          🏥 STAFF ROTA SYSTEM - SETUP WIZARD 🏥              ║
║                                                               ║
║  Welcome! This wizard will guide you through setting up      ║
║  your staff rota system for the first time.                  ║
║                                                               ║
║  The setup process includes:                                 ║
║    ✓ Admin account creation                                  ║
║    ✓ Organizational structure (units, roles)                 ║
║    ✓ Shift type configuration                                ║
║    ✓ Staff data import                                       ║
║    ✓ Initial rota generation                                 ║
║                                                               ║
║  Estimated time: 10-15 minutes                               ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
        """
        self.stdout.write(self.style.SUCCESS(welcome))

    def step_check_existing(self):
        """Check if system already has data"""
        self.stdout.write(self.style.HTTP_INFO('\n' + '='*60))
        self.stdout.write(self.style.HTTP_INFO('STEP 1: Checking Existing Configuration'))
        self.stdout.write(self.style.HTTP_INFO('='*60 + '\n'))
        
        # Check for existing data
        existing = {
            'users': User.objects.count(),
            'roles': Role.objects.count(),
            'units': Unit.objects.count(),
            'shift_types': ShiftType.objects.count(),
        }
        
        self.stdout.write('Current system status:')
        for key, count in existing.items():
            status = '✓' if count > 0 else '✗'
            self.stdout.write(f'  {status} {key.title()}: {count}')
        
        # Warn if data exists
        if any(existing.values()):
            self.stdout.write(self.style.WARNING(
                '\n⚠️  System already contains data. Continuing may create duplicates.'
            ))
            if not self.skip_confirm:
                proceed = input('Continue anyway? (yes/no): ').lower()
                if proceed not in ['yes', 'y']:
                    self.stdout.write(self.style.WARNING('Setup cancelled.'))
                    sys.exit(0)
        else:
            self.stdout.write(self.style.SUCCESS('\n✓ System is ready for initial setup.'))

    def step_admin_account(self):
        """Create or verify admin account"""
        self.stdout.write(self.style.HTTP_INFO('\n' + '='*60))
        self.stdout.write(self.style.HTTP_INFO('STEP 2: Admin Account Setup'))
        self.stdout.write(self.style.HTTP_INFO('='*60 + '\n'))
        
        # Check for existing superuser
        admin_exists = User.objects.filter(is_superuser=True).exists()
        
        if admin_exists:
            self.stdout.write(self.style.SUCCESS('✓ Admin account already exists.'))
            admins = User.objects.filter(is_superuser=True)
            self.stdout.write(f'  Found {admins.count()} admin account(s):')
            for admin in admins[:3]:
                self.stdout.write(f'    • {admin.sap} ({admin.email})')
            return
        
        self.stdout.write('No admin account found. Creating one now...\n')
        
        if self.quick_mode:
            # Quick mode defaults
            sap = 'ADMIN001'
            email = 'admin@staffrota.local'
            password = 'admin123'
            first_name = 'System'
            last_name = 'Administrator'
        else:
            # Interactive prompts
            sap = self._get_input('Admin SAP ID', 'ADMIN001')
            email = self._get_input('Admin email', 'admin@staffrota.local')
            first_name = self._get_input('First name', 'System')
            last_name = self._get_input('Last name', 'Administrator')
            password = self._get_password()
        
        # Create admin user
        with transaction.atomic():
            admin = User.objects.create_superuser(
                sap=sap,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_staff=True,
                is_active=True
            )
            
            self.stdout.write(self.style.SUCCESS(f'\n✓ Admin account created: {admin.sap}'))
            if self.quick_mode:
                self.stdout.write(self.style.WARNING(
                    f'  Default password: {password} (CHANGE THIS!)'
                ))

    def step_org_structure(self):
        """Set up organizational structure"""
        self.stdout.write(self.style.HTTP_INFO('\n' + '='*60))
        self.stdout.write(self.style.HTTP_INFO('STEP 3: Organizational Structure'))
        self.stdout.write(self.style.HTTP_INFO('='*60 + '\n'))
        
        # Check for existing roles
        if Role.objects.exists():
            self.stdout.write(self.style.SUCCESS(
                f'✓ Found {Role.objects.count()} existing roles.'
            ))
        else:
            self.stdout.write('Setting up default roles...')
            self._create_default_roles()
        
        # Check for existing units
        if Unit.objects.exists():
            self.stdout.write(self.style.SUCCESS(
                f'✓ Found {Unit.objects.count()} existing units.'
            ))
        else:
            self.stdout.write('\nSetting up default units...')
            self._create_default_units()

    def step_shift_types(self):
        """Set up shift types"""
        self.stdout.write(self.style.HTTP_INFO('\n' + '='*60))
        self.stdout.write(self.style.HTTP_INFO('STEP 4: Shift Types Configuration'))
        self.stdout.write(self.style.HTTP_INFO('='*60 + '\n'))
        
        if ShiftType.objects.exists():
            self.stdout.write(self.style.SUCCESS(
                f'✓ Found {ShiftType.objects.count()} existing shift types.'
            ))
            for shift_type in ShiftType.objects.all():
                self.stdout.write(
                    f'  • {shift_type.name}: {shift_type.start_time} - {shift_type.end_time}'
                )
        else:
            self.stdout.write('Setting up default shift types...')
            self._create_default_shift_types()

    def step_staff_import(self):
        """Guide user through staff import options"""
        self.stdout.write(self.style.HTTP_INFO('\n' + '='*60))
        self.stdout.write(self.style.HTTP_INFO('STEP 5: Staff Data Import'))
        self.stdout.write(self.style.HTTP_INFO('='*60 + '\n'))
        
        staff_count = User.objects.filter(is_staff=False).count()
        self.stdout.write(f'Current staff count: {staff_count}\n')
        
        if staff_count > 0:
            self.stdout.write(self.style.SUCCESS('✓ Staff data already exists.'))
            if not self.skip_confirm:
                add_more = input('Add more staff? (yes/no): ').lower()
                if add_more not in ['yes', 'y']:
                    return
        
        # Show import options
        self.stdout.write('\nStaff Import Options:\n')
        self.stdout.write('  1. Quick onboarding (one at a time, minimal info)')
        self.stdout.write('  2. CSV bulk import (7 required fields)')
        self.stdout.write('  3. Detailed CSV import (13 fields, full details)')
        self.stdout.write('  4. Skip for now (add staff later)\n')
        
        if self.skip_confirm or self.quick_mode:
            choice = '4'
        else:
            choice = input('Select option (1-4): ').strip()
        
        if choice == '1':
            self._guide_quick_onboarding()
        elif choice == '2':
            self._guide_csv_import('quick')
        elif choice == '3':
            self._guide_csv_import('detailed')
        else:
            self.stdout.write('Staff import skipped. You can add staff later using:')
            self.stdout.write('  • python3 manage.py onboard_staff --help')
            self.stdout.write('  • python3 manage.py import_staff_csv <file.csv>')

    def step_initial_rotas(self):
        """Guide rota generation"""
        self.stdout.write(self.style.HTTP_INFO('\n' + '='*60))
        self.stdout.write(self.style.HTTP_INFO('STEP 6: Initial Rota Generation'))
        self.stdout.write(self.style.HTTP_INFO('='*60 + '\n'))
        
        staff_count = User.objects.filter(is_staff=False, is_active=True).count()
        
        if staff_count == 0:
            self.stdout.write(self.style.WARNING(
                '⚠️  No staff found. Add staff before generating rotas.'
            ))
            return
        
        self.stdout.write(f'Found {staff_count} active staff members.\n')
        
        if self.skip_confirm or self.quick_mode:
            generate = 'no'
        else:
            generate = input('Generate initial rotas now? (yes/no): ').lower()
        
        if generate in ['yes', 'y']:
            self._generate_rotas()
        else:
            self.stdout.write('\nRota generation skipped. Generate rotas later using:')
            self.stdout.write('  • python3 manage.py generate_six_week_roster')
            self.stdout.write('  • python3 manage.py generate_supernumerary_shifts')

    def step_summary(self):
        """Display setup summary and next steps"""
        self.stdout.write(self.style.HTTP_INFO('\n' + '='*60))
        self.stdout.write(self.style.HTTP_INFO('SETUP COMPLETE!'))
        self.stdout.write(self.style.HTTP_INFO('='*60 + '\n'))
        
        # Gather stats
        stats = {
            'Admin Users': User.objects.filter(is_superuser=True).count(),
            'Staff Members': User.objects.filter(is_staff=False).count(),
            'Roles': Role.objects.count(),
            'Units': Unit.objects.count(),
            'Shift Types': ShiftType.objects.count(),
        }
        
        self.stdout.write(self.style.SUCCESS('📊 System Summary:\n'))
        for key, value in stats.items():
            self.stdout.write(f'  ✓ {key}: {value}')
        
        # Next steps
        self.stdout.write(self.style.SUCCESS('\n\n🚀 Next Steps:\n'))
        self.stdout.write('  1. Start the development server:')
        self.stdout.write('     python3 manage.py runserver\n')
        self.stdout.write('  2. Access the admin panel:')
        self.stdout.write('     http://127.0.0.1:8000/admin\n')
        self.stdout.write('  3. Access the main application:')
        self.stdout.write('     http://127.0.0.1:8000\n')
        self.stdout.write('  4. Review documentation:')
        self.stdout.write('     - README.md - General overview')
        self.stdout.write('     - QUICK_ONBOARDING_GUIDE.md - Staff management')
        self.stdout.write('     - CUSTOMIZATION_GUIDE.md - Configuration options\n')
        
        self.stdout.write(self.style.SUCCESS('\n✨ Setup wizard complete! ✨\n'))

    # Helper methods
    
    def _get_input(self, prompt, default=''):
        """Get user input with optional default"""
        if default:
            response = input(f'{prompt} [{default}]: ').strip()
            return response if response else default
        return input(f'{prompt}: ').strip()

    def _get_password(self):
        """Get password with confirmation"""
        import getpass
        while True:
            password = getpass.getpass('Password: ')
            if len(password) < 6:
                self.stdout.write(self.style.WARNING('Password must be at least 6 characters.'))
                continue
            confirm = getpass.getpass('Confirm password: ')
            if password == confirm:
                return password
            self.stdout.write(self.style.WARNING('Passwords do not match. Try again.'))

    def _create_default_roles(self):
        """Create default role structure"""
        roles = [
            {'name': 'OPERATIONS_MANAGER', 'color_code': '#1E88E5', 'is_management': True},
            {'name': 'SERVICE_MANAGER', 'color_code': '#43A047', 'is_management': True},
            {'name': 'SSCW', 'color_code': '#FB8C00', 'is_management': False},
            {'name': 'SCW', 'color_code': '#8E24AA', 'is_management': False},
            {'name': 'SCA', 'color_code': '#E53935', 'is_management': False},
        ]
        
        created = 0
        for role_data in roles:
            role, created_flag = Role.objects.get_or_create(**role_data)
            if created_flag:
                created += 1
                self.stdout.write(f'  ✓ Created role: {role.name}')
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ {created} roles created.'))

    def _create_default_units(self):
        """Create default unit structure"""
        units = [
            {'name': 'DEMENTIA', 'description': 'Dementia Care Unit'},
            {'name': 'BLUE', 'description': 'Blue Unit'},
            {'name': 'GREEN', 'description': 'Green Unit'},
            {'name': 'ROSE', 'description': 'Rose Unit'},
            {'name': 'VIOLET', 'description': 'Violet Unit'},
            {'name': 'ORANGE', 'description': 'Orange Unit'},
            {'name': 'PEACH', 'description': 'Peach Unit'},
            {'name': 'GRAPE', 'description': 'Grape Unit'},
            {'name': 'ADMIN', 'description': 'Administration'},
        ]
        
        created = 0
        for unit_data in units:
            unit, created_flag = Unit.objects.get_or_create(
                name=unit_data['name'],
                defaults={'description': unit_data['description']}
            )
            if created_flag:
                created += 1
                self.stdout.write(f'  ✓ Created unit: {unit.name}')
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ {created} units created.'))

    def _create_default_shift_types(self):
        """Create default shift types"""
        from datetime import time
        
        shift_types = [
            {
                'name': 'DAY_SENIOR',
                'start_time': time(8, 0),
                'end_time': time(20, 0),
                'hours': Decimal('12.0'),
                'is_night_shift': False
            },
            {
                'name': 'DAY_ASSISTANT',
                'start_time': time(8, 0),
                'end_time': time(20, 0),
                'hours': Decimal('12.0'),
                'is_night_shift': False
            },
            {
                'name': 'NIGHT_SENIOR',
                'start_time': time(20, 0),
                'end_time': time(8, 0),
                'hours': Decimal('12.0'),
                'is_night_shift': True
            },
            {
                'name': 'NIGHT_ASSISTANT',
                'start_time': time(20, 0),
                'end_time': time(8, 0),
                'hours': Decimal('12.0'),
                'is_night_shift': True
            },
        ]
        
        created = 0
        for shift_data in shift_types:
            shift_type, created_flag = ShiftType.objects.get_or_create(
                name=shift_data['name'],
                defaults=shift_data
            )
            if created_flag:
                created += 1
                self.stdout.write(
                    f'  ✓ Created shift: {shift_type.name} '
                    f'({shift_type.start_time}-{shift_type.end_time})'
                )
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ {created} shift types created.'))

    def _guide_quick_onboarding(self):
        """Guide user through quick onboarding"""
        self.stdout.write('\n📝 Quick Onboarding Guide:\n')
        self.stdout.write('  Required information (7 fields):')
        self.stdout.write('    • SAP ID (unique identifier)')
        self.stdout.write('    • Name')
        self.stdout.write('    • Role (SCW, SSCW, SCA, OPERATIONS_MANAGER)')
        self.stdout.write('    • Unit (home unit)')
        self.stdout.write('    • Team (A, B, or C)')
        self.stdout.write('    • Hours (24 or 35)')
        self.stdout.write('    • Start date (YYYY-MM-DD)\n')
        self.stdout.write('  Example command:')
        self.stdout.write('    python3 manage.py onboard_staff \\')
        self.stdout.write('      --sap STAFF001 \\')
        self.stdout.write('      --name "Jane Smith" \\')
        self.stdout.write('      --role SCW \\')
        self.stdout.write('      --unit ROSE \\')
        self.stdout.write('      --team A \\')
        self.stdout.write('      --hours 35 \\')
        self.stdout.write('      --start-date 2025-12-01\n')

    def _guide_csv_import(self, mode):
        """Guide user through CSV import"""
        if mode == 'quick':
            template = 'quick_onboard_template.csv'
            guide = 'QUICK_ONBOARDING_GUIDE.md'
            fields = '7 required fields'
        else:
            template = 'staff_import_template.csv'
            guide = 'STAFF_IMPORT_GUIDE.md'
            fields = '13 detailed fields'
        
        self.stdout.write(f'\n📁 CSV Import Guide ({mode} mode):\n')
        self.stdout.write(f'  1. Copy template file: {template}')
        self.stdout.write(f'  2. Fill in staff data ({fields})')
        self.stdout.write(f'  3. Run import command:\n')
        self.stdout.write(f'     python3 manage.py import_staff_csv {template}\n')
        self.stdout.write(f'  See {guide} for detailed instructions.\n')

    def _generate_rotas(self):
        """Generate initial rotas"""
        self.stdout.write('\n⏳ Generating rotas...\n')
        
        # Get start date
        if self.quick_mode:
            start_date = date.today()
        else:
            date_str = self._get_input(
                'Start date (YYYY-MM-DD)',
                date.today().strftime('%Y-%m-%d')
            )
            start_date = date.fromisoformat(date_str)
        
        # Get number of weeks
        if self.quick_mode:
            weeks = 6
        else:
            weeks_str = self._get_input('Number of weeks', '6')
            weeks = int(weeks_str)
        
        try:
            from django.core.management import call_command
            
            self.stdout.write(f'Generating {weeks} weeks of rotas from {start_date}...')
            call_command(
                'generate_six_week_roster',
                start_date=start_date.strftime('%Y-%m-%d'),
                weeks=weeks,
                verbosity=0
            )
            
            self.stdout.write(self.style.SUCCESS(f'✓ Generated {weeks} weeks of rotas!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to generate rotas: {str(e)}'))
