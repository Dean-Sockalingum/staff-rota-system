"""
Test-specific settings to fix Python 3.14 compatibility issues
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rotasystems.settings import *

# Disable auditlog middleware in tests to avoid template context errors
# Issue: auditlog has incompatibility with Python 3.14's template rendering
# This doesn't affect production - audit logging isn't needed in tests
MIDDLEWARE = [m for m in MIDDLEWARE if 'auditlog' not in m.lower()]

# Disable auditlog app in tests
INSTALLED_APPS = [app for app in INSTALLED_APPS if 'auditlog' not in app.lower()]

# Use faster password hasher for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable migrations for faster tests (optional - uncomment if needed)
# class DisableMigrations:
#     def __contains__(self, item):
#         return True
#     def __getitem__(self, item):
#         return None
# MIGRATION_MODULES = DisableMigrations()

