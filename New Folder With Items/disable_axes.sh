#!/bin/bash
cd /home/staff-rota-system

# Backup settings
cp rotasystems/settings.py rotasystems/settings.py.with_axes

# Comment out AXES in INSTALLED_APPS
sed -i "s/'axes',/# 'axes',/g" rotasystems/settings.py

# Comment out AXES middleware
sed -i "s/'axes.middleware.AxesMiddleware',/# 'axes.middleware.AxesMiddleware',/g" rotasystems/settings.py

# Comment out AXES authentication backend
sed -i "s/'axes.backends.AxesStandaloneBackend',/# 'axes.backends.AxesStandaloneBackend',/g" rotasystems/settings.py

# Restart service
systemctl restart staffrota

echo "AXES disabled and server restarted"
systemctl status staffrota --no-pager | head -15
