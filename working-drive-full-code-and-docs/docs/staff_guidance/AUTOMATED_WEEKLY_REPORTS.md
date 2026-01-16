# Automated Weekly Reports to Management

## Overview
The system automatically generates and sends **three key reports to management every Monday morning**, providing comprehensive oversight of operations, compliance, and staffing for the previous week.

---

## 1. Weekly Management Report
**Time:** Every Monday at **7:00 AM**  
**Coverage:** Previous Friday-Sunday (weekend coverage)  
**Recipients:** All management staff

### What's Included
- **Sickness Absences** - Staff who were absent over the weekend
- **Overtime Usage** - Staff working additional hours beyond their rota
- **Agency Staff** - External agency workers utilized
- **Hospital Admissions** - Residents admitted to hospital
- **Deaths** - Resident deaths (if any)
- **Incidents** - All incidents categorized by severity

### Report Sections

#### Sickness Data
```
Shows for each sick staff member:
- Name and SAP number
- Last working day
- Estimated return date
- Days absent
- Current status
```

#### Overtime Analysis
```
Weekend Overtime Metrics:
- Total overtime hours worked
- Number of staff working overtime
- Breakdown by staff member
- Shift details (dates, times, units)
```

#### Agency Staff Usage
```
For each agency worker:
- Agency company name
- Worker name
- Shifts worked
- Total hours
- Shift details
```

#### Incident Reports
```
Categorized by severity:
- CRITICAL - Immediate attention required
- HIGH - Serious incidents
- MEDIUM - Standard incidents
- LOW - Minor incidents

For each incident:
- Date and time
- Resident involved
- Description
- Reporter
- Actions taken
```

#### Hospital Admissions & Deaths
```
Hospital Admissions:
- Resident name
- Admission date
- Hospital
- Reason for admission

Deaths:
- Resident name
- Date of death
- Time of death (if recorded)
```

### Cron Schedule
```bash
# Every Monday at 7:00 AM
0 7 * * 1 cd /path/to/project && python3 manage.py generate_weekly_report --save --email
```

### Manual Testing
```bash
# Run report now
python3 manage.py generate_weekly_report

# Save to file
python3 manage.py generate_weekly_report --save

# For specific Monday
python3 manage.py generate_weekly_report --date 2025-12-16
```

### Files Generated
- **JSON Report:** `/tmp/weekly_report_YYYYMMDD.json`
- **Log File:** `logs/weekly_report.log`

---

## 2. Weekly Additional Staffing Report
**Time:** Every Monday at **8:00 AM**  
**Coverage:** Previous Sunday-Saturday (full week)  
**Recipients:** All management staff with active email addresses

### What's Included
- **Overtime Hours** - Permanent staff working beyond contracted hours
- **Agency Staff Usage** - External workers and associated costs
- **Cost Breakdown** - Financial impact by agency company
- **Shift Details** - Complete list of all additional shifts

### Report Sections

#### Summary Metrics
```
Total Additional Hours: XXX hours
Total Additional Shifts: XXX shifts
Total Agency Cost: £X,XXX.XX
```

#### Overtime Details
```
Staff Working Overtime:
- Total hours: XXX
- Total shifts: XXX
- Number of staff: XX people

Breakdown by Staff Member:
- Name (SAP)
- Total hours worked
- Number of shifts
- Dates worked
```

#### Agency Usage by Company
```
For Each Agency Company:
- Company name
- Day shifts vs Night shifts
- Total hours supplied
- Average cost per shift
- Total cost
- List of workers used

Example Companies:
- Newcross Healthcare (Day: £39.50, Night: £44.50)
- REED (Day: £41, Night: £46)
- Rapid Response Healthcare (Day: £40, Night: £45)
- Staffscanner (Day: £40, Night: £45)
```

#### Detailed Shift List
```
Each Additional Shift Shows:
- Date
- Shift type (Day/Night)
- Staff name (or Agency worker)
- Unit assigned
- Hours worked
- Cost (for agency)
```

### Email Format
The report is sent as:
- **HTML Email** - Formatted tables and styling
- **Plain Text Version** - For email clients that don't support HTML
- **Subject Line:** `Weekly Staffing Report - DD/MM/YYYY to DD/MM/YYYY`

### Cron Schedule
```bash
# Every Monday at 8:00 AM
0 8 * * 1 cd /path/to/project && python3 manage.py send_weekly_staffing_report
```

### Manual Testing
```bash
# Dry run (no email sent)
python3 manage.py send_weekly_staffing_report --dry-run

# Test for previous week
python3 manage.py send_weekly_staffing_report

# Test for specific week
python3 manage.py send_weekly_staffing_report --week-start 2025-12-01

# Send to specific email (testing)
python3 manage.py send_weekly_staffing_report --email manager@example.com
```

