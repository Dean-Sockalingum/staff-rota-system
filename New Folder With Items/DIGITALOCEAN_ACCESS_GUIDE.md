# DigitalOcean Console Access Guide

## Step 1: Access DigitalOcean Console

1. **Go to**: https://cloud.digitalocean.com/
2. **Login** with your credentials
3. **Navigate to**: Droplets (left sidebar)
4. **Find your droplet**: Should be named something like "staff-rota-prod" or similar
5. **Click** on the droplet name
6. **Click "Console"** button (top right, next to "More" dropdown)

This opens a browser-based terminal directly to your server.

---

## Step 2: Login to Your Droplet

Once the console loads, you'll be prompted to login:

```
login: root
# OR
login: staffrota_user
# OR  
login: ubuntu
```

**Common usernames for DigitalOcean droplets:**
- `root` (if you haven't created another user)
- `staffrota_user` (if you created this user)
- `ubuntu` (if using Ubuntu image)

**Password**: [Your server password, NOT the database password]

---

## Step 3: Run Basic Health Check

Once logged in, run:

```bash
# Download the health check script
wget https://raw.githubusercontent.com/YOUR_REPO/production_health_check.sh

# Make it executable
chmod +x production_health_check.sh

# Run it
./production_health_check.sh
```

**OR** run commands manually:

```bash
# 1. Find Django project
find /home /var/www /opt -name "manage.py" -type f 2>/dev/null | grep -v venv

# 2. Check disk space
df -h

# 3. Check memory
free -h

# 4. Check running processes
ps aux | grep python | grep -v grep

# 5. Check web server
systemctl status nginx
```

---

## Step 4: Navigate to Django Project

Based on the output from Step 3, find your project path:

```bash
# Common locations:
cd /var/www/staff-rota-system
# OR
cd /home/staffrota_user/staff-rota-system
# OR
cd /opt/staff-rota-system

# Activate virtualenv
source venv/bin/activate
# OR
source env/bin/activate
```

---

## Step 5: Run Django Health Checks

```bash
# System check
python manage.py check --deploy

# Migration status
python manage.py showmigrations

# Test database connection
python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('✅ DB Connected')"

# Count records
python manage.py shell -c "
from scheduling.models import User, Shift
print(f'Staff: {User.objects.count()}')
print(f'Shifts: {Shift.objects.count()}')
"
```

---

## Step 6: Check Logs

```bash
# Django logs
tail -50 /var/log/django/production.log
# OR
tail -50 /var/log/supervisor/*.log

# Nginx logs
tail -50 /var/log/nginx/error.log
tail -50 /var/log/nginx/access.log

# System logs
journalctl -u gunicorn -n 50
# OR
journalctl -u nginx -n 50
```

---

## Step 7: Database Direct Access (Optional)

```bash
# Connect to PostgreSQL
psql -U staffrota_user -d staffrota_production

# Inside psql, run:
\dt  -- List tables
\d scheduling_user  -- Describe user table
SELECT COUNT(*) FROM scheduling_user;  -- Count users
\q  -- Quit
```

---

## Common Issues & Solutions

### Issue: Can't find Django project
```bash
# Search more directories
find / -name "manage.py" -type f 2>/dev/null | grep -v venv
```

### Issue: Permission denied
```bash
# Switch to root if needed
sudo su -
# OR
sudo -i
```

### Issue: Virtualenv not found
```bash
# Find virtualenv
find /var/www /home /opt -type d -name "venv" -o -name "env" 2>/dev/null
```

### Issue: Service not running
```bash
# Restart services
sudo systemctl restart nginx
sudo systemctl restart gunicorn
# OR
sudo systemctl restart uwsgi
```

---

## Quick Production Health Checklist

Run these commands and share the output:

```bash
# 1. Find project
find / -name "manage.py" -type f 2>/dev/null | grep -v venv | head -3

# 2. Check services
systemctl status nginx --no-pager
systemctl status gunicorn --no-pager || systemctl status uwsgi --no-pager

# 3. Check database
systemctl status postgresql --no-pager

# 4. Disk space
df -h | grep -E "Filesystem|/$"

# 5. Memory
free -h

# 6. Recent errors
tail -30 /var/log/nginx/error.log
```

---

## What to Share With Me

After running the commands, share:

1. **Django project path**: (from find command)
2. **Service status**: (nginx, gunicorn/uwsgi output)
3. **Disk/memory**: (df -h, free -h output)
4. **Any errors**: (from log files)
5. **Django check output**: (python manage.py check --deploy)

I'll analyze and help troubleshoot any issues found!

---

## Safety Reminders

✅ **READ-ONLY commands are safe**:
- `ls`, `cat`, `tail`, `grep`, `find`
- `python manage.py check`
- `python manage.py showmigrations`
- `SELECT` queries in database

⚠️ **CAREFUL with these**:
- `python manage.py migrate` (changes database)
- `systemctl restart` (restarts services)
- `rm`, `mv`, `cp` (modifies files)

🚫 **NEVER run without confirmation**:
- `python manage.py flush` (deletes data!)
- `DROP TABLE` (deletes data!)
- `rm -rf` (deletes files!)

---

**Ready to start? Let me know what you see in the DigitalOcean console!**
