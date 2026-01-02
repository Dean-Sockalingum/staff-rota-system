#!/usr/bin/env python3
"""
Generate unique Scottish names for all 813 staff members.
Replace duplicate names with traditional Scottish names.
"""

import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User
from django.db.models import Count

# Traditional Scottish first names
SCOTTISH_FIRST_NAMES_MALE = [
    'Alasdair', 'Alistair', 'Angus', 'Archie', 'Blair', 'Boyd', 'Bruce', 'Callum',
    'Cameron', 'Campbell', 'Colin', 'Craig', 'David', 'Donald', 'Douglas', 'Duncan', 
    'Ewan', 'Fergus', 'Finlay', 'Fraser', 'Gavin', 'Gordon', 'Graham', 'Grant',
    'Gregor', 'Hamish', 'Hugh', 'Iain', 'Ian', 'Jamie', 'Kenneth', 'Lachlan',
    'Logan', 'Magnus', 'Malcolm', 'Murray', 'Neil', 'Niall', 'Rory', 'Ross',
    'Scott', 'Stewart', 'Stuart', 'Wallace', 'William', 'Andrew', 'Alan', 'Alexander',
    'Brian', 'Charles', 'Derek', 'Eric', 'Frank', 'George', 'Gerald', 'Gordon',
    'Harry', 'Jack', 'James', 'John', 'Keith', 'Kevin', 'Lewis', 'Mark',
    'Michael', 'Norman', 'Oliver', 'Patrick', 'Paul', 'Peter', 'Philip', 'Richard',
    'Robert', 'Ronald', 'Samuel', 'Stephen', 'Thomas', 'Timothy', 'Walter', 'Wayne'
]

