#!/usr/bin/env python3
import os
import sys
import django

sys.path.insert(0, '/Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete')
os.chdir('/Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import Unit, Shift
from scheduling.models_multi_home import CareHome
from datetime import date

print('=== CARE HOMES ===')
for home in CareHome.objects.all().order_by('name'):
    print(f'{home.name}: {home.get_name_display()}')

print('\n=== UNITS BY CARE HOME ===')
for home in CareHome.objects.all().order_by('name'):
    print(f'\n{home.get_name_display()} ({home.name}):')
    units = Unit.objects.filter(care_home=home, is_active=True).order_by('name')
    for unit in units:
        print(f'  - {unit.name}: {unit.get_name_display()}')
    if not units.exists():
        print('  (no units)')

print('\n=== SHIFT COUNTS FOR JAN 4-10 BY CARE HOME ===')
start_date = date(2026, 1, 4)
end_date = date(2026, 1, 10)

for home in CareHome.objects.all().order_by('name'):
    shift_count = Shift.objects.filter(
        date__range=[start_date, end_date],
        unit__care_home=home
    ).count()
    with_staff = Shift.objects.filter(
        date__range=[start_date, end_date],
        unit__care_home=home,
        user__isnull=False
    ).count()
    print(f'{home.get_name_display()}: {shift_count} shifts ({with_staff} with staff)')
