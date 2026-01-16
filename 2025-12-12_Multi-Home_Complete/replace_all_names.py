#!/usr/bin/env python3
"""
Replace ALL staff names with unique traditional Scottish names.
"""

import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User

# Traditional Scottish first names
FIRST_NAMES = [
    # Male names
    'Alasdair', 'Alistair', 'Angus', 'Archie', 'Blair', 'Boyd', 'Bruce', 'Callum',
    'Cameron', 'Campbell', 'Colin', 'Craig', 'David', 'Donald', 'Douglas', 'Duncan', 
    'Ewan', 'Fergus', 'Finlay', 'Fraser', 'Gavin', 'Gordon', 'Graham', 'Grant',
    'Gregor', 'Hamish', 'Hugh', 'Iain', 'Ian', 'Jamie', 'Kenneth', 'Lachlan',
    'Logan', 'Magnus', 'Malcolm', 'Murray', 'Neil', 'Niall', 'Rory', 'Ross',
    'Scott', 'Stewart', 'Stuart', 'Wallace', 'William', 'Andrew', 'Alan', 'Alexander',
    'Brian', 'Charles', 'Derek', 'Eric', 'Frank', 'George', 'Gerald',
    'Harry', 'Jack', 'James', 'John', 'Keith', 'Kevin', 'Lewis', 'Mark',
    'Michael', 'Norman', 'Oliver', 'Patrick', 'Paul', 'Peter', 'Philip', 'Richard',
    'Robert', 'Ronald', 'Samuel', 'Stephen', 'Thomas', 'Timothy', 'Walter', 'Wayne',
    # Female names  
    'Ailsa', 'Aileen', 'Bonnie', 'Catriona', 'Eilidh', 'Elspeth', 'Fiona', 'Flora',
    'Heather', 'Isla', 'Jeanette', 'Kirsty', 'Lesley', 'Mairi', 'Morag', 'Rhona',
    'Senga', 'Shona', 'Una', 'Agnes', 'Alice', 'Anne', 'Beth', 'Carol',
    'Catherine', 'Christine', 'Clare', 'Diane', 'Elizabeth', 'Emma', 'Frances', 'Grace',
    'Hannah', 'Helen', 'Isabel', 'Jacqueline', 'Janet', 'Jean', 'Jennifer', 'Jessica',
    'Joan', 'Joyce', 'Judith', 'Karen', 'Kate', 'Katherine', 'Laura', 'Linda',
    'Louise', 'Lucy', 'Margaret', 'Marion', 'Mary', 'Maureen', 'Megan', 'Michelle',
    'Nicola', 'Olivia', 'Patricia', 'Rachel', 'Rebecca', 'Ruth', 'Sally', 'Sandra',
    'Sarah', 'Sharon', 'Sophie', 'Susan', 'Teresa', 'Tracy', 'Victoria', 'Wendy',
    'Ava', 'Charlotte', 'Chloe', 'Emily', 'Evie', 'Freya', 'Georgia', 'Holly',
    'Iris', 'Lily', 'Maisie', 'Millie', 'Poppy', 'Rose', 'Ruby', 'Skye'
]

