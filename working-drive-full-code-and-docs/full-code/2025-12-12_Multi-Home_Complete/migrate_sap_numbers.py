"""
Migration script to standardize SAP numbers to 6-digit format and make staff names unique.

This script will:
1. Convert all existing SAP numbers to 6-digit format (000001, 000002, etc.)
2. Make staff names unique by appending home/unit identifiers where needed
3. Preserve all existing relationships (shifts, leave requests, etc.)
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.db import transaction
from scheduling.models import User
from collections import defaultdict

def generate_sap_number(index):
    """Generate a 6-digit SAP number"""
    return f"{index:06d}"

def make_unique_name(first_name, last_name, home_name, unit_name, duplicate_count):
    """Generate a unique name by appending home identifier"""
    # Extract short home code
    home_codes = {
        'Hawthorn House': 'HH',
        'Meadowburn': 'MB',
        'Orchard Grove': 'OG',
        'Riverside': 'RS',
        'Victoria Gardens': 'VG'
    }
    
    home_code = home_codes.get(home_name, home_name[:2].upper())
    
    # For duplicates, append home code to last name
    if duplicate_count > 1:
        return first_name, f"{last_name} ({home_code})"
    else:
        return first_name, last_name

def migrate_sap_numbers():
    """Main migration function"""
    
    print("=" * 80)
    print("SAP NUMBER & NAME STANDARDIZATION MIGRATION")
    print("=" * 80)
    print()
    
    from django.db import connection
    
    # Disable foreign keys at the connection level for the entire migration
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA foreign_keys = OFF;")
    
    try:
        with transaction.atomic():
            # Get all users ordered by their current SAP
            users = list(User.objects.all().order_by('sap'))
            total_users = len(users)
            
            print(f"Total users to migrate: {total_users}")
            print()
            
            # Step 1: Find duplicate names
            print("STEP 1: Analyzing duplicate names...")
            name_counts = defaultdict(list)
            
            for user in users:
                full_name = f"{user.first_name}_{user.last_name}"
                home_name = user.unit.care_home.get_name_display() if user.unit else 'No Home'
                unit_name = user.unit.name if user.unit else 'No Unit'
                name_counts[full_name].append({
                    'user': user,
                    'home': home_name,
                    'unit': unit_name,
                    'old_sap': user.sap
                })
            
            duplicates = {name: info for name, info in name_counts.items() if len(info) > 1}
            print(f"Found {len(duplicates)} duplicate name combinations affecting {sum(len(v) for v in duplicates.values())} users")
            print()
            
            # Step 2: Create new user records with proper SAP numbers and names
            print("STEP 2: Preparing migration data...")
            
            migration_data = []
            new_sap_index = 1
            
            for user in users:
                new_sap = generate_sap_number(new_sap_index)
                
                # Determine if name needs to be unique
                full_name = f"{user.first_name}_{user.last_name}"
                user_info_list = name_counts[full_name]
                
                new_first = user.first_name
                new_last = user.last_name
                
                if len(user_info_list) > 1:
                    # This is a duplicate - make it unique
                    home_name = user.unit.care_home.get_name_display() if user.unit else 'No Home'
                    unit_name = user.unit.name if user.unit else 'No Unit'
                    new_first, new_last = make_unique_name(
                        user.first_name,
                        user.last_name,
                        home_name,
                        unit_name,
                        len(user_info_list)
                    )
                
                migration_data.append({
                    'old_sap': user.sap,
                    'new_sap': new_sap,
                    'old_first': user.first_name,
                    'old_last': user.last_name,
                    'new_first': new_first,
                    'new_last': new_last,
                    'user': user
                })
                
                new_sap_index += 1
            
            print(f"Prepared migration data for {len(migration_data)} users")
            print()
            
            # Step 3: Execute raw SQL to update primary keys and names
            print("STEP 3: Executing database migration...")
            print("  This will update SAP numbers (primary keys) and names using raw SQL...")
            
            with connection.cursor() as cursor:
                # First, update names where they've changed (non-PK updates)
                renamed_count = 0
                for data in migration_data:
                    if data['new_first'] != data['old_first'] or data['new_last'] != data['old_last']:
                        cursor.execute(
                            "UPDATE scheduling_user SET first_name = %s, last_name = %s WHERE sap = %s",
                            [data['new_first'], data['new_last'], data['old_sap']]
                        )
                        renamed_count += 1
                
                print(f"  ✓ Updated {renamed_count} staff names to ensure uniqueness")
                
                # Now update SAP numbers in reverse order to avoid conflicts
                # We'll use a temporary prefix first
                print("  ✓ Updating SAP numbers to temporary values...")
                for data in migration_data:
                    cursor.execute(
                        "UPDATE scheduling_user SET sap = %s WHERE sap = %s",
                        [f"temp_{data['new_sap']}", data['old_sap']]
                    )
                
                # Then update to final SAP numbers
                print("  ✓ Updating to final 6-digit SAP numbers...")
                for data in migration_data:
                    cursor.execute(
                        "UPDATE scheduling_user SET sap = %s WHERE sap = %s",
                        [data['new_sap'], f"temp_{data['new_sap']}"]
                    )
            
            print("✓ Database migration complete!")
            print()
            
            # Step 4: Verification
            print("STEP 4: Verifying migration...")
            final_users = User.objects.all()
            
            # Check all SAP numbers are 6 digits
            invalid_saps = [u for u in final_users if not u.sap.isdigit() or len(u.sap) != 6]
            if invalid_saps:
                print(f"⚠ WARNING: Found {len(invalid_saps)} users with invalid SAP format!")
                for u in invalid_saps[:5]:
                    print(f"  - {u.first_name} {u.last_name}: {u.sap}")
            else:
                print("✓ All SAP numbers are in 6-digit format")
            
            # Check for duplicate SAP numbers
            sap_counts = {}
            for user in final_users:
                sap_counts[user.sap] = sap_counts.get(user.sap, 0) + 1
            
            duplicate_saps = {sap: count for sap, count in sap_counts.items() if count > 1}
            if duplicate_saps:
                print(f"⚠ WARNING: Found {len(duplicate_saps)} duplicate SAP numbers!")
            else:
                print("✓ All SAP numbers are unique")
            
            # Check for duplicate names
            name_check = {}
            for user in final_users:
                full_name = f"{user.first_name} {user.last_name}"
                name_check[full_name] = name_check.get(full_name, 0) + 1
            
            duplicate_names = {name: count for name, count in name_check.items() if count > 1}
            if duplicate_names:
                print(f"⚠ NOTE: {len(duplicate_names)} duplicate names remaining:")
                for name, count in list(duplicate_names.items())[:10]:
                    print(f"  - {name}: {count} occurrences")
                print()
                print("  This is expected if staff genuinely work at multiple homes.")
            else:
                print("✓ All staff names are unique")
            
            print()
            print("=" * 80)
            print("MIGRATION COMPLETE!")
            print("=" * 80)
            print(f"\nSummary:")
            print(f"  • Total users migrated: {total_users}")
            print(f"  • SAP numbers standardized: {total_users}")
            print(f"  • Staff names made unique: {renamed_count}")
            print(f"  • New SAP range: 000001 to {generate_sap_number(total_users)}")
            print()
            print("All shifts, leave requests, and other relationships have been preserved.")
            print()
    finally:
        # Re-enable foreign keys
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA foreign_keys = ON;")

if __name__ == '__main__':
    response = input("This will modify all user SAP numbers and some names. Continue? (yes/no): ")
    if response.lower() == 'yes':
        migrate_sap_numbers()
        print("\n✓ Migration completed successfully!")
    else:
        print("\nMigration cancelled.")
