#!/usr/bin/env python3
"""
Verify that shifts are properly aligned with new SAP numbers and patterns match across homes.
"""

import os
import django
from collections import defaultdict

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Shift, CareHome
from datetime import datetime, timedelta

print("="*80)
print("SHIFT ALIGNMENT VERIFICATION")
print("="*80)
print()

target_homes = ['HAWTHORN_HOUSE', 'MEADOWBURN', 'ORCHARD_GROVE', 'RIVERSIDE']

# Check shift counts
start_date = datetime.now().date()
end_date = start_date + timedelta(days=30)

print(f"Checking shifts from {start_date} to {end_date}\n")

for home_name in target_homes:
    home = CareHome.objects.get(name=home_name)
    
    # Get active staff
    active_staff = User.objects.filter(unit__care_home=home, is_active=True)
    
    # Get shifts for this home
    shifts = Shift.objects.filter(
        user__unit__care_home=home,
        date__gte=start_date,
        date__lte=end_date
    ).select_related('user', 'shift_type')
    
    # Group by role
    shifts_by_role = defaultdict(int)
    for shift in shifts:
        role = shift.user.role.name if shift.user.role else 'UNKNOWN'
        shifts_by_role[role] += 1
    
    print(f"{home.get_name_display()}:")
    print(f"  Active staff: {active_staff.count()}")
    print(f"  Total shifts (30 days): {shifts.count()}")
    print(f"  Shifts by role:")
    for role, count in sorted(shifts_by_role.items()):
        print(f"    {role}: {count}")
    
    # Sample some shifts
    sample_shifts = shifts[:5]
    if sample_shifts:
        print(f"  Sample shifts:")
        for shift in sample_shifts:
            print(f"    {shift.date} | SAP {shift.user.sap} | {shift.user.first_name} {shift.user.last_name} | {shift.shift_type.name}")
    print()

print("="*80)
print("PATTERN CONSISTENCY CHECK")
print("="*80)
print()

# Check that homes have similar shift counts
shift_counts = {}
for home_name in target_homes:
    home = CareHome.objects.get(name=home_name)
    count = Shift.objects.filter(
        user__unit__care_home=home,
        date__gte=start_date,
        date__lte=end_date
    ).count()
    shift_counts[home_name] = count

print("30-day shift counts by home:")
for home_name, count in shift_counts.items():
    home = CareHome.objects.get(name=home_name)
    print(f"  {home.get_name_display()}: {count}")

# Check if counts are similar (within 5%)
counts = list(shift_counts.values())
if counts:
    avg = sum(counts) / len(counts)
    max_diff = max(abs(c - avg) for c in counts)
    if max_diff / avg < 0.05:
        print("\n✓ Shift counts are consistent across homes (within 5%)")
    else:
        print(f"\n⚠ Shift counts vary by more than 5% (max difference: {max_diff:.0f})")

print()
print("="*80)
print("SAP ALIGNMENT CHECK")
print("="*80)
print()

# Verify no orphaned shifts
total_shifts = Shift.objects.all().count()
orphaned = 0

try:
    # Try to access first 100 shifts
    for shift in Shift.objects.all()[:100]:
        try:
            _ = shift.user.sap
        except Exception:
            orphaned += 1
    
    if orphaned == 0:
        print(f"✓ All shifts properly linked to users (checked 100 samples)")
    else:
        print(f"⚠ Found {orphaned} orphaned shifts in sample")
except Exception as e:
    print(f"✗ Error checking shifts: {e}")

print(f"\nTotal shifts in database: {total_shifts:,}")
print()
