# Fix: Performance KPIs 500 Error on Demo Site

**Issue:** `demo.therota.co.uk/performance-kpis/` showing 500 Internal Server Error

**Root Cause:** The `performance_kpis` app tables don't exist in the production database. The app is installed in `INSTALLED_APPS` but the database migrations haven't been run on the production server.

---

## Quick Fix (SSH into Production Server)

```bash
# 1. SSH into the production server
ssh user@demo.therota.co.uk

# 2. Navigate to project directory
cd /path/to/staff-rota-system

# 3. Activate virtual environment
source venv/bin/activate

# 4. Run migrations for performance_kpis app
python manage.py migrate performance_kpis

# 5. Verify tables were created
python manage.py showmigrations performance_kpis

# 6. Restart web server (Gunicorn/uWSGI)
sudo systemctl restart gunicorn
# OR
sudo supervisorctl restart rotasystem
```

---

## Expected Output

After running migrations, you should see:
```
Operations to perform:
  Apply all migrations: performance_kpis
Running migrations:
  Applying performance_kpis.0001_initial... OK
  Applying performance_kpis.0002_...  OK
```

---

## Tables Created

The following tables will be created in PostgreSQL:

1. `performance_kpis_kpidefinition` - KPI definitions
2. `performance_kpis_kpimeasurement` - KPI measurements
3. `performance_kpis_executivedashboard` - Dashboard configurations
4. `performance_kpis_dashboardkpi` - Dashboard-KPI relationships
5. `performance_kpis_performancetarget` - Targets
6. `performance_kpis_benchmarkdata` - Benchmark data
7. `performance_kpis_balancedscorecardperspective` - Balanced scorecard perspectives

---

## Verify Fix

After restarting, visit:
- https://demo.therota.co.uk/performance-kpis/

You should see:
- Dashboard page loads successfully
- "No Dashboard Selected" message if no dashboards created yet
- No 500 error

---

## Create Test Dashboard (Optional)

```python
# Open Django shell on production
python manage.py shell

# Create a test dashboard
from performance_kpis.models import ExecutiveDashboard
from django.contrib.auth import get_user_model

User = get_user_model()
admin_user = User.objects.filter(is_superuser=True).first()

# Create executive dashboard
dashboard = ExecutiveDashboard.objects.create(
    name="Executive Overview",
    description="Main executive dashboard",
    owner=admin_user,
    is_public=True,
    refresh_interval=300  # 5 minutes
)

print(f"✅ Dashboard created: {dashboard.name} (ID: {dashboard.id})")
exit()
```

---

## Alternative: Deploy from Local

If you can't SSH into production, deploy from local with migrations:

```bash
# On your local machine
cd /Users/deansockalingum/Desktop/Staff_Rota_Backups

# Ensure migrations exist
python manage.py makemigrations performance_kpis

# Deploy script should include:
# 1. Push code to production
# 2. Run: python manage.py migrate
# 3. Restart web server
./deploy_to_production.sh
```

---

## Why This Happened

The `performance_kpis` app is relatively new (TQM Module 7) and was likely added to `INSTALLED_APPS` but migrations weren't run on production. This happens when:

1. Local development has migrations
2. Code deployed to production
3. `python manage.py migrate` not run on production
4. App tries to query tables that don't exist → 500 error

---

## Prevention for Future

Update `deploy_to_production.sh` to always run migrations:

```bash
#!/bin/bash
# Add to your deployment script

echo "Running database migrations..."
python manage.py migrate --no-input

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Restarting web server..."
sudo systemctl restart gunicorn
```

---

## Troubleshooting

### If migrations fail:

```bash
# Check which migrations are pending
python manage.py showmigrations

# Check if performance_kpis app is in INSTALLED_APPS
python manage.py check

# View SQL that would be run (without executing)
python manage.py sqlmigrate performance_kpis 0001
```

### If still getting 500 error after migrations:

```bash
# Check Django logs
tail -f /var/log/gunicorn/error.log

# Check database connection
python manage.py dbshell
\dt performance_kpis*
\q
```

### Permissions issue:

```bash
# Ensure database user has CREATE TABLE permissions
GRANT CREATE ON DATABASE rotasystem TO rotasystem_user;
```

---

## Status

**Current Status:** ❌ 500 Error  
**After Fix:** ✅ Page loads (may show "No Dashboard Selected" until dashboards created)  
**Data:** Empty tables (need to create dashboards and KPIs via admin or shell)

---

## Contact

If issue persists after running migrations, check:
1. Django error logs: `/var/log/gunicorn/error.log`
2. PostgreSQL logs: `/var/log/postgresql/postgresql-*.log`
3. Nginx logs: `/var/log/nginx/error.log`

The specific error will show which table or query is failing.
