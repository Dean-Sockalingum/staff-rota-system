# Email Configuration Guide

This guide walks you through setting up production email notifications for the Staff Rota compliance system.

---

## Current Status

✅ **Email System**: Tested and working  
⚙️ **Current Mode**: Console backend (testing mode)  
📧 **Test Results**: Successfully sent daily digest with 24 violations  
🎯 **Next Step**: Configure production SMTP to send real emails

---

## Choose Your Email Provider

### Option 1: Gmail (Recommended for Small Teams)

**Pros:**
- Free for low volume
- Reliable delivery
- Easy to set up

**Cons:**
- Daily sending limit (500 emails/day)
- Requires app password setup

**Setup Steps:**

1. **Generate Gmail App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Sign in to your Google account
   - Click "Generate" 
   - Select "Mail" and "Mac" (or your device)
   - Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

2. **Edit settings.py**
   - Open: `/Users/deansockalingum/Staff Rota/rotasystems/rotasystems/settings.py`
   - Find the email configuration section (around line 200)
   - Comment out this line:
     ```python
     # EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
     ```
   - Uncomment and configure Gmail settings:
     ```python
     EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
     EMAIL_HOST = 'smtp.gmail.com'
     EMAIL_PORT = 587
     EMAIL_USE_TLS = True
     EMAIL_HOST_USER = 'yourname@gmail.com'  # Your actual Gmail
     EMAIL_HOST_PASSWORD = 'abcd efgh ijkl mnop'  # App password from step 1
     DEFAULT_FROM_EMAIL = 'Staff Rota System <yourname@gmail.com>'
     ```

3. **Add Recipient Emails**
   ```python
   COMPLIANCE_NOTIFICATION_EMAILS = [
       'manager1@example.com',
       'manager2@example.com',
       'compliance.officer@example.com',
   ]
   ```

4. **Test the Configuration** (see Testing section below)

---

### Option 2: Office 365 (Best for Organizations)

**Pros:**
- Professional email from your domain
- Higher sending limits
- Integrated with organization

**Cons:**
- Requires Office 365 subscription
- May need IT department approval

**Setup Steps:**

1. **Get Your Office 365 Credentials**
   - Email: Your full Office 365 email address
   - Password: Your Office 365 password
   - Check with IT if you need special SMTP permissions

2. **Edit settings.py**
   - Open: `/Users/deansockalingum/Staff Rota/rotasystems/rotasystems/settings.py`
   - Comment out console backend
   - Uncomment and configure Office 365 settings:
     ```python
     EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
     EMAIL_HOST = 'smtp.office365.com'
     EMAIL_PORT = 587
     EMAIL_USE_TLS = True
     EMAIL_HOST_USER = 'your.name@yourdomain.com'
     EMAIL_HOST_PASSWORD = 'your-office365-password'
     DEFAULT_FROM_EMAIL = 'Staff Rota System <your.name@yourdomain.com>'
     ```

3. **Add Recipient Emails**
   ```python
   COMPLIANCE_NOTIFICATION_EMAILS = [
       'manager1@yourdomain.com',
       'manager2@yourdomain.com',
   ]
   ```

4. **Test the Configuration** (see Testing section below)

---

### Option 3: Other SMTP Server

If you have a different email provider:

1. **Get SMTP Settings from Your Provider**
   - SMTP host (e.g., `smtp.yourprovider.com`)
   - SMTP port (usually 587 for TLS or 465 for SSL)
   - Username and password

2. **Edit settings.py**
   ```python
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST = 'smtp.yourprovider.com'
   EMAIL_PORT = 587  # or 465 for SSL
   EMAIL_USE_TLS = True  # or EMAIL_USE_SSL = True for port 465
   EMAIL_HOST_USER = 'username@yourprovider.com'
   EMAIL_HOST_PASSWORD = 'your-password'
   DEFAULT_FROM_EMAIL = 'Staff Rota System <username@yourprovider.com>'
   ```

---

## Testing Email Configuration

After configuring your SMTP settings, test before the automated tasks run:

### Quick Test

```bash
cd "/Users/deansockalingum/Staff Rota/rotasystems"

# Test sending a daily digest
python3 manage.py shell -c "
from scheduling.utils.notifications import send_daily_violation_digest
result = send_daily_violation_digest()
print(f'Emails sent: {result}')
"
```

**Expected result:** You should receive an email within 1-2 minutes

### Test Critical Alert

```bash
python3 manage.py shell -c "
from scheduling.models import ComplianceViolation
from scheduling.utils.notifications import send_critical_violation_alert

# Get a HIGH violation to test with
violation = ComplianceViolation.objects.filter(severity='HIGH').first()
if violation:
    send_critical_violation_alert(violation)
    print('Critical alert sent!')
else:
    print('No HIGH violations to test with')
"
```

### Test Weekly Summary

```bash
python3 manage.py shell -c "
from scheduling.utils.notifications import send_weekly_compliance_summary
result = send_weekly_compliance_summary()
print(f'Emails sent: {result}')
"
```

---

## Troubleshooting

### Emails Not Arriving

