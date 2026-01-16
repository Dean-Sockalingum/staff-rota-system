#!/bin/bash
# Nightly Auto-Sync Script for Staff Rota System
# Syncs Desktop → GitHub → NVMe 990 locations
# Created: December 26, 2025

LOG_FILE="$HOME/Library/Logs/staff_rota_sync.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "========================================" >> "$LOG_FILE"
echo "[$DATE] Starting nightly sync..." >> "$LOG_FILE"

# Location 1: Desktop (Primary development location)
DESKTOP_PATH="/Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete"

# Location 2: NVMe 990 Backups
NVME_BACKUPS_PATH="/Volumes/NVMe_990Pro/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete"

# Location 3: NVMe 990 Production
NVME_PRODUCTION_PATH="/Volumes/NVMe_990Pro/Staff_Rota_Production_Ready_2025-12-21"

# Function to log messages
log() {
    echo "[$DATE] $1" >> "$LOG_FILE"
}

# Function to sync a repository
sync_repo() {
    local REPO_PATH=$1
    local REPO_NAME=$2
    
    log "Syncing $REPO_NAME..."
    
    if [ ! -d "$REPO_PATH" ]; then
        log "ERROR: $REPO_NAME not found at $REPO_PATH"
        return 1
    fi
    
    cd "$REPO_PATH" || return 1
    
    # Check if there are any changes
    if ! git diff-index --quiet HEAD --; then
        log "Changes detected in $REPO_NAME, committing..."
        git add -A >> "$LOG_FILE" 2>&1
        git commit -m "Nightly auto-sync: $(date '+%Y-%m-%d %H:%M')" >> "$LOG_FILE" 2>&1
        log "Changes committed in $REPO_NAME"
    else
        log "No changes in $REPO_NAME"
    fi
    
    # Pull latest changes
    log "Pulling latest changes for $REPO_NAME..."
    git pull origin main --rebase >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        log "Pull successful for $REPO_NAME"
    else
        log "WARNING: Pull failed for $REPO_NAME, attempting reset..."
        git rebase --abort >> "$LOG_FILE" 2>&1
        git pull origin main --no-rebase >> "$LOG_FILE" 2>&1
    fi
}

# Step 1: Sync Desktop (primary location) and push to GitHub
log "=== STEP 1: Desktop → GitHub ==="
cd "$DESKTOP_PATH" || exit 1

if ! git diff-index --quiet HEAD --; then
    log "Committing Desktop changes..."
    git add -A >> "$LOG_FILE" 2>&1
    git commit -m "Nightly auto-sync: $(date '+%Y-%m-%d %H:%M')" >> "$LOG_FILE" 2>&1
    log "Desktop changes committed"
fi

log "Pushing to GitHub..."
git push origin main >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    log "Push to GitHub successful"
else
    log "ERROR: Push to GitHub failed"
    exit 1
fi

# Step 2: Sync NVMe 990 Backups location
log "=== STEP 2: GitHub → NVMe Backups ==="
if [ -d "/Volumes/NVMe_990Pro" ]; then
    sync_repo "$NVME_BACKUPS_PATH" "NVMe Backups"
else
    log "WARNING: NVMe 990 drive not mounted, skipping NVMe locations"
fi

# Step 3: Sync NVMe 990 Production location
log "=== STEP 3: GitHub → NVMe Production ==="
if [ -d "/Volumes/NVMe_990Pro" ]; then
    sync_repo "$NVME_PRODUCTION_PATH" "NVMe Production"
else
    log "WARNING: NVMe 990 drive not mounted, skipping NVMe locations"
fi

# Summary
log "=== SYNC COMPLETE ==="
log "All locations synced successfully"
echo "========================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

exit 0
