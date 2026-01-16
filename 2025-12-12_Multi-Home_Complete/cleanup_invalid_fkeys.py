#!/usr/bin/env python3
"""
Clean up all invalid foreign key references in the database before running migrations.
"""
import sqlite3
import sys

DB_PATH = 'db.sqlite3'

# Tables and their user foreign key columns
FK_CHECKS = [
    ('scheduling_systemaccesslog', 'user_id'),
    ('scheduling_activitylog', 'user_id'),
    ('scheduling_complianceviolation', 'affected_user_id'),
    ('scheduling_supervisionrecord', 'supervisor_id'),
    ('scheduling_incidentreport', 'reported_by_id'),
    ('scheduling_leaverequest', 'user_id'),
    ('scheduling_staffingreallocation', 'assigned_user_id'),
    ('scheduling_shiftswaprequest', 'requesting_user_id'),
    ('scheduling_shiftswaprequest', 'target_user_id'),
    ('scheduling_staffingalertresponse', 'user_id'),
    ('scheduling_postshiftadministration_ot_staff', 'user_id'),
    ('scheduling_datachangelog', 'user_id'),
]

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    total_deleted = 0
    
    for table, fk_column in FK_CHECKS:
        # Check if table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if not cursor.fetchone():
            print(f"⚠️  Table {table} does not exist, skipping")
            continue
        
        # Check if column exists
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        if fk_column not in columns:
            print(f"⚠️  Column {fk_column} does not exist in {table}, skipping")
            continue
        
        # Find and delete invalid references
        query = f"""
            DELETE FROM {table} 
            WHERE {fk_column} NOT IN (SELECT sap FROM scheduling_user) 
            AND {fk_column} IS NOT NULL
        """
        
        cursor.execute(query)
        deleted = cursor.rowcount
        
        if deleted > 0:
            print(f"✅ Deleted {deleted} invalid records from {table}.{fk_column}")
            total_deleted += deleted
        else:
            print(f"✓  No invalid records in {table}.{fk_column}")
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"Total records deleted: {total_deleted}")
    print(f"{'='*60}")
    print("\nYou can now run: python3 manage.py migrate")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
