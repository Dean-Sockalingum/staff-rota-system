"""
Update Production Shift Types
Date: January 8, 2026
Purpose: Configure the 3 accurate shift types used in production

SHIFT TYPES:
1. Day Shift: 08:00-20:00 (12 hours)
2. Night Shift: 20:00-08:00 (12 hours)  
3. Management: 09:00-17:00 (8 hours)
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, '/home/staff-rota-system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import ShiftType
from datetime import time

def update_shift_types():
    """Update shift types to match production reality"""
    
    print("\n" + "="*60)
    print("UPDATING SHIFT TYPES TO PRODUCTION CONFIGURATION")
    print("="*60 + "\n")
    
    # Define the 3 accurate shift types
    shift_configs = [
        {
            'name': 'Day Shift',
            'start_time': time(8, 0),    # 08:00
            'end_time': time(20, 0),      # 20:00
            'duration_hours': 12.0,
            'is_active': True,
            'applicable_roles': 'SCA,SCW,SSCW',
            'color_code': '#3498db'  # Blue
        },
        {
            'name': 'Night Shift',
            'start_time': time(20, 0),    # 20:00
            'end_time': time(8, 0),       # 08:00 next day
            'duration_hours': 12.0,
            'is_active': True,
            'applicable_roles': 'SCA,SCW,SSCW',
            'color_code': '#34495e'  # Dark gray
        },
        {
            'name': 'Management',
            'start_time': time(9, 0),     # 09:00
            'end_time': time(17, 0),      # 17:00
            'duration_hours': 8.0,
            'is_active': True,
            'applicable_roles': 'OM,SM,ADMIN,HR',
            'color_code': '#9b59b6'  # Purple
        }
    ]
    
    # Clear existing shift types (production has incorrect ones)
    existing_count = ShiftType.objects.count()
    if existing_count > 0:
        print(f"⚠️  Found {existing_count} existing shift types - will be updated/replaced\n")
    
    # Create/update shift types
    created_count = 0
    updated_count = 0
    
    for config in shift_configs:
        shift_type, created = ShiftType.objects.update_or_create(
            name=config['name'],
            defaults={
                'start_time': config['start_time'],
                'end_time': config['end_time'],
                'duration_hours': config['duration_hours'],
                'is_active': config['is_active'],
                'applicable_roles': config['applicable_roles'],
                'color_code': config['color_code'],
            }
        )
        
        if created:
            created_count += 1
            print(f"✅ Created: {config['name']}")
        else:
            updated_count += 1
            print(f"✅ Updated: {config['name']}")
        
        print(f"   └─ Hours: {config['start_time'].strftime('%H:%M')} - {config['end_time'].strftime('%H:%M')} ({config['duration_hours']}h)")
    
    # Delete any shift types NOT in our production list
    production_names = [c['name'] for c in shift_configs]
    deleted = ShiftType.objects.exclude(name__in=production_names).delete()
    
    print(f"\n{'='*60}")
    print("SUMMARY:")
    print(f"  • Created: {created_count} shift types")
    print(f"  • Updated: {updated_count} shift types")
    print(f"  • Deleted: {deleted[0]} obsolete shift types")
    print(f"  • Total Active: {ShiftType.objects.count()} shift types")
    print(f"{'='*60}\n")
    
    # Verify final state
    print("FINAL SHIFT TYPE CONFIGURATION:\n")
    for st in ShiftType.objects.order_by('name'):
        print(f"  {st.name:15} | {st.start_time.strftime('%H:%M')}-{st.end_time.strftime('%H:%M')} | {st.duration_hours}h | Roles: {st.applicable_roles}")
    
    print(f"\n✅ Shift types updated successfully!\n")

if __name__ == '__main__':
    update_shift_types()
