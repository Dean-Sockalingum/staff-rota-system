"""
Context processors for adding global template variables.
"""

from django.conf import settings
from django.utils import timezone
from pathlib import Path


def system_mode(request):
    """
    Add system mode (DEMO/PRODUCTION) to all template contexts.
    This allows templates to display the current mode.
    """
    mode_file = settings.BASE_DIR / '.current_mode'
    
    if mode_file.exists():
        mode = mode_file.read_text().strip()
    else:
        mode = 'UNKNOWN'
    
    # Add timestamp for cache busting
    timestamp = int(timezone.now().timestamp())
    
    return {
        'SYSTEM_MODE': mode,
        'IS_DEMO_MODE': mode == 'DEMO',
        'IS_PRODUCTION_MODE': mode == 'PRODUCTION',
        'timestamp': timestamp,
    }
