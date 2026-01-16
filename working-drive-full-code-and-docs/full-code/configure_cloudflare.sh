#!/bin/bash
# Update Django settings for Cloudflare

ssh root@159.65.18.80 << 'ENDSSH'
cd /home/staff-rota-system

# Backup settings
cp rotasystems/settings.py rotasystems/settings.py.backup_cloudflare

# Add Cloudflare configuration
cat >> rotasystems/settings.py << 'EOF'

# Cloudflare Configuration
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Security headers for Cloudflare
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
EOF

echo "✅ Cloudflare configuration added to settings.py"

# Restart gunicorn
pkill gunicorn
/home/staff-rota-system/venv/bin/gunicorn --workers 3 --bind unix:/home/staff-rota-system/staffrota.sock rotasystems.wsgi:application --daemon --access-logfile /home/staff-rota-system/logs/gunicorn-access.log --error-logfile /home/staff-rota-system/logs/gunicorn-error.log

sleep 2
ps aux | grep gunicorn | grep -v grep
echo "✅ Gunicorn restarted"

ENDSSH
