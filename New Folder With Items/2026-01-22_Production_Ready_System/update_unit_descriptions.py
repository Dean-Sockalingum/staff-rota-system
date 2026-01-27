#!/usr/bin/env python
"""
Update unit descriptions to properly classify as Residential, SRD, or Management
Based on correct unit structure from CARE_INSPECTORATE_REPORTS_SUMMARY.md
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import Unit, CareHome

def update_unit_descriptions():
    """Update all unit descriptions with correct types"""
    
    # SRD (Specialist Residential Dementia) units
    srd_units = [
        'OG_PEAR',           # Orchard Grove
        'HH_SNOWDROP_SRD',   # Hawthorn House
        'HH_THISTLE_SRD',    # Hawthorn House
        'MB_POPPY_SRD',      # Meadowburn
        'RS_MAPLE',          # Riverside
    ]
    
    # Management units (for SM/OM office hours Mon-Fri 9-5)
    mgmt_units = [
        'OG_MGMT',
        'HH_MGMT',
        'MB_MGMT',
        'RS_MGMT',
        'VG_MGMT',
    ]
    
    updated_count = 0
    
    # Update SRD units
    for unit_name in srd_units:
        try:
            unit = Unit.objects.get(name=unit_name)
            unit.description = 'Specialist Residential Dementia (SRD)'
            unit.save()
            print(f"✅ Updated {unit_name}: {unit.description}")
            updated_count += 1
        except Unit.DoesNotExist:
            print(f"⚠️  Unit not found: {unit_name}")
    
    # Update MGMT units
    for unit_name in mgmt_units:
        try:
            unit = Unit.objects.get(name=unit_name)
            unit.description = 'Management (SM/OM Office - Mon-Fri 9am-5pm)'
            unit.save()
            print(f"✅ Updated {unit_name}: {unit.description}")
            updated_count += 1
        except Unit.DoesNotExist:
            print(f"⚠️  Unit not found: {unit_name}")
    
    # Update all other units to Residential
    all_units = Unit.objects.exclude(name__in=srd_units + mgmt_units)
    for unit in all_units:
        if unit.name != 'VICTORIA_MGMT':  # Skip duplicate
            unit.description = 'Residential (Frail Older People)'
            unit.save()
            print(f"✅ Updated {unit.name}: {unit.description}")
            updated_count += 1
    
    # Handle Victoria Gardens duplicate MGMT unit
    try:
        duplicate = Unit.objects.get(name='VICTORIA_MGMT')
        print(f"\n⚠️  Found duplicate Victoria Gardens MGMT unit (ID: {duplicate.id})")
        print(f"   This should be deleted or renamed to VG_AZALEA (missing residential unit)")
        print(f"   Current description: {duplicate.description}")
    except Unit.DoesNotExist:
        pass
    
    print(f"\n✅ Updated {updated_count} units")
    
    # Summary by home
    print("\n" + "="*70)
    print("SUMMARY BY HOME")
    print("="*70)
    
    for home in CareHome.objects.all().order_by('name'):
        units = Unit.objects.filter(care_home=home).order_by('name')
        residential = units.filter(description='Residential (Frail Older People)').count()
        srd = units.filter(description='Specialist Residential Dementia (SRD)').count()
        mgmt = units.filter(description='Management (SM/OM Office - Mon-Fri 9am-5pm)').count()
        
        print(f"\n{home.name}:")
        print(f"  Total Units: {units.count()}")
        print(f"  - Residential: {residential}")
        print(f"  - SRD: {srd}")
        print(f"  - MGMT: {mgmt}")
        
        if units.count() != (residential + srd + mgmt):
            print(f"  ⚠️  Uncategorized units found!")

if __name__ == '__main__':
    print("Updating unit descriptions...")
    print("="*70)
    update_unit_descriptions()
