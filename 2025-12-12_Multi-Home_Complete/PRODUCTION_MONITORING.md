# Production Monitoring & Maintenance Guide

**Staff Rota System**  
**Date:** January 16, 2026  
**Status:** Production Monitoring Setup

---

## 📊 Application Monitoring

### 1. Real-Time Log Monitoring

#### Django Application Logs
```bash
# Follow Django application logs
tail -f /home/staff-rota-system/logs/django.log

# Search for errors
grep ERROR /home/staff-rota-system/logs/django.log | tail -20

# Search for specific user activity
grep "SAP: 000541" /home/staff-rota-system/logs/django.log
```

#### Gunicorn Logs
```bash
# Follow Gunicorn access logs
tail -f /home/staff-rota-system/logs/gunicorn.log

# Follow Gunicorn error logs
tail -f /home/staff-rota-system/logs/gunicorn_error.log

# Check for worker crashes
grep "Worker" /home/staff-rota-system/logs/gunicorn_error.log
```

#### Nginx Logs
```bash
# Follow Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Follow Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Check for 502/503 errors
sudo grep "502\|503" /var/log/nginx/error.log | tail -20
```

### 2. Application Status Checks

```bash
# Check if application is running
sudo supervisorctl status staff-rota

# View all supervisor processes
sudo supervisorctl status

# Restart application
sudo supervisorctl restart staff-rota

# Stop application
sudo supervisorctl stop staff-rota

# Start application
sudo supervisorctl start staff-rota
```

### 3. Database Monitoring

```bash
# Check database status
python manage.py shell

# In Django shell:
from scheduling.models import User, CareHome, Unit, ShiftType
from django.db import connection

# Check record counts
print(f"Users: {User.objects.count()}")
print(f"Care Homes: {CareHome.objects.count()}")
print(f"Units: {Unit.objects.count()}")
print(f"Shift Types: {ShiftType.objects.count()}")

# Check database size
with connection.cursor() as cursor:
    cursor.execute("SELECT pg_size_pretty(pg_database_size('rotasystem'));")
    print(f"Database size: {cursor.fetchone()[0]}")
```

#### PostgreSQL Performance
```bash
# Check PostgreSQL connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# View active queries
sudo -u postgres psql -d rotasystem -c "
SELECT pid, usename, application_name, client_addr, state, query 
FROM pg_stat_activity 
WHERE state != 'idle';
"

# Database size
sudo -u postgres psql -c "
SELECT datname, pg_size_pretty(pg_database_size(datname)) 
FROM pg_database 
WHERE datname = 'rotasystem';
"

# Table sizes
sudo -u postgres psql -d rotasystem -c "
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables 
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC 
LIMIT 10;
"
```

---

## 🖥️ System Resource Monitoring

### CPU & Memory

```bash
# Overall system status
htop

# CPU usage
top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"%"}'

# Memory usage
free -h

# Memory by process
ps aux --sort=-%mem | head -10

# Python processes
ps aux | grep python
```

### Disk Space

```bash
# Overall disk usage
df -h

# Directory sizes
du -sh /home/staff-rota-system/*
du -sh /var/www/staff-rota/*

# Find large files
find /home/staff-rota-system -type f -size +100M

# Check inode usage
df -i
```

### Network

```bash
# Active connections
netstat -tulpn | grep python

# Check if port 8000 is listening
sudo lsof -i :8000

# Network traffic
sudo iftop
```

---

## 🔔 Automated Monitoring Scripts

### Health Check Script

Create `/home/staff-rota-system/health_check.sh`:

```bash
#!/bin/bash

LOGFILE="/home/staff-rota-system/logs/health_check.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Check if application is running
if sudo supervisorctl status staff-rota | grep -q RUNNING; then
    echo "[$DATE] ✅ Application RUNNING" >> $LOGFILE
else
    echo "[$DATE] ❌ Application DOWN - Attempting restart" >> $LOGFILE
    sudo supervisorctl restart staff-rota
    
    # Send alert email
    echo "Staff Rota application was down and has been restarted at $DATE" | \
        mail -s "ALERT: Staff Rota System Restarted" admin@therota.co.uk
fi

# Check database connectivity
cd /home/staff-rota-system
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=rotasystems.settings_production

if python manage.py dbshell --command="SELECT 1;" &>/dev/null; then
    echo "[$DATE] ✅ Database connection OK" >> $LOGFILE
else
    echo "[$DATE] ❌ Database connection FAILED" >> $LOGFILE
    echo "Database connection failed at $DATE" | \
        mail -s "ALERT: Staff Rota Database Error" admin@therota.co.uk
fi

# Check disk space (alert if > 80%)
DISK_USAGE=$(df / | grep / | awk '{print $5}' | sed 's/%//g')
if [ "$DISK_USAGE" -gt 80 ]; then
    echo "[$DATE] ⚠️ Disk usage at ${DISK_USAGE}%" >> $LOGFILE
    echo "Disk usage is at ${DISK_USAGE}% at $DATE" | \
        mail -s "WARNING: High Disk Usage" admin@therota.co.uk
else
    echo "[$DATE] ✅ Disk usage OK (${DISK_USAGE}%)" >> $LOGFILE
fi
```

