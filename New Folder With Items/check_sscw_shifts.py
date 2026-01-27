#!/usr/bin/env python3
"""
Check SSCW shifts in database.
"""

import os
import django
import sys
from datetime import date

sys.path.insert(0, '/home/staff-rota-system/2025-12-12_Multi-Home_Complete')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import Shift, User
from scheduling.models_multi_home import CareHome

homes = ['HAWTHORN_HOUSE', 'MEADOWBURN', 'RIVERSIDE', 'ORCHARD_GROVE']

print("="*80)
print("SSCW SHIFT CHECK (Jan 18-24, 2026)")
print("="*80)

for home_name in homes:
    home = CareHome.objects.get(name=home_name)
    
    # Count SSCW shifts
    sscw_shifts = Shift.objects.filter(
        unit__care_home=home,
        user__role__name='SSCW',
        date__gte=date(2026, 1, 18),
        date__lte=date(2026, 1, 24)
    )
    
    total_shifts = Shift.objects.filter(
        unit__care_home=home,
        date__gte=date(2026, 1, 18),
        date__lte=date(2026, 1, 24)
    )
    
    print(f"\n{home_name}:")
    print(f"  SSCW shifts: {sscw_shifts.count()}")
    print(f"  Total shifts: {total_shifts.count()}")
    
    # Check SSCW staff count
    sscw_staff = User.objects.filter(
        unit__care_home=home,
        role__name='SSCW',
        is_active=True
    ).count()
    print(f"  SSCW staff available: {sscw_staff}")
    
    # Sample a few shifts
    if sscw_shifts.exists():
        print(f"  Sample SSCW shifts:")
        for shift in sscw_shifts[:3]:
            print(f"    {shift.date}: {shift.user.get_full_name()} - {shift.shift_type.name}")
