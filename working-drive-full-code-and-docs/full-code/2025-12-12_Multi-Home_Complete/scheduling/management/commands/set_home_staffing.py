"""
Set specific staffing requirements for each care home
"""
from django.core.management.base import BaseCommand
from scheduling.models_multi_home import CareHome


class Command(BaseCommand):
    help = 'Set home-level staffing requirements'

    def handle(self, *args, **options):
        
        # Staffing requirements per home
        # Format: {home_name: (day_staff_min, day_staff_ideal, night_staff_min, night_staff_ideal)}
        staffing_requirements = {
            'HAWTHORN_HOUSE': {
                'day_staff_min': 18,
                'day_staff_ideal': 24,
                'night_staff_min': 18,
                'night_staff_ideal': 21,
            },
            # Add other homes as provided by user
        }
        
        for home_name, requirements in staffing_requirements.items():
            try:
                home = CareHome.objects.get(name=home_name)
                
                # Add fields if they don't exist (will need migration first)
                if hasattr(home, 'day_staff_min'):
                    home.day_staff_min = requirements['day_staff_min']
                    home.day_staff_ideal = requirements['day_staff_ideal']
                    home.night_staff_min = requirements['night_staff_min']
                    home.night_staff_ideal = requirements['night_staff_ideal']
                    home.save()
                    
                    self.stdout.write(
                        f'{home.get_name_display()}: '
                        f'Day {requirements["day_staff_min"]}/{requirements["day_staff_ideal"]}, '
                        f'Night {requirements["night_staff_min"]}/{requirements["night_staff_ideal"]}'
                    )
            except CareHome.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Home not found: {home_name}'))
        
        self.stdout.write(self.style.SUCCESS('✓ Staffing requirements updated'))
