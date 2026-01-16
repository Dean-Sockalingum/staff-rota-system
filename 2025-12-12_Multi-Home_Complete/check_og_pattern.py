import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from datetime import date, timedelta
from scheduling.models import Shift, Unit
from scheduling.models_multi_home import CareHome

# Check multiple days to see the pattern
start_date = date(2025, 12, 18)
dates_to_check = [start_date + timedelta(days=i) for i in range(7)]

print("\n=== Orchard Grove Staffing Pattern Analysis ===\n")

og = CareHome.objects.get(name='ORCHARD_GROVE')
units = Unit.objects.filter(care_home=og, is_active=True)

print(f"Orchard Grove - {units.count()} units: {[u.name for u in units]}\n")

for check_date in dates_to_check:
    shifts = Shift.objects.filter(
        date=check_date,
        unit__in=units,
        status__in=['SCHEDULED', 'CONFIRMED']
    ).select_related('shift_type')
    
    if shifts.count() > 0:
        day_senior = shifts.filter(shift_type__name='DAY_SENIOR').count()
        day_assistant = shifts.filter(shift_type__name='DAY_ASSISTANT').count()
        night_senior = shifts.filter(shift_type__name='NIGHT_SENIOR').count()
        night_assistant = shifts.filter(shift_type__name='NIGHT_ASSISTANT').count()
        
        total_day = day_senior + day_assistant
        total_night = night_senior + night_assistant
        
        print(f"{check_date}:")
        print(f"  Day: {total_day} (Senior: {day_senior}, Assistant: {day_assistant})")
        print(f"  Night: {total_night} (Senior: {night_senior}, Assistant: {night_assistant})")

print("\n" + "="*60)
print("\nRECOMMENDED MINIMUM REQUIREMENTS:")
print("Based on Orchard Grove pattern, the 4 large homes should have:")
print(f"  Day minimum: {total_day}")
print(f"  Night minimum: {total_night}")
