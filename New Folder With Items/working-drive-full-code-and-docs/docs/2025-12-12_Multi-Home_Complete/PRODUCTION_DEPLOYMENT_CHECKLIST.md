# Production Deployment Checklist - Staff Rota System

**Version:** 1.0  
**Date:** 21 December 2025  
**Purpose:** Ensure secure production deployment with all Phase 6 security enhancements

---

## Pre-Deployment Checklist

### 1. Environment Configuration ✅

#### .env File (Production)
```bash
# Django Core
SECRET_KEY='[GENERATE-50-CHAR-RANDOM-KEY]'  # Use: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
DEBUG=False
ALLOWED_HOSTS=rotasystem.orchardgrove.com,www.rotasystem.orchardgrove.com,127.0.0.1

# Database (PostgreSQL recommended for production)
DATABASE_NAME=rota_production
DATABASE_USER=rota_app
DATABASE_PASSWORD='[STRONG-DB-PASSWORD]'
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Field Encryption
FIELD_ENCRYPTION_KEY=[YOUR-EXISTING-KEY-FROM-DEV]

# Email SMTP
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@orchardgrove.com
EMAIL_HOST_PASSWORD='[SMTP-APP-PASSWORD]'

# System Mode
SYSTEM_MODE=PRODUCTION

# Celery (Redis)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Twilio (Optional)
TWILIO_ACCOUNT_SID=[YOUR-TWILIO-SID]
TWILIO_AUTH_TOKEN=[YOUR-TWILIO-TOKEN]
TWILIO_PHONE_NUMBER=[YOUR-TWILIO-NUMBER]
```

**Action Items:**
- [ ] Generate new SECRET_KEY (50+ characters)
- [ ] Set DEBUG=False
- [ ] Configure production domain in ALLOWED_HOSTS
- [ ] Set up PostgreSQL database
- [ ] Configure email SMTP credentials
- [ ] Copy FIELD_ENCRYPTION_KEY from development .env

---

### 2. Database Migration ✅

```bash
# Backup existing data
python manage.py dumpdata > backup_$(date +%Y%m%d_%H%M%S).json

# Run migrations on production database
python manage.py migrate

# Create superuser
python manage.py createsuperuser --sap OM0001 --email admin@orchardgrove.com

# Verify migrations
python manage.py showmigrations
```

**Action Items:**
- [ ] Backup development database
- [ ] Configure PostgreSQL connection
- [ ] Run all migrations
- [ ] Create production admin account
- [ ] Test database connectivity

---

### 3. Static Files & Media ✅

```bash
# Collect static files for CDN/nginx serving
python manage.py collectstatic --noinput

# Set proper permissions
chmod -R 755 staticfiles/
chmod -R 755 media/
```

**Configure nginx/Apache:**
```nginx
# Static files
location /static/ {
    alias /var/www/rota/staticfiles/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}

# Media files
location /media/ {
    alias /var/www/rota/media/;
    expires 7d;
}
```

**Action Items:**
- [ ] Run collectstatic
- [ ] Configure web server for static serving
- [ ] Set up CDN (optional, recommended)
- [ ] Test static file access

---

### 4. HTTPS/SSL Configuration ✅

#### Option A: Let's Encrypt (Recommended - Free)
```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot --nginx -d rotasystem.orchardgrove.com -d www.rotasystem.orchardgrove.com

# Auto-renewal (cron)
sudo certbot renew --dry-run
```

#### Option B: Commercial SSL Certificate
- Purchase from trusted CA (Sectigo, DigiCert, etc.)
- Install on web server
- Configure nginx/Apache for SSL

#### nginx SSL Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name rotasystem.orchardgrove.com;

    ssl_certificate /etc/letsencrypt/live/rotasystem.orchardgrove.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/rotasystem.orchardgrove.com/privkey.pem;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers off;
    
    # HSTS (enforced by Django settings)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    
    # Security headers (also set by Django, belt-and-braces)
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name rotasystem.orchardgrove.com www.rotasystem.orchardgrove.com;
    return 301 https://$server_name$request_uri;
}
```

**Action Items:**
- [ ] Install SSL certificate (Let's Encrypt or commercial)
- [ ] Configure nginx/Apache for HTTPS
- [ ] Test SSL configuration (https://www.ssllabs.com/ssltest/)
- [ ] Verify HTTP → HTTPS redirect
- [ ] Enable auto-renewal for Let's Encrypt

---

### 5. Security Verification ✅

#### Run Django Deployment Checks
```bash
# With production settings
DEBUG=False python manage.py check --deploy

