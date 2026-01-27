#!/usr/bin/env python3
"""
Fix shift inconsistencies across the 4 standardized homes.
Delete existing shifts and regenerate with identical patterns.
"""

import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.db import transaction
from scheduling.models import User, Shift, ShiftType, Unit, CareHome

# Get the 4 standardized homes
STANDARDIZED_HOMES = ['HAWTHORN_HOUSE', 'MEADOWBURN', 'ORCHARD_GROVE', 'RIVERSIDE']

def analyze_current_state():
    """Show current shift counts"""
    print("\n=== CURRENT SHIFT COUNTS (Dec 2025) ===\n")
    
    for home_name in STANDARDIZED_HOMES:
        home = CareHome.objects.get(name=home_name)
        dec_shifts = Shift.objects.filter(
            unit__care_home=home,
            date__year=2025,
            date__month=12
        ).count()
        print(f"{home_name}: {dec_shifts} shifts in Dec 2025")
    
    # Show specific date comparison
    print("\n=== Dec 16, 2025 Comparison ===")
    target = date(2025, 12, 16)
    for home_name in STANDARDIZED_HOMES:
        home = CareHome.objects.get(name=home_name)
        count = Shift.objects.filter(
            unit__care_home=home,
            date=target
        ).count()
        print(f"{home_name}: {count} shifts")

def delete_all_shifts_for_standardized_homes():
    """Delete all shifts for the 4 standardized homes"""
    print("\n=== DELETING EXISTING SHIFTS ===\n")
    
    for home_name in STANDARDIZED_HOMES:
        home = CareHome.objects.get(name=home_name)
        count = Shift.objects.filter(unit__care_home=home).count()
        print(f"Deleting {count} shifts for {home_name}...")
        Shift.objects.filter(unit__care_home=home).delete()
    
    print("\nAll shifts deleted.")

def main():
    print("=" * 80)
    print("SHIFT CONSISTENCY FIX")
    print("=" * 80)
    
    # Show current state
    analyze_current_state()
    
    # Ask for confirmation
    print("\n" + "=" * 80)
    response = input("\nDo you want to DELETE all shifts for these 4 homes? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Operation cancelled.")
        return
    
    # Delete shifts
    with transaction.atomic():
        delete_all_shifts_for_standardized_homes()
    
    print("\n" + "=" * 80)
    print("Shifts deleted successfully!")
    print("\nNow run: python3 regenerate_shifts_for_standardized_homes.py")
    print("=" * 80)

if __name__ == '__main__':
    main()