```bash
# Make executable
chmod +x /home/staff-rota-system/health_check.sh

# Add to crontab (run every 5 minutes)
*/5 * * * * /home/staff-rota-system/health_check.sh
```

### Performance Monitor Script

Create `/home/staff-rota-system/performance_monitor.sh`:

```bash
#!/bin/bash

LOGFILE="/home/staff-rota-system/logs/performance.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# CPU usage
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')

# Memory usage
MEM_USAGE=$(free | grep Mem | awk '{print ($3/$2) * 100.0}')

# Disk usage
DISK_USAGE=$(df / | grep / | awk '{print $5}' | sed 's/%//g')

# Active connections
CONNECTIONS=$(sudo supervisorctl status staff-rota | grep -c RUNNING)

# Database size
DB_SIZE=$(sudo -u postgres psql -d rotasystem -t -c "SELECT pg_size_pretty(pg_database_size('rotasystem'));" | tr -d ' ')

# Log metrics
echo "[$DATE] CPU:${CPU_USAGE}% MEM:${MEM_USAGE}% DISK:${DISK_USAGE}% DB:${DB_SIZE} CONN:${CONNECTIONS}" >> $LOGFILE

# Alert if CPU > 80%
if (( $(echo "$CPU_USAGE > 80" | bc -l) )); then
    echo "High CPU usage: ${CPU_USAGE}% at $DATE" | \
        mail -s "WARNING: High CPU Usage" admin@therota.co.uk
fi

# Alert if Memory > 85%
if (( $(echo "$MEM_USAGE > 85" | bc -l) )); then
    echo "High memory usage: ${MEM_USAGE}% at $DATE" | \
        mail -s "WARNING: High Memory Usage" admin@therota.co.uk
fi
```

```bash
# Make executable
chmod +x /home/staff-rota-system/performance_monitor.sh

# Add to crontab (run every 15 minutes)
*/15 * * * * /home/staff-rota-system/performance_monitor.sh
```

---

## 💾 Automated Backup System

### Database Backup Script

Create `/home/staff-rota-system/backup_database.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/home/backups/staff-rota"
DATE=$(date +%Y%m%d_%H%M%S)
DAY=$(date +%A)
LOGFILE="/home/staff-rota-system/logs/backup.log"

mkdir -p $BACKUP_DIR

echo "[$(date)] Starting database backup..." >> $LOGFILE

# Daily backup
sudo -u postgres pg_dump rotasystem | gzip > $BACKUP_DIR/db_daily_$DATE.sql.gz

# Weekly backup (Sunday)
if [ "$DAY" == "Sunday" ]; then
    sudo -u postgres pg_dump rotasystem | gzip > $BACKUP_DIR/db_weekly_$DATE.sql.gz
    echo "[$(date)] Weekly backup created" >> $LOGFILE
fi

# Monthly backup (1st of month)
if [ $(date +%d) == "01" ]; then
    sudo -u postgres pg_dump rotasystem | gzip > $BACKUP_DIR/db_monthly_$DATE.sql.gz
    echo "[$(date)] Monthly backup created" >> $LOGFILE
fi

# Media files backup
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/staff-rota/media/

# Cleanup: Keep daily backups for 7 days
find $BACKUP_DIR -name "db_daily_*.sql.gz" -mtime +7 -delete
find $BACKUP_DIR -name "media_*.tar.gz" -mtime +7 -delete

# Keep weekly backups for 30 days
find $BACKUP_DIR -name "db_weekly_*.sql.gz" -mtime +30 -delete

# Keep monthly backups for 365 days
find $BACKUP_DIR -name "db_monthly_*.sql.gz" -mtime +365 -delete

echo "[$(date)] Backup completed. Size: $(du -sh $BACKUP_DIR | cut -f1)" >> $LOGFILE

# Verify backup integrity
if gunzip -t $BACKUP_DIR/db_daily_$DATE.sql.gz 2>/dev/null; then
    echo "[$(date)] Backup integrity verified ✅" >> $LOGFILE
else
    echo "[$(date)] Backup integrity check FAILED ❌" >> $LOGFILE
    echo "Database backup failed integrity check at $(date)" | \
        mail -s "ALERT: Backup Integrity Failed" admin@therota.co.uk
fi
```

```bash
# Make executable
chmod +x /home/staff-rota-system/backup_database.sh

# Add to crontab (run daily at 2 AM)
0 2 * * * /home/staff-rota-system/backup_database.sh
```

### Backup Restoration

```bash
# List available backups
ls -lh /home/backups/staff-rota/

# Restore from backup
gunzip < /home/backups/staff-rota/db_daily_YYYYMMDD_HHMMSS.sql.gz | \
    sudo -u postgres psql rotasystem

# Restore media files
tar -xzf /home/backups/staff-rota/media_YYYYMMDD_HHMMSS.tar.gz -C /
```

---

## 🔧 Maintenance Tasks

### Daily Tasks

