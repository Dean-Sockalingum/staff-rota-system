"""
Rotasystems package initialization.

This module loads Celery when Django starts.
"""

# Load Celery app
from .celery import app as celery_app

__all__ = ('celery_app',)
