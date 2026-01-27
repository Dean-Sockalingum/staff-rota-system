# Email Configuration - Admin UI Guide
**Document:** UI-Based Email Setup for HSCP Administrators  
**Date:** January 6, 2026  
**Status:** Production Ready  
**Target Users:** HSCP administrators, Service Managers, Technical staff

---

## Executive Summary

The Staff Rota System now includes a **user-friendly admin interface** for configuring email settings. This eliminates the need for technical .env file editing or server access, allowing HSCP administrators to:

✅ Configure email providers through Django admin UI  
✅ Choose from Gmail, SendGrid, Microsoft 365, or custom SMTP  
✅ Test email configurations before activation  
✅ Switch providers without server restarts  
✅ View encrypted password storage (secure)  
✅ Monitor email test results and status

---

## Benefits Over Manual .env Configuration

| Feature | Manual .env Editing | **UI-Based Admin** |
|---------|---------------------|-------------------|
| **Technical Knowledge Required** | High (terminal, SSH, file editing) | None (web browser only) |
| **Server Access Needed** | Yes (SSH or remote desktop) | No (admin login only) |
| **Password Security** | Plain text in .env file | Encrypted in database |
| **Provider Switching** | Manual file edit + restart | Single click in UI |
| **Testing** | Manual test commands | Built-in "Test Email" button |
| **Multiple Configurations** | Difficult (backup .env) | Easy (store multiple, activate one) |
| **Error Validation** | Manual (trial and error) | Automatic (form validation) |
| **Audit Trail** | None | Timestamps, test results logged |

---

## Accessing Email Configuration

### Step 1: Log in to Django Admin

1. Navigate to: **https://your-domain.com/admin/**
2. Log in with **superuser credentials** (admin account)
3. In the admin sidebar, locate **EMAIL CONFIG** section
4. Click on **Email Configurations**

### Step 2: View Existing Configurations

You'll see a list of all configured email setups:
- **Provider:** Gmail, SendGrid, Microsoft 365, Custom
- **From Email:** Default sender address
- **Host/Port:** SMTP server details
- **Active Status:** ✓ (Active) or blank (Inactive)
- **Test Status:** Success ✓ / Failed ✗ / Not tested
- **Updated:** Last modification date

---

## Creating a New Email Configuration

### Option 1: Gmail (FREE - Recommended for Pilot)

**Requirements:**
- Gmail account (e.g., `staffrota@gmail.com`)
- 2-Factor Authentication (2FA) enabled
- App Password generated

**Setup Steps:**

1. **Enable 2FA on Gmail:**
   - Go to: https://myaccount.google.com/security
   - Click "2-Step Verification"
   - Follow setup wizard

2. **Generate App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and device type
   - Click "Generate"
   - **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)

3. **Create Configuration in Admin UI:**
   - Click **"Add Email Configuration"** button
   - **Provider:** Select "Gmail" (auto-fills host/port)
   - **Host:** `smtp.gmail.com` (auto-filled)
   - **Port:** `587` (auto-filled)
   - **Use TLS:** ✓ Checked (auto-filled)
   - **Use SSL:** ☐ Unchecked (auto-filled)
   - **Username:** Your Gmail address (e.g., `staffrota@gmail.com`)
   - **Password:** Paste the 16-character app password
   - **From Email:** Same as username or custom (e.g., `Staff Rota <staffrota@gmail.com>`)
   - **Is Active:** ☐ Leave unchecked for now (test first)

4. **Click "Save"**

5. **Test Configuration:**
   - Select the configuration checkbox
   - In "Action" dropdown, choose **"✉ Test Email Configuration"**
   - Click **"Go"**
   - Check your email inbox for test message

6. **Activate if Test Succeeds:**
   - Edit the configuration
   - Check **"Is Active"** checkbox
   - Click **"Save"**

**Limits:**
- FREE tier: **500 emails/day**
- Sufficient for: Pilot (2 homes), small deployments
- Cost: **£0/year**

---

### Option 2: SendGrid (Scalable for Production)

**Requirements:**
- SendGrid account (free or paid)
- API key generated

**Setup Steps:**

1. **Create SendGrid Account:**
   - Go to: https://sendgrid.com/
   - Sign up for free account (100 emails/day)
   - OR paid account (40,000 emails/month at £14.95/mo)

