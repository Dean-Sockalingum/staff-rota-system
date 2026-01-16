"""
Management command to export shift data for ML forecasting

Scottish Design Principles Applied:
- Data Minimization: Only exports fields needed for forecasting
- Privacy by Design: Anonymizes personal identifiers
- Transparency: Clear documentation of what data is exported
- Evidence-Based: Supports ML model validation and research

Usage:
    python manage.py export_shift_data --start-date 2024-01-01 --end-date 2024-12-31
    python manage.py export_shift_data --anonymize --days-back 365
    python manage.py export_shift_data --care-home "Orchard Grove" --output shifts.csv
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import datetime, timedelta
from scheduling.models import Shift, CareHome, Unit, Role, User
import csv
import os
import hashlib


class Command(BaseCommand):
    help = 'Export shift data for ML forecasting with optional anonymization'

    def add_arguments(self, parser):
        parser.add_argument(
            '--start-date',
            type=str,
            help='Start date (YYYY-MM-DD). Defaults to 1 year ago.'
        )
        parser.add_argument(
            '--end-date',
            type=str,
            help='End date (YYYY-MM-DD). Defaults to today.'
        )
        parser.add_argument(
            '--days-back',
            type=int,
            help='Alternative to start-date: export last N days of data'
        )
        parser.add_argument(
            '--care-home',
            type=str,
            help='Filter by care home name. Exports all homes if not specified.'
        )
        parser.add_argument(
            '--unit',
            type=str,
            help='Filter by unit name within care home.'
        )
        parser.add_argument(
            '--output',
            type=str,
            default='ml_data/shift_export.csv',
            help='Output CSV file path. Default: ml_data/shift_export.csv'
        )
        parser.add_argument(
            '--anonymize',
            action='store_true',
            help='Anonymize SAP numbers and staff names (GDPR compliance)'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Shift Data Export for ML ===\n'))

        # Parse date range
        end_date = self.parse_end_date(options)
        start_date = self.parse_start_date(options, end_date)

        self.stdout.write(f"Date range: {start_date.date()} to {end_date.date()}")

        # Build queryset
        shifts = Shift.objects.filter(
            date__gte=start_date.date(),
            date__lte=end_date.date()
        ).select_related(
            'user', 'user__role', 'shift_type', 'unit', 'unit__care_home'
        ).order_by('date', 'shift_type__name')

        # Apply filters
        if options['care_home']:
            shifts = shifts.filter(unit__care_home__name__icontains=options['care_home'])
            self.stdout.write(f"Filtering: Care home '{options['care_home']}'")

        if options['unit']:
            shifts = shifts.filter(unit__name__icontains=options['unit'])
            self.stdout.write(f"Filtering: Unit '{options['unit']}'")

        shift_count = shifts.count()
        if shift_count == 0:
            raise CommandError('No shifts found for the specified criteria.')

        self.stdout.write(f"Found: {shift_count} shifts")

        # Create output directory
        output_path = options['output']
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Export to CSV
        anonymize = options['anonymize']
        exported_count = self.export_shifts(shifts, output_path, anonymize)

        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n✓ Exported {exported_count} shifts to {output_path}'))
        if anonymize:
            self.stdout.write(self.style.WARNING('  ⚠ Data anonymized - SAP numbers hashed'))
        self.stdout.write(f'  File size: {os.path.getsize(output_path):,} bytes')

    def parse_end_date(self, options):
        """Parse end date from options or default to today"""
        if options['end_date']:
            try:
                return datetime.strptime(options['end_date'], '%Y-%m-%d')
            except ValueError:
                raise CommandError('Invalid end-date format. Use YYYY-MM-DD.')
        return timezone.now()

    def parse_start_date(self, options, end_date):
        """Parse start date from options or default to 1 year ago"""
        if options['start_date']:
            try:
                return datetime.strptime(options['start_date'], '%Y-%m-%d')
            except ValueError:
                raise CommandError('Invalid start-date format. Use YYYY-MM-DD.')
        elif options['days_back']:
            return end_date - timedelta(days=options['days_back'])
        else:
            return end_date - timedelta(days=365)  # Default: 1 year

    def anonymize_sap(self, sap):
        """Hash SAP number for anonymization"""
        return hashlib.sha256(sap.encode()).hexdigest()[:12]

    def export_shifts(self, shifts, output_path, anonymize):
        """Export shifts to CSV with optional anonymization"""
        
        # Define fields to export (data minimization)
        fieldnames = [
            'date',
            'day_of_week',
            'shift_type',
            'shift_hours',
            'care_home',
            'unit',
            'role',
            'is_management',
            'is_senior_management',
            'staff_sap',  # Anonymized if --anonymize flag
            'shift_classification',  # REGULAR, OVERTIME, AGENCY
            'agency_rate',
        ]

        with open(output_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for shift in shifts:
                # Skip shifts without user (should not happen, but safety check)
                if not shift.user:
                    continue

                row = {
                    'date': shift.date.isoformat(),
                    'day_of_week': shift.date.strftime('%A'),
                    'shift_type': shift.shift_type.name if shift.shift_type else 'Unknown',
                    'shift_hours': float(shift.shift_type.duration_hours) if shift.shift_type else 0,
                    'care_home': shift.unit.care_home.name if shift.unit and shift.unit.care_home else 'Unknown',
                    'unit': shift.unit.name if shift.unit else 'Unknown',
                    'role': shift.user.role.get_name_display() if shift.user.role else 'Unknown',
                    'is_management': shift.user.role.is_management if shift.user.role else False,
                    'is_senior_management': shift.user.role.is_senior_management_team if shift.user.role else False,
                    'staff_sap': self.anonymize_sap(shift.user.sap) if anonymize else shift.user.sap,
                    'shift_classification': shift.shift_classification,
                    'agency_rate': float(shift.agency_hourly_rate) if shift.agency_hourly_rate else 0,
                }

                writer.writerow(row)

        return shifts.count()
