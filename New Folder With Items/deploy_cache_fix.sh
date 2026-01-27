#!/bin/bash
# Deploy cache-prevention fix to production

echo "Deploying cache-prevention fix..."

# Copy views.py to production
scp /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete/scheduling/views.py root@159.65.18.80:/home/staff-rota-system/2025-12-12_Multi-Home_Complete/scheduling/views.py

# Restart the service
ssh root@159.65.18.80 << 'ENDSSH'
# Clear Django cache
cd /home/staff-rota-system/2025-12-12_Multi-Home_Complete
source ../venv/bin/activate
python manage.py clearsessions

# Restart Gunicorn
systemctl restart staffrota

# Wait and check status
sleep 2
systemctl status staffrota --no-pager | head -10
ENDSSH

echo "Deployment complete!"
echo "IMPORTANT: Clear browser cache or use Ctrl+Shift+R (hard refresh)"
echo "Also consider clearing Cloudflare cache if issue persists"
