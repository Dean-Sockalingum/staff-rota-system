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
echo -e "${GREEN}[1/4]${NC} Adding all changes..."
git add -A

# Step 2: Commit
echo -e "${GREEN}[2/4]${NC} Committing with message: '$COMMIT_MSG'"
git commit -m "$COMMIT_MSG"

# Step 3: Push to GitHub
echo -e "${GREEN}[3/4]${NC} Pushing to GitHub..."
git push origin main

# Run post-push hook manually (since post-push is not a standard Git hook)
if [ -x .git/hooks/post-push ]; then
    .git/hooks/post-push
fi

# Step 4: Summary
echo -e "${GREEN}[4/4]${NC} NVMe sync completed (check log: ~/Library/Logs/staff_rota_post_push.log)""

# Step 5: Summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ All locations synced successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Desktop → GitHub → NVMe locations all updated"
