#!/usr/bin/env python3
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import Shift, Unit
from scheduling.models_multi_home import CareHome
from datetime import date

today = date(2025, 12, 18)

print("=" * 60)
print(f"Investigating shifts for {today}")
print("=" * 60)

for home in CareHome.objects.all().order_by('name'):
    print(f"\n{home.get_name_display()}:")
    units = Unit.objects.filter(care_home=home, is_active=True)
    print(f"  Units: {units.count()} - {[u.name for u in units]}")
    
    day_shifts = Shift.objects.filter(
        date=today, 
        unit__in=units, 
        status__in=['SCHEDULED', 'CONFIRMED'], 
        shift_type__name__icontains='DAY'
    )
    
    night_shifts = Shift.objects.filter(
        date=today, 
        unit__in=units, 
        status__in=['SCHEDULED', 'CONFIRMED'], 
        shift_type__name__icontains='NIGHT'
    )
    
    print(f"  Day shifts (total records): {day_shifts.count()}")
    print(f"  Day shifts (unique users): {day_shifts.values('user').distinct().count()}")
    print(f"  Night shifts (total records): {night_shifts.count()}")
    print(f"  Night shifts (unique users): {night_shifts.values('user').distinct().count()}")
    
    if day_shifts.count() > 0:
        # Show first few shifts to see pattern
        print(f"  Sample day shifts:")
        for shift in day_shifts[:5]:
            print(f"    - {shift.user.full_name}, Unit: {shift.unit.name}, Type: {shift.shift_type.name}")
