import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from datetime import date
from scheduling.models import Shift, Unit, ShiftType
from scheduling.models_multi_home import CareHome

today = date(2025, 12, 18)

print(f"\n=== Detailed Shift Analysis for {today} ===\n")

# First, let's see all shift types
print("All Shift Types in Database:")
for st in ShiftType.objects.all():
    print(f"  - {st.name}")

print("\n" + "="*60)

hawthorn = CareHome.objects.get(name='HAWTHORN_HOUSE')
units = Unit.objects.filter(care_home=hawthorn, is_active=True)

print(f"\nHawthorn House Analysis:")
print(f"Units: {[u.name for u in units]}")

# Get all shifts for today
all_shifts = Shift.objects.filter(
    date=today,
    unit__in=units,
    status__in=['SCHEDULED', 'CONFIRMED']
).select_related('user', 'shift_type', 'unit')

print(f"\nTotal shifts for today: {all_shifts.count()}")

# Group by shift type
print("\nShifts by Type:")
for st in ShiftType.objects.all():
    count = all_shifts.filter(shift_type=st).count()
    if count > 0:
        print(f"  {st.name}: {count} shifts")

# Check for users with multiple shifts
print("\nUsers with multiple shifts today:")
from collections import Counter
user_shift_counts = Counter([s.user.id for s in all_shifts])
for user_id, count in user_shift_counts.most_common(10):
    if count > 1:
        user = all_shifts.filter(user_id=user_id).first().user
        user_shifts = all_shifts.filter(user_id=user_id)
        print(f"  {user.first_name} {user.last_name} ({count} shifts):")
        for shift in user_shifts:
            print(f"    - {shift.shift_type.name} in {shift.unit.name}")

# Now check what the query is actually returning
print("\n" + "="*60)
print("What the dashboard query returns:")

day_filter_shifts = all_shifts.filter(shift_type__name__icontains='DAY')
night_filter_shifts = all_shifts.filter(shift_type__name__icontains='NIGHT')

print(f"\nShifts with 'DAY' in type name: {day_filter_shifts.count()}")
print(f"Shifts with 'NIGHT' in type name: {night_filter_shifts.count()}")

print(f"\nUnique users in DAY shifts: {day_filter_shifts.values('user').distinct().count()}")
print(f"Unique users in NIGHT shifts: {night_filter_shifts.values('user').distinct().count()}")
