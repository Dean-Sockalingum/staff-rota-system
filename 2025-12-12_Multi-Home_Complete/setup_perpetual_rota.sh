#!/bin/bash

# Setup script for perpetual rota system
# This will generate initial future shifts and optionally setup automated checks

set -e

echo "======================================"
echo "Perpetual Rota System Setup"
echo "======================================"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Find Python executable
if [ -f "../.venv/bin/python" ]; then
    PYTHON="../.venv/bin/python"
elif [ -f ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
else
    PYTHON="python"
fi

echo "Using Python: $PYTHON"
echo ""

# Step 1: Check current coverage
echo "Step 1: Checking current rota coverage..."
$PYTHON manage.py check_rota_coverage

echo ""
echo "======================================"
echo "Step 2: Generate initial future shifts"
echo "======================================"
echo ""

read -p "How many weeks ahead do you want to generate? (default: 52 for 1 year): " WEEKS
WEEKS=${WEEKS:-52}

echo "Generating $WEEKS weeks of future shifts based on 3-week rolling pattern..."
$PYTHON manage.py generate_future_shifts --weeks "$WEEKS"

echo ""
echo "======================================"
echo "Step 3: Setup Automated Checks (Optional)"
echo "======================================"
echo ""

read -p "Do you want to setup a daily automated check? (y/n): " SETUP_CRON

if [ "$SETUP_CRON" = "y" ] || [ "$SETUP_CRON" = "Y" ]; then
    echo ""
    echo "Setting up cron job to run daily at 2:00 AM..."
    
    # Create the cron command
    CRON_CMD="0 2 * * * cd $SCRIPT_DIR && $PYTHON manage.py check_rota_coverage >> /tmp/rota_coverage.log 2>&1"
    
    # Check if cron job already exists
    if crontab -l 2>/dev/null | grep -q "check_rota_coverage"; then
        echo "⚠️  Cron job already exists. Skipping..."
    else
        # Add to crontab
        (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
        echo "✓ Cron job added successfully!"
        echo ""
        echo "The system will now check coverage daily at 2:00 AM"
        echo "Logs will be written to: /tmp/rota_coverage.log"
    fi
else
    echo ""
    echo "Skipping automated setup."
    echo "You can manually run checks with:"
    echo "  python manage.py check_rota_coverage"
fi

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Summary:"
echo "  ✓ Generated $WEEKS weeks of future shifts"
echo "  ✓ 3-week rolling pattern will repeat indefinitely"
echo "  ✓ System will auto-maintain coverage"
echo ""
echo "To view your rota:"
echo "  1. Start server: python manage.py runserver"
echo "  2. Visit: http://localhost:8000/rota/"
echo "  3. Navigate to 2026 weeks to see new shifts"
echo ""
echo "See PERPETUAL_ROTA_SETUP.md for full documentation"
echo ""
