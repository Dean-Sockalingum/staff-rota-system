"""
Generate rotas for multiple care homes

This command generates 6-week rotas for specified care homes, taking into account:
- Staff assigned to each home's units
- Unit-specific staffing requirements
- Individual shift preferences
- Admin day requirements

Usage:
    python3 manage.py generate_multi_home_rotas --homes 2,3,4,5
    python3 manage.py generate_multi_home_rotas --homes 2 --start-date 2025-12-16
    python3 manage.py generate_multi_home_rotas --all
"""

from collections import defaultdict
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from scheduling.models import Shift, ShiftType, Unit, User, CareHome


class Command(BaseCommand):
    help = 'Generate 6-week rotas for specified care homes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--homes',
            type=str,
            help='Comma-separated list of care home IDs (e.g., "2,3,4,5")'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Generate rotas for all homes except Orchard Grove (ID 1)'
        )
        parser.add_argument(
            '--start-date',
            type=str,
            help='Start date in YYYY-MM-DD format. Defaults to today.'
        )

    def handle(self, *args, **options):
        # Determine which homes to process
        if options['all']:
            homes = CareHome.objects.exclude(id=1).order_by('name')
        elif options['homes']:
            home_ids = [int(x.strip()) for x in options['homes'].split(',')]
            homes = CareHome.objects.filter(id__in=home_ids).order_by('name')
        else:
            self.stderr.write(self.style.ERROR('❌ Please specify --homes or --all'))
            return

        if not homes.exists():
            self.stderr.write(self.style.ERROR('❌ No care homes found matching criteria'))
            return

        # Parse start date
        if options['start_date']:
            start_date = date.fromisoformat(options['start_date'])
        else:
            start_date = date.today()

        end_date = start_date + timedelta(weeks=6)

        self.stdout.write(self.style.SUCCESS(f'\n{"="*70}'))
        self.stdout.write(self.style.SUCCESS('🏥 MULTI-HOME ROTA GENERATION'))
        self.stdout.write(self.style.SUCCESS(f'{"="*70}'))
        self.stdout.write(f'📅 Period: {start_date} to {end_date - timedelta(days=1)}')
        self.stdout.write(f'🏠 Homes: {homes.count()}\n')

        # Load shift types
        try:
            shift_types = {
                'DAY_SENIOR': ShiftType.objects.get(name='DAY_SENIOR'),
                'DAY_ASSISTANT': ShiftType.objects.get(name='DAY_ASSISTANT'),
                'NIGHT_SENIOR': ShiftType.objects.get(name='NIGHT_SENIOR'),
                'NIGHT_ASSISTANT': ShiftType.objects.get(name='NIGHT_ASSISTANT'),
            }
        except ShiftType.DoesNotExist as e:
            self.stderr.write(self.style.ERROR(f'❌ Missing shift type: {e}'))
            return

        total_shifts_created = 0

        # Process each home
        for home in homes:
            self.stdout.write(f'\n{"-"*70}')
            self.stdout.write(self.style.SUCCESS(f'🏥 {home.get_name_display()}'))
            self.stdout.write(f'{"-"*70}')

            shifts_created = self.generate_home_rota(
                home, start_date, end_date, shift_types
            )
            total_shifts_created += shifts_created

        self.stdout.write(f'\n{"="*70}')
        self.stdout.write(self.style.SUCCESS(f'✅ COMPLETE: {total_shifts_created} shifts created across {homes.count()} homes'))
        self.stdout.write(f'{"="*70}\n')

    def generate_home_rota(self, home, start_date, end_date, shift_types):
        """Generate rota for a single care home"""
        
        # Get units for this home (excluding management unit)
        care_units = list(
            Unit.objects.filter(care_home=home, is_active=True)
            .exclude(name__icontains='MGMT')
            .order_by('name')
        )

        if not care_units:
            self.stdout.write(self.style.WARNING(f'⚠️  No active care units found'))
            return 0

        # Get staff assigned to this home's units
        unit_ids = [unit.id for unit in care_units]
        
        day_senior_staff = list(
            User.objects.filter(
                unit_id__in=unit_ids,
                is_active=True,
                role__name__in=['SCW', 'SSCW'],
                shift_preference='DAY_SENIOR'
            ).select_related('role', 'unit')
        )

        night_senior_staff = list(
            User.objects.filter(
                unit_id__in=unit_ids,
                is_active=True,
                role__name__in=['SCW', 'SSCW'],
                shift_preference='NIGHT_SENIOR'
            ).select_related('role', 'unit')
        )

        day_assistant_staff = list(
            User.objects.filter(
                unit_id__in=unit_ids,
                is_active=True,
                role__name='SCA',
                shift_preference='DAY_ASSISTANT'
            ).select_related('role', 'unit')
        )

        night_assistant_staff = list(
            User.objects.filter(
                unit_id__in=unit_ids,
                is_active=True,
                role__name='SCA',
                shift_preference='NIGHT_ASSISTANT'
            ).select_related('role', 'unit')
        )

        self.stdout.write(f'📊 Units: {len(care_units)}')
        self.stdout.write(f'👥 Staff: Day Senior: {len(day_senior_staff)}, Night Senior: {len(night_senior_staff)}, '
                         f'Day Assistant: {len(day_assistant_staff)}, Night Assistant: {len(night_assistant_staff)}')

        if not day_senior_staff or not night_senior_staff:
            self.stdout.write(self.style.WARNING(f'⚠️  Insufficient senior staff - generating with available staff'))

        if not day_assistant_staff or not night_assistant_staff:
            self.stdout.write(self.style.WARNING(f'⚠️  Insufficient assistant staff - generating with available staff'))

        # Delete existing shifts for this home in the date range
        deleted_count = Shift.objects.filter(
            unit__in=care_units,
            date__gte=start_date,
            date__lt=end_date
        ).delete()[0]
        
        if deleted_count > 0:
            self.stdout.write(f'🧹 Cleared {deleted_count} existing shifts')

        # Generate shifts
        shifts_to_create = []
        current_date = start_date

        # Track staff already assigned on each date/shift_type to avoid UNIQUE constraint
        assigned_staff_per_date = defaultdict(lambda: defaultdict(set))
        
        # Simple round-robin assignment
        day_senior_idx = 0
        night_senior_idx = 0
        day_assistant_idx = 0
        night_assistant_idx = 0

        while current_date < end_date:
            for unit in care_units:
                # Day senior shifts (need min_day_staff, typically 2)
                for _ in range(unit.min_day_staff):
                    if day_senior_staff:
                        # Find next available staff member not already assigned today
                        for attempt in range(len(day_senior_staff)):
                            staff = day_senior_staff[day_senior_idx % len(day_senior_staff)]
                            day_senior_idx += 1
                            
                            if staff.sap not in assigned_staff_per_date[current_date]['DAY_SENIOR']:
                                assigned_staff_per_date[current_date]['DAY_SENIOR'].add(staff.sap)
                                shifts_to_create.append(Shift(
                                    date=current_date,
                                    shift_type=shift_types['DAY_SENIOR'],
                                    unit=unit,
                                    user=staff,
                                    status='SCHEDULED',
                                    shift_classification='REGULAR'
                                ))
                                break

                # Day assistant shifts
                for _ in range(unit.min_day_staff):
                    if day_assistant_staff:
                        for attempt in range(len(day_assistant_staff)):
                            staff = day_assistant_staff[day_assistant_idx % len(day_assistant_staff)]
                            day_assistant_idx += 1
                            
                            if staff.sap not in assigned_staff_per_date[current_date]['DAY_ASSISTANT']:
                                assigned_staff_per_date[current_date]['DAY_ASSISTANT'].add(staff.sap)
                                shifts_to_create.append(Shift(
                                    date=current_date,
                                    shift_type=shift_types['DAY_ASSISTANT'],
                                    unit=unit,
                                    user=staff,
                                    status='SCHEDULED',
                                    shift_classification='REGULAR'
                                ))
                                break

                # Night senior shifts (need min_night_staff, typically 1)
                for _ in range(unit.min_night_staff):
                    if night_senior_staff:
                        for attempt in range(len(night_senior_staff)):
                            staff = night_senior_staff[night_senior_idx % len(night_senior_staff)]
                            night_senior_idx += 1
                            
                            if staff.sap not in assigned_staff_per_date[current_date]['NIGHT_SENIOR']:
                                assigned_staff_per_date[current_date]['NIGHT_SENIOR'].add(staff.sap)
                                shifts_to_create.append(Shift(
                                    date=current_date,
                                    shift_type=shift_types['NIGHT_SENIOR'],
                                    unit=unit,
                                    user=staff,
                                    status='SCHEDULED',
                                    shift_classification='REGULAR'
                                ))
                                break

                # Night assistant shifts
                for _ in range(unit.min_night_staff):
                    if night_assistant_staff:
                        for attempt in range(len(night_assistant_staff)):
                            staff = night_assistant_staff[night_assistant_idx % len(night_assistant_staff)]
                            night_assistant_idx += 1
                            
                            if staff.sap not in assigned_staff_per_date[current_date]['NIGHT_ASSISTANT']:
                                assigned_staff_per_date[current_date]['NIGHT_ASSISTANT'].add(staff.sap)
                                shifts_to_create.append(Shift(
                                    date=current_date,
                                    shift_type=shift_types['NIGHT_ASSISTANT'],
                                    unit=unit,
                                    user=staff,
                                    status='SCHEDULED',
                                    shift_classification='REGULAR'
                                ))
                                break

            current_date += timedelta(days=1)

        # Bulk create shifts
        if shifts_to_create:
            with transaction.atomic():
                Shift.objects.bulk_create(shifts_to_create, batch_size=500)
            
            self.stdout.write(self.style.SUCCESS(f'✅ Created {len(shifts_to_create)} shifts'))
            return len(shifts_to_create)
        else:
            self.stdout.write(self.style.WARNING(f'⚠️  No shifts created - check staff assignments'))
            return 0
