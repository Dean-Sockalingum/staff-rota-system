#!/usr/bin/env python3
"""Check each database for foreign key violations"""

import sqlite3
import os

databases = [
    'db_backup_before_migration_fix.sqlite3',  # Dec 23 00:09
    'db_production_phase5.sqlite3',             # Dec 21 10:13
    'db_backup_production.sqlite3',             # Dec 21 10:12
    'db_backup_pre_migration.sqlite3',          # Dec 21 10:11
]

def check_fk_violations(db_path):
    """Check a database for foreign key violations"""
    if not os.path.exists(db_path):
        return None
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    violations = {}
    
    # Check scheduling_resident
    cursor.execute("""
        SELECT COUNT(*) FROM scheduling_resident 
        WHERE unit_manager_id IS NOT NULL
        AND unit_manager_id NOT IN (SELECT sap FROM scheduling_user);
    """)
    violations['resident_unit_manager'] = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM scheduling_resident 
        WHERE keyworker_id IS NOT NULL
        AND keyworker_id NOT IN (SELECT sap FROM scheduling_user);
    """)
    violations['resident_keyworker'] = cursor.fetchone()[0]
    
    # Check scheduling_leaverequest
    cursor.execute("""
        SELECT COUNT(*) FROM scheduling_leaverequest 
        WHERE user_id IS NOT NULL
        AND user_id NOT IN (SELECT sap FROM scheduling_user);
    """)
    violations['leaverequest_user'] = cursor.fetchone()[0]
    
    conn.close()
    
    return violations

print("Checking databases for foreign key violations...\n")
print(f"{'Database':<45} {'Resident UM':<12} {'Resident KW':<12} {'Leave Req':<10} {'Total':<10}")
print("=" * 95)

for db in databases:
    violations = check_fk_violations(db)
    if violations:
        total = sum(violations.values())
        status = "✅ CLEAN" if total == 0 else "❌ VIOLATIONS"
        print(f"{db:<45} {violations['resident_unit_manager']:<12} {violations['resident_keyworker']:<12} {violations['leaverequest_user']:<10} {total:<10} {status}")
    else:
        print(f"{db:<45} NOT FOUND")

print("\n" + "=" * 95)
print("\nLegend:")
print("  Resident UM = Invalid unit_manager_id references")
print("  Resident KW = Invalid keyworker_id references")
print("  Leave Req   = Invalid leave request user_id references")