2. **Generate API Key:**
   - Log in to SendGrid dashboard
   - Go to: Settings → API Keys
   - Click "Create API Key"
   - Name: `Staff Rota System`
   - Permissions: "Full Access" or "Mail Send"
   - Click "Create & View"
   - **Copy the API key** (starts with `SG.`)

3. **Create Configuration in Admin UI:**
   - Click **"Add Email Configuration"**
   - **Provider:** Select "SendGrid" (auto-fills host/port)
   - **Host:** `smtp.sendgrid.net` (auto-filled)
   - **Port:** `587` (auto-filled)
   - **Use TLS:** ✓ Checked (auto-filled)
   - **Use SSL:** ☐ Unchecked (auto-filled)
   - **Username:** `apikey` (literally the word "apikey")
   - **Password:** Paste your SendGrid API key
   - **From Email:** Your verified sender (e.g., `noreply@hscp.scot`)
   - **Is Active:** ☐ Leave unchecked

4. **Verify Sender Identity (SendGrid Requirement):**
   - In SendGrid dashboard: Settings → Sender Authentication
   - Verify your domain OR single sender email
   - Follow verification steps (click email link)

5. **Test Configuration:**
   - Select configuration → Action: **"Test Email Configuration"** → Go
   - Check inbox for test email
   - **Check SendGrid dashboard** for delivery confirmation

6. **Activate if Test Succeeds:**
   - Edit configuration → Check "Is Active" → Save

**Limits:**
- **Free tier:** 100 emails/day
- **Essentials tier (£14.95/mo):** 40,000 emails/month
- **Pro tier (£79.95/mo):** 100,000 emails/month
- Recommended for: Full production (5 homes, 821 staff)

**Benefits:**
- Scalable for large deployments
- Detailed delivery analytics
- Bounce/spam handling
- Professional reputation management

---

### Option 3: Microsoft 365 / Outlook (For HSCP Enterprise)

**Requirements:**
- Microsoft 365 business account
- 2FA enabled
- App Password generated

**Setup Steps:**

1. **Enable 2FA:**
   - Go to: https://account.microsoft.com/security
   - Enable "Two-step verification"

2. **Generate App Password:**
   - Go to: https://account.live.com/proofs/AppPassword
   - Create app password for "Mail"
   - **Copy the generated password**

3. **Create Configuration in Admin UI:**
   - **Provider:** Select "Microsoft 365 / Outlook"
   - **Host:** `smtp-mail.outlook.com` (auto-filled)
   - **Port:** `587` (auto-filled)
   - **Use TLS:** ✓ Checked
   - **Use SSL:** ☐ Unchecked
   - **Username:** Your Microsoft 365 email
   - **Password:** Paste app password
   - **From Email:** Same as username
   - **Is Active:** ☐ Leave unchecked

4. **Test and Activate** (same as Gmail steps)

**Limits:**
- Depends on Microsoft 365 subscription tier
- Business Basic: 10,000 emails/day per user
- Cost: £4-18/user/month (if already using Microsoft 365)

---

### Option 4: Custom SMTP Server

**For organizations with existing email infrastructure**

**Requirements:**
- SMTP server hostname (e.g., `mail.yourdomain.com`)
- Port number (usually 587 for TLS, 465 for SSL)
- Username and password

**Setup Steps:**

1. **Get SMTP Details from IT Department:**
   - Request: Host, Port, Username, Password, TLS/SSL settings

2. **Create Configuration in Admin UI:**
   - **Provider:** Select "Custom SMTP Server"
   - **Host:** Enter SMTP hostname
   - **Port:** Enter port number (587 or 465)
   - **Use TLS:** ✓ Check for port 587
   - **Use SSL:** ✓ Check for port 465
   - **Username:** Enter SMTP username
   - **Password:** Enter SMTP password
   - **From Email:** Enter sender email address
   - **Is Active:** ☐ Leave unchecked

3. **Test and Activate**

---

## Testing Email Configuration

### Built-In Test Email Feature

**Purpose:** Verify SMTP connection before activating configuration

**Steps:**

1. **Navigate to Email Configurations list**
2. **Select configuration** (checkbox on left)
3. **Action dropdown:** Choose **"✉ Test Email Configuration"**
4. **Click "Go"**

