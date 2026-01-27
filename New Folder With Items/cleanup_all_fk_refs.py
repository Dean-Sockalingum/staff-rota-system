#!/usr/bin/env python3
"""
Comprehensive foreign key cleanup script for NHS Staff Rota System
Removes all invalid user references across all tables
"""
import sqlite3
import sys

def cleanup_foreign_keys():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    print("=" * 70)
    print("NHS STAFF ROTA SYSTEM - FOREIGN KEY CLEANUP")
    print("=" * 70)
    
    # Get all valid SAP numbers
    cursor.execute("SELECT sap FROM scheduling_user")
    valid_saps = set(row[0] for row in cursor.fetchall())
    print(f"\nFound {len(valid_saps)} valid SAP numbers in scheduling_user")
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    all_tables = [row[0] for row in cursor.fetchall()]
    
    total_deleted = 0
    tables_cleaned = []
    
    for table in all_tables:
        # Skip Django internal tables
        if table.startswith('django_') or table.startswith('auth_') or table.startswith('sqlite_'):
            continue
        
        # Get table structure
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
        except:
            continue
        
        # Find user-related columns (foreign keys to scheduling_user)
        user_columns = []
        profile_columns = []
        for col in columns:
            col_name = col[1]
            # Check for common user FK patterns
            if any(pattern in col_name for pattern in ['user_id', 'supervisor_id', 'staff_member_id', 
                                                         'unit_manager_id', 'recipient_id', 'author_id',
                                                         'created_by_id', 'updated_by_id', 'staff_id',
                                                         'reported_by_id', 'approved_by_id']):
                user_columns.append(col_name)
            # Check for profile FK patterns
            elif 'profile_id' in col_name:
                profile_columns.append(col_name)
        
        if not user_columns and not profile_columns:
            continue
        
        # Check each user column for invalid references
        for col in user_columns:
            try:
                # Count invalid references
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {table} 
                    WHERE {col} IS NOT NULL 
                    AND {col} NOT IN (SELECT sap FROM scheduling_user)
                """)
                count = cursor.fetchone()[0]
                
                if count > 0:
                    # Get sample of invalid values
                    cursor.execute(f"""
                        SELECT DISTINCT {col} FROM {table} 
                        WHERE {col} IS NOT NULL 
                        AND {col} NOT IN (SELECT sap FROM scheduling_user)
                        LIMIT 5
                    """)
                    invalid_values = [row[0] for row in cursor.fetchall()]
                    
                    print(f"\n  {table}.{col}:")
                    print(f"    - Found {count} invalid references: {', '.join(invalid_values)}")
                    
                    # Delete invalid rows
                    cursor.execute(f"""
                        DELETE FROM {table} 
                        WHERE {col} IS NOT NULL 
                        AND {col} NOT IN (SELECT sap FROM scheduling_user)
                    """)
                    conn.commit()
                    
                    deleted = cursor.rowcount
                    total_deleted += deleted
                    if table not in tables_cleaned:
                        tables_cleaned.append(table)
                    
                    print(f"    - ✓ Deleted {deleted} rows")
                    
            except Exception as e:
                print(f"\n  WARNING: Error processing {table}.{col}: {e}")
                continue
        
        # Check each profile column for invalid references
        for col in profile_columns:
            try:
                # Count invalid references
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {table} 
                    WHERE {col} IS NOT NULL 
                    AND {col} NOT IN (SELECT id FROM staff_records_staffprofile)
                """)
                count = cursor.fetchone()[0]
                
                if count > 0:
                    print(f"\n  {table}.{col}:")
                    print(f"    - Found {count} invalid profile references")
                    
                    # Delete invalid rows
                    cursor.execute(f"""
                        DELETE FROM {table} 
                        WHERE {col} IS NOT NULL 
                        AND {col} NOT IN (SELECT id FROM staff_records_staffprofile)
                    """)
                    conn.commit()
                    
                    deleted = cursor.rowcount
                    total_deleted += deleted
                    if table not in tables_cleaned:
                        tables_cleaned.append(table)
                    
                    print(f"    - ✓ Deleted {deleted} rows")
                    
            except Exception as e:
                print(f"\n  WARNING: Error processing {table}.{col}: {e}")
                continue
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("CLEANUP SUMMARY")
    print("=" * 70)
    print(f"Tables cleaned: {len(tables_cleaned)}")
    print(f"Total rows deleted: {total_deleted}")
    print(f"\nCleaned tables:")
    for table in tables_cleaned:
        print(f"  - {table}")
    print("\n✓ Foreign key cleanup complete")
    print("=" * 70)
    
    return total_deleted > 0

if __name__ == '__main__':
    success = cleanup_foreign_keys()
    sys.exit(0 if success else 1)
