import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, CareHome, Unit
from collections import defaultdict

print("=" * 80)
print("ORCHARD GROVE STAFF STRUCTURE ANALYSIS")
print("=" * 80)

og = CareHome.objects.get(name='ORCHARD_GROVE')
og_units = Unit.objects.filter(care_home=og)

print(f"\nOrchard Grove Units: {og_units.count()}")
for unit in og_units:
    print(f"  - {unit.name}")

print(f"\n" + "=" * 80)
print("STAFF BY UNIT")
print("=" * 80)

total_staff = 0
unit_staff_count = {}

for unit in og_units:
    staff = User.objects.filter(unit=unit, is_active=True)
    unit_staff_count[unit.name] = staff.count()
    total_staff += staff.count()
    
    # Count by role
    role_counts = defaultdict(int)
    for s in staff:
        role_name = s.role.name if s.role else 'NO_ROLE'
        role_counts[role_name] += 1
    
    print(f"\n{unit.name}:")
    print(f"  Total: {staff.count()}")
    print(f"  By role:")
    for role, count in sorted(role_counts.items()):
        print(f"    {role}: {count}")

print(f"\n" + "=" * 80)
print(f"TOTAL ORCHARD GROVE STAFF: {total_staff}")
print("=" * 80)

# Analyze role distribution across all OG
all_og_staff = User.objects.filter(unit__in=og_units, is_active=True)
overall_roles = defaultdict(int)
for s in all_og_staff:
    role_name = s.role.name if s.role else 'NO_ROLE'
    overall_roles[role_name] += 1

print("\nOverall role distribution:")
for role, count in sorted(overall_roles.items()):
    print(f"  {role}: {count}")
