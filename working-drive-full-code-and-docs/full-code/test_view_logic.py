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

start_date = date(2026, 1, 4)
end_date = date(2026, 1, 10)

# Test the exact filtering logic from the view
day_care_roles = {'SCW', 'SCA'}
night_care_roles = {'SCWN', 'SCAN'}

print('=== TESTING VIEW FILTERING LOGIC ===\n')

from scheduling.models_multi_home import CareHome

for home in ['HAWTHORN_HOUSE', 'MEADOWBURN', 'ORCHARD_GROVE']:
    print(f'\n{home}:')
    
    # Simulate the view's query
    shifts_query = Shift.objects.filter(
        date__range=[start_date, end_date],
        unit__care_home__name=home
    ).select_related('user', 'unit', 'shift_type')
    
    total_shifts = shifts_query.count()
    print(f'  Total shifts in week: {total_shifts}')
    
    # Test for one specific date
    date_shifts = [shift for shift in shifts_query if shift.date == start_date]
    print(f'  Shifts on Jan 4: {len(date_shifts)}')
    
    day_shifts = [s for s in date_shifts if s.shift_type.name in ['DAY', 'EARLY', 'LATE', 'LONG_DAY']]
    print(f'  DAY shifts on Jan 4: {len(day_shifts)}')
    
    day_care = [
        s for s in day_shifts
        if getattr(getattr(s.user, 'role', None), 'name', '') in day_care_roles
    ]
    print(f'  DAY CARE shifts (SCW/SCA): {len(day_care)}')
    
    # Show sample
    if day_care:
        print(f'  Sample: {day_care[0].user.full_name} ({day_care[0].user.role.name}) at {day_care[0].unit.name}')
    else:
        # Debug - show what's there
        if day_shifts:
            sample = day_shifts[0]
            user_role = getattr(getattr(sample.user, 'role', None), 'name', 'NO ROLE')
            print(f'  Sample day_shift: {sample.user.full_name if sample.user else "NO USER"} (role={user_role})')
