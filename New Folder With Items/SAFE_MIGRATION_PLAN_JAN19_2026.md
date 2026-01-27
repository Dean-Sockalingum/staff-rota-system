# Safe Database Migration Plan - January 19, 2026

## Executive Summary
This plan outlines safe database migrations to add missing fields and tables to the production database, enabling full feature functionality while minimizing downtime and risk.

---

## Missing Database Components

### 1. Shift Model - Missing Fields ❌
**Location:** `scheduling/models.py` Line 444-600

Currently Production Has:
- Basic shift fields (user, unit, shift_type, date, status)
- shift_classification, shift_pattern
- custom_start_time, custom_end_time
- Agency fields (agency_company, agency_staff_name, agency_hourly_rate)

**Missing in Production:**
1. `is_overtime` (BooleanField) - Not in production database
2. `duration_hours` - **EXISTS as @property method** (lines 494-502)

**Code Currently Uses These Fields:**
- `scheduling/utils_rota_health_scoring.py` lines 265, 306, 339, 388-390
- Overtime tracking and fairness calculations
- WTD (Working Time Directive) compliance checking

### 2. StaffCertification Table - Completely Missing ❌
**Location:** `scheduling/models.py` Lines 3623-3680

**Status:** Model exists in code but table never created in production database

**Fields Needed:**
```python
staff_member (FK to User)
certification_type (CharField - FIRST_AID, MANUAL_HANDLING, etc.)
certification_name (CharField)
issue_date (DateField)
expiry_date (DateField)
renewal_date (DateField, nullable)
issuing_body (CharField)
certificate_number (CharField)
status (CharField - VALID, EXPIRING_SOON, EXPIRED, PENDING)
certificate_file (FileField)
days_before_expiry_alert (IntegerField, default=30)
alert_sent (BooleanField, default=False)
alert_sent_at (DateTimeField, nullable)
notes (TextField)
created_at, updated_at, created_by
```

**Code Currently Uses This Table:**
- `scheduling/views.py` line 14545 (compliance dashboard)
- Staff certification expiry tracking
- Compliance reporting

---

## Analysis: What Needs Migration

### Priority 1: Add is_overtime Field to Shift Model ⚠️ HIGH
**Reason:** Code actively queries this field, currently disabled

**Migration Required:**
```python
# Add to Shift model (scheduling/models.py around line 490)
is_overtime = models.BooleanField(
    default=False,
    help_text="True if this is an overtime shift"
)
```

**Impact:**
- LOW RISK - Simple boolean field
- Re-enables overtime tracking in rota health scoring
- Re-enables overtime fairness calculations
- Required for accurate cost tracking

**Data Backfill Strategy:**
- All existing shifts: `is_overtime = False` (safe default)
- Future logic: Set `is_overtime = True` where `shift_classification = 'OVERTIME'`

### Priority 2: Create StaffCertification Table ⚠️ MEDIUM
**Reason:** Table completely missing, compliance dashboard limited

**Migration Required:**
- Full table creation with all fields from model
- Indexes on: expiry_date, staff_member, status

**Impact:**
- MEDIUM RISK - New table, no existing data conflicts
- Enables staff certification tracking
- Enables compliance dashboard full functionality
- Required for Care Inspectorate compliance reporting

**Data Backfill Strategy:**
- Start with empty table (no historical data exists)
- Manual data entry required for existing staff certifications

### Priority 3: Review duration_hours ✅ NO MIGRATION NEEDED
**Status:** Already exists as @property method in model

**Analysis:**
- NOT a database field - calculated property
- Code at lines 494-502 calculates from start_time/end_time
- Error in checkpoint was from incorrect query attempting to filter on property
- **FIX:** Change queries to NOT filter by duration_hours

**Action Required:**
- Update `scheduling/utils_rota_health_scoring.py` line 388-390
- Change from filtering to calculating after retrieval
- NO DATABASE MIGRATION NEEDED

---

## Safe Migration Process

### Phase 1: Pre-Migration Preparation ✅

#### Step 1.1: Full Database Backup
```bash
# On production server
cd /home/staff-rota-system
sudo -u postgres pg_dump staffrota_production > backup_pre_migration_$(date +%Y%m%d_%H%M%S).sql

# Or if using SQLite
sqlite3 db.sqlite3 ".backup backup_pre_migration_$(date +%Y%m%d_%H%M%S).db"
```

#### Step 1.2: Test Environment Setup
```bash
# Create test database copy
cp db.sqlite3 db_test_migration.sqlite3

# Update test settings to use test database
# Test migrations on copy first
```

#### Step 1.3: Verify Current State
```bash
# List current database tables
python manage.py inspectdb | grep "class.*models.Model"

# Check for existing migrations
python manage.py showmigrations scheduling
```

### Phase 2: Create Migration Files 📝