**What Happens:**
- System sends test email to your admin email address
- Test email includes:
  - Configuration details (host, port, TLS/SSL)
  - Test timestamp
  - Success confirmation message
- Results saved to configuration:
  - **Last Test Date:** When test was run
  - **Test Status:** Success ✓ or Failed ✗
  - **Test Message:** Detailed results or error message

**Success Indicators:**
- ✓ Green "Success" status
- "Test email sent successfully" message
- Test email received in inbox (check spam folder)

**Failure Indicators:**
- ✗ Red "Failed" status
- Error message displayed (e.g., "Authentication failed", "Connection timeout")
- Detailed error in "Last Test Message" field

---

## Common Configuration Errors & Solutions

### Error 1: Authentication Failed

**Symptoms:**
- Test Status: Failed ✗
- Message: "Authentication failed" or "Invalid credentials"

**Solutions:**

**For Gmail:**
1. Verify 2FA is enabled: https://myaccount.google.com/security
2. Generate new App Password: https://myaccount.google.com/apppasswords
3. Copy password correctly (no spaces)
4. Use App Password, NOT your Gmail password

**For SendGrid:**
1. Verify username is exactly `apikey` (not your email)
2. Verify API key is complete (starts with `SG.`)
3. Check API key permissions (needs "Mail Send")

**For Microsoft 365:**
1. Verify 2FA is enabled
2. Generate new App Password
3. Ensure using App Password, not account password

---

### Error 2: Connection Timeout

**Symptoms:**
- Test Status: Failed ✗
- Message: "Connection timed out" or "Could not connect"

**Solutions:**
1. **Check firewall rules:** Allow outbound port 587 (TLS) or 465 (SSL)
2. **Verify host/port:** Correct spelling, no typos
3. **Network connectivity:** Ensure server has internet access
4. **Try alternative port:** If 587 fails, try 465 (and switch to SSL)

---

### Error 3: TLS/SSL Errors

**Symptoms:**
- Message: "TLS handshake failed" or "SSL error"

**Solutions:**
1. **Don't use both:** Uncheck one of TLS or SSL (never both)
2. **Port/encryption match:**
   - Port 587 → Use TLS ✓, Use SSL ☐
   - Port 465 → Use TLS ☐, Use SSL ✓
3. **Update configuration:** Edit and save with correct settings

---

### Error 4: From Address Rejected

**Symptoms:**
- Message: "From address rejected" or "Sender not verified"

**Solutions:**

**For SendGrid:**
1. Verify sender identity in SendGrid dashboard
2. Go to: Settings → Sender Authentication
3. Verify domain OR single sender email
4. Use verified email in "From Email" field

**For Custom SMTP:**
1. Ensure "From Email" matches authenticated domain
2. Check SPF/DKIM records configured
3. Contact IT department for allowed sender addresses

---

## Activating Email Configuration

### Single Active Configuration

**Rule:** Only **one** configuration can be active at a time

**To Activate:**

**Method 1: During Save**
1. Edit configuration
2. Check **"Is Active"** checkbox
3. Click **"Save"**
4. System automatically deactivates other configurations

**Method 2: Using Action**
1. Select configuration (checkbox)
2. Action: **"✓ Activate Configuration"**
3. Click **"Go"**
4. Other configurations automatically deactivated

**To Deactivate:**
1. Select active configuration
2. Action: **"✗ Deactivate Configuration"**
3. Click **"Go"**
4. System reverts to console email backend (development mode)

---

## Email Configuration Best Practices

### 1. Security

✅ **DO:**
- Use App Passwords (not account passwords)
- Test before activating
- Keep .env file secure (never commit to git)
- Use HTTPS for admin access
- Limit admin access to trusted staff

❌ **DON'T:**
- Share SMTP credentials publicly
- Use personal email accounts for production
- Disable TLS/SSL encryption
- Activate untested configurations

### 2. Reliability

✅ **DO:**
- Test configurations after creation
- Monitor email delivery rates
- Keep backup configuration (inactive)
- Document provider login credentials securely

❌ **DON'T:**
- Use free tier for high-volume production
- Ignore test failures
- Delete working configurations without backup

### 3. Compliance

