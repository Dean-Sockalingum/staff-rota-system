#!/bin/bash
#
# Annual Leave Reminder Email Automation Script
# 
# This script provides easy commands to send leave reminder emails
# with various filtering options.
#
# Usage:
#   ./send_leave_emails.sh [option]
#
# Options:
#   monthly       - Send monthly reminder (5+ days remaining)
#   quarterly     - Send quarterly reminder (1+ days remaining)  
#   urgent        - Send to all staff with any leave remaining
#   test          - Dry run to ADMIN001 only (preview)
#   specific SAP  - Send to specific staff by SAP ID
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Project directory
PROJECT_DIR="/Users/deansockalingum/Staff Rota/rotasystems"
PYTHON="/Library/Frameworks/Python.framework/Versions/3.14/bin/python3"
LOG_DIR="/var/log/rotasystem"

# Ensure log directory exists
mkdir -p "$LOG_DIR" 2>/dev/null || true

echo -e "${PURPLE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║     Annual Leave Reminder Email Automation Script         ║${NC}"
echo -e "${PURPLE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Change to project directory
cd "$PROJECT_DIR"

# Check if argument provided
if [ $# -eq 0 ]; then
    echo -e "${YELLOW}Usage:${NC} $0 [option]"
    echo ""
    echo -e "${BLUE}Available options:${NC}"
    echo "  monthly       - Monthly reminder (staff with 5+ days remaining)"
    echo "  quarterly     - Quarterly reminder (staff with 1+ days remaining)"
    echo "  urgent        - Year-end urgent (all staff with unused leave)"
    echo "  test          - Dry run to ADMIN001 (preview mode)"
    echo "  specific SAP  - Send to specific staff by SAP ID (e.g., specific ADMIN001)"
    echo ""
    echo -e "${BLUE}Examples:${NC}"
    echo "  $0 test                    # Preview mode"
    echo "  $0 monthly                 # Monthly reminder"
    echo "  $0 specific ADMIN001       # Send to ADMIN001 only"
    echo ""
    exit 1
fi

OPTION=$1

case "$OPTION" in
    test)
        echo -e "${GREEN}Running in TEST/DRY-RUN mode...${NC}"
        echo "This will preview an email to ADMIN001 without actually sending"
        echo ""
        $PYTHON manage.py send_leave_reminders --specific-staff ADMIN001 --dry-run
        ;;
    
    monthly)
        echo -e "${GREEN}Sending MONTHLY leave reminders...${NC}"
        echo "Target: All staff with 5+ days remaining"
        echo "Log: $LOG_DIR/leave_reminders.log"
        echo ""
        read -p "Continue? (y/N): " confirm
        if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
            $PYTHON manage.py send_leave_reminders --min-days 5 | tee -a "$LOG_DIR/leave_reminders.log"
            echo ""
            echo -e "${GREEN}✅ Monthly reminders sent!${NC}"
        else
            echo "Cancelled."
        fi
        ;;
    
    quarterly)
        echo -e "${GREEN}Sending QUARTERLY leave reminders...${NC}"
        echo "Target: All staff with 1+ days remaining"
        echo "Log: $LOG_DIR/leave_reminders.log"
        echo ""
        read -p "Continue? (y/N): " confirm
        if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
            $PYTHON manage.py send_leave_reminders --min-days 1 | tee -a "$LOG_DIR/leave_reminders.log"
            echo ""
            echo -e "${GREEN}✅ Quarterly reminders sent!${NC}"
        else
            echo "Cancelled."
        fi
        ;;
    
    urgent)
        echo -e "${RED}Sending URGENT year-end leave reminders...${NC}"
        echo "Target: ALL staff with any unused leave"
        echo "Log: $LOG_DIR/leave_reminders.log"
        echo ""
        read -p "⚠️  This will email ALL staff with remaining leave. Continue? (y/N): " confirm
        if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
            $PYTHON manage.py send_leave_reminders | tee -a "$LOG_DIR/leave_reminders.log"
            echo ""
            echo -e "${GREEN}✅ Urgent reminders sent!${NC}"
        else
            echo "Cancelled."
        fi
        ;;
    
    specific)
        if [ -z "$2" ]; then
            echo -e "${RED}Error: SAP ID required${NC}"
            echo "Usage: $0 specific <SAP_ID>"
            echo "Example: $0 specific ADMIN001"
            exit 1
        fi
        SAP_ID=$2
        echo -e "${GREEN}Sending reminder to specific staff: ${BLUE}$SAP_ID${NC}"
        echo ""
        $PYTHON manage.py send_leave_reminders --specific-staff "$SAP_ID"
        echo ""
        echo -e "${GREEN}✅ Email sent to $SAP_ID!${NC}"
        ;;
    
    *)
        echo -e "${RED}Error: Unknown option '$OPTION'${NC}"
        echo ""
        echo "Available options: test, monthly, quarterly, urgent, specific"
        echo "Run '$0' without arguments for help"
        exit 1
        ;;
esac

echo ""
echo -e "${PURPLE}═══════════════════════════════════════════════════════════${NC}"
echo ""
