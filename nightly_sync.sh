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

# Location 4: Working dri Volume - Future Iterations
WORKING_DRI_PATH="/Volumes/Working dri/future iterations/2025-12-12_Multi-Home_Complete"

# Location 5: Desktop Future Iterations
DESKTOP_FUTURE_PATH="/Users/deansockalingum/Desktop/Future iterations/2025-12-12_Multi-Home_Complete"

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

# Step 4: Sync Working dri Volume - Future Iterations
log "=== STEP 4: GitHub → Working dri Future Iterations ==="
if [ -d "/Volumes/Working dri" ]; then
    # Use rsync for external volume to avoid git complexity
    log "Syncing to Working dri volume..."
    rsync -av --delete --exclude='.venv' --exclude='__pycache__' --exclude='*.pyc' --exclude='db.sqlite3' --exclude='staticfiles' --exclude='.git/objects' \
        "$DESKTOP_PATH/" "$WORKING_DRI_PATH/" >> "$LOG_FILE" 2>&1
    if [ $? -eq 0 ]; then
        log "Working dri sync successful"
    else
        log "WARNING: Working dri sync failed"
    fi
else
    log "WARNING: Working dri volume not mounted, skipping"
fi

# Step 5: Sync Desktop Future Iterations
log "=== STEP 5: Desktop → Desktop Future Iterations ==="
if [ -d "/Users/deansockalingum/Desktop/Future iterations" ]; then
    # Use rsync for backup copy
    log "Syncing to Desktop Future Iterations..."
    rsync -av --delete --exclude='.venv' --exclude='__pycache__' --exclude='*.pyc' --exclude='db.sqlite3' --exclude='staticfiles' --exclude='.git/objects' \
        "$DESKTOP_PATH/" "$DESKTOP_FUTURE_PATH/" >> "$LOG_FILE" 2>&1
    if [ $? -eq 0 ]; then
        log "Desktop Future Iterations sync successful"
    else
        log "WARNING: Desktop Future Iterations sync failed"
    fi
else
    log "WARNING: Desktop Future Iterations folder not found, skipping"
fi

# Summary
log "=== SYNC COMPLETE ==="
log "All 5 locations synced successfully:"
log "  1. Desktop → GitHub (git push)"
log "  2. GitHub → NVMe 990 Backups (git pull)"
log "  3. GitHub → NVMe 990 Production (git pull)"
log "  4. Desktop → Working dri Future Iterations (rsync)"
log "  5. Desktop → Desktop Future Iterations (rsync)"
echo "========================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

exit 0
