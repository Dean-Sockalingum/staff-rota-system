#!/bin/bash
# Fix production database by running migrations

echo "=========================================="
echo "FIXING PRODUCTION DATABASE"
echo "=========================================="
echo ""

ssh root@159.65.18.80 << 'ENDSSH'
cd /home/staff-rota-system
source venv/bin/activate

echo "Step 1: Running database migrations..."
python manage.py migrate

echo ""
echo "Step 2: Checking if User model exists..."
python manage.py shell -c "
from scheduling.models import User, CareHome
print(f'✓ User model is accessible')
print(f'✓ Users in database: {User.objects.count()}')
print(f'✓ Care Homes: {CareHome.objects.count()}')
"

echo ""
echo "Step 3: Restarting Gunicorn..."
pkill -f gunicorn
sleep 2
gunicorn --workers 3 --bind unix:/home/staff-rota-system/staffrota.sock rotasystems.wsgi:application --daemon --error-logfile /home/staff-rota-system/logs/gunicorn-error.log --access-logfile /home/staff-rota-system/logs/gunicorn-access.log

echo "✓ Gunicorn restarted"
ENDSSH

echo ""
echo "=========================================="
echo "FIX COMPLETE"
echo "=========================================="
echo ""
echo "Please test: https://demo.therota.co.uk/compliance/training/management/"
