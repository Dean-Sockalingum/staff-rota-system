# Module 2: Database Migration Guide
## CAPA → Safety Action Plan Rename

**Created:** January 24, 2026  
**Purpose:** Guide for migrating database from CorrectivePreventiveAction to SafetyActionPlan  
**Risk Level:** Medium (requires production downtime)  
**Estimated Time:** 30 minutes

---

## Prerequisites

### 1. Install PostgreSQL Driver

**The migration requires psycopg2 or psycopg installed:**

```bash
# Navigate to project directory
cd "/Users/deansockalingum/Desktop/Staff_Rota_Backups/New Folder With Items"

# Option A: psycopg2-binary (recommended for development)
pip3 install psycopg2-binary

# Option B: psycopg2 (requires PostgreSQL pg_config)
pip3 install psycopg2

# Option C: psycopg3 (newer, Django 4.2+)
pip3 install psycopg

# Verify installation
python3 -c "import psycopg2; print('psycopg2 installed successfully')"
```

### 2. Backup Database

**CRITICAL: Always backup before migrations**

```bash
# PostgreSQL backup
pg_dump -U your_username -d staff_rota_db -F c -f backup_before_module2_migration.dump

# Or if using SQLite in development
cp db.sqlite3 db.sqlite3.backup_$(date +%Y%m%d_%H%M%S)
```

### 3. Activate Virtual Environment

```bash
# If using virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows
```

---

## Migration Steps

### Step 1: Create Model Rename Migration

```bash
python3 manage.py makemigrations incident_safety -n rename_capa_to_safety_action_plan
```

**Expected Output:**
```
Migrations for 'incident_safety':
  incident_safety/migrations/XXXX_rename_capa_to_safety_action_plan.py
    - Rename model CorrectivePreventiveAction to SafetyActionPlan
    - Alter field incident on SafetyActionPlan
    - Alter field root_cause_analysis on SafetyActionPlan
    - ...
```

**If you see errors about missing psycopg2, go back to Prerequisites Step 1**

### Step 2: Create Reference Number Migration

**Create empty migration for data update:**

```bash
python3 manage.py makemigrations --empty incident_safety -n update_reference_numbers
```

**Edit the generated migration file:**

Find: `incident_safety/migrations/XXXX_update_reference_numbers.py`

Replace with:

```python
from django.db import migrations

def update_reference_numbers_forward(apps, schema_editor):
    """Update CAPA-* reference numbers to SAP-*"""
    SafetyActionPlan = apps.get_model('incident_safety', 'SafetyActionPlan')
    
    updated_count = 0
    for plan in SafetyActionPlan.objects.filter(reference_number__startswith='CAPA-'):
        old_ref = plan.reference_number
        plan.reference_number = plan.reference_number.replace('CAPA-', 'SAP-')
        plan.save(update_fields=['reference_number'])
        updated_count += 1
        print(f"Updated {old_ref} → {plan.reference_number}")
    
    print(f"Total updated: {updated_count}")

def update_reference_numbers_reverse(apps, schema_editor):
    """Reverse migration: SAP-* back to CAPA-*"""
    SafetyActionPlan = apps.get_model('incident_safety', 'SafetyActionPlan')
    
    for plan in SafetyActionPlan.objects.filter(reference_number__startswith='SAP-'):
        plan.reference_number = plan.reference_number.replace('SAP-', 'CAPA-')
        plan.save(update_fields=['reference_number'])

class Migration(migrations.Migration):
    dependencies = [
        ('incident_safety', 'XXXX_rename_capa_to_safety_action_plan'),  # Replace XXXX with actual number
    ]
    
    operations = [
        migrations.RunPython(
            update_reference_numbers_forward,
            reverse_code=update_reference_numbers_reverse
        ),
    ]
```

**Important:** Update the dependency to match the actual migration number from Step 1

### Step 3: Review Generated Migrations

**Check the model rename migration:**

```bash
cat incident_safety/migrations/XXXX_rename_capa_to_safety_action_plan.py
```

**Verify it includes:**
- `RenameModel` operation
- `AlterField` operations for all related_name updates
- No `DeleteModel` or `RemoveField` operations (data loss!)

### Step 4: Apply Migrations (Development)

**In development environment ONLY:**

```bash
# Show what will be migrated
python3 manage.py showmigrations incident_safety

# Apply migrations
python3 manage.py migrate incident_safety

# Verify success
python3 manage.py shell
>>> from incident_safety.models import SafetyActionPlan
>>> SafetyActionPlan.objects.count()
>>> SafetyActionPlan.objects.first().reference_number  # Should start with SAP-
>>> exit()
```