### Special Cases

**No Additional Staffing Used:**
If no overtime or agency staff were used during the week, managers receive a simple confirmation email:
```
Subject: Weekly Staffing Report - DD/MM/YYYY to DD/MM/YYYY

No additional staffing (overtime or agency) was used during the week.
All shifts were covered by regular scheduled staff.
```

### Log File
`logs/weekly_staffing_report.log` - Contains execution history and any errors

---

## 3. Weekly Compliance Summary
**Time:** Every Sunday at **3:00 AM** (for previous 30 days)  
**Coverage:** Rolling 30-day compliance check  
**Recipients:** Management and compliance officers

### What's Included
- **Training Compliance** - Staff with expired or expiring training
- **Supervision Records** - Overdue supervision sessions
- **Induction Progress** - New staff induction completion
- **Compliance Violations** - System-detected policy breaches
- **Audit Activity** - Recent data changes and system access

### Report Sections

#### Training Compliance
```
Shows:
- Staff with expired training certificates
- Training expiring in next 30 days
- Courses requiring renewal
- Completion rates by course type
```

#### Supervision Status
```
Tracks:
- Staff requiring supervision
- Overdue supervision sessions
- Last supervision date
- Next due date
```

#### Compliance Violations
```
Categories:
- Attendance issues
- Training gaps
- Documentation missing
- Policy breaches

Each violation shows:
- Staff member affected
- Violation type
- Date detected
- Severity level
- Status (Open/Resolved)
```

### Cron Schedule
```bash
# Every Sunday at 3:00 AM (weekly full check)
0 3 * * 0 cd /path/to/project && python3 manage.py run_compliance_checks \
  --start-date $(date -d '30 days ago' +%Y-%m-%d) \
  --end-date $(date +%Y-%m-%d)
```

### Additional Daily Check
```bash
# Every day at 2:00 AM (7-day rolling check)
0 2 * * * cd /path/to/project && python3 manage.py scheduled_compliance_check \
  --notify --period-days 7
```

### Manual Testing
```bash
# Run full compliance check
python3 manage.py run_compliance_checks

# Check specific date range
python3 manage.py run_compliance_checks \
  --start-date 2025-11-01 \
  --end-date 2025-12-01

# Daily automated check
python3 manage.py scheduled_compliance_check --notify --period-days 7
```

---

## Installation & Setup

### Installing All Reports

#### 1. Weekly Management Report
```bash
cd /path/to/project
./install_weekly_report.sh
```

#### 2. Weekly Staffing Report
```bash
cd /path/to/project
./install_weekly_staffing_report.sh
```

#### 3. Compliance Checks
```bash
cd /path/to/project
./setup_compliance_cron.sh
```

### Viewing Installed Cron Jobs
```bash
# List all cron jobs
crontab -l

# Filter for rota system jobs
crontab -l | grep -E 'weekly|compliance|staffing'
```

### Expected Cron Output
```
0 7 * * 1 cd /path/to/project && python3 manage.py generate_weekly_report --save --email
0 8 * * 1 cd /path/to/project && python3 manage.py send_weekly_staffing_report
0 2 * * * cd /path/to/project && python3 manage.py scheduled_compliance_check --notify --period-days 7
0 3 * * 0 cd /path/to/project && python3 manage.py run_compliance_checks
```

---

## Monitoring & Troubleshooting

### Check Report Execution

#### View Logs
```bash
# Weekly management report
tail -f logs/weekly_report.log

# Weekly staffing report
tail -f logs/weekly_staffing_report.log

# Compliance checks
tail -f /tmp/compliance_check.log
tail -f /tmp/compliance_weekly.log
```

#### Check Last Execution
```bash
# View cron execution history (macOS/Linux)
grep CRON /var/log/system.log | tail -20

# Check if cron service is running
ps aux | grep cron
```

### Common Issues

#### Reports Not Sending

**1. Check Cron Job Exists**
```bash
crontab -l | grep weekly
```
If no output, re-run installation scripts.

**2. Check Email Configuration**
Verify in `rotasystems/settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
```

**3. Check Recipients**
```bash
# Test staffing report
python3 manage.py send_weekly_staffing_report --dry-run

# Look for email addresses
```
Managers must have:
- `role.is_management = True`
- `is_active = True`
- Valid email address set

**4. Check Permissions**
```bash
# Ensure project directory is accessible
ls -la /path/to/project

# Ensure logs directory exists
mkdir -p /path/to/project/logs
chmod 755 /path/to/project/logs
```

#### Empty Reports

**No Data Shows Up:**
- Check date ranges in commands
- Verify data exists in database
- Run manual test to see console output

