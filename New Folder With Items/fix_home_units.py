import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import CareHome, Unit, User, Shift

# Define correct units for each home
CORRECT_UNITS = {
    'HAWTHORN_HOUSE': ['Thistle', 'Violet', 'Iris', 'Heather', 'Snowdrop', 'Bluebell', 'Daisy', 'Primrose', 'Mgmt'],
    'MEADOWBURN': ['Daisy', 'Aster', 'Poppy', 'Bluebell', 'Marigold', 'Foxglove', 'Cornflower', 'Honeysuckle', 'Mgmt'],
    'RIVERSIDE': ['Daffodil', 'Maple', 'Heather', 'Rose', 'Lily', 'Lotus', 'Orchid', 'Jasmine', 'Mgmt'],
}

def fix_home_units():
    """Update units for Hawthorn House, Meadowburn, and Riverside"""
    
    for home_name, unit_names in CORRECT_UNITS.items():
        try:
            home = CareHome.objects.get(name=home_name)
            print(f"\n{'='*60}")
            print(f"Fixing {home.get_name_display()}")
            print(f"{'='*60}")
            
            # Get existing units for this home
            existing_units = Unit.objects.filter(care_home=home)
            print(f"Current units: {[u.name for u in existing_units]}")
            
            # Deactivate old units (don't delete to preserve data integrity)
            for unit in existing_units:
                if not any(name in unit.name for name in unit_names):
                    unit.is_active = False
                    unit.save()
                    print(f"  ❌ Deactivated: {unit.name}")
            
            # Create or activate new units
            for unit_name in unit_names:
                full_name = f"{home_name}_{unit_name}"
                unit, created = Unit.objects.get_or_create(
                    name=full_name,
                    care_home=home,
                    defaults={'is_active': True}
                )
                if created:
                    print(f"  ✅ Created: {full_name}")
                else:
                    if not unit.is_active:
                        unit.is_active = True
                        unit.save()
                        print(f"  ✅ Reactivated: {full_name}")
                    else:
                        print(f"  ℹ️  Already exists: {full_name}")
            
            # Show final state
            active_units = Unit.objects.filter(care_home=home, is_active=True).order_by('name')
            print(f"\nFinal active units ({active_units.count()}):")
            for unit in active_units:
                staff_count = User.objects.filter(unit=unit).count()
                shift_count = Shift.objects.filter(unit=unit).count()
                print(f"  - {unit.name}: {staff_count} staff, {shift_count} shifts")
                
        except CareHome.DoesNotExist:
            print(f"❌ Home {home_name} not found!")
            continue
    
    print(f"\n{'='*60}")
    print("✅ Unit corrections complete!")
    print(f"{'='*60}\n")
    
    # Summary
    print("SUMMARY:")
    for home_name in ['HAWTHORN_HOUSE', 'MEADOWBURN', 'RIVERSIDE', 'ORCHARD_GROVE', 'VICTORIA_GARDENS']:
        try:
            home = CareHome.objects.get(name=home_name)
            active_units = Unit.objects.filter(care_home=home, is_active=True).order_by('name')
            print(f"\n{home.get_name_display()} ({active_units.count()} units):")
            for unit in active_units:
                clean = unit.name.split('_')[-1]
                print(f"  - {clean}")
        except CareHome.DoesNotExist:
            pass

if __name__ == '__main__':
    fix_home_units()