SCOTTISH_FIRST_NAMES_FEMALE = [
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
SCOTTISH_SURNAMES = [
    'Anderson', 'Armstrong', 'Bell', 'Black', 'Brown', 'Campbell', 'Cameron', 'Clark',
    'Crawford', 'Davidson', 'Douglas', 'Duncan', 'Elliott', 'Ferguson', 'Forbes', 'Fraser',
    'Gibson', 'Gordon', 'Graham', 'Grant', 'Gray', 'Hamilton', 'Henderson', 'Hunter',
    'Johnston', 'Kelly', 'Kennedy', 'Kerr', 'MacDonald', 'MacKenzie', 'MacLean', 'MacLeod',
    'Marshall', 'Martin', 'Macdonald', 'Mackenzie', 'Macleod', 'Miller', 'Mitchell', 'Morrison',
    'Munro', 'Murray', 'Paterson', 'Reid', 'Robertson', 'Ross', 'Scott', 'Simpson',
    'Smith', 'Stewart', 'Sutherland', 'Taylor', 'Thomson', 'Walker', 'Wallace', 'Watson',
    'White', 'Wilson', 'Young', 'Allan', 'Baird', 'Bruce', 'Burns', 'Burnett',
    'Carr', 'Christie', 'Cunningham', 'Currie', 'Docherty', 'Drummond', 'Duff', 'Dunn',
    'Fleming', 'Fletcher', 'Forsyth', 'Gillespie', 'Goodwin', 'Greig', 'Hay', 'Hogg',
    'Hughes', 'Inglis', 'Irvine', 'Jackson', 'Johnstone', 'Keith', 'Lamont', 'Lang',
    'Lawson', 'Lindsay', 'Logan', 'MacGregor', 'MacIntosh', 'MacIntyre', 'MacKay', 'MacLaren',
    'MacMillan', 'MacNeil', 'MacPherson', 'MacRae', 'Mair', 'Malcolm', 'Mann', 'Maxwell',
    'McAllister', 'McBride', 'McCabe', 'McCall', 'McCann', 'McCarthy', 'McCormick', 'McCulloch',
    'McDonald', 'McFarlane', 'McGill', 'McGrath', 'McGregor', 'McGuire', 'McIntyre', 'McKay',
    'McKenzie', 'McLean', 'McLeod', 'McMillan', 'McNeil', 'McPherson', 'Menzies', 'Moir',
    'Nicholson', 'Ogilvie', 'Oliver', 'Parker', 'Pollock', 'Rae', 'Ramsay', 'Rennie',
    'Ritchie', 'Russell', 'Semple', 'Shaw', 'Sinclair', 'Sloan', 'Stevenson', 'Stirling',
    'Strachan', 'Struthers', 'Sym', 'Tennant', 'Urquhart', 'Watt', 'Weir', 'Woods'
]

print("🏴 Generating Unique Scottish Names for All Staff")
print("=" * 70)

# Get all active staff
all_staff = list(User.objects.filter(is_active=True).exclude(sap='000745').order_by('sap'))

print(f"\n📊 Total active staff: {len(all_staff)}")

# Check for actual duplicates
from collections import Counter
name_pairs = [(s.first_name, s.last_name) for s in all_staff]
name_counts = Counter(name_pairs)
duplicates = {name: count for name, count in name_counts.items() if count > 1}

print(f"📊 Current duplicate name combinations: {len(duplicates)}")

if duplicates:
    print("\n📋 Current Duplicates:")
    for (first, last), count in sorted(duplicates.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {first} {last}: {count} instances")

# Track used names to ensure uniqueness
used_names = set()

# Combine all names for random selection
all_first_names = SCOTTISH_FIRST_NAMES_MALE + SCOTTISH_FIRST_NAMES_FEMALE
random.shuffle(all_first_names)
random.shuffle(SCOTTISH_SURNAMES)

# Generate unique names for each staff member
print("\n🔄 Generating unique names...")
updates = []
first_name_idx = 0
surname_idx = 0

for staff in all_staff:
    # Strip any home suffix from last name (e.g., "Ahmed (HH)" -> "Ahmed")
    clean_last_name = staff.last_name.split(' (')[0] if ' (' in staff.last_name else staff.last_name
    
    # Check if name has suffix or if cleaned name would be duplicate
    has_suffix = ' (' in staff.last_name
    current_name = (staff.first_name, clean_last_name)
    
    # Need to update if: has suffix OR cleaned name is duplicate OR original name is duplicate
    needs_update = has_suffix or current_name in used_names or (staff.first_name, staff.last_name) in duplicates
    
    if needs_update:
        # Need to generate a new unique name
        attempts = 0
        while attempts < 10000:
            # Get next first name
            first_name = all_first_names[first_name_idx % len(all_first_names)]
            first_name_idx += 1
            
            # Get next surname
            surname = SCOTTISH_SURNAMES[surname_idx % len(SCOTTISH_SURNAMES)]
            surname_idx += 1
            
            new_name = (first_name, surname)
            
            if new_name not in used_names:
                staff.first_name = first_name
                staff.last_name = surname
                used_names.add(new_name)
                updates.append(staff)
                break
            
            attempts += 1
        
        if attempts >= 10000:
            print(f"  ⚠️  Warning: Could not generate unique name for SAP {staff.sap}")
    else:
        # Name is unique and clean
        used_names.add((staff.first_name, staff.last_name))

print(f"\n📝 Updating {len(updates)} staff records...")

# Bulk update using update_fields to bypass full_clean validation
updated_count = 0
for staff in updates:
    try:
        # Use update() to bypass validation
        User.objects.filter(sap=staff.sap).update(
            first_name=staff.first_name,
            last_name=staff.last_name
        )
        updated_count += 1
    except Exception as e:
        print(f"  ⚠️  Error updating SAP {staff.sap}: {e}")

print(f"✅ Updated {updated_count} staff records")

# Verify uniqueness
print("\n" + "=" * 70)
print("📊 VERIFICATION")
print("=" * 70)

final_staff = User.objects.filter(is_active=True).exclude(sap='000745')
final_names = [(s.first_name, s.last_name) for s in final_staff]
final_counts = Counter(final_names)
final_dupes = {name: count for name, count in final_counts.items() if count > 1}

print(f"Total staff: {len(final_staff)}")
print(f"Unique names: {len(set(final_names))}")
print(f"Duplicate names: {len(final_dupes)}")

if final_dupes:
    print("\n⚠️  Remaining duplicates:")
    for (first, last), count in sorted(final_dupes.items(), key=lambda x: x[1], reverse=True):
        print(f"  {first} {last}: {count} instances")
else:
    print("\n✅ All staff now have unique names!")

# Show sample
print("\n📋 Sample of updated staff (first 20):")
for staff in list(final_staff.order_by('sap')[:20]):
    print(f"  SAP {staff.sap}: {staff.first_name} {staff.last_name} - {staff.role.name if staff.role else 'No Role'}")

print("\n" + "=" * 70)
print("✅ COMPLETE")
print("=" * 70)
