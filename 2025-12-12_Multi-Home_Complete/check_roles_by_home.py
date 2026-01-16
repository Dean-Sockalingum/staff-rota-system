#!/usr/bin/env python3
import os
import sys
import django

sys.path.insert(0, '/Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete')
os.chdir('/Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import Shift
from datetime import date

print('=== SAMPLE SHIFTS BY CARE HOME (JAN 4) ===\n')
start_date = date(2026, 1, 4)

from scheduling.models_multi_home import CareHome

for home in CareHome.objects.all().order_by('name')[:3]:  # First 3 homes
    print(f'{home.get_name_display()}:')
    shifts = Shift.objects.filter(
        date=start_date,
        unit__care_home=home,
        user__isnull=False
    ).select_related('user', 'user__role', 'shift_type', 'unit')[:10]
    
    for shift in shifts:
        role = shift.user.role.name if shift.user and shift.user.role else 'NO ROLE'
        shift_type = shift.shift_type.name if shift.shift_type else 'NO TYPE'
        print(f'  {shift.unit.name:20} | {shift_type:10} | Role: {role:5} | {shift.user.full_name}')
    
    if not shifts:
        print('  (no shifts found)')
    print()