#### Step 2.1: Generate Migrations for Shift.is_overtime
```python
# File: scheduling/models.py (add after line 490)

class Shift(models.Model):
    # ... existing fields ...
    
    # Add this field
    is_overtime = models.BooleanField(
        default=False,
        db_index=True,  # Index for overtime queries
        help_text="True if this is an overtime shift"
    )
    
    # ... rest of model ...
```

**Then run:**
```bash
python manage.py makemigrations scheduling -n add_is_overtime_to_shift
```

#### Step 2.2: Generate Migration for StaffCertification Table
**Model already exists** in `scheduling/models.py` lines 3623-3680

**Run:**
```bash
python manage.py makemigrations scheduling -n create_staff_certification_table
```

### Phase 3: Review Generated Migrations ⚠️

#### Step 3.1: Inspect Migration Files
```bash
# Location: scheduling/migrations/XXXX_add_is_overtime_to_shift.py
# Location: scheduling/migrations/XXXX_create_staff_certification_table.py

# Review each file before applying
cat scheduling/migrations/XXXX_add_is_overtime_to_shift.py
cat scheduling/migrations/XXXX_create_staff_certification_table.py
```

#### Step 3.2: Verify SQL Preview
```bash
# See what SQL will be executed
python manage.py sqlmigrate scheduling XXXX_add_is_overtime_to_shift
python manage.py sqlmigrate scheduling XXXX_create_staff_certification_table
```

**Expected SQL for is_overtime:**
```sql
ALTER TABLE "scheduling_shift" 
ADD COLUMN "is_overtime" boolean DEFAULT false NOT NULL;

CREATE INDEX "scheduling_shift_is_overtime_idx" 
ON "scheduling_shift" ("is_overtime");
```

**Expected SQL for StaffCertification:**
```sql
CREATE TABLE "scheduling_staffcertification" (
    "id" serial NOT NULL PRIMARY KEY,
    "certification_type" varchar(50) NOT NULL,
    "certification_name" varchar(200) NOT NULL,
    "issue_date" date NOT NULL,
    "expiry_date" date NOT NULL,
    -- ... all other fields ...
);

CREATE INDEX "scheduling_staffcertification_expiry_date_idx" 
ON "scheduling_staffcertification" ("expiry_date");
-- ... other indexes ...
```

### Phase 4: Test Migrations on Copy 🧪

#### Step 4.1: Run on Test Database
```bash
# Point to test database
export DATABASE_URL=sqlite:///db_test_migration.sqlite3

# Apply migrations
python manage.py migrate scheduling

# Verify tables created
python manage.py dbshell
> .tables
> .schema scheduling_shift
> .schema scheduling_staffcertification
> .quit
```

#### Step 4.2: Test Application Functionality
```bash
# Start test server
python manage.py runserver 8001

# Test URLs:
# - Compliance dashboard
# - Rota health scoring
# - Overtime reports
```

#### Step 4.3: Verify Data Integrity
```python
# Django shell
python manage.py shell

# Test queries
from scheduling.models import Shift, StaffCertification
Shift.objects.filter(is_overtime=True).count()  # Should work
StaffCertification.objects.all()  # Should return empty queryset
```

### Phase 5: Production Deployment 🚀

#### Step 5.1: Schedule Maintenance Window
**Recommended:** Low-traffic period (e.g., Sunday 2:00 AM)
**Duration:** Estimated 5-10 minutes
**Notification:** Inform staff 24 hours in advance

#### Step 5.2: Put System in Maintenance Mode
```bash
# Create maintenance.html in static folder
# Redirect all traffic to maintenance page
sudo systemctl stop staffrota
```

#### Step 5.3: Create Pre-Migration Backup
```bash
# Final backup before changes
cd /home/staff-rota-system/2025-12-12_Multi-Home_Complete
python manage.py dumpdata > backup_full_data_$(date +%Y%m%d_%H%M%S).json
cp db.sqlite3 db_pre_migration_$(date +%Y%m%d_%H%M%S).sqlite3
```

#### Step 5.4: Apply Migrations
```bash
# Run migrations
python manage.py migrate scheduling

# Verify migration success
python manage.py showmigrations scheduling
```

**Expected Output:**
```
scheduling
  [X] XXXX_add_is_overtime_to_shift
  [X] XXXX_create_staff_certification_table
```

#### Step 5.5: Verify Production Database
```bash
# Check tables exist
python manage.py dbshell

# SQLite commands
.tables
.schema scheduling_shift  # Should show is_overtime field
.schema scheduling_staffcertification  # Should exist
.quit
```

#### Step 5.6: Re-enable Features
**File:** `scheduling/utils_rota_health_scoring.py`

```python
# Line 265 - RE-ENABLE overtime shift filtering
overtime_shifts = self.shifts.filter(is_overtime=True)

# Line 306 - RE-ENABLE overtime count
overtime_count = self.shifts.filter(is_overtime=True).count()

# Line 339 - RE-ENABLE overtime fairness
# (restore original calculation)

# Lines 388-390 - Keep long shift check DISABLED
# duration_hours is @property, not a field - cannot filter
# Calculate duration after retrieving shifts instead
```

**File:** `scheduling/views.py`

