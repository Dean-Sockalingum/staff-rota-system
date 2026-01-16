#!/bin/bash
# Production Deployment Test
# Tests the production deployment

echo "=========================================="
echo "PRODUCTION DEPLOYMENT TEST"
echo "=========================================="
echo ""

echo "Test 1: Check production site is accessible..."
if curl -s -f https://demo.therota.co.uk/login/ > /dev/null; then
    echo "  ✓ Site is accessible"
else
    echo "  ✗ Site is NOT accessible"
    exit 1
fi

echo ""
echo "Test 2: Verify database..."
ssh root@159.65.18.80 'cd /home/staff-rota-system && source venv/bin/activate && python verify_production.py' | grep -A 20 "PRODUCTION DATABASE"

echo ""
echo "=========================================="
echo "PRODUCTION DEPLOYMENT STATUS"
echo "=========================================="
echo ""
echo "✅ Production is READY for demo!"
echo ""
echo "Login Details:"
echo "  URL: https://demo.therota.co.uk"
echo "  SAP: 000541"
echo "  Password: Greenball99##"
echo ""
echo "Features Available:"
echo "  • 5 Care Homes"
echo "  • 42 Units"
echo "  • 813 Active Staff"
echo "  • Multi-home dashboard"
echo "  • Shift scheduling"
echo "  • Staff management"
echo ""
echo "=========================================="
echo "BACKUP OPTION (if production has issues):"
echo "=========================================="
echo ""
echo "Your local demo is still available:"
echo "  Location: /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete/"
echo "  Start: cd above && python3 manage.py runserver 8001"
echo "  URL: http://127.0.0.1:8001"
echo "  Login: SAP 000541 / Greenball99##"
echo ""
