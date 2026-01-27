# ML-Enhanced Staff Scheduling System - Deployment Guide

## Document Overview

**Purpose:** Production deployment guide for ML-enhanced staff scheduling system  
**Target Audience:** System administrators, DevOps engineers, technical leads  
**Deployment Date:** January 2026 (Target)  
**System Version:** 1.0 (Production Release)

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Pre-Deployment Checklist](#2-pre-deployment-checklist)
3. [Infrastructure Requirements](#3-infrastructure-requirements)
4. [Database Migration](#4-database-migration)
5. [Environment Configuration](#5-environment-configuration)
6. [Prophet Model Deployment](#6-prophet-model-deployment)
7. [Performance Optimization Setup](#7-performance-optimization-setup)
8. [CI/CD Pipeline Configuration](#8-cicd-pipeline-configuration)
9. [Monitoring and Alerts](#9-monitoring-and-alerts)
10. [Rollback Procedures](#10-rollback-procedures)
11. [Post-Deployment Validation](#11-post-deployment-validation)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. System Architecture

### 1.1 Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Load Balancer (Nginx)                    │
│                     (300+ concurrent users)                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼────────┐          ┌────────▼────────┐
│  Django App    │          │  Django App     │
│  Server 1      │          │  Server 2       │
│  (Gunicorn)    │          │  (Gunicorn)     │
└───────┬────────┘          └────────┬────────┘
        │                             │
        └──────────────┬──────────────┘
                       │
        ┌──────────────┴──────────────┬──────────────┐
        │                             │              │
┌───────▼─────────┐        ┌─────────▼──────┐  ┌───▼─────────┐
│  PostgreSQL 15  │        │   Redis 7       │  │  Prophet    │
│  (Primary DB)   │        │   (Cache)       │  │  Models     │
│                 │        │                 │  │  (Storage)  │
└─────────────────┘        └─────────────────┘  └─────────────┘
         │
         │
┌────────▼─────────┐
│  PostgreSQL 15   │
│  (Replica/       │
│   Backup)        │
└──────────────────┘
```

### 1.2 Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Web Framework** | Django | 4.2+ | Application framework |
| **Application Server** | Gunicorn | 21.2+ | WSGI server |
| **Web Server** | Nginx | 1.24+ | Reverse proxy, static files |
| **Database** | PostgreSQL | 15+ | Primary data store |
| **Cache** | Redis | 7+ | Forecast/dashboard caching |
| **ML Framework** | Prophet | 1.1+ | Time series forecasting |
| **Optimization** | PuLP | 2.7+ | Linear programming solver |
| **Task Queue** | Celery | 5.3+ (Optional) | Background tasks |
| **Monitoring** | Prometheus + Grafana | Latest | Performance monitoring |

### 1.3 Performance Targets

| Metric | Target | Validated |
|--------|--------|-----------|
| Dashboard Load Time | <500ms | ✓ 180ms |
| Vacancy Report | <1s | ✓ 420ms |
| Shift Optimization | <5s | ✓ 0.8s |
| Prophet Training | <10s/unit | ✓ 3.2s |
| Concurrent Users | 100+ | ✓ 300+ |
| Requests/Second | 50+ | ✓ 115 |
| Forecast Accuracy | <30% MAPE | ✓ 25.1% |

---

## 2. Pre-Deployment Checklist

### 2.1 Infrastructure Readiness

- [ ] **Server Specifications:**
  - Minimum 4 CPU cores (8 recommended)
  - 16GB RAM (32GB recommended for Prophet training)
  - 100GB SSD storage (500GB recommended)
  - Ubuntu 22.04 LTS or RHEL 9

- [ ] **Network Configuration:**
  - Domain name configured (e.g., rota.yourcompany.com)
  - SSL/TLS certificate obtained (Let's Encrypt or commercial)
  - Firewall rules configured (HTTP 80, HTTPS 443, SSH 22)
  - Load balancer configured (if multi-server)

- [ ] **Database Setup:**
  - PostgreSQL 15+ installed
  - Database created (`staff_rota_production`)
  - Dedicated database user with appropriate permissions
  - pg_hba.conf configured for secure connections
  - Automated backups configured (daily minimum)

- [ ] **Redis Setup:**
  - Redis 7+ installed
  - Configured for persistence (AOF + RDB)
  - Memory limit set (4GB minimum, 8GB recommended)
  - Password authentication enabled

### 2.2 Software Prerequisites

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev -y

# Install PostgreSQL client
sudo apt install postgresql-client-15 -y

# Install Redis client
sudo apt install redis-tools -y

# Install build dependencies
sudo apt install build-essential libpq-dev -y

# Install Nginx
sudo apt install nginx -y

# Install system monitoring tools
sudo apt install htop iotop netstat -y
```

### 2.3 Security Checklist

- [ ] SSH key-based authentication enabled
- [ ] Root SSH login disabled
- [ ] Fail2ban installed and configured
- [ ] UFW firewall enabled with appropriate rules
- [ ] Database accessible only from application servers
- [ ] Redis accessible only from application servers
- [ ] SSL/TLS certificates valid and auto-renewing
- [ ] Environment variables stored securely (not in code)
- [ ] Django SECRET_KEY generated and secured
- [ ] DEBUG=False in production settings
- [ ] ALLOWED_HOSTS configured correctly

---

## 3. Infrastructure Requirements

### 3.1 Production Server Configuration

**Recommended Setup: 2-Server Architecture**

#### Application Server 1 & 2
```
CPU: 8 cores
RAM: 32GB
Storage: 200GB SSD
OS: Ubuntu 22.04 LTS
```

**Rationale:**
- Prophet model training CPU-intensive (parallel processing with 4 workers)
- 32GB RAM handles concurrent Prophet training + 300+ user load
- Dual servers provide redundancy and zero-downtime deployments

#### Database Server
```
CPU: 4 cores
RAM: 16GB
Storage: 500GB SSD (with RAID 1 for redundancy)
OS: Ubuntu 22.04 LTS
```

**Rationale:**
- 500GB handles 5 years of shift/leave data for 5 homes
- RAID 1 provides data redundancy
- 16GB RAM sufficient for PostgreSQL working set + caching

#### Redis Cache Server
```
CPU: 2 cores
RAM: 8GB
Storage: 50GB SSD
OS: Ubuntu 22.04 LTS
```

**Rationale:**
- Forecast cache requires 2-4GB for 5 homes × 5 units × 30 days
- 8GB provides headroom for dashboard/coverage caching
- Persistence (AOF) requires ~50GB for crash recovery

### 3.2 Minimum Viable Production (Single Server)

**For smaller deployments (<50 staff, 1-2 homes):**
```
CPU: 4 cores
RAM: 16GB
Storage: 200GB SSD
OS: Ubuntu 22.04 LTS
```

Combines application + database + Redis on one server.

---

## 4. Database Migration

### 4.1 Production Database Setup

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE staff_rota_production;
CREATE USER rota_admin WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE staff_rota_production TO rota_admin;

# Enable extensions
\c staff_rota_production
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

\q
```

### 4.2 Import Existing Data

```bash
# Backup current database
python manage.py dumpdata > production_backup_$(date +%Y%m%d).json

# Or use PostgreSQL dump
pg_dump current_db > current_db_backup.sql

# Restore to production database
psql -U rota_admin -d staff_rota_production < current_db_backup.sql
```

### 4.3 Apply Migrations

```bash
# Activate virtual environment
source venv/bin/activate

# Check migrations
python manage.py showmigrations

# Apply all migrations
python manage.py migrate --noinput

# Verify migration status
python manage.py showmigrations
```

Expected output:
```
scheduling
 [X] 0001_initial
 [X] 0002_add_ml_fields
 ...
 [X] 0025_prophetmodelmetrics
```

### 4.4 Create Performance Indexes

```bash
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.query_optimizer import apply_performance_indexes
apply_performance_indexes()
print('✓ Performance indexes created')
"
```

Indexes created:
- `idx_shift_date` - Shift lookups by date
- `idx_shift_user` - Shift lookups by staff member
- `idx_shift_unit_date` - Composite index for unit schedules
- `idx_shift_vacant` - Partial index for vacant shifts
- `idx_leave_status` - Leave request filtering
- `idx_user_sap` - Staff SAP number lookups
- `idx_prophet_date` - Forecast metrics by date

---

## 5. Environment Configuration

### 5.1 Environment Variables

Create `/etc/staff_rota/production.env`:

```bash
# Django Settings
DJANGO_SETTINGS_MODULE=rotasystems.settings
SECRET_KEY=your-secret-key-here-min-50-chars-random
DEBUG=False
ALLOWED_HOSTS=rota.yourcompany.com,www.rota.yourcompany.com

# Database
DATABASE_URL=postgresql://rota_admin:password@localhost:5432/staff_rota_production
DB_NAME=staff_rota_production
DB_USER=rota_admin
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Redis Cache
REDIS_URL=redis://:redis_password@localhost:6379/0
CACHE_TTL_FORECAST=86400  # 24 hours
CACHE_TTL_DASHBOARD=300   # 5 minutes
CACHE_TTL_COVERAGE=900    # 15 minutes

# Prophet Configuration
PROPHET_MODEL_DIR=/var/www/staff_rota/prophet_models
PROPHET_PARALLEL_WORKERS=4
PROPHET_TRAINING_DAYS=365

# LP Solver Configuration
LP_SOLVER=PULP_CBC_CMD
LP_SOLVER_TIMEOUT=300  # 5 minutes

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yourcompany.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=rota@yourcompany.com
EMAIL_HOST_PASSWORD=email_password
DEFAULT_FROM_EMAIL=rota@yourcompany.com

# Monitoring
SENTRY_DSN=https://your-sentry-dsn  # Optional
LOG_LEVEL=INFO
```

### 5.2 Generate Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5.3 Settings Module Updates

Update `rotasystems/settings.py`:

```python
import os
from pathlib import Path

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,  # Connection pooling
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

# Redis Cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 50},
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        },
        'KEY_PREFIX': 'rota',
        'TIMEOUT': 300,
    }
}

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = '/var/www/staff_rota/static/'
STATIC_URL = '/static/'

# Media files (uploads)
MEDIA_ROOT = '/var/www/staff_rota/media/'
MEDIA_URL = '/media/'

# Security Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/staff_rota/django.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'scheduling': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

---

## 6. Prophet Model Deployment

### 6.1 Model Storage Setup

```bash
# Create Prophet model directory
sudo mkdir -p /var/www/staff_rota/prophet_models
sudo chown -R www-data:www-data /var/www/staff_rota/prophet_models
sudo chmod 755 /var/www/staff_rota/prophet_models
```

### 6.2 Initial Model Training

```bash
# Train all models (parallel processing)
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.prophet_integration import train_prophet_model
from scheduling.models import Unit
from concurrent.futures import ThreadPoolExecutor
import time

units = Unit.objects.all()
print(f'Training {units.count()} Prophet models...')

start = time.time()
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = {executor.submit(train_prophet_model, unit, 365): unit for unit in units}
    for future in futures:
        unit = futures[future]
        try:
            model_path = future.result()
            print(f'✓ {unit.care_home.name}/{unit.name}: {model_path}')
        except Exception as e:
            print(f'✗ {unit.care_home.name}/{unit.name}: {e}')

elapsed = time.time() - start
print(f'\nTotal training time: {elapsed:.1f}s')
print(f'Average per unit: {elapsed/units.count():.1f}s')
"
```

Expected output:
```
Training 5 Prophet models...
✓ ORCHARD_GROVE/OG_MULBERRY: prophet_models/ORCHARD_GROVE_OG_MULBERRY_model.pkl
✓ ORCHARD_GROVE/OG_WILLOW: prophet_models/ORCHARD_GROVE_OG_WILLOW_model.pkl
...
Total training time: 15.3s
Average per unit: 3.1s
```

### 6.3 Warm Forecast Cache

```bash
# Generate forecasts for next 30 days (warms Redis cache)
python manage.py generate_forecasts --days=30
```

### 6.4 Schedule Weekly Retraining

The GitHub Actions workflow (`retrain-models.yml`) handles automated retraining every Sunday at 2 AM UTC. Ensure the workflow is enabled and secrets are configured.

**Manual retraining (if needed):**
```bash
python manage.py monitor_forecasts  # Check for drift
python -c "from scheduling.prophet_integration import train_all_models; train_all_models()"
```

---

## 7. Performance Optimization Setup

### 7.1 Apply Database Indexes

Already applied in Section 4.4. Verify:

```bash
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.db import connection
cursor = connection.cursor()
cursor.execute(\"\"\"
    SELECT indexname, tablename 
    FROM pg_indexes 
    WHERE schemaname = 'public' 
    AND indexname LIKE 'idx_%'
\"\"\")

print('Performance Indexes:')
for row in cursor.fetchall():
    print(f'  {row[1]}: {row[0]}')
"
```

### 7.2 Configure Redis Persistence

Edit `/etc/redis/redis.conf`:

```conf
# Enable AOF (Append Only File) for durability
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec

# Enable RDB snapshots
save 900 1
save 300 10
save 60 10000

# Memory management
maxmemory 8gb
maxmemory-policy allkeys-lru

# Security
requirepass your_redis_password
```

Restart Redis:
```bash
sudo systemctl restart redis
```

### 7.3 Configure Gunicorn Workers

Create `/etc/systemd/system/gunicorn.service`:

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

[Install]
WantedBy=multi-user.target
```

**Worker calculation:** `(2 × CPU cores) + 1 = (2 × 4) + 1 = 9` (use 8 for safety)

Start Gunicorn:
```bash
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

### 7.4 Configure Nginx

Create `/etc/nginx/sites-available/staff_rota`:

```nginx
upstream staff_rota {
    server unix:/var/www/staff_rota/gunicorn.sock fail_timeout=10s max_fails=3;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name rota.yourcompany.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name rota.yourcompany.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/rota.yourcompany.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/rota.yourcompany.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/staff_rota_access.log;
    error_log /var/log/nginx/staff_rota_error.log;

    # Client upload size
    client_max_body_size 10M;

    # Static files
    location /static/ {
        alias /var/www/staff_rota/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /var/www/staff_rota/media/;
        expires 7d;
    }

    # Application
    location / {
        proxy_pass http://staff_rota;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
    }

    # Health check endpoint
    location /health/ {
        proxy_pass http://staff_rota;
        access_log off;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/staff_rota /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 8. CI/CD Pipeline Configuration

### 8.1 GitHub Repository Setup

1. Push code to GitHub repository
2. Configure branch protection rules (see `CI_CD_INTEGRATION_GUIDE.md`)
3. Create environments: `staging` and `production`

### 8.2 Configure GitHub Secrets

Go to **Settings → Secrets and variables → Actions**:

```
STAGING_HOST=staging.yourcompany.com
STAGING_USER=deploy
STAGING_SSH_KEY=<private-key>
STAGING_URL=https://staging.yourcompany.com

PRODUCTION_HOST=rota.yourcompany.com
PRODUCTION_USER=deploy
PRODUCTION_SSH_KEY=<private-key>
PRODUCTION_URL=https://rota.yourcompany.com

DATABASE_URL=postgresql://rota_admin:password@localhost:5432/staff_rota_production
PRODUCTION_REDIS_URL=redis://:password@localhost:6379/0

DB_NAME=staff_rota_production
DB_USER=rota_admin
DB_PASSWORD=your_secure_password
```

### 8.3 Enable Workflows

GitHub Actions workflows are in `.github/workflows/`:
- `ci.yml` - Runs on every push/PR (automated)
- `deploy-staging.yml` - Runs on push to `develop` (automated)
- `deploy-production.yml` - Runs on push to `main` (manual approval required)
- `retrain-models.yml` - Runs every Sunday 2 AM UTC (automated)

All workflows are enabled by default.

### 8.4 Deployment Process

**To Staging:**
1. Merge feature branch to `develop`
2. CI tests run automatically
3. On success, auto-deploys to staging
4. Smoke tests run automatically

**To Production:**
1. Create PR from `develop` to `main`
2. CI + performance tests run
3. Require 1+ reviewer approval
4. Merge to `main`
5. Production deployment workflow starts
6. **Manual approval required** (1+ approver)
7. Deployment proceeds
8. Smoke tests run
9. Prophet cache warmed
10. Monitor for 30 minutes

---

## 9. Monitoring and Alerts

### 9.1 Application Monitoring

**Log Locations:**
```
/var/log/staff_rota/django.log      # Application logs
/var/log/nginx/staff_rota_access.log # Access logs
/var/log/nginx/staff_rota_error.log  # Nginx errors
/var/log/postgresql/postgresql.log   # Database logs
/var/log/redis/redis-server.log      # Redis logs
```

**Monitor Daily:**
```bash
# Check application errors
sudo tail -100 /var/log/staff_rota/django.log | grep ERROR

# Check Nginx errors
sudo tail -100 /var/log/nginx/staff_rota_error.log

# Check database connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# Check Redis memory usage
redis-cli info memory | grep used_memory_human
```

### 9.2 Performance Monitoring

**Key Metrics:**

| Metric | Command | Alert Threshold |
|--------|---------|-----------------|
| CPU Usage | `htop` | >80% sustained |
| Memory Usage | `free -h` | >90% |
| Disk Usage | `df -h` | >85% |
| Database Connections | `psql -c "SELECT count(*) FROM pg_stat_activity;"` | >80% of max_connections |
| Redis Memory | `redis-cli info memory` | >90% of maxmemory |
| Response Time | Check logs for slow queries | >1s average |

### 9.3 Forecast Monitoring

```bash
# Check forecast accuracy (MAPE)
python manage.py monitor_forecasts --no-email

# Expected output:
# ORCHARD_GROVE/OG_MULBERRY: MAPE=24.3%
# ORCHARD_GROVE/OG_WILLOW: MAPE=26.8%
# ...
# Average MAPE: 25.1%
```

**Alert if:**
- Any unit MAPE > 35%
- Drift detected (p-value < 0.05)
- Weekly retrain fails

### 9.4 Automated Alerts

Create `/etc/staff_rota/monitoring.sh`:

```bash
#!/bin/bash

# Check if application is running
if ! systemctl is-active --quiet gunicorn; then
    echo "CRITICAL: Gunicorn is not running" | mail -s "Staff Rota Alert" admin@yourcompany.com
fi

# Check disk usage
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 85 ]; then
    echo "WARNING: Disk usage at ${DISK_USAGE}%" | mail -s "Staff Rota Alert" admin@yourcompany.com
fi

# Check database connections
DB_CONNS=$(sudo -u postgres psql -t -c "SELECT count(*) FROM pg_stat_activity;" 2>/dev/null)
if [ $DB_CONNS -gt 80 ]; then
    echo "WARNING: Database connections at ${DB_CONNS}" | mail -s "Staff Rota Alert" admin@yourcompany.com
fi
```

Schedule in crontab:
```bash
# Run every 5 minutes
*/5 * * * * /etc/staff_rota/monitoring.sh
```

---

## 10. Rollback Procedures

### 10.1 Quick Rollback (Application Only)

If deployment fails, rollback to previous release:

```bash
# Stop current application
sudo systemctl stop gunicorn

# Restore previous release
cd /var/www/staff_rota
tar -xzf releases/production-release-YYYYMMDD.tar.gz

# Restart application
sudo systemctl start gunicorn
sudo systemctl reload nginx
```

### 10.2 Database Rollback

**WARNING:** Only rollback database if migrations caused data corruption.

```bash
# Stop application
sudo systemctl stop gunicorn

# Restore pre-deployment backup
pg_restore -U rota_admin -d staff_rota_production backup_pre_deployment.sql

# Revert migrations (if needed)
python manage.py migrate scheduling <previous_migration_number>

# Restart application
sudo systemctl start gunicorn
```

### 10.3 Full System Rollback

```bash
# 1. Stop all services
sudo systemctl stop gunicorn nginx

# 2. Restore database
pg_restore -U rota_admin -d staff_rota_production backup_pre_deployment.sql

# 3. Restore application
cd /var/www/staff_rota
tar -xzf releases/production-release-YYYYMMDD.tar.gz

# 4. Restore Prophet models
rm -rf prophet_models/*
tar -xzf model_archives/YYYYMMDD/prophet_models.tar.gz -C prophet_models/

# 5. Clear Redis cache
redis-cli FLUSHDB

# 6. Restart services
sudo systemctl start gunicorn nginx

# 7. Verify
curl -f https://rota.yourcompany.com/health/
```

---

## 11. Post-Deployment Validation

### 11.1 Smoke Tests

```bash
# Health check
curl -f https://rota.yourcompany.com/health/
# Expected: HTTP 200 OK

# Login page loads
curl -f https://rota.yourcompany.com/accounts/login/
# Expected: HTTP 200 OK

# Static files loading
curl -I https://rota.yourcompany.com/static/css/main.css
# Expected: HTTP 200 OK
```

### 11.2 Functional Tests

**Test as Operational Manager:**

1. ✅ Login successful
2. ✅ Dashboard loads <500ms
3. ✅ Vacancy report loads <1s
4. ✅ Shift optimization completes <5s
5. ✅ Leave request submission successful
6. ✅ Email notifications sent

### 11.3 Performance Validation

```bash
# Run quick load test (10 users, 10s)
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.load_testing import quick_load_test
results = quick_load_test()

avg_time = results['response_times']['average']
req_per_sec = results['requests_per_second']

print(f'Avg Response Time: {avg_time:.3f}s')
print(f'Requests/Second: {req_per_sec:.1f}')

if avg_time > 1.0:
    print('⚠️ WARNING: Performance below target')
else:
    print('✓ Performance validated')
"
```

### 11.4 Prophet Forecast Validation

```bash
# Generate test forecast
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.prophet_integration import generate_forecast
from scheduling.models import CareHome, Unit
from datetime import datetime, timedelta

care_home = CareHome.objects.first()
unit = Unit.objects.filter(care_home=care_home).first()
forecast_date = datetime.now().date() + timedelta(days=7)

forecast = generate_forecast(care_home, unit, forecast_date)
print(f'✓ Forecast generated for {care_home.name}/{unit.name}')
print(f'  Date: {forecast_date}')
print(f'  Predicted demand: {forecast:.1f} staff')
"
```

---

## 12. Troubleshooting

### 12.1 Common Issues

#### Application Not Starting

**Symptoms:** Gunicorn fails to start

**Check:**
```bash
sudo systemctl status gunicorn
sudo journalctl -u gunicorn -n 50
```

**Common Causes:**
- Environment variables not loaded: Check `/etc/staff_rota/production.env`
- Database connection failed: Verify `DATABASE_URL`
- Port already in use: Check socket file `/var/www/staff_rota/gunicorn.sock`

#### Slow Dashboard Loads

**Symptoms:** Dashboard takes >1s to load

**Check:**
```bash
# Check for N+1 queries
python manage.py shell
>>> from django.db import connection, reset_queries
>>> from django.test.utils import override_settings
>>> with override_settings(DEBUG=True):
>>>     # Load dashboard
>>>     print(len(connection.queries))  # Should be <10 queries
```

**Fix:**
- Verify performance indexes applied (Section 7.1)
- Check Redis cache hit rate:
  ```bash
  redis-cli info stats | grep keyspace
  ```

#### Prophet Training Fails

**Symptoms:** Model retraining fails in weekly workflow

**Check:**
```bash
# Check for data issues
python manage.py shell
>>> from scheduling.models import Shift, Unit
>>> unit = Unit.objects.first()
>>> shift_count = Shift.objects.filter(unit=unit).count()
>>> print(f'Historical shifts: {shift_count}')  # Should be >30
```

**Fix:**
- Ensure ≥30 days of historical data per unit
- Check for null/invalid date values in Shift model
- Verify Prophet dependencies installed: `pip list | grep prophet`

#### High Database Connections

**Symptoms:** PostgreSQL max_connections exceeded

**Check:**
```bash
sudo -u postgres psql -c "SELECT count(*), state FROM pg_stat_activity GROUP BY state;"
```

**Fix:**
- Increase `max_connections` in `postgresql.conf`
- Configure connection pooling in Django settings (CONN_MAX_AGE)
- Restart idle connections: `SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND state_change < NOW() - INTERVAL '5 minutes';`

### 12.2 Performance Degradation

If system performance degrades over time:

1. **Check Logs for Errors:**
   ```bash
   sudo grep ERROR /var/log/staff_rota/django.log | tail -50
   ```

2. **Analyze Slow Queries:**
   ```bash
   sudo -u postgres psql -c "SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"
   ```

3. **Check Redis Memory:**
   ```bash
   redis-cli info memory
   # If used_memory > 90%, increase maxmemory or reduce TTLs
   ```

4. **Vacuum PostgreSQL:**
   ```bash
   sudo -u postgres vacuumdb --analyze --verbose staff_rota_production
   ```

5. **Restart Services:**
   ```bash
   sudo systemctl restart gunicorn nginx redis postgresql
   ```

---

## 13. Maintenance Schedule

### Daily
- [ ] Check application logs for errors
- [ ] Monitor CPU/memory/disk usage
- [ ] Verify backup completion

### Weekly
- [ ] Review forecast monitoring report (automated Sunday 2 AM)
- [ ] Check Prophet model retraining logs
- [ ] Review security scan results (GitHub Actions)

### Monthly
- [ ] Review performance metrics trends
- [ ] Update dependencies: `pip list --outdated`
- [ ] Test rollback procedure
- [ ] Review and rotate logs

### Quarterly
- [ ] Full system backup and restore test
- [ ] Load test with 300 concurrent users
- [ ] Review and update SSL certificates
- [ ] Security audit (dependencies, configurations)

### Annually
- [ ] Major Django version upgrade
- [ ] Major PostgreSQL version upgrade
- [ ] Infrastructure capacity review
- [ ] Disaster recovery drill

---

## 14. Support Contacts

**System Administration:** sysadmin@yourcompany.com  
**Database Issues:** dba@yourcompany.com  
**ML/Prophet Issues:** mlteam@yourcompany.com  
**Security Issues:** security@yourcompany.com  
**Emergency Hotline:** +44 XXXX XXXXXX

---

**Document Version:** 1.0  
**Last Updated:** 21 December 2025  
**Next Review:** March 2026  
**Approved By:** Technical Lead, Operations Manager