✅ **DO:**
- Use HSCP-owned email domain (e.g., `@hscp.scot`)
- Verify sender identity (SPF/DKIM/DMARC)
- Include opt-out for non-critical emails
- Log email activity (audit trail)

❌ **DON'T:**
- Use personal Gmail for official communications
- Send without proper authentication
- Ignore bounce/spam complaints

---

## Email Configuration Scenarios

### Scenario 1: Pilot Deployment (Hawthorn + Meadowburn)

**Recommended Configuration:**
- **Provider:** Gmail (FREE)
- **Email Volume:** ~100 emails/day (leave requests, notifications)
- **Cost:** £0/year
- **Setup Time:** 15 minutes

**Rationale:**
- Free tier sufficient for 2 homes (~117 staff)
- Easy setup (no billing required)
- Reliable delivery (Gmail reputation)
- Good for proof-of-concept

---

### Scenario 2: Full Production (All 5 Homes)

**Recommended Configuration:**
- **Provider:** SendGrid Essentials (£14.95/mo)
- **Email Volume:** ~500-1000 emails/day (821 staff)
- **Cost:** £179.40/year
- **Setup Time:** 30 minutes (includes domain verification)

**Rationale:**
- Scalable for 821 staff
- 40,000 emails/month (sufficient headroom)
- Professional delivery analytics
- Better reputation management than Gmail

---

### Scenario 3: HSCP Enterprise (Using Existing Infrastructure)

**Recommended Configuration:**
- **Provider:** Custom SMTP (HSCP mail server)
- **Email Volume:** Unlimited (depends on HSCP infrastructure)
- **Cost:** £0 (included in HSCP IT budget)
- **Setup Time:** 1 hour (coordinate with IT department)

**Rationale:**
- Uses existing HSCP email infrastructure
- Complies with HSCP IT policies
- Centralized management
- No external dependencies

---

## Monitoring & Maintenance

### Daily Checks (Automated)

**Email Configuration Model Tracks:**
- Last test date
- Test status (success/failed)
- Test message (detailed results)
- Active status
- Updated timestamp

### Weekly Review (Manual)

**Service Manager Tasks:**
1. **Check email delivery rates:**
   - Review Django logs: `grep "EMAIL" /var/log/django.log`
   - SendGrid dashboard (if using SendGrid)

2. **Monitor test status:**
   - Admin → Email Configurations
   - Verify active config shows "Success ✓"

3. **Review bounces/failures:**
   - Check spam complaints
   - Update recipient lists if needed

### Monthly Maintenance

1. **Rotate credentials (security):**
   - Generate new App Password (Gmail/Microsoft 365)
   - Update configuration in admin UI
   - Test before activating

2. **Review email volume vs limits:**
   - Gmail: Max 500/day (monitor if approaching limit)
   - SendGrid: Review monthly usage (upgrade if needed)

3. **Audit email activity:**
   - Export email logs from Django
   - Verify compliance with GDPR/data protection

---

## Troubleshooting Checklist

### Configuration Not Working

- [ ] Configuration is active (checkbox ✓)
- [ ] Test status shows "Success ✓"
- [ ] Test was run after latest changes
- [ ] Username/password correct (no typos)
- [ ] TLS/SSL settings match port number
- [ ] Firewall allows outbound port 587/465
- [ ] Server has internet connectivity
- [ ] From Email matches verified sender (SendGrid)
- [ ] App Password used (not account password)

### Emails Not Being Sent

- [ ] Check Django logs for errors
- [ ] Verify active configuration exists
- [ ] Test email sends successfully
- [ ] Check spam folder for emails
- [ ] Review recipient email addresses (valid?)
- [ ] Check provider daily/monthly limits

### Emails Going to Spam

- [ ] Configure SPF record in DNS
- [ ] Configure DKIM record in DNS
- [ ] Configure DMARC record in DNS
- [ ] Use verified sender domain
- [ ] Avoid spam trigger words in subject
- [ ] Use reputable email provider (not free Gmail)

---

## Migration Guide: .env to UI Configuration

**For systems currently using .env file for email:**

### Step 1: Backup Existing Configuration

**Record current .env settings:**
```bash
# Example .env values
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_USER=staffrota@gmail.com
EMAIL_PASSWORD=abcd efgh ijkl mnop
DEFAULT_FROM_EMAIL=Staff Rota <staffrota@gmail.com>
```

