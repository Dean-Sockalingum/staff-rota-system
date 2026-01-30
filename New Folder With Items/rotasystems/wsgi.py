"""
WSGI config for rotasystems project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from django.conf import settings
import logging
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')

application = get_wsgi_application()

# Emit a startup log with key settings for operational verification
try:
	logger = logging.getLogger('django')
	logger.info(
		"WSGI startup: DEBUG=%s, ALLOWED_HOSTS=%s, CSRF_TRUSTED_ORIGINS=%s, SETTINGS_FILE=%s, CWD=%s, SYS_PATH_HEAD=%s",
		settings.DEBUG,
		settings.ALLOWED_HOSTS,
		settings.CSRF_TRUSTED_ORIGINS,
		getattr(settings, "__file__", "<unknown>"),
		os.getcwd(),
		sys.path[:3],
	)
except Exception as e:
	# Fallback to stdout if logging is not yet fully configured
	print(f"WSGI startup log failed: {e}")
