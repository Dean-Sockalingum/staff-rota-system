"""
Management command to generate future shifts based on 3-week rolling rota pattern.
This ensures the rota continues indefinitely without manual intervention.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import date, timedelta
from scheduling.models import Shift, User
from collections import defaultdict


class Command(BaseCommand):
    help = 'Generates future shifts based on 3-week rolling rota pattern'

    def add_arguments(self, parser):
        parser.add_argument(
            '--weeks',
            type=int,
            default=26,
            help='Number of weeks ahead to generate (default: 26 weeks / 6 months)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regeneration even if shifts already exist'
        )

    def handle(self, *args, **options):
        weeks_ahead = options['weeks']
        force = options['force']

        self.stdout.write(self.style.SUCCESS(
            f'\n=== Generating {weeks_ahead} weeks of future shifts ===\n'
        ))

        # Find the last shift date in the database
        last_shift = Shift.objects.order_by('-date').first()
        if not last_shift:
            self.stdout.write(self.style.ERROR('No existing shifts found in database!'))
            return

        last_date = last_shift.date
        self.stdout.write(f'Last shift in database: {last_date}')

        # Calculate target end date
        today = timezone.now().date()
        target_end_date = today + timedelta(weeks=weeks_ahead)
        
        # If we already have shifts beyond the target date and not forcing, exit
        if last_date >= target_end_date and not force:
            self.stdout.write(self.style.SUCCESS(
                f'Shifts already exist until {last_date}, which is beyond target {target_end_date}. Use --force to regenerate.'
            ))
            return

        # Define the 3-week pattern period (21 days)
        pattern_days = 21
        
        # Find the reference pattern by looking at the most recent complete 3-week cycle
        # We'll use the last 3 weeks as the pattern to replicate
        pattern_start = last_date - timedelta(days=pattern_days - 1)
        pattern_end = last_date
        
        self.stdout.write(f'Using pattern from {pattern_start} to {pattern_end}')
        
        # Get all shifts in the pattern period, organized by date
        pattern_shifts = Shift.objects.filter(
            date__gte=pattern_start,
            date__lte=pattern_end
        ).select_related('user', 'unit', 'shift_type').order_by('date')
        
        if not pattern_shifts.exists():
            self.stdout.write(self.style.ERROR('No pattern shifts found!'))
            return
        
        # Organize pattern by day offset (0-20 for 21 days)
        pattern_by_day = defaultdict(list)
        for shift in pattern_shifts:
            day_offset = (shift.date - pattern_start).days
            pattern_by_day[day_offset].append({
                'user': shift.user,
                'unit': shift.unit,
                'shift_type': shift.shift_type,
                'status': shift.status,
                'shift_classification': shift.shift_classification,
                'shift_pattern': shift.shift_pattern,
                'custom_start_time': shift.custom_start_time,
                'custom_end_time': shift.custom_end_time,
                'agency_company': shift.agency_company,
                'agency_staff_name': shift.agency_staff_name,
                'agency_hourly_rate': shift.agency_hourly_rate,
                'notes': shift.notes,
            })
        
        self.stdout.write(f'Pattern contains {len(pattern_shifts)} shifts across {len(pattern_by_day)} days')
        
        # Generate shifts from last_date + 1 day until target_end_date
        start_generation = last_date + timedelta(days=1)
        current_date = start_generation
        
        shifts_to_create = []
        created_count = 0
        skipped_count = 0
        
        self.stdout.write(f'\nGenerating shifts from {start_generation} to {target_end_date}...')
        
        with transaction.atomic():
            while current_date <= target_end_date:
                # Calculate which day in the 3-week cycle this is
                days_since_pattern_start = (current_date - pattern_start).days
                pattern_day = days_since_pattern_start % pattern_days
                
                # Get the template shifts for this day in the cycle
                template_shifts = pattern_by_day.get(pattern_day, [])
                
                if template_shifts:
                    # Check if shifts already exist for this date
                    existing_shifts = Shift.objects.filter(date=current_date)
                    if existing_shifts.exists() and not force:
                        skipped_count += len(template_shifts)
                    else:
                        # Delete existing shifts if forcing
                        if force and existing_shifts.exists():
                            deleted_count = existing_shifts.delete()[0]
                            self.stdout.write(f'  Deleted {deleted_count} existing shifts for {current_date}')
                        
                        # Create new shifts based on pattern
                        for template in template_shifts:
                            shift = Shift(
                                date=current_date,
                                user=template['user'],
                                unit=template['unit'],
                                shift_type=template['shift_type'],
                                status=template['status'],
                                shift_classification=template['shift_classification'],
                                shift_pattern=template['shift_pattern'],
                                custom_start_time=template['custom_start_time'],
                                custom_end_time=template['custom_end_time'],
                                agency_company=template['agency_company'],
                                agency_staff_name=template['agency_staff_name'],
                                agency_hourly_rate=template['agency_hourly_rate'],
                                notes=template['notes'],
                            )
                            shifts_to_create.append(shift)
                            created_count += 1
                
                # Bulk create every 1000 shifts to avoid memory issues
                if len(shifts_to_create) >= 1000:
                    Shift.objects.bulk_create(shifts_to_create, batch_size=500)
                    self.stdout.write(f'  Created batch: {len(shifts_to_create)} shifts')
                    shifts_to_create = []
                
                current_date += timedelta(days=1)
            
            # Create remaining shifts
            if shifts_to_create:
                Shift.objects.bulk_create(shifts_to_create, batch_size=500)
                self.stdout.write(f'  Created final batch: {len(shifts_to_create)} shifts')
        
        self.stdout.write(self.style.SUCCESS(
            f'\n=== Shift Generation Complete ===\n'
            f'Created: {created_count} new shifts\n'
            f'Skipped: {skipped_count} existing shifts\n'
            f'Coverage: {start_generation} to {target_end_date}\n'
        ))
        
        # Verify final coverage
        new_last_shift = Shift.objects.order_by('-date').first()
        self.stdout.write(self.style.SUCCESS(
            f'Database now contains shifts until: {new_last_shift.date}\n'
        ))
