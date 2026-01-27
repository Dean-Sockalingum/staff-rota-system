#!/usr/bin/env python
"""
Apply migrations with foreign key checks disabled
"""
import os
import django
import sqlite3

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

print("Temporarily disabling foreign key checks...")

# Disable foreign key checks
with connection.cursor() as cursor:
    cursor.execute("PRAGMA foreign_keys=OFF;")

print("Applying migrations...")
try:
    call_command('migrate', verbosity=2)
    print("\n✓ Migrations applied successfully!")
except Exception as e:
    print(f"\n✗ Error: {e}")
    raise
finally:
    # Re-enable foreign key checks
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA foreign_keys=ON;")
    print("\n✓ Foreign key checks re-enabled")

print("\n✓ All done! You can now start the server.")
