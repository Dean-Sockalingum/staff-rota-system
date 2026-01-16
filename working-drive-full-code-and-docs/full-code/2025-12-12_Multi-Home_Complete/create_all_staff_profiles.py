#!/usr/bin/env python3
"""
Create StaffProfile records for all active users
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(__file__))
os.environ['DJANGO_SETTINGS_MODULE'] = 'rotasystems.settings'
django.setup()

from scheduling.models import User
from staff_records.models import StaffProfile

print("Creating staff profiles for all active users...\n")

# Get all active users
active_users = User.objects.filter(is_active=True)
total = active_users.count()

created = 0
existing = 0

for user in active_users:
    profile, created_new = StaffProfile.objects.get_or_create(
        user=user,
        defaults={
            'employment_status': 'ACTIVE',
            'emergency_contact_name': '',
            'emergency_contact_phone': '',
        }
    )
    
    if created_new:
        created += 1
        if created % 100 == 0:
            print(f"Created {created}/{total} profiles...")
    else:
        existing += 1

print(f"\n✓ Profile creation complete")
print(f"  Created: {created} new profiles")
print(f"  Existing: {existing} profiles")
print(f"  Total: {total} active users")
