#!/usr/bin/env python3
"""
Sync database schema with Django models by checking for missing columns.
This reads the User model and ensures all fields exist in the database.
"""
import django
import os
import sys
import sqlite3

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User
from django.db import connection

DB_PATH = 'db.sqlite3'

def get_model_fields(model):
    """Get all field names from a Django model."""
    return {field.name: field for field in model._meta.get_fields() 
            if hasattr(field, 'column')}

def get_db_columns(table_name):
    """Get all column names from a database table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = {row[1]: row for row in cursor.fetchall()}
    conn.close()
    return columns

def get_field_sql_type(field):
    """Get the SQL type for a Django field."""
    from django.db.models import (
        CharField, TextField, IntegerField, BooleanField,
        DateField, DateTimeField, DecimalField, ForeignKey
    )
    
    if isinstance(field, BooleanField):
        return 'INTEGER'
    elif isinstance(field, (IntegerField,)):
        return 'INTEGER'
    elif isinstance(field, CharField):
        return f'VARCHAR({field.max_length})'
    elif isinstance(field, TextField):
        return 'TEXT'
    elif isinstance(field, DateField):
        return 'DATE'
    elif isinstance(field, DateTimeField):
        return 'TEXT'  # SQLite stores as TEXT
    elif isinstance(field, DecimalField):
        return 'DECIMAL'
    elif isinstance(field, ForeignKey):
        # Get the target field type
        target_field = field.target_field
        if hasattr(target_field, 'max_length'):
            return f'VARCHAR({target_field.max_length})'
        return 'INTEGER'
    else:
        return 'TEXT'

def get_field_default(field):
    """Get the default value for a field."""
    if field.default is not None and field.default != '':
        if isinstance(field.default, bool):
            return 1 if field.default else 0
        elif isinstance(field.default, (int, float)):
            return field.default
        elif isinstance(field.default, str):
            return f"'{field.default}'"
    
    if field.null:
        return 'NULL'
    
    # Sensible defaults by type
    from django.db.models import BooleanField, IntegerField
    if isinstance(field, BooleanField):
        return 0
    elif isinstance(field, IntegerField):
        return 0
    
    return 'NULL'

def main():
    print("="*70)
    print("DATABASE SCHEMA SYNC CHECK")
    print("="*70)
    
    # Get User model fields
    model_fields = get_model_fields(User)
    print(f"\n✓ Found {len(model_fields)} fields in User model")
    
    # Get database columns
    db_columns = get_db_columns('scheduling_user')
    print(f"✓ Found {len(db_columns)} columns in scheduling_user table")
    
    # Find missing columns
    missing_columns = []
    for field_name, field in model_fields.items():
        if hasattr(field, 'column') and field.column not in db_columns:
            missing_columns.append((field_name, field))
    
    if not missing_columns:
        print("\n✅ All model fields exist in database!")
        return 0
    
    print(f"\n⚠️  Found {len(missing_columns)} missing columns:")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for field_name, field in missing_columns:
        column_name = field.column
        sql_type = get_field_sql_type(field)
        default_value = get_field_default(field)
        
        sql = f"ALTER TABLE scheduling_user ADD COLUMN {column_name} {sql_type}"
        
        # Add default if not NULL
        if default_value != 'NULL':
            sql += f" DEFAULT {default_value}"
        
        print(f"\n  Adding: {column_name} ({sql_type})")
        print(f"  SQL: {sql}")
        
        try:
            cursor.execute(sql)
            print(f"  ✅ Added successfully")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*70)
    print("SCHEMA SYNC COMPLETE")
    print("="*70)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
