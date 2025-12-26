# 🔄 Daily Workflow - NVMe Primary, Desktop Backup

**Last Updated:** 26 December 2025  
**Primary Workspace:** `/Volumes/NVMe_990Pro/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete`  
**Backup Workspace:** `/Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete`

---

## ✅ Daily Workflow

### **ALWAYS Work from NVMe:**

```bash
cd /Volumes/NVMe_990Pro/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
```

### **Start Development:**

```bash
# 1. Navigate to NVMe
cd /Volumes/NVMe_990Pro/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete

# 2. Pull latest (if working across machines)
git pull origin main

# 3. Start Django server
python3 manage.py runserver
```

### **During Development:**

```bash
# Make changes on NVMe
# Test your changes
# Commit regularly

git add .
git commit -m "Your commit message"
```

### **End of Day - Sync to Desktop Backup:**

```bash
# Run the daily sync script (from NVMe)
./sync_to_desktop.sh
```

**What this does:**
1. ✅ Checks for uncommitted changes on NVMe
2. ✅ Pulls latest from GitHub to NVMe (if needed)
3. ✅ Pushes NVMe changes to GitHub
4. ✅ Syncs GitHub to Desktop (backup)
5. ✅ Verifies all locations match

---

## 📋 Quick Commands

### Check NVMe Status
```bash
cd /Volumes/NVMe_990Pro/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
git status
git log --oneline -5
```

### Run Tests
```bash
cd /Volumes/NVMe_990Pro/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
python3 test_pitch_demo.py          # System integrity
python3 test_task10_nlp_interface.py # Task 10 tests
```

### Django Server
```bash
cd /Volumes/NVMe_990Pro/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
python3 manage.py runserver
```

### Manual Sync (if needed)
```bash
# On NVMe
cd /Volumes/NVMe_990Pro/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
git push origin main

# On Desktop
cd /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
git pull origin main
```

---

## ⚠️ Important Rules

1. **NEVER edit files on Desktop** - Desktop is backup only
2. **ALWAYS work from NVMe** - NVMe is the source of truth
3. **Commit regularly** - Don't lose work
4. **Run sync daily** - Keep Desktop backup current
5. **Test before committing** - Run tests to catch issues

---

## 🔧 Troubleshooting

### "NVMe not mounted"
```bash
# Check if NVMe is mounted
ls /Volumes/

# If not mounted, connect the drive and try again
```

### "Uncommitted changes" during sync
```bash
# The sync script will prompt you to commit
# Or manually commit first:
cd /Volumes/NVMe_990Pro/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
git add .
git commit -m "Your message"
./sync_to_desktop.sh
```

### "Desktop has changes"
```bash
# Desktop should never have changes (backup only)
# If it does, the sync script will stash them
# Or manually discard:
cd /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
git checkout .
git pull origin main
```

### Verify sync worked
```bash
# Check both locations have same commit:
cd /Volumes/NVMe_990Pro/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
git log --oneline -1

cd /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
git log --oneline -1

# Should show identical commit hashes
```

---

## 📊 Current Status

**All locations synced at commit:** `2b30961`

✅ NVMe: Primary workspace (2b30961)  
✅ Desktop: Backup (2b30961)  
✅ GitHub: Remote (2b30961)

**Phase 3 Progress:**
- ✅ Task 10: Natural Language Query Interface (75% tests pass)
- ⏳ Task 11: Contextual Learning from Feedback (next)
- ⏳ Task 12: Multi-Modal Input Processing
- ⏳ Task 13: Predictive Anomaly Detection
- ⏳ Task 14: Phase 3 Integration Testing

**Cumulative ROI:** £320,300/year (73% of £441,400 goal)

---

## 🚀 Next Steps

1. ✅ Continue working from NVMe
2. ✅ Implement Task 11 (Contextual Learning)
3. ✅ Run `./sync_to_desktop.sh` at end of day
4. ✅ Keep Desktop as read-only backup

---

*Script Location:* `/Volumes/NVMe_990Pro/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete/sync_to_desktop.sh`  
*Usage:* `./sync_to_desktop.sh` (from NVMe directory)
