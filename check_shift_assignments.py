import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
import django
django.setup()

from scheduling.models import Shift, User
from datetime import date, timedelta

# Get current week's shifts
today = date.today()
start_of_week = today - timedelta(days=today.weekday())
end_of_week = start_of_week + timedelta(days=6)

print(f'\n{"="*60}')
print(f'SHIFT ANALYSIS FOR WEEK: {start_of_week} to {end_of_week}')
print(f'{"="*60}\n')

# Get all shifts for this week
shifts = Shift.objects.filter(
    date__range=[start_of_week, end_of_week]
).select_related('unit', 'shift_type', 'user')

print(f'Total shifts this week: {shifts.count()}')
print(f'{"="*60}\n')

# Count shifts with and without staff assigned
shifts_with_staff = shifts.exclude(user__isnull=True).count()
shifts_without_staff = shifts.filter(user__isnull=True).count()

print(f'Shifts WITH staff assigned: {shifts_with_staff}')
print(f'Shifts WITHOUT staff assigned: {shifts_without_staff}')
print(f'{"="*60}\n')

# Show sample of shifts without staff
print(f'SAMPLE OF SHIFTS WITHOUT STAFF (first 10):')
print(f'{"="*60}')
unassigned_shifts = shifts.filter(user__isnull=True)[:10]
for shift in unassigned_shifts:
    print(f'Date: {shift.date}, Type: {shift.shift_type.name}, Unit: {shift.unit.name}, Staff: {shift.user}')

# Show sample of shifts with staff
print(f'\n{"="*60}')
print(f'SAMPLE OF SHIFTS WITH STAFF (first 10):')
print(f'{"="*60}')
assigned_shifts = shifts.exclude(user__isnull=True)[:10]
for shift in assigned_shifts:
    staff_name = f'{shift.user.first_name} {shift.user.last_name}' if shift.user else 'None'
    print(f'Date: {shift.date}, Type: {shift.shift_type.name}, Unit: {shift.unit.name}, Staff: {staff_name} ({shift.user.sap if shift.user else "N/A"})')

# Check if there are any active staff available
print(f'\n{"="*60}')
print(f'ACTIVE STAFF SUMMARY')
print(f'{"="*60}')
active_staff = User.objects.filter(is_active=True)
print(f'Total active staff: {active_staff.count()}')

# Count by role
from collections import Counter
role_counts = Counter()
for staff in active_staff:
    role_name = staff.role.name if staff.role else 'No Role'
    role_counts[role_name] += 1

print(f'\nStaff by role:')
for role, count in role_counts.most_common():
    print(f'  {role}: {count}')
