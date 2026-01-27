# SOP: System Maintenance

**Document ID:** SOP-007  
**Version:** 1.0  
**Effective Date:** December 2025  
**Review Date:** March 2026  
**Owner:** IT Manager

---

## Purpose

This SOP defines procedures for maintaining the Staff Rota Management System, including backups, updates, troubleshooting, and system health monitoring.

## Scope

- System administrators and IT support staff
- Database backups and restoration
- Management command operations
- System monitoring and troubleshooting
- User access management

## Responsibilities

| Role | Responsibility |
|------|----------------|
| **IT Manager** | Overall system health, security, strategic decisions |
| **System Administrator** | Daily operations, backups, user management |
| **Developer/Support** | Updates, bug fixes, custom development |
| **Database Administrator** | Database optimization, migrations |

---

## Daily Operations

### Morning Health Check (Every Day at 9 AM)

**Steps:**

1. **Check Server Status**
   ```bash
   # Navigate to project directory
   cd /Users/deansockalingum/Staff\ Rota/rotasystems
   
   # Check if server is running
   ps aux | grep manage.py
   ```
   
   **Expected:** Python process running on port 8000

2. **Test System Access**
   - Open browser: `http://127.0.0.1:8000/`
   - Should load login page within 2 seconds
   - Test login with admin account
   - Check main dashboard loads

3. **Review Error Logs**
   ```bash
   # Check Django logs
   tail -50 logs/django_error.log
   
   # Check for critical errors
   grep "ERROR" logs/django_error.log | tail -20
   ```

4. **Check Automated Tasks**
   ```bash
   # Verify weekly staffing report ran (Mondays)
   ls -ltr exports/staffing_reports/ | tail -1
   
   # Check care plan review schedules updated
   python3 manage.py careplan_stats
   ```

5. **Review System Metrics**
   - Active users today
   - Database size
   - Disk space available
   - Response times

**Time Required:** 10-15 minutes

---

## Database Backup Procedures

### Automatic Daily Backup (Recommended)

