#!/usr/bin/env python3
"""Fix resident integrity issues by temporarily disabling foreign key constraints"""

import os
import django
import sqlite3

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

# Direct SQLite connection to bypass Django's FK checks
db_path = 'db.sqlite3'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Disable foreign key constraints
cursor.execute("PRAGMA foreign_keys = OFF;")

# Fix all invalid foreign keys in scheduling_resident
print("Checking for invalid foreign keys...")

# Fix unit_manager_id
cursor.execute("""
    UPDATE scheduling_resident 
    SET unit_manager_id = NULL 
    WHERE unit_manager_id IS NOT NULL
    AND unit_manager_id NOT IN (SELECT sap FROM scheduling_user);
""")
unit_fixed = cursor.rowcount
print(f"✅ Fixed {unit_fixed} residents with invalid unit_manager_id")

# Fix keyworker_id
cursor.execute("""
    UPDATE scheduling_resident 
    SET keyworker_id = NULL 
    WHERE keyworker_id IS NOT NULL
    AND keyworker_id NOT IN (SELECT sap FROM scheduling_user);
""")
key_fixed = cursor.rowcount
print(f"✅ Fixed {key_fixed} residents with invalid keyworker_id")

# Re-enable foreign key constraints
cursor.execute("PRAGMA foreign_keys = ON;")

conn.commit()
conn.close()

print("✅ Database integrity fixed - migrations should now work")
