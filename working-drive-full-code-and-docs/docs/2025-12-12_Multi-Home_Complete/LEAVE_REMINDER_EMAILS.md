# Annual Leave Reminder Email System

## Overview

The Staff Rota System includes an automated email reminder system to help ensure staff members are aware of their remaining annual leave entitlement and encourages them to book their leave before it expires.

## Features

✅ **Personalized Emails** - Each staff member receives a customized email with their specific leave details  
✅ **Beautiful HTML Design** - Professional, responsive email templates with visual appeal  
✅ **Smart Filtering** - Target specific groups of staff based on various criteria  
✅ **Dry Run Mode** - Preview emails before sending to avoid mistakes  
✅ **Urgency Indicators** - Color-coded urgency levels based on remaining leave  
✅ **Detailed Statistics** - Shows total entitlement, used, pending, and remaining leave  
✅ **Leave Breakdown** - Both hours and days displayed for clarity  
✅ **Carryover Information** - Includes any carryover hours from previous year  

## Email Content

Each email includes:

1. **Leave Summary Card**:
   - Total entitlement (hours and days)
   - Leave already used
   - Leave remaining
   - Usage percentage
   - Carryover hours (if applicable)

2. **Urgency Alert**:
   - 🔴 **HIGH** (< 5 days remaining): "You have very few days remaining! Please book your leave soon."
   - 🟡 **MEDIUM** (< 10 days remaining): "Please consider booking your remaining leave in the coming weeks."
   - 🟢 **LOW** (10+ days remaining): "You have plenty of time to plan and book your leave."

3. **How to Request Leave**:
   - Step-by-step instructions
   - Direct link to leave request page
   - Tips for planning leave

4. **Important Deadline**:
   - Leave year end date
   - Warning about unused leave being lost

## Usage

### Basic Usage

Send reminders to all staff with remaining leave:

```bash
python manage.py send_leave_reminders
```

### Dry Run (Preview Mode)

Preview what emails would be sent without actually sending them:

```bash
python manage.py send_leave_reminders --dry-run
```

**Always use --dry-run first to verify everything is correct!**

### Filter by Minimum Days

Send only to staff with at least X days remaining:

```bash
# Only staff with 10+ days remaining
python manage.py send_leave_reminders --min-days 10

# Only staff with 5+ days remaining
python manage.py send_leave_reminders --dry-run --min-days 5
```

### Filter by Minimum Hours

Send only to staff with at least X hours remaining:

```bash
# Only staff with 50+ hours remaining
python manage.py send_leave_reminders --min-hours 50
```

### Specific Staff Members

Send to specific staff only by SAP ID:

```bash
python manage.py send_leave_reminders --specific-staff ADMIN001 SCW1001 SCA1010
```

### Exclude Management

Exclude management staff from reminders:

```bash
python manage.py send_leave_reminders --exclude-management
```

### Specific Leave Year

Check a specific leave year (default is current year):

```bash
python manage.py send_leave_reminders --year 2025
```

### Combined Filters

You can combine multiple filters:

```bash
# Dry run for non-management staff with 10+ days in 2025
python manage.py send_leave_reminders --dry-run --min-days 10 --exclude-management --year 2025

# Real send to specific staff with 5+ days
python manage.py send_leave_reminders --specific-staff SCW1001 SCA1010 --min-days 5
```

## Command Options

| Option | Description | Example |
|--------|-------------|---------|
| `--dry-run` | Preview mode - no emails sent | `--dry-run` |
| `--min-days` | Minimum days remaining | `--min-days 10` |
| `--min-hours` | Minimum hours remaining | `--min-hours 50` |
| `--specific-staff` | SAP IDs to send to | `--specific-staff SAP001 SAP002` |
| `--year` | Leave year to check | `--year 2025` |
| `--exclude-management` | Skip management staff | `--exclude-management` |

## Email Configuration

The system uses Django's email backend configured in `settings.py`.

### Current Setup (Development)

```python
# Console backend - emails appear in terminal
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Production Setup (Gmail Example)

To actually send emails, update `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # 16-character app password
DEFAULT_FROM_EMAIL = 'Staff Rota System <your-email@gmail.com>'
```

### Production Setup (Office 365 Example)

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.office365.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@yourdomain.com'
EMAIL_HOST_PASSWORD = 'your-password'
DEFAULT_FROM_EMAIL = 'Staff Rota System <your-email@yourdomain.com>'
```

## Best Practices

### 1. Always Test First

```bash
# Test with dry-run
python manage.py send_leave_reminders --dry-run

# Test with a single staff member
python manage.py send_leave_reminders --specific-staff ADMIN001 --dry-run

# Then send for real
python manage.py send_leave_reminders --specific-staff ADMIN001
```

### 2. Staged Rollout

Send to different groups gradually:

```bash
# Day 1: Send to staff with < 5 days remaining (urgent)
python manage.py send_leave_reminders --min-days 0 --max-days 5

# Day 7: Send to staff with 5-10 days remaining
python manage.py send_leave_reminders --min-days 5 --max-days 10

# Day 14: Send to everyone else
python manage.py send_leave_reminders --min-days 10
```

### 3. Regular Reminders

Set up automated reminders:

```bash
# Monthly reminder (first day of month)
0 9 1 * * cd /path/to/rotasystems && python manage.py send_leave_reminders --min-days 5

# Quarterly reminder
0 9 1 1,4,7,10 * cd /path/to/rotasystems && python manage.py send_leave_reminders --min-days 10

# End of year urgent reminder (December 1st)
0 9 1 12 * cd /path/to/rotasystems && python manage.py send_leave_reminders --min-days 0
```

## Output Example

```
======================================================================
Annual Leave Reminder Email System
======================================================================

🔍 DRY RUN MODE - No emails will be sent

Filtering to staff with at least 5.0 days remaining
Found 181 staff member(s) eligible for reminders
──────────────────────────────────────────────────────────────────────
📧 SCW1080 - Jack Henderson (scw1080@facility.com): 25.5 days remaining - WOULD SEND
📧 SCW1081 - Karen Watson (scw1081@facility.com): 25.5 days remaining - WOULD SEND
📧 ADMIN001 - System Administrator (admin@facility.com): 28.5 days remaining - WOULD SEND
...

──────────────────────────────────────────────────────────────────────

📊 SUMMARY
──────────────────────────────────────────────────────────────────────
Total eligible staff:  181
✅ Emails sent:        181
──────────────────────────────────────────────────────────────────────

🔍 This was a DRY RUN - no emails were actually sent.
Remove --dry-run to send emails for real.
```

## Troubleshooting

### No Emails Being Sent

1. Check email backend is configured (not console backend in production)
2. Verify SMTP credentials are correct
3. Check firewall/network allows SMTP connections
4. Look for errors in the terminal output

### Staff Not Receiving Emails

1. Verify staff have email addresses in their profile
2. Check email addresses are valid
3. Look in spam/junk folders
4. Verify staff are active (`is_active=True`)

### Filtering Not Working

1. Use `--dry-run` to see who would receive emails
2. Check leave entitlements exist for the year
3. Verify `days_remaining` values are correct

## Security Notes

⚠️ **Never commit email passwords to version control!**

Use environment variables:

```python
# settings.py
import os

EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')
```

```bash
# In your shell
export EMAIL_USER="your-email@domain.com"
export EMAIL_PASSWORD="your-app-password"
```

## Support

For issues or questions:
- Check the terminal output for specific error messages
- Verify email configuration in `settings.py`
- Test with `--dry-run` first
- Contact system administrator or IT support

---

**Created:** November 2025  
**Last Updated:** November 2025  
**Version:** 1.0
