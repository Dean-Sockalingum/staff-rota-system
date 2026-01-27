#!/usr/bin/env python3
"""
Delete StaffProfile records for all inactive users
"""
import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'rotasystems.settings'
django.setup()

from staff_records.models import StaffProfile
from scheduling.models import User

def main():
    print("\n" + "="*80)
    print("DELETE PROFILES FOR INACTIVE USERS")
    print("="*80)
    
    # Get counts
    total_profiles = StaffProfile.objects.count()
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    inactive_users = total_users - active_users
    
    print(f"\nBefore cleanup:")
    print(f"  Total staff profiles: {total_profiles}")
    print(f"  Total users: {total_users}")
    print(f"  Active users: {active_users}")
    print(f"  Inactive users: {inactive_users}")
    
    # Get all active user SAPs
    active_saps = set(User.objects.filter(is_active=True).values_list('sap', flat=True))
    print(f"\nActive user SAPs: {len(active_saps)}")
    
    # Delete profiles where user_id (SAP) is not in active users
    profiles_to_delete = StaffProfile.objects.exclude(user_id__in=active_saps)
    delete_count = profiles_to_delete.count()
    
    print(f"Profiles to delete: {delete_count}")
    
    if delete_count > 0:
        print(f"\nDeleting {delete_count} profiles...")
        deleted = profiles_to_delete.delete()
        print(f"✓ Deleted {deleted[0]} profiles")
    
    # Final verification
    remaining = StaffProfile.objects.count()
    print(f"\nAfter cleanup:")
    print(f"  Staff profiles: {remaining}")
    print(f"  Active users: {active_users}")
    print(f"  Match: {'✓ YES' if remaining == active_users else '✗ NO'}")

if __name__ == '__main__':
    main()
