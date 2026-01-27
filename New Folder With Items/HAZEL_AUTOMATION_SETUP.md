# Hazel Automation Setup Guide
**NVMe (Fast Working Drive) + Desktop (Cold Storage Archive)**

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  NVMe_990Pro (FAST - Active Development)                │
│  - Active development files                             │
│  - Current Git repositories                             │
│  - Files modified in last 30 days                       │
│  - Documents being actively edited                      │
│  Capacity: ~500GB SSD                                   │
└─────────────────────────────────────────────────────────┘
                    ↓ (Auto-archive after 30 days)
┌─────────────────────────────────────────────────────────┐
│  Working Drive (OWC Envoy - Cold Storage)               │
│  - Archived project versions                            │
│  - Historical backups                                   │
│  - Completed documentation                              │
│  - Files not accessed in 30+ days                       │
│  Capacity: 1.7TB (only 1% used - plenty of space!)     │
└─────────────────────────────────────────────────────────┘
                    ↑
┌─────────────────────────────────────────────────────────┐
│  Desktop (Laptop Internal - CLEAN)                      │
│  - Only current session files                           │
│  - Quick access shortcuts                               │
│  - Temporary working files                              │
│  Auto-cleaned daily → Keep laptop storage free          │
└─────────────────────────────────────────────────────────┘
```

---

## Hazel Rules Setup

### Rule Set 1: NVMe Working Directory
**Monitor**: `/Volumes/NVMe_990Pro/Staff_Rota_Backups/`

#### Rule 1.1: Archive Old Project Folders
**Name**: "Archive to Working Drive - Inactive Projects"  
**Conditions**:
- Kind is Folder
- Date Last Matched is not in the last 30 days
- Name does not contain "2025-12-12_Multi-Home_Complete" (current active project)
- Name matches pattern: `202*` (dated backup folders)

**Actions**:
1. Move to folder: `/Volumes/Working dri/Staff_Rota_Backups/ARCHIVED_PROJECTS/`
2. Add Finder Tag: "Archived"
3. Add Spotlight Comment: "Auto-archived by Hazel on {date}"

---

#### Rule 1.2: Archive Old Documentation Files
**Name**: "Archive Old Documentation"  
**Conditions**:
- Extension is md
- Date Last Opened is not in the last 45 days
- Name does not contain "PHASE_1" (keep current phase docs active)
- Name does not contain "ROADMAP"

**Actions**:
1. Move to folder: `/Volumes/Working dri/Staff_Rota_Backups/ARCHIVED_DOCS/`
2. Add Finder Tag: "Cold Storage"
3. Color Label: Gray

---

#### Rule 1.3: Clean Up .DS_Store Files
**Name**: "Remove .DS_Store Files"  
**Conditions**:
- Name is .DS_Store
- Date Last Modified is not in the last 7 days

**Actions**:
1. Move to Trash

---

### Rule Set 3: Working Drive Archive Management
**Monitor**: `/Volumes/Working dri/Staff_Rota_Backups/`

#### Rule 3.1: Compress Old Archives
**Monitor**: `/Volumes/NVMe_990Pro/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete/`

#### Rule 2.1: Auto-Backup Modified Files
**Name**: "Backup Modified Python Files to Working Drive"  
**Conditions**:
- Extension is py
- Date Last Modified is in the last 1 hour
- Size is greater than 1 KB

**Actions**:
1. Run shell script:
```bash
#!/bin/bash
SOURCE="$1"
DEST="/Volumes/Working dri/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete/$(basename "$SOURCE")"
cp "$SOURCE" "$DEST"
echo "Backed up: $(basename "$SOURCE") at $(date)" >> "/Volumes/Working dri/Staff_Rota_Backups/hazel_backup_log.txt"
```

---

#### Rule 2.2: Organize Screenshots
**Name**: "Move Screenshots to Docs Folder"  
**Conditions**:
- Name starts with "Screenshot"
- Date Added is in the last 7 days

**Actions**:
1. Move to folder: `/Volumes/NVMe_990Pro/Staff_Rota_Backups/SCREENSHOTS/`
2. Rename: `Screenshot_{date}_{time}.png`

---

### Rule Set 3: Desktop Archive Management
**Monitor**: `~/Desktop/Staff_Rota_Backups/`

#### Rule 3.1: Compress Old Archives
**Name**: "Compress Old Project Folders"  
**Conditions**:
- Kind is Folder
- Date Last Opened is not in the last 90 days
- Size is greater than 100 MB
- Name does not end with .zip

**Actions**:
1. Run shell script:
```bash
#!/bin/bash
cd "$(dirname "$1")"
FOLDER="$(basename "$1")"
zip -r "${FOLDER}_$(date +%Y%m%d).zip" "$FOLDER"
mv "${FOLDER}_$(date +%Y%m%d).zip" "$HOME/Desktop/Staff_Rota_Backups/COMPRESSED_ARCHIVES/"
rm -rf "$1"
```
2. Add Spotlight Comment: "Compressed to save space on {date}"

---

#### Rule 3.2: Tag Documentation by Phase
**Name**: "Auto-Tag Phase Documents"  
**Conditions**:
- Extension is md
- Name contains "PHASE_"

**Actions**:
1. If Name contains "PHASE_1":
   - Add Finder Tag: "Phase 1"
   - Color Label: Green
2. If Name contains "PHASE_2":
   - Add Finder Tag: "Phase 2"
   - Color Label: Blue
3. If Name contains "PHASE_3":
   - Add Finder Tag: "Phase 3"
   - Color Label: Purple

---

### Rule Set 4: Git Repository Maintenance
**Monitor**: `/Volumes/NVMe_990Pro/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete/`

#### Rule 4.1: Daily Git Sync to Working Drive
**Name**: "Daily Git Backup to Working Drive"  
**Conditions**:
- Kind is Folder
- Name is ".git"
- Date Last Modified is in the last 1 day

**Actions**:
1. Run shell script:
```bash
#!/bin/bash
# Daily sync from NVMe to Working Drive
NVME_REPO="/Volumes/NVMe_990Pro/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete"
WORKING_REPO="/Volumes/Working dri/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete"

