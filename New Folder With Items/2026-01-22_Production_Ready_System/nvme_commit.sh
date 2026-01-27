#!/bin/bash
# Wrapper script for NVMe-based development workflow
# Commits, pushes, and syncs to Desktop automatically

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

NVME_DIR="/Volumes/NVMe_990Pro/Staff_Rota_Production_Ready_2025-12-21"

cd "$NVME_DIR" || exit 1

# Get commit message from argument or generate timestamp
if [ -z "$1" ]; then
    COMMIT_MSG="Auto-commit: $(date '+%Y-%m-%d %H:%M:%S')"
else
    COMMIT_MSG="$1"
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🚀 NVMe Development Workflow${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Stage all changes
echo -e "${YELLOW}📦 Staging changes...${NC}"
git add -A

# Commit
echo -e "${YELLOW}💾 Committing: ${COMMIT_MSG}${NC}"
git commit -m "$COMMIT_MSG"

# Push and sync happen automatically via post-commit hook
echo -e "${GREEN}✅ Workflow complete! Desktop will be synced automatically.${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