```python
# Line 14545 - RE-ENABLE StaffCertification query
expiring_certifications = StaffCertification.objects.filter(
    staff_member__unit__care_home=care_home,
    status__in=['EXPIRING_SOON', 'EXPIRED']
).select_related('staff_member')
```

#### Step 5.7: Restart Service
```bash
# Restart application
sudo systemctl start staffrota

# Monitor logs
journalctl -u staffrota -f

# Check memory usage
systemctl status staffrota | grep Memory
```

#### Step 5.8: Smoke Testing
```bash
# Test critical paths
curl https://therota.co.uk/  # Homepage
curl https://therota.co.uk/compliance/dashboard/  # Compliance
curl https://therota.co.uk/rota-health/  # Rota health

# Check for errors in logs
journalctl -u staffrota -n 50 | grep ERROR
```

### Phase 6: Post-Migration Verification ✅

#### Step 6.1: Feature Testing Checklist
- [ ] Compliance dashboard loads without errors
- [ ] Staff certification list appears (empty initially)
- [ ] Overtime shifts can be created
- [ ] Overtime tracking appears in reports
- [ ] Rota health scoring includes overtime metrics
- [ ] No memory leaks or performance degradation

#### Step 6.2: Data Backfill (Optional)
```python
# Set is_overtime based on shift_classification
from scheduling.models import Shift

Shift.objects.filter(shift_classification='OVERTIME').update(is_overtime=True)
```

#### Step 6.3: Monitor for 24 Hours
- Watch memory usage trends
- Check error logs hourly
- Verify user feedback is positive
- Monitor database query performance

### Phase 7: Rollback Plan 🔄 (If Needed)

#### If Migration Fails:

**Step 7.1: Stop Service**
```bash
sudo systemctl stop staffrota
```

**Step 7.2: Restore Database**
```bash
# Restore from backup
cp db_pre_migration_YYYYMMDD_HHMMSS.sqlite3 db.sqlite3

# Or restore from JSON dump
python manage.py flush --no-input
python manage.py loaddata backup_full_data_YYYYMMDD_HHMMSS.json
```

**Step 7.3: Revert Code Changes**
```bash
# Re-disable features in code
# Restore previous versions of:
# - scheduling/utils_rota_health_scoring.py
# - scheduling/views.py
```

**Step 7.4: Restart Service**
```bash
sudo systemctl start staffrota
```

---

## Risk Assessment

### Low Risk ✅
- **Adding is_overtime field:** Simple boolean, default False, no data conflicts
- **Test migrations on copy:** Safe testing before production

### Medium Risk ⚠️
- **StaffCertification table:** New table, requires data entry workflow
- **Service downtime:** 5-10 minutes maintenance window needed

### High Risk ❌
- **None** - All changes are additive (no data deletion or modification)

---

## Success Criteria

### Must Have ✅
1. Database migrations apply successfully
2. Service restarts without errors
3. Memory usage remains stable (~76MB)
4. Core features (rotas, shifts) continue working

### Should Have ⚠️
1. Compliance dashboard shows certification tracking
2. Overtime metrics appear in rota health scoring
3. No performance degradation

### Nice to Have 💡
1. Historical overtime shifts backfilled
2. Staff certification data entered for all staff
3. Improved reporting accuracy

---

## Timeline

### Preparation (Day 1-2)
- Create test database copy
- Test migrations locally
- Review migration SQL
- Verify rollback procedure

### Deployment (Day 3)
- Schedule maintenance window
- Execute migration during low-traffic period
- Monitor for 24 hours

### Completion (Day 4)
- Data backfill if needed
- User training on new features
- Documentation updates

---

## Dependencies

### Technical Requirements
- Django migrations system functional
- Database backup tools available
- Sufficient disk space for backups
- SSH access to production server

### Team Requirements
- Database administrator approval
- User notification (24 hours advance)
- Support team on standby during migration
- Rollback plan tested and documented

---

## Files to Modify

### Models (Add Field)
- `scheduling/models.py` (line ~490) - Add is_overtime field to Shift model

### Views (Re-enable Features)
- `scheduling/utils_rota_health_scoring.py` (lines 265, 306, 339)
- `scheduling/views.py` (line 14545)

### No Changes Needed
- `scheduling/models.py` (StaffCertification already defined)
- Templates (all work with new fields)

---

## Next Steps

1. **Review this plan** with database administrator
2. **Test migrations** on local copy this week
3. **Schedule maintenance window** for next weekend
4. **Notify users** 24 hours before deployment
5. **Execute migration** during scheduled window
6. **Monitor system** for 24 hours post-migration

---

## Contact & Support

**Production Server:** root@159.65.18.80  
**Service:** staffrota.service  
**Database:** SQLite3 (`db.sqlite3`)  
**Migrations:** `python manage.py migrate`  
**Logs:** `journalctl -u staffrota -f`

---

*Document Created: January 19, 2026*  
*Status: Ready for Review*  
*Next Action: Test migrations on local database copy*
