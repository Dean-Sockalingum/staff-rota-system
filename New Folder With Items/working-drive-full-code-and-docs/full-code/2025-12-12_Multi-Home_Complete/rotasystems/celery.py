"""
Celery configuration for rotasystems project.

This module configures Celery for automated task scheduling and monitoring.

Author: Dean Sockalingum
Created: 2025-01-18
"""

import os
from celery import Celery

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')

# Create Celery app
app = Celery('rotasystems')

# Load config from Django settings with CELERY_ prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup"""
    print(f'Request: {self.request!r}')
