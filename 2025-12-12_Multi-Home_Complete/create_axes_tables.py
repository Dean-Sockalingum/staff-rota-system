#!/usr/bin/env python3
"""
Create axes tables by temporarily disabling FK constraints
"""
import sqlite3
import sys

def main():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # Disable FK constraints
    cursor.execute("PRAGMA foreign_keys=OFF")
    
    # Delete axes migration records
    cursor.execute("DELETE FROM django_migrations WHERE app = 'axes'")
    conn.commit()
    
    print("Deleted axes migration records")
    print("Now run: python3 -c \"import os; os.environ.setdefault('DISABLE_FK', '1'); import django; django.setup(); from django.core.management import execute_from_command_line; execute_from_command_line(['manage.py', 'migrate', 'axes'])\"")
    
    conn.close()

if __name__ == '__main__':
    main()
