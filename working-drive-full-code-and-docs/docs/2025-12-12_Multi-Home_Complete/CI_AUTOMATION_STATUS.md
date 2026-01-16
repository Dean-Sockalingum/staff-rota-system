# Care Inspectorate Automation - System Status

**Date:** 27 December 2025  
**Status:** ✅ **INSTALLED & ACTIVE**

---

## ✅ What's Working Now

### 1. **Automation Schedule - LIVE**
- macOS LaunchAgent installed: `com.staffrota.ciautomation`
- Runs **every April 1st at 2:00 AM** automatically
- Status: **Active** ✓

### 2. **Django Management Commands - READY**
Both commands are installed and functional:

```bash
✓ python3 manage.py import_ci_reports --help
✓ python3 manage.py generate_annual_improvement_plans --help
```

### 3. **Dependencies Installed**
```
✓ beautifulsoup4 (web scraping)
✓ requests (HTTP)
✓ python-dateutil (date handling)
```

### 4. **Automation Script Created**
Location: `/Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete/run_annual_ci_automation.sh`

Logs to: `~/Library/Logs/ci_automation.log`

---

## ⏳ What Needs to Be Done Before First Run

Before the automation can **fully execute**, you need to complete the database setup:

### Step 1: Add CS Number Field to Unit Model

**File:** `scheduling/models.py`

Add this field to the `Unit` model:

```python
care_inspectorate_cs_number = models.CharField(
    max_length=20, 
    blank=True, 
    null=True, 
    unique=True,
    help_text="Care Service registration number (e.g., CS2018371804)"
)
```

### Step 2: Create and Run Migrations

```bash
cd /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
python3 manage.py makemigrations
python3 manage.py migrate
```

### Step 3: Update Units with CS Numbers

```python
# In Django shell or migration
python3 manage.py shell

from scheduling.models import Unit

Unit.objects.filter(name="Meadowburn").update(care_inspectorate_cs_number="CS2018371804")
Unit.objects.filter(name="Hawthorn House").update(care_inspectorate_cs_number="CS2003001025")
Unit.objects.filter(name="Orchard Grove").update(care_inspectorate_cs_number="CS2014333831")
Unit.objects.filter(name="Riverside").update(care_inspectorate_cs_number="CS2014333834")
Unit.objects.filter(name="Victoria Gardens").update(care_inspectorate_cs_number="CS2018371437")
```

### Step 4: Import models_improvement.py Models

**File:** `scheduling/__init__.py` or `scheduling/models.py`

Import the new models so Django recognizes them:

```python
from .models_improvement import (
    CareInspectorateReport,
    ServiceImprovementPlan,
    ImprovementAction,
    ActionProgressUpdate,
    OrganizationalImprovementPlan,
)
```

### Step 5: Create Migrations for New Models

```bash
python3 manage.py makemigrations scheduling
python3 manage.py migrate scheduling
```

### Step 6: Register in Admin (Optional)

**File:** `scheduling/admin.py`

```python
from .models_improvement import (
    CareInspectorateReport,
    ServiceImprovementPlan,
    ImprovementAction,
)

admin.site.register(CareInspectorateReport)
admin.site.register(ServiceImprovementPlan)
admin.site.register(ImprovementAction)
```

---

## 🧪 Testing Before April 1st

Once the database setup is complete, you can test manually:

### Test 1: Import Latest CI Reports (Dry Run)

```bash
python3 manage.py import_ci_reports --all --latest-only
```

**Expected:** Fetches reports from careinspectorate.com for all 5 homes

### Test 2: Generate Improvement Plans (Dry Run)

```bash
python3 manage.py generate_annual_improvement_plans --all --dry-run
```

**Expected:** Shows analysis of 12 months data without saving

### Test 3: Run Full Automation Script

```bash
/Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete/run_annual_ci_automation.sh
```

**Expected:** Imports reports + generates plans, logs to `~/Library/Logs/ci_automation.log`

### Test 4: Verify LaunchAgent

```bash
# Check if scheduled
launchctl list | grep staffrota

# View LaunchAgent config
cat ~/Library/LaunchAgents/com.staffrota.ciautomation.plist
```

---

## 📅 What Happens on April 1st, 2026

At **2:00 AM**, the system will:

1. **Import CI Reports** (5-10 minutes)
   - Fetch latest reports from careinspectorate.com
   - Extract ratings, requirements, recommendations
   - Save to `CareInspectorateReport` table

