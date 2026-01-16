import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
import django
django.setup()

from scheduling.models import Shift
from datetime import date, timedelta

# Get the week starting Jan 4 (the screenshot shows JAN 4 as Sunday)
week_start = date(2026, 1, 4)
week_end = week_start + timedelta(days=6)

print(f'\n{"="*60}')
print(f'SHIFT ANALYSIS FOR WEEK: {week_start} to {week_end}')
print(f'{"="*60}\n')

shifts = Shift.objects.filter(
    date__range=[week_start, week_end]
).select_related('unit', 'shift_type', 'user').order_by('date', 'shift_type__name', 'unit__name')

print(f'Total shifts this week: {shifts.count()}')
print(f'Shifts WITH staff: {shifts.exclude(user__isnull=True).count()}')
print(f'Shifts WITHOUT staff: {shifts.filter(user__isnull=True).count()}\n')

# Show shifts for Jan 4 (Sunday) grouped by unit
print(f'{"="*60}')
print(f'SHIFTS FOR SUNDAY, JAN 4, 2026 (grouped by unit)')
print(f'{"="*60}\n')

jan4_shifts = shifts.filter(date=date(2026, 1, 4)).order_by('unit__name', 'shift_type__name')

from collections import defaultdict
shifts_by_unit = defaultdict(list)

for shift in jan4_shifts:
    shifts_by_unit[shift.unit.name].append(shift)

for unit_name in sorted(shifts_by_unit.keys()):
    unit_shifts = shifts_by_unit[unit_name]
    print(f'\n{unit_name}:')
    for shift in unit_shifts:
        staff_name = f'{shift.user.first_name} {shift.user.last_name}' if shift.user else 'NO STAFF'
        print(f'  - {shift.shift_type.name}: {staff_name}')

print(f'\n{"="*60}')
print(f'CHECKING HAWTHORN HOUSE UNITS')
print(f'{"="*60}')

# Check if there are Hawthorn House (HH_) shifts
hh_shifts = shifts.filter(unit__name__startswith='HH_').order_by('date', 'unit__name')
print(f'\nTotal HH_ shifts this week: {hh_shifts.count()}')
print(f'HH_ shifts WITH staff: {hh_shifts.exclude(user__isnull=True).count()}')
print(f'HH_ shifts WITHOUT staff: {hh_shifts.filter(user__isnull=True).count()}\n')

# Show sample
print(f'Sample HH_ shifts (first 20):')
for shift in hh_shifts[:20]:
    staff_name = f'{shift.user.first_name} {shift.user.last_name}' if shift.user else 'NO STAFF'
    print(f'{shift.date} | {shift.unit.name} | {shift.shift_type.name} | {staff_name}')
