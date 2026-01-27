#!/usr/bin/env python3
"""
Clear all shifts in batches to avoid SQLite variable limit
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ['DJANGO_SETTINGS_MODULE'] = 'rotasystems.settings'
django.setup()

from scheduling.models import Shift

print(f'Deleting {Shift.objects.all().count()} shifts in batches...')
batch_size = 1000
total = Shift.objects.count()
deleted = 0

while Shift.objects.exists():
    ids = list(Shift.objects.values_list('id', flat=True)[:batch_size])
    Shift.objects.filter(id__in=ids).delete()
    deleted += len(ids)
    remaining = Shift.objects.count()
    print(f'  Deleted {deleted}/{total} ({remaining} remaining)...')

print('✓ All shifts deleted')
