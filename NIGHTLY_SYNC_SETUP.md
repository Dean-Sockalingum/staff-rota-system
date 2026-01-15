# Nightly Auto-Sync Setup Complete ✅

**Created:** December 26, 2025  
**Updated:** January 13, 2026 - Expanded to 5 locations  
**Status:** Active and Running

## What Was Set Up

An automatic nightly sync system that keeps all five Staff Rota locations synchronized:

1. **Desktop** → GitHub (commits & pushes changes)
2. **GitHub** → NVMe 990 Backups (pulls updates)
3. **GitHub** → NVMe 990 Production (pulls updates)
4. **Desktop** → Working dri Future Iterations (rsync copy)
5. **Desktop** → Desktop Future Iterations (rsync copy)

## Sync Schedule

- **Runs:** Every night at **2:00 AM**
- **Method:** macOS launchd (system scheduler)
- **Job Name:** `com.staffrota.nightlysync`

## File Locations

### Sync Script
```
/Users/deansockalingum/Desktop/Staff_Rota_Backups/nightly_sync.sh
```
- Executable bash script that performs the sync
- Commits Desktop changes → Pushes to GitHub → Pulls to NVMe locations

### LaunchAgent Configuration
```
/Users/deansockalingum/Library/LaunchAgents/com.staffrota.nightlysync.plist
```
- macOS scheduler configuration (launchd)
- Triggers script at 2 AM daily

### Log Files
```
Main Log: ~/Library/Logs/staff_rota_sync.log
Stdout: ~/Library/Logs/staff_rota_sync_stdout.log
Stderr: ~/Library/Logs/staff_rota_sync_stderr.log
```

## What Gets Synced

### Location 1: Desktop (Primary Development)
- **Path:** `/Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete`
- **Action:** Auto-commits any changes + pushes to GitHub
- **Commit Message:** "Nightly auto-sync: YYYY-MM-DD HH:MM"

### Location 2: NVMe 990 Backups
- **Path:** `/Volumes/NVMe_990Pro/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete`
- **Action:** Pulls latest from GitHub
- **Fallback:** Auto-resolves conflicts if needed

### Location 3: NVMe 990 Production
- **Path:** `/Volumes/NVMe_990Pro/Staff_Rota_Production_Ready_2025-12-21`
- **Action:** Pulls latest from GitHub
- **Fallback:** Auto-resolves conflicts if needed

### Location 4: Working dri Future Iterations (NEW - Jan 13, 2026)
- **Path:** `/Volumes/Working dri/future iterations/2025-12-12_Multi-Home_Complete`
- **Action:** Rsync copy from Desktop (non-git backup)
- **Purpose:** Staging/iteration folder on external drive
- **Excludes:** .venv, __pycache__, *.pyc, db.sqlite3, .git

### Location 5: Desktop Future Iterations (NEW - Jan 13, 2026)
- **Path:** `/Users/deansockalingum/Desktop/Future iterations/2025-12-12_Multi-Home_Complete`
- **Action:** Rsync copy from Desktop (non-git backup)
- **Purpose:** Local staging/iteration folder
- **Excludes:** .venv, __pycache__, *.pyc, db.sqlite3, .git

## How It Works

**Every night at 2 AM:**

1. Checks Desktop for uncommitted changes
2. If changes exist → commits with timestamp
3. Pushes Desktop → GitHub
4. If NVMe 990 is mounted:
   - Pulls GitHub → NVMe Backups location
   - Pulls GitHub → NVMe Production location
5. If Working dri volume is mounted:
   - Rsyncs Desktop → Working dri Future Iterations
6. If Desktop Future iterations folder exists:
   - Rsyncs Desktop → Desktop Future Iterations
7. Logs all actions to log files

**Safety Features:**
- ✅ Checks if NVMe drive is mounted before syncing
- ✅ Checks if Working dri volume is mounted before syncing
- ✅ Auto-handles merge conflicts (prefers GitHub version)
- ✅ Rsync uses --delete to keep copies identical
- ✅ Excludes virtual environments and compiled files
- ✅ Detailed logging for troubleshooting
- ✅ Commits changes before pulling to avoid data loss

## Manual Commands

### Test the sync now (don't wait for 2 AM)
```bash
/Users/deansockalingum/Desktop/Staff_Rota_Backups/nightly_sync.sh
```

### View sync logs
```bash
# Main detailed log
tail -f ~/Library/Logs/staff_rota_sync.log

# Quick view of last 50 lines
tail -50 ~/Library/Logs/staff_rota_sync.log
```

### Check if job is running
```bash
launchctl list | grep staffrota
```

### Manually trigger the job
```bash
launchctl start com.staffrota.nightlysync
```

### Stop the nightly sync
```bash
launchctl unload ~/Library/LaunchAgents/com.staffrota.nightlysync.plist
```

### Re-enable the nightly sync
```bash
launchctl load ~/Library/LaunchAgents/com.staffrota.nightlysync.plist
```

## Important Notes

### NVMe Drive Considerations
- Script checks if `/Volumes/NVMe_990Pro` exists before syncing
- If drive not mounted → Desktop still syncs to GitHub (safe)
- NVMe locations sync next time drive is mounted

### GitHub Credentials
- Uses existing git credentials (SSH or HTTPS token)
- Must be configured to avoid password prompts
- Verify with: `git config --global credential.helper`

### Conflict Resolution
- Desktop version always wins (pushes first)
- NVMe locations auto-pull and accept GitHub version
- Manual changes on NVMe will be overwritten

## Troubleshooting

### Sync not running?
1. Check if job is loaded: `launchctl list | grep staffrota`
2. Check logs: `cat ~/Library/Logs/staff_rota_sync.log`
3. Test manually: `/Users/deansockalingum/Desktop/Staff_Rota_Backups/nightly_sync.sh`

### Git authentication errors?
```bash
# Verify credentials are stored
git config --global credential.helper store

# Or use SSH instead
cd /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
git remote set-url origin git@github.com:Dean-Sockalingum/staff-rota-system.git
```

### NVMe drive not syncing?
1. Check if drive is mounted: `ls /Volumes/NVMe_990Pro`
2. Verify paths exist in script
3. Check logs for "WARNING: NVMe 990 drive not mounted"

### Change sync time (default is 2 AM)?
Edit the plist file:
```bash
nano ~/Library/LaunchAgents/com.staffrota.nightlysync.plist
# Change <integer>2</integer> under Hour
# Change <integer>0</integer> under Minute
launchctl unload ~/Library/LaunchAgents/com.staffrota.nightlysync.plist
launchctl load ~/Library/LaunchAgents/com.staffrota.nightlysync.plist
```

## Verification

**Current Status:**
- ✅ Script created and executable
- ✅ LaunchAgent installed
- ✅ Job loaded and scheduled
- ✅ Will run next at 2:00 AM

**Next Sync:** Tomorrow at 2:00 AM (or manually trigger now to test)

---

**Created by GitHub Copilot** | December 26, 2025