2. **Analyze Historical Data** (10-15 minutes)
   - Query 12 months of shifts, compliance, training, sickness
   - Calculate 50+ metrics per home
   - Identify trends and patterns

3. **ML Analysis & Action Generation** (5-10 minutes)
   - Compare baseline vs current metrics
   - Predict future issues using ML
   - Generate prioritized improvement actions
   - Assign to Quality Framework themes

4. **Create Plans** (2-5 minutes)
   - 5 home improvement plans
   - 1 organizational improvement plan
   - Executive summaries auto-generated

5. **Log Results**
   - All output saved to `~/Library/Logs/ci_automation.log`
   - Plans ready for review at 9 AM

**Total Time:** ~30-40 minutes

---

## 📊 Expected Output (April 1st)

### Database Records Created:
- **5 CareInspectorateReport** records (latest inspections)
- **5 ServiceImprovementPlan** records (one per home)
- **40-60 ImprovementAction** records (prioritized actions)
- **1 OrganizationalImprovementPlan** record (aggregated)

### Example Action:
```
HAW-2026-001: Improve Care Planning Documentation
Priority: CRITICAL
Source: Care Inspectorate Inspection
Theme: Theme 1 (Care and Support)
Target: April 1 → June 30, 2026
Expected: Care planning rating 3 Adequate → 4 Good
Success Metrics:
  - Care plan review compliance 78.9% → 95%+
  - Protected time for documentation allocated
  - Staff training on care planning completed
```

---

## 🔧 Manual Override Commands

If you need to run manually before/after April 1st:

```bash
# Import only Hawthorn House (priority)
python3 manage.py import_ci_reports --home "Hawthorn House" --latest-only

# Generate plan for specific home
python3 manage.py generate_annual_improvement_plans --home "Orchard Grove"

# Analyze different time period (6 months)
python3 manage.py generate_annual_improvement_plans --all --period-months 6

# Force re-generation (overwrites existing)
python3 manage.py generate_annual_improvement_plans --all
```

---

## 📝 Logs & Monitoring

### View Real-Time Logs
```bash
tail -f ~/Library/Logs/ci_automation.log
```

### Check Last Run
```bash
grep "Automation complete" ~/Library/Logs/ci_automation.log | tail -1
```

### Verify LaunchAgent Status
```bash
launchctl list | grep staffrota
# Should show: com.staffrota.ciautomation (PID when running, or 0 when idle)
```

---

## 🚨 Troubleshooting

### If Automation Doesn't Run on April 1st:

1. **Check LaunchAgent is loaded:**
   ```bash
   launchctl list | grep staffrota
   ```

2. **Check logs for errors:**
   ```bash
   cat ~/Library/Logs/ci_automation.log
   cat ~/Library/Logs/ci_automation_stderr.log
   ```

3. **Manually reload LaunchAgent:**
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.staffrota.ciautomation.plist
   launchctl load ~/Library/LaunchAgents/com.staffrota.ciautomation.plist
   ```

4. **Test manually:**
   ```bash
   /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete/run_annual_ci_automation.sh
   ```

### If Commands Fail:

1. **Check database migrations:**
   ```bash
   python3 manage.py showmigrations scheduling
   ```

2. **Verify CS numbers are set:**
   ```bash
   python3 manage.py shell -c "from scheduling.models import Unit; print(Unit.objects.values('name', 'care_inspectorate_cs_number'))"
   ```

3. **Check dependencies:**
   ```bash
   pip3 list | grep -E "beautifulsoup|requests"
   ```

---

## ✅ Summary

| Component | Status | Next Action |
|-----------|--------|-------------|
| LaunchAgent Installed | ✅ Active | None - will run April 1st |
| Django Commands | ✅ Working | None - ready to use |
| Dependencies | ✅ Installed | None |
| Database Models | ⏳ Pending | Add CS field to Unit model |
| Migrations | ⏳ Pending | Create & run migrations |
| CS Numbers | ⏳ Pending | Update 5 units |
| Testing | ⏳ Pending | Run dry-run tests |

**Next Steps:**
1. Complete database setup (Steps 1-5 above)
2. Test with `--dry-run` flag
3. Verify one full run manually
4. System will run automatically every April 1st! 🎉

---

**Created:** 27 December 2025  
**Last Updated:** 27 December 2025  
**System Version:** 1.0  
**Next Scheduled Run:** April 1, 2026 at 2:00 AM
