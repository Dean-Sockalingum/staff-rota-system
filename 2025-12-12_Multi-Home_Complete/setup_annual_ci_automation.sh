#!/bin/bash

#############################################################################
# Care Inspectorate Report Automation Setup
# 
# This script sets up automated annual CI report imports and improvement
# plan generation to run every April 1st at 2 AM
#
# Usage: ./setup_annual_ci_automation.sh
#############################################################################

set -e

echo "=================================================="
echo "Care Inspectorate Automation Setup"
echo "=================================================="
echo ""

# Get the current directory (project root)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH=$(which python3)

echo "Project Directory: $PROJECT_DIR"
echo "Python Path: $PYTHON_PATH"
echo ""

# Create cron script for CI report import and plan generation
CRON_SCRIPT="$PROJECT_DIR/run_annual_ci_automation.sh"

cat > "$CRON_SCRIPT" <<'EOF'
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
EOF

chmod +x "$CRON_SCRIPT"

echo "✓ Created automation script: $CRON_SCRIPT"
echo ""

# Create LaunchAgent for macOS
PLIST_FILE="$HOME/Library/LaunchAgents/com.staffrota.ciautomation.plist"

cat > "$PLIST_FILE" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.staffrota.ciautomation</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>$CRON_SCRIPT</string>
    </array>
    
    <key>StartCalendarInterval</key>
    <dict>
        <key>Month</key>
        <integer>4</integer>
        <key>Day</key>
        <integer>1</integer>
        <key>Hour</key>
        <integer>2</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    
    <key>StandardOutPath</key>
    <string>$HOME/Library/Logs/ci_automation_stdout.log</string>
    
    <key>StandardErrorPath</key>
    <string>$HOME/Library/Logs/ci_automation_stderr.log</string>
    
    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>
    
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
EOF

echo "✓ Created LaunchAgent: $PLIST_FILE"
echo ""

# Load the LaunchAgent
echo "Loading LaunchAgent..."
launchctl unload "$PLIST_FILE" 2>/dev/null || true
launchctl load "$PLIST_FILE"

if [ $? -eq 0 ]; then
    echo "✓ LaunchAgent loaded successfully"
else
    echo "✗ Failed to load LaunchAgent"
    exit 1
fi

echo ""

# Verify it's loaded
echo "Verifying LaunchAgent status..."
if launchctl list | grep -q "com.staffrota.ciautomation"; then
    echo "✓ LaunchAgent is active"
else
    echo "⚠️  LaunchAgent may not be active"
fi

echo ""
echo "=================================================="
echo "Setup Complete!"
echo "=================================================="
echo ""
echo "Configuration Summary:"
echo "  - Automation script: $CRON_SCRIPT"
echo "  - LaunchAgent: $PLIST_FILE"
echo "  - Schedule: April 1st at 2:00 AM annually"
echo "  - Logs: ~/Library/Logs/ci_automation.log"
echo ""
echo "What happens on April 1st:"
echo "  1. Import latest CI reports for all homes"
echo "  2. Analyze 12 months of operational data"
echo "  3. Generate ML-powered improvement plans"
echo "  4. Create organizational improvement plan"
echo ""
echo "Manual Commands:"
echo "  Test import:     python3 manage.py import_ci_reports --all --latest-only"
echo "  Test generation: python3 manage.py generate_annual_improvement_plans --all --dry-run"
echo "  Run now:         $CRON_SCRIPT"
echo "  View logs:       tail -f ~/Library/Logs/ci_automation.log"
echo ""
echo "=================================================="
