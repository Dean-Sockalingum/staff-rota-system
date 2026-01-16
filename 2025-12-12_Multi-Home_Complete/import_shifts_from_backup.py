#!/usr/bin/env python3
"""
Import shift/rota data from production backup database.
Handles unit name mapping and staff SAP mapping.
"""

import sqlite3
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import Shift, User, Unit, ShiftType
from django.db import transaction

# Unit name mapping (old names -> new prefixed names)
UNIT_MAPPING = {
    # Orchard Grove
    'BRAMLEY': 'OG_BRAMLEY',
    'CHERRY': 'OG_CHERRY',
    'GRAPE': 'OG_GRAPE',
    'ORANGE': 'OG_ORANGE',
    'PEACH': 'OG_PEACH',
    'PEAR': 'OG_PEAR',
    'PLUM': 'OG_PLUM',
    'STRAWBERRY': 'OG_STRAWBERRY',
    'OG_MANAGEMENT': 'OG_MGMT',
    'MGMT': 'OG_MGMT',
    
    # Hawthorn House
    'BLUEBELL': 'HH_BLUEBELL',
    'DAISY': 'HH_DAISY',
    'HEATHER': 'HH_HEATHER',
    'IRIS': 'HH_IRIS',
    'PRIMROSE': 'HH_PRIMROSE',
    'SNOWDROP': 'HH_SNOWDROP_SRD',
    'SNOWDROP_SRD': 'HH_SNOWDROP_SRD',
    'THISTLE': 'HH_THISTLE_SRD',
    'THISTLE_SRD': 'HH_THISTLE_SRD',
    'VIOLET': 'HH_VIOLET',
    'HH_MANAGEMENT': 'HH_MGMT',
    
    # Meadowburn
    'ASTER': 'MB_ASTER',
    'CORNFLOWER': 'MB_CORNFLOWER',
    'FOXGLOVE': 'MB_FOXGLOVE',
    'HONEYSUCKLE': 'MB_HONEYSUCKLE',
    'MARIGOLD': 'MB_MARIGOLD',
    'POPPY': 'MB_POPPY_SRD',
    'POPPY_SRD': 'MB_POPPY_SRD',
    'MB_BLUEBELL': 'MB_BLUEBELL',
    'MB_DAISY': 'MB_DAISY',
    'MB_MANAGEMENT': 'MB_MGMT',
    
    # Riverside
    'DAFFODIL': 'RS_DAFFODIL',
    'JASMINE': 'RS_JASMINE',
    'LILY': 'RS_LILY',
    'LOTUS': 'RS_LOTUS',
    'MAPLE': 'RS_MAPLE',
    'ORCHID': 'RS_ORCHID',
    'ROSE': 'RS_ROSE',
    'RS_HEATHER': 'RS_HEATHER',
    'RS_MANAGEMENT': 'RS_MGMT',
    
    # Victoria Gardens
    'AZALEA': 'VG_AZALEA',
    'CROCUS': 'VG_CROCUS',
    'TULIP': 'VG_TULIP',
    'VG_LILY': 'VG_LILY',
    'VG_ROSE': 'VG_ROSE',
    'VG_MANAGEMENT': 'VG_MGMT',
    'VICTORIA_MGMT': 'VG_MGMT',  # Old name in backup
    'VG_AZALEA': 'VG_AZALEA',
    'VG_CROCUS': 'VG_CROCUS',
    'VG_TULIP': 'VG_TULIP',
    'VG_MGMT': 'VG_MGMT',
}

# Shift type mapping (old names -> new names)
SHIFT_TYPE_MAPPING = {
    'DAY_SENIOR': 'DAY',
    'DAY_ASSISTANT': 'DAY',
    'NIGHT_SENIOR': 'NIGHT',
    'NIGHT_ASSISTANT': 'NIGHT',
    'ADMIN': 'DAY',
    'LONG_DAY': 'LONG_DAY',
    'NIGHT': 'NIGHT',
    'DAY': 'DAY',
    'EARLY': 'EARLY',
    'LATE': 'LATE',
    'OFF': 'OFF',
    'ANNUAL_LEAVE': 'ANNUAL_LEAVE',
}

