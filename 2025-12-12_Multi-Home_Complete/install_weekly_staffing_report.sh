#!/bin/bash

# Installation script for weekly additional staffing report (Overtime & Agency)
# This report runs every Monday morning at 8:00 AM

echo "================================================================"
echo "WEEKLY ADDITIONAL STAFFING REPORT - INSTALLATION"
echo "================================================================"
echo ""
echo "This script will set up a cron job to automatically send weekly"
echo "staffing reports (overtime and agency usage) to management"
echo "every Monday morning at 8:00 AM."
echo ""

# Get the absolute path to the project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

echo "Project directory: $PROJECT_DIR"
echo ""

# Find Python 3 executable
PYTHON_CMD=$(which python3)
if [ -z "$PYTHON_CMD" ]; then
    echo "❌ Error: python3 not found in PATH"
    exit 1
fi

echo "Python executable: $PYTHON_CMD"
echo ""

# Test the command
echo "Testing the weekly report command..."
echo "-----------------------------------"
$PYTHON_CMD "$PROJECT_DIR/manage.py" send_weekly_staffing_report --dry-run

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Error: Command test failed. Please check for errors above."
    exit 1
fi

echo ""
echo "✓ Command test successful!"
echo ""

# Create cron job entry
CRON_CMD="0 8 * * 1 cd $PROJECT_DIR && $PYTHON_CMD $PROJECT_DIR/manage.py send_weekly_staffing_report >> $PROJECT_DIR/logs/weekly_staffing_report.log 2>&1"

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_DIR/logs"

echo "Proposed cron job:"
echo "-----------------------------------"
echo "$CRON_CMD"
echo "-----------------------------------"
echo ""
echo "This will run every Monday at 8:00 AM"
echo ""

# Check if cron job already exists
(crontab -l 2>/dev/null | grep -q "send_weekly_staffing_report") && ALREADY_EXISTS=true || ALREADY_EXISTS=false

if [ "$ALREADY_EXISTS" = true ]; then
    echo "⚠️  A weekly staffing report cron job already exists."
    echo ""
    read -p "Do you want to replace it? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
    
    # Remove existing cron job
    crontab -l 2>/dev/null | grep -v "send_weekly_staffing_report" | crontab -
    echo "✓ Removed existing cron job"
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -

echo ""
echo "================================================================"
echo "✅ WEEKLY STAFFING REPORT INSTALLED SUCCESSFULLY!"
echo "================================================================"
echo ""
echo "Schedule: Every Monday at 8:00 AM"
echo "Report Period: Previous week (Sunday to Saturday)"
echo "Recipients: All managers with is_management=True"
echo "Log File: $PROJECT_DIR/logs/weekly_staffing_report.log"
echo ""
echo "Manual Testing:"
echo "  • Test for previous week:"
echo "    $PYTHON_CMD manage.py send_weekly_staffing_report"
echo ""
echo "  • Test for specific week:"
echo "    $PYTHON_CMD manage.py send_weekly_staffing_report --week-start 2025-12-01"
echo ""
echo "  • Send to specific email (testing):"
echo "    $PYTHON_CMD manage.py send_weekly_staffing_report --email test@example.com"
echo ""
echo "  • Dry run (no email sent):"
echo "    $PYTHON_CMD manage.py send_weekly_staffing_report --dry-run"
echo ""
echo "View cron jobs:"
echo "  crontab -l | grep staffing"
echo ""
echo "================================================================"