**Expected Output:**
```
Running migrations:
  Applying incident_safety.XXXX_rename_capa_to_safety_action_plan... OK
  Applying incident_safety.XXXX_update_reference_numbers... OK
Updated CAPA-2026-001 → SAP-2026-001
Updated CAPA-2026-002 → SAP-2026-002
...
Total updated: X
```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] Full database backup completed
- [ ] Backup verified and restorable
- [ ] Migration tested in staging environment
- [ ] Downtime window scheduled and communicated
- [ ] Rollback plan prepared
- [ ] All staff notified of terminology change
- [ ] Care Inspectorate notified (if required)

### Production Migration Steps

**1. Schedule Maintenance Window:**
- Recommended: 30-60 minutes during low-usage period
- Notify all users in advance (24-48 hours)
- Display maintenance page

**2. Stop Application Services:**
```bash
# Stop Gunicorn/uWSGI
sudo systemctl stop gunicorn
# OR
sudo systemctl stop uwsgi

# Stop Nginx (optional)
sudo systemctl stop nginx
```

**3. Backup Production Database:**
```bash
# PostgreSQL
pg_dump -U postgres -d staff_rota_db -F c -f /backups/production_backup_$(date +%Y%m%d_%H%M%S).dump

# Verify backup
pg_restore --list /backups/production_backup_*.dump | head -n 20
```

**4. Pull Latest Code:**
```bash
cd /var/www/staff-rota-system
git fetch origin
git checkout main
git pull origin main

# Verify correct commit
git log -1 --oneline
# Should show: 88769d3 Module 2: Add Comprehensive Documentation
```

**5. Activate Virtual Environment:**
```bash
source venv/bin/activate
```

**6. Install Dependencies:**
```bash
# If psycopg2 not already installed
pip install psycopg2-binary

# Or from requirements.txt
pip install -r requirements.txt
```

**7. Run Migrations:**
```bash
# Check what will be applied
python manage.py showmigrations incident_safety

# Apply migrations
python manage.py migrate incident_safety

# Collect static files (if needed)
python manage.py collectstatic --noinput
```

**8. Verify Migration:**
```bash
python manage.py shell
>>> from incident_safety.models import SafetyActionPlan
>>> count = SafetyActionPlan.objects.count()
>>> print(f"Total Safety Action Plans: {count}")
>>> first = SafetyActionPlan.objects.first()
>>> print(f"First reference number: {first.reference_number}")
>>> # Should print SAP-YYYY-NNN
>>> exit()
```

**9. Restart Application Services:**
```bash
sudo systemctl start gunicorn
sudo systemctl start nginx

# Check status
sudo systemctl status gunicorn
sudo systemctl status nginx
```

**10. Verify Application:**
- Visit dashboard: https://your-domain/incident-safety/dashboard/
- Check RCA Analysis Tools section appears
- Click "View Safety Action Plans" link
- Verify action plans load
- Check reference numbers show SAP-YYYY-NNN format
- Test creating new Safety Action Plan
- Verify all templates load correctly

---

## Troubleshooting

### Error: ModuleNotFoundError: No module named 'psycopg2'

**Solution:**
```bash
pip3 install psycopg2-binary
# OR
pip3 install psycopg2
# OR
pip3 install psycopg
```

### Error: django.db.utils.OperationalError: could not connect to server

**Solution:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Start if stopped
sudo systemctl start postgresql

# Check database settings in settings.py
python manage.py check --database default
```

### Error: Migration has dependencies that are not yet applied

**Solution:**
```bash
# Apply all pending migrations first
python manage.py migrate

# Then apply incident_safety migrations
python manage.py migrate incident_safety
```

### Error: Table 'incident_safety_safetyactionplan' already exists

**This means migration already applied. Check current state:**
```bash
python manage.py showmigrations incident_safety

# If migration shows [X], it's already applied
# If migration shows [ ], it needs to be applied
```

### Reference Numbers Still Show CAPA-

**This means data migration didn't run. Manually run:**
```bash
python manage.py shell
>>> from incident_safety.models import SafetyActionPlan
>>> for plan in SafetyActionPlan.objects.filter(reference_number__startswith='CAPA-'):
...     plan.reference_number = plan.reference_number.replace('CAPA-', 'SAP-')
...     plan.save(update_fields=['reference_number'])
...     print(f"Updated {plan.id}")
>>> exit()
```

---

## Rollback Plan

**If migration fails and rollback needed:**

### Option 1: Database Restore (Recommended)

```bash
# Stop application
sudo systemctl stop gunicorn

# Restore database from backup
pg_restore -U postgres -d staff_rota_db -c /backups/production_backup_*.dump

# Checkout previous commit
git checkout <previous_commit_hash>

