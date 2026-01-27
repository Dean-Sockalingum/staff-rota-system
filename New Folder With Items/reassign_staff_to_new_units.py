import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import CareHome, Unit, User, Shift

# Mapping of old units to new units for each home
UNIT_MAPPINGS = {
    'HAWTHORN_HOUSE': {
        'HAWTHORN_HOUSE_Bramley': 'HAWTHORN_HOUSE_Thistle',
        'HAWTHORN_HOUSE_Cherry': 'HAWTHORN_HOUSE_Violet',
        'HAWTHORN_HOUSE_Grape': 'HAWTHORN_HOUSE_Iris',
        'HAWTHORN_HOUSE_Orange': 'HAWTHORN_HOUSE_Heather',
        'HAWTHORN_HOUSE_Peach': 'HAWTHORN_HOUSE_Snowdrop',
        'HAWTHORN_HOUSE_Pear': 'HAWTHORN_HOUSE_Bluebell',
        'HAWTHORN_HOUSE_Plum': 'HAWTHORN_HOUSE_Daisy',
        'HAWTHORN_HOUSE_Strawberry': 'HAWTHORN_HOUSE_Primrose',
    },
    'MEADOWBURN': {
        'MEADOWBURN_Bramley': 'MEADOWBURN_Daisy',
        'MEADOWBURN_Cherry': 'MEADOWBURN_Aster',
        'MEADOWBURN_Grape': 'MEADOWBURN_Poppy',
        'MEADOWBURN_Orange': 'MEADOWBURN_Bluebell',
        'MEADOWBURN_Peach': 'MEADOWBURN_Marigold',
        'MEADOWBURN_Pear': 'MEADOWBURN_Foxglove',
        'MEADOWBURN_Plum': 'MEADOWBURN_Cornflower',
        'MEADOWBURN_Strawberry': 'MEADOWBURN_Honeysuckle',
    },
    'RIVERSIDE': {
        'RIVERSIDE_Bramley': 'RIVERSIDE_Daffodil',
        'RIVERSIDE_Cherry': 'RIVERSIDE_Maple',
        'RIVERSIDE_Grape': 'RIVERSIDE_Heather',
        'RIVERSIDE_Orange': 'RIVERSIDE_Rose',
        'RIVERSIDE_Peach': 'RIVERSIDE_Lily',
        'RIVERSIDE_Pear': 'RIVERSIDE_Lotus',
        'RIVERSIDE_Plum': 'RIVERSIDE_Orchid',
        'RIVERSIDE_Strawberry': 'RIVERSIDE_Jasmine',
    }
}

def reassign_staff_and_shifts():
    """Reassign staff and shifts from old units to new units"""
    
    total_staff_updated = 0
    total_shifts_updated = 0
    
    for home_name, mappings in UNIT_MAPPINGS.items():
        print(f"\n{'='*60}")
        print(f"Processing {home_name}")
        print(f"{'='*60}")
        
        for old_unit_name, new_unit_name in mappings.items():
            try:
                old_unit = Unit.objects.get(name=old_unit_name)
                new_unit = Unit.objects.get(name=new_unit_name)
                
                # Update staff assignments
                staff_count = User.objects.filter(unit=old_unit).count()
                if staff_count > 0:
                    User.objects.filter(unit=old_unit).update(unit=new_unit)
                    print(f"  ✅ {old_unit_name} → {new_unit_name}: {staff_count} staff")
                    total_staff_updated += staff_count
                
                # Update shift assignments
                shift_count = Shift.objects.filter(unit=old_unit).count()
                if shift_count > 0:
                    Shift.objects.filter(unit=old_unit).update(unit=new_unit)
                    print(f"     {shift_count} shifts reassigned")
                    total_shifts_updated += shift_count
                    
            except Unit.DoesNotExist as e:
                print(f"  ⚠️  Unit not found: {e}")
                continue
    
    print(f"\n{'='*60}")
    print(f"✅ COMPLETE!")
    print(f"{'='*60}")
    print(f"Total staff updated: {total_staff_updated}")
    print(f"Total shifts updated: {total_shifts_updated}")
    
    # Verify results
    print(f"\n{'='*60}")
    print("VERIFICATION")
    print(f"{'='*60}")
    for home_name in ['HAWTHORN_HOUSE', 'MEADOWBURN', 'RIVERSIDE']:
        home = CareHome.objects.get(name=home_name)
        active_units = Unit.objects.filter(care_home=home, is_active=True).order_by('name')
        print(f"\n{home.get_name_display()}:")
        for unit in active_units:
            staff_count = User.objects.filter(unit=unit).count()
            shift_count = Shift.objects.filter(unit=unit).count()
            if staff_count > 0 or shift_count > 0:
                clean_name = unit.name.split('_')[-1]
                print(f"  {clean_name}: {staff_count} staff, {shift_count} shifts")

if __name__ == '__main__':
    reassign_staff_and_shifts()
