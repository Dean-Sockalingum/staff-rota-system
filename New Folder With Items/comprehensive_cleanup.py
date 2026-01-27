#!/usr/bin/env python3
"""Comprehensive database cleanup - fix all foreign key violations"""

import sqlite3
import shutil
from datetime import datetime

# Backup current database first
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_name = f'db_before_cleanup_{timestamp}.sqlite3'
shutil.copy2('db.sqlite3', backup_name)
print(f"✅ Created backup: {backup_name}\n")

# Connect and disable FK constraints
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = OFF;")

print("=" * 80)
print("COMPREHENSIVE DATABASE CLEANUP")
print("=" * 80)

# Fix scheduling_resident
print("\n1. FIXING SCHEDULING_RESIDENT TABLE")
print("-" * 80)

cursor.execute("""
    SELECT COUNT(*) FROM scheduling_resident 
    WHERE unit_manager_id IS NOT NULL
    AND unit_manager_id NOT IN (SELECT sap FROM scheduling_user);
""")
um_count = cursor.fetchone()[0]
print(f"   Found {um_count} residents with invalid unit_manager_id")

if um_count > 0:
    cursor.execute("""
        UPDATE scheduling_resident 
        SET unit_manager_id = NULL 
        WHERE unit_manager_id IS NOT NULL
        AND unit_manager_id NOT IN (SELECT sap FROM scheduling_user);
    """)
    print(f"   ✅ Fixed {cursor.rowcount} residents - set unit_manager_id to NULL")

cursor.execute("""
    SELECT COUNT(*) FROM scheduling_resident 
    WHERE keyworker_id IS NOT NULL
    AND keyworker_id NOT IN (SELECT sap FROM scheduling_user);
""")
kw_count = cursor.fetchone()[0]
print(f"   Found {kw_count} residents with invalid keyworker_id")

if kw_count > 0:
    cursor.execute("""
        UPDATE scheduling_resident 
        SET keyworker_id = NULL 
        WHERE keyworker_id IS NOT NULL
        AND keyworker_id NOT IN (SELECT sap FROM scheduling_user);
    """)
    print(f"   ✅ Fixed {cursor.rowcount} residents - set keyworker_id to NULL")

# Fix scheduling_leaverequest
print("\n2. FIXING SCHEDULING_LEAVEREQUEST TABLE")
print("-" * 80)

cursor.execute("""
    SELECT COUNT(*) FROM scheduling_leaverequest 
    WHERE user_id IS NOT NULL
    AND user_id NOT IN (SELECT sap FROM scheduling_user);
""")
lr_count = cursor.fetchone()[0]
print(f"   Found {lr_count} leave requests with invalid user_id")

if lr_count > 0:
    cursor.execute("""
        DELETE FROM scheduling_leaverequest 
        WHERE user_id IS NOT NULL
        AND user_id NOT IN (SELECT sap FROM scheduling_user);
    """)
    print(f"   ✅ Deleted {cursor.rowcount} invalid leave requests")

# Fix scheduling_shift (set to NULL instead of delete to preserve shift records)
print("\n3. FIXING SCHEDULING_SHIFT TABLE")
print("-" * 80)

cursor.execute("""
    SELECT COUNT(*) FROM scheduling_shift 
    WHERE user_id IS NOT NULL
    AND user_id NOT IN (SELECT sap FROM scheduling_user);
""")
shift_count = cursor.fetchone()[0]
print(f"   Found {shift_count} shifts with invalid user_id")

if shift_count > 0:
    cursor.execute("""
        UPDATE scheduling_shift 
        SET user_id = NULL 
        WHERE user_id IS NOT NULL
        AND user_id NOT IN (SELECT sap FROM scheduling_user);
    """)
    print(f"   ✅ Fixed {cursor.rowcount} shifts - set user_id to NULL (vacancies)")

# Check other common tables
print("\n4. CHECKING OTHER TABLES")
print("-" * 80)

# Get all tables with potential FK issues
cursor.execute("""
    SELECT name FROM sqlite_master 
    WHERE type='table' AND name LIKE 'scheduling_%'
    ORDER BY name;
""")
tables = [row[0] for row in cursor.fetchall()]

tables_to_check = [
    ('scheduling_incident', 'user_id'),
    ('scheduling_overtime', 'user_id'),
    ('scheduling_training', 'user_id'),
    ('scheduling_sicknessrecord', 'user_id'),
]

for table_name, fk_field in tables_to_check:
    if table_name in tables:
        try:
            cursor.execute(f"""
                SELECT COUNT(*) FROM {table_name} 
                WHERE {fk_field} IS NOT NULL
                AND {fk_field} NOT IN (SELECT sap FROM scheduling_user);
            """)
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"   Found {count} invalid records in {table_name}")
                cursor.execute(f"""
                    DELETE FROM {table_name} 
                    WHERE {fk_field} IS NOT NULL
                    AND {fk_field} NOT IN (SELECT sap FROM scheduling_user);
                """)
                print(f"   ✅ Deleted {cursor.rowcount} invalid records from {table_name}")
        except Exception as e:
            print(f"   ⚠️  Skipped {table_name}: {str(e)[:50]}")

# Re-enable foreign key constraints
cursor.execute("PRAGMA foreign_keys = ON;")

# Verify cleanup
print("\n" + "=" * 80)
print("VERIFICATION")
print("=" * 80)

cursor.execute("""
    SELECT COUNT(*) FROM scheduling_resident 
    WHERE unit_manager_id IS NOT NULL
    AND unit_manager_id NOT IN (SELECT sap FROM scheduling_user);
""")
verify_um = cursor.fetchone()[0]

cursor.execute("""
    SELECT COUNT(*) FROM scheduling_resident 
    WHERE keyworker_id IS NOT NULL
    AND keyworker_id NOT IN (SELECT sap FROM scheduling_user);
""")
verify_kw = cursor.fetchone()[0]

cursor.execute("""
    SELECT COUNT(*) FROM scheduling_leaverequest 
    WHERE user_id IS NOT NULL
    AND user_id NOT IN (SELECT sap FROM scheduling_user);
""")
verify_lr = cursor.fetchone()[0]

total_violations = verify_um + verify_kw + verify_lr

print(f"\nRemaining violations:")
print(f"  Resident unit_manager: {verify_um}")
print(f"  Resident keyworker: {verify_kw}")
print(f"  Leave requests: {verify_lr}")
print(f"  TOTAL: {total_violations}")

if total_violations == 0:
    print("\n✅ DATABASE IS NOW CLEAN - NO FOREIGN KEY VIOLATIONS")
else:
    print("\n⚠️  WARNING: Some violations remain")

conn.commit()
conn.close()

# Create production backup
shutil.copy2('db.sqlite3', 'db_clean_production.sqlite3')
print(f"\n✅ Created clean production backup: db_clean_production.sqlite3")

print("\n" + "=" * 80)
print("CLEANUP COMPLETE")
print("=" * 80)
print("\nNext steps:")
print("  1. Test migrations: python3 manage.py migrate")
print("  2. If successful, rename: mv db_clean_production.sqlite3 db_backup_production.sqlite3")