# Traditional Scottish surnames
SURNAMES = [
    'Anderson', 'Armstrong', 'Bell', 'Black', 'Brown', 'Campbell', 'Cameron', 'Clark',
    'Crawford', 'Davidson', 'Douglas', 'Duncan', 'Elliott', 'Ferguson', 'Forbes', 'Fraser',
    'Gibson', 'Gordon', 'Graham', 'Grant', 'Gray', 'Hamilton', 'Henderson', 'Hunter',
    'Johnston', 'Kelly', 'Kennedy', 'Kerr', 'MacDonald', 'MacKenzie', 'MacLean', 'MacLeod',
    'Marshall', 'Martin', 'Miller', 'Mitchell', 'Morrison', 'Munro', 'Murray', 'Paterson',
    'Reid', 'Robertson', 'Ross', 'Scott', 'Simpson', 'Smith', 'Stewart', 'Sutherland',
    'Taylor', 'Thomson', 'Walker', 'Wallace', 'Watson', 'White', 'Wilson', 'Young',
    'Allan', 'Baird', 'Bruce', 'Burns', 'Burnett', 'Carr', 'Christie', 'Cunningham',
    'Currie', 'Docherty', 'Drummond', 'Duff', 'Dunn', 'Fleming', 'Fletcher', 'Forsyth',
    'Gillespie', 'Goodwin', 'Greig', 'Hay', 'Hogg', 'Hughes', 'Inglis', 'Irvine',
    'Jackson', 'Johnstone', 'Keith', 'Lamont', 'Lang', 'Lawson', 'Lindsay', 'Logan',
    'MacGregor', 'MacIntosh', 'MacIntyre', 'MacKay', 'MacLaren', 'MacMillan', 'MacNeil',
    'MacPherson', 'MacRae', 'Mair', 'Maxwell', 'McAllister', 'McBride', 'McCabe',
    'McCall', 'McCann', 'McCarthy', 'McCormick', 'McCulloch', 'McDonald', 'McFarlane',
    'McGill', 'McGrath', 'McGregor', 'McGuire', 'McIntyre', 'McKay', 'McKenzie',
    'McLean', 'McLeod', 'McMillan', 'McNeil', 'McPherson', 'Menzies', 'Moir',
    'Nicholson', 'Ogilvie', 'Parker', 'Pollock', 'Rae', 'Ramsay', 'Rennie',
    'Ritchie', 'Russell', 'Semple', 'Shaw', 'Sinclair', 'Sloan', 'Stevenson', 'Stirling',
    'Strachan', 'Struthers', 'Sym', 'Tennant', 'Urquhart', 'Watt', 'Weir', 'Woods'
]

print("🏴 Replacing ALL Staff Names with Unique Scottish Names")
print("=" * 70)

# Get all active staff
all_staff = list(User.objects.filter(is_active=True).exclude(sap='000745').order_by('sap'))
print(f"\n📊 Total staff to update: {len(all_staff)}")

# Generate all possible unique name combinations
all_combinations = []
for first in FIRST_NAMES:
    for surname in SURNAMES:
        all_combinations.append((first, surname))

# Shuffle for randomness
random.shuffle(all_combinations)

print(f"📊 Available unique name combinations: {len(all_combinations)}")

if len(all_combinations) < len(all_staff):
    print(f"⚠️  Warning: Not enough unique combinations! Need {len(all_staff) - len(all_combinations)} more")
else:
    print(f"✅ Sufficient unique names available")

# Assign names
print("\n🔄 Assigning unique names...")
updated = 0
errors = 0

for i, staff in enumerate(all_staff):
    if i < len(all_combinations):
        first_name, surname = all_combinations[i]
        try:
            User.objects.filter(sap=staff.sap).update(
                first_name=first_name,
                last_name=surname
            )
            updated += 1
            if updated % 100 == 0:
                print(f"  Updated {updated}/{len(all_staff)}...")
        except Exception as e:
            print(f"  ⚠️  Error updating SAP {staff.sap}: {e}")
            errors += 1
    else:
        print(f"  ⚠️  No name available for SAP {staff.sap}")
        errors += 1

print(f"\n✅ Updated: {updated}")
print(f"❌ Errors: {errors}")

# Verify
print("\n" + "=" * 70)
print("📊 VERIFICATION")
print("=" * 70)

from collections import Counter
final_staff = User.objects.filter(is_active=True).exclude(sap='000745')
final_names = [(s.first_name, s.last_name) for s in final_staff]
final_counts = Counter(final_names)
final_dupes = {name: count for name, count in final_counts.items() if count > 1}

print(f"Total staff: {len(final_staff)}")
print(f"Unique names: {len(set(final_names))}")
print(f"Duplicates: {len(final_dupes)}")

if final_dupes:
    print("\n⚠️  Duplicates found:")
    for (first, last), count in sorted(final_dupes.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {first} {last}: {count} times")
else:
    print("\n✅ All staff have unique names!")

# Show samples
print("\n📋 Sample staff (first 15):")
for staff in list(final_staff.order_by('sap')[:15]):
    print(f"  SAP {staff.sap}: {staff.first_name} {staff.last_name} - {staff.role.name if staff.role else 'No Role'}")

print("\n📋 Previously duplicated staff (from screenshot):")
for sap in ['000953', '001013', '001073', '000773', '000833', '000893', '001133', '001193']:
    try:
        staff = User.objects.get(sap=sap)
        print(f"  SAP {sap}: {staff.first_name} {staff.last_name} - {staff.role.name}")
    except:
        print(f"  SAP {sap}: NOT FOUND")

print("\n" + "=" * 70)
print("✅ COMPLETE")
print("=" * 70)
