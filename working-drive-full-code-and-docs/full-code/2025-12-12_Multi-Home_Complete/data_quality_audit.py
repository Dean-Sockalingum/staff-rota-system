#!/usr/bin/env python3
"""
Comprehensive Data Quality Audit
Checks all aspects of the database for issues and cleans them.
"""

import os
import django
from datetime import datetime, timedelta
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Shift, Unit, CareHome, Role, ShiftType
from django.db.models import Count, Q
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

print("=" * 80)
print("🔍 COMPREHENSIVE DATA QUALITY AUDIT")
print("=" * 80)
print(f"Audit Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

issues_found = []
fixes_applied = []

# ============================================================================
# 1. STAFF DATA QUALITY
# ============================================================================
print("\n📋 1. STAFF DATA QUALITY")
print("-" * 80)

all_staff = User.objects.all()
active_staff = User.objects.filter(is_active=True).exclude(sap='000745')

print(f"Total staff records: {all_staff.count()}")
print(f"Active staff: {active_staff.count()}")
print(f"Inactive staff: {all_staff.count() - active_staff.count()}")

# 1.1 Check for duplicate SAP numbers
print("\n  1.1 SAP Number Integrity:")
sap_dupes = User.objects.values('sap').annotate(count=Count('sap')).filter(count__gt=1)
if sap_dupes:
    print(f"    ❌ {len(sap_dupes)} duplicate SAP numbers found!")
    issues_found.append(f"Duplicate SAP numbers: {len(sap_dupes)}")
else:
    print("    ✅ All SAP numbers unique")

# 1.2 Check SAP number format (should be 6 digits)
invalid_saps = User.objects.exclude(sap__regex=r'^\d{6}$')
if invalid_saps.exists():
    print(f"    ❌ {invalid_saps.count()} invalid SAP formats:")
    for user in invalid_saps[:5]:
        print(f"       - {user.sap}: {user.first_name} {user.last_name}")
    issues_found.append(f"Invalid SAP formats: {invalid_saps.count()}")
else:
    print("    ✅ All SAP numbers are 6 digits")

# 1.3 Check email validity
print("\n  1.2 Email Address Quality:")
invalid_emails = []
for user in all_staff:
    try:
        validate_email(user.email)
    except ValidationError:
        invalid_emails.append(user)

if invalid_emails:
    print(f"    ❌ {len(invalid_emails)} invalid email addresses:")
    for user in invalid_emails[:5]:
        print(f"       - SAP {user.sap}: {user.email}")
    issues_found.append(f"Invalid emails: {len(invalid_emails)}")
else:
    print("    ✅ All email addresses valid")

# 1.4 Check for duplicate emails
email_dupes = User.objects.values('email').annotate(count=Count('email')).filter(count__gt=1)
if email_dupes:
    print(f"    ❌ {len(email_dupes)} duplicate email addresses")
    issues_found.append(f"Duplicate emails: {len(email_dupes)}")
else:
    print("    ✅ All email addresses unique")

# 1.5 Check staff without roles
print("\n  1.3 Role Assignments:")
no_role = active_staff.filter(role__isnull=True)
if no_role.exists():
    print(f"    ❌ {no_role.count()} active staff without roles:")
    for user in no_role[:5]:
        print(f"       - SAP {user.sap}: {user.first_name} {user.last_name}")
    issues_found.append(f"Staff without roles: {no_role.count()}")
else:
    print("    ✅ All active staff have roles assigned")

# 1.6 Check staff without units
print("\n  1.4 Unit Assignments:")
no_unit = active_staff.filter(unit__isnull=True)
if no_unit.exists():
    print(f"    ❌ {no_unit.count()} active staff without units:")
    for user in no_unit[:5]:
        print(f"       - SAP {user.sap}: {user.first_name} {user.last_name} ({user.role.name if user.role else 'No Role'})")
    issues_found.append(f"Staff without units: {no_unit.count()}")
else:
    print("    ✅ All active staff have units assigned")

# 1.7 Check MGMT unit assignments
print("\n  1.5 MGMT Unit Compliance:")
care_roles = ['SCA', 'SCAN', 'SCW', 'SCWN', 'SSCW', 'SSCWN']
mgmt_violations = active_staff.filter(
    unit__name__icontains='MGMT',
    role__name__in=care_roles
)
if mgmt_violations.exists():
    print(f"    ❌ {mgmt_violations.count()} care staff in MGMT units:")
    for user in mgmt_violations[:5]:
        print(f"       - SAP {user.sap}: {user.role.name} in {user.unit.name}")
    issues_found.append(f"Care staff in MGMT units: {mgmt_violations.count()}")
else:
    print("    ✅ MGMT units contain only SM/OM staff")

# 1.8 Check name quality
print("\n  1.6 Name Quality:")
names_with_suffixes = active_staff.filter(
    Q(last_name__contains='(') | Q(first_name__contains='(')
)
if names_with_suffixes.exists():
    print(f"    ❌ {names_with_suffixes.count()} names with suffixes/brackets:")
    for user in names_with_suffixes[:5]:
        print(f"       - SAP {user.sap}: {user.first_name} {user.last_name}")
    issues_found.append(f"Names with suffixes: {names_with_suffixes.count()}")
else:
    print("    ✅ All names clean (no suffixes)")

# ============================================================================
# 2. SHIFT DATA QUALITY
# ============================================================================
print("\n" + "=" * 80)
print("📅 2. SHIFT DATA QUALITY")
print("-" * 80)

all_shifts = Shift.objects.all()
print(f"Total shift records: {all_shifts.count()}")

# 2.1 Check for orphaned shifts (user doesn't exist)
print("\n  2.1 Orphaned Shifts:")
orphaned_shifts = Shift.objects.filter(user__isnull=True)
if orphaned_shifts.exists():
    print(f"    ❌ {orphaned_shifts.count()} shifts with no user assigned")
    issues_found.append(f"Orphaned shifts: {orphaned_shifts.count()}")
else:
    print("    ✅ All shifts have valid users")

# 2.2 Check for shifts with invalid units
print("\n  2.2 Shift Unit Validity:")
invalid_unit_shifts = Shift.objects.filter(unit__isnull=True)
if invalid_unit_shifts.exists():
    print(f"    ❌ {invalid_unit_shifts.count()} shifts with no unit assigned")
    issues_found.append(f"Shifts without units: {invalid_unit_shifts.count()}")
else:
    print("    ✅ All shifts have valid units")

# 2.3 Check for shifts with invalid shift types
print("\n  2.3 Shift Type Validity:")
invalid_type_shifts = Shift.objects.filter(shift_type__isnull=True)
if invalid_type_shifts.exists():
    print(f"    ❌ {invalid_type_shifts.count()} shifts with no shift type")
    issues_found.append(f"Shifts without types: {invalid_type_shifts.count()}")
else:
    print("    ✅ All shifts have valid shift types")

# 2.4 Check for future-dated shifts beyond reasonable range
print("\n  2.4 Date Range Validity:")
far_future = datetime.now().date() + timedelta(days=730)  # 2 years
far_future_shifts = Shift.objects.filter(date__gt=far_future)
if far_future_shifts.exists():
    print(f"    ⚠️  {far_future_shifts.count()} shifts scheduled more than 2 years ahead")
else:
    print("    ✅ All shifts within reasonable date range")

# 2.5 Check date range
from django.db.models import Min, Max
date_range = all_shifts.aggregate(
    min_date=Min('date'),
    max_date=Max('date')
)
if date_range['min_date'] and date_range['max_date']:
    print(f"    📊 Shift date range: {date_range['min_date']} to {date_range['max_date']}")
    total_days = (date_range['max_date'] - date_range['min_date']).days
    print(f"    📊 Spans {total_days} days ({total_days/30:.1f} months)")

# 2.6 Check for potential duplicate shifts (same user, date, unit, type)
print("\n  2.5 Duplicate Shift Detection:")
duplicate_shifts = Shift.objects.values(
    'user', 'date', 'unit', 'shift_type'
).annotate(
    count=Count('id')
).filter(count__gt=1)

if duplicate_shifts:
    print(f"    ⚠️  {len(duplicate_shifts)} potential duplicate shift patterns")
    total_dupes = sum(d['count'] - 1 for d in duplicate_shifts)
    print(f"    ⚠️  {total_dupes} duplicate shift records")
    issues_found.append(f"Duplicate shifts: {total_dupes}")
else:
    print("    ✅ No duplicate shifts detected")

# ============================================================================
# 3. UNIT DATA QUALITY
# ============================================================================
print("\n" + "=" * 80)
print("🏢 3. UNIT DATA QUALITY")
print("-" * 80)

all_units = Unit.objects.all()
print(f"Total units: {all_units.count()}")

# 3.1 Check units without care homes
print("\n  3.1 Care Home Assignments:")
no_home = all_units.filter(care_home__isnull=True)
if no_home.exists():
    print(f"    ❌ {no_home.count()} units without care home assignment:")
    for unit in no_home:
        print(f"       - {unit.name}")
    issues_found.append(f"Units without care homes: {no_home.count()}")
else:
    print("    ✅ All units assigned to care homes")

# 3.2 Check unit distribution
print("\n  3.2 Unit Distribution by Care Home:")
for home in CareHome.objects.all():
    unit_count = home.units.count()
    mgmt_count = home.units.filter(name__icontains='MGMT').count()
    care_count = unit_count - mgmt_count
    expected_care = 8 if home.name != 'VICTORIA_GARDENS' else 5
    
    status = "✅" if care_count == expected_care and mgmt_count == 1 else "⚠️"
    print(f"    {status} {home.name}: {care_count} care units + {mgmt_count} MGMT (expected {expected_care}+1)")
    
    if care_count != expected_care or mgmt_count != 1:
        issues_found.append(f"{home.name}: incorrect unit count")

# ============================================================================
# 4. ROLE DATA QUALITY
# ============================================================================
print("\n" + "=" * 80)
print("👥 4. ROLE DATA QUALITY")
print("-" * 80)

all_roles = Role.objects.all()
print(f"Total roles: {all_roles.count()}")

# 4.1 Check expected roles exist
expected_roles = ['SM', 'OM', 'SSCW', 'SSCWN', 'SCW', 'SCWN', 'SCA', 'SCAN', 'HOS', 'Admin']
print("\n  4.1 Expected Roles:")
for role_name in expected_roles:
    try:
        role = Role.objects.get(name=role_name)
        print(f"    ✅ {role_name}: {role.user_set.filter(is_active=True).count()} active staff")
    except Role.DoesNotExist:
        print(f"    ❌ {role_name}: MISSING")
        issues_found.append(f"Missing role: {role_name}")

# 4.2 Check for roles without staff
print("\n  4.2 Unused Roles:")
unused_roles = Role.objects.annotate(
    staff_count=Count('user', filter=Q(user__is_active=True))
).filter(staff_count=0)

if unused_roles.exists():
    print(f"    ⚠️  {unused_roles.count()} roles with no active staff:")
    for role in unused_roles:
        print(f"       - {role.name}")
else:
    print("    ✅ All roles have active staff")

# ============================================================================
# 5. CARE HOME DATA QUALITY
# ============================================================================
print("\n" + "=" * 80)
print("🏠 5. CARE HOME DATA QUALITY")
print("-" * 80)

all_homes = CareHome.objects.all()
print(f"Total care homes: {all_homes.count()}")

expected_homes = ['ORCHARD_GROVE', 'HAWTHORN_HOUSE', 'MEADOWBURN', 'RIVERSIDE', 'VICTORIA_GARDENS']
print("\n  5.1 Expected Care Homes:")
for home_name in expected_homes:
    try:
        home = CareHome.objects.get(name=home_name)
        staff_count = User.objects.filter(unit__care_home=home, is_active=True).count()
        print(f"    ✅ {home_name}: {staff_count} active staff")
    except CareHome.DoesNotExist:
        print(f"    ❌ {home_name}: MISSING")
        issues_found.append(f"Missing care home: {home_name}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("📊 AUDIT SUMMARY")
print("=" * 80)

if issues_found:
    print(f"\n⚠️  ISSUES FOUND: {len(issues_found)}")
    for i, issue in enumerate(issues_found, 1):
        print(f"  {i}. {issue}")
else:
    print("\n✅ NO ISSUES FOUND - Database is clean!")

if fixes_applied:
    print(f"\n🔧 FIXES APPLIED: {len(fixes_applied)}")
    for i, fix in enumerate(fixes_applied, 1):
        print(f"  {i}. {fix}")

print("\n" + "=" * 80)
print("✅ AUDIT COMPLETE")
print("=" * 80)

# Save audit report
report_path = 'DATA_QUALITY_AUDIT_REPORT.txt'
with open(report_path, 'w') as f:
    f.write(f"Data Quality Audit Report\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("=" * 80 + "\n\n")
    
    if issues_found:
        f.write(f"ISSUES FOUND: {len(issues_found)}\n")
        for issue in issues_found:
            f.write(f"  - {issue}\n")
    else:
        f.write("NO ISSUES FOUND - Database is clean!\n")
    
    if fixes_applied:
        f.write(f"\nFIXES APPLIED: {len(fixes_applied)}\n")
        for fix in fixes_applied:
            f.write(f"  - {fix}\n")

print(f"\n📄 Report saved to: {report_path}")
