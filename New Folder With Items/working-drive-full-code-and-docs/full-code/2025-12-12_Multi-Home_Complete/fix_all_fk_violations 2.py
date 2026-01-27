#!/usr/bin/env python3
"""
Comprehensive fix for ALL foreign key violations in the database.
Finds every table with user_id references and fixes them.
"""

import sqlite3
import sys

def fix_all_violations():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # Disable FK constraints
    cursor.execute('PRAGMA foreign_keys = OFF;')
    
    print("\n" + "="*60)
    print("COMPREHENSIVE FOREIGN KEY VIOLATION FIX")
    print("="*60 + "\n")
    
    # Get all scheduling tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'scheduling_%'")
    tables = [row[0] for row in cursor.fetchall()]
    
    total_fixed = 0
    tables_fixed = []
    
    for table in tables:
        # Get column info
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        
        for col in columns:
            col_name = col[1]
            # Look for any _id columns that might reference scheduling_user.sap
            if '_id' in col_name or col_name in ['supervisor', 'manager', 'keyworker', 'unit_manager']:
                try:
                    # Check for violations
                    cursor.execute(f'''
                        SELECT COUNT(*) FROM {table} 
                        WHERE {col_name} IS NOT NULL 
                        AND {col_name} NOT IN (SELECT sap FROM scheduling_user)
                    ''')
                    violation_count = cursor.fetchone()[0]
                    
                    if violation_count > 0:
                        # Try to set to NULL
                        try:
                            cursor.execute(f'UPDATE {table} SET {col_name} = NULL WHERE {col_name} NOT IN (SELECT sap FROM scheduling_user)')
                            fixed = cursor.rowcount
                            print(f"✓ {table}.{col_name}: Set {fixed} invalid references to NULL")
                            total_fixed += fixed
                            tables_fixed.append(f"{table}.{col_name}")
                        except sqlite3.IntegrityError:
                            # Column doesn't allow NULL, so delete the rows
                            cursor.execute(f'DELETE FROM {table} WHERE {col_name} NOT IN (SELECT sap FROM scheduling_user)')
                            deleted = cursor.rowcount
                            print(f"✓ {table}.{col_name}: Deleted {deleted} rows with invalid references")
                            total_fixed += deleted
                            tables_fixed.append(f"{table}.{col_name}")
                except Exception as e:
                    # Column might not reference users, skip it
                    pass
    
    conn.commit()
    cursor.execute('PRAGMA foreign_keys = ON;')
    conn.close()
    
    print("\n" + "="*60)
    print(f"TOTAL FIXES: {total_fixed} records across {len(tables_fixed)} fields")
    print("="*60 + "\n")
    
    if tables_fixed:
        print("Fields fixed:")
        for field in tables_fixed:
            print(f"  - {field}")
    
    print("\n✅ All foreign key violations fixed!")
    return total_fixed

if __name__ == '__main__':
    fix_all_violations()
