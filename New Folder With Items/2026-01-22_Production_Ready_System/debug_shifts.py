import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from datetime import date
from scheduling.models import Shift, Unit
from scheduling.models_multi_home import CareHome

today = date(2025, 12, 18)

print(f"\n=== Shift Analysis for {today} ===\n")

for home in CareHome.objects.all().order_by('name'):
    print(f"\n{home.get_name_display()}:")
    units = Unit.objects.filter(care_home=home, is_active=True)
    print(f"  Active units: {units.count()}")
    
    # Get shifts for today
    shifts = Shift.objects.filter(
        date=today,
        unit__in=units,
        status__in=['SCHEDULED', 'CONFIRMED']
    ).select_related('user', 'shift_type', 'unit')
    
    day_shifts = shifts.filter(shift_type__name__icontains='DAY')
    night_shifts = shifts.filter(shift_type__name__icontains='NIGHT')
    
    print(f"  Day shifts (total records): {day_shifts.count()}")
    print(f"  Night shifts (total records): {night_shifts.count()}")
    
    # Count unique users
    day_users = day_shifts.values('user').distinct()
    night_users = night_shifts.values('user').distinct()
    
    print(f"  Day shifts (unique users): {day_users.count()}")
    print(f"  Night shifts (unique users): {night_users.count()}")
    
    # Show sample of shifts
    if day_shifts.count() > 0:
        print(f"\n  Sample day shifts:")
        for shift in day_shifts[:5]:
            print(f"    - {shift.user.first_name} {shift.user.last_name} ({shift.unit.name}) - {shift.shift_type.name} - {shift.status}")
