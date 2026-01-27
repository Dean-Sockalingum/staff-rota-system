# Production Server - Critical Issues Found

**Date:** January 19, 2026  
**Issue:** Multiple 500 errors on demo.therota.co.uk due to incomplete deployment

---

## Problems Identified

1. **❌ AUTH_USER_MODEL Configuration Error**
   - Error: `AUTH_USER_MODEL refers to model 'scheduling.User' that has not been installed`
   - Root cause: Production code is outdated/incomplete
   - The `scheduling` app directory may be missing or incomplete

2. **❌ Performance KPIs Module Missing**
   - Error: 500 on `/performance-kpis/` route
   - Root cause: Database tables don't exist (migration not run)
   - Secondary issue: Can't run migrations due to issue #1

3. **❌ Gunicorn Service Not Found**
   - Error: `Unit gunicorn.service not found`
   - The web server may be running under a different service name
   - Need to identify actual service: `uwsgi`, `rotasystem`, or similar

---

## Required Actions

### **CRITICAL: Full Code Sync Required**

The production server needs a complete code redeployment from your local working system.

**Option A: Manual Full Deployment**

```bash
# 1. Create deployment package from working local system
cd /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
tar -czf staff-rota-complete.tar.gz \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='.git' \
  --exclude='venv' \
  --exclude='*.sqlite3' \
  --exclude='staticfiles' \
  --exclude='media' \
  .

# 2. Backup production database FIRST
ssh root@159.65.18.80 "cd /home/staff-rota-system && \
  source venv/bin/activate && \
  python manage.py dumpdata > backup_$(date +%Y%m%d_%H%M%S).json"

# 3. Upload complete codebase
scp staff-rota-complete.tar.gz root@159.65.18.80:/tmp/

# 4. Deploy on production
ssh root@159.65.18.80 << 'ENDSSH'
cd /home/staff-rota-system

# Backup current code
mv /home/staff-rota-system /home/staff-rota-system.backup.$(date +%Y%m%d)

# Extract new code
mkdir -p /home/staff-rota-system
cd /home/staff-rota-system
tar -xzf /tmp/staff-rota-complete.tar.gz

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --no-input

# Find and restart web server
systemctl list-units --type=service | grep -i "uwsgi\|gunicorn\|rota"
# Then restart the correct service, e.g.:
# systemctl restart uwsgi
# OR
# systemctl restart rotasystem
ENDSSH
```

---

### **Option B: Incremental Fix (If SSH Access Stable)**

If you can get stable SSH access:

```bash
ssh root@159.65.18.80

# 1. Check what service is actually running
systemctl list-units --type=service | grep -i "uwsgi\|gunicorn\|rota"
ps aux | grep -i "python.*manage"

# 2. Check actual directory structure
cd /home/staff-rota-system
ls -la

# 3. Verify settings
cat rotasystems/settings.py | grep -A 5 "AUTH_USER_MODEL"
cat rotasystems/settings.py | grep -A 30 "INSTALLED_APPS"

# 4. If scheduling/ is missing:
# - Production deployment is completely broken
# - Need full code redeploy (Option A)

# 5. If scheduling/ exists but incomplete:
# - Sync specific missing files from local
# - Run migrations
# - Restart service
```

---

## Why This Happened

The production server appears to have either:

1. **Never received the complete codebase** from 2025-12-12_Multi-Home_Complete
2. **Partial deployment** - some files uploaded but not all
3. **Git-based deployment issue** - if using git pull, some files may not have synced

The `deploy_to_production.sh` script only uploads **data** (`demo_export_cleaned.json`), not the **application code**.

---

## Recommended Approach

### **Immediate (Today)**

1. **Accept that demo.therota.co.uk has issues**
2. **Use your LOCAL demo** for any presentations:
   - URL: `http://127.0.0.1:8001`
   - This is 100% working with all features
   - Zero risk during senior management demo

### **This Week**

1. **Schedule production maintenance window** (1-2 hours)
2. **Full code redeployment** using Option A above
3. **Complete testing** before going live again

### **Long Term**

1. **Create proper CI/CD pipeline**:
   ```bash
   # In your deploy_to_production.sh
   # Add code sync, not just data sync
   
   # Sync code via rsync
   rsync -avz --delete \
     --exclude='*.pyc' \
     --exclude='__pycache__' \
     --exclude='venv' \
     --exclude='*.sqlite3' \
     /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete/ \
     root@159.65.18.80:/home/staff-rota-system/
   
   # Then run migrations + restart
   ssh root@159.65.18.80 "cd /home/staff-rota-system && \
     source venv/bin/activate && \
     python manage.py migrate && \
     python manage.py collectstatic --no-input && \
     systemctl restart [service-name]"
   ```

2. **Automated health checks**:
   ```bash
   # Check critical URLs return 200
   curl -f https://demo.therota.co.uk/ || alert
   curl -f https://demo.therota.co.uk/performance-kpis/ || alert
   ```

3. **Monitoring & Alerts**:
   - Setup Sentry for error tracking
   - Configure email alerts for 500 errors
   - Weekly health check reports

---

## Immediate Next Steps

**For Senior Management Demo (This Week):**
- ✅ Use **LOCAL** demo: `http://127.0.0.1:8001`
- ✅ All features work perfectly
- ✅ No risk of 500 errors during demo

**For Production Fix (After Demo):**
1. Schedule maintenance window
2. Full code redeployment (Option A)
3. Verify all routes working
4. Update DNS/announce service restored

---

## Files to Check on Production

When you can access the server, verify these exist:

```bash
/home/staff-rota-system/
├── scheduling/          ← CRITICAL: Must exist with models.py
│   ├── models.py        ← Must contain User model
│   ├── views.py
│   └── ...
├── performance_kpis/    ← New module (causing 500)
│   ├── models.py
│   ├── views.py
│   └── ...
├── rotasystems/
│   ├── settings.py      ← Check AUTH_USER_MODEL setting
│   └── urls.py
├── manage.py
├── requirements.txt
└── venv/
```

---

## Contact Support

If production is business-critical and local demo won't work:

1. **Hire DevOps consultant** for emergency deployment (4-6 hours)
2. **OR** Schedule pair programming session to walk through deployment
3. **OR** Use managed hosting (Heroku/DigitalOcean App Platform) for auto-deployments

**Current Status:**
- Production: ❌ BROKEN (multiple 500 errors)
- Local Demo: ✅ WORKING (100% reliable)

**Recommendation:** Use local demo for presentations until production properly redeployed.
