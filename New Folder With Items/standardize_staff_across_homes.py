import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, CareHome, Unit, Role
from collections import defaultdict

print("=" * 80)
print("STANDARDIZING STAFF ACROSS 4 HOMES")
print("Using Orchard Grove as the baseline model")
print("=" * 80)

# Target structure from Orchard Grove
TARGET_ROLES = {
    'SCA': 52,
    'SCAN': 67,
    'SCW': 27,
    'SCWN': 14,
    'SM': 1,
    'SSCW': 9,
    'SSCWN': 8
}
TOTAL_TARGET = sum(TARGET_ROLES.values())  # 178

# Homes to standardize (excluding Victoria Gardens)
target_homes = ['HAWTHORN_HOUSE', 'MEADOWBURN', 'RIVERSIDE', 'ORCHARD_GROVE']

print(f"\nTarget staff per home: {TOTAL_TARGET}")
print(f"Target role distribution: {TARGET_ROLES}")
print(f"\nHomes to standardize: {', '.join(target_homes)}")

print("\n" + "=" * 80)
print("CURRENT STATE")
print("=" * 80)

for home_name in target_homes:
    home = CareHome.objects.get(name=home_name)
    units = Unit.objects.filter(care_home=home)
    staff = User.objects.filter(unit__in=units, is_active=True)
    
    role_counts = defaultdict(int)
    for s in staff:
        role_name = s.role.name if s.role else 'NO_ROLE'
        role_counts[role_name] += 1
    
    print(f"\n{home.get_name_display()}:")
    print(f"  Current total: {staff.count()}")
    print(f"  Target: {TOTAL_TARGET}")
    print(f"  Difference: {staff.count() - TOTAL_TARGET}")
    
    if staff.count() > TOTAL_TARGET:
        print(f"  ⚠️  Need to remove {staff.count() - TOTAL_TARGET} staff")

print("\n" + "=" * 80)
print("STANDARDIZATION PLAN")
print("=" * 80)
print("\nFor homes with excess staff (HH, MB, RS):")
print("1. Keep the first 178 staff (sorted by SAP number)")
print("2. Set is_active=False for the remaining staff")
print("3. This preserves data but removes them from active rosters")
print("\nOrchard Grove: No changes needed (already at target)")

proceed = input("\nProceed with standardization? (yes/no): ")

if proceed.lower() != 'yes':
    print("Standardization cancelled.")
    exit()

print("\n" + "=" * 80)
print("EXECUTING STANDARDIZATION")
print("=" * 80)

deactivated_total = 0

for home_name in target_homes:
    if home_name == 'ORCHARD_GROVE':
        print(f"\n{home_name}: Already at target, skipping")
        continue
    
    home = CareHome.objects.get(name=home_name)
    units = Unit.objects.filter(care_home=home)
    staff = User.objects.filter(unit__in=units, is_active=True).order_by('sap')
    
    current_count = staff.count()
    
    if current_count <= TOTAL_TARGET:
        print(f"\n{home.get_name_display()}: At or below target ({current_count}), skipping")
        continue
    
    # Keep first 178, deactivate the rest
    staff_to_keep = list(staff[:TOTAL_TARGET])
    staff_to_deactivate = list(staff[TOTAL_TARGET:])
    
    print(f"\n{home.get_name_display()}:")
    print(f"  Keeping: {len(staff_to_keep)} staff (SAP {staff_to_keep[0].sap} to {staff_to_keep[-1].sap})")
    print(f"  Deactivating: {len(staff_to_deactivate)} staff (SAP {staff_to_deactivate[0].sap} to {staff_to_deactivate[-1].sap})")
    
    # Deactivate excess staff
    for user in staff_to_deactivate:
        user.is_active = False
        user.save()
    
    deactivated_total += len(staff_to_deactivate)
    
    # Verify
    active_after = User.objects.filter(unit__in=units, is_active=True).count()
    print(f"  ✓ Verified: {active_after} active staff remaining")

print("\n" + "=" * 80)
print("STANDARDIZATION COMPLETE")
print("=" * 80)
print(f"\nTotal staff deactivated: {deactivated_total}")
print("Deactivated staff are preserved in database but excluded from active rosters")

# Final verification
print("\n" + "=" * 80)
print("FINAL STATE")
print("=" * 80)

for home_name in target_homes:
    home = CareHome.objects.get(name=home_name)
    units = Unit.objects.filter(care_home=home)
    staff = User.objects.filter(unit__in=units, is_active=True)
    print(f"{home.get_name_display():30} | Active staff: {staff.count()}")

print("\n✓ All 4 homes now have standardized staff counts")
