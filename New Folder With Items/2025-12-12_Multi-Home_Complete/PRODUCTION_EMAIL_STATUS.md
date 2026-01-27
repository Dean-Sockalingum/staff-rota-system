# 📧 Production Email Setup - Complete! ✅

## Current Status

✅ **Email system configured with environment variables**  
✅ **Interactive setup script created** (`setup_email.sh`)  
✅ **Currently in TESTING mode** (safe - emails print to terminal)  
⏸️ **Production SMTP not yet activated**  

---

## What's Been Done

### 1. Settings.py Updated ✅
- Automatically detects environment variables
- Uses console mode when `EMAIL_HOST` is not set
- Uses SMTP when `EMAIL_HOST` is configured
- No passwords stored in code (secure!)

### 2. Interactive Setup Script Created ✅
**File:** `setup_email.sh`

**Features:**
- Configure Gmail SMTP (guided)
- Configure Office 365 SMTP (guided)  
- Configure Custom SMTP (guided)
- Switch to console mode
- Test email configuration
- View current settings

### 3. Documentation Created ✅
- **EMAIL_SETUP_PRODUCTION.md** - Complete setup guide
- **LEAVE_EMAILS_QUICK_START.md** - Quick reference
- **LEAVE_REMINDER_EMAILS.md** - Full feature docs

---

## 🚀 How to Activate Production Email

### Quick Method (Recommended)

```bash
cd /Users/deansockalingum/Staff\ Rota/rotasystems

# Run interactive setup
./setup_email.sh

# Choose:
#   Option 1: Gmail (most common)
#   Option 2: Office 365
#   Option 3: Custom SMTP

# Follow prompts to enter:
#   - Email address
#   - Password/App Password
#   - From name

# Apply changes
source ~/.zshrc

# Test it works
./send_leave_emails.sh test
```

### Manual Method

Edit `~/.zshrc` and add:

```bash
# For Gmail:
export EMAIL_HOST="smtp.gmail.com"
export EMAIL_PORT="587"
export EMAIL_USE_TLS="True"
export EMAIL_USER="your-email@gmail.com"
export EMAIL_PASSWORD="your-app-password"  # 16-char from Google
export DEFAULT_FROM_EMAIL="Staff Rota System <your-email@gmail.com>"

# For Office 365:
export EMAIL_HOST="smtp.office365.com"
export EMAIL_PORT="587"
export EMAIL_USE_TLS="True"
export EMAIL_USER="your-email@company.com"
export EMAIL_PASSWORD="your-password"
export DEFAULT_FROM_EMAIL="Staff Rota System <your-email@company.com>"
```

Then:
```bash
source ~/.zshrc
./send_leave_emails.sh test
```

---

## 📋 Pre-Production Checklist

Before activating production email:

- [ ] Choose email provider (Gmail recommended for testing)
- [ ] Create App Password (Gmail) or get credentials (Office 365)
- [ ] Run `./setup_email.sh` to configure
- [ ] Run `source ~/.zshrc` to apply
- [ ] Test with: `./send_leave_emails.sh test`
- [ ] Send real test: `./send_leave_emails.sh specific ADMIN001`
- [ ] Verify email received and looks correct
- [ ] Check spam folder if needed
- [ ] Install automation: `./install_scheduled_tasks.sh`
- [ ] Monitor logs: `tail -f /var/log/rotasystem/leave_reminders.log`

---

## 🔄 How Environment Variables Work

### Console Mode (Current - Safe for Testing)
```bash
# No EMAIL_HOST set
$ echo $EMAIL_HOST
[empty]

# Django uses: django.core.mail.backends.console.EmailBackend
# Result: Emails print to terminal (no real emails sent)
```

### Production Mode (After Configuration)
```bash
# EMAIL_HOST is set
$ echo $EMAIL_HOST
smtp.gmail.com

# Django uses: django.core.mail.backends.smtp.EmailBackend
# Result: Real emails sent via SMTP
```

**Switching is automatic!** Just set or unset `EMAIL_HOST`.

---

## 🧪 Testing Steps

### 1. Check Current Mode
```bash
./setup_email.sh
# Choose option 6: View current settings
```

### 2. Preview Email (Dry Run)
```bash
./send_leave_emails.sh test
# Shows what email would look like
# Doesn't actually send anything
```

