# Production Server Connection Guide

**Site**: demo.therota.co.uk  
**Database**: staffrota_production  
**User**: staffrota_user  
**Password**: [STORED SECURELY]

## Quick Reference Commands

### 1. Connect to Server
```bash
# SSH to production server
ssh username@demo.therota.co.uk

# Or if using specific user/port
ssh -p 22 username@demo.therota.co.uk
```

### 2. Navigate to Django Project
```bash
# Common locations
cd /var/www/staff-rota-system
# OR
cd /home/staffrota/staff-rota-system
# OR
cd /opt/staff-rota-system

# Find Django project
find / -name "manage.py" 2>/dev/null | grep -v venv
```

### 3. Database Access (Read-Only Checks)
```bash
# PostgreSQL connection
psql -h localhost -U staffrota_user -d staffrota_production

# MySQL connection (if using MySQL)
mysql -u staffrota_user -p staffrota_production
```

### 4. Safe Diagnostic Commands
```bash
# Check Django installation
python manage.py --version

# Check for migration issues (READ ONLY)
python manage.py showmigrations

# Check system configuration (READ ONLY)
python manage.py check --deploy

# View recent logs (READ ONLY)
tail -100 /var/log/django/production.log
```

**CRITICAL**: All commands above are READ-ONLY and safe for production.
