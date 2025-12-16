"""
Quick Staff Onboarding Command

Quickly add a new staff member with minimal information and automatically
populate them into the rota system.

Usage:
    python3 manage.py onboard_staff --sap STAFF001 --name "Jane Smith" --role SCW --unit ROSE --team A --hours 24 --start-date 2025-12-01

This command will:
1. Create the staff member
2. Assign to specified team and unit
3. Set up shift patterns based on role and hours
4. Create annual leave entitlement
5. Add to active rotas (if --add-to-rota flag is used)
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from scheduling.models import User, Role, Unit, ShiftType, Shift
from staff_records.models import StaffProfile, AnnualLeaveEntitlement
from datetime import date, timedelta
from decimal import Decimal
import sys


class Command(BaseCommand):
    help = 'Quick onboard a new staff member with minimal information'

    def add_arguments(self, parser):
        # Required arguments
        parser.add_argument(
            '--sap',
            type=str,
            required=True,
            help='Staff SAP ID (e.g., STAFF001)'
        )
        parser.add_argument(
            '--name',
            type=str,
            required=True,
            help='Full name (e.g., "Jane Smith")'
        )
        parser.add_argument(
            '--role',
            type=str,
            required=True,
            choices=['OPERATIONS_MANAGER', 'SSCW', 'SCW', 'SCA'],
            help='Role: OPERATIONS_MANAGER, SSCW, SCW, or SCA'
        )
        parser.add_argument(
            '--unit',
            type=str,
            required=True,
            help='Home unit name (e.g., ROSE, BLUE, GREEN)'
        )
        parser.add_argument(
            '--team',
            type=str,
            required=True,
            choices=['A', 'B', 'C'],
            help='Team: A, B, or C'
        )
        parser.add_argument(
            '--hours',
            type=int,
            required=True,
            choices=[24, 35],
            help='Contracted hours per week: 24 or 35'
        )
        parser.add_argument(
            '--start-date',
            type=str,
            required=True,
            help='Start date (YYYY-MM-DD format, e.g., 2025-12-01)'
        )
        
        # Optional arguments
        parser.add_argument(
            '--email',
            type=str,
            help='Email address (auto-generated if not provided)'
        )
        parser.add_argument(
            '--phone',
            type=str,
            help='Phone number'
        )
        parser.add_argument(
            '--shift-preference',
            type=str,
            choices=['DAY_SENIOR', 'DAY_ASSISTANT', 'NIGHT_SENIOR', 'NIGHT_ASSISTANT'],
            help='Shift preference (auto-detected if not provided)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='changeme123',
            help='Initial password (default: changeme123)'
        )
        parser.add_argument(
            '--add-to-rota',
            action='store_true',
            help='Automatically add to upcoming rotas from start date'
        )
        parser.add_argument(
            '--weeks',
            type=int,
            default=4,
            help='Number of weeks to generate shifts for (if --add-to-rota is used)'
        )

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('🎯 QUICK STAFF ONBOARDING'))
        self.stdout.write('=' * 70)

        try:
            with transaction.atomic():
                staff_member = self._onboard_staff(options)
                
                if options['add_to_rota']:
                    self._add_to_rota(staff_member, options)
                
                self._print_summary(staff_member, options)
                
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'\n❌ Error: {str(e)}'))
            sys.exit(1)

    def _onboard_staff(self, options):
        """Create staff member with all required records"""
        
        # Parse inputs
        sap = options['sap'].upper().strip()
        name_parts = options['name'].strip().split(maxsplit=1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        role_name = options['role']
        unit_name = options['unit'].upper()
        team = options['team'].upper()
        contracted_hours = Decimal(str(options['hours']))
        start_date = date.fromisoformat(options['start_date'])
        
        # Auto-generate email if not provided
        email = options.get('email') or f"{sap.lower()}@staffrota.local"
        phone = options.get('phone', '')
        password = options['password']
        
        # Check for duplicates
        if User.objects.filter(sap=sap).exists():
            raise ValueError(f'Staff member with SAP {sap} already exists')
        if User.objects.filter(email=email).exists():
            raise ValueError(f'Email {email} already in use')
        
        self.stdout.write(f'\n📝 Creating staff record for {first_name} {last_name}...')
        
        # Get or create role
        role, _ = Role.objects.get_or_create(
            name=role_name,
            defaults={
                'description': f'{role_name} role',
                'is_management': role_name == 'OPERATIONS_MANAGER'
            }
        )
        
        # Get or create unit
        unit, created = Unit.objects.get_or_create(
            name=unit_name,
            defaults={
                'description': f'{unit_name} unit',
                'min_day_staff': 2,
                'min_night_staff': 2
            }
        )
        if created:
            self.stdout.write(f'   ✅ Created new unit: {unit_name}')
        
        # Auto-detect shift preference if not provided
        shift_preference = options.get('shift_preference')
        if not shift_preference:
            if role_name in ['OPERATIONS_MANAGER', 'SSCW', 'SCW']:
                shift_preference = 'DAY_SENIOR'  # Default senior staff to day
            else:
                shift_preference = 'DAY_ASSISTANT'  # Default assistants to day
        
        # Create User
        user = User.objects.create(
            sap=sap,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone,
            role=role,
            home_unit=unit,
            unit=unit,
            team=team,
            shift_preference=shift_preference,
            is_active=True,
            is_staff=(role_name == 'OPERATIONS_MANAGER'),
            annual_leave_allowance=28 if contracted_hours >= 30 else 17
        )
        user.set_password(password)
        user.save()
        self.stdout.write(f'   ✅ User account created')
        
        # Create StaffProfile
        profile = StaffProfile.objects.create(
            user=user,
            contracted_hours_per_week=contracted_hours,
            employment_status='ACTIVE',
            start_date=start_date
        )
        self.stdout.write(f'   ✅ Staff profile created')
        
        # Create Annual Leave Entitlement
        current_year = start_date.year
        leave_year_start = date(current_year, 1, 1)
        leave_year_end = date(current_year, 12, 31)
        
        # Calculate hours based on contract
        if contracted_hours >= 30:
            total_hours = Decimal('297.5')  # 35hr staff: ~25.5 days @ 11.66hrs
        else:
            total_hours = Decimal('204.0')   # 24hr staff: 17 days @ 12hrs
        
        # Pro-rate if starting mid-year
        days_in_year = (leave_year_end - leave_year_start).days + 1
        days_remaining = (leave_year_end - start_date).days + 1
        pro_rata_hours = (total_hours * Decimal(str(days_remaining))) / Decimal(str(days_in_year))
        
        entitlement = AnnualLeaveEntitlement.objects.create(
            profile=profile,
            leave_year_start=leave_year_start,
            leave_year_end=leave_year_end,
            contracted_hours_per_week=contracted_hours,
            total_entitlement_hours=pro_rata_hours.quantize(Decimal('0.1')),
            hours_used=Decimal('0.0'),
            hours_pending=Decimal('0.0'),
            carryover_hours=Decimal('0.0')
        )
        self.stdout.write(f'   ✅ Annual leave entitlement created ({entitlement.total_entitlement_hours} hrs)')
        
        return user

    def _add_to_rota(self, user, options):
        """Add staff member to upcoming rotas"""
        
        self.stdout.write(f'\n📅 Adding to rota schedule...')
        
        start_date = date.fromisoformat(options['start_date'])
        weeks = options['weeks']
        end_date = start_date + timedelta(weeks=weeks)
        
        # Determine shift types based on preference
        if user.shift_preference == 'DAY_SENIOR':
            shift_type_names = ['DAY_SENIOR']
        elif user.shift_preference == 'NIGHT_SENIOR':
            shift_type_names = ['NIGHT_SENIOR']
        elif user.shift_preference == 'DAY_ASSISTANT':
            shift_type_names = ['DAY_ASSISTANT']
        elif user.shift_preference == 'NIGHT_ASSISTANT':
            shift_type_names = ['NIGHT_ASSISTANT']
        else:
            shift_type_names = ['DAY_SENIOR']  # Default
        
        shift_types = ShiftType.objects.filter(name__in=shift_type_names)
        
        if not shift_types.exists():
            self.stdout.write(self.style.WARNING(
                f'   ⚠️  No shift types found for {user.shift_preference}'
            ))
            return
        
        # Calculate shifts per week based on contracted hours and role
        contracted_hours = Decimal(str(options['hours']))
        role_name = options['role']
        
        # Management/Admin get 5 shifts per week (Mon-Fri)
        if role_name in ['OPERATIONS_MANAGER', 'SERVICE_MANAGER']:
            shifts_per_week = 5
        # 35hr staff (SCW, SSCW) get 3 shifts per week (12-hour shifts)
        elif contracted_hours >= 30:
            shifts_per_week = 3
        # 24hr staff (SCA) get 2 shifts per week
        else:
            shifts_per_week = 2
        
        # Generate shifts
        shifts_created = 0
        current_date = start_date
        shift_count_this_week = 0
        week_start = start_date
        
        while current_date < end_date:
            # Reset counter on new week
            if (current_date - week_start).days >= 7:
                week_start = current_date
                shift_count_this_week = 0
            
            # Add shift if we haven't hit limit for this week
            if shift_count_this_week < shifts_per_week:
                # Check if suitable day (skip weekends for day staff, prefer weekends for night staff)
                is_weekday = current_date.weekday() < 5
                
                if user.shift_preference in ['DAY_SENIOR', 'DAY_ASSISTANT'] and is_weekday:
                    for shift_type in shift_types:
                        Shift.objects.create(
                            user=user,
                            unit=user.home_unit,
                            shift_type=shift_type,
                            date=current_date,
                            status='SCHEDULED'
                        )
                        shifts_created += 1
                        shift_count_this_week += 1
                        break
                elif user.shift_preference in ['NIGHT_SENIOR', 'NIGHT_ASSISTANT']:
                    # Night staff work mix of weekdays and weekends
                    if shifts_created % 3 != 0 or not is_weekday:  # Simple pattern
                        for shift_type in shift_types:
                            Shift.objects.create(
                                user=user,
                                unit=user.home_unit,
                                shift_type=shift_type,
                                date=current_date,
                                status='SCHEDULED'
                            )
                            shifts_created += 1
                            shift_count_this_week += 1
                            break
            
            current_date += timedelta(days=1)
        
        self.stdout.write(f'   ✅ Created {shifts_created} shifts over {weeks} weeks')

    def _print_summary(self, user, options):
        """Print onboarding summary"""
        
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('✅ ONBOARDING COMPLETE!'))
        self.stdout.write('=' * 70)
        
        self.stdout.write(f'\n👤 Staff Member: {user.full_name}')
        self.stdout.write(f'📋 SAP: {user.sap}')
        self.stdout.write(f'📧 Email: {user.email}')
        self.stdout.write(f'🔑 Password: {options["password"]} (MUST CHANGE ON FIRST LOGIN)')
        self.stdout.write(f'👔 Role: {user.role.name}')
        self.stdout.write(f'🏢 Home Unit: {user.home_unit.name}')
        self.stdout.write(f'👥 Team: {user.team}')
        self.stdout.write(f'⏰ Contracted Hours: {user.staffprofile.contracted_hours_per_week}/week')
        self.stdout.write(f'🌅 Shift Preference: {user.get_shift_preference_display()}')
        self.stdout.write(f'📅 Start Date: {user.staffprofile.start_date}')
        
        entitlement = user.staffprofile.annual_leave_entitlements.first()
        if entitlement:
            self.stdout.write(f'🏖️  Annual Leave: {entitlement.total_entitlement_hours} hours ({entitlement.total_entitlement_hours / Decimal("11.66"):.1f} days)')
        
        if options['add_to_rota']:
            shifts = Shift.objects.filter(user=user, date__gte=options['start_date'])
            self.stdout.write(f'📊 Shifts Created: {shifts.count()}')
        
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('🎉 Ready to start work!'))
        self.stdout.write('=' * 70)
