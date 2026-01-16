#!/usr/bin/env python
"""
Quick script to apply pending migrations
Run this when terminal is unresponsive
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.core.management import call_command

print("Applying migrations...")
try:
    call_command('migrate', verbosity=2)
    print("\n✓ Migrations applied successfully!")
    print("\nYou can now restart the server.")
except Exception as e:
    print(f"\n✗ Error applying migrations: {e}")
    sys.exit(1)
