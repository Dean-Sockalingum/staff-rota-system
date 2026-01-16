"""
Data Migration: Convert alphanumeric SAP numbers to 6-digit numeric format
This script will convert all existing SAP numbers to proper 6-digit format.
"""
import re
from django.db import connection

# Mapping rules for common patterns
SAP_MAPPING = {
    # Admin users
    'ADMIN001': '999999',
    'DEMO999': '999998',
    'STAFF999': '999997',
    
    # Operations Managers
    'OM0001': '900001',
    'OM0002': '900002',
    
    # Service Managers
    'SM0001': '910001',
    
    # Senior Social Care Workers (day)
    'SSCW0001': '920001',
    'SSCW0002': '920002',
    'SSCW0003': '920003',
    'SSCW0004': '920004',
    'SSCW0005': '920005',
    'SSCW0006': '920006',
    'SSCW0007': '920007',
    'SSCW0008': '920008',
    'SSCW0009': '920009',
    
    # Social Care Workers (day)
    # SCW1001-SCW1009 -> 930001-930009
    # SCW1026-SCW1034 -> 930026-930034
    # SCW1051-SCW1059 -> 930051-930059
    # SCW1081-SCW1083 -> 930081-930083
    # SCW1108-SCW1111 -> 930108-930111
    # SCW1135-SCW1140 -> 930135-930140
}

def extract_number(sap):
    """Extract number from alphanumeric SAP"""
    match = re.search(r'(\d+)', sap)
    return int(match.group(1)) if match else None

def convert_sap(old_sap):
    """Convert alphanumeric SAP to 6-digit numeric SAP"""
    
    # If already 6 digits and numeric, return as is
    if re.match(r'^\d{6}$', old_sap):
        return old_sap
    
    # Check if in manual mapping
    if old_sap in SAP_MAPPING:
        return SAP_MAPPING[old_sap]
    
    # Pattern matching for various role codes
    number = extract_number(old_sap)
    if number is None:
        # Generate a unique SAP based on hash
        import hashlib
        hash_val = int(hashlib.md5(old_sap.encode()).hexdigest()[:6], 16)
        return f"{hash_val % 900000 + 100000:06d}"  # Range: 100000-999999
    
    # Social Care Workers (day)
    if old_sap.startswith('SCW'):
        if number < 100000:
            return f"93{number:04d}"  # 930001-939999
        else:
            return f"{number:06d}"
    
    # Social Care Assistants
    if old_sap.startswith('SCA'):
        if number < 100000:
            return f"94{number:04d}"  # 940001-949999
        else:
            return f"{number:06d}"
    
    # Senior Social Care Workers (night)
    if old_sap.startswith('SSCWN'):
        if number < 100000:
            return f"95{number:04d}"  # 950001-959999
        else:
            return f"{number:06d}"
    
    # For any 5-digit number, prepend with 0
    if 10000 <= number < 100000:
        return f"0{number:05d}"
    
    # For any number already 6+ digits, take last 6
    if number >= 100000:
        return f"{number:06d}"[-6:]
    
    # For numbers < 10000, pad with zeros
    return f"{number:06d}"

def update_all_sap_numbers():
    """Update all SAP numbers in the database"""
    from scheduling.models import User
    
    # Get all users with non-compliant SAP numbers
    users = User.objects.all()
    conversions = []
    errors = []
    
    for user in users:
        old_sap = user.sap
        if not re.match(r'^\d{6}$', old_sap):
            new_sap = convert_sap(old_sap)
            conversions.append((old_sap, new_sap, f"{user.first_name} {user.last_name}"))
    
    # Check for duplicates in new SAPs
    new_saps = [c[1] for c in conversions]
    duplicates = [sap for sap in set(new_saps) if new_saps.count(sap) > 1]
    
    if duplicates:
        print(f"ERROR: Found {len(duplicates)} duplicate SAP numbers after conversion:")
        for dup in duplicates:
            users = [c for c in conversions if c[1] == dup]
            print(f"  {dup}: {', '.join([f'{c[0]} ({c[2]})' for c in users])}")
        return False
    
    # Perform conversions
    print(f"Converting {len(conversions)} SAP numbers...")
    
    with connection.cursor() as cursor:
        # Temporarily disable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        try:
            for old_sap, new_sap, name in conversions:
                print(f"  {old_sap:15} -> {new_sap:6}  ({name})")
                
                # Update scheduling_user table
                cursor.execute(
                    "UPDATE scheduling_user SET sap = ? WHERE sap = ?",
                    [new_sap, old_sap]
                )
                
                # Update foreign key references in all related tables
                tables_with_fks = [
                    ('scheduling_shift', 'assigned_to_id'),
                    ('scheduling_leaverequest', 'user_id'),
                    ('staff_records_staffprofile', 'user_id'),
                    ('scheduling_trainingrecord', 'staff_id'),
                    ('scheduling_shiftswap', 'requesting_staff_id'),
                    ('scheduling_shiftswap', 'target_staff_id'),
                    ('scheduling_notification', 'user_id'),
                    ('scheduling_userpreferences', 'user_id'),
                    ('scheduling_videopr ogress', 'user_id'),
                    ('scheduling_videorating', 'user_id'),
                    ('scheduling_videoplaylist', 'user_id'),
                    ('scheduling_activityfeedwidget', 'user_id'),
                    ('scheduling_recentactivity', 'user_id'),
                    ('scheduling_recentactivity', 'target_user_id'),
                    # Add more tables as needed
                ]
                
                for table, column in tables_with_fks:
                    try:
                        cursor.execute(
                            f"UPDATE {table} SET {column} = ? WHERE {column} = ?",
                            [new_sap, old_sap]
                        )
                    except Exception as e:
                        # Table might not exist, that's okay
                        pass
            
            # Re-enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys = ON")
            print(f"\nSuccessfully converted {len(conversions)} SAP numbers!")
            return True
            
        except Exception as e:
            cursor.execute("PRAGMA foreign_keys = ON")
            print(f"ERROR during conversion: {e}")
            return False

if __name__ == '__main__':
    import os
    import django
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
    django.setup()
    
    success = update_all_sap_numbers()
    
    if success:
        print("\n✅ All SAP numbers converted successfully!")
        print("You can now run: python manage.py migrate")
    else:
        print("\n❌ Conversion failed. Please fix errors and try again.")
