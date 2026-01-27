#!/bin/bash

# Annual CI Report Import and Service Improvement Plan Generation
# Runs every April 1st at 2 AM

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$HOME/Library/Logs"
LOG_FILE="$LOG_DIR/ci_automation.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Start logging
echo "========================================" >> "$LOG_FILE"
echo "CI Automation Run: $DATE" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# Change to project directory
cd "$PROJECT_DIR" || exit 1

# Step 1: Import latest Care Inspectorate reports
echo "[$DATE] Step 1: Importing CI reports..." >> "$LOG_FILE"
python3 manage.py import_ci_reports --all --latest-only 2>> "$LOG_FILE"

if [ $? -eq 0 ]; then
    echo "[$DATE] ✓ CI reports imported successfully" >> "$LOG_FILE"
else
    echo "[$DATE] ✗ CI report import failed" >> "$LOG_FILE"
    exit 1
fi

# Step 2: Generate annual improvement plans
echo "[$DATE] Step 2: Generating improvement plans..." >> "$LOG_FILE"
python3 manage.py generate_annual_improvement_plans --all 2>> "$LOG_FILE"

if [ $? -eq 0 ]; then
    echo "[$DATE] ✓ Improvement plans generated successfully" >> "$LOG_FILE"
else
    echo "[$DATE] ✗ Improvement plan generation failed" >> "$LOG_FILE"
    exit 1
fi

# Step 3: Send notification emails (optional)
# Uncomment if you want email notifications
# python3 manage.py send_plan_notifications 2>> "$LOG_FILE"

echo "[$DATE] Automation complete" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Keep log file size manageable (keep last 1000 lines)
tail -1000 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
