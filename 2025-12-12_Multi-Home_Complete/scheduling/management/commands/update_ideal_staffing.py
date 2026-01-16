"""
Update ideal staffing levels to realistic values based on actual coverage patterns
"""
from django.core.management.base import BaseCommand
from scheduling.models import Unit


class Command(BaseCommand):
    help = 'Update ideal staffing levels for all units based on actual operational needs'

    def handle(self, *args, **options):
        # Based on the Head of Service dashboard showing typical coverage:
        # Day shifts: ~2 seniors + 17-18 staff per home = ideal of ~20-22 total
        # Night shifts: typically lower coverage
        
        units = Unit.objects.filter(is_active=True)
        
        self.stdout.write(self.style.WARNING(f'Updating ideal staffing for {units.count()} units...'))
        
        updated_count = 0
        for unit in units:
            # Skip MGMT units - they don't need shift coverage
            if 'MGMT' in unit.name:
                unit.ideal_day_staff = 0
                unit.ideal_night_staff = 0
                unit.save()
                self.stdout.write(f'  {unit.name}: Set to 0 (management unit)')
                updated_count += 1
                continue
            
            # For SRD (Special Residential Designation) units - higher needs
            if 'SRD' in unit.name:
                # Keep higher minimums, set ideals slightly above
                unit.ideal_day_staff = unit.min_day_staff + 1  # e.g., min 3 → ideal 4
                unit.ideal_night_staff = unit.min_night_staff + 1  # e.g., min 2 → ideal 3
            else:
                # For standard units
                unit.ideal_day_staff = unit.min_day_staff + 1  # e.g., min 2 → ideal 3, min 3 → ideal 4
                unit.ideal_night_staff = unit.min_night_staff + 1  # e.g., min 1 → ideal 2
            
            unit.save()
            self.stdout.write(
                f'  {unit.name}: Day {unit.min_day_staff}→{unit.ideal_day_staff}, '
                f'Night {unit.min_night_staff}→{unit.ideal_night_staff}'
            )
            updated_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Updated {updated_count} units with ideal staffing levels'))
        
        # Show totals per home
        from scheduling.models_multi_home import CareHome
        self.stdout.write(self.style.SUCCESS('\nHome-level staffing targets:'))
        for home in CareHome.objects.all():
            home_units = Unit.objects.filter(care_home=home, is_active=True)
            day_min = sum(u.min_day_staff for u in home_units)
            day_ideal = sum(u.ideal_day_staff for u in home_units)
            night_min = sum(u.min_night_staff for u in home_units)
            night_ideal = sum(u.ideal_night_staff for u in home_units)
            
            self.stdout.write(
                f'  {home.get_name_display()}: '
                f'Day {day_min} min / {day_ideal} ideal, '
                f'Night {night_min} min / {night_ideal} ideal'
            )
