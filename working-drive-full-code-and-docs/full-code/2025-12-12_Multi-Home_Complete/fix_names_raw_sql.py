#!/usr/bin/env python3
"""
Replace ALL staff names with unique traditional Scottish names using raw SQL.
"""

import sqlite3
import random

DB_PATH = 'db.sqlite3'

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

print("🏴 Replacing ALL Staff Names with Unique Scottish Names (RAW SQL)")
print("=" * 70)

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get all active staff (excluding admin)
cursor.execute('''
    SELECT sap
    FROM scheduling_user
    WHERE is_active = 1 AND sap != '000745'
    ORDER BY sap
''')

all_staff_saps = [row[0] for row in cursor.fetchall()]
print(f"\n📊 Total staff to update: {len(all_staff_saps)}")

# Generate all possible unique name combinations
all_combinations = []
for first in FIRST_NAMES:
    for surname in SURNAMES:
        all_combinations.append((first, surname))

# Shuffle for randomness
random.shuffle(all_combinations)

print(f"📊 Available unique name combinations: {len(all_combinations)}")

if len(all_combinations) < len(all_staff_saps):
    print(f"⚠️  Warning: Not enough unique combinations!")
else:
    print(f"✅ Sufficient unique names available")

# Assign names
print("\n🔄 Updating names...")
updated = 0

for i, sap in enumerate(all_staff_saps):
    if i < len(all_combinations):
        first_name, surname = all_combinations[i]
        
        cursor.execute('''
            UPDATE scheduling_user
            SET first_name = ?, last_name = ?
            WHERE sap = ?
        ''', (first_name, surname, sap))
        
        updated += 1
        if updated % 100 == 0:
            print(f"  Updated {updated}/{len(all_staff_saps)}...")

# Commit changes
conn.commit()

print(f"\n✅ Updated: {updated} staff records")

# Verify
print("\n" + "=" * 70)
print("📊 VERIFICATION")
print("=" * 70)

cursor.execute('''
    SELECT first_name, last_name, COUNT(*) as count
    FROM scheduling_user
    WHERE is_active = 1 AND sap != '000745'
    GROUP BY first_name, last_name
    HAVING count > 1
''')

duplicates = cursor.fetchall()
print(f"Duplicates found: {len(duplicates)}")

if duplicates:
    print("\n⚠️  Duplicate names:")
    for first, last, count in duplicates[:10]:
        print(f"  {first} {last}: {count} times")
else:
    print("\n✅ All staff have unique names!")

# Show samples
print("\n📋 Sample staff (first 15):")
cursor.execute('''
    SELECT sap, first_name, last_name
    FROM scheduling_user
    WHERE is_active = 1 AND sap != '000745'
    ORDER BY sap
    LIMIT 15
''')

for sap, first, last in cursor.fetchall():
    print(f"  SAP {sap}: {first} {last}")

print("\n📋 Previously duplicated staff (from screenshot):")
for sap in ['000953', '001013', '001073', '000773', '000833', '000893', '001133', '001193']:
    cursor.execute('''
        SELECT first_name, last_name
        FROM scheduling_user
        WHERE sap = ?
    ''', (sap,))
    
    row = cursor.fetchone()
    if row:
        print(f"  SAP {sap}: {row[0]} {row[1]}")
    else:
        print(f"  SAP {sap}: NOT FOUND")

conn.close()

print("\n" + "=" * 70)
print("✅ COMPLETE")
print("=" * 70)
