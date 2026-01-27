#!/bin/bash
# Deploy Training Compliance Dashboard Fix to Production
# This script uploads the fixed views_compliance.py file to production

echo "=========================================="
echo "DEPLOYING COMPLIANCE DASHBOARD FIX"
echo "=========================================="
echo ""
echo "This will:"
echo "1. Upload the fixed views_compliance.py to production"
echo "2. Restart the Django application"
echo "3. Check the production logs for any errors"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Deployment cancelled."
    exit 1
fi

echo ""
echo "Step 1: Uploading fixed views_compliance.py..."
scp scheduling/views_compliance.py root@159.65.18.80:/home/staff-rota-system/scheduling/

echo ""
echo "Step 2: Restarting Django application..."
ssh root@159.65.18.80 << 'ENDSSH'
cd /home/staff-rota-system

# Restart Gunicorn service
sudo systemctl restart gunicorn 2>/dev/null || supervisorctl restart all 2>/dev/null || pkill -HUP gunicorn

echo "Waiting 3 seconds for restart..."
sleep 3

echo ""
echo "Step 3: Checking recent application logs..."
tail -30 /var/log/gunicorn/error.log 2>/dev/null || \
tail -30 /var/log/gunicorn/gunicorn.log 2>/dev/null || \
tail -30 logs/django.log 2>/dev/null || \
journalctl -u gunicorn -n 30 --no-pager 2>/dev/null || \
echo "Could not find application logs"

ENDSSH

echo ""
echo "=========================================="
echo "DEPLOYMENT COMPLETE"
echo "=========================================="
echo ""
echo "Please test the training compliance dashboard at:"
echo "https://demo.therota.co.uk/compliance/training/management/"
echo ""
echo "If you still see an error, check the output above for details."
echo ""