**Setup Cron Job:**

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /Users/deansockalingum/Staff\ Rota/rotasystems && /usr/local/bin/python3 manage.py backup_database
```

**Backup Command:**

```bash
python3 manage.py backup_database
```

**Creates:**
- JSON export: `database_backup_YYYYMMDD_HHMMSS.json`
- SQLite copy: `db_backup_YYYYMMDD_HHMMSS.sqlite3`
- Stored in project root directory

**Retention Policy:**
- Keep daily backups for 7 days
- Keep weekly backups (Monday) for 4 weeks
- Keep monthly backups (1st of month) for 12 months
- Archive older backups to external storage

---

### Manual Backup (On Demand)

**When to Use:**
- Before major system updates
- Before running data migrations
- Before bulk data imports/deletions
- Weekly (if auto-backup not configured)

**Steps:**

1. **Navigate to Project Directory**
   ```bash
   cd /Users/deansockalingum/Staff\ Rota/rotasystems
   ```

2. **Run Backup Command**
   ```bash
   python3 manage.py backup_database
   ```

3. **Verify Backup Created**
   ```bash
   ls -lh database_backup_*.json | tail -1
   ls -lh db_backup_*.sqlite3 | tail -1
   ```

4. **Test Backup Integrity**
   ```bash
   # Check JSON file is valid
   python3 -c "import json; json.load(open('database_backup_YYYYMMDD_HHMMSS.json'))"
   ```

5. **Copy to Safe Location**
   ```bash
   # Copy to external drive
   cp database_backup_*.json /Volumes/BackupDrive/staff_rota_backups/
   cp db_backup_*.sqlite3 /Volumes/BackupDrive/staff_rota_backups/
   ```

**Time Required:** 2-5 minutes

---

### Backup Restoration

**Emergency Only - Data Loss Recovery**

**Prerequisites:**
- Stop the running server
- Have valid backup files
- Administrator access

**Steps:**

1. **Stop Server**
   ```bash
   # Find process ID
   ps aux | grep "manage.py runserver"
   
   # Kill process (use PID from above)
   kill [PID]
   ```

2. **Restore from JSON Backup**
   ```bash
   cd /Users/deansockalingum/Staff\ Rota/rotasystems
   
   # Clear current database (WARNING: DESTRUCTIVE)
   rm db.sqlite3
   
   # Run migrations to create fresh schema
   python3 manage.py migrate
   
   # Load backup data
   python3 manage.py loaddata database_backup_YYYYMMDD_HHMMSS.json
   ```

3. **Restore from SQLite Backup** (Alternative)
   ```bash
   # Backup current (corrupted) database
   mv db.sqlite3 db.sqlite3.corrupted
   
   # Copy backup as new database
   cp db_backup_YYYYMMDD_HHMMSS.sqlite3 db.sqlite3
   ```

4. **Verify Restoration**
   ```bash
   # Check data integrity
   python3 manage.py check
   
   # Count key records
   python3 -c "
   import os, django
   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
   django.setup()
   
   from scheduling.models import Staff, Resident, CarePlanReview
   print(f'Staff: {Staff.objects.count()}')
   print(f'Residents: {Resident.objects.count()}')
   print(f'Care Plan Reviews: {CarePlanReview.objects.count()}')
   "
   ```

5. **Restart Server**
   ```bash
   python3 manage.py runserver 0.0.0.0:8000 &
   ```

6. **Test System**
   - Log in as admin
   - Check recent data visible
   - Test key functions (create shift, request leave, etc.)

**Time Required:** 15-30 minutes

**Document Incident:**
- Date/time of failure
- Cause of data loss
- Backup used for restoration
- Data lost (if any)
- Lessons learned

---

## Management Commands Reference

### Staff Management

**List All Active Staff:**
```bash
python3 manage.py list_staff
```

**Add Staff Member:**
```bash
python3 manage.py add_staff --first-name "John" --last-name "Smith" --sap "SAP001234" --unit "DEMENTIA"
```

**Deactivate Staff Member:**
```bash
python3 manage.py deactivate_staff --sap "SAP001234"
```

---

### Care Plan Reviews

**Generate Missing Reviews:**
```bash
python3 manage.py generate_careplan_reviews
```

**Send Review Alerts:**
```bash
python3 manage.py send_careplan_alerts
```

**Care Plan Statistics:**
```bash
python3 manage.py careplan_stats
```

**Update Review Statuses:**
```bash
python3 manage.py update_careplan_status
```

---

### Annual Leave

**Calculate Leave Balances:**
```bash
python3 manage.py calculate_leave_balances
```

**Process Carry-Over:**
```bash
python3 manage.py process_leave_carryover --year 2026
```

**Leave Usage Report:**
```bash
python3 manage.py leave_usage_report
```

---

### Additional Staffing

**Generate Weekly Staffing Report:**
```bash
python3 manage.py generate_staffing_report --week-start 2025-12-02
```

**Send Weekly Report Email:**
```bash
python3 manage.py send_weekly_staffing_report
```

---

### Database Maintenance

**Check Database Integrity:**
```bash
python3 manage.py check --database default
```

**Run Migrations:**
```bash
# Check for pending migrations
python3 manage.py showmigrations

# Apply migrations
python3 manage.py migrate
```

**Clear Cache:**
```bash
python3 manage.py clear_cache
```

**Vacuum Database (SQLite):**
```bash
sqlite3 db.sqlite3 "VACUUM;"
```

---

### Import/Export

**Import Staff from CSV:**
```bash
python3 manage.py import_staff staff_list.csv
```

**Import Care Plan Data:**
```bash
python3 manage.py import_careplan_data careplan_data.csv
```

**Export Data:**
```bash
# Export all data
python3 manage.py dumpdata > full_export_YYYYMMDD.json

# Export specific app
python3 manage.py dumpdata scheduling > scheduling_export.json
```

---

## System Updates

### Minor Updates (Bug Fixes)

**When:** Monthly or as needed  
**Risk:** Low  
**Downtime:** Minimal (5-10 minutes)

**Steps:**

1. **Notify Users**
   - Email: "System maintenance tonight 10 PM - 10:30 PM"
   - Banner on website: "Maintenance in progress"

2. **Backup Database**
   ```bash
   python3 manage.py backup_database
   ```

3. **Pull Latest Code**
   ```bash
   cd /Users/deansockalingum/Staff\ Rota/rotasystems
   git pull origin main
   ```

4. **Install Dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

5. **Run Migrations**
   ```bash
   python3 manage.py migrate
   ```

6. **Restart Server**
   ```bash
   # Stop current server
   ps aux | grep manage.py
   kill [PID]
   
   # Start new server
   python3 manage.py runserver 0.0.0.0:8000 &
   ```

7. **Test System**
   - Log in
   - Test new features/fixes
   - Check error logs

8. **Notify Users**
   - Email: "Maintenance complete. System available."

---

### Major Updates (New Features)

**When:** Quarterly or as needed  
**Risk:** Medium-High  
**Downtime:** 1-2 hours

**Steps:**

1. **Plan Update**
   - Schedule during low-usage period (weekend/evening)
   - Notify users 1 week in advance
   - Prepare rollback plan

2. **Test in Staging Environment**
   - Clone production database to staging
   - Apply updates to staging
   - Test thoroughly (all features)
   - Fix any issues

3. **Backup Production**
   ```bash
   # Full backup
   python3 manage.py backup_database
   
   # Verify backup
   ls -lh database_backup_*.json
   
   # Copy to safe location
   cp database_backup_*.json /Volumes/BackupDrive/
   ```

4. **Apply Update to Production**
   - Follow minor update steps above
   - May include database schema changes
   - May require data migrations

5. **Post-Update Verification**
   - Test all critical features
   - Review error logs
   - Check performance
   - Monitor for 24-48 hours

6. **Document Changes**
   - Update SYSTEM_FEATURE_INDEX.md
   - Update version history
   - Update SOPs if processes changed

7. **User Training** (if UI changes)
   - Email summary of changes
   - Offer training sessions
   - Update help documentation

---

## Monitoring & Alerts

### Automated Monitoring (Setup)

**Cron Jobs to Configure:**

```bash
# Edit crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * cd /Users/deansockalingum/Staff\ Rota/rotasystems && python3 manage.py backup_database

