import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User
from django.db.models import Count

print("=" * 80)
print("CURRENT SAP NUMBER FORMATS")
print("=" * 80)

users = User.objects.all().order_by('sap')
print(f"\nTotal Users: {users.count()}")
print("\nSAP Number Examples:")
for user in users[:20]:
    print(f"  {user.sap:15} | {user.first_name} {user.last_name} | {user.unit.care_home.get_name_display() if user.unit else 'No Unit'}")

print("\n" + "=" * 80)
print("SAP NUMBER ANALYSIS")
print("=" * 80)

# Analyze SAP format
numeric_only = []
alphanumeric = []
various_lengths = {}

for user in users:
    sap = user.sap
    if sap.isdigit():
        numeric_only.append(sap)
    else:
        alphanumeric.append(sap)
    
    length = len(sap)
    various_lengths[length] = various_lengths.get(length, 0) + 1

print(f"\nNumeric only: {len(numeric_only)}")
print(f"Alphanumeric: {len(alphanumeric)}")
print(f"\nLength distribution:")
for length, count in sorted(various_lengths.items()):
    print(f"  {length} digits/chars: {count} users")

print("\n" + "=" * 80)
print("DUPLICATE NAMES")
print("=" * 80)

# Find duplicate names
duplicates = User.objects.values('first_name', 'last_name').annotate(
    count=Count('sap')
).filter(count__gt=1).order_by('-count')

if duplicates:
    print(f"\nFound {duplicates.count()} duplicate name combinations:\n")
    for dup in duplicates:
        full_name = f"{dup['first_name']} {dup['last_name']}"
        count = dup['count']
        print(f"  {full_name}: {count} users")
        
        # Show details of each duplicate
        users_with_name = User.objects.filter(
            first_name=dup['first_name'],
            last_name=dup['last_name']
        )
        for user in users_with_name:
            home = user.unit.care_home.get_name_display() if user.unit else 'No Unit'
            unit = user.unit.name if user.unit else 'N/A'
            print(f"    - SAP: {user.sap:10} | Home: {home:20} | Unit: {unit}")
        print()
else:
    print("\nNo duplicate names found - all names are unique!")

print("=" * 80)