def main():
    print("\n" + "="*70)
    print("IMPORTING SHIFT/ROTA DATA FROM PRODUCTION BACKUP")
    print("="*70)
    
    backup_db = 'db_demo.sqlite3'
    
    if not os.path.exists(backup_db):
        print(f"\n❌ Backup database not found: {backup_db}")
        return
    
    # Connect to backup database
    conn = sqlite3.connect(backup_db)
    cursor = conn.cursor()
    
    # Import shifts in date ranges to manage memory
    # Let's import from Jan 1, 2025 to Jan 31, 2026 (13 months of data)
    start_date = '2025-01-01'
    end_date = '2026-01-31'
    
    print(f"\n📅 Importing shifts from {start_date} to {end_date}")
    
    # Get shift data
    cursor.execute('''
        SELECT 
            s.id,
            s.user_id,
            s.date,
            st.name as shift_type_name,
            s.unit_id,
            unit.name as unit_name,
            s.notes,
            s.custom_start_time,
            s.custom_end_time
        FROM scheduling_shift s
        LEFT JOIN scheduling_shifttype st ON s.shift_type_id = st.id
        LEFT JOIN scheduling_unit unit ON s.unit_id = unit.id
        WHERE s.date BETWEEN ? AND ?
        ORDER BY s.date, s.user_id
    ''', (start_date, end_date))
    
    shift_data = cursor.fetchall()
    conn.close()
    
    print(f"\n📊 Found {len(shift_data):,} shifts in backup")
    
    # Get current database objects
    users_map = {u.sap: u for u in User.objects.all()}
    units_map = {u.name: u for u in Unit.objects.all()}
    shift_types_map = {st.name: st for st in ShiftType.objects.all()}
    
    created = 0
    updated = 0
    skipped = 0
    errors = []
    
    print("\n🔄 Importing shifts (this may take a few minutes)...")
    
    # Clear existing shifts in this date range first
    print(f"\n🗑️  Clearing existing shifts from {start_date} to {end_date}...")
    deleted_count = Shift.objects.filter(date__range=[start_date, end_date]).delete()[0]
    print(f"   Deleted {deleted_count:,} existing shifts")
    
    batch_size = 1000
    shifts_to_create = []
    
    debug_first_10_skips = []
    
    for idx, row in enumerate(shift_data, 1):
        shift_id, user_sap, date, shift_type_name, unit_id, unit_name, notes, start_time, end_time = row
        
        try:
            # Get staff
            staff = users_map.get(user_sap)
            if not staff:
                if len(debug_first_10_skips) < 10:
                    debug_first_10_skips.append(f"No staff found for SAP: {user_sap}")
                skipped += 1
                continue
            
            # Map unit name - backup already has correct names, just handle special case
            mapped_unit_name = unit_name
            if unit_name:
                # Special case: VICTORIA_MGMT -> VG_MGMT
                if unit_name.upper() == 'VICTORIA_MGMT':
                    mapped_unit_name = 'VG_MGMT'
                else:
                    # Try mapping, otherwise use original name
                    old_unit_upper = unit_name.upper()
                    mapped_unit_name = UNIT_MAPPING.get(old_unit_upper, unit_name)
            
            unit = units_map.get(mapped_unit_name)
            if not unit:
                if len(debug_first_10_skips) < 10:
                    debug_first_10_skips.append(f"No unit found: {unit_name} -> {mapped_unit_name}")
                skipped += 1
                continue
            
            # Get shift type - map old names to new
            mapped_shift_type_name = SHIFT_TYPE_MAPPING.get(shift_type_name, shift_type_name)
            shift_type_obj = shift_types_map.get(mapped_shift_type_name)
            if not shift_type_obj:
                if len(debug_first_10_skips) < 10:
                    debug_first_10_skips.append(f"No shift type: {shift_type_name} -> {mapped_shift_type_name}")
                skipped += 1
                continue
            
            # Create shift object (don't save yet)
            shift = Shift(
                user=staff,
                date=date,
                shift_type=shift_type_obj,
                unit=unit,
                status='SCHEDULED',
                shift_classification='REGULAR',
                shift_pattern='DAY_0800_2000' if mapped_shift_type_name != 'NIGHT' else 'NIGHT_2000_0800',
                notes=notes or '',
            )
            shifts_to_create.append(shift)
            
            # Bulk create when batch is full
            if len(shifts_to_create) >= batch_size:
                with transaction.atomic():
                    Shift.objects.bulk_create(shifts_to_create, ignore_conflicts=True)
                created += len(shifts_to_create)
                shifts_to_create = []
                if created % 10000 == 0:
                    print(f"   ✅ Created {created:,} shifts...")
        
        except Exception as e:
            errors.append(f"Shift ID {shift_id}: {str(e)}")
            if len(errors) <= 10:
                print(f"  ❌ Error on shift {shift_id}: {str(e)}")
            skipped += 1
    
    # Create remaining shifts
    if shifts_to_create:
        with transaction.atomic():
            Shift.objects.bulk_create(shifts_to_create, ignore_conflicts=True)
        created += len(shifts_to_create)
    
    print("\n" + "="*70)
    print("IMPORT COMPLETE")
    print("="*70)
    
    print(f"\n📊 Summary:")
    print(f"  • Created: {created:,}")
    print(f"  • Updated: {updated:,}")
    print(f"  • Skipped: {skipped:,}")
    print(f"  • Errors: {len(errors):,}")
    
    if debug_first_10_skips:
        print(f"\n⚠️  Sample skip reasons:")
        for reason in debug_first_10_skips:
            print(f"  {reason}")
    
    if errors and len(errors) <= 10:
        print(f"\n⚠️  Errors:")
        for error in errors[:10]:
            print(f"  {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")
    
    # Final verification
    total_shifts = Shift.objects.filter(date__range=[start_date, end_date]).count()
    print(f"\n✅ Total shifts in database ({start_date} to {end_date}): {total_shifts:,}")
    
    # Show sample by month
    print(f"\n📅 Shifts by Month:")
    from django.db.models import Count
    from django.db.models.functions import TruncMonth
    
    monthly_counts = Shift.objects.filter(
        date__range=[start_date, end_date]
    ).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')[:6]  # Show first 6 months
    
    for item in monthly_counts:
        month_str = item['month'].strftime('%B %Y')
        print(f"  {month_str:20s}: {item['count']:5,} shifts")
    
    print("\n" + "="*70)

if __name__ == '__main__':
    main()
