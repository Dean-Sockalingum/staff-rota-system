"""
Clone Orchard Grove's complete rota structure to other homes

Creates identical shift patterns with new staff members for each target home.
Staff members are cloned with new names and consecutive SAP numbers.

Usage:
    python3 manage.py clone_orchard_rota --target-homes 2,3,4
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from scheduling.models import Shift, Unit, User, CareHome, Role
from collections import defaultdict


class Command(BaseCommand):
    help = 'Clone Orchard Grove rota structure to other homes with new staff'

    def add_arguments(self, parser):
        parser.add_argument(
            '--target-homes',
            type=str,
            required=True,
            help='Comma-separated care home IDs (e.g., "2,3,4" for Meadowburn, Hawthorn, Riverside)'
        )

    def handle(self, *args, **options):
        target_home_ids = [int(x.strip()) for x in options['target_homes'].split(',')]
        
        self.stdout.write(self.style.SUCCESS(f'\n{"="*70}'))
        self.stdout.write(self.style.SUCCESS('🏥 CLONING ORCHARD GROVE ROTA STRUCTURE'))
        self.stdout.write(self.style.SUCCESS(f'{"="*70}\n'))

        # Get Orchard Grove (home ID 1)
        try:
            orchard_grove = CareHome.objects.get(id=1)
        except CareHome.DoesNotExist:
            self.stderr.write(self.style.ERROR('❌ Orchard Grove (ID 1) not found'))
            return

        # Get target homes
        target_homes = CareHome.objects.filter(id__in=target_home_ids).order_by('name')
        if target_homes.count() != len(target_home_ids):
            self.stderr.write(self.style.ERROR('❌ One or more target homes not found'))
            return

        self.stdout.write(f'📋 Source: {orchard_grove.get_name_display()}')
        self.stdout.write(f'🎯 Targets: {", ".join([h.get_name_display() for h in target_homes])}\n')

        # Get Orchard Grove's units and shifts
        orchard_units = list(Unit.objects.filter(care_home=orchard_grove, is_active=True))
        orchard_shifts = Shift.objects.filter(unit__in=orchard_units).select_related(
            'user', 'user__role', 'shift_type', 'unit'
        ).order_by('date', 'unit', 'shift_type')

        self.stdout.write(f'📊 Orchard Grove: {len(orchard_units)} units, {orchard_shifts.count()} shifts')

        # Get highest SAP number currently in use
        last_sap = User.objects.filter(sap__regex=r'^\d+$').order_by('-sap').first()
        if last_sap:
            next_sap_number = int(last_sap.sap) + 1
        else:
            # Fallback: check for pattern-based SAPs
            last_user = User.objects.order_by('-sap').first()
            next_sap_number = 10000  # Start from 10000 if we can't determine
        
        self.stdout.write(f'🔢 Starting SAP number: {next_sap_number}\n')

        # Process each target home
        for target_home in target_homes:
            self.stdout.write(f'{"-"*70}')
            self.stdout.write(self.style.SUCCESS(f'🏥 {target_home.get_name_display()}'))
            self.stdout.write(f'{"-"*70}')

            next_sap_number = self.clone_home_structure(
                orchard_grove, target_home, orchard_units, orchard_shifts, next_sap_number
            )

        self.stdout.write(f'\n{"="*70}')
        self.stdout.write(self.style.SUCCESS(f'✅ CLONING COMPLETE'))
        self.stdout.write(f'{"="*70}\n')

    def clone_home_structure(self, source_home, target_home, source_units, source_shifts, start_sap):
        """Clone complete rota structure from source to target home"""
        
        # Get target home's units
        target_units = list(Unit.objects.filter(care_home=target_home, is_active=True).order_by('name'))
        
        if len(target_units) != len(source_units):
            self.stdout.write(self.style.WARNING(
                f'⚠️  Unit count mismatch: Source has {len(source_units)}, Target has {len(target_units)}'
            ))
            # Use what we have
            min_units = min(len(source_units), len(target_units))
            source_units = source_units[:min_units]
            target_units = target_units[:min_units]

        # Create unit mapping (source unit -> target unit)
        unit_mapping = dict(zip([u.id for u in source_units], target_units))
        
        self.stdout.write(f'📊 Unit mapping created: {len(unit_mapping)} units')

        # Delete existing shifts for target home
        deleted_count = Shift.objects.filter(unit__in=target_units).delete()[0]
        if deleted_count > 0:
            self.stdout.write(f'🧹 Deleted {deleted_count} existing shifts')

        # Get all unique Orchard Grove staff from shifts
        orchard_staff_ids = source_shifts.values_list('user__sap', flat=True).distinct()
        orchard_staff = {
            u.sap: u for u in User.objects.filter(sap__in=orchard_staff_ids).select_related('role')
        }

        self.stdout.write(f'👥 Orchard Grove staff in rota: {len(orchard_staff)}')

        # Create staff mapping and clone staff
        staff_mapping = {}
        current_sap = start_sap

        with transaction.atomic():
            for source_sap, source_user in orchard_staff.items():
                # Generate new name
                new_first_name = self.generate_name(target_home.name, current_sap, 'first')
                new_last_name = self.generate_name(target_home.name, current_sap, 'last')
                new_sap = str(current_sap)

                # Find corresponding target unit
                source_unit_id = source_user.unit_id
                target_unit = unit_mapping.get(source_unit_id)
                
                if not target_unit:
                    # Assign to first available unit
                    target_unit = target_units[0]

                # Create new staff member
                new_user = User.objects.create(
                    sap=new_sap,
                    first_name=new_first_name,
                    last_name=new_last_name,
                    email=f'{new_sap}@{target_home.name.lower()}.care',
                    role=source_user.role,
                    unit=target_unit,
                    is_active=True,
                    shift_preference=source_user.shift_preference,
                    team=source_user.team,
                    annual_leave_allowance=source_user.annual_leave_allowance,
                    annual_leave_used=0,
                    annual_leave_year_start=source_user.annual_leave_year_start,
                    shifts_per_week_override=source_user.shifts_per_week_override
                )
                new_user.set_unusable_password()
                new_user.save()

                staff_mapping[source_sap] = new_user
                current_sap += 1

            self.stdout.write(f'✅ Created {len(staff_mapping)} new staff members (SAP {start_sap} to {current_sap-1})')

            # Clone shifts
            shifts_to_create = []
            for source_shift in source_shifts:
                target_unit = unit_mapping.get(source_shift.unit_id)
                target_user = staff_mapping.get(source_shift.user.sap)

                if target_unit and target_user:
                    shifts_to_create.append(Shift(
                        date=source_shift.date,
                        shift_type=source_shift.shift_type,
                        unit=target_unit,
                        user=target_user,
                        status=source_shift.status,
                        shift_classification=source_shift.shift_classification,
                        shift_pattern=source_shift.shift_pattern,
                        custom_start_time=source_shift.custom_start_time,
                        custom_end_time=source_shift.custom_end_time,
                        notes=f'Cloned from Orchard Grove'
                    ))

            # Bulk create shifts
            if shifts_to_create:
                Shift.objects.bulk_create(shifts_to_create, batch_size=1000)
                self.stdout.write(self.style.SUCCESS(f'✅ Created {len(shifts_to_create)} shifts'))
            else:
                self.stdout.write(self.style.WARNING('⚠️  No shifts created'))

        return current_sap

    def generate_name(self, home_name, sap_number, name_type):
        """Generate realistic Scottish names based on home and SAP number"""
        
        first_names = [
            'Ailsa', 'Angus', 'Bonnie', 'Bruce', 'Catriona', 'Craig', 'Duncan', 'Eilidh',
            'Fiona', 'Fraser', 'Heather', 'Iain', 'Isla', 'Jamie', 'Kirsty', 'Lachlan',
            'Morag', 'Niall', 'Rhona', 'Ross', 'Senga', 'Stuart', 'Una', 'Wallace',
            'Ava', 'Cameron', 'Elspeth', 'Gregor', 'Hannah', 'Kenneth', 'Lesley', 'Malcolm',
            'Nicola', 'Ewan', 'Shona', 'Andrew', 'Beth', 'Colin', 'Donna', 'Gordon'
        ]
        
        last_names = [
            'MacLeod', 'Campbell', 'MacDonald', 'Stewart', 'Robertson', 'Thomson', 'Anderson',
            'Scott', 'Murray', 'Wilson', 'Cameron', 'Ross', 'Ferguson', 'Grant', 'Mitchell',
            'Hamilton', 'Fraser', 'Wallace', 'Simpson', 'Kennedy', 'Gibson', 'Reid',
            'Crawford', 'Henderson', 'Graham', 'Duncan', 'Morrison', 'Douglas', 'Kelly',
            'MacKenzie', 'Johnston', 'Hunter', 'Gordon', 'Walker', 'Black', 'Armstrong'
        ]

        if name_type == 'first':
            return first_names[sap_number % len(first_names)]
        else:
            return last_names[sap_number % len(last_names)]
