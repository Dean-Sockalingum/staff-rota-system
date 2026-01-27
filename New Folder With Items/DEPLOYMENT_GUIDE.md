# 🚀 Staff Rota System - Deployment Guide

**Last Updated:** December 28, 2025  
**Version:** 1.0 with Quick Win AI Features

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [GitHub Secrets Configuration](#github-secrets-configuration)
3. [Server Setup](#server-setup)
4. [Staging Deployment](#staging-deployment)
5. [Production Deployment](#production-deployment)
6. [Post-Deployment Verification](#post-deployment-verification)
7. [Rollback Procedures](#rollback-procedures)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- **Python:** 3.14.0
- **Database:** SQLite3 (or PostgreSQL for production)
- **Web Server:** Nginx + Gunicorn (recommended)
- **Process Manager:** systemd
- **OS:** Ubuntu 20.04+ or similar Linux distribution

### Required Access
- GitHub repository access
- SSH access to staging/production servers
- Sudo privileges on deployment servers
- Domain names configured (staging.yourdomain.com, yourdomain.com)

---

## GitHub Secrets Configuration

### Step 1: Access Repository Settings

1. Go to your GitHub repository: `https://github.com/Dean-Sockalingum/staff-rota-system`
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

### Step 2: Add Staging Secrets

Add each of the following secrets:

#### `STAGING_HOST`
```
staging.yourdomain.com
```
Your staging server hostname or IP address.

#### `STAGING_USER`
```
deploy-user
```
SSH username for deployment (recommended: create dedicated deploy user).

#### `STAGING_SSH_KEY`
```
-----BEGIN OPENSSH PRIVATE KEY-----
[Your private SSH key content]
-----END OPENSSH PRIVATE KEY-----
```

**To generate SSH key pair:**
```bash
ssh-keygen -t ed25519 -C "github-actions-staging" -f ~/.ssh/github_staging
cat ~/.ssh/github_staging  # Copy this as STAGING_SSH_KEY
cat ~/.ssh/github_staging.pub  # Add this to server's authorized_keys
```

#### `STAGING_PATH`
```
/var/www/staff-rota-staging
```
Deployment directory on staging server.

#### `STAGING_URL`
```
https://staging.yourdomain.com
```
Full staging URL for smoke tests.

### Step 3: Add Production Secrets

Repeat for production with these keys:
- `PROD_HOST`
- `PROD_USER`
- `PROD_SSH_KEY`
- `PROD_PATH`
- `PROD_URL`

---

## Server Setup

### Staging Server Setup

SSH into your staging server and run:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.14
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.14 python3.14-venv python3.14-dev -y

# Install system dependencies
sudo apt install -y \
    nginx \
    supervisor \
    git \
    build-essential \
    libpq-dev \
    sqlite3

# Create deployment directory
sudo mkdir -p /var/www/staff-rota-staging
sudo chown $USER:$USER /var/www/staff-rota-staging
cd /var/www/staff-rota-staging

# Create virtual environment
python3.14 -m venv venv
source venv/bin/activate

# Install gunicorn
pip install gunicorn

# Create systemd service
sudo tee /etc/systemd/system/staff-rota-staging.service << 'EOF'
[Unit]
Description=Staff Rota System - Staging
After=network.target

[Service]
Type=notify
User=deploy-user
Group=www-data
WorkingDirectory=/var/www/staff-rota-staging/current
Environment="PATH=/var/www/staff-rota-staging/venv/bin"
ExecStart=/var/www/staff-rota-staging/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/var/www/staff-rota-staging/staff-rota.sock \
    --access-logfile /var/log/staff-rota-staging/access.log \
    --error-logfile /var/log/staff-rota-staging/error.log \
    rotasystems.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Create log directory
sudo mkdir -p /var/log/staff-rota-staging
sudo chown deploy-user:www-data /var/log/staff-rota-staging

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable staff-rota-staging
```

### Nginx Configuration

```bash
sudo tee /etc/nginx/sites-available/staff-rota-staging << 'EOF'
server {
    listen 80;
    server_name staging.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name staging.yourdomain.com;

    # SSL Configuration (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/staging.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/staging.yourdomain.com/privkey.pem;

    client_max_body_size 10M;

    location /static/ {
        alias /var/www/staff-rota-staging/current/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/staff-rota-staging/current/media/;
        expires 7d;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/staff-rota-staging/staff-rota.sock;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/staff-rota-staging /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d staging.yourdomain.com

# Auto-renewal (already configured by certbot)
sudo systemctl status certbot.timer
```

---

## Environment Configuration

Create `.env` file in `/var/www/staff-rota-staging/current/`:

```bash
# Django Settings
DEBUG=False
SECRET_KEY=your-very-long-random-secret-key-here
ALLOWED_HOSTS=staging.yourdomain.com,localhost

# Database (SQLite for staging)
DATABASE_URL=sqlite:///db.sqlite3

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password

# AI Features
OPENAI_API_KEY=your-openai-key-if-using-gpt

# Monitoring
SENTRY_DSN=your-sentry-dsn-for-error-tracking
```

**Generate SECRET_KEY:**
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Staging Deployment

### Automatic Deployment

Deployments trigger automatically on push to `main` branch:

```bash
# On your local machine
git add .
git commit -m "Your changes"
git push origin main
```

### Monitor Deployment

1. Go to GitHub repository → **Actions** tab
2. Click on the latest workflow run
3. Watch real-time deployment progress
4. Check smoke test results

### Manual Deployment Trigger

Via GitHub UI:
1. Go to **Actions** → **Deploy to Staging**
2. Click **Run workflow**
3. Select `main` branch
4. Click **Run workflow**

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] All tests passing on staging
- [ ] Database migrations tested on staging
- [ ] Smoke tests passing on staging
- [ ] Load testing completed (if applicable)
- [ ] Backup production database
- [ ] Notify team of deployment window
- [ ] Rollback plan prepared

### Deployment via Git Tag

```bash
# Create release tag
git tag -a v1.0.0 -m "Release v1.0.0 - Quick Win AI Features"
git push origin v1.0.0
```

This triggers the production deployment workflow.

### Monitor Production Deployment

1. **GitHub Actions** - Watch workflow progress
2. **Server Logs** - Monitor application logs:
   ```bash
   ssh user@prod-server
   sudo journalctl -u staff-rota-production -f
   ```
3. **Application Health** - Check endpoints after deployment

---

## Post-Deployment Verification

### Health Checks

```bash
# Admin interface
curl -I https://yourdomain.com/admin/

# Management dashboard
curl -I https://yourdomain.com/management/

# AI Assistant
curl -I https://yourdomain.com/management/ai-assistant/

# Static files
curl -I https://yourdomain.com/static/css/style.css
```

### Quick Win AI Features Verification

```bash
# Test intelligent OT system
curl https://yourdomain.com/management/overtime/preferences/

# Test proactive suggestions API
curl https://yourdomain.com/management/api/proactive-suggestions/

# Test AI assistant
curl https://yourdomain.com/management/api/ai-assistant/ \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"query":"What are my staffing levels?"}'
```

### Database Migration Check

```bash
ssh user@server
cd /var/www/staff-rota-[staging|production]/current
source venv/bin/activate
python manage.py showmigrations
```

### Performance Check

```bash
# Response time test
time curl -s https://yourdomain.com/management/ > /dev/null

# Load test (using Apache Bench)
ab -n 100 -c 10 https://yourdomain.com/management/
```

---

## Rollback Procedures

### Automatic Rollback

The workflow includes automatic rollback on deployment failure.

### Manual Rollback

If you need to manually rollback:

```bash
# SSH to server
ssh user@server
cd /var/www/staff-rota-production

# List available backups
ls -la backup_*

# Restore backup
BACKUP_DIR="backup_20251228_143000"  # Use actual timestamp
rm -f current
ln -sfn $BACKUP_DIR current

# Restart application
sudo systemctl restart staff-rota-production

# Verify
curl -I https://yourdomain.com/management/
```

### Database Rollback

```bash
cd /var/www/staff-rota-production
source venv/bin/activate

# List backups
ls -la backup_*.json
ls -la db.sqlite3.backup_*

# Restore from backup
python manage.py flush --noinput
python manage.py loaddata backup_20251228_143000.json

# Or restore SQLite file directly
cp db.sqlite3.backup_20251228_143000 db.sqlite3
```

---

## Troubleshooting

### Deployment Fails - SSH Connection

**Issue:** Cannot connect to server

```bash
# Test SSH connection locally
ssh -i ~/.ssh/github_staging deploy-user@staging-server

# Check SSH key permissions
chmod 600 ~/.ssh/github_staging

# Verify key in GitHub Secrets
# Ensure no extra spaces or line breaks
```

### Application Won't Start

**Issue:** Gunicorn service fails

```bash
# Check service status
sudo systemctl status staff-rota-staging

# View logs
sudo journalctl -u staff-rota-staging -n 50

# Common issues:
# 1. Virtual environment not activated
# 2. Wrong Python path
# 3. Missing dependencies
# 4. Database migration needed
```

### Static Files Not Loading

**Issue:** 404 on static files

```bash
# Collect static files
cd /var/www/staff-rota-staging/current
source venv/bin/activate
python manage.py collectstatic --noinput

# Check nginx configuration
sudo nginx -t
sudo systemctl reload nginx

# Verify permissions
ls -la static/
```

### Database Migration Errors

**Issue:** Migration fails during deployment

```bash
# Check migration status
python manage.py showmigrations

# Apply migrations manually
python manage.py migrate --fake-initial

# Or roll back problematic migration
python manage.py migrate scheduling 0042_previous_migration
```

### 502 Bad Gateway

**Issue:** Nginx shows 502 error

```bash
# Check if application is running
sudo systemctl status staff-rota-staging

# Check socket file exists
ls -la /var/www/staff-rota-staging/staff-rota.sock

# Restart services
sudo systemctl restart staff-rota-staging
sudo systemctl reload nginx
```

### High Memory Usage

**Issue:** Server running out of memory

```bash
# Check memory usage
free -h
htop

# Reduce gunicorn workers in systemd service
# Edit: /etc/systemd/system/staff-rota-staging.service
# Change: --workers 3 to --workers 2

sudo systemctl daemon-reload
sudo systemctl restart staff-rota-staging
```

---

## Monitoring & Alerts

### Set Up Monitoring

```bash
# Install monitoring tools
sudo apt install prometheus-node-exporter -y

# Django health check endpoint
# Add to urls.py:
# path('health/', views.health_check, name='health_check'),
```

### Log Rotation

```bash
sudo tee /etc/logrotate.d/staff-rota-staging << 'EOF'
/var/log/staff-rota-staging/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 deploy-user www-data
    sharedscripts
    postrotate
        systemctl reload staff-rota-staging > /dev/null 2>&1 || true
    endscript
}
EOF
```

---

## Security Checklist

- [ ] Firewall configured (ufw enable)
- [ ] SSH key-based authentication only
- [ ] Fail2ban installed and configured
- [ ] SSL certificates installed and auto-renewing
- [ ] SECRET_KEY unique per environment
- [ ] DEBUG=False in production
- [ ] Database credentials secured
- [ ] Regular security updates scheduled
- [ ] Sentry/error tracking configured
- [ ] Backup strategy implemented

---

## Support & Maintenance

### Regular Maintenance Tasks

**Weekly:**
- Review error logs
- Check disk space
- Monitor response times

**Monthly:**
- Update dependencies (test in staging first)
- Review and archive old logs
- Performance optimization review

**Quarterly:**
- Security audit
- Backup restoration test
- Load testing
- Update SSL certificates (if not auto-renewing)

### Getting Help

- **Documentation:** This guide + Django docs
- **Logs:** `/var/log/staff-rota-[env]/`
- **System Logs:** `sudo journalctl -u staff-rota-[env]`
- **GitHub Issues:** Report bugs and feature requests

---

**Deployment Guide Version:** 1.0  
**Last Updated:** December 28, 2025  
**System Version:** Quick Win AI Features Complete
