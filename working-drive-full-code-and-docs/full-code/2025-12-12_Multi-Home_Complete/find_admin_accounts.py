import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User

print("=" * 80)
print("ADMIN & SUPERUSER ACCOUNTS - NEW SAP NUMBERS")
print("=" * 80)
print()

# Find superusers
superusers = User.objects.filter(is_superuser=True).order_by('sap')
print(f"SUPERUSER ACCOUNTS ({superusers.count()}):")
print("-" * 80)
for user in superusers:
    home = user.unit.care_home.get_name_display() if user.unit else 'No Home'
    role = user.role.get_name_display() if user.role else 'No Role'
    print(f"  SAP: {user.sap}")
    print(f"  Name: {user.first_name} {user.last_name}")
    print(f"  Email: {user.email}")
    print(f"  Role: {role}")
    print(f"  Home: {home}")
    print()

# Find management staff
print("\n" + "=" * 80)
print("MANAGEMENT STAFF (Operations Managers)")
print("=" * 80)
managers = User.objects.filter(role__name='OPERATIONS_MANAGER').order_by('sap')
for user in managers:
    home = user.unit.care_home.get_name_display() if user.unit else 'No Home'
    print(f"  SAP: {user.sap} | {user.first_name} {user.last_name:30} | {home}")

# Find staff with specific old SAP patterns that might be admins
print("\n" + "=" * 80)
print("LIKELY ADMIN ACCOUNTS (based on SAP range)")
print("=" * 80)
print("First 20 staff members (likely to include admins):")
first_staff = User.objects.all().order_by('sap')[:20]
for user in first_staff:
    home = user.unit.care_home.get_name_display() if user.unit else 'No Home'
    role = user.role.get_name_display() if user.role else 'No Role'
    is_staff = "✓" if user.is_staff else " "
    is_super = "⭐" if user.is_superuser else " "
    print(f"  {is_super} {is_staff} SAP: {user.sap} | {user.first_name} {user.last_name:25} | {role:30} | {home}")

print("\n" + "=" * 80)
print("LOGIN INSTRUCTIONS")
print("=" * 80)
print("""
To log in, use:
  • Username: Your new 6-digit SAP number (e.g., 000001)
  • Password: Your existing password (unchanged)

If you don't remember your password, you can reset it using Django admin
or create a new superuser account.
""")
