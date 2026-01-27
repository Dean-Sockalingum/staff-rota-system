#!/bin/bash

# Script to install weekly Monday morning report cron job
# This will run every Monday at 7:00 AM

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$SCRIPT_DIR"
MANAGE_PY="$PROJECT_DIR/manage.py"

echo "=================================================="
echo "Weekly Report Cron Job Installation"
echo "=================================================="
echo ""

# Check if manage.py exists
if [ ! -f "$MANAGE_PY" ]; then
    echo "❌ Error: manage.py not found at $MANAGE_PY"
    exit 1
fi

echo "Project directory: $PROJECT_DIR"
echo ""

# Create the cron job command
# This runs every Monday at 7:00 AM
CRON_SCHEDULE="0 7 * * 1"  # Minute Hour Day Month DayOfWeek (1 = Monday)
CRON_COMMAND="cd $PROJECT_DIR && /usr/bin/python3 $MANAGE_PY generate_weekly_report --save --email >> $PROJECT_DIR/logs/weekly_report.log 2>&1"

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_DIR/logs"

echo "Cron job will be configured as follows:"
echo "Schedule: Every Monday at 7:00 AM"
echo "Command: $CRON_COMMAND"
echo ""

# Check if cron job already exists
EXISTING_CRON=$(crontab -l 2>/dev/null | grep -F "generate_weekly_report")

if [ ! -z "$EXISTING_CRON" ]; then
    echo "⚠️  Warning: A weekly report cron job already exists:"
    echo "$EXISTING_CRON"
    echo ""
    read -p "Do you want to replace it? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
    
    # Remove existing cron job
    (crontab -l 2>/dev/null | grep -vF "generate_weekly_report") | crontab -
    echo "✓ Removed existing cron job"
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_SCHEDULE $CRON_COMMAND") | crontab -

echo ""
echo "✅ Weekly report cron job installed successfully!"
echo ""
echo "The report will run every Monday at 7:00 AM and will:"
echo "  • Cover events from Friday-Sunday"
echo "  • Include sickness, overtime, agency usage, and incidents"
echo "  • Save to JSON file in /tmp/"
echo "  • Log output to: $PROJECT_DIR/logs/weekly_report.log"
echo ""
echo "Current crontab:"
crontab -l
echo ""
echo "=================================================="
echo "Testing the report (dry run)..."
echo "=================================================="
echo ""

# Run a test of the command
cd "$PROJECT_DIR"
python3 manage.py generate_weekly_report

echo ""
echo "=================================================="
echo "Installation Complete!"
echo "=================================================="
echo ""
echo "To manually run the report:"
echo "  cd $PROJECT_DIR"
echo "  python3 manage.py generate_weekly_report --save --email"
echo ""
echo "To view the cron log:"
echo "  tail -f $PROJECT_DIR/logs/weekly_report.log"
echo ""
echo "To remove the cron job:"
echo "  crontab -e"
echo "  (Then delete the line containing 'generate_weekly_report')"
echo ""
