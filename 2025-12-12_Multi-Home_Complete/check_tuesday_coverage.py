#!/usr/bin/env python3
"""Check complete Tuesday coverage across all units and identify the 18-staff shortfall"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import Shift, Unit, User
from datetime import datetime, timedelta
from collections import defaultdict

# Check Tuesday Jan 14, 2026
tuesday = datetime(2026, 1, 14).date()

print(f"COMPLETE TUESDAY COVERAGE ANALYSIS: {tuesday}")
print("=" * 80)

# Get all care units (exclude MGMT units)
care_units = Unit.objects.exclude(name__endswith='_MGMT').filter(is_active=True).order_by('care_home__name', 'name')

total_required = 0
total_scheduled = 0
total_shortfall = 0

by_home = defaultdict(lambda: {'required': 0, 'scheduled': 0, 'shortfall': 0, 'units': []})

for unit in care_units:
    # Count day shifts scheduled (exclude night shifts)
    day_shifts = Shift.objects.filter(
        unit=unit,
        date=tuesday,
        shift_type__name__icontains='Day'
    ).exclude(
        shift_type__name__icontains='Night'
    ).count()
    
    required = unit.min_day_staff
    shortfall = max(0, required - day_shifts)
    
    home_name = unit.care_home.name if unit.care_home else 'Unknown'
    
    by_home[home_name]['required'] += required
    by_home[home_name]['scheduled'] += day_shifts
    by_home[home_name]['shortfall'] += shortfall
    
    if shortfall > 0:
        by_home[home_name]['units'].append({
            'name': unit.name,
            'required': required,
            'scheduled': day_shifts,
            'shortfall': shortfall
        })
    
    total_required += required
    total_scheduled += day_shifts
    total_shortfall += shortfall

# Print results by home
for home_name in sorted(by_home.keys()):
    data = by_home[home_name]
    print(f"\n{home_name}")
    print("-" * 80)
    print(f"  Required: {data['required']} day shifts")
    print(f"  Scheduled: {data['scheduled']} day shifts")
    print(f"  Shortfall: {data['shortfall']} shifts")
    
    if data['units']:
        print(f"\n  Units with shortfalls:")
        for unit_data in data['units']:
            print(f"    {unit_data['name']}: {unit_data['scheduled']}/{unit_data['required']} (short {unit_data['shortfall']})")

print("\n" + "=" * 80)
print(f"SYSTEM TOTALS:")
print(f"  Total Required: {total_required} day shifts")
print(f"  Total Scheduled: {total_scheduled} day shifts")
print(f"  Total Shortfall: {total_shortfall} shifts")
print("=" * 80)

if total_shortfall != 18:
    print(f"\n⚠️  User reported 18 staff short, but calculation shows {total_shortfall}")
    print(f"   Checking if night shifts are also included...")
    
    # Check night coverage too
    total_night_required = 0
    total_night_scheduled = 0
    for unit in care_units:
        night_shifts = Shift.objects.filter(
            unit=unit,
            date=tuesday,
            shift_type__name__icontains='Night'
        ).count()
        total_night_required += unit.min_night_staff
        total_night_scheduled += night_shifts
    
    night_shortfall = max(0, total_night_required - total_night_scheduled)
    print(f"\n   Night shifts required: {total_night_required}")
    print(f"   Night shifts scheduled: {total_night_scheduled}")
    print(f"   Night shortfall: {night_shortfall}")
    print(f"\n   COMBINED SHORTFALL: {total_shortfall + night_shortfall} shifts")

# Check total active staff
print("\n" + "=" * 80)
print("STAFF AVAILABILITY CHECK:")
total_staff = User.objects.filter(is_active=True).exclude(role__name__in=['SM', 'OM', 'ADMIN', 'HOS', 'IDI']).count()
staff_with_shifts = Shift.objects.filter(date=tuesday).values('user').distinct().count()
print(f"  Total active care staff: {total_staff}")
print(f"  Staff scheduled on {tuesday}: {staff_with_shifts}")
print(f"  Staff NOT scheduled: {total_staff - staff_with_shifts}")
