#!/bin/bash
# Desktop Shortcut Creator for Staff Rota System
# Creates clickable shortcuts on your macOS Desktop

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

DESKTOP="$HOME/Desktop"
PROJECT_DIR="/Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║      CREATING DESKTOP SHORTCUTS                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Create "Start Demo" shortcut
echo -e "${BLUE}Creating 'Start Demo' shortcut...${NC}"
cat > "$DESKTOP/Start_Demo.command" << 'EOF'
#!/bin/bash
cd /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
./demo_start.sh
EOF

chmod +x "$DESKTOP/Start_Demo.command"
echo -e "${GREEN}✓ Created: Start_Demo.command${NC}"

# Create "Switch Mode" shortcut
echo -e "${BLUE}Creating 'Switch Mode' shortcut...${NC}"
cat > "$DESKTOP/Switch_Mode.command" << 'EOF'
#!/bin/bash
cd /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
./switch_mode.sh
EOF

chmod +x "$DESKTOP/Switch_Mode.command"
echo -e "${GREEN}✓ Created: Switch_Mode.command${NC}"

# Create "Stop Server" shortcut
echo -e "${BLUE}Creating 'Stop Server' shortcut...${NC}"
cat > "$DESKTOP/Stop_Server.command" << 'EOF'
#!/bin/bash
echo ""
echo "Stopping Staff Rota System server..."
pkill -f "python3 manage.py runserver"
sleep 1
echo "✓ Server stopped"
echo ""
read -p "Press Enter to close..."
EOF

chmod +x "$DESKTOP/Stop_Server.command"
echo -e "${GREEN}✓ Created: Stop_Server.command${NC}"

# Create "Reset Demo" shortcut
echo -e "${BLUE}Creating 'Reset Demo' shortcut...${NC}"
cat > "$DESKTOP/Reset_Demo.command" << 'EOF'
#!/bin/bash
cd /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
python3 manage.py reset_demo
echo ""
read -p "Press Enter to close..."
EOF

chmod +x "$DESKTOP/Reset_Demo.command"
echo -e "${GREEN}✓ Created: Reset_Demo.command${NC}"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║      SHORTCUTS CREATED!                                  ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}Desktop shortcuts created:${NC}"
echo "  📱 Start_Demo.command       - Launch demo in one click"
echo "  🔄 Switch_Mode.command      - Switch between demo/production"
echo "  🛑 Stop_Server.command      - Stop the running server"
echo "  ♻️  Reset_Demo.command      - Reset demo data"
echo ""
echo -e "${YELLOW}To use:${NC} Just double-click any .command file on your Desktop"
echo ""
echo -e "${BLUE}TIP:${NC} Right-click → Get Info → change icon for better visuals!"
echo ""
