#!/usr/bin/env python
"""Delete the incorrectly created VG_AZALEA unit"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, '/home/staff-rota-system/2025-12-12_Multi-Home_Complete')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'staff_rota_project.settings')
django.setup()

from scheduling.models import Unit

# Delete VG_AZALEA unit
deleted_count, _ = Unit.objects.filter(name='VG_AZALEA').delete()
print(f"✓ Deleted {deleted_count} VG_AZALEA unit(s)")

# Verify Victoria Gardens units
vg_units = Unit.objects.filter(name__startswith='VG_').order_by('name')
print(f"\nVictoria Gardens now has {vg_units.count()} units:")
for unit in vg_units:
    print(f"  - {unit.name}")