**No Agency/Overtime Data:**
- Verify `shift_classification` field is set correctly
- Check shifts have `OVERTIME` or `AGENCY` classification
- Confirm date range covers the period

#### Cron Not Running

**1. Check Cron Service (Linux)**
```bash
sudo systemctl status cron
sudo systemctl start cron
```

**2. Check Cron Service (macOS)**
```bash
sudo launchctl list | grep cron
```

**3. Check Path Issues**
Cron may not have same PATH as your shell:
```bash
# Edit crontab
crontab -e

# Add PATH at top
PATH=/usr/local/bin:/usr/bin:/bin
```

---

## Report Recipients

### Who Receives Each Report

**Weekly Management Report (7:00 AM Monday)**
- All users with `role.is_management = True`
- Active users only (`is_active = True`)
- Configured in future email implementation

**Weekly Staffing Report (8:00 AM Monday)**
- All users with `role.is_management = True`
- Active users only (`is_active = True`)
- Must have valid email address

**Weekly Compliance Summary (3:00 AM Sunday)**
- Management staff
- Compliance officers
- HR administrators (if configured)

### Customizing Recipients

To send to specific email addresses during testing:
```bash
# Staffing report to one person
python3 manage.py send_weekly_staffing_report --email yourname@example.com

# Or edit the command in send_weekly_staffing_report.py to customize logic
```

---

## Key Benefits of Automated Reports

### For Management
✅ **No Manual Work** - Reports generated automatically  
✅ **Consistent Schedule** - Every Monday morning, without fail  
✅ **Complete Coverage** - All weekend activity captured  
✅ **Cost Visibility** - Agency spending tracked weekly  
✅ **Compliance Oversight** - Training and supervision monitored  
✅ **Early Warning** - Issues flagged before they escalate

### For Operations
✅ **Data-Driven Decisions** - Concrete metrics for planning  
✅ **Resource Optimization** - Identify overtime patterns  
✅ **Budget Control** - Track agency costs weekly  
✅ **Risk Management** - Incident trends identified  
✅ **Regulatory Compliance** - Care Inspectorate requirements met

### For Staff
✅ **Transparency** - Clear oversight of operations  
✅ **Fairness** - Overtime tracked objectively  
✅ **Support** - Sickness patterns identified for wellbeing  
✅ **Recognition** - Additional hours documented

---

## Quick Reference Card

### Monday Morning Reports Timeline

| Time | Report | Coverage | Focus |
|------|--------|----------|-------|
| **7:00 AM** | Weekly Management Report | Fri-Sun | Incidents, sickness, critical events |
| **8:00 AM** | Weekly Staffing Report | Sun-Sat | Overtime, agency, costs |

### Sunday Night Report

| Time | Report | Coverage | Focus |
|------|--------|----------|-------|
| **3:00 AM** | Weekly Compliance Check | 30 days | Training, supervision, violations |

### Daily Report

| Time | Report | Coverage | Focus |
|------|--------|----------|-------|
| **2:00 AM** | Daily Compliance Check | 7 days | Urgent compliance issues |

---

## Testing Before Monday

Don't wait until Monday to verify reports work:

```bash
# Test all three reports NOW
cd /path/to/project

# 1. Weekly management report (dry run)
python3 manage.py generate_weekly_report

# 2. Weekly staffing report (dry run - no email)
python3 manage.py send_weekly_staffing_report --dry-run

# 3. Compliance check
python3 manage.py scheduled_compliance_check --period-days 7

# If all work, check cron is configured
crontab -l | grep -E 'weekly|compliance'
```

---

## Future Enhancements

**Planned Features:**
- 📧 **Email Distribution** - HTML emails with formatted tables
- 📊 **PDF Attachments** - Professional PDF reports attached to emails
- 📈 **Trend Analysis** - Week-over-week comparisons and charts
- 🔔 **SMS Alerts** - Critical incidents sent via text message
- 💾 **Database Archiving** - Historical reports stored for audits
- 📱 **Mobile Push** - Notifications to management mobile apps
- 🤖 **AI Insights** - Automated pattern detection and recommendations

---

## Related Documentation

- **[Weekly Report Guide](WEEKLY_REPORT_GUIDE.md)** - Detailed technical documentation
- **[Weekly Report Quick Ref](WEEKLY_REPORT_QUICK_REF.md)** - Fast reference for common tasks
- **[Email Setup Guide](EMAIL_SETUP_PRODUCTION.md)** - Configuring email for reports
- **[Compliance Web Forms](COMPLIANCE_WEB_FORMS_COMPLETE.md)** - Compliance system overview
- **[Manager Dashboard Guide](AI_ASSISTANT_GUIDE.md)** - Using the management interface

---

**Document Version:** 1.0  
**Last Updated:** December 20, 2025  
**Status:** Production Ready ✅
