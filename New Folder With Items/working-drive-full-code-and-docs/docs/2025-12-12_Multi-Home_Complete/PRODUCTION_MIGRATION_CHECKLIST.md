# Production Migration Checklist
## Staff Rota System - Final Deployment

**Migration Date:** [To be scheduled]  
**Estimated Duration:** 4-6 hours (includes cutover window)  
**Go-Live Date:** [To be confirmed]  
**Rollback Time:** 30 minutes if needed

---

## Table of Contents

1. [Pre-Migration (1-2 weeks before)](#1-pre-migration-1-2-weeks-before)
2. [Migration Day -1 (Day Before)](#2-migration-day--1-day-before)
3. [Migration Day (Deployment)](#3-migration-day-deployment)
4. [Post-Migration Validation](#4-post-migration-validation)
5. [Rollback Procedure](#5-rollback-procedure)
6. [Post-Go-Live Monitoring](#6-post-go-live-monitoring)

---

## 1. Pre-Migration (1-2 weeks before)

### 1.1 Infrastructure Preparation

**Server Provisioning:**
- [ ] Production application server provisioned (8 cores, 32GB RAM, 200GB SSD)
- [ ] Database server provisioned (4 cores, 16GB RAM, 500GB RAID 1)
- [ ] Redis cache server provisioned (2 cores, 8GB RAM, 50GB SSD)
- [ ] Load balancer configured (if 2-server setup)
- [ ] Firewall rules applied (ports 80, 443, 5432, 6379)
- [ ] DNS records created (rota.yourcompany.com → server IP)
- [ ] SSL certificate obtained (Let's Encrypt or commercial)

**Software Installation:**
- [ ] Ubuntu 22.04 LTS installed on all servers
- [ ] PostgreSQL 15 installed and running
- [ ] Redis 7 installed and configured
- [ ] Nginx installed
- [ ] Python 3.11 installed
- [ ] Build tools installed (`build-essential`, `python3-dev`, `libpq-dev`)
- [ ] Git installed

**Security Hardening:**
- [ ] SSH key-based authentication configured
- [ ] Root login disabled
- [ ] Fail2ban installed and configured
- [ ] UFW firewall enabled
- [ ] Automatic security updates enabled
- [ ] SSL/TLS configured with A+ rating (ssllabs.com test)

**Backup Infrastructure:**
- [ ] Automated PostgreSQL backups configured (daily at 2 AM)
- [ ] Backup retention policy set (30 days)
- [ ] Backup restoration tested successfully
- [ ] Backup storage location secured (off-server)

### 1.2 Code Preparation

**GitHub Repository:**
- [ ] `main` branch frozen (no new commits except critical fixes)
- [ ] All tests passing in CI/CD pipeline
- [ ] Code coverage ≥80%
- [ ] Performance benchmarks passing (<1s average response time)
- [ ] Security scans clean (no critical vulnerabilities)
- [ ] Release tagged (`v1.0.0`)
- [ ] Release notes documented

**Dependencies:**
- [ ] All Python dependencies in `requirements.txt` (pinned versions)
- [ ] No deprecated packages (check `pip list --outdated`)
- [ ] Security vulnerabilities resolved (`safety check`)
- [ ] License compliance verified

### 1.3 Data Preparation

**Export from Development/Staging:**
- [ ] Staff data exported (`python manage.py dumpdata scheduling.Staff > staff.json`)
- [ ] Care home data exported
- [ ] Unit data exported
- [ ] Shift pattern data exported
- [ ] Leave data exported (if applicable)
- [ ] User accounts exported
- [ ] Sensitive data reviewed (passwords, API keys)

**Data Validation:**
- [ ] Check for duplicate staff records
- [ ] Verify SAP numbers are unique
- [ ] Ensure all units linked to care homes
- [ ] Validate email addresses
- [ ] Check Working Time Directive settings

**Historical Data (Optional):**
- [ ] Import historical shifts (past 12 months) for forecasting accuracy
- [ ] Verify historical data quality (no missing dates, valid assignments)
- [ ] Prophet models pre-trained on historical data

### 1.4 Environment Configuration

**Create Environment Variables File:**
```bash
# /etc/staff_rota/production.env

# Django Settings
DJANGO_SETTINGS_MODULE=rotasystems.settings
SECRET_KEY=[50+ character random string - GENERATE NEW]
DEBUG=False
ALLOWED_HOSTS=rota.yourcompany.com

# Database
DATABASE_URL=postgresql://rota_admin:[PASSWORD]@localhost:5432/staff_rota_production

# Redis
REDIS_URL=redis://:[PASSWORD]@localhost:6379/0

# Prophet ML
PROPHET_MODEL_DIR=/var/www/staff_rota/prophet_models
PROPHET_PARALLEL_WORKERS=4

# LP Solver
LP_SOLVER=PULP_CBC_CMD

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yourcompany.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=rota@yourcompany.com
EMAIL_HOST_PASSWORD=[EMAIL_PASSWORD]
DEFAULT_FROM_EMAIL=rota@yourcompany.com

# Monitoring
SENTRY_DSN=[SENTRY_URL]  # Optional
LOG_LEVEL=INFO
```

**Checklist:**
- [ ] `SECRET_KEY` generated (50+ random characters)
- [ ] Database password generated (strong, 20+ characters)
- [ ] Redis password generated
- [ ] Email credentials verified
- [ ] File permissions set (`chmod 600 /etc/staff_rota/production.env`)
- [ ] Ownership set (`chown www-data:www-data /etc/staff_rota/production.env`)

### 1.5 Stakeholder Communication

**Email to All Users (1 week before):**
```
Subject: Staff Rota System Go-Live - [DATE]

Dear Team,

We are excited to announce the go-live of the new Staff Rota System on [DATE].

What to Expect:
- Access: https://rota.yourcompany.com
- Login: Your SAP number (e.g., SAP12345)
- Temporary Password: Sent separately (check email)
- Training: Completed on [TRAINING_DATE]

Downtime:
- Migration Window: [DATE] 6:00 AM - 10:00 AM
- System unavailable during this period
- Plan accordingly for shift handovers

Support:
- Technical Issues: support@yourcompany.com
- Training Questions: hr@yourcompany.com
- Emergency: +44 XXXX XXXXXX

Thank you for your patience during the migration.

Best regards,
[Name], Senior Management
```

**Checklist:**
- [ ] Email sent to all Operational Managers (OMs)
- [ ] Email sent to all Senior Managers (SMs)
- [ ] Email sent to all care staff (read-only access)
- [ ] IT support team briefed
- [ ] On-call support scheduled for go-live day

### 1.6 Training Completion

- [ ] OM/SM training completed (3-hour session)
- [ ] Training materials distributed (USER_TRAINING_GUIDE_OM_SM.md)
- [ ] Post-training quiz passed (all attendees)
- [ ] Demo environment access provided for practice
- [ ] Quick reference cards printed and distributed

### 1.7 Testing in Staging

**Functional Testing:**
- [ ] Login/logout works
- [ ] View rota (all units)
- [ ] Create shifts
- [ ] Fill vacancies
- [ ] Approve/reject leave requests
- [ ] Run optimization
- [ ] Generate reports
- [ ] Export to Excel

**Performance Testing:**
- [ ] Load test with 300 concurrent users (target: <1s average)
- [ ] Dashboard loads in <200ms
- [ ] Forecast generation <2s
- [ ] Optimization completes in <30s

**Data Migration Dry Run:**
- [ ] Import production data to staging
- [ ] Run migrations
- [ ] Verify all data imported correctly
- [ ] Apply performance indexes
- [ ] Train Prophet models
- [ ] Test forecasts

**Rollback Test:**
- [ ] Simulate production failure
- [ ] Execute rollback procedure
- [ ] Verify system restored to working state
- [ ] Time rollback (target: <30 minutes)

---

## 2. Migration Day -1 (Day Before)

### 2.1 Final Checks

**Code:**
- [ ] `main` branch last commit tagged (`v1.0.0`)
- [ ] Release notes finalized
- [ ] CI/CD pipeline passing (all green)
- [ ] No pending pull requests

**Infrastructure:**
- [ ] All servers online and accessible
- [ ] Disk space ≥50% free
- [ ] CPU/memory usage normal (<20%)
- [ ] Network connectivity verified
- [ ] Backup completed successfully last night

**Team Readiness:**
- [ ] On-call support confirmed (names, phone numbers)
- [ ] Escalation contacts available
- [ ] Migration team briefed (deployment steps reviewed)
- [ ] Rollback plan reviewed
- [ ] Communication templates ready

### 2.2 Freeze Development

- [ ] All developers notified: "Code freeze in effect"
- [ ] `main` branch protected (no commits allowed)
- [ ] `develop` branch frozen
- [ ] Only critical hotfixes allowed (with approval)

### 2.3 Final Backup

**Create Pre-Migration Backup:**
```bash
# Backup current production data (if existing system)
pg_dump -U rota_admin -d staff_rota_production -F c -f /backups/pre_migration_$(date +%Y%m%d).backup

# Backup configuration
tar -czf /backups/config_backup_$(date +%Y%m%d).tar.gz /etc/staff_rota/

# Backup Prophet models (if any)
tar -czf /backups/prophet_backup_$(date +%Y%m%d).tar.gz /var/www/staff_rota/prophet_models/
```

**Checklist:**
- [ ] Database backup completed
- [ ] Configuration backup completed
- [ ] Prophet models backup completed (if applicable)
- [ ] Backups copied to off-server location
- [ ] Backup integrity verified (test restore)

---

## 3. Migration Day (Deployment)

**Migration Window:** 6:00 AM - 10:00 AM (4 hours)  
**Team:** Database Admin, DevOps Engineer, ML Engineer, OM Representative

### Phase 1: System Preparation (6:00 - 6:30 AM)

#### 3.1 Pre-Deployment Backup

**Database:**
```bash
sudo -u postgres pg_dump -d staff_rota_production -F c -f /backups/pre_deploy_$(date +%Y%m%d_%H%M).backup
```
- [ ] Backup completed
- [ ] Backup size verified (expected: ~50-500MB depending on data)

**Configuration:**
```bash
tar -czf /backups/config_$(date +%Y%m%d_%H%M).tar.gz /etc/staff_rota/ /etc/nginx/ /etc/systemd/system/gunicorn.service
```
- [ ] Configuration backup completed

#### 3.2 Stop Existing Services (if applicable)

```bash
sudo systemctl stop gunicorn
sudo systemctl stop nginx
sudo systemctl stop redis
```
- [ ] Services stopped
- [ ] Maintenance page displayed (if configured)

### Phase 2: Database Setup (6:30 - 7:15 AM)

#### 3.3 Create Production Database

```bash
# Connect to PostgreSQL
sudo -u postgres psql

-- Create database and user
CREATE DATABASE staff_rota_production;
CREATE USER rota_admin WITH PASSWORD '[STRONG_PASSWORD]';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE staff_rota_production TO rota_admin;

-- Connect to database
\c staff_rota_production

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO rota_admin;

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;

\q
```
- [ ] Database created
- [ ] User created and privileges granted
- [ ] Extensions enabled

#### 3.4 Run Migrations

```bash
cd /var/www/staff_rota
source venv/bin/activate
source /etc/staff_rota/production.env

# Check migration status
python manage.py showmigrations

# Run migrations
python manage.py migrate --noinput

# Verify all migrations applied
python manage.py showmigrations | grep "\[X\]" | wc -l
```
- [ ] Migrations completed successfully
- [ ] No errors in output
- [ ] All migrations marked `[X]`

**Expected Output:**
```
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying scheduling.0001_initial... OK
  Applying scheduling.0002_add_prophet_fields... OK
  ...
  Applying scheduling.0015_leave_targets... OK
```

#### 3.5 Import Production Data

```bash
# Import staff data
python manage.py loaddata staff.json

# Import care homes
python manage.py loaddata carehomes.json

# Import units
python manage.py loaddata units.json

# Import shift patterns
python manage.py loaddata shift_patterns.json

# Import historical shifts (optional)
python manage.py loaddata historical_shifts.json
```

**Checklist:**
- [ ] Staff imported (verify count: `python manage.py shell -c "from scheduling.models import Staff; print(Staff.objects.count())"`)
- [ ] Care homes imported
- [ ] Units imported
- [ ] Shift patterns imported
- [ ] Historical shifts imported (if applicable)

**Verify Data Integrity:**
```bash
python manage.py shell

from scheduling.models import Staff, CareHome, Unit

# Check staff
print(f"Staff count: {Staff.objects.count()}")
print(f"Staff with SAP: {Staff.objects.exclude(sap_number='').count()}")

# Check duplicates
from django.db.models import Count
dups = Staff.objects.values('sap_number').annotate(count=Count('id')).filter(count__gt=1)
print(f"Duplicate SAP numbers: {dups.count()}")

# Check units
print(f"Care Homes: {CareHome.objects.count()}")
print(f"Units: {Unit.objects.count()}")
print(f"Units without home: {Unit.objects.filter(care_home__isnull=True).count()}")
```

- [ ] No duplicate SAP numbers
- [ ] All units linked to care homes
- [ ] Staff count matches expected

#### 3.6 Apply Performance Indexes

```bash
python manage.py shell

from scheduling.query_optimizer import apply_performance_indexes

# Apply indexes
apply_performance_indexes()

# Verify indexes created
from django.db import connection
cursor = connection.cursor()
cursor.execute("""
    SELECT indexname, tablename 
    FROM pg_indexes 
    WHERE schemaname = 'public' 
    AND indexname LIKE 'idx_%'
""")
indexes = cursor.fetchall()
print(f"Performance indexes created: {len(indexes)}")
for idx in indexes:
    print(f"  - {idx[0]} on {idx[1]}")
```

**Expected Indexes:**
- `idx_shift_date`
- `idx_shift_user`
- `idx_shift_unit_date`
- `idx_shift_vacant`
- `idx_leave_status`
- `idx_user_sap`
- `idx_prophet_date`
- `idx_forecast_unit_date`
- `idx_shift_user_date`
- `idx_staff_unit`

- [ ] All 10 indexes created
- [ ] No errors during index creation

### Phase 3: Application Deployment (7:15 - 8:00 AM)

#### 3.7 Deploy Application Code

```bash
# Create application directory
sudo mkdir -p /var/www/staff_rota
sudo chown www-data:www-data /var/www/staff_rota

# Clone repository
cd /var/www/staff_rota
sudo -u www-data git clone https://github.com/yourcompany/staff-rota.git .
sudo -u www-data git checkout tags/v1.0.0

# Create virtual environment
sudo -u www-data python3.11 -m venv venv
sudo -u www-data venv/bin/pip install --upgrade pip

# Install dependencies
sudo -u www-data venv/bin/pip install -r requirements.txt
```

**Checklist:**
- [ ] Code deployed to `/var/www/staff_rota`
- [ ] Virtual environment created
- [ ] Dependencies installed (check: `venv/bin/pip list | grep -i django`)

#### 3.8 Configure Static Files

```bash
source venv/bin/activate
source /etc/staff_rota/production.env

# Collect static files
python manage.py collectstatic --noinput

# Set permissions
sudo chown -R www-data:www-data static/
sudo chmod -R 755 static/
```

- [ ] Static files collected to `/var/www/staff_rota/static/`
- [ ] Permissions set correctly

#### 3.9 Create Gunicorn Service

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

**Service File:**
```ini
[Unit]
Description=Gunicorn daemon for Staff Rota
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/staff_rota
EnvironmentFile=/etc/staff_rota/production.env

ExecStart=/var/www/staff_rota/venv/bin/gunicorn \
    --workers 8 \
    --worker-class sync \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 300 \
    --bind unix:/var/www/staff_rota/gunicorn.sock \
    rotasystems.wsgi:application

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
sudo systemctl status gunicorn
```

- [ ] Gunicorn service created
- [ ] Service enabled
- [ ] Service started successfully
- [ ] Socket file created (`/var/www/staff_rota/gunicorn.sock`)

#### 3.10 Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/staff_rota
```

**Nginx Configuration:**
```nginx
upstream staff_rota {
    server unix:/var/www/staff_rota/gunicorn.sock fail_timeout=10s max_fails=3;
}

server {
    listen 80;
    server_name rota.yourcompany.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name rota.yourcompany.com;

    ssl_certificate /etc/letsencrypt/live/rota.yourcompany.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/rota.yourcompany.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    client_max_body_size 50M;

    location /static/ {
        alias /var/www/staff_rota/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/staff_rota/media/;
    }

    location / {
        proxy_pass http://staff_rota;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/staff_rota /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

- [ ] Nginx configured
- [ ] Configuration test passed (`nginx -t`)
- [ ] Nginx restarted successfully

### Phase 4: ML Model Deployment (8:00 - 8:45 AM)

#### 3.11 Create Prophet Model Directory

```bash
sudo mkdir -p /var/www/staff_rota/prophet_models
sudo chown www-data:www-data /var/www/staff_rota/prophet_models
sudo chmod 755 /var/www/staff_rota/prophet_models
```

- [ ] Prophet model directory created
- [ ] Permissions set

#### 3.12 Train Initial Prophet Models

```bash
cd /var/www/staff_rota
source venv/bin/activate
source /etc/staff_rota/production.env

python manage.py shell
```

**In Django shell:**
```python
from scheduling.models import Unit, Shift
from scheduling.ml_forecasting import train_prophet_model
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

units = Unit.objects.all()
print(f"Training models for {units.count()} units...")

start_time = time.time()
results = []

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = {
        executor.submit(train_prophet_model, unit, days=365): unit 
        for unit in units
    }
    
    for future in as_completed(futures):
        unit = futures[future]
        try:
            model_path = future.result()
            results.append((unit, model_path, "SUCCESS"))
            print(f"✓ {unit.care_home.name}/{unit.name}: {model_path}")
        except Exception as e:
            results.append((unit, None, f"ERROR: {e}"))
            print(f"✗ {unit.care_home.name}/{unit.name}: {e}")

elapsed = time.time() - start_time
print(f"\nTotal training time: {elapsed:.1f}s")
print(f"Average per unit: {elapsed/len(results):.1f}s")

# Print summary
success = sum(1 for r in results if r[2] == "SUCCESS")
print(f"\nSummary: {success}/{len(results)} models trained successfully")
```

**Expected Output:**
```
Training models for 5 units...
✓ Orchard Grove/OG Mulberry: prophet_models/Orchard_Grove_OG_Mulberry_model.pkl
✓ Orchard Grove/OG Willow: prophet_models/Orchard_Grove_OG_Willow_model.pkl
✓ Orchard Grove/OG Oak: prophet_models/Orchard_Grove_OG_Oak_model.pkl
✓ Victoria Gardens/VG Rose: prophet_models/Victoria_Gardens_VG_Rose_model.pkl
✓ Victoria Gardens/VG Lily: prophet_models/Victoria_Gardens_VG_Lily_model.pkl

Total training time: 15.2s
Average per unit: 3.0s

Summary: 5/5 models trained successfully
```

- [ ] All Prophet models trained
- [ ] No errors
- [ ] Model files created in `prophet_models/` directory

#### 3.13 Validate Prophet Models

```python
# Still in Django shell
from pathlib import Path
import pickle

model_dir = Path("/var/www/staff_rota/prophet_models")
model_files = list(model_dir.glob("*.pkl"))
print(f"Found {len(model_files)} model files")

for model_file in model_files:
    try:
        with open(model_file, 'rb') as f:
            model = pickle.load(f)
        
        # Test prediction
        import pandas as pd
        future = pd.DataFrame({'ds': pd.date_range(start='2026-01-01', periods=7)})
        forecast = model.predict(future)
        
        print(f"✓ {model_file.name}: Valid (predicted {len(forecast)} days)")
    except Exception as e:
        print(f"✗ {model_file.name}: Invalid - {e}")
```

- [ ] All models valid
- [ ] Test predictions successful

#### 3.14 Warm Forecast Cache

```python
from scheduling.ml_forecasting import get_or_create_forecast
from datetime import datetime, timedelta

# Warm cache for next 30 days
end_date = datetime.now().date() + timedelta(days=30)

for unit in units:
    try:
        forecast = get_or_create_forecast(
            unit_id=unit.id,
            end_date=end_date
        )
        print(f"✓ {unit.care_home.name}/{unit.name}: Cached {len(forecast)} days")
    except Exception as e:
        print(f"✗ {unit.care_home.name}/{unit.name}: {e}")
```

- [ ] Forecast cache warmed for all units
- [ ] Redis cache populated

### Phase 5: Final Validation (8:45 - 9:30 AM)

#### 3.15 Smoke Tests

**Test 1: Health Check**
```bash
curl -I https://rota.yourcompany.com/health/
# Expected: HTTP/2 200 OK
```
- [ ] Health check returns 200 OK

**Test 2: Login Page**
```bash
curl -I https://rota.yourcompany.com/accounts/login/
# Expected: HTTP/2 200 OK
```
- [ ] Login page loads

**Test 3: Static Files**
```bash
curl -I https://rota.yourcompany.com/static/admin/css/base.css
# Expected: HTTP/2 200 OK
```
- [ ] Static files serving correctly

**Test 4: Admin Login**
- [ ] Navigate to `https://rota.yourcompany.com/admin/`
- [ ] Login with superuser account
- [ ] Dashboard loads
- [ ] View staff list
- [ ] View shifts

**Test 5: OM Dashboard**
- [ ] Login as Operational Manager
- [ ] Dashboard loads with widgets
- [ ] View rota (select care home, unit, date range)
- [ ] Generate demand forecast
- [ ] View vacant shifts

#### 3.16 Performance Validation

**Load Test:**
```bash
cd /var/www/staff_rota
source venv/bin/activate
source /etc/staff_rota/production.env

python manage.py shell

from scheduling.load_testing import quick_load_test

results = quick_load_test()

print(f"Average Response Time: {results['response_times']['average']:.2f}ms")
print(f"95th Percentile: {results['response_times']['p95']:.2f}ms")
print(f"99th Percentile: {results['response_times']['p99']:.2f}ms")
print(f"Error Rate: {results['error_rate']:.2%}")
```

**Acceptance Criteria:**
- [ ] Average response time <1000ms
- [ ] 95th percentile <1500ms
- [ ] Error rate <1%

#### 3.17 Functional Tests

**Create Test Shift:**
```python
from scheduling.models import Staff, Unit, Shift
from datetime import datetime, timedelta

# Get test staff and unit
staff = Staff.objects.first()
unit = Unit.objects.first()

# Create shift
tomorrow = datetime.now().date() + timedelta(days=1)
shift = Shift.objects.create(
    user=staff,
    unit=unit,
    date=tomorrow,
    shift_type='D',
    is_vacant=False
)

print(f"✓ Created test shift: {shift}")

# Verify shift appears in rota
shifts_tomorrow = Shift.objects.filter(date=tomorrow, unit=unit)
print(f"✓ Found {shifts_tomorrow.count()} shifts for tomorrow in {unit.name}")

# Clean up
shift.delete()
print("✓ Test shift deleted")
```

- [ ] Shift creation successful
- [ ] Shift appears in database
- [ ] Shift deletion successful

**Generate Forecast:**
```python
from scheduling.ml_forecasting import get_or_create_forecast
from datetime import datetime, timedelta

unit = Unit.objects.first()
end_date = datetime.now().date() + timedelta(days=14)

forecast = get_or_create_forecast(unit_id=unit.id, end_date=end_date)

print(f"✓ Generated forecast for {unit.name}:")
print(f"  - Days: {len(forecast)}")
print(f"  - Average demand: {sum(f['yhat'] for f in forecast) / len(forecast):.2f} staff/day")
```

- [ ] Forecast generation successful
- [ ] Forecast values reasonable (not negative, within expected range)

**Run Optimization:**
```python
from scheduling.optimizer import optimize_schedule
from datetime import datetime, timedelta

start_date = datetime.now().date() + timedelta(days=7)
end_date = start_date + timedelta(days=7)

try:
    result = optimize_schedule(
        care_home_id=1,  # Adjust ID as needed
        start_date=start_date,
        end_date=end_date
    )
    print(f"✓ Optimization completed:")
    print(f"  - Status: {result['status']}")
    print(f"  - Cost: £{result.get('total_cost', 0):.2f}")
    print(f"  - Shifts created: {result.get('shifts_created', 0)}")
except Exception as e:
    print(f"✗ Optimization failed: {e}")
```

- [ ] Optimization completes without errors
- [ ] Results include cost, shifts created
- [ ] Execution time <60s

### Phase 6: User Access Setup (9:30 - 10:00 AM)

#### 3.18 Create Superuser (if not exists)

```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@yourcompany.com
# Password: [STRONG_PASSWORD]
```

- [ ] Superuser created
- [ ] Superuser can login

#### 3.19 Create OM/SM Accounts

```python
from django.contrib.auth.models import User
from scheduling.models import Staff

# Create user accounts for all OMs
oms = Staff.objects.filter(role__icontains='Manager')

for om in oms:
    # Create Django user
    user, created = User.objects.get_or_create(
        username=om.sap_number,
        defaults={
            'email': om.email,
            'first_name': om.first_name,
            'last_name': om.last_name,
            'is_staff': True,  # Can access admin
        }
    )
    
    if created:
        # Set temporary password
        temp_password = f"Rota{om.sap_number}!"
        user.set_password(temp_password)
        user.save()
        
        print(f"✓ Created user: {om.sap_number} (temp password: {temp_password})")
    else:
        print(f"- User already exists: {om.sap_number}")
```

- [ ] OM/SM user accounts created
- [ ] Temporary passwords generated
- [ ] Passwords recorded securely (send via encrypted email)

#### 3.20 Send Welcome Emails

**Email Template:**
```
Subject: Your Staff Rota System Access

Dear [OM_NAME],

Your account for the new Staff Rota System is now active!

Login Details:
- URL: https://rota.yourcompany.com
- Username: [SAP_NUMBER]
- Temporary Password: [TEMP_PASSWORD]

IMPORTANT: Please change your password immediately after first login:
1. Login with temporary password
2. Click your name (top right) → "Change Password"
3. Create a strong password (min 8 characters, uppercase, lowercase, number)

Training Materials:
- User Guide: [Attach USER_TRAINING_GUIDE_OM_SM.md]
- Quick Reference: [Link to quick reference card]

Support:
- Technical Issues: support@yourcompany.com
- Training Questions: hr@yourcompany.com
- Emergency: +44 XXXX XXXXXX

Best regards,
Staff Rota Support Team
```

- [ ] Welcome emails sent to all OMs/SMs
- [ ] Temporary passwords sent securely
- [ ] Training materials attached

---

## 4. Post-Migration Validation

### 4.1 System Health Check

**Check Services:**
```bash
sudo systemctl status gunicorn
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis
```

- [ ] All services running
- [ ] No errors in status output

**Check Logs:**
```bash
# Gunicorn logs
sudo journalctl -u gunicorn -n 50

# Nginx logs
sudo tail -50 /var/log/nginx/error.log
sudo tail -50 /var/log/nginx/access.log

# Django logs
sudo tail -50 /var/www/staff_rota/logs/django.log
```

- [ ] No critical errors in logs
- [ ] No unexpected exceptions
- [ ] Access logs show successful requests

### 4.2 Performance Metrics

**Dashboard Response Times:**
```bash
# Test dashboard load time
time curl -s https://rota.yourcompany.com/dashboard/ > /dev/null
# Target: <1 second
```

- [ ] Dashboard loads in <1s
- [ ] No timeout errors

**Database Connection Pool:**
```bash
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity WHERE datname = 'staff_rota_production';"
# Expected: <20 connections
```

- [ ] Connection count reasonable (<20)

### 4.3 Data Integrity

**Staff Count:**
```python
from scheduling.models import Staff
print(f"Staff count: {Staff.objects.count()}")
# Expected: Match pre-migration count
```

**Shift Count:**
```python
from scheduling.models import Shift
print(f"Shift count: {Shift.objects.count()}")
# Expected: Match historical data if imported
```

**Prophet Models:**
```bash
ls -lh /var/www/staff_rota/prophet_models/*.pkl
# Expected: 1 model file per unit
```

- [ ] Staff count matches expected
- [ ] Shift count matches expected
- [ ] All Prophet models present

### 4.4 User Acceptance

**Test with OMs:**
1. Invite 2-3 OMs to test system
2. Have them:
   - [ ] Login with temporary password
   - [ ] Change password
   - [ ] View dashboard
   - [ ] View rota for their care home
   - [ ] Create a test shift
   - [ ] Approve a leave request (if available)
3. Collect feedback

---

## 5. Rollback Procedure

**If critical issues arise, execute rollback within 30 minutes:**

### 5.1 Stop Current Services

```bash
sudo systemctl stop gunicorn
sudo systemctl stop nginx
```

### 5.2 Restore Database

```bash
# Drop current database
sudo -u postgres psql -c "DROP DATABASE staff_rota_production;"

# Restore from backup
sudo -u postgres pg_restore -C -d postgres /backups/pre_deploy_YYYYMMDD_HHMM.backup
```

### 5.3 Restore Configuration

```bash
tar -xzf /backups/config_YYYYMMDD_HHMM.tar.gz -C /
```

### 5.4 Restore Application (if previous version exists)

```bash
cd /var/www/staff_rota
git checkout [PREVIOUS_TAG]
venv/bin/pip install -r requirements.txt
```

### 5.5 Restart Services

```bash
sudo systemctl start gunicorn
sudo systemctl start nginx
```

### 5.6 Verify Rollback

```bash
curl -I https://rota.yourcompany.com/
# Expected: HTTP/2 200 OK
```

**Communicate Rollback:**
- [ ] Email all users: "Migration rolled back due to [REASON]. New migration date TBD."
- [ ] Update status page (if applicable)
- [ ] Schedule post-mortem meeting

---

## 6. Post-Go-Live Monitoring

### 6.1 Day 1 Monitoring (Go-Live Day)

**Every 1 Hour (10am - 6pm):**
- [ ] Check Gunicorn status: `sudo systemctl status gunicorn`
- [ ] Check Nginx error log: `sudo tail -20 /var/log/nginx/error.log`
- [ ] Check Django errors: `sudo tail -20 /var/www/staff_rota/logs/django.log`
- [ ] Check database connections: `sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity WHERE datname = 'staff_rota_production';"`
- [ ] Check Redis memory: `redis-cli INFO memory | grep used_memory_human`
- [ ] Test login: Visit `https://rota.yourcompany.com/accounts/login/`

**Document any issues:**
- [ ] User-reported issues logged in support ticket system
- [ ] Performance anomalies noted
- [ ] Errors categorized (critical, warning, info)

### 6.2 Week 1 Monitoring

**Daily Checks:**
- [ ] Review Django logs for errors
- [ ] Check email notifications sent successfully
- [ ] Verify Prophet forecast generation (weekly retraining on Sunday)
- [ ] Monitor disk space: `df -h`
- [ ] Check database backup completed: `ls -lh /backups/`

**User Feedback:**
- [ ] Send survey to OMs/SMs (ease of use, performance, issues)
- [ ] Schedule office hours for questions (e.g., daily 2-3pm)
- [ ] Document feature requests and bugs

### 6.3 Month 1 Monitoring

**Weekly Reviews:**
- [ ] Review performance trends (response times, database query times)
- [ ] Check forecast accuracy (compare predicted vs. actual demand)
- [ ] Analyze cost savings (agency usage, overtime)
- [ ] Review security logs (failed login attempts, suspicious activity)

**Optimization Opportunities:**
- [ ] Identify slow queries (use `pg_stat_statements`)
- [ ] Tune Redis cache TTLs if needed
- [ ] Adjust Gunicorn worker count based on CPU usage

**Monthly Report:**
```
Monthly System Report - [MONTH YEAR]

Uptime: 99.x%
Average Response Time: Xms
Users Active: X OMs, Y SMs, Z staff
Shifts Created: X,XXX
Forecasts Generated: XXX
Cost Savings: £X,XXX (X% reduction)

Issues Resolved: X
  - Critical: X
  - High: X
  - Medium: X
  - Low: X

Top Feature Requests:
1. [Feature 1]
2. [Feature 2]
3. [Feature 3]

Next Month Focus:
- [Action 1]
- [Action 2]
```

---

## Post-Migration Tasks

### Immediate (Day 1-7)

- [ ] Update documentation with production URLs
- [ ] Configure monitoring alerts (email/SMS for critical errors)
- [ ] Schedule first weekly forecast retraining (Sunday 2 AM)
- [ ] Archive migration backups to long-term storage
- [ ] Update project status to "PRODUCTION"

### Short-term (Week 2-4)

- [ ] Conduct post-go-live review meeting
- [ ] Document lessons learned
- [ ] Update academic paper with go-live metrics
- [ ] Finalize handover documentation
- [ ] Train backup support staff

### Long-term (Month 2+)

- [ ] Quarterly security audit
- [ ] Quarterly performance review
- [ ] Annual disaster recovery drill
- [ ] Plan feature enhancements based on user feedback

---

## Contacts

**Migration Team:**
- Database Admin: [name] - [email] - [phone]
- DevOps Engineer: [name] - [email] - [phone]
- ML Engineer: [name] - [email] - [phone]
- OM Representative: [name] - [email] - [phone]

**Escalation:**
- Senior Management: [name] - [email] - [phone]
- IT Director: [name] - [email] - [phone]
- Emergency Hotline: +44 XXXX XXXXXX

---

**Document Version:** 1.0  
**Last Updated:** 21 December 2025  
**Next Review:** Post-migration (within 1 week of go-live)
