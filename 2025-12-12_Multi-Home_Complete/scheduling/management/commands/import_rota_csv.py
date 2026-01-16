import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from scheduling.models import User, Unit

class Command(BaseCommand):
    help = 'Import rota data from a CSV and assign home units to staff.'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Path to the rota CSV file')

    def handle(self, *args, **options):
        csv_path = options['csv_path']
        if not os.path.exists(csv_path):
            self.stderr.write(self.style.ERROR(f'File not found: {csv_path}'))
            return

        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                sap = row.get('SAP')
                first_name = row.get('First')
                last_name = row.get('Surname')
                unit_name = row.get('Unit')
                if not sap or not unit_name:
                    continue
                # Get or create the unit
                unit, _ = Unit.objects.get_or_create(name=unit_name)
                # Get or create the user (staff)
                user, created = User.objects.get_or_create(sap=sap, defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': f"{sap}@example.com",  # Placeholder if email not in CSV
                })
                # Assign home unit
                user.home_unit = unit
                user.save()
                self.stdout.write(self.style.SUCCESS(f"{'Created' if created else 'Updated'} {first_name} {last_name} ({sap}) - Home Unit: {unit_name}"))
        self.stdout.write(self.style.SUCCESS('Rota import complete.'))
