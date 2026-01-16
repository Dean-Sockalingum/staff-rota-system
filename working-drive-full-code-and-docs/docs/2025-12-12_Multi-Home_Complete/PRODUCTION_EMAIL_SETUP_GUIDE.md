# Production Email Configuration Guide
**Document:** Email Setup for Staff Rota System  
**Date:** January 6, 2026  
**Status:** Ready for Implementation  
**Effort:** 1-2 hours

---

## Overview

This guide walks through setting up production email for the Staff Rota System. Email notifications are critical for:
- Leave request approvals
- 2FA authentication codes
- Password reset links
- Shift change notifications
- Training compliance alerts
- System alerts

**Good News:** Your Django settings are already configured to support production email! You just need to set environment variables.

---

## Option 1: Gmail SMTP (Recommended for Small-Medium Scale)

### Advantages
- ✅ **FREE** for personal Gmail accounts
- ✅ Easy setup (2 steps)
- ✅ Reliable delivery
- ✅ 500 emails/day limit (sufficient for 821 staff)

### Disadvantages
- ⚠️ Requires app password (not regular password)
- ⚠️ May flag as "less secure" (but safe with app password)

---

### Step 1: Create Gmail App Password

1. **Go to your Google Account:**
   - Visit: https://myaccount.google.com/
   - Sign in with your Gmail account

2. **Enable 2-Factor Authentication (if not already):**
   - Security → 2-Step Verification → Turn on
   - Follow prompts (SMS or authenticator app)

3. **Create App Password:**
   - Security → 2-Step Verification → App passwords
   - Select app: "Mail"
   - Select device: "Other" (enter "Staff Rota System")
   - Click **Generate**
   - Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)
   - **Save this password** - you'll need it in Step 2

---

### Step 2: Configure Environment Variables

**Location:** `/Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete/.env`

Add the following to your `.env` file:

```bash
# Email Configuration (Gmail SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=abcd efgh ijkl mnop  # App password from Step 1
DEFAULT_FROM_EMAIL=Staff Rota System <your-email@gmail.com>
```

**Replace:**
- `your-email@gmail.com` → Your actual Gmail address
- `abcd efgh ijkl mnop` → The 16-character app password from Step 1

---

### Step 3: Test Email Sending

**Method 1: Django Shell**

```bash
cd /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
python3 manage.py shell
```

Then run:

```python
from django.core.mail import send_mail

# Send test email
send_mail(
    subject='Test Email from Staff Rota System',
    message='This is a test email. If you receive this, email is working!',
    from_email=None,  # Uses DEFAULT_FROM_EMAIL
    recipient_list=['your-email@gmail.com'],  # Change to your email
    fail_silently=False,
)

# Should print: 1 (success)
# Check your Gmail inbox
```

**Method 2: Management Command**

Create a test management command:

```bash
# Create the file
mkdir -p scheduling/management/commands
touch scheduling/management/commands/test_email.py
```

Add this content to `test_email.py`:

```python
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Test email configuration'

    def add_arguments(self, parser):
        parser.add_argument('recipient', type=str, help='Email address to send test to')

    def handle(self, *args, **options):
        recipient = options['recipient']
        
        try:
            result = send_mail(
                subject='Staff Rota System - Email Test',
                message='Congratulations! Email is configured correctly.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
            
            if result == 1:
                self.stdout.write(self.style.SUCCESS(f'✅ Email sent successfully to {recipient}'))
            else:
                self.stdout.write(self.style.ERROR('❌ Email failed to send'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))
```

Then run:

```bash
python3 manage.py test_email your-email@gmail.com
```

---

### Step 4: Test Leave Approval Notification

1. **Login as a staff member:**
   - Go to http://127.0.0.1:8000/
   - Login with staff credentials

2. **Submit a leave request:**
   - Navigate to "Leave Requests"
   - Click "Request Leave"
   - Select dates (≤5 days for auto-approval)
   - Submit

3. **Check email:**
   - You should receive an email notification
   - Subject: "Leave Request Approved" or similar
   - Check spam folder if not in inbox

---

### Step 5: Test 2FA Email (if using 2FA)

1. **Logout and login as a manager:**
   - Manager accounts have 2FA enabled

2. **Enter username/password:**
   - Click "Login"

3. **Check email for 2FA code:**
   - Email subject: "Your Verification Code" or similar
   - Copy the 6-digit code
   - Enter code to complete login

---

## Option 2: SendGrid (Recommended for Large Scale)

