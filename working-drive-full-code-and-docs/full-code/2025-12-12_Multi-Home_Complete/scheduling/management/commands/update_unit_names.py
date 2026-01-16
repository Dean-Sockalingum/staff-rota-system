"""
Management command to update unit names to match the correct facility naming
"""
from django.core.management.base import BaseCommand
from scheduling.models import CareHome, Unit

class Command(BaseCommand):
    help = 'Update unit names to correct facility names'

    def handle(self, *args, **options):
        # Define the mapping from old names to new names for each home
        # Based on the actual unit names from the spreadsheet
        # Note: Unit names must be unique across all homes
        unit_mappings = {
            'MEADOWBURN': [
                'MB_DAISY', 'MB_ASTER', 'MB_POPPY_SRD', 'MB_BLUEBELL', 'MB_MARIGOLD', 
                'MB_FOXGLOVE', 'MB_CORNFLOWER', 'MB_HONEYSUCKLE', 'MB_MGMT'
            ],
            'ORCHARD_GROVE': [
                'OG_PEAR', 'OG_GRAPE', 'OG_ORANGE', 'OG_CHERRY', 'OG_BRAMLEY', 
                'OG_PLUM', 'OG_PEACH', 'OG_STRAWBERRY', 'OG_MGMT'
            ],
            'RIVERSIDE': [
                'RS_DAFFODIL', 'RS_MAPLE', 'RS_HEATHER', 'RS_ROSE', 'RS_LILY', 
                'RS_LOTUS', 'RS_ORCHID', 'RS_JASMINE', 'RS_MGMT'
            ],
            'VICTORIA_GARDENS': [
                'VG_CROCUS', 'VG_LILY', 'VG_ROSE', 'VG_TULIP', 'VG_MGMT'
            ],
            'HAWTHORN_HOUSE': [
                'HH_THISTLE_SRD', 'HH_VIOLET', 'HH_IRIS', 'HH_HEATHER', 'HH_SNOWDROP_SRD', 
                'HH_BLUEBELL', 'HH_DAISY', 'HH_PRIMROSE', 'HH_MGMT'
            ]
        }

        total_updated = 0
        
        for home_name, new_names in unit_mappings.items():
            try:
                home = CareHome.objects.get(name=home_name)
                units = list(home.units.all().order_by('id'))
                
                self.stdout.write(f"\n{home_name}:")
                
                for idx, new_name in enumerate(new_names):
                    if idx < len(units):
                        unit = units[idx]
                        old_name = unit.name
                        unit.name = new_name
                        unit.save()
                        total_updated += 1
                        self.stdout.write(f"  Updated: {old_name} → {new_name}")
                    else:
                        self.stdout.write(self.style.WARNING(
                            f"  Skipped index {idx} - only {len(units)} units found"
                        ))
                        
            except CareHome.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Home not found: {home_name}"))
        
        self.stdout.write(self.style.SUCCESS(
            f"\n✓ Successfully updated {total_updated} units"
        ))
        
        # Verify the changes
        self.stdout.write("\n=== Verification ===")
        for home in CareHome.objects.all():
            units = home.units.all().order_by('id')
            self.stdout.write(f"\n{home.name} ({units.count()} units):")
            for unit in units:
                self.stdout.write(f"  - {unit.name}")
