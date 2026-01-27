#!/usr/bin/env python3
"""
Remove StaffProfile records for inactive/historical staff
"""
import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'rotasystems.settings'
django.setup()

from staff_records.models import StaffProfile
from scheduling.models import User

def main():
    print("\n" + "="*80)
    print("CLEANUP INACTIVE STAFF PROFILES")
    print("="*80)
    
    # Get all profiles
    total_profiles = StaffProfile.objects.count()
    print(f"\nTotal profiles before cleanup: {total_profiles}")
    
    # Get profiles for inactive users
    inactive_profiles = StaffProfile.objects.filter(user__is_active=False)
    inactive_count = inactive_profiles.count()
    
    # Get profiles with no user (orphaned)
    orphaned_profiles = StaffProfile.objects.filter(user__isnull=True)
    orphaned_count = orphaned_profiles.count()
    
    print(f"Profiles for inactive users: {inactive_count}")
    print(f"Orphaned profiles (no user): {orphaned_count}")
    print(f"Total to delete: {inactive_count + orphaned_count}")
    
    # Delete inactive profiles
    if inactive_count > 0:
        deleted = inactive_profiles.delete()
        print(f"\n✓ Deleted {deleted[0]} profiles for inactive users")
    
    # Delete orphaned profiles
    if orphaned_count > 0:
        deleted = orphaned_profiles.delete()
        print(f"✓ Deleted {deleted[0]} orphaned profiles")
    
    # Verify
    remaining = StaffProfile.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    
    print(f"\nFinal count:")
    print(f"  Staff profiles: {remaining}")
    print(f"  Active users: {active_users}")
    print(f"  Match: {'✓ YES' if remaining == active_users else '✗ NO'}")

if __name__ == '__main__':
    main()
