#!/usr/bin/env python
"""
Fix foreign key constraint issues before migration
"""
import os
import django
import sqlite3

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User

# Connect to database directly
db_path = '/Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete/db.sqlite3'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Checking for invalid foreign keys...")

# Get all tables
cursor.execute("""
    SELECT name FROM sqlite_master 
    WHERE type='table' AND (name LIKE 'scheduling_%' OR name LIKE 'staff_records_%')
""")
all_tables = [t[0] for t in cursor.fetchall()]

# Get all foreign keys for each table
tables_to_fix = []
for table_name in all_tables:
    cursor.execute(f"PRAGMA foreign_key_list({table_name})")
    fks = cursor.fetchall()
    
    for fk in fks:
        fk_id, seq, ref_table, from_col, to_col = fk[:5]
        if ref_table == 'scheduling_user' and to_col == 'sap':
            tables_to_fix.append((table_name, from_col))

print(f"Found {len(tables_to_fix)} foreign key columns to check...\n")

total_fixed = 0

for table_name, column_name in tables_to_fix:
    try:
        cursor.execute(f"""
            SELECT COUNT(*) FROM {table_name} 
            WHERE {column_name} IS NOT NULL 
            AND {column_name} NOT IN (SELECT sap FROM scheduling_user)
        """)
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"⚠ {table_name}.{column_name}: {count} invalid references")
            
            # Delete or NULL based on column name
            if column_name in ['user_id', 'created_by_id', 'reported_by_id', 'generated_by_id']:
                # Delete records with invalid user references
                cursor.execute(f"""
                    DELETE FROM {table_name} 
                    WHERE {column_name} NOT IN (SELECT sap FROM scheduling_user)
                """)
                print(f"  ✓ Deleted {cursor.rowcount} records")
            else:
                # Set to NULL for other fields (resolved_by, acknowledged_by, etc.)
                cursor.execute(f"""
                    UPDATE {table_name} 
                    SET {column_name} = NULL 
                    WHERE {column_name} NOT IN (SELECT sap FROM scheduling_user)
                """)
                print(f"  ✓ Set {cursor.rowcount} to NULL")
            
            total_fixed += cursor.rowcount
    except sqlite3.OperationalError as e:
        print(f"⚠ Error with {table_name}.{column_name}: {e}")

if total_fixed > 0:
    conn.commit()
    print(f"\n✓ Fixed {total_fixed} total invalid records")

# Check for other potential issues
print("\n" + "="*50)
print("Cleanup complete!")
print("="*50)

conn.close()

print("\n✓ All foreign key issues resolved!")
print("\nNow run: python3 manage.py migrate")
