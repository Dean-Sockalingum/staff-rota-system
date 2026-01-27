#!/bin/bash
# Quick Mode Switcher for Staff Rota System
# Easily switch between DEMO and PRODUCTION modes

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Change to script directory
cd "$(dirname "$0")"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║      STAFF ROTA SYSTEM - MODE SWITCHER                   ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check current mode
python3 manage.py set_mode status

echo ""
echo "What would you like to do?"
echo ""
echo "  1) Switch to DEMO mode (safe testing environment)"
echo "  2) Switch to PRODUCTION mode (live data)"
echo "  3) Reset DEMO data to clean state"
echo "  4) Check current status"
echo "  5) Exit"
echo ""
read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        echo ""
        echo -e "${YELLOW}Switching to DEMO mode...${NC}"
        python3 manage.py set_mode demo
        ;;
    2)
        echo ""
        echo -e "${RED}⚠️  WARNING: This will switch to PRODUCTION mode${NC}"
        echo -e "${RED}All changes will affect LIVE data!${NC}"
        echo ""
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            python3 manage.py set_mode prod
        else
            echo "Cancelled."
        fi
        ;;
    3)
        echo ""
        echo -e "${YELLOW}Resetting DEMO data...${NC}"
        python3 manage.py reset_demo
        ;;
    4)
        echo ""
        python3 manage.py set_mode status
        ;;
    5)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✓ Done!${NC}"
echo ""
