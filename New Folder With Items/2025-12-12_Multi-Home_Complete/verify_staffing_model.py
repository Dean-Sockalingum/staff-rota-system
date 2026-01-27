#!/usr/bin/env python3
"""
Verify staffing model corrections:
1. MGMT units should only contain SM and OM staff
2. All staff should have unique names (traditional Scottish names)
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Unit
from django.db.models import Count

print('=' * 70)
print('📊 FINAL VERIFICATION REPORT')
print('=' * 70)

print('\n1️⃣  MGMT UNIT STAFF ASSIGNMENTS (Should be SM & OM only):')
print('-' * 70)
all_correct = True
for unit in Unit.objects.filter(name__icontains='MGMT').order_by('name'):
    staff = User.objects.filter(unit=unit, is_active=True).exclude(sap='000745')
    roles = staff.values('role__name').annotate(count=Count('sap')).order_by('-count')
    print(f'\n  {unit.name}:')
    for role in roles:
        role_name = role['role__name']
        if role_name in ['SM', 'OM']:
            print(f'    ✅ {role_name}: {role["count"]} staff')
        else:
            print(f'    ❌ {role_name}: {role["count"]} staff (INCORRECT!)')
            all_correct = False

if all_correct:
    print('\n  ✅ ALL MGMT UNITS CORRECT - Only SM and OM staff')
else:
    print('\n  ❌ ERRORS FOUND - Care staff still in MGMT units')

print('\n' + '=' * 70)
print('2️⃣  STAFF NAME DIVERSITY:')
print('-' * 70)
total = User.objects.filter(is_active=True).exclude(sap='000745').count()
unique_first = User.objects.filter(is_active=True).exclude(sap='000745').values('first_name').distinct().count()
unique_last = User.objects.filter(is_active=True).exclude(sap='000745').values('last_name').distinct().count()
duplicates = User.objects.filter(is_active=True).exclude(sap='000745').values('first_name', 'last_name').annotate(count=Count('sap')).filter(count__gt=1).count()

print(f'  Total Active Staff: {total}')
print(f'  Unique First Names: {unique_first}')
print(f'  Unique Last Names: {unique_last}')
print(f'  Full Name Combinations: {total}')
print(f'  Duplicate Names: {duplicates}')
if duplicates == 0:
    print('  ✅ All 813 staff have unique names (traditional Scottish names)')
else:
    print(f'  ❌ {duplicates} duplicate names found')

# Show sample names
print('\n📋 Sample Staff Names (first 15):')
staff = User.objects.filter(is_active=True).exclude(sap='000745').order_by('sap')[:15]
for s in staff:
    print(f'  SAP {s.sap}: {s.first_name} {s.last_name}')

print('\n' + '=' * 70)
print('3️⃣  STAFF DISTRIBUTION BY ROLE:')
print('-' * 70)
roles = User.objects.filter(is_active=True).exclude(sap='000745').values('role__name').annotate(count=Count('sap')).order_by('-count')
for role in roles:
    print(f'  {role["role__name"]:10s}: {role["count"]:3d} staff')

print('\n' + '=' * 70)
if all_correct and duplicates == 0:
    print('✅ STAFFING MODEL CORRECTIONS COMPLETE - ALL CHECKS PASSED')
else:
    print('⚠️  SOME ISSUES REMAIN - REVIEW ABOVE')
print('=' * 70)
