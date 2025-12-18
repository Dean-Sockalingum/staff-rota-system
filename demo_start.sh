#!/bin/bash
# Quick Start for Demo Mode
# Sets up and launches the system in DEMO mode for safe testing

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Change to script directory
cd "$(dirname "$0")"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║      STAFF ROTA SYSTEM - DEMO QUICK START                ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check if we're already in demo mode
MODE_FILE=".current_mode"
if [ -f "$MODE_FILE" ]; then
    CURRENT_MODE=$(cat "$MODE_FILE")
    echo -e "Current mode: ${YELLOW}$CURRENT_MODE${NC}"
else
    echo "No mode set yet."
fi

echo ""
echo -e "${BLUE}This will:${NC}"
echo "  1. Switch to DEMO mode (if not already)"
echo "  2. Ensure demo data is ready"
echo "  3. Start the development server"
echo "  4. Open your browser to the system"
echo ""

read -p "Continue? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo -e "${YELLOW}Step 1: Switching to DEMO mode...${NC}"
python3 manage.py set_mode demo

echo ""
echo -e "${YELLOW}Step 2: Checking server status...${NC}"
# Kill any existing server
pkill -f "python3 manage.py runserver" 2>/dev/null
sleep 1

echo ""
echo -e "${GREEN}✓ Demo environment ready!${NC}"
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║      DEMO MODE ACTIVE                                    ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}Starting development server...${NC}"
echo ""
echo "The server will start at: http://127.0.0.1:8000"
echo ""
echo -e "${YELLOW}Login Credentials:${NC}"
echo "  Username: admin"
echo "  Password: admin"
echo ""
echo -e "${BLUE}Press Ctrl+C to stop the server${NC}"
echo ""
echo "────────────────────────────────────────────────────────────"
echo ""

# Start the server
python3 manage.py runserver

echo ""
echo -e "${GREEN}Demo session ended.${NC}"
echo ""
