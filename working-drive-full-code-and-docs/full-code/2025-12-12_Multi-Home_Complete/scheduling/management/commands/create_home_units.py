"""
Management command to create units for the other 4 care homes.

Usage:
    python3 manage.py create_home_units
    python3 manage.py create_home_units --reset  # Delete and recreate units
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from scheduling.models import Unit
from scheduling.models_multi_home import CareHome


class Command(BaseCommand):
    help = 'Create units for Meadowburn, Hawthorn House, Riverside, and Victoria Gardens'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing units for these homes and recreate them',
        )

    def handle(self, *args, **options):
        reset = options['reset']

        # Define units for each home
        # Meadowburn: 9 units (45 beds)
        # Hawthorn House: 9 units (38 beds)
        # Riverside: 9 units (52 beds)
        # Victoria Gardens: 6 units (40 beds)
        
        home_units = {
            'MEADOWBURN': [
                {'name': 'MEADOW_RED', 'description': 'Red Unit', 'min_day': 3, 'min_night': 2},
                {'name': 'MEADOW_BLUE', 'description': 'Blue Unit', 'min_day': 3, 'min_night': 2},
                {'name': 'MEADOW_GREEN', 'description': 'Green Unit', 'min_day': 3, 'min_night': 2},
                {'name': 'MEADOW_YELLOW', 'description': 'Yellow Unit', 'min_day': 3, 'min_night': 2},
                {'name': 'MEADOW_PURPLE', 'description': 'Purple Unit', 'min_day': 3, 'min_night': 2},
                {'name': 'MEADOW_ORANGE', 'description': 'Orange Unit', 'min_day': 3, 'min_night': 2},
                {'name': 'MEADOW_PINK', 'description': 'Pink Unit', 'min_day': 3, 'min_night': 2},
                {'name': 'MEADOW_WHITE', 'description': 'White Unit', 'min_day': 3, 'min_night': 2},
                {'name': 'MEADOW_MGMT', 'description': 'Management', 'min_day': 3, 'min_night': 0},
            ],
            'HAWTHORN_HOUSE': [
                {'name': 'HAWTHORN_AMBER', 'description': 'Amber Unit', 'min_day': 3, 'min_night': 2},
                {'name': 'HAWTHORN_BIRCH', 'description': 'Birch Unit', 'min_day': 3, 'min_night': 2},
                {'name': 'HAWTHORN_CEDAR', 'description': 'Cedar Unit', 'min_day': 3, 'min_night': 2},
                {'name': 'HAWTHORN_ELDER', 'description': 'Elder Unit', 'min_day': 3, 'min_night': 2},
                {'name': 'HAWTHORN_HOLLY', 'description': 'Holly Unit', 'min_day': 3, 'min_night': 2},
                {'name': 'HAWTHORN_MAPLE', 'description': 'Maple Unit', 'min_day': 2, 'min_night': 1},
                {'name': 'HAWTHORN_OAK', 'description': 'Oak Unit', 'min_day': 2, 'min_night': 1},
                {'name': 'HAWTHORN_WILLOW', 'description': 'Willow Unit', 'min_day': 2, 'min_night': 1},
                {'name': 'HAWTHORN_MGMT', 'description': 'Management', 'min_day': 3, 'min_night': 0},
            ],
            'RIVERSIDE': [
                {'name': 'RIVERSIDE_NORTH1', 'description': 'North Unit 1', 'min_day': 3, 'min_night': 2},
                {'name': 'RIVERSIDE_NORTH2', 'description': 'North Unit 2', 'min_day': 3, 'min_night': 2},
                {'name': 'RIVERSIDE_NORTH3', 'description': 'North Unit 3', 'min_day': 3, 'min_night': 2},
                {'name': 'RIVERSIDE_SOUTH1', 'description': 'South Unit 1', 'min_day': 3, 'min_night': 2},
                {'name': 'RIVERSIDE_SOUTH2', 'description': 'South Unit 2', 'min_day': 3, 'min_night': 2},
                {'name': 'RIVERSIDE_SOUTH3', 'description': 'South Unit 3', 'min_day': 3, 'min_night': 2},
                {'name': 'RIVERSIDE_EAST', 'description': 'East Unit', 'min_day': 3, 'min_night': 2},
                {'name': 'RIVERSIDE_WEST', 'description': 'West Unit', 'min_day': 3, 'min_night': 2},
                {'name': 'RIVERSIDE_MGMT', 'description': 'Management', 'min_day': 3, 'min_night': 0},
            ],
            'VICTORIA_GARDENS': [
                {'name': 'VICTORIA_ROSE', 'description': 'Rose Wing', 'min_day': 3, 'min_night': 2},
                {'name': 'VICTORIA_LILY', 'description': 'Lily Wing', 'min_day': 3, 'min_night': 2},
                {'name': 'VICTORIA_DAISY', 'description': 'Daisy Wing', 'min_day': 3, 'min_night': 2},
                {'name': 'VICTORIA_TULIP', 'description': 'Tulip Wing', 'min_day': 3, 'min_night': 2},
                {'name': 'VICTORIA_IRIS', 'description': 'Iris Wing', 'min_day': 2, 'min_night': 1},
                {'name': 'VICTORIA_MGMT', 'description': 'Management', 'min_day': 3, 'min_night': 0},
            ],
        }

        self.stdout.write(self.style.MIGRATE_HEADING('🏥 Creating Units for 4 Care Homes'))
        self.stdout.write('')

        total_created = 0
        total_deleted = 0

        for home_code, units_data in home_units.items():
            try:
                care_home = CareHome.objects.get(name=home_code)
            except CareHome.DoesNotExist:
                self.stdout.write(self.style.ERROR(
                    f'❌ {home_code} not found. Run "python3 manage.py initialize_care_homes" first.'
                ))
                continue

            home_display = care_home.get_name_display()
            self.stdout.write(self.style.SUCCESS(f'📍 {home_display}'))

            if reset:
                deleted_count = Unit.objects.filter(care_home=care_home).delete()[0]
                if deleted_count > 0:
                    total_deleted += deleted_count
                    self.stdout.write(f'   🗑️  Deleted {deleted_count} existing unit(s)')

            with transaction.atomic():
                for unit_data in units_data:
                    # Check if unit already exists
                    existing = Unit.objects.filter(name=unit_data['name']).first()
                    
                    if existing and not reset:
                        self.stdout.write(self.style.WARNING(
                            f'   ⚠️  {unit_data["name"]} already exists - skipping'
                        ))
                        continue

                    unit = Unit.objects.create(
                        name=unit_data['name'],
                        description=unit_data['description'],
                        care_home=care_home,
                        is_active=True,
                        min_day_staff=unit_data['min_day'],
                        min_night_staff=unit_data['min_night'],
                        min_weekend_staff=unit_data['min_day'],  # Same as weekday for now
                    )
                    
                    total_created += 1
                    self.stdout.write(
                        f'   ✅ {unit.name} - Day: {unit.min_day_staff}, Night: {unit.min_night_staff}'
                    )

            self.stdout.write('')

        self.stdout.write('=' * 70)
        if total_deleted > 0:
            self.stdout.write(self.style.WARNING(f'🗑️  Deleted {total_deleted} existing unit(s)'))
        self.stdout.write(self.style.SUCCESS(f'✨ Created {total_created} new unit(s)'))
        self.stdout.write('')

        # Summary by home
        self.stdout.write('Unit Distribution:')
        for home_code in home_units.keys():
            try:
                care_home = CareHome.objects.get(name=home_code)
                unit_count = Unit.objects.filter(care_home=care_home).count()
                home_display = care_home.get_name_display()
                self.stdout.write(f'  • {home_display:<20} {unit_count} units')
            except CareHome.DoesNotExist:
                pass

        # Include Orchard Grove in summary
        try:
            orchard_grove = CareHome.objects.get(name='ORCHARD_GROVE')
            og_count = Unit.objects.filter(care_home=orchard_grove).count()
            self.stdout.write(f'  • Orchard Grove         {og_count} units')
        except CareHome.DoesNotExist:
            pass

        self.stdout.write('')
        total_units = Unit.objects.count()
        self.stdout.write(f'📊 Total units across all homes: {total_units}')
        self.stdout.write('=' * 70)
