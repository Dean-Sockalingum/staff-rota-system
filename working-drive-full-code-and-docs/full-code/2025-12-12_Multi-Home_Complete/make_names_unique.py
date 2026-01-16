#!/usr/bin/env python3
"""
Make staff names unique by using alternative forenames.
This will eliminate duplicate base names across homes.
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User
from collections import defaultdict
import random

# Alternative Scottish forenames to use for variations
ALTERNATIVE_NAMES = {
    'Ailsa': ['Elsa', 'Alisa', 'Ailish', 'Eliza'],
    'Angus': ['Aonghas', 'Gus', 'Fergus', 'Magnus'],
    'Ava': ['Eva', 'Aoife', 'Evie', 'Aimee'],
    'Beth': ['Betty', 'Bethan', 'Bethany', 'Elisabeth'],
    'Bonnie': ['Bonny', 'Bronwen', 'Brianna', 'Briony'],
    'Bruce': ['Brodie', 'Blair', 'Boyd', 'Brett'],
    'Cameron': ['Cam', 'Callum', 'Calvin', 'Camden'],
    'Catriona': ['Katrina', 'Catrin', 'Cait', 'Katy'],
    'Colin': ['Calum', 'Coll', 'Connor', 'Conall'],
    'Craig': ['Graeme', 'Graham', 'Greg', 'Grant'],
    'Donna': ['Dana', 'Dina', 'Diane', 'Doreen'],
    'Duncan': ['Dougal', 'Douglas', 'Donnie', 'Donald'],
    'Eilidh': ['Aileen', 'Eileen', 'Isla', 'Ellie'],
    'Elspeth': ['Elizabeth', 'Eliza', 'Elsie', 'Effie'],
    'Ewan': ['Euan', 'Owen', 'Evan', 'Ewen'],
    'Fiona': ['Ffion', 'Faye', 'Flora', 'Frances'],
    'Fraser': ['Frazer', 'Finlay', 'Flynn', 'Fergus'],
    'Gordon': ['Gordie', 'Glen', 'Gavin', 'Gilbert'],
    'Gregor': ['Gregory', 'Graeme', 'Grant', 'Gareth'],
    'Hannah': ['Hanna', 'Anna', 'Annie', 'Annabel'],
    'Heather': ['Holly', 'Hazel', 'Hope', 'Harriet'],
    'Iain': ['Ian', 'Euan', 'Ewan', 'Ivan'],
    'Isla': ['Iris', 'Islay', 'Imogen', 'Iona'],
    'Jamie': ['James', 'Hamish', 'Jack', 'Jake'],
    'Kenneth': ['Kenny', 'Kent', 'Keith', 'Kevin'],
    'Kirsty': ['Kirsten', 'Kristin', 'Keira', 'Kira'],
    'Lachlan': ['Lachie', 'Logan', 'Liam', 'Lewis'],
    'Lesley': ['Leslie', 'Leanna', 'Leigh', 'Lorna'],
    'Malcolm': ['Mal', 'Maxwell', 'Marcus', 'Martin'],
    'Morag': ['Morna', 'Maura', 'Maureen', 'Muriel'],
    'Niall': ['Neil', 'Noel', 'Nathan', 'Nico'],
    'Nicola': ['Nicole', 'Nikki', 'Nina', 'Nessa'],
    'Rhona': ['Rona', 'Rowena', 'Roslyn', 'Rachel'],
    'Ross': ['Rory', 'Rowan', 'Robert', 'Robin'],
    'Senga': ['Seonaid', 'Shona', 'Sine', 'Siobhan'],
    'Shona': ['Catriona', 'Fiona', 'Sian', 'Shannon'],
    'Stuart': ['Stewart', 'Steven', 'Stevan', 'Struan'],
    'Una': ['Oona', 'Úna', 'Unity', 'Ursula'],
    'Wallace': ['Wally', 'Walter', 'Warren', 'Wayne'],
}

def get_base_name(user):
    """Extract base name without home suffix."""
    first = user.first_name.replace(' (HH)', '').replace(' (OG)', '').replace(' (MB)', '').replace(' (RS)', '').replace(' (VG)', '')
    last = user.last_name.replace(' (HH)', '').replace(' (OG)', '').replace(' (MB)', '').replace(' (RS)', '').replace(' (VG)', '')
    return first, last

def find_duplicates():
    """Find all staff with duplicate base names."""
    name_map = defaultdict(list)
    
    for user in User.objects.filter(is_active=True).select_related('unit', 'unit__care_home', 'role'):
        first, last = get_base_name(user)
        full_name = f"{first} {last}"
        name_map[full_name].append(user)
    
    # Return only duplicates
    return {name: users for name, users in name_map.items() if len(users) > 1}

def make_names_unique(dry_run=True):
    """
    Make all duplicate names unique by using alternative forenames.
    
    Strategy:
    - For duplicates, keep first instance with original name
    - Use alternative forenames for subsequent instances
    - Remove home suffixes from all names (no longer needed when truly unique)
    """
    duplicates = find_duplicates()
    
    print(f"Found {len(duplicates)} duplicate base names")
    print(f"Affecting {sum(len(users) for users in duplicates.values())} staff members\n")
    
    if dry_run:
        print("=== DRY RUN MODE - No changes will be made ===\n")
    
    total_changed = 0
    used_names = set()  # Track which names we've used globally
    
    for base_name, users in sorted(duplicates.items()):
        print(f"\n{base_name} ({len(users)} instances):")
        
        first_base, last_base = get_base_name(users[0])
        
        # Get alternative names for this forename
        alternatives = ALTERNATIVE_NAMES.get(first_base, [])
        
        for i, user in enumerate(users):
            first, last = get_base_name(user)
            home_code = user.unit.care_home.name if user.unit and user.unit.care_home else 'UNKNOWN'
            
            if i == 0:
                # Keep first instance with original name (remove home suffix only)
                new_first_name = first
                new_last_name = last
            else:
                # Use alternative name for subsequent instances
                if i - 1 < len(alternatives):
                    new_first_name = alternatives[i - 1]
                else:
                    # Fallback: add number suffix if we run out of alternatives
                    new_first_name = f"{first}{i}"
                new_last_name = last
                
                # Check if this combination is already used
                attempt = 0
                while f"{new_first_name} {new_last_name}" in used_names and attempt < 10:
                    attempt += 1
                    new_first_name = f"{first}{i + attempt}"
            
            full_new_name = f"{new_first_name} {new_last_name}"
            used_names.add(full_new_name)
            
            print(f"  SAP {user.sap} ({home_code}):")
            print(f"    Old: {user.first_name} {user.last_name}")
            print(f"    New: {new_first_name} {new_last_name}")
            
            if not dry_run:
                user.first_name = new_first_name
                user.last_name = new_last_name
                user.save()
                total_changed += 1
    
    if not dry_run:
        print(f"\n✓ Updated {total_changed} staff names")
    else:
        print(f"\n✓ Would update {sum(len(users) for users in duplicates.values())} staff names")
        print("\nRun with --yes to apply changes")
    
    return total_changed

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Make duplicate staff names unique')
    parser.add_argument('--yes', action='store_true', help='Apply changes (default is dry-run)')
    args = parser.parse_args()
    
    dry_run = not args.yes
    
    if not dry_run:
        response = input("This will modify staff names. Are you sure? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled.")
            return
    
    make_names_unique(dry_run=dry_run)

if __name__ == '__main__':
    main()
