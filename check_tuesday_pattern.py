#!/usr/bin/env python3
"""Check Tuesday staffing pattern across multiple weeks"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import Shift, Unit
from datetime import datetime, timedelta
from collections import defaultdict

# Get next several Tuesdays starting from Jan 14, 2026
start = datetime(2026, 1, 14)  # First Tuesday
tuesdays = []
for i in range(9):  # Check 9 Tuesdays (3 cycles of 3 weeks)
    tuesday = start + timedelta(weeks=i)
    tuesdays.append(tuesday.date())

# Check all care units across all homes
print("Tuesday Staffing Pattern Analysis")
print("=" * 80)

# Sample a few units from different homes
sample_units = [
    'RS_DAFFODIL', 'RS_LILY', 'RS_MAPLE',  # Riverside
    'HH_BLUEBELL', 'HH_DAISY',  # Hawthorn
    'MB_ASTER', 'MB_DAISY',  # Meadowburn
    'OG_CHERRY', 'OG_PEACH',  # Orchard Grove
    'VG_CROCUS', 'VG_LILY'  # Victoria Gardens
]

for unit_name in sample_units:
    unit = Unit.objects.filter(name=unit_name).first()
    if not unit:
        continue
        
    print(f"\n{unit_name}:")
    print("-" * 60)
    
    staffing = []
    for i, tuesday in enumerate(tuesdays, 1):
        # Count day shifts only
        day_shifts = Shift.objects.filter(
            unit=unit, 
            date=tuesday, 
            shift_type__name__icontains='Day'
        ).exclude(
            shift_type__name__icontains='Night'
        ).count()
        staffing.append(day_shifts)
        
        marker = " ⚠️  SHORTFALL" if day_shifts < unit.min_day_staff else ""
        print(f"  Week {i} ({tuesday}): {day_shifts} day shifts{marker}")
    
    # Check for pattern
    if len(staffing) >= 9:
        week3_count = staffing[2]  # Week 3
        week6_count = staffing[5]  # Week 6
        week9_count = staffing[8]  # Week 9
        
        if week3_count == week6_count == week9_count and week3_count < unit.min_day_staff:
            print(f"  🔴 PATTERN DETECTED: Every 3rd week (weeks 3, 6, 9) has {week3_count} shifts")

print("\n" + "=" * 80)
print("Summary:")
print("Min day staff per unit: 2-3 (varies by unit)")
print("If you see a repeating 3-week pattern of shortfalls, this indicates")
print("the shift rotation cycle is causing gaps in coverage.")
