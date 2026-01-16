# NVMe Development Workflow

**Status:** ✅ Active (January 3, 2026)  
**Primary Location:** `/Volumes/NVMe_990Pro/Staff_Rota_Production_Ready_2025-12-21`  
**Backup Location:** `/Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete`

## Overview

You now work directly on the **NVMe drive** for faster performance, and changes automatically sync to Desktop after each commit.

**Flow:** NVMe (work here) → GitHub → Desktop (backup mirror)

## Quick Start

### Navigate to NVMe
```bash
cd /Volumes/NVMe_990Pro/Staff_Rota_Production_Ready_2025-12-21
```

### Make Your Changes
Edit files as normal using VS Code or any editor.

### Commit Changes

**Option 1: Use the wrapper script (recommended)**
```bash
# With custom message
./nvme_commit.sh "Task 45: Your feature description"

# With auto-timestamp
./nvme_commit.sh
```

**Option 2: Standard Git commands**
```bash
git add -A
git commit -m "Your commit message"
# Push and Desktop sync happen automatically via post-commit hook
```

## What Happens Automatically

When you commit on NVMe:
1. ✅ Code pushed to GitHub
2. ✅ Desktop location syncs via `git fetch && git reset --hard origin/main`
3. ✅ All locations stay in sync

## Logs

View sync activity:
```bash
tail -f ~/Library/Logs/nvme_to_desktop_sync.log
```

## Verify Sync

Check Desktop is synced:
```bash
cd /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
git log --oneline -3
```

Should match your NVMe commits.

## Benefits

- 🚀 **Faster**: NVMe drive = faster file operations, git operations, test runs
- 💾 **Automatic backup**: Desktop stays synced as a local backup
- ☁️ **GitHub sync**: Everything pushed to GitHub automatically
- 🔄 **No manual sync**: Post-commit hook handles everything

## Important Notes

1. **Always work on NVMe** - Desktop is now a read-only mirror
2. **Don't edit on Desktop** - Changes will be overwritten by sync
3. **Desktop hook disabled** - Prevents bidirectional sync conflicts

## Restore Desktop Hook (if needed)

If you want to switch back to Desktop as primary:
```bash
cd /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
mv .git/hooks/post-commit.disabled .git/hooks/post-commit
chmod +x .git/hooks/post-commit
```

Then disable NVMe hook:
```bash
cd /Volumes/NVMe_990Pro/Staff_Rota_Production_Ready_2025-12-21
mv .git/hooks/post-commit .git/hooks/post-commit.disabled
```

## Files Created

- `.git/hooks/post-commit` - Auto-sync hook on NVMe
- `nvme_commit.sh` - Convenient commit wrapper script
- `~/Library/Logs/nvme_to_desktop_sync.log` - Sync log file
