# Automatic NVMe Sync Setup

**Status:** ✅ Active  
**Created:** December 30, 2025

## Overview

Your Staff Rota system now automatically syncs to NVMe locations in **two ways**:

1. **Immediately after every commit** (post-commit hook)
2. **Nightly at 2 AM** (existing scheduled sync)

## How It Works

### Immediate Sync (New!)

**Two ways to trigger automatic NVMe sync:**

#### 1. Use the wrapper script (Recommended)
```bash
./commit_and_sync.sh "Your commit message"
```
This automatically runs the sync hook after pushing.

#### 2. Use Git alias
```bash
git pushsync origin main
```
This is a Git alias that pushes and then syncs NVMe.

**What happens:**
1. Pushes your changes to GitHub
2. Runs `.git/hooks/post-push` hook
3. Syncs to `/Volumes/NVMe_990Pro/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete`
4. Syncs to `/Volumes/NVMe_990Pro/Staff_Rota_Production_Ready_2025-12-21`

**Files:**
- Hook: `.git/hooks/post-push` (custom hook, not standard Git)
- Log: `~/Library/Logs/staff_rota_post_push.log`
- Git alias: `pushsync` (configured in `.git/config`)

### Nightly Sync (Existing)

Runs at 2:00 AM every night via macOS launchd.

**Files:**
- Script: `nightly_sync.sh`
- Log: `~/Library/Logs/staff_rota_sync.log`

## Usage Options

### Option 1: Use the Wrapper Script (Recommended)

From the `Staff_Rota_Backups` directory:

```bash
# With custom message
./commit_and_sync.sh "Task 44: Your feature description"

# With auto-generated timestamp message
./commit_and_sync.sh
```

**What it does:**
1. `git add -A` - Stages all changes
2. `git commit -m "Your message"` - Commits
3. `git push origin main` - Pushes to GitHub
4. Syncs both NVMe locations
5. Shows colorful progress output

### Option 2: Git Alias

Use the configured Git alias:

```bash
cd /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete

git add -A
git commit -m "Your commit message"
git pushsync origin main  # ← Pushes AND syncs NVMe automatically
```

### Option 3: Manual Git + Hook

If you use standard `git push`, you can manually trigger the hook:

```bash
cd /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete

git add -A
git commit -m "Your commit message"
git push origin main

# Then manually run the hook:
./.git/hooks/post-push
```

### Option 4: Manual Sync

If you need to sync without committing:

```bash
cd /Users/deansockalingum/Desktop/Staff_Rota_Backups
./nightly_sync.sh
```

## Verification

### Check if NVMe is Synced

```bash
# Check NVMe Backups
cd /Volumes/NVMe_990Pro/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
git log --oneline -3

# Check NVMe Production  
cd /Volumes/NVMe_990Pro/Staff_Rota_Production_Ready_2025-12-21
git log --oneline -3
```

Both should show the same latest commit as Desktop.

### View Sync Logs

```bash
# Post-push hook logs (immediate sync)
tail -f ~/Library/Logs/staff_rota_post_push.log

# Nightly sync logs
tail -f ~/Library/Logs/staff_rota_sync.log
```

## Troubleshooting

### NVMe Not Mounting

If the NVMe drive isn't mounted, syncs are skipped (no error).

**Check logs:**
```bash
grep "not mounted" ~/Library/Logs/staff_rota_post_push.log
```

### Sync Conflicts

If there are conflicts, the sync will fail but won't break your commit.

**Resolution:**
```bash
# Go to the conflicting NVMe location
cd /Volumes/NVMe_990Pro/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete

# Force sync to match GitHub
git fetch origin main
git reset --hard origin/main
```

### Hook Not Running

**Verify hook is executable:**
```bash
ls -la /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete/.git/hooks/post-push
```

Should show `-rwxr-xr-x` (x = executable).

**Re-enable if needed:**
```bash
chmod +x /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete/.git/hooks/post-push
```

## Locations

### Desktop (Primary Development)
```
/Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
```
- **Role:** Primary development location
- **Action:** Commit here, syncs propagate automatically

### NVMe Backups
```
/Volumes/NVMe_990Pro/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
```
- **Role:** Fast NVMe backup
- **Action:** Auto-updated from GitHub

### NVMe Production
```
/Volumes/NVMe_990Pro/Staff_Rota_Production_Ready_2025-12-21
```
- **Role:** Production-ready deployment
- **Action:** Auto-updated from GitHub

## Best Practices

1. **Always work from Desktop location** - Don't edit files directly on NVMe
2. **Use the wrapper script** - `./commit_and_sync.sh "message"` for visual feedback
3. **Check logs if issues arise** - Post-commit log shows immediate sync status
4. **Verify NVMe is mounted** - Before expecting immediate syncs

## Summary

✅ **Immediate sync** after every push (post-push hook)  
✅ **Nightly sync** at 2 AM (scheduled)  
✅ **Manual sync** available anytime  
✅ **Three-location backup** (Desktop → GitHub → 2x NVMe)

**You're now fully protected with real-time and scheduled backups!**