# Update care plan review statuses at 8 AM daily
0 8 * * * cd /Users/deansockalingum/Staff\ Rota/rotasystems && python3 manage.py update_careplan_status

# Send care plan review alerts at 8:30 AM daily
30 8 * * * cd /Users/deansockalingum/Staff\ Rota/rotasystems && python3 manage.py send_careplan_alerts

# Weekly staffing report on Mondays at 8 AM
0 8 * * 1 cd /Users/deansockalingum/Staff\ Rota/rotasystems && python3 manage.py send_weekly_staffing_report

# Monthly leave balance calculation on 1st of month at midnight
0 0 1 * * cd /Users/deansockalingum/Staff\ Rota/rotasystems && python3 manage.py calculate_leave_balances

# Disk space check daily at 9 AM
0 9 * * * df -h | grep -E '(Filesystem|/Users)' | mail -s "Disk Space Report" admin@example.com
```

---

### Performance Monitoring

**Check Response Times:**
```bash
# Time a typical page load
time curl -o /dev/null -s http://127.0.0.1:8000/management/dashboard/
```

**Expected:** <1 second

**Database Query Performance:**
```bash
# Enable query logging in settings.py temporarily
# Check logs/queries.log for slow queries (>1 second)
```

**Disk Space:**
```bash
df -h
```

**Expected:** >20% free space

---

## Troubleshooting

### Issue: Server Won't Start

**Symptoms:** `python3 manage.py runserver` fails or exits immediately

**Diagnostic Steps:**

1. **Check for Errors**
   ```bash
   python3 manage.py check
   ```

2. **Check Port Availability**
   ```bash
   lsof -i :8000
   ```
   If port in use: Kill process or use different port

3. **Check Database Connection**
   ```bash
   python3 -c "
   import os, django
   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
   django.setup()
   from django.db import connection
   connection.ensure_connection()
   print('Database connection OK')
   "
   ```

4. **Check for Missing Migrations**
   ```bash
   python3 manage.py showmigrations | grep "\[ \]"
   ```
   If any unchecked: Run `python3 manage.py migrate`

---

### Issue: Slow Performance

**Symptoms:** Pages load slowly, timeouts

**Diagnostic Steps:**

1. **Check Database Size**
   ```bash
   ls -lh db.sqlite3
   ```
   If >500MB: Consider PostgreSQL migration

2. **Check for Long-Running Queries**
   - Enable DEBUG = True temporarily
   - Check Django Debug Toolbar
   - Look for N+1 query problems

3. **Optimize Database**
   ```bash
   # SQLite vacuum
   sqlite3 db.sqlite3 "VACUUM;"
   
   # Rebuild indexes
   python3 manage.py sqlflush | sqlite3 db.sqlite3
   ```

4. **Check Disk Space**
   ```bash
   df -h
   ```
   If <10% free: Clear old backups, logs

---

### Issue: Users Can't Log In

**Symptoms:** Correct credentials rejected

**Diagnostic Steps:**

1. **Check User Exists**
   ```bash
   python3 manage.py shell
   >>> from django.contrib.auth.models import User
   >>> User.objects.filter(username='jsmith').exists()
   ```

2. **Reset Password**
   ```bash
   python3 manage.py changepassword jsmith
   ```

3. **Check User is Active**
   ```bash
   python3 manage.py shell
   >>> User.objects.get(username='jsmith').is_active
   ```
   If False: Reactivate user

---

### Issue: Scheduled Tasks Not Running

**Symptoms:** Weekly reports not sent, backups missing

**Diagnostic Steps:**

1. **Check Crontab**
   ```bash
   crontab -l
   ```
   Verify jobs listed

2. **Check Cron Logs**
   ```bash
   # macOS
   log show --predicate 'process == "cron"' --last 1d
   
   # Linux
   grep CRON /var/log/syslog
   ```

3. **Test Command Manually**
   ```bash
   cd /Users/deansockalingum/Staff\ Rota/rotasystems
   python3 manage.py send_weekly_staffing_report
   ```
   Check for errors

4. **Check Email Configuration**
   - Verify EMAIL_HOST, EMAIL_PORT in settings.py
   - Test email sending

---

## Security Procedures

### User Access Audit

**Monthly Review:**

1. **List All Active Users**
   ```bash
   python3 manage.py list_users --active
   ```

2. **Check for Unused Accounts**
   - Last login >90 days ago = review
   - Never logged in = delete or remind

3. **Review Permissions**
   - Staff should not have admin access
   - Unit managers should only manage their units
   - Deactivated staff should have no access

4. **Check for Suspicious Activity**
   ```bash
   python3 manage.py access_log --days 30 --failed-logins
   ```

---

### Password Policy Enforcement

**Requirements:**
- Minimum 8 characters
- Contains uppercase, lowercase, number, special character
- Cannot be same as username
- Must change every 90 days (optional)
- Cannot reuse last 3 passwords (optional)

**Force Password Reset:**
```bash
python3 manage.py expire_passwords --days 90
```

---

### Data Protection Compliance

**GDPR Requirements:**

1. **Data Retention**
   - Active staff: Retained while employed
   - Left staff: Retained 7 years, then deleted
   - Audit logs: Retained 7 years

2. **Right to Access**
   - Staff can request their data
   - Export personal data: `python3 manage.py export_staff_data --sap SAP001234`

3. **Right to Deletion**
   - After 7-year retention: `python3 manage.py delete_staff_data --sap SAP001234 --confirm`

4. **Data Breach Procedure**
   - Notify IT Manager immediately
   - Notify Data Protection Officer within 24 hours
   - Notify affected individuals within 72 hours
   - Document incident in breach register

---

## Disaster Recovery

### Server Failure

**Recovery Time Objective (RTO):** 4 hours  
**Recovery Point Objective (RPO):** 24 hours (last backup)

**Steps:**

1. **Assess Damage**
   - Hardware failure?
   - Software corruption?
   - Data loss?

2. **Restore to Backup Server**
   - Copy latest backup to new/spare server
   - Follow restoration procedure above
   - Update DNS/network settings

3. **Test Functionality**
   - Verify all features working
   - Check data integrity
   - Test user logins

4. **Communicate with Users**
   - Estimated recovery time
   - What data (if any) was lost
   - Interim procedures

---

### Data Corruption

**If Database Corrupted:**

1. **Stop Using System Immediately**
   - Prevent further corruption
   - Notify all users

2. **Attempt Repair**
   ```bash
   sqlite3 db.sqlite3 "PRAGMA integrity_check;"
   ```

3. **If Repair Fails: Restore from Backup**
   - Use most recent backup
   - Document data loss period

4. **Root Cause Analysis**
   - Why did corruption occur?
   - How to prevent in future?

---

## Documentation Updates

**When to Update SOPs:**

- New features added to system
- Processes change
- User feedback identifies confusion
- Errors or incidents reveal gaps
- Quarterly review cycle

**Update Process:**

1. Identify SOP needing update
2. Draft changes
3. Review with stakeholders
4. Update version number and date
5. Notify all users of changes
6. Archive old version

---

## Contact Escalation

| Issue | Contact | Response Time |
|-------|---------|---------------|
| **Critical (System Down)** | IT Manager | 1 hour |
| **High (Feature Broken)** | System Administrator | 4 hours |
| **Medium (Question/Training)** | Help Desk | 1 business day |
| **Low (Enhancement Request)** | Project Manager | 1 week |

---

## Document History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | Dec 2025 | Initial SOP creation | IT Manager |

---

**For system maintenance support:**
- **IT Manager:** [Insert contact]
- **System Administrator:** [Insert contact]
- **Emergency Hotline:** [Insert number]

**Back to:** [SOP Index](SYSTEM_SOP_INDEX.md)
