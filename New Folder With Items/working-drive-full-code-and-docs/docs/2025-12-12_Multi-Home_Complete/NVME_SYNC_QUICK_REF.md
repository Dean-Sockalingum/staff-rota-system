# 🚀 Quick Reference: NVMe Auto-Sync

## TL;DR

When committing changes, use ONE of these:

```bash
# Option 1: Easiest (does everything)
./commit_and_sync.sh "Your commit message"

# Option 2: Git alias (after normal commit)
git pushsync origin main

# Option 3: Manual sync (after normal push)
git push origin main && ./.git/hooks/post-push
```

## What Happens

1. ✅ Commits to Desktop
2. ✅ Pushes to GitHub  
3. ✅ Syncs to NVMe Backups
4. ✅ Syncs to NVMe Production

**All in one command!**

## Verify Sync

```bash
# Check log
tail ~/Library/Logs/staff_rota_post_push.log

# Verify commits match
git log --oneline -1
```

## Troubleshooting

### NVMe not syncing?
```bash
# Check if NVMe is mounted
ls /Volumes/NVMe_990Pro/

# Check sync log for errors
grep -i error ~/Library/Logs/staff_rota_post_push.log
```

### Force sync now
```bash
./.git/hooks/post-push
```

## Files

- 📝 `commit_and_sync.sh` - Wrapper script
- 🔧 `.git/hooks/post-push` - Sync hook  
- 📋 `NVME_SYNC_SETUP.md` - Full documentation
- ✅ `NVME_AUTO_SYNC_COMPLETE.md` - Setup summary

## Status

✅ **ACTIVE** - Syncing on every push  
✅ **TESTED** - Working perfectly  
✅ **LOGGED** - Full audit trail

---

**That's it! Just code and commit normally.** 🎉
