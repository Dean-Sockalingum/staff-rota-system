# Annual Leave Email Reminders - Quick Start Guide

## 🚀 Quick Commands

All automation is now set up! You can use either **manual commands** or **automated scheduling**.

---

## Option 1: Manual Email Sending (Simple)

Use the convenient wrapper script:

```bash
cd /Users/deansockalingum/Staff\ Rota/rotasystems

# Test first (preview mode)
./send_leave_emails.sh test

# Send monthly reminder (5+ days remaining)
./send_leave_emails.sh monthly

# Send quarterly reminder (1+ days remaining)
./send_leave_emails.sh quarterly

# Send urgent year-end (all staff)
./send_leave_emails.sh urgent

# Send to specific person
./send_leave_emails.sh specific ADMIN001
```

---

## Option 2: Automated Scheduling (Cron)

The automation script has been updated with 4 automated schedules:

### Install Automation

```bash
cd /Users/deansockalingum/Staff\ Rota/rotasystems
chmod +x install_scheduled_tasks.sh
./install_scheduled_tasks.sh
```

### Verify Installation

```bash
crontab -l
```

You should see these entries:

| Schedule | Day | Time | Command | Filters |
|----------|-----|------|---------|---------|
| **Monthly** | 1st of every month | 9:00 AM | `send_leave_reminders` | `--min-days 5` |
| **Quarterly** | 1st of Jan/Apr/Jul/Oct | 9:00 AM | `send_leave_reminders` | `--min-days 1` |
| **Year-end Urgent** | December 1st | 9:00 AM | `send_leave_reminders` | All staff |
| **Final Warning** | December 15th | 9:00 AM | `send_leave_reminders` | All staff |

---

## 📧 Email Preview

Each email contains:

- **Header**: Beautiful purple gradient with facility logo
- **Greeting**: Personalized "Dear [Name]"
- **Leave Summary Box**:
  - Total entitlement
  - Used so far
  - **Remaining** (highlighted)
- **Urgency Indicator**: 🔴 High / 🟡 Medium / 🟢 Low
- **Call to Action**: "Request Leave Now" button
- **Instructions**: Step-by-step guide
- **Contact**: Support information

### Urgency Levels

| Days Remaining | Urgency | Color | Message |
|----------------|---------|-------|---------|
| 0-5 days | HIGH | 🔴 Red | "URGENT: Please book your leave immediately" |
| 5-10 days | MEDIUM | 🟡 Amber | "Please book your leave soon" |
| 10+ days | LOW | 🟢 Green | "You have time to plan your leave" |

---

## 📊 Testing & Validation

### Test Email (Dry Run)

```bash
# Preview what would be sent to ADMIN001
./send_leave_emails.sh test

# Or use the full command
python3 manage.py send_leave_reminders --specific-staff ADMIN001 --dry-run
```

### Test with Filters

```bash
# Only staff with 10+ days remaining
python3 manage.py send_leave_reminders --min-days 10 --dry-run

# Only staff with 50+ hours remaining
python3 manage.py send_leave_reminders --min-hours 50 --dry-run

# Exclude managers from the campaign
python3 manage.py send_leave_reminders --exclude-management --dry-run
```

### Real Send (Remove --dry-run)

```bash
# Send to ADMIN001 only (real email)
python3 manage.py send_leave_reminders --specific-staff ADMIN001

# Send monthly reminder (real)
python3 manage.py send_leave_reminders --min-days 5
```

---

## 📝 Logs & Monitoring

### Check Email Logs

```bash
# View real-time log output
tail -f /var/log/rotasystem/leave_reminders.log

# View last 50 entries
tail -n 50 /var/log/rotasystem/leave_reminders.log

# Search for specific staff
grep "ADMIN001" /var/log/rotasystem/leave_reminders.log
```

### Log Location

All automation logs are stored in:
```
/var/log/rotasystem/
├── compliance.log          # Daily compliance checks
├── notifications.log       # Violation digests
└── leave_reminders.log     # Leave reminder emails (NEW)
```

---

## 🔧 Production Email Configuration

Currently using **console email backend** (emails print to terminal).

### Switch to Production SMTP

Edit `rotasystems/settings.py`:

```python
# For Gmail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_USER')  # your-email@gmail.com
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')  # App password
DEFAULT_FROM_EMAIL = 'Staff Rota System <your-email@gmail.com>'

# For Office 365
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.office365.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')
DEFAULT_FROM_EMAIL = 'Staff Rota System <your-email@company.com>'
```

### Set Environment Variables

```bash
# Add to ~/.zshrc or ~/.bash_profile
export EMAIL_USER="your-email@gmail.com"
export EMAIL_PASSWORD="your-app-password"  # NOT your regular password!

# Reload
source ~/.zshrc
```

---

## ✅ Checklist

Before going live:

- [ ] Test dry-run mode with `./send_leave_emails.sh test`
- [ ] Verify email content looks correct
- [ ] Configure production SMTP settings
- [ ] Set environment variables for email credentials
- [ ] Test real send to yourself: `./send_leave_emails.sh specific ADMIN001`
- [ ] Install automation: `./install_scheduled_tasks.sh`
- [ ] Verify cron: `crontab -l`
- [ ] Check logs work: `tail -f /var/log/rotasystem/leave_reminders.log`
- [ ] Document who to contact for issues
- [ ] Announce to staff that reminders are coming

---

## 🆘 Troubleshooting

### Problem: No emails sending

**Check:**
1. Email backend configured? (`settings.py`)
2. SMTP credentials correct? (`echo $EMAIL_USER`)
3. App password (not regular password) for Gmail
4. Firewall blocking port 587?

### Problem: Cron jobs not running

**Check:**
```bash
# Verify cron installed
crontab -l

# Check system cron logs
tail -f /var/log/system.log | grep CRON

# Manually test command
cd /Users/deansockalingum/Staff\ Rota/rotasystems
python3 manage.py send_leave_reminders --dry-run
```

### Problem: Wrong staff getting emails

**Check:**
- Filters: `--min-days`, `--min-hours`
- Staff data: Annual leave entitlements up to date?
- Leave year: Correct year active?

### Problem: Email looks broken

**Check:**
- HTML email client support (some email clients block HTML)
- Plain text fallback included automatically
- Test in multiple email clients (Gmail, Outlook, Apple Mail)

---

## 📖 Full Documentation

For comprehensive details, see:
- **LEAVE_REMINDER_EMAILS.md** - Complete feature documentation
- **Command help**: `python3 manage.py send_leave_reminders --help`

---

## 🎯 Summary

**You now have:**
- ✅ Beautiful HTML email templates
- ✅ Manual sending script (`send_leave_emails.sh`)
- ✅ Automated monthly/quarterly/year-end scheduling
- ✅ Dry-run testing mode
- ✅ Comprehensive logging
- ✅ Multiple filtering options
- ✅ Urgency level color-coding
- ✅ Full documentation

**Next step:** Run `./send_leave_emails.sh test` to preview your first email! 🎉
