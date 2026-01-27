import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Unit, CareHome

print("=" * 80)
print("STAFF AND UNIT ANALYSIS")
print("=" * 80)

# Check care homes
homes = CareHome.objects.all()
print(f"\nCare Homes: {homes.count()}")
for home in homes:
    print(f"  - {home.get_name_display()} ({home.name})")

# Check units
units = Unit.objects.all()
print(f"\nUnits: {units.count()}")
for unit in units:
    home_name = unit.care_home.get_name_display() if unit.care_home else "NO HOME"
    staff_count = User.objects.filter(unit=unit, is_active=True).count()
    print(f"  - {unit.name:30} | Home: {home_name:20} | Staff: {staff_count}")

# Check staff by home
print("\n" + "=" * 80)
print("STAFF COUNT BY HOME")
print("=" * 80)
for home in homes:
    units_in_home = Unit.objects.filter(care_home=home)
    staff_count = User.objects.filter(unit__in=units_in_home, is_active=True).count()
    print(f"{home.get_name_display():30} | Units: {units_in_home.count():2} | Staff: {staff_count}")

# Check users without units
print("\n" + "=" * 80)
print("USERS WITHOUT UNITS")
print("=" * 80)
users_without_unit = User.objects.filter(unit__isnull=True)
print(f"Total: {users_without_unit.count()}")
for user in users_without_unit:
    print(f"  SAP: {user.sap} | {user.first_name} {user.last_name} | Role: {user.role.name if user.role else 'None'}")
