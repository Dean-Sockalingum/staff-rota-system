"""
Management command to initialize the 5 Care Homes in the database.

Usage:
    python3 manage.py initialize_care_homes
    python3 manage.py initialize_care_homes --reset  # Drop existing and recreate
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from scheduling.models_multi_home import CareHome


class Command(BaseCommand):
    help = 'Initialize the 5 Care Homes with default configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing homes and recreate them',
        )

    def handle(self, *args, **options):
        reset = options['reset']

        if reset:
            self.stdout.write(self.style.WARNING('🗑️  Resetting all care homes...'))
            deleted_count, _ = CareHome.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'   Deleted {deleted_count} existing home(s)'))
            self.stdout.write('')

        existing_count = CareHome.objects.count()
        
        if existing_count > 0 and not reset:
            self.stdout.write(self.style.WARNING(
                f'⚠️  {existing_count} care home(s) already exist. Use --reset to recreate.'
            ))
            return

        # Care home configurations based on typical Scottish care home sizes
        care_homes = [
            {
                'name': 'ORCHARD_GROVE',
                'bed_capacity': 60,
                'current_occupancy': 57,
                'location_address': '123 Orchard Grove, Edinburgh',
                'postcode': 'EH12 7XY',
                'care_inspectorate_id': 'CS2023012345',
                'registration_number': 'REG-2023-OG',
            },
            {
                'name': 'MEADOWBURN',
                'bed_capacity': 45,
                'current_occupancy': 42,
                'location_address': '45 Meadowburn Road, Glasgow',
                'postcode': 'G12 9QQ',
                'care_inspectorate_id': 'CS2023012346',
                'registration_number': 'REG-2023-MB',
            },
            {
                'name': 'HAWTHORN_HOUSE',
                'bed_capacity': 38,
                'current_occupancy': 35,
                'location_address': '78 Hawthorn Lane, Aberdeen',
                'postcode': 'AB10 1XX',
                'care_inspectorate_id': 'CS2023012347',
                'registration_number': 'REG-2023-HH',
            },
            {
                'name': 'RIVERSIDE',
                'bed_capacity': 52,
                'current_occupancy': 48,
                'location_address': '91 Riverside Drive, Dundee',
                'postcode': 'DD1 4HH',
                'care_inspectorate_id': 'CS2023012348',
                'registration_number': 'REG-2023-RS',
            },
            {
                'name': 'VICTORIA_GARDENS',
                'bed_capacity': 40,
                'current_occupancy': 38,
                'location_address': '156 Victoria Gardens, Perth',
                'postcode': 'PH1 5LU',
                'care_inspectorate_id': 'CS2023012349',
                'registration_number': 'REG-2023-VG',
            },
        ]

        self.stdout.write(self.style.MIGRATE_HEADING('🏥 Initializing 5 Care Homes'))
        self.stdout.write('')

        created_homes = []
        
        with transaction.atomic():
            for home_data in care_homes:
                home = CareHome.objects.create(**home_data)
                created_homes.append(home)
                
                # Get display name
                display_name = dict(CareHome.HOME_CHOICES).get(home.name, home.name)
                
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ {display_name}')
                )
                self.stdout.write(f'     📍 {home.location_address}')
                self.stdout.write(f'     🛏️  Capacity: {home.current_occupancy}/{home.bed_capacity} beds')
                self.stdout.write(f'     📋 Care Inspectorate: {home.care_inspectorate_id}')
                self.stdout.write('')

        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS(f'✨ Successfully created {len(created_homes)} care homes'))
        self.stdout.write('')
        self.stdout.write('Total capacity across all homes:')
        total_capacity = sum(h.bed_capacity for h in created_homes)
        total_occupancy = sum(h.current_occupancy for h in created_homes)
        occupancy_pct = (total_occupancy / total_capacity * 100) if total_capacity > 0 else 0
        
        self.stdout.write(f'  🛏️  Total beds: {total_capacity}')
        self.stdout.write(f'  👥 Total residents: {total_occupancy}')
        self.stdout.write(f'  📊 Overall occupancy: {occupancy_pct:.1f}%')
        self.stdout.write('')
        self.stdout.write('Next steps:')
        self.stdout.write('  1. Assign units to care homes')
        self.stdout.write('  2. Configure home-specific settings')
        self.stdout.write('  3. Set up senior management dashboard')
        self.stdout.write('=' * 70)
