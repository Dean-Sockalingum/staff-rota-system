#!/usr/bin/env python3
"""
Simple import: Just copy staff from local demo to production
Uses only fields that exist in both databases
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/home/staff-rota-system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Unit, Role, CareHome
from django.contrib.auth.hashers import make_password

print("="*80)
print("SIMPLE STAFF IMPORT FROM DEMO DATA")
print("="*80)

# Staff data from demo (simplified - just the essentials)
# We'll create staff matching the demo structure

homes_staff = {
    'ORCHARD_GROVE': 180,
    'MEADOWBURN': 179,
    'HAWTHORN_HOUSE': 178,
    'RIVERSIDE': 178,
    'VICTORIA_GARDENS': 98
}

print("\nTarget staff counts:")
for home, count in homes_staff.items():
    print(f"  {home:20} {count} staff")

current_total = User.objects.filter(is_active=True, is_superuser=False).count()
print(f"\nCurrent staff in production: {current_total}")

target_total = sum(homes_staff.values())
print(f"Target staff total: {target_total}")
print(f"Need to create: {target_total - current_total}")

print("\n" + "="*80)
print("This is a placeholder - we need the actual staff data from demo.")
print("Please use the staff_export_821.json file instead.")
print("="*80)
