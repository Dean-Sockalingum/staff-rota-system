#!/bin/bash
# Complete Production Deployment - Run this when SSH is stable
# This script will deploy the local demo to production

echo "=========================================="
echo "PRODUCTION DEPLOYMENT CHECKLIST"
echo "=========================================="
echo ""
echo "Your LOCAL DEMO is safe at:"
echo "  /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete/"
echo "  Nothing in this script will touch it!"
echo ""
echo "Step 1: Upload cleaned data..."
scp /Users/deansockalingum/Desktop/Staff_Rota_Backups/demo_export_cleaned.json root@159.65.18.80:/home/staff-rota-system/

echo ""
echo "Step 2: Import to production database..."
ssh root@159.65.18.80 << 'ENDSSH'
cd /home/staff-rota-system
source venv/bin/activate
python manage.py loaddata demo_export_cleaned.json
echo ""
echo "Step 3: Verify production database..."
python manage.py shell -c "
from scheduling.models import User, CareHome, Unit, Role, ShiftType
print('========================================')
print('PRODUCTION DATABASE STATUS')
print('========================================')
print(f'  Homes: {CareHome.objects.count()}')
print(f'  Units: {Unit.objects.count()}')
print(f'  Roles: {Role.objects.count()}')
print(f'  Shift Types: {ShiftType.objects.count()}')
print(f'  Users: {User.objects.count()}')
print('')
print('Login: SAP 000541 / Greenball99##')
print('URL: https://demo.therota.co.uk')
print('========================================')
"
ENDSSH

echo ""
echo "✅ Deployment complete!"
echo ""
echo "NEXT STEPS:"
echo "1. Test login at https://demo.therota.co.uk"
echo "2. If it works, you're ready for senior management!"
echo "3. If issues, use local demo at http://127.0.0.1:8001"