### 3. Send Test Email
```bash
# After configuring production email
./send_leave_emails.sh specific ADMIN001
# Sends real email to ADMIN001
```

### 4. Verify Email
- Check ADMIN001's inbox
- Verify sender name and address
- Check email formatting (should be beautiful HTML)
- Verify leave statistics are correct
- Click "Request Leave Now" button (should work)

---

## 📊 Email System Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Environment Variables (~/.zshrc)                       │
│  ┌───────────────────────────────────────────────────┐ │
│  │ EMAIL_HOST="smtp.gmail.com"                       │ │
│  │ EMAIL_USER="your-email@gmail.com"                 │ │
│  │ EMAIL_PASSWORD="app-password"                     │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  Django Settings (rotasystems/settings.py)              │
│  ┌───────────────────────────────────────────────────┐ │
│  │ if EMAIL_HOST:                                    │ │
│  │   → Use SMTP backend (production)                 │ │
│  │ else:                                             │ │
│  │   → Use console backend (testing)                 │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  Email Sending                                          │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Management Command:                               │ │
│  │   send_leave_reminders.py                         │ │
│  │                                                   │ │
│  │ Wrapper Script:                                   │ │
│  │   send_leave_emails.sh                            │ │
│  │                                                   │ │
│  │ Cron Automation:                                  │ │
│  │   install_scheduled_tasks.sh                      │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## 🔐 Security Features

### ✅ Implemented
- Environment variables (not in code)
- No passwords committed to git
- Automatic mode detection
- Interactive script hides password input
- Shell config backup before changes

### 📝 Recommended
- Use App Passwords (Gmail)
- Different credentials for dev/prod
- Regular password rotation
- Whitelist IP addresses (if supported)
- Monitor email logs

---

## 📖 Documentation Files

| File | Purpose |
|------|---------|
| `EMAIL_SETUP_PRODUCTION.md` | Complete setup guide (this file) |
| `LEAVE_EMAILS_QUICK_START.md` | Quick reference for commands |
| `LEAVE_REMINDER_EMAILS.md` | Full feature documentation |
| `setup_email.sh` | Interactive configuration script |
| `send_leave_emails.sh` | Convenient email sending wrapper |

---

## 🎯 Common Tasks

### Check Current Configuration
```bash
./setup_email.sh
# Choose option 6
```

### Switch to Gmail
```bash
./setup_email.sh
# Choose option 1
# Follow prompts
source ~/.zshrc
```

### Switch to Office 365
```bash
./setup_email.sh
# Choose option 2
# Follow prompts
source ~/.zshrc
```

### Switch Back to Testing
```bash
./setup_email.sh
# Choose option 4
source ~/.zshrc
```

### Test Email System
```bash
./setup_email.sh
# Choose option 5
```

### Send Monthly Reminders
```bash
./send_leave_emails.sh monthly
```

---

## 🚨 Troubleshooting

### "Command not found: setup_email.sh"
```bash
chmod +x setup_email.sh
./setup_email.sh
```

### "Environment variables not set"
```bash
source ~/.zshrc
echo $EMAIL_HOST  # Should show smtp server
```

### "Still in console mode"
```bash
# Check if EMAIL_HOST is commented
grep EMAIL_HOST ~/.zshrc

# Should be:
export EMAIL_HOST="smtp.gmail.com"

# NOT:
# export EMAIL_HOST="smtp.gmail.com"
```

### "Authentication failed"
- Gmail: Use App Password (not regular password)
- Office 365: Check password is correct
- Verify EMAIL_USER matches EMAIL_PASSWORD

---

## ✅ Summary

**What's Ready:**
- ✅ Secure environment variable system
- ✅ Interactive setup script
- ✅ Automatic mode detection
- ✅ Testing mode active (safe)
- ✅ Production mode ready to activate
- ✅ Full documentation
- ✅ Email reminder commands
- ✅ Automation scripts

**Next Steps:**
1. Run `./setup_email.sh` when ready for production
2. Configure your email provider (Gmail/Office 365)
3. Test with `./send_leave_emails.sh test`
4. Send real test to ADMIN001
5. Install automation: `./install_scheduled_tasks.sh`

**Current Mode:** 🟢 TESTING (Safe - No real emails sent)

**To Activate Production:** Run `./setup_email.sh` → Choose option 1 or 2

---

🎉 **Your production email system is ready to activate!**

Just run `./setup_email.sh` when you're ready to start sending real emails.
