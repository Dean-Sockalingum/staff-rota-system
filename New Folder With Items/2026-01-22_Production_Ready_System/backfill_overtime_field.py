#!/usr/bin/env python
"""
Backfill is_overtime field based on shift_classification
Run this once after migration to populate historical data
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, '/home/staff-rota-system/2025-12-12_Multi-Home_Complete')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import Shift

def backfill_overtime_field():
    """Set is_overtime=True for all shifts with shift_classification='OVERTIME'"""
    
    print("Starting overtime field backfill...")
    
    # Count shifts to update
    overtime_shifts = Shift.objects.filter(
        shift_classification='OVERTIME',
        is_overtime=False  # Only update those not already marked
    )
    
    total_count = overtime_shifts.count()
    print(f"Found {total_count} shifts marked as OVERTIME but is_overtime=False")
    
    if total_count == 0:
        print("No shifts to update. Backfill complete!")
        return
    
    # Update in batches for performance
    updated = overtime_shifts.update(is_overtime=True)
    
    print(f"✅ Successfully updated {updated} shifts")
    print(f"   Set is_overtime=True for all OVERTIME shifts")
    
    # Verify the update
    verification = Shift.objects.filter(
        shift_classification='OVERTIME',
        is_overtime=True
    ).count()
    
    print(f"\nVerification: {verification} shifts now have is_overtime=True")
    print("Backfill complete!")

if __name__ == '__main__':
    try:
        backfill_overtime_field()
    except Exception as e:
        print(f"❌ Error during backfill: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