# Expected: 0 critical issues
```

#### Verify Security Headers
```bash
# Test with curl
curl -I https://rotasystem.orchardgrove.com

# Expected headers:
# Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
# X-Frame-Options: DENY
# X-Content-Type-Options: nosniff
# Content-Security-Policy: [CSP directives]
```

#### Test Account Lockout
```bash
# Attempt 5 failed logins
# Expected: Account locked for 1 hour, friendly lockout page displayed
```

**Action Items:**
- [ ] Run `python manage.py check --deploy` with 0 errors
- [ ] Verify all security headers present
- [ ] Test account lockout functionality
- [ ] Test password policy enforcement
- [ ] Verify CSRF protection working

---

### 6. Application Server Setup ✅

#### Gunicorn Configuration (Recommended)
```bash
# Install gunicorn
pip install gunicorn

# Test run
gunicorn rotasystems.wsgi:application --bind 127.0.0.1:8000 --workers 4

# Systemd service: /etc/systemd/system/rota.service
[Unit]
Description=Staff Rota System Gunicorn
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/rota
Environment="PATH=/var/www/rota/venv/bin"
Environment="DEBUG=False"
EnvironmentFile=/var/www/rota/.env
ExecStart=/var/www/rota/venv/bin/gunicorn \
          --workers 4 \
          --bind 127.0.0.1:8000 \
          --access-logfile /var/log/rota/access.log \
          --error-logfile /var/log/rota/error.log \
          rotasystems.wsgi:application

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable rota
sudo systemctl start rota
sudo systemctl status rota
```

**Action Items:**
- [ ] Install and configure Gunicorn
- [ ] Create systemd service file
- [ ] Enable and start service
- [ ] Verify process running
- [ ] Test application access

---

### 7. Background Tasks (Celery) ✅

#### Redis Setup
```bash
# Install Redis
sudo apt-get install redis-server

# Start and enable
sudo systemctl enable redis
sudo systemctl start redis

