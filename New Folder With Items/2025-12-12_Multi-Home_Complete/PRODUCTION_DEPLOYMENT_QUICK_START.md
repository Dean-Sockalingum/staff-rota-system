# 🚀 Production Deployment Quick Start Guide
**For HSCP/CGI IT Team**

Generated: December 26, 2025  
Estimated Deployment Time: **2-4 hours**

---

## 📋 Pre-Deployment Checklist

### What You'll Need
- [ ] Production server with Ubuntu 20.04+ or similar
- [ ] Root/sudo access to production server
- [ ] Production domain name (e.g., staffrota.hscp.gov.uk)
- [ ] SSL certificate (Let's Encrypt or purchased)
- [ ] PostgreSQL 12+ installed (recommended) OR SQLite (simpler)
- [ ] Python 3.9+ installed
- [ ] Email server credentials (can be configured later)

---

## ⚡ Quick Deployment (4 Steps)

### Step 1: Configure Environment (30 minutes)

```bash
# On production server
cd /opt/staff-rota-system

# Copy production environment template
cp .env.production.template .env.production

# Generate production SECRET_KEY
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
# Copy the output - you'll paste it in next step

# Edit production configuration
nano .env.production
```

**Required Changes in `.env.production`:**
```bash
DEBUG=False
SECRET_KEY=<PASTE_GENERATED_KEY_HERE>
ALLOWED_HOSTS=staffrota.hscp.gov.uk,www.staffrota.hscp.gov.uk
CSRF_TRUSTED_ORIGINS=https://staffrota.hscp.gov.uk,https://www.staffrota.hscp.gov.uk

# Database (choose one)
# Option A: PostgreSQL (recommended)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=staff_rota_production
DB_USER=staffrota_user
DB_PASSWORD=<YOUR_SECURE_PASSWORD>
DB_HOST=localhost
DB_PORT=5432

# Option B: SQLite (simpler, but not for high traffic)
# DB_ENGINE=django.db.backends.sqlite3
# DB_NAME=/opt/staff-rota-system/db_production.sqlite3
```

**Validate Configuration:**
```bash
python3 validate_production_config.py
```

You should see: ✓ Configuration is ready for production deployment

---

### Step 2: Install Dependencies (15 minutes)

```bash
# Install Python dependencies
pip3 install -r requirements.txt

# Install production web server
pip3 install gunicorn

# If using PostgreSQL
sudo apt-get install postgresql postgresql-contrib python3-psycopg2
```

---

### Step 3: Database Setup (30 minutes)

**For PostgreSQL:**
```bash
# Create database and user
sudo -u postgres psql

CREATE DATABASE staff_rota_production;
CREATE USER staffrota_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE staff_rota_production TO staffrota_user;
\q

# Run migrations
python3 manage.py migrate

# Create superuser
python3 manage.py createsuperuser

# Populate reference data
python3 manage.py populate_compliance_rules
python3 manage.py populate_training_courses
```

**For SQLite:**
```bash
# Run migrations
python3 manage.py migrate

# Create superuser
python3 manage.py createsuperuser

# Populate reference data
python3 manage.py populate_compliance_rules
python3 manage.py populate_training_courses
```

---

### Step 4: Deploy Web Server (1-2 hours)

**Option A: Nginx + Gunicorn (Recommended)**

Create systemd service:
```bash
sudo nano /etc/systemd/system/staffrota.service
```

Add:
```ini
[Unit]
Description=Staff Rota System
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/staff-rota-system
Environment="PATH=/opt/staff-rota-system/venv/bin"
ExecStart=/opt/staff-rota-system/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/opt/staff-rota-system/staffrota.sock \
    rotasystems.wsgi:application

[Install]
WantedBy=multi-user.target
```

Configure Nginx:
```bash
sudo nano /etc/nginx/sites-available/staffrota
```

Add:
```nginx
server {
    listen 80;
    server_name staffrota.hscp.gov.uk;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name staffrota.hscp.gov.uk;

    ssl_certificate /etc/ssl/certs/staffrota.crt;
    ssl_certificate_key /etc/ssl/private/staffrota.key;

    location /static/ {
        alias /var/www/staffrota/static/;
    }

    location /media/ {
        alias /var/www/staffrota/media/;
    }

    location / {
        proxy_pass http://unix:/opt/staff-rota-system/staffrota.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Collect static files and start:
```bash
# Collect static files
python3 manage.py collectstatic --noinput

# Enable and start services
sudo ln -s /etc/nginx/sites-available/staffrota /etc/nginx/sites-enabled/
sudo systemctl enable staffrota
sudo systemctl start staffrota
sudo systemctl reload nginx

# Check status
sudo systemctl status staffrota
```

**Option B: Simple Development Server (Testing Only)**
```bash
# NOT FOR PRODUCTION - Use for testing only
python3 manage.py runserver 0.0.0.0:8000
```

---

## ✅ Post-Deployment Verification

### 1. Test Basic Access
```bash
# Visit your domain
https://staffrota.hscp.gov.uk

# You should see the login page
# Default credentials from setup: username you created during createsuperuser
```

### 2. Run Security Check
```bash
python3 manage.py check --deploy
```

Should return: **System check identified no issues (0 silenced).**

### 3. Test Admin Access
```bash
# Visit admin panel
https://staffrota.hscp.gov.uk/admin/

# Login with superuser credentials
# Verify you can access all sections
```

### 4. Create Test Data (Optional)
```bash
# Import sample staff and shifts
python3 manage.py import_staff staff_import_template.csv
python3 manage.py generate_shifts --weeks 4
```

---

## 📊 Monitoring & Maintenance

### Daily Tasks
```bash
# Backup database (automate with cron)
python3 manage.py dbbackup

# View logs
tail -f /var/log/staffrota/django.log
```

### Weekly Tasks
- Review error logs
- Check disk space
- Verify backup integrity

### Monthly Tasks
- Update dependencies: `pip install -r requirements.txt --upgrade`
- Security audit
- Performance review

---

## 🔧 Troubleshooting

### Issue: 502 Bad Gateway
```bash
# Check Gunicorn status
sudo systemctl status staffrota

# Check Nginx error log
sudo tail -f /var/log/nginx/error.log

# Restart services
sudo systemctl restart staffrota
sudo systemctl restart nginx
```

### Issue: Static Files Not Loading
```bash
# Recollect static files
python3 manage.py collectstatic --noinput

# Check Nginx static file permissions
sudo chown -R www-data:www-data /var/www/staffrota/static/
```

### Issue: Database Connection Error
```bash
# Test PostgreSQL connection
psql -U staffrota_user -d staff_rota_production -h localhost

# Check credentials in .env.production
nano .env.production
```

---

## 📞 Support Contacts

**Technical Issues:**
- Review documentation in `/docs` folder
- Check Django logs: `/var/log/staffrota/`
- Review system logs: `sudo journalctl -u staffrota`

**For Urgent Production Issues:**
- System Administrator: [Contact Info]
- Database Administrator: [Contact Info]
- Application Developer: [Contact Info]

---

## 🎯 Success Criteria

Your deployment is successful when:

- ✅ Website accessible via HTTPS
- ✅ No errors in `python3 manage.py check --deploy`
- ✅ Admin panel accessible and functional
- ✅ Can create/view staff and shifts
- ✅ All security headers in place (check with: https://securityheaders.com)
- ✅ Automated backups running
- ✅ Monitoring/logging active

---

## 📚 Additional Documentation

For detailed information, see:
- `PRODUCTION_MIGRATION_CHECKLIST.md` - Comprehensive migration guide
- `ML_DEPLOYMENT_GUIDE.md` - ML features deployment
- `SYSTEM_HANDOVER_DOCUMENTATION.md` - Complete system documentation
- `USER_TRAINING_GUIDE_OM_SM.md` - User training materials

---

**Questions?** Review the documentation or contact the development team.

**Good luck with your deployment! 🚀**
