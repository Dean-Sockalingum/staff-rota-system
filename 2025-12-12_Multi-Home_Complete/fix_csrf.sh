#!/bin/bash

# Fix CSRF_TRUSTED_ORIGINS for production

ssh root@159.65.18.80 << 'ENDSSH'
cd /home/staff-rota-system

# Backup settings
cp rotasystems/settings.py rotasystems/settings.py.backup_$(date +%Y%m%d_%H%M%S)

# Check if CSRF_TRUSTED_ORIGINS exists
if grep -q "CSRF_TRUSTED_ORIGINS" rotasystems/settings.py; then
    echo "CSRF_TRUSTED_ORIGINS found, updating..."
    # Update existing
    sed -i "s/CSRF_TRUSTED_ORIGINS = .*/CSRF_TRUSTED_ORIGINS = ['https:\/\/demo.therota.co.uk', 'https:\/\/therota.co.uk']/" rotasystems/settings.py
else
    echo "CSRF_TRUSTED_ORIGINS not found, adding..."
    # Add after ALLOWED_HOSTS
    sed -i "/^ALLOWED_HOSTS/a\\
\\
# CSRF Settings\\
CSRF_TRUSTED_ORIGINS = ['https://demo.therota.co.uk', 'https://therota.co.uk']" rotasystems/settings.py
fi

# Also ensure ALLOWED_HOSTS includes the domain
if ! grep -q "demo.therota.co.uk" rotasystems/settings.py; then
    echo "Adding demo.therota.co.uk to ALLOWED_HOSTS..."
    sed -i "s/ALLOWED_HOSTS = \[/ALLOWED_HOSTS = ['demo.therota.co.uk', 'therota.co.uk', /" rotasystems/settings.py
fi

echo "Settings updated. Restarting gunicorn..."
pkill gunicorn
gunicorn --workers 3 --bind unix:/home/staff-rota-system/staffrota.sock rotasystems.wsgi:application --daemon --access-logfile /home/staff-rota-system/logs/gunicorn-access.log --error-logfile /home/staff-rota-system/logs/gunicorn-error.log

sleep 2
ps aux | grep gunicorn | grep -v grep

echo ""
echo "Testing login..."
curl -s -o /dev/null -w "Login page: %{http_code}\n" https://demo.therota.co.uk/login/

ENDSSH

echo ""
echo "Fix applied. Test login manually at: https://demo.therota.co.uk/login/"
echo "Credentials: SAP 000541 / Greenball99##"
