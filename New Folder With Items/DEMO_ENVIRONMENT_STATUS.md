# Demo Environment Status - January 19, 2026

## URGENT: Both Demo Environments Broken

### Summary
**STATUS**: ❌ NO WORKING DEMOS AVAILABLE FOR PRESENTATION

Both production and local demo environments are currently non-functional with different critical issues.

---

## Environment 1: Production Server (demo.therota.co.uk)
**Status**: ❌ BROKEN
**URL**: http://demo.therota.co.uk
**Server**: DigitalOcean 159.65.18.80

### Issues
1. ❌ `/performance-kpis/` → 500 Internal Server Error  
2. ❌ Database tables missing (migrations not run)
3. ❌ AUTH_USER_MODEL error ('scheduling.User' doesn't exist)
4. ❌ Gunicorn service not found

### Root Cause
`deploy_to_production.sh` only uploads demo_export_cleaned.json (data) - does NOT upload application code

### Fix Required
- Full code redeployment (1-2 hours)
- See: PRODUCTION_SYNC_FIX.md
- **RECOMMENDATION**: Not worth fixing for presentation - too risky, too time-consuming

---

## Environment 2: Local PostgreSQL Demo (2025-12-12_Multi-Home_Complete)
**Status**: ⚠️ PARTIALLY FIXED - DATABASE EMPTY
**Path**: `/Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete/`

### Issues
1. ✅ FIXED: Missing `sentence_transformers` package → Installed
2. ✅ FIXED: Migration dependency errors → Resolved (faked duplicates)
3. ✅ FIXED: All migrations applied successfully
4. ❌ **CRITICAL**: Database is completely EMPTY (no data loaded)
5. ❌ Cannot load `complete_demo_export.json` → Field length error

### Database Status
```
Care Homes: 0
Units: 0  
Staff: 0
Shifts: 0
Executive Dashboards: 0
```

### Error Loading Data
```
django.db.utils.DataError: Problem installing fixture 'complete_demo_export.json': 
Could not load scheduling.User(pk=000001): value too long for type character varying(1)
```

### Next Steps to Fix
**Option A: Fix Data Load (30-60 min)**
1. Identify field with varchar(1) causing error
2. Temporarily alter field length
3. Load complete_demo_export.json
4. Verify all data loaded correctly
5. Test server: `python manage.py runserver 8001`

**Option B: Find Working Environment (5-15 min)**
1. Search for other working demos on machine:
   ```bash
   find /Users/deansockalingum/Desktop/Staff_Rota_Backups -name "db.sqlite3" -type f
   ```
2. Look for SQLite-based demos (simpler, more portable)
3. Verify database has data before starting server

**Option C: Fresh SQLite Setup (60-90 min)**
1. Copy 2025-12-12_Multi-Home_Complete to new directory
2. Edit settings.py to use SQLite instead of PostgreSQL
3. Delete all migrations, recreate fresh
4. Load demo data into SQLite
5. Test and verify

---

## Environment 3: Parent Directory (Staff_Rota_Backups/)
**Status**: ❌ BROKEN - PostgreSQL Missing
**Path**: `/Users/deansockalingum/Desktop/Staff_Rota_Backups/`

### Issues
- Tries to use PostgreSQL (no venv, using system Python)
- Missing psycopg2 package
- db.sqlite3 is just a symlink (not real database)
- Not suitable for presentation

---

## Presentation Materials Ready
✅ **AUTOMATION_WORKFLOW_DIAGRAMS.docx** - Complete with all 9 workflows
✅ **AUTOMATION_WORKFLOW_DIAGRAMS.md** - Markdown source
✅ Documentation includes:
   - Workflow 6: Annual Leave Auto-Approval (81% instant approval)
   - Workflow 7: Care Inspectorate Evidence Pack (40h → 2-3h)
   - 8 other complete automated workflows
   - Time savings: 20-30 hours/week
   - Annual savings: £52K-78K

---

## Immediate Action Required

### RECOMMENDED: Option B (Find Working Environment)
**Why**: Fastest path to working demo (5-15 minutes vs 30-90 minutes)

**Execute Now**:
```bash
cd /Users/deansockalingum/Desktop/Staff_Rota_Backups

# Find all SQLite databases
find . -name "db.sqlite3" -type f -ls

# Check each one for data
for db in $(find . -name "db.sqlite3" -type f); do
  echo "=== $db ==="
  sqlite3 "$db" "SELECT COUNT(*) FROM scheduling_carehome;" 2>&1 | head -1
done
```

### If No Working Environment Found: Option A (Fix Current PostgreSQL Demo)

**Step 1: Identify Problem Field**
```bash
cd /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
source venv/bin/activate

# Check User model fields
python manage.py inspectdb scheduling_user | grep "varchar(1)"
```

**Step 2: Fix Field Length**
Create migration to increase field size or alter model definition

**Step 3: Load Data**
```bash
python manage.py loaddata complete_demo_export.json
```

**Step 4: Verify & Start**
```bash
python manage.py shell -c "from scheduling.models import User; print(f'Staff: {User.objects.count()}')"
python manage.py runserver 8001
```

---

## Test Credentials (Once Working)
```
SAP Number: 000541 (or field name may be 'sap')
Password: Greenball99##
URL: http://127.0.0.1:8001/
```

---

## Timeline Estimate

| Option | Time | Risk | Success Probability |
|--------|------|------|-------------------|
| **Option B: Find working demo** | 5-15 min | Low | 70% (if one exists) |
| **Option A: Fix PostgreSQL data** | 30-60 min | Medium | 85% |
| **Option C: Fresh SQLite install** | 60-90 min | Medium | 95% |
| **Production server fix** | 1-2 hours | High | 60% (SSH unstable) |

---

## Current Status (19 Jan 2026, 14:30)

✅ sentence_transformers installed
✅ All migrations applied
✅ Django can start
✅ Documentation ready for presentation
❌ Database completely empty
❌ Data load failing on field length
⏳ **NEXT**: Search for existing working demo OR fix data load

---

**DECISION NEEDED**: Choose Option A, B, or C and execute immediately