```bash
# 1. Check application status
sudo supervisorctl status staff-rota

# 2. Review error logs
grep ERROR /home/staff-rota-system/logs/django.log | tail -20

# 3. Check disk space
df -h

# 4. Verify backups completed
tail /home/staff-rota-system/logs/backup.log
```

### Weekly Tasks

```bash
# 1. Update system packages
sudo apt update && sudo apt upgrade -y

# 2. Restart application for updates
sudo supervisorctl restart staff-rota

# 3. Clean old log files (keep 30 days)
find /home/staff-rota-system/logs -name "*.log" -mtime +30 -delete

# 4. Vacuum database
sudo -u postgres psql -d rotasystem -c "VACUUM ANALYZE;"

# 5. Check SSL certificate expiry
sudo certbot certificates
```

### Monthly Tasks

```bash
# 1. Review user activity logs
python manage.py shell -c "
from scheduling.models import User
from django.utils import timezone
from datetime import timedelta
last_month = timezone.now() - timedelta(days=30)
active_users = User.objects.filter(last_login__gte=last_month).count()
print(f'Active users (last 30 days): {active_users}')
"

# 2. Database statistics
sudo -u postgres psql -d rotasystem -c "
SELECT schemaname, tablename, n_live_tup, n_dead_tup
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;
"

# 3. Check for Django updates
cd /home/staff-rota-system
source venv/bin/activate
pip list --outdated

# 4. Review and archive old logs
tar -czf /home/backups/staff-rota/logs_$(date +%Y%m).tar.gz \
    /home/staff-rota-system/logs/*.log
```

---

## 📈 Performance Optimization

### Database Optimization

```bash
# Analyze query performance
sudo -u postgres psql -d rotasystem -c "
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;
"

# Create indexes (if needed based on slow queries)
python manage.py dbshell
# Example: CREATE INDEX idx_user_sap ON scheduling_user(sap);

# Update statistics
sudo -u postgres psql -d rotasystem -c "ANALYZE;"
```

### Static File Optimization

```bash
# Compress static files
cd /var/www/staff-rota/staticfiles
find . -type f \( -name "*.css" -o -name "*.js" \) -exec gzip -k {} \;

# Enable Nginx gzip compression in /etc/nginx/nginx.conf
```

### Application Performance

```bash
# Check for slow requests in Gunicorn logs
grep -E "slow|timeout" /home/staff-rota-system/logs/gunicorn.log

# Monitor response times
tail -f /var/log/nginx/access.log | awk '{print $NF}' | sort -n
```

---

## 🚨 Alerting & Notifications

### Email Alerts Setup

```bash
# Install mailutils
sudo apt install mailutils

# Configure email in Django settings
# Already configured in settings_production.py

# Test email
python manage.py shell
from django.core.mail import send_mail
send_mail(
    'Test Alert',
    'This is a test alert from Staff Rota System',
    'noreply@therota.co.uk',
    ['admin@therota.co.uk'],
)
```

### Critical Alerts

The monitoring scripts above send alerts for:
- ❌ Application downtime
- ❌ Database connection failures
- ⚠️ High disk usage (> 80%)
- ⚠️ High CPU usage (> 80%)
- ⚠️ High memory usage (> 85%)
- ❌ Backup failures

---

## 📱 Quick Reference Commands

```bash
# Application Management
sudo supervisorctl status staff-rota          # Check status
sudo supervisorctl restart staff-rota         # Restart app
sudo supervisorctl tail -f staff-rota stderr  # Follow error logs

# Log Viewing
tail -f /home/staff-rota-system/logs/django.log        # Django logs
tail -f /home/staff-rota-system/logs/gunicorn.log      # Gunicorn logs
sudo tail -f /var/log/nginx/error.log                  # Nginx logs

# Database
sudo -u postgres psql rotasystem              # Connect to DB
python manage.py dbshell                       # Django DB shell

# System Resources
htop                                           # System monitor
df -h                                          # Disk space
free -h                                        # Memory usage

# Backups
/home/staff-rota-system/backup_database.sh    # Manual backup
ls -lh /home/backups/staff-rota/              # List backups

# Updates
cd /home/staff-rota-system && git pull         # Pull code updates
source venv/bin/activate && pip install -r requirements.txt  # Update deps
python manage.py migrate                       # Run migrations
python manage.py collectstatic --noinput       # Collect static
sudo supervisorctl restart staff-rota          # Restart app
```

---

## 📞 Troubleshooting Quick Guide

| Problem | Solution |
|---------|----------|
| 502 Bad Gateway | Check if Gunicorn running: `sudo supervisorctl status staff-rota` |
| Database connection error | Check PostgreSQL: `sudo systemctl status postgresql` |
| Static files not loading | Re-collect: `python manage.py collectstatic --noinput` |
| High memory usage | Restart Gunicorn: `sudo supervisorctl restart staff-rota` |
| Disk full | Clean old logs and backups |
| SSL certificate expired | Renew: `sudo certbot renew` |
| Slow response times | Check database queries and add indexes |

---

**Last Updated:** January 16, 2026  
**Maintained By:** System Administrator  
**Support Contact:** admin@therota.co.uk
