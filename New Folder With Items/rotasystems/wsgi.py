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

# Defensive: ensure required hosts/origins are present in environment before settings load
required_hosts = [
	'therota.co.uk',
	'www.therota.co.uk',
	'demo.therota.co.uk',
	'localhost',
	'127.0.0.1',
	'192.168.1.125',
]
hosts_env = os.environ.get('ALLOWED_HOSTS', '')
if hosts_env:
	current = {h.strip() for h in hosts_env.split(',') if h.strip()}
	merged = current.union(required_hosts)
	os.environ['ALLOWED_HOSTS'] = ','.join(sorted(merged))
else:
	os.environ['ALLOWED_HOSTS'] = ','.join(required_hosts)

required_csrf = [
	'https://therota.co.uk',
	'https://www.therota.co.uk',
	'https://demo.therota.co.uk',
]
csrf_env = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
if csrf_env:
	current = {o.strip() for o in csrf_env.split(',') if o.strip()}
	merged = current.union(required_csrf)
	os.environ['CSRF_TRUSTED_ORIGINS'] = ','.join(sorted(merged))
else:
	os.environ['CSRF_TRUSTED_ORIGINS'] = ','.join(required_csrf)

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