### Step 2: Create Equivalent UI Configuration

1. Log in to Django admin
2. Add Email Configuration
3. Fill fields with .env values:
   - Provider: Custom (or match provider)
   - Host: EMAIL_HOST value
   - Port: EMAIL_PORT value
   - Use TLS: EMAIL_USE_TLS value
   - Use SSL: EMAIL_USE_SSL value
   - Username: EMAIL_USER value
   - Password: EMAIL_PASSWORD value
   - From Email: DEFAULT_FROM_EMAIL value

### Step 3: Test UI Configuration

1. Select configuration
2. Action: "Test Email Configuration"
3. Verify test succeeds

### Step 4: Activate UI Configuration

1. Edit configuration
2. Check "Is Active"
3. Save

### Step 5: Remove .env Email Variables (Optional)

**System will prioritize UI config over .env**

```bash
# Comment out or remove from .env
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# ... etc
```

**Restart not required** - changes take effect immediately

---

## Support & Help

### Getting Help

**For HSCP Administrators:**
1. **Documentation:** This guide
2. **In-app help:** Hover over field labels for tooltips
3. **Technical Support:** Contact Technical Lead
4. **Email:** support@staffrota.yourdomain.com

**For Technical Issues:**
- Check Django admin logs
- Review test error messages
- Consult provider documentation:
  - Gmail: https://support.google.com/mail/answer/7126229
  - SendGrid: https://docs.sendgrid.com/
  - Microsoft 365: https://support.microsoft.com/

---

## Frequently Asked Questions (FAQ)

### Q1: Can I have multiple active configurations?

**A:** No, only one configuration can be active at a time. The system automatically deactivates other configurations when you activate a new one.

---

### Q2: Is my password secure?

**A:** Yes, passwords are encrypted using industry-standard encryption (Fernet) before being stored in the database. They are never displayed in plain text in the admin UI.

---

### Q3: What happens if I deactivate all configurations?

**A:** The system falls back to the console email backend, which prints emails to the terminal instead of sending them. This is useful for development/testing but not recommended for production.

---

### Q4: Can I test without activating?

**A:** Yes! Use the "Test Email Configuration" action to send a test email without activating the configuration. Activate only after confirming the test succeeds.

---

### Q5: How do I switch providers?

**A:** Create a new configuration for the new provider, test it, then activate it. The old configuration will be automatically deactivated but remains stored for easy rollback.

---

### Q6: What if the test fails?

**A:** Check the "Last Test Message" field for detailed error information. Common issues: wrong password, firewall blocking, TLS/SSL mismatch. Refer to the "Common Configuration Errors" section above.

---

### Q7: Do I need to restart the server?

**A:** No! Configuration changes take effect immediately without requiring a server restart.

---

### Q8: Can I revert to .env configuration?

**A:** Yes, the system checks database configurations first, then falls back to .env variables. If no active UI configuration exists, .env settings will be used.

---

## Next Steps

### For Pilot Deployment (Week 1)

1. **Choose provider:**
   - Gmail (FREE) for pilot
   - Custom SMTP if HSCP has existing infrastructure

2. **Create configuration** (15-30 mins)
3. **Test thoroughly** (send 5-10 test emails)
4. **Activate** after successful tests
5. **Monitor** first 24 hours for delivery issues

### For Production Deployment (Month 2+)

1. **Evaluate pilot results:**
   - Email volume (actual vs estimated)
   - Delivery success rate
   - User feedback

2. **Scale up if needed:**
   - Upgrade to SendGrid Essentials if >500 emails/day
   - OR coordinate with HSCP IT for enterprise SMTP

3. **Configure monitoring:**
   - Weekly delivery rate checks
   - Monthly usage vs limits review

4. **Document procedures:**
   - Add to runbook
   - Train support staff
   - Create escalation path

---

**Document Version:** 1.0  
**Last Updated:** January 6, 2026  
**Author:** Technical Lead  
**Status:** Production Ready  
**Related Documents:**
- PRODUCTION_EMAIL_SETUP_GUIDE.md (legacy .env setup)
- 12_WEEK_IMPLEMENTATION_PLAN.md (deployment roadmap)
- PILOT_DEPLOYMENT_PLAN.md (pilot strategy)
