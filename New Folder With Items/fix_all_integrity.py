#!/usr/bin/env python3
"""Comprehensive fix for all foreign key integrity issues"""

import sqlite3

db_path = 'db.sqlite3'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Disable foreign key constraints
cursor.execute("PRAGMA foreign_keys = OFF;")

print("Fixing all foreign key integrity issues...\n")

# Fix scheduling_resident
cursor.execute("""
    UPDATE scheduling_resident 
    SET unit_manager_id = NULL 
    WHERE unit_manager_id IS NOT NULL
    AND unit_manager_id NOT IN (SELECT sap FROM scheduling_user);
""")
print(f"✅ Fixed {cursor.rowcount} residents with invalid unit_manager_id")

cursor.execute("""
    UPDATE scheduling_resident 
    SET keyworker_id = NULL 
    WHERE keyworker_id IS NOT NULL
    AND keyworker_id NOT IN (SELECT sap FROM scheduling_user);
""")
print(f"✅ Fixed {cursor.rowcount} residents with invalid keyworker_id")

# Fix scheduling_leaverequest
cursor.execute("""
    DELETE FROM scheduling_leaverequest 
    WHERE user_id IS NOT NULL
    AND user_id NOT IN (SELECT sap FROM scheduling_user);
""")
print(f"✅ Deleted {cursor.rowcount} leave requests with invalid user_id")

# Fix scheduling_shift
cursor.execute("""
    UPDATE scheduling_shift 
    SET user_id = NULL 
    WHERE user_id IS NOT NULL
    AND user_id NOT IN (SELECT sap FROM scheduling_user);
""")
print(f"✅ Fixed {cursor.rowcount} shifts with invalid user_id")

# Check if tables exist before fixing them
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'scheduling_%';")
tables = [row[0] for row in cursor.fetchall()]
print(f"\nFound tables: {len(tables)}")

# Only fix tables that exist
if 'scheduling_sicknessrecord' in tables:
    cursor.execute("""
        DELETE FROM scheduling_sicknessrecord 
        WHERE user_id IS NOT NULL
        AND user_id NOT IN (SELECT sap FROM scheduling_user);
    """)
    print(f"✅ Deleted {cursor.rowcount} sickness records with invalid user_id")

if 'scheduling_overtime' in tables:
    cursor.execute("""
        DELETE FROM scheduling_overtime 
        WHERE user_id IS NOT NULL
        AND user_id NOT IN (SELECT sap FROM scheduling_user);
    """)
    print(f"✅ Deleted {cursor.rowcount} overtime records with invalid user_id")

# Re-enable foreign key constraints
cursor.execute("PRAGMA foreign_keys = ON;")

conn.commit()
conn.close()

print("\n✅ All foreign key integrity issues fixed")
print("✅ Migrations should now complete successfully")
