#!/bin/bash
# Daily Sync Script: NVMe → GitHub → Desktop
# Run this daily from NVMe to backup to Desktop
# Usage: ./sync_to_desktop.sh

set -e  # Exit on error

NVME_PATH="/Volumes/NVMe_990Pro/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete"
DESKTOP_PATH="/Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete"

echo "═══════════════════════════════════════════════════════════════"
echo "  📦 Daily Backup: NVMe → GitHub → Desktop"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Step 1: Check we're on NVMe
cd "$NVME_PATH"
echo "✓ Working from NVMe (source of truth)"

# Step 2: Check for uncommitted changes
if [[ -n $(git status --porcelain) ]]; then
    echo ""
    echo "⚠️  You have uncommitted changes on NVMe:"
    git status --short
    echo ""
    read -p "Commit these changes first? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter commit message: " commit_msg
        git add .
        git commit -m "$commit_msg"
        echo "✓ Changes committed"
    else
        echo "❌ Sync aborted - commit changes first"
        exit 1
    fi
fi

# Step 3: Pull latest from GitHub (in case of remote changes)
echo ""
echo "📥 Pulling latest from GitHub to NVMe..."
git pull origin main
echo "✓ NVMe updated from GitHub"

# Step 4: Push NVMe to GitHub
echo ""
echo "📤 Pushing NVMe to GitHub..."
git push origin main
echo "✓ GitHub updated from NVMe"

# Step 5: Sync to Desktop
echo ""
echo "💾 Syncing to Desktop backup..."
cd "$DESKTOP_PATH"

# Stash any local changes on Desktop
if [[ -n $(git status --porcelain) ]]; then
    echo "⚠️  Desktop has local changes - stashing..."
    git stash
fi

# Pull from GitHub to Desktop
git pull origin main
echo "✓ Desktop synced from GitHub"

# Step 6: Verification
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  ✅ SYNC COMPLETE"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Current commits:"
echo ""
echo "NVMe (Primary):"
cd "$NVME_PATH"
git log --oneline -3

echo ""
echo "Desktop (Backup):"
cd "$DESKTOP_PATH"
git log --oneline -3

echo ""
echo "GitHub (Remote):"
echo "Both locations now at: $(git rev-parse --short HEAD)"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  💡 Remember: Work from NVMe only!"
echo "  💡 Run this script daily for backup"
echo "═══════════════════════════════════════════════════════════════"
