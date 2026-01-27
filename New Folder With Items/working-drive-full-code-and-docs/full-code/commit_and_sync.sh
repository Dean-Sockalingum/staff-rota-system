#!/bin/bash
# Commit and Sync Script - commits to Desktop, pushes to GitHub, syncs to NVMe
# Usage: ./commit_and_sync.sh "Your commit message"

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

COMMIT_MSG="${1:-Auto-commit: $(date '+%Y-%m-%d %H:%M')}"
DESKTOP_PATH="/Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete"

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Staff Rota Commit & Sync${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""

# Change to Desktop repository
cd "$DESKTOP_PATH"

# Step 1: Add all changes
echo -e "${GREEN}[1/5]${NC} Adding all changes..."
git add -A

# Step 2: Commit
echo -e "${GREEN}[2/5]${NC} Committing with message: '$COMMIT_MSG'"
git commit -m "$COMMIT_MSG"

# Step 3: Push to GitHub
echo -e "${GREEN}[3/5]${NC} Pushing to GitHub..."
git push origin main

# Step 4: Sync to NVMe Backups
if [ -d "/Volumes/NVMe_990Pro/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete" ]; then
    echo -e "${GREEN}[4/5]${NC} Syncing to NVMe Backups..."
    cd "/Volumes/NVMe_990Pro/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete"
    git fetch origin main
    git reset --hard origin/main
    echo -e "  ${GREEN}✓${NC} NVMe Backups synced"
else
    echo -e "${YELLOW}[4/5]${NC} NVMe Backups location not found - skipping"
fi

# Step 5: Sync to NVMe Production
if [ -d "/Volumes/NVMe_990Pro/Staff_Rota_Production_Ready_2025-12-21" ]; then
    echo -e "${GREEN}[5/5]${NC} Syncing to NVMe Production..."
    cd "/Volumes/NVMe_990Pro/Staff_Rota_Production_Ready_2025-12-21"
    git fetch origin main
    git reset --hard origin/main
    echo -e "  ${GREEN}✓${NC} NVMe Production synced"
else
    echo -e "${YELLOW}[5/5]${NC} NVMe Production location not found - skipping"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ All locations synced successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Desktop → GitHub → NVMe locations all updated"