cd "$NVME_REPO"
git fetch origin

cd "$WORKING_REPO"
git fetch origin
git reset --hard origin/main

echo "Git repos synced at $(date)" >> "/Volumes/Working dri/Staff_Rota_Backups/hazel_git_sync_log.txt"
```

---

## Hazel Configuration Steps

### Step 1: Install Hazel Rules

1. **Open Hazel Preferences**:
   - System Preferences → Hazel

2. **Add Monitored Folders**:
   - Click "+" → Add `/Volumes/NVMe_990Pro/Staff_Rota_Backups/` (Active work)
   - Click "+" → Add `/Volumes/Working dri/Staff_Rota_Backups/` (Cold storage)
   - Click "+" → Add `/Volumes/NVMe_990Pro/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete/` (Current project)

3. **Create Rules**:
   - For each folder, click "+" to add new rule
   - Copy conditions and actions from sections above

---

### Step 2: Create Required Destination Folders

```bash
# Create archive folders on Working Drive (1.7TB external)
mkdir -p "/Volumes/Working dri/Staff_Rota_Backups/ARCHIVED_PROJECTS"
mkdir -p "/Volumes/Working dri/Staff_Rota_Backups/ARCHIVED_DOCS"
mkdir -p "/Volumes/Working dri/Staff_Rota_Backups/COMPRESSED_ARCHIVES"
mkdir -p "/Volumes/Working dri/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete"

