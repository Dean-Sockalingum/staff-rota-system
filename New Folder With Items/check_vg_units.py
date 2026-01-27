#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import CareHome, Unit, User

vg = CareHome.objects.get(name='VICTORIA_GARDENS')
print('Victoria Gardens Current Units:')
print('=' * 60)
units = Unit.objects.filter(care_home=vg).order_by('name')
total_beds = 0
for unit in units:
    staff_count = User.objects.filter(unit=unit).count()
    # Extract bed count from description
    if '15 beds' in unit.description:
        beds = 15
    elif '10 beds' in unit.description:
        beds = 10
    else:
        beds = 0
    total_beds += beds
    is_mgmt = 'Mgmt' in unit.name
    print(f'  {unit.name:30s}: {beds:2d} beds, {staff_count:2d} staff {"(Management)" if is_mgmt else ""}')

print(f'\nTotal care beds: {total_beds}')
print(f'Total units: {units.count()}')