### Advantages
- ✅ **FREE** tier: 100 emails/day
- ✅ Paid tier: 40,000 emails/month for $19.95
- ✅ Better deliverability (dedicated IP)
- ✅ Email analytics (open rates, clicks)
- ✅ No daily limits on paid tier

### Disadvantages
- ⚠️ Requires account signup
- ⚠️ More complex setup

---

### Step 1: Create SendGrid Account

1. **Sign up:**
   - Visit: https://signup.sendgrid.com/
   - Enter email, password, create account
   - Verify email address

2. **Create API Key:**
   - Dashboard → Settings → API Keys
   - Click "Create API Key"
   - Name: "Staff Rota System"
   - Permissions: "Full Access"
   - Click "Create & View"
   - **Copy the API key** (starts with `SG.`)
   - **Save this key** - you won't see it again!

---

### Step 2: Configure Environment Variables

Add to `.env` file:

```bash
# Email Configuration (SendGrid)
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_USER=apikey  # Literal string "apikey"
EMAIL_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  # Your API key
DEFAULT_FROM_EMAIL=Staff Rota System <noreply@yourdomain.com>
```

**Important:**
- `EMAIL_USER` must be literally `apikey` (not your SendGrid username)
- `EMAIL_PASSWORD` is your API key (starts with `SG.`)
- `DEFAULT_FROM_EMAIL` should use a domain you own (or noreply@sendgrid.net for testing)

---

### Step 3: Verify Sender Identity (Required)

SendGrid requires sender verification to prevent spam.

**Option A: Single Sender Verification (Quick)**

1. **Dashboard → Settings → Sender Authentication → Single Sender Verification**
2. Click "Create New Sender"
3. Fill in details:
   - From Name: "Staff Rota System"
   - From Email: your-email@yourdomain.com
   - Reply To: same as above
   - Company Address: your organization address
4. Click "Create"
5. **Check your email** and verify

**Option B: Domain Authentication (Production)**

1. **Dashboard → Settings → Sender Authentication → Authenticate Your Domain**
2. Enter your domain (e.g., `yourdomain.com`)
3. Add DNS records provided by SendGrid to your domain registrar
4. Wait for verification (24-48 hours)

---

### Step 4: Test Email (Same as Gmail)

Use the Django shell or management command from Gmail Step 3.

---

## Option 3: Microsoft 365 / Outlook.com SMTP

### Configuration

Add to `.env` file:

```bash
# Email Configuration (Outlook)
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_USER=your-email@outlook.com  # Or yourdomain.com if custom domain
EMAIL_PASSWORD=your-password-or-app-password
DEFAULT_FROM_EMAIL=Staff Rota System <your-email@outlook.com>
```

**Limits:**
- Personal accounts: 300 emails/day
- Business accounts: 10,000 emails/day

---

## Production Deployment Checklist

After configuring email locally, prepare for production:

### 1. Environment Variables (Production Server)

**If using Systemd service (from SSL_SETUP_GUIDE.md):**

Edit `/etc/systemd/system/staff-rota.service`:

```ini
[Service]
Environment="EMAIL_HOST=smtp.gmail.com"
Environment="EMAIL_PORT=587"
Environment="EMAIL_USE_TLS=True"
Environment="EMAIL_USER=your-email@gmail.com"
Environment="EMAIL_PASSWORD=your-app-password"
Environment="DEFAULT_FROM_EMAIL=Staff Rota System <your-email@gmail.com>"
```

Then reload:

```bash
sudo systemctl daemon-reload
sudo systemctl restart staff-rota
```

---

### 2. Firewall Configuration

Ensure outbound SMTP traffic is allowed:

```bash
# Allow outbound SMTP (port 587)
sudo ufw allow out 587/tcp

# Check firewall status
sudo ufw status
```

---

### 3. Test All Email Types

| Email Type | How to Test | Expected Result |
|------------|-------------|-----------------|
| **Leave Approval** | Submit leave request (≤5 days) | Auto-approval email received |
| **Leave Request (Manager)** | Submit leave request (>5 days) | Manager receives approval request email |
| **Leave Rejection** | Manager rejects leave | Staff receives rejection email |
| **Password Reset** | Click "Forgot Password" | Reset link email received |
| **2FA Code** | Login as manager | 6-digit code email received |
| **Shift Change** | Manager edits shift | Affected staff receives notification |
| **Training Expiry** | Training record expires | Manager receives compliance alert |
| **System Alert** | Error occurs | Admin receives error notification |

