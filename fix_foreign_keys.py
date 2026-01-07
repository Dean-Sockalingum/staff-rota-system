import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.db import connection

# Get all valid SAP numbers
with connection.cursor() as cursor:
    cursor.execute("SELECT sap FROM scheduling_user")
    valid_saps = {row[0] for row in cursor.fetchall()}
    
    # Find tables with user foreign keys
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'scheduling_%'")
    tables = [row[0] for row in cursor.fetchall()]
    
    fixed = 0
    for table in tables:
        try:
            # Get table info
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            
            # Find user_id or similar columns
            user_cols = [col[1] for col in columns if 'user_id' in col[1] or col[1] in ['supervisor_id', 'staff_member_id', 'reported_by_id', 'created_by_id']]
            
            for col in user_cols:
                # Delete invalid rows
                cursor.execute(f"DELETE FROM {table} WHERE {col} NOT IN (SELECT sap FROM scheduling_user) AND {col} IS NOT NULL")
                if cursor.rowcount > 0:
                    print(f"Deleted {cursor.rowcount} invalid rows from {table}.{col}")
                    fixed += cursor.rowcount
        except Exception as e:
            print(f"Error processing {table}: {e}")
    
    print(f"\nTotal rows fixed: {fixed}")
