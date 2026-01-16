# Production Email Configuration Guide

## 🎯 Quick Start

The Staff Rota system now uses **environment variables** for secure email configuration. This means you can switch between testing and production modes without editing code!

### **Current Mode**
- ✅ **Testing/Console Mode**: Emails print to terminal (no real emails sent)
- ⏸️ **Production Mode**: Not yet configured

---

## 🚀 Easy Setup (Recommended)

Use the interactive setup script:

```bash
cd /Users/deansockalingum/Staff\ Rota/rotasystems
./setup_email.sh
```

The script will guide you through:
1. Choosing your email provider (Gmail, Office 365, or custom)
2. Entering credentials securely
3. Automatically configuring environment variables
4. Testing the configuration

---

## 📧 Provider-Specific Setup

### **Option 1: Gmail** (Most Common)

#### Step 1: Generate App Password

1. Go to: https://myaccount.google.com/apppasswords
2. Sign in to your Gmail account
3. Select app: "Mail"
4. Select device: "Mac" or "Other"
5. Click "Generate"
6. **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)

#### Step 2: Configure Environment Variables

Add these lines to `~/.zshrc`:

```bash
# Staff Rota Email Configuration (Gmail)
export EMAIL_HOST="smtp.gmail.com"
export EMAIL_PORT="587"
export EMAIL_USE_TLS="True"
export EMAIL_USER="your-email@gmail.com"
export EMAIL_PASSWORD="abcd efgh ijkl mnop"  # Your App Password
export DEFAULT_FROM_EMAIL="Staff Rota System <your-email@gmail.com>"
```

#### Step 3: Apply Changes

```bash
source ~/.zshrc
```

---

### **Option 2: Office 365**

Add these lines to `~/.zshrc`:

```bash
# Staff Rota Email Configuration (Office 365)
export EMAIL_HOST="smtp.office365.com"
export EMAIL_PORT="587"
export EMAIL_USE_TLS="True"
export EMAIL_USER="your-email@company.com"
export EMAIL_PASSWORD="your-password"
export DEFAULT_FROM_EMAIL="Staff Rota System <your-email@company.com>"
```

Then apply:
```bash
source ~/.zshrc
```

---

### **Option 3: Other SMTP Server**

Add these lines to `~/.zshrc`:

```bash
# Staff Rota Email Configuration (Custom SMTP)
export EMAIL_HOST="smtp.yourserver.com"
export EMAIL_PORT="587"  # or 465 for SSL
export EMAIL_USE_TLS="True"  # or False
export EMAIL_USE_SSL="False"  # or True for port 465
export EMAIL_USER="your-email@domain.com"
export EMAIL_PASSWORD="your-password"
export DEFAULT_FROM_EMAIL="Staff Rota System <your-email@domain.com>"
```

Then apply:
```bash
source ~/.zshrc
```

---

## ✅ Testing Your Configuration

### Test 1: Check Environment Variables

```bash
echo $EMAIL_HOST
# Should show: smtp.gmail.com (or your SMTP server)

echo $EMAIL_USER
# Should show: your-email@gmail.com
```

If empty, you forgot to run `source ~/.zshrc`

### Test 2: Dry Run (Preview Only)

```bash
cd /Users/deansockalingum/Staff\ Rota/rotasystems
python3 manage.py send_leave_reminders --specific-staff ADMIN001 --dry-run
```

This previews the email without sending.

### Test 3: Send Real Test Email

```bash
python3 manage.py send_leave_reminders --specific-staff ADMIN001
```

Check ADMIN001's inbox for the email!

### Test 4: Use the Wrapper Script

```bash
./send_leave_emails.sh test
```

---

## 🔄 Switching Between Modes

### Switch to Production (SMTP)

```bash
# Uncomment the EMAIL_HOST line in ~/.zshrc
source ~/.zshrc
```

### Switch to Testing (Console)

```bash
# Comment out EMAIL_HOST in ~/.zshrc by adding # at the start:
# export EMAIL_HOST="smtp.gmail.com"

source ~/.zshrc
```

Or use the setup script:
```bash
./setup_email.sh
# Choose option 4: Switch to Console/Testing mode
```

---

## 🔒 Security Best Practices

### ✅ DO:
- Use App Passwords for Gmail (not your regular password)
- Store credentials in environment variables (never in code)
- Add `~/.zshrc` to `.gitignore` if committing code
- Use different credentials for dev/staging/production
- Regularly rotate passwords
- Test with a personal email first

### ❌ DON'T:
- Commit passwords to git
- Use your main email password
- Share credentials in plain text
- Store passwords in settings.py

---

## 🐛 Troubleshooting

### Problem: "Connection refused" or timeout

**Check:**
```bash
# Test SMTP connection
telnet smtp.gmail.com 587
# Should connect. Press Ctrl+] then type 'quit'
```

**Solutions:**
- Check firewall isn't blocking port 587
- Try port 465 with SSL instead of TLS
- Verify SMTP server address is correct

### Problem: "Authentication failed"

**Check:**
```bash
echo $EMAIL_USER
echo $EMAIL_PASSWORD
```

**Solutions:**
- Gmail: Did you create an App Password?
- Office 365: Try enabling "Less secure app access"
- Verify credentials are correct
- Check for typos in `~/.zshrc`