# Create organization folders on NVMe (fast active work)
mkdir -p /Volumes/NVMe_990Pro/Staff_Rota_Backups/SCREENSHOTS
mkdir -p /Volumes/NVMe_990Pro/Staff_Rota_Backups/TEMP_WORK
mkdir -p /Volumes/NVMe_990Pro/Staff_Rota_Backups/DAILY_BACKUPS

# Create log files on Working Drive
touch "/Volumes/Working dri/Staff_Rota_Backups/hazel_backup_log.txt"
touch "/Volumes/Working dri/Staff_Rota_Backups/hazel_git_sync_log.txt"
```

---

### Step 3: Configure Hazel Settings

**General Settings**:
- [x] Run rules in the background
- [x] Monitor folders even when not logged in
- [x] Show Hazel menu in menu bar

**Advanced Settings**:
- **Trash**: Move to Trash (not delete immediately)
- **Notifications**: Show notification for important actions
- **Log**: Keep logs for 30 days

---

## Workflow Examples

### Example 1: Active Development on NVMe

**Scenario**: You're actively coding on NVMe

```
09:00 - Edit views_cost_analysis.py on NVMe
09:05 - Hazel detects change, backs up to Desktop (Rule 2.1)
09:30 - Git commit and push
10:00 - Hazel syncs .git folder to Desktop (Rule 4.1)
```

**Result**: Fast NVMe for active work, Desktop has backup copy

---

### Example 2: Archive Old Project

**Scenario**: Project from November 2025 hasn't been touched in 45 days

```
Day 45 - Hazel checks last access date
        ↓
        Rule 1.1 triggers: "Archive to Desktop - Inactive Projects"
        ↓
        Folder moved to ~/Desktop/Staff_Rota_Backups/ARCHIVED_PROJECTS/
        ↓
        Tagged "Archived", Gray label
```

**Result**: NVMe stays clean, old projects archived to Desktop

---

### Example 3: Documentation Lifecycle

**Scenario**: PHASE_1_*.md files completed

```
Week 1: Active editing on NVMe → Hazel monitors
Week 2: Still referenced → Stays on NVMe
Week 6: Not opened in 45 days
        ↓
        Rule 1.2 triggers: "Archive Old Documentation"
        ↓
        Moved to Desktop/ARCHIVED_DOCS/
        ↓
        Tagged "Cold Storage"
```

**Result**: Active docs on fast NVMe, archived docs on Desktop

---

## Smart Folder Views

### Create Smart Folders for Quick Access

**Smart Folder 1: Recent Work (Last 7 Days)**
- Location: `/Volumes/NVMe_990Pro/`
- Criteria:
  - Date Last Opened is in the last 7 days
  - Kind is not Folder
  - Size is greater than 1 KB

**Smart Folder 2: Active Python Files**
- Location: `/Volumes/NVMe_990Pro/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete/`
- Criteria:
  - Extension is py
  - Date Last Modified is in the last 14 days

**Smart Folder 3: All Phase 1 Docs (Both Drives)**
- Location: Search entire Mac
- Criteria:
  - Extension is md
  - Name contains "PHASE_1"

---

## Maintenance Schedule

### Daily (Automated by Hazel)
- ✅ Backup modified Python files to Desktop
- ✅ Sync Git repositories
- ✅ Clean up .DS_Store files
- ✅ Move screenshots to organized folder

### Weekly (Manual Review)
- [ ] Check `hazel_backup_log.txt` for any issues
- [ ] Review archived files on Desktop
- [ ] Verify NVMe has <80% capacity

### Monthly (Automated + Manual)
- ✅ Compress old archives (90+ days)
- [ ] Delete compressed archives >6 months old
- [ ] Backup Desktop to external drive

---

## Performance Benefits

### Before Hazel Automation
```
NVMe:    Mixed files (active + old) → Cluttered, hard to find
Desktop: Random backups → No organization
Sync:    Manual → Forget to backup
```

### After Hazel Automation
```
NVMe:    Only active files (<30 days) → Fast, organized
Desktop: Systematic archive → Easy retrieval
Sync:    Automatic hourly → Zero data loss risk
```

**Estimated Time Savings**: 2-3 hours/week on file organization

---

## Advanced Rules (Optional)

### Rule: Auto-Commit Documentation Changes
**Name**: "Auto-Commit Markdown Changes"  
**Monitor**: `/Volumes/NVMe_990Pro/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete/`  
**Conditions**:
- Extension is md
- Date Last Modified is in the last 5 minutes
- Name does not contain "temp"

**Actions**:
```bash
#!/bin/bash
cd "/Volumes/NVMe_990Pro/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete"
FILE="$1"
git add "$FILE"
git commit -m "Auto-commit: Updated $(basename "$FILE")"
# Don't auto-push, let user review commits
```

---

### Rule: Smart Backup by File Type
**Name**: "Priority Backup: Code Files"  
**Conditions**:
- Extension is py or js or ts
- Date Last Modified is in the last 30 minutes

**Actions**:
1. Copy to Desktop backup folder
2. Also copy to NVMe/DAILY_BACKUPS/
3. Keep 7 versions (rotate daily)

Script:
```bash
#!/bin/bash
SOURCE="$1"
FILENAME=$(basename "$SOURCE")
DATE=$(date +%Y%m%d_%H%M)
BACKUP_DIR="/Volumes/NVMe_990Pro/Staff_Rota_Backups/DAILY_BACKUPS"

