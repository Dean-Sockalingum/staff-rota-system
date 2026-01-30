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
import importlib

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')

application = get_wsgi_application()

# Emit a startup log with key settings for operational verification
try:
	logger = logging.getLogger('django')
	settings_module = os.environ.get("DJANGO_SETTINGS_MODULE", "<unset>")
	settings_file = "<unknown>"
	try:
		if settings_module and settings_module != "<unset>":
			settings_file = importlib.import_module(settings_module).__file__
	except Exception:
		pass

	logger.info(
		"WSGI startup: DEBUG=%s, ALLOWED_HOSTS=%s, CSRF_TRUSTED_ORIGINS=%s, SETTINGS_MODULE=%s, SETTINGS_FILE=%s, CWD=%s, SYS_PATH_HEAD=%s",
		settings.DEBUG,
		settings.ALLOWED_HOSTS,
		settings.CSRF_TRUSTED_ORIGINS,
		settings_module,
		settings_file,
		os.getcwd(),
		sys.path[:3],
	)
except Exception as e:
	# Fallback to stdout if logging is not yet fully configured
	print(f"WSGI startup log failed: {e}")