---

### 4. Monitor Email Delivery

**Gmail:**
- Check "Sent" folder in Gmail
- Check Google Account activity for suspicious logins

**SendGrid:**
- Dashboard → Activity Feed
- Monitor delivery rates, bounces, spam reports

**General:**
- Check Django logs: `/var/log/gunicorn/error.log`
- Monitor Sentry for email errors

---

## Troubleshooting

### Issue 1: "SMTPAuthenticationError"

**Cause:** Wrong username or password

**Solution:**
- Gmail: Verify app password (16 chars, no spaces)
- SendGrid: Ensure `EMAIL_USER=apikey` (literal string)
- Check `.env` file for typos

**Test:**

```bash
python3 manage.py shell

from django.core.mail import get_connection
conn = get_connection()
conn.open()  # Should not raise error
conn.close()
```

---

### Issue 2: "SMTPServerDisconnected"

**Cause:** Firewall blocking port 587

**Solution:**

```bash
# Test SMTP connection
telnet smtp.gmail.com 587

# Should see:
# 220 smtp.gmail.com ESMTP...

# If "Connection refused", firewall is blocking
sudo ufw allow out 587/tcp
```

---

### Issue 3: Emails Going to Spam

**Cause:** Missing SPF/DKIM records, suspicious "From" address

**Solution:**

**For Gmail:**
- Use your real email address (not noreply@)
- Add recipients to contacts

**For SendGrid:**
- Complete domain authentication (Option B, Step 3)
- Add SPF record: `v=spf1 include:sendgrid.net ~all`
- Add DKIM record (provided by SendGrid)

---

### Issue 4: "Connection Timeout"

**Cause:** Server can't reach SMTP server

**Solution:**

1. Check internet connectivity:
   ```bash
   ping smtp.gmail.com
   ```

2. Check DNS resolution:
   ```bash
   nslookup smtp.gmail.com
   ```

3. Try port 465 (SSL) instead of 587 (TLS):
   ```bash
   EMAIL_PORT=465
   EMAIL_USE_TLS=False
   EMAIL_USE_SSL=True
   ```

---

### Issue 5: "Daily Sending Quota Exceeded"

**Cause:** Sent too many emails (Gmail: 500/day)

**Solution:**

- **Short-term:** Wait 24 hours for quota reset
- **Long-term:** Upgrade to SendGrid paid tier (40,000/month)
- **Monitor:** Track daily email count in Django

---

## Email Templates (Optional Enhancement)

Create custom HTML email templates for better branding.

**Location:** `scheduling/templates/emails/`

**Example: Leave Approval Email**

`leave_approved.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .header { background-color: #4CAF50; color: white; padding: 20px; }
        .content { padding: 20px; }
        .button { background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Leave Request Approved ✅</h1>
    </div>
    <div class="content">
        <p>Hello {{ staff_name }},</p>
        <p>Your leave request has been <strong>approved</strong>:</p>
        <ul>
            <li><strong>Dates:</strong> {{ start_date }} to {{ end_date }}</li>
            <li><strong>Days:</strong> {{ num_days }} days</li>
            <li><strong>Remaining Balance:</strong> {{ remaining_balance }} days</li>
        </ul>
        <p>
            <a href="{{ view_url }}" class="button">View Details</a>
        </p>
        <p>Thank you,<br>Staff Rota System</p>
    </div>
</body>
</html>
```

**Usage in Django:**

```python
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

# HTML version
html_content = render_to_string('emails/leave_approved.html', {
    'staff_name': request.user.get_full_name(),
    'start_date': leave_request.start_date,
    'end_date': leave_request.end_date,
    'num_days': leave_request.num_days,
    'remaining_balance': request.user.leave_balance,
    'view_url': request.build_absolute_uri(f'/leave-requests/{leave_request.id}/')
})

# Plain text fallback
text_content = f"Your leave request from {leave_request.start_date} to {leave_request.end_date} has been approved."

# Send email
email = EmailMultiAlternatives(
    subject='Leave Request Approved',
    body=text_content,
    from_email=settings.DEFAULT_FROM_EMAIL,
    to=[request.user.email]
)
email.attach_alternative(html_content, "text/html")
email.send()
```

---

## Security Best Practices

### 1. Never Commit Email Credentials

**Check `.gitignore` includes:**

```
.env
*.env
.env.local
.env.production
```

**Verify:**

```bash
git status  # Should not show .env file
```

---

### 2. Encrypt .env File (Production)