cp "$SOURCE" "$BACKUP_DIR/${FILENAME%.py}_${DATE}.py"

# Keep only last 7 versions
ls -t "$BACKUP_DIR"/"${FILENAME%.py}_"* | tail -n +8 | xargs rm -f
```

---

## Troubleshooting

### Issue: Hazel Not Running Rules
**Solution**:
1. Check System Preferences → Security & Privacy → Full Disk Access
2. Add Hazel to allowed apps
3. Restart Hazel: `killall Hazel && open -a Hazel`

### Issue: Files Not Moving to Desktop
**Solution**:
1. Verify destination folders exist
2. Check permissions: `ls -la ~/Desktop/Staff_Rota_Backups/`
3. Review Hazel logs: Hazel → Info → Show Log

### Issue: Git Sync Failing
**Solution**:
1. Check Git credentials: `git config --list`
2. Verify remote: `git remote -v`
3. Manual sync: `cd [repo] && git fetch && git status`

---

## Quick Reference Commands

```bash
# View Hazel backup log
tail -f ~/Desktop/hazel_backup_log.txt

# Check NVMe capacity
df -h /Volumes/NVMe_990Pro

# Find files modified today on NVMe
find /Volumes/NVMe_990Pro/Staff_Rota_Backups -type f -mtime 0

# List archived projects on Desktop
ls -lht ~/Desktop/Staff_Rota_Backups/ARCHIVED_PROJECTS/

# Manually trigger Hazel on folder
hazelctl run /Volumes/NVMe_990Pro/Staff_Rota_Backups/

# Check Git sync status
cd /Volumes/NVMe_990Pro/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete && git status
cd ~/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete && git status
```

---

## Summary

**Setup Complete**:
- ✅ NVMe = Fast working drive (active files <30 days)
- ✅ Desktop = Cold storage archive (files >30 days)
- ✅ Automatic hourly backups
- ✅ Git sync between drives
- ✅ Smart organization by file type and age
- ✅ Compression of old archives

**Expected Results**:
- 2-3 hours/week saved on file management
- Zero data loss (automatic backups)
- Always work on fastest drive (NVMe)
- Easy access to archived files when needed

**Next Steps**:
1. Run the folder creation script above
2. Configure Hazel rules from this guide
3. Test with a few files first
4. Monitor logs for 1 week
5. Adjust timing thresholds as needed

---

**Status**: Ready to implement  
**Estimated Setup Time**: 30 minutes  
**Maintenance**: <5 minutes/week
