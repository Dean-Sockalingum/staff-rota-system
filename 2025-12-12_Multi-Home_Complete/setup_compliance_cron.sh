#!/bin/bash
#
# Setup Scheduled Compliance Checks
# This script creates cron jobs to run automated compliance checks
#

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$SCRIPT_DIR"

echo "📋 Setting up Scheduled Compliance Checks"
echo "=========================================="
echo ""

# Check if running in correct directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found. Please run from project root."
    exit 1
fi

# Get Python path
PYTHON_PATH=$(which python3)
if [ -z "$PYTHON_PATH" ]; then
    PYTHON_PATH=$(which python)
fi

echo "Python: $PYTHON_PATH"
echo "Project: $PROJECT_DIR"
echo ""

# Create cron job entries
CRON_DAILY="0 2 * * * cd $PROJECT_DIR && $PYTHON_PATH manage.py scheduled_compliance_check --notify --period-days 7 >> /tmp/compliance_check.log 2>&1"
CRON_WEEKLY="0 3 * * 0 cd $PROJECT_DIR && $PYTHON_PATH manage.py run_compliance_checks --start-date \$(date -d '30 days ago' +\%Y-\%m-\%d) --end-date \$(date +\%Y-\%m-\%d) >> /tmp/compliance_weekly.log 2>&1"

echo "📅 Recommended Cron Schedule:"
echo ""
echo "Daily Check (2am every day):"
echo "$CRON_DAILY"
echo ""
echo "Weekly Full Check (3am every Sunday):"
echo "$CRON_WEEKLY"
echo ""

# Ask user if they want to install cron jobs
read -p "Install these cron jobs now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Backup existing crontab
    crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null
    
    # Add new cron jobs
    (crontab -l 2>/dev/null; echo ""; echo "# Staff Rota Compliance Checks"; echo "$CRON_DAILY"; echo "$CRON_WEEKLY") | crontab -
    
    echo "✅ Cron jobs installed successfully!"
    echo ""
    echo "Current crontab:"
    crontab -l | grep -A 2 "Staff Rota Compliance"
else
    echo "ℹ️  Manual installation:"
    echo "   1. Run: crontab -e"
    echo "   2. Add the cron jobs shown above"
    echo "   3. Save and exit"
fi

echo ""
echo "📊 Test Commands:"
echo "   Test daily check:"
echo "   python3 manage.py scheduled_compliance_check --notify --period-days 7"
echo ""
echo "   Test weekly check:"
echo "   python3 manage.py run_compliance_checks"
echo ""
echo "✅ Setup complete!"