# Test connection
redis-cli ping  # Expected: PONG
```

#### Celery Worker Service
```bash
# Systemd service: /etc/systemd/system/celery.service
[Unit]
Description=Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/var/www/rota
Environment="PATH=/var/www/rota/venv/bin"
EnvironmentFile=/var/www/rota/.env
ExecStart=/var/www/rota/venv/bin/celery -A rotasystems worker \
          --loglevel=info \
          --logfile=/var/log/rota/celery.log \
          --pidfile=/var/run/celery/worker.pid

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable celery
sudo systemctl start celery
sudo systemctl status celery
```

#### Celery Beat Service (Scheduled Tasks)
```bash
# Systemd service: /etc/systemd/system/celerybeat.service
[Unit]
Description=Celery Beat Scheduler
After=network.target redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/rota
Environment="PATH=/var/www/rota/venv/bin"
EnvironmentFile=/var/www/rota/.env
ExecStart=/var/www/rota/venv/bin/celery -A rotasystems beat \
          --loglevel=info \
          --logfile=/var/log/rota/celerybeat.log \
          --pidfile=/var/run/celery/beat.pid

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable celerybeat
sudo systemctl start celerybeat
sudo systemctl status celerybeat
```

**Action Items:**
- [ ] Install and configure Redis
- [ ] Create Celery worker service
- [ ] Create Celery beat service
- [ ] Start all services
- [ ] Test scheduled tasks running

---

### 8. Monitoring & Logging ✅

#### Application Logging
```python
# rotasystems/settings.py - Production logging
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
            'filename': '/var/log/rota/django.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'security': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/rota/security.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 20,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['security'],
            'level': 'WARNING',
            'propagate': False,
        },
        'axes': {
            'handlers': ['security'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

#### Log Rotation (logrotate)
```bash
# /etc/logrotate.d/rota
/var/log/rota/*.log {
    daily
    missingok
    rotate 90
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload rota
    endscript
}
```

**Action Items:**
- [ ] Configure Django logging to files
- [ ] Set up logrotate for log management
- [ ] Create /var/log/rota/ directory
- [ ] Test log writing and rotation
- [ ] Configure monitoring alerts (optional)

---

### 9. Backup Strategy ✅

#### Database Backups
```bash
# Daily database backup script: /usr/local/bin/backup-rota-db.sh
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/rota"
mkdir -p $BACKUP_DIR

# PostgreSQL backup
pg_dump -U rota_app -h localhost rota_production | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Keep last 30 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete

# Crontab: 0 2 * * * /usr/local/bin/backup-rota-db.sh
```

#### Media Files Backup
```bash
# Weekly media backup
rsync -avz /var/www/rota/media/ /var/backups/rota/media_$(date +%Y%m%d)/
```

**Action Items:**
- [ ] Create backup script
- [ ] Schedule daily database backups (cron)
- [ ] Schedule weekly media backups
- [ ] Test restore procedure
- [ ] Configure off-site backup storage (AWS S3, etc.)

---

### 10. Performance Optimization ✅

#### Database Optimization
```bash
# PostgreSQL tuning (postgresql.conf)
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB

# Create indexes
python manage.py migrate  # Applies index migrations from scheduling.0014, 0.021
```

#### Redis Optimization
```bash
# redis.conf
maxmemory 512mb
maxmemory-policy allkeys-lru
```

**Action Items:**
- [ ] Tune PostgreSQL configuration
- [ ] Configure Redis memory limits
- [ ] Verify database indexes created
- [ ] Run EXPLAIN ANALYZE on slow queries
- [ ] Enable query logging for optimization

---

## Post-Deployment Verification

### Security Tests ✅

1. **SSL/TLS Configuration**
   - [ ] Test at https://www.ssllabs.com/ssltest/
   - [ ] Expected: A+ rating

2. **Security Headers**
   - [ ] Test at https://securityheaders.com/
   - [ ] Expected: A rating

3. **OWASP Top 10 Checks**
   - [ ] SQL Injection: Parameterized queries (Django ORM ✅)
   - [ ] XSS: Template auto-escaping (Django ✅)
   - [ ] CSRF: django-middleware ✅
   - [ ] Authentication: Django-Axes ✅
   - [ ] Sensitive Data: Field encryption ✅

4. **Account Lockout**
   - [ ] Test 5 failed login attempts
   - [ ] Verify 1-hour lockout
   - [ ] Check friendly lockout page displayed

5. **Audit Logging**
   - [ ] Create test user
   - [ ] Modify shift assignment
   - [ ] Verify audit trail in database

### Functional Tests ✅

1. **User Authentication**
   - [ ] Login with valid credentials
   - [ ] Logout functionality
   - [ ] Password reset flow

2. **Shift Management**
   - [ ] Create new shift
   - [ ] Assign staff to shift
   - [ ] Verify schedule display

3. **Leave Requests**
   - [ ] Submit leave request
   - [ ] OM approval workflow
   - [ ] Email notifications sent

4. **Reports**
   - [ ] Generate staffing report
   - [ ] Export to PDF
   - [ ] Verify data accuracy

### Performance Tests ✅

1. **Load Testing**
   ```bash
   # Install Apache Bench
   sudo apt-get install apache2-utils
   
   # Test with 100 concurrent users
   ab -n 1000 -c 100 https://rotasystem.orchardgrove.com/
   
   # Expected: >95% success rate, <500ms average response time
   ```

2. **Database Query Performance**
   ```bash
   # Enable Django Debug Toolbar (staging only)
   # Check for N+1 queries, slow queries
   ```

**Action Items:**
- [ ] Load test with expected user concurrency
- [ ] Identify and optimize slow queries
- [ ] Configure CDN for static assets (optional)
- [ ] Enable Gzip compression in nginx

---

## Scottish Design - OM/SM Feedback Session

### Staging Environment Testing (Week 2)

**Participants:**
- 2 Operational Managers (daily users)
- 1 Service Manager (approval workflows)
- 1 IT Support Lead (technical validation)

**Test Scenarios:**
1. **Login & Security**
   - Test password policy (10-char minimum)
   - Trigger account lockout (verify user-friendly page)
   - Test password reset flow

2. **Daily Operations**
   - Create and assign shifts
   - Submit and approve leave requests
   - Generate weekly rota

3. **Error Handling**
   - Intentional errors (missing fields, invalid data)
   - Verify error messages are clear and helpful

4. **Performance**
   - Page load times acceptable? (<2 seconds target)
   - Mobile device responsiveness

**Feedback Collection:**
- Survey: Security features usability (1-10 scale)
- Open discussion: Pain points and suggestions
- Document in IMPLEMENTATION_LOG.md

**Success Criteria:**
- ✅ 80%+ satisfaction with security UX
- ✅ <3 critical usability issues
- ✅ All workflows functional on mobile

---

## Production Deployment Timeline

### Day 1: Environment Setup
- [ ] Provision server (Ubuntu 22.04 LTS)
- [ ] Install dependencies (Python 3.14, PostgreSQL, Redis, nginx)
- [ ] Configure SSL certificate
- [ ] Create production .env file

### Day 2: Application Deployment
- [ ] Deploy codebase to /var/www/rota
- [ ] Run migrations
- [ ] Collect static files
- [ ] Configure Gunicorn + nginx

### Day 3: Service Configuration
- [ ] Set up Celery workers
- [ ] Configure logging and monitoring
- [ ] Create backup scripts
- [ ] Schedule cron jobs

### Day 4: Testing & Validation
- [ ] Run security scans
- [ ] Load testing
- [ ] OM/SM staging environment testing
- [ ] Fix any identified issues

### Day 5: Go-Live
- [ ] Final database backup
- [ ] Switch DNS to production server
- [ ] Monitor logs for errors
- [ ] On-call support available

---

## Emergency Rollback Procedure

If critical issues arise:

1. **Restore database backup**
   ```bash
   gunzip < /var/backups/rota/db_YYYYMMDD_HHMMSS.sql.gz | psql -U rota_app rota_production
   ```

2. **Revert codebase**
   ```bash
   cd /var/www/rota
   git checkout [previous-stable-tag]
   systemctl restart rota
   ```

3. **Switch DNS back to old server** (if applicable)

4. **Notify stakeholders**
   - Email to all OMs/SMs with issue description
   - Estimated resolution time
   - Temporary workaround instructions

---

## Production Settings Summary

All security features already configured in `rotasystems/settings.py`:

✅ Password Policy (10-char, validators)  
✅ Django-Axes (account lockout)  
✅ Session Security (1-hour timeout, HttpOnly, Secure)  
✅ CSRF Protection  
✅ Security Headers (XSS, NOSNIFF, X-Frame-Options)  
✅ HTTPS/SSL Enforcement (when DEBUG=False)  
✅ HSTS (1-year, includeSubDomains, preload)  
✅ Content Security Policy  
✅ Audit Logging (11 models registered)  
✅ Field Encryption Infrastructure  

**Only required for production:**
- Set `DEBUG=False` in .env
- Generate strong `SECRET_KEY`
- Configure `ALLOWED_HOSTS`
- Install SSL certificate
- Use PostgreSQL instead of SQLite

---

## Support & Maintenance

### Weekly Tasks
- [ ] Review security logs (/var/log/rota/security.log)
- [ ] Check failed login attempts (Django-Axes)
- [ ] Monitor Celery task queue health
- [ ] Review application errors

### Monthly Tasks
- [ ] Run `pip-audit` and `safety check`
- [ ] Update dependencies (security patches)
- [ ] Database optimization (VACUUM, ANALYZE)
- [ ] Review and archive old audit logs

### Quarterly Tasks
- [ ] Penetration testing (internal or external)
- [ ] Disaster recovery drill (restore from backup)
- [ ] Review and update security policies
- [ ] OM/SM feedback session on system performance

---

## Contact Information

**IT Support:** itsupport@orchardgrove.com  
**Emergency Contact:** +44 1234 567890  
**Django Documentation:** https://docs.djangoproject.com/en/4.2/  
**Security Issues:** security@orchardgrove.com

---

**Checklist Status:** Ready for Production Deployment  
**Next Step:** Schedule OM/SM staging environment testing (Week 2)