**Check 1: SMTP Credentials**
```bash
python3 manage.py shell -c "
from django.core.mail import send_mail
from django.conf import settings

print(f'EMAIL_BACKEND: {settings.EMAIL_BACKEND}')
print(f'EMAIL_HOST: {settings.EMAIL_HOST}')
print(f'EMAIL_PORT: {settings.EMAIL_PORT}')
print(f'EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')
print(f'EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}')
"
```

**Check 2: Test Simple Email**
```bash
python3 manage.py shell -c "
from django.core.mail import send_mail

send_mail(
    'Test Email',
    'This is a test message from Staff Rota System.',
    'from@example.com',
    ['your-email@example.com'],
    fail_silently=False,
)
print('Test email sent!')
"
```

**Check 3: Common Issues**

| Problem | Solution |
|---------|----------|
| "Authentication failed" | Check username/password, verify app password for Gmail |
| "Connection refused" | Check EMAIL_HOST and EMAIL_PORT |
| "TLS/SSL error" | Verify EMAIL_USE_TLS is True for port 587 |
| "Recipient rejected" | Check COMPLIANCE_NOTIFICATION_EMAILS has valid addresses |
| Nothing happens | Check console output for error messages |

### Gmail Specific Issues

1. **"Less secure app" error**
   - Use App Password, not your regular password
   - Enable 2-factor authentication first
   - Generate app password at: https://myaccount.google.com/apppasswords

2. **Daily limit reached**
   - Gmail allows 500 emails/day
   - Current system sends max 3 emails/day (should be fine)
   - If you hit limit, wait 24 hours or upgrade to Google Workspace

### Office 365 Specific Issues

1. **"SMTP AUTH disabled"**
   - Contact IT to enable SMTP authentication
   - May need to allow your account in Exchange admin

2. **"Client not authenticated"**
   - Verify password is correct
   - Check if modern authentication is enabled

---

## Email Schedule

Once configured, these emails will be sent automatically:

| Email Type | Schedule | Recipients | Content |
|------------|----------|------------|---------|
| **Daily Compliance Checks** | 2:00 AM | Logs only | Runs checks, no email |
| **Daily Violation Digest** | 8:00 AM | All in list | HIGH/MEDIUM violations from last 24h |
| **Weekly Compliance Summary** | Monday 9:00 AM | All in list | Full week metrics and trends |
| **Critical Alerts** | Immediate | All in list | When CRITICAL violations detected |

---

## Security Best Practices

### 1. Protect Your Credentials

**Never commit passwords to git!**

Consider using environment variables:

```python
# In settings.py
import os

EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'default@example.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
```

Then set in your terminal:
```bash
export EMAIL_HOST_USER="your-email@gmail.com"
export EMAIL_HOST_PASSWORD="your-app-password"
```

### 2. Restrict Recipient List

Only add people who need compliance notifications:
- Care home managers
- Compliance officers
- Senior management
- Regulatory contacts (if required)

### 3. Review Regularly

- Check email logs: `tail -f /var/log/rotasystem/notifications.log`
- Monitor bounce rates
- Update recipient list when staff changes

---

## Next Steps After Configuration

1. ✅ **Review current violations** at http://localhost:8000/audit/violations/
2. ✅ **Configure email settings** (you're here!)
3. ⏳ **Test email delivery** (follow Testing section above)
4. ⏳ **Monitor first automated send** (tomorrow at 8:00 AM)
5. ⏳ **Review logs regularly** (`/var/log/rotasystem/`)

---

## Quick Reference Commands

```bash
# Navigate to project
cd "/Users/deansockalingum/Staff Rota/rotasystems"

# Edit email settings
nano rotasystems/settings.py  # or use VS Code

# Test daily digest
python3 manage.py shell -c "from scheduling.utils.notifications import send_daily_violation_digest; send_daily_violation_digest()"

# Test weekly summary
python3 manage.py shell -c "from scheduling.utils.notifications import send_weekly_compliance_summary; send_weekly_compliance_summary()"

# Check cron jobs
crontab -l

# View email logs
tail -f /var/log/rotasystem/notifications.log

# View compliance check logs
tail -f /var/log/rotasystem/compliance.log
```

---

## Example: Complete Gmail Configuration

Here's a complete example with Gmail:

```python
# In rotasystems/settings.py (around line 200)

# TESTING (comment out)
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# PRODUCTION (uncomment and configure)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'carehome.manager@gmail.com'
EMAIL_HOST_PASSWORD = 'abcd efgh ijkl mnop'  # App password from Google
DEFAULT_FROM_EMAIL = 'Staff Rota Compliance System <carehome.manager@gmail.com>'

COMPLIANCE_NOTIFICATION_EMAILS = [
    'manager1@carehome.com',
    'manager2@carehome.com',
    'compliance@carehome.com',
]

SITE_URL = 'http://localhost:8000'  # Update in production
```

---

## Support

For issues:
1. Check the Troubleshooting section above
2. Review logs: `/var/log/rotasystem/notifications.log`
3. Test with console backend first to verify email content
4. Check Django documentation: https://docs.djangoproject.com/en/5.2/topics/email/

---

**Ready to configure?** Open `rotasystems/settings.py` and follow the steps for your chosen email provider!
