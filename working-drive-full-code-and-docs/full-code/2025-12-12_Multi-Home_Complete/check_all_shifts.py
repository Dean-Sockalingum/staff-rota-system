#!/usr/bin/env python3
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Shift, CareHome
from datetime import datetime, timedelta

print("="*80)
print("SHIFT DATA CHECK ACROSS ALL HOMES")
print("="*80)

# Check all homes
target_homes = ['HAWTHORN_HOUSE', 'MEADOWBURN', 'ORCHARD_GROVE', 'RIVERSIDE', 'VICTORIA_GARDENS']

end_date = datetime.now().date()
start_date = end_date - timedelta(days=30)

print(f"\nChecking shifts from {start_date} to {end_date}\n")

for home_name in target_homes:
    try:
        home = CareHome.objects.get(name=home_name)
        
        # Get all staff (active and inactive)
        all_staff = User.objects.filter(unit__care_home=home)
        active_staff = all_staff.filter(is_active=True)
        inactive_staff = all_staff.filter(is_active=False)
        
        # Get shifts for all staff
        all_shifts = Shift.objects.filter(user__in=all_staff, date__gte=start_date)
        active_staff_shifts = Shift.objects.filter(user__in=active_staff, date__gte=start_date)
        inactive_staff_shifts = Shift.objects.filter(user__in=inactive_staff, date__gte=start_date)
        
        print(f"{home.get_name_display()}:")
        print(f"  Active staff: {active_staff.count()}")
        print(f"  Inactive staff: {inactive_staff.count()}")
        print(f"  Total shifts (last 30 days): {all_shifts.count()}")
        print(f"    - Active staff shifts: {active_staff_shifts.count()}")
        print(f"    - Inactive staff shifts: {inactive_staff_shifts.count()}")
        
        # Show SAP ranges
        if active_staff.exists():
            saps = [s.sap for s in active_staff]
            print(f"  Active SAP range: {min(saps)} to {max(saps)}")
        if inactive_staff.exists():
            saps = [s.sap for s in inactive_staff]
            print(f"  Inactive SAP range: {min(saps)} to {max(saps)}")
        
        print()
        
    except CareHome.DoesNotExist:
        print(f"{home_name}: NOT FOUND\n")

print("="*80)
print("TOTAL DATABASE SUMMARY")
print("="*80)

total_users = User.objects.all().count()
active_users = User.objects.filter(is_active=True).count()
inactive_users = User.objects.filter(is_active=False).count()
total_shifts = Shift.objects.filter(date__gte=start_date).count()

print(f"\nTotal users: {total_users}")
print(f"Active users: {active_users}")
print(f"Inactive users: {inactive_users}")
print(f"Total shifts (last 30 days): {total_shifts}")

# Check if ANY shifts exist at all
all_time_shifts = Shift.objects.all().count()
print(f"Total shifts (all time): {all_time_shifts}")
