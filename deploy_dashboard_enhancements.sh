#!/bin/bash
# Deploy Dashboard Enhancements to Production
# Date: January 12, 2026

echo "🚀 Deploying Dashboard Enhancements to demo.therota.co.uk..."

# Production server details
PROD_SERVER="root@159.65.18.80"
PROD_PATH="/home/staff-rota-system/scheduling/templates/scheduling"
LOCAL_FILE="/Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete/scheduling/templates/scheduling/senior_management_dashboard.html"

echo "📁 Source: $LOCAL_FILE"
echo "🎯 Target: $PROD_SERVER:$PROD_PATH"
echo ""

# Step 1: Backup existing file on production
echo "Step 1: Creating backup on production..."
ssh $PROD_SERVER "cd $PROD_PATH && cp senior_management_dashboard.html senior_management_dashboard.html.backup.$(date +%Y%m%d_%H%M%S)"
if [ $? -eq 0 ]; then
    echo "✅ Backup created"
else
    echo "❌ Backup failed - aborting deployment"
    exit 1
fi

# Step 2: Transfer enhanced file
echo ""
echo "Step 2: Transferring enhanced dashboard file..."
scp "$LOCAL_FILE" "$PROD_SERVER:$PROD_PATH/senior_management_dashboard.html"
if [ $? -eq 0 ]; then
    echo "✅ File transferred successfully"
else
    echo "❌ File transfer failed"
    exit 1
fi

# Step 3: Set proper permissions
echo ""
echo "Step 3: Setting file permissions..."
ssh $PROD_SERVER "chmod 644 $PROD_PATH/senior_management_dashboard.html && chown www-data:www-data $PROD_PATH/senior_management_dashboard.html"
if [ $? -eq 0 ]; then
    echo "✅ Permissions set"
else
    echo "⚠️  Permission setting failed (may need manual fix)"
fi

# Step 4: Restart services
echo ""
echo "Step 4: Restarting production services..."
ssh $PROD_SERVER "systemctl restart gunicorn && systemctl restart nginx"
if [ $? -eq 0 ]; then
    echo "✅ Services restarted"
else
    echo "❌ Service restart failed"
    exit 1
fi

# Step 5: Verify deployment
echo ""
echo "Step 5: Verifying deployment..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" https://demo.therota.co.uk/scheduling/management/senior-dashboard/)
if [ "$RESPONSE" = "200" ]; then
    echo "✅ Dashboard responding (HTTP $RESPONSE)"
else
    echo "⚠️  Dashboard response: HTTP $RESPONSE (check manually)"
fi

echo ""
echo "=========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "📊 Dashboard URL: https://demo.therota.co.uk/scheduling/management/senior-dashboard/"
echo ""
echo "🧪 Test Checklist:"
echo "  1. Multi-Home Staffing chart click handlers"
echo "  2. Budget vs Actual dynamic colors"
echo "  3. Overtime Trend threshold line"
echo "  4. Compliance Score status indicators"
echo "  5. GAP breakdown modal (click green Gap section)"
echo ""
echo "📝 Rollback command if needed:"
echo "  ssh $PROD_SERVER 'cd $PROD_PATH && cp senior_management_dashboard.html.backup.* senior_management_dashboard.html && systemctl restart gunicorn'"
echo ""
