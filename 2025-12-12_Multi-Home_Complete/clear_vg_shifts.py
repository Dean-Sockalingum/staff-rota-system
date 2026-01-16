#!/usr/bin/env python3
"""
Clear Victoria Gardens shifts only and regenerate with correct SSCWN patterns
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import Shift, CareHome, User

def main():
    print("\n" + "="*80)
    print("CLEAR VICTORIA GARDENS SHIFTS")
    print("="*80)
    
    # Get Victoria Gardens
    vg = CareHome.objects.get(name='VICTORIA_GARDENS')
    vg_staff = User.objects.filter(unit__care_home=vg, is_active=True)
    
    # Count existing shifts
    vg_shifts = Shift.objects.filter(user__in=vg_staff)
    shift_count = vg_shifts.count()
    
    print(f"\nFound {shift_count} shifts for Victoria Gardens staff")
    print("Deleting in batches...")
    
    # Delete in batches
    batch_size = 1000
    deleted = 0
    
    while True:
        # Get a batch of shift IDs
        batch_ids = list(vg_shifts.values_list('id', flat=True)[:batch_size])
        if not batch_ids:
            break
        
        # Delete the batch
        Shift.objects.filter(id__in=batch_ids).delete()
        deleted += len(batch_ids)
        
        if deleted % 1000 == 0:
            print(f"  Deleted {deleted:,} shifts...")
    
    print(f"\n✓ Total deleted: {deleted:,} shifts")
    print("\nNow run: python3 implement_vg_exact_pattern.py")

if __name__ == '__main__':
    main()
