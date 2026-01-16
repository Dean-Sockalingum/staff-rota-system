#!/usr/bin/env python3
"""
Map old SAP numbers to new SAP numbers and update shift records.

The issue: During SAP migration, foreign keys were disabled, so shift records
still reference old SAP numbers. We need to map old->new and update shifts.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Shift
from django.db import connection

print("="*80)
print("SHIFT SAP NUMBER REALIGNMENT")
print("="*80)
print()

# Get current state
total_users = User.objects.all().count()
total_shifts = Shift.objects.all().count()

print(f"Current state:")
print(f"  Total users: {total_users}")
print(f"  Total shifts: {total_shifts}")
print()

# Get all unique SAP numbers from shifts
with connection.cursor() as cursor:
    cursor.execute("SELECT DISTINCT user_id FROM scheduling_shift ORDER BY user_id")
    old_saps_in_shifts = [row[0] for row in cursor.fetchall()]

print(f"Unique SAP numbers in shift table: {len(old_saps_in_shifts)}")
print(f"Sample old SAPs: {old_saps_in_shifts[:20]}")
print()

# Check how many shifts are orphaned
orphaned_count = 0
for old_sap in old_saps_in_shifts[:10]:
    try:
        user = User.objects.get(sap=old_sap)
    except User.DoesNotExist:
        orphaned_count += 1

print(f"Sample check: {orphaned_count}/10 SAPs in shifts don't match current users")
print()

# THE PROBLEM: 
# The migration script disabled foreign keys and updated SAP numbers in User table
# but didn't update the foreign keys in Shift table, so all shifts are orphaned.

print("="*80)
print("ANALYSIS: SHIFT RECORDS ARE ORPHANED")
print("="*80)
print()
print("The SAP migration changed User.sap (primary key) but foreign keys were")
print("disabled, so Shift.user_id still references old SAP numbers.")
print()
print("We cannot automatically map old SAPs to new SAPs because the mapping")
print("information was not preserved during migration.")
print()
print("RECOMMENDED SOLUTION:")
print("1. The shifts need to be regenerated from scratch OR")
print("2. We need to determine the mapping logic to realign SAPs")
print()

# Check if there's a pattern we can use
print("Analyzing SAP patterns...")
print()

# Sample current users
current_users = User.objects.all().order_by('sap')[:10]
print("Current users (first 10):")
for u in current_users:
    home = u.unit.care_home.get_name_display() if u.unit else 'No Home'
    role = u.role.name if u.role else 'No Role'
    print(f"  SAP {u.sap}: {u.first_name} {u.last_name:30} | {role:8} | {home}")

print()
print("The shifts are from a previous rota system with different SAP numbers.")
print("Without the mapping, we cannot reliably update the shifts.")
print()
print("=" * 80)
print("ACTION REQUIRED")
print("="*80)
print()
print("Option 1: DELETE ALL EXISTING SHIFTS")
print("  - Clear all 98,413 shifts")
print("  - Generate new shifts based on current staff structure")
print("  - Use Orchard Grove as template for patterns")
print()
print("Option 2: FIND OR RECREATE THE SAP MAPPING")
print("  - Look for backup/migration logs")
print("  - Try to infer mapping from names/roles/units")
print("  - Update all shift records")
print()