**Option A: GPG Encryption**

```bash
# Encrypt
gpg --symmetric --cipher-algo AES256 .env

# Creates: .env.gpg (commit this)
# Delete plaintext: rm .env

# Decrypt on server
gpg --decrypt .env.gpg > .env
```

**Option B: Ansible Vault**

```bash
ansible-vault encrypt .env
# Enter password

# Decrypt
ansible-vault decrypt .env
```

---

### 3. Monitor for Abuse

**Track daily email count:**

```python
# In Django
from django.core.cache import cache

def send_tracked_email(subject, message, recipient_list):
    # Get today's count
    today = timezone.now().date()
    cache_key = f'email_count_{today}'
    count = cache.get(cache_key, 0)
    
    # Check limit (e.g., 400/day for Gmail)
    if count >= 400:
        raise Exception("Daily email limit reached")
    
    # Send email
    result = send_mail(subject, message, None, recipient_list)
    
    # Increment count
    cache.set(cache_key, count + 1, timeout=86400)  # 24 hours
    
    return result
```

---

## Performance Optimization

### 1. Async Email Sending (Optional)

For high-volume email, send asynchronously with Celery.

**Install Celery + Redis:**

```bash
pip3 install celery redis
```

**Create `scheduling/tasks.py`:**

```python
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_async_email(subject, message, recipient_list):
    return send_mail(subject, message, None, recipient_list)
```

**Usage:**

```python
from scheduling.tasks import send_async_email

# Instead of:
# send_mail(subject, message, None, [user.email])

# Use:
send_async_email.delay(subject, message, [user.email])
# Returns immediately, email sent in background
```

---

### 2. Batch Email Sending

For notifications to many users:

```python
from django.core.mail import send_mass_mail

messages = [
    (subject, message, from_email, [user1.email]),
    (subject, message, from_email, [user2.email]),
    # ... up to 100 users
]

send_mass_mail(messages, fail_silently=False)
```

---

## Cost Summary

| Provider | Free Tier | Paid Tier | Recommendation |
|----------|-----------|-----------|----------------|
| **Gmail** | 500 emails/day | N/A (personal use) | ✅ Best for pilot (117 staff) |
| **SendGrid** | 100 emails/day | $19.95/mo (40k emails) | ✅ Best for production (821 staff) |
| **Office 365** | 300 emails/day | $6/user/month | ⚠️ Expensive for many staff |

**Recommendation:**
- **Pilot (Weeks 1-8):** Gmail (FREE, sufficient for 2 homes)
- **Production (Month 4+):** SendGrid paid tier (£15/month for 40k emails)

**Projected Usage (821 staff):**
- Daily: ~50 emails (leave approvals, shift changes)
- Weekly: ~200 emails (training alerts, compliance reports)
- Monthly: ~1,000 emails

**Verdict:** Gmail FREE tier sufficient for production! Upgrade to SendGrid only if exceeding 500/day.

---

## Testing Checklist

Before marking this todo item complete, verify:

- [ ] `.env` file updated with email credentials
- [ ] Test email sent successfully via Django shell
- [ ] Leave approval email received
- [ ] Password reset email received
- [ ] 2FA code email received (if using 2FA)
- [ ] Emails not going to spam
- [ ] `DEFAULT_FROM_EMAIL` displays correctly (not noreply@localhost)
- [ ] Email credentials NOT committed to Git
- [ ] Firewall allows outbound SMTP (port 587)
- [ ] Systemd service configured with email env vars (production only)

---

## Next Steps (After This Task)

1. **Secrets Management** (Todo item 4)
   - Encrypt .env file for production
   - Set up AWS Secrets Manager or Vault

2. **Load Testing** (Todo item 6)
   - Include email sending in load tests
   - Verify email queue handles 50+ concurrent users

3. **UAT Execution** (Week 3-4)
   - Test all email types with real users
   - Collect feedback on email content/formatting

---

## Support Resources

- **Gmail SMTP Issues:** https://support.google.com/mail/answer/7126229
- **SendGrid Docs:** https://docs.sendgrid.com/for-developers/sending-email/django
- **Django Email Backend:** https://docs.djangoproject.com/en/4.2/topics/email/
- **Email Testing Tool:** https://mailtrap.io/ (sandbox for testing)

---

**Document Status:** Ready for Implementation  
**Estimated Time:** 1-2 hours (Gmail), 2-3 hours (SendGrid)  
**Next Todo Item:** Secrets Management  
**Last Updated:** January 6, 2026