### Problem: Environment variables not set

```bash
# Check if set
echo $EMAIL_HOST

# If empty, reload shell config
source ~/.zshrc

# Verify it's in the file
grep EMAIL_HOST ~/.zshrc
```

### Problem: Still using console mode

```bash
# Check if EMAIL_HOST is commented out
grep EMAIL_HOST ~/.zshrc

# Should be:
export EMAIL_HOST="smtp.gmail.com"

# NOT:
# export EMAIL_HOST="smtp.gmail.com"
```

### Problem: Emails going to spam

**Solutions:**
- Add your domain to SPF records (advanced)
- Use a professional email address
- Ask recipients to whitelist your email
- Send a test to yourself first and mark "Not Spam"

---

## 📊 Verification Checklist

Before going live, verify:

- [ ] Environment variables are set: `echo $EMAIL_HOST`
- [ ] Shell config sourced: `source ~/.zshrc`
- [ ] Test email works: `./send_leave_emails.sh test`
- [ ] Real email sends: `./send_leave_emails.sh specific ADMIN001`
- [ ] Email arrives in inbox (check spam folder)
- [ ] Email looks correct (HTML formatting)
- [ ] "From" address is correct
- [ ] Subject line is correct
- [ ] Links work (if any)
- [ ] Plain text fallback works

---

## 🔄 How It Works

The system automatically detects your configuration:

```python
# In settings.py (you don't need to edit this)
if os.environ.get('EMAIL_HOST'):
    # Production SMTP - uses environment variables
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST')
    EMAIL_USER = os.environ.get('EMAIL_USER')
    # ... etc
else:
    # Development - console backend
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

When `EMAIL_HOST` environment variable is set → Uses SMTP  
When `EMAIL_HOST` is not set → Uses console mode

---

## 📝 Quick Reference

| Task | Command |
|------|---------|
| Setup email (interactive) | `./setup_email.sh` |
| View current settings | `./setup_email.sh` → Option 6 |
| Test configuration | `./setup_email.sh` → Option 5 |
| Switch to production | Set `EMAIL_HOST` in `~/.zshrc` |
| Switch to testing | Unset/comment `EMAIL_HOST` in `~/.zshrc` |
| Send test email | `./send_leave_emails.sh test` |
| Check environment | `echo $EMAIL_HOST` |
| Reload config | `source ~/.zshrc` |

---

## 🎯 Common Scenarios

### Scenario 1: First Time Setup

```bash
cd /Users/deansockalingum/Staff\ Rota/rotasystems
./setup_email.sh
# Choose option 1 (Gmail) or 2 (Office 365)
# Enter credentials
source ~/.zshrc
./send_leave_emails.sh test
```

### Scenario 2: Testing Before Production

```bash
# Currently in console mode (testing)
./send_leave_emails.sh test  # Preview

# Ready for production
./setup_email.sh  # Configure SMTP
source ~/.zshrc
./send_leave_emails.sh specific ADMIN001  # Real test
```

### Scenario 3: Switching Back to Testing

```bash
./setup_email.sh
# Choose option 4 (Console mode)
source ~/.zshrc
# Now emails print to terminal again
```

### Scenario 4: Changing Email Provider

```bash
# Edit ~/.zshrc
nano ~/.zshrc

# Change EMAIL_HOST from Gmail to Office 365
# Before: export EMAIL_HOST="smtp.gmail.com"
# After:  export EMAIL_HOST="smtp.office365.com"

# Also update EMAIL_USER, EMAIL_PASSWORD, etc.

# Apply changes
source ~/.zshrc

# Test
./send_leave_emails.sh test
```

---

## 🚀 Production Deployment

When you're ready to go live:

1. **Configure Email**
   ```bash
   ./setup_email.sh
   ```

2. **Test Thoroughly**
   ```bash
   ./send_leave_emails.sh test
   ./send_leave_emails.sh specific ADMIN001
   ```

3. **Install Automation**
   ```bash
   ./install_scheduled_tasks.sh
   ```

4. **Verify Cron Jobs**
   ```bash
   crontab -l
   ```

5. **Monitor Logs**
   ```bash
   tail -f /var/log/rotasystem/leave_reminders.log
   ```

6. **Send First Campaign**
   ```bash
   ./send_leave_emails.sh monthly
   ```

---

## 📖 Related Documentation

- **LEAVE_EMAILS_QUICK_START.md** - Quick reference for email commands
- **LEAVE_REMINDER_EMAILS.md** - Full feature documentation
- **EMAIL_SETUP_GUIDE.md** - This file

---

## ✅ Summary

**You now have:**
- ✅ Secure environment variable configuration
- ✅ Interactive setup script (`setup_email.sh`)
- ✅ Easy mode switching (testing ↔ production)
- ✅ No passwords in code
- ✅ Simple testing workflow
- ✅ Production-ready SMTP support

**Next steps:**
1. Run `./setup_email.sh` to configure
2. Test with `./send_leave_emails.sh test`
3. Send real test: `./send_leave_emails.sh specific ADMIN001`
4. Install automation: `./install_scheduled_tasks.sh`

🎉 **Your email system is ready for production!**