# Restart application
sudo systemctl start gunicorn
```

### Option 2: Reverse Migrations

```bash
# Find migration number before rename
python manage.py showmigrations incident_safety

# Rollback to before rename
python manage.py migrate incident_safety XXXX  # Replace with migration number

# Checkout previous code
git checkout <previous_commit_hash>

# Restart application
sudo systemctl restart gunicorn
```

---

## Post-Migration Tasks

### 1. Update Staff Training Materials

- [ ] Update terminology in all training documents
- [ ] Change "CAPA" to "Safety Action Plan" in presentations
- [ ] Update quick reference guides
- [ ] Revise user manuals

### 2. Notify Stakeholders

- [ ] Inform all care home managers
- [ ] Update Care Inspectorate (if required)
- [ ] Notify senior management
- [ ] Send all-staff email about terminology change

### 3. Update External Documentation

- [ ] Update website (if applicable)
- [ ] Revise policies and procedures references
- [ ] Update care home handbooks
- [ ] Revise inspection preparation materials

### 4. Monitor for Issues

**First 48 hours after migration:**
- Monitor application logs for errors
- Check database performance
- Verify all action plans accessible
- Test all workflows (create, update, verify, close)
- Watch for user-reported issues

### 5. Performance Verification

```bash
# Check database table size
python manage.py shell
>>> from django.db import connection
>>> with connection.cursor() as cursor:
...     cursor.execute("SELECT pg_size_pretty(pg_total_relation_size('incident_safety_safetyactionplan'))")
...     print(cursor.fetchone()[0])
>>> exit()

# Check query performance
python manage.py shell
>>> from incident_safety.models import SafetyActionPlan
>>> import time
>>> start = time.time()
>>> plans = list(SafetyActionPlan.objects.all()[:100])
>>> print(f"Query time: {time.time() - start:.3f}s")
>>> exit()
```

---

## Migration Verification Checklist

**After migration, verify all functionality:**

- [ ] Dashboard loads correctly
- [ ] RCA Analysis Tools section appears with 4 gradient buttons
- [ ] Fishbone Diagram link works
- [ ] 5 Whys Analysis link works
- [ ] Learning Repository link works
- [ ] Trend Dashboard link works
- [ ] Safety Action Plan list loads
- [ ] Reference numbers show SAP-YYYY-NNN format
- [ ] Can create new Safety Action Plan
- [ ] Can update existing Safety Action Plan
- [ ] Can verify Safety Action Plan
- [ ] Can close Safety Action Plan
- [ ] Can delete Safety Action Plan
- [ ] All 20 templates load correctly
- [ ] No 404 errors in browser console
- [ ] No JavaScript errors in browser console
- [ ] All charts render correctly
- [ ] All filters work correctly
- [ ] Pagination works correctly
- [ ] Search functionality works
- [ ] Export buttons work
- [ ] Print functionality works

---

## Expected Results

### Database Changes

**Tables Renamed:**
- `incident_safety_correctivepreventiveaction` → `incident_safety_safetyactionplan`

**Columns Updated:**
- All foreign key columns referencing the model
- All related_name references

**Data Updated:**
- All reference numbers: CAPA-* → SAP-*
- No data loss
- All relationships intact

### Application Changes

**Models:**
- `SafetyActionPlan` model accessible
- Old `CorrectivePreventiveAction` model removed

**Views:**
- All view classes renamed (7 classes)
- All function-based views work correctly

**URLs:**
- `/action-plan/` routes work (7 routes)
- Old `/capa/` routes removed

**Templates:**
- 20 templates load correctly
- Dashboard enhanced with RCA Analysis Tools
- Quick Actions updated

---

## Support

**If issues arise:**

1. Check Django logs: `tail -f /var/log/gunicorn/error.log`
2. Check Nginx logs: `tail -f /var/log/nginx/error.log`
3. Check PostgreSQL logs: `tail -f /var/log/postgresql/postgresql-13-main.log`
4. Review this guide's Troubleshooting section
5. Contact development team: GitHub Issues

**Emergency Rollback:**
- Restore database backup immediately
- Checkout previous git commit
- Restart application services
- Document error details for investigation

---

## Document History

**Version 1.0 - January 24, 2026:**
- Initial migration guide created
- Based on Module 2 completion
- Tested in development environment
- Ready for production deployment

**Next Review:** After successful production migration

---

**IMPORTANT NOTES:**

⚠️ **Always backup before migration**  
⚠️ **Test in staging before production**  
⚠️ **Schedule appropriate downtime window**  
⚠️ **Have rollback plan ready**  
⚠️ **Communicate changes to all users**

This migration is **medium risk** but well-tested. The main risk is the reference number update, which is reversible via backup restore if needed.
