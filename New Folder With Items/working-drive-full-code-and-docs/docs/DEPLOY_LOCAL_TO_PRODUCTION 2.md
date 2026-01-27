# DEPLOY LOCAL DEMO TO PRODUCTION - Quick Guide

## Option 1: Export Complete Database (Recommended)

### Step 1: Export from Local Demo
```bash
cd /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete

# Export all staff, shifts, and related data
python3 manage.py dumpdata scheduling.User scheduling.Shift scheduling.ShiftType scheduling.Unit scheduling.CareHome \
  --indent 2 \
  --output complete_demo_data.json
```

### Step 2: Copy to Production
```bash
# Upload to production server
scp complete_demo_data.json root@159.65.18.80:/home/staff-rota-system/
```

### Step 3: Load on Production
```bash
# SSH to production
ssh root@159.65.18.80

# Backup current production DB first
cd /home/staff-rota-system
pg_dump staffrota_demo > backup_before_import_$(date +%Y%m%d).sql

# Load complete data
python3 manage.py loaddata complete_demo_data.json

# Verify
python3 manage.py shell -c "
from scheduling.models import User, Shift
print(f'Staff: {User.objects.filter(is_active=True).count()}')
print(f'Shifts: {Shift.objects.count()}')
"
```

---

## Option 2: Direct Database Copy (SQLite → PostgreSQL)

If both use SQLite, even simpler:

```bash
# 1. Copy local demo database to production
scp /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete/db.sqlite3 \
  root@159.65.18.80:/home/staff-rota-system/db_complete_demo.sqlite3

# 2. On production, backup current and swap
ssh root@159.65.18.80
cd /home/staff-rota-system
mv db.sqlite3 db_old_$(date +%Y%m%d).sqlite3
mv db_complete_demo.sqlite3 db.sqlite3

# 3. Restart service
systemctl restart staffrota

# Done!
```

---

## Option 3: Selective Import (Just Missing Staff)

Use the scripts we already prepared:

```bash
# Already done earlier today:
# - staff_export_821.json created ✓
# - import_production_staff.py ready ✓

# Just run the import:
ssh root@159.65.18.80 'cd /home/staff-rota-system && python3 import_production_staff.py'
```

---

## Recommendation for Tomorrow

**Use Option 2** (Direct database copy) because:
- ✅ Fastest (5 minutes)
- ✅ Complete data (staff + 133k shifts)
- ✅ All relationships intact
- ✅ Proven working (local demo runs perfectly)
- ✅ Easy rollback (keep backup)

**Steps:**
1. Backup production DB (2 min)
2. Copy local demo db.sqlite3 to production (1 min)
3. Restart service (1 min)
4. Test login (1 min)

**Total time: 5 minutes** 🚀

---

## Local Demo Details

**Location:** `/Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete/`

**Start Local Demo:**
```bash
cd /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
./demo_start.sh
# Opens at http://127.0.0.1:8001
# Login: admin / admin
```

**Database:** `db.sqlite3` (63MB)
- 813 active staff
- 133,658 shifts
- All 5 homes configured
- Complete 2026-2027 coverage

This is your **golden copy** - working, tested, complete!
