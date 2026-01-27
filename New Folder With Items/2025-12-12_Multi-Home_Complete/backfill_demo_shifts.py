#!/usr/bin/env python3
"""
Backfill shifts to start from today for demo purposes.
This adjusts all shifts backward so they start from today's date.
"""

import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import Shift

print("="*60)
print("  BACKFILL DEMO SHIFTS TO TODAY")
print("="*60)
print()

# Get current shift date range
first_shift = Shift.objects.order_by('date').first()
last_shift = Shift.objects.order_by('-date').last()

if not first_shift:
    print("✗ No shifts found in database")
    exit(1)

current_start = first_shift.date
current_end = last_shift.date
today = date.today()

print(f"Current shift range: {current_start} to {current_end}")
print(f"Today's date: {today}")
print()

# Calculate how many days to shift backward
days_to_shift = (current_start - today).days

if days_to_shift <= 0:
    print(f"✓ Shifts already start in the past ({current_start})")
    print("No backfilling needed!")
    exit(0)

print(f"Need to shift {days_to_shift} days backward")
print(f"New range will be: {today} to {current_end - timedelta(days=days_to_shift)}")
print()

response = input("Proceed with backfilling? (yes/no): ")
if response.lower() != 'yes':
    print("Cancelled.")
    exit(0)

print()
print("Updating shifts...")

# Update all shifts in batches
batch_size = 1000
total_shifts = Shift.objects.count()
updated = 0

shifts = Shift.objects.all()
for shift in shifts.iterator(chunk_size=batch_size):
    shift.date = shift.date - timedelta(days=days_to_shift)
    shift.save(update_fields=['date'])
    updated += 1
    
    if updated % batch_size == 0:
        print(f"  Updated {updated}/{total_shifts} shifts...")

print(f"  Updated {updated}/{total_shifts} shifts...")
print()

# Verify
new_first = Shift.objects.order_by('date').first()
new_last = Shift.objects.order_by('-date').last()
today_count = Shift.objects.filter(date=today).count()

print("="*60)
print("  BACKFILL COMPLETE!")
print("="*60)
print()
print(f"New shift range: {new_first.date} to {new_last.date}")
print(f"Shifts today ({today}): {today_count}")
print()
print("✅ Demo database now has current data!")
