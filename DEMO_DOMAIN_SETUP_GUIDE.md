# Demo Domain & Marketing Site Setup Guide
**Date:** January 8, 2026  
**Purpose:** Marketing website and demo instance for HSCP sales  

---

## 🎯 RECOMMENDED DOMAIN OPTIONS

### Primary Recommendation:
**`staffrotascotland.co.uk`** (£10-15/year)

**Pros:**
- ✅ Geographic targeting (Scotland)
- ✅ Professional .co.uk TLD
- ✅ Clear purpose
- ✅ Easy to remember

**Alternatives:**
- `nhsstaffrota.com` - Stronger NHS association but may cause confusion
- `staffrotasystem.com` - Generic, scalable to England/Wales
- `glasgowstaffrota.co.uk` - Too narrow, limits growth

### Subdomain Structure:
```
staffrotascotland.co.uk           → Marketing site
demo.staffrotascotland.co.uk      → Demo instance
docs.staffrotascotland.co.uk      → Documentation
support.staffrotascotland.co.uk   → Support portal (future)
```

---

## 📋 DOMAIN REGISTRATION CHECKLIST

### Step 1: Register Domain
**Recommended Registrar:** Namecheap, 123-reg, or GoDaddy

**Cost:** £10-15/year for .co.uk

**Settings:**
- ✅ Privacy protection enabled
- ✅ Auto-renewal enabled
- ✅ 2-factor authentication on registrar account

### Step 2: DNS Configuration
Point to your hosting provider:

```
A Record:    @              →  [Your server IP]
A Record:    demo           →  [Demo server IP]
A Record:    docs           →  [Docs server IP]
CNAME:       www            →  staffrotascotland.co.uk
TXT Record:  @              →  v=spf1 include:_spf.google.com ~all (email)
```

---

## 🖥️ HOSTING RECOMMENDATIONS

### Option 1: DigitalOcean (Recommended for Demo)
**Cost:** £12-24/month (Droplet)

**Pros:**
- ✅ Simple setup
- ✅ £200 free credit for new accounts
- ✅ Easy scaling
- ✅ Good documentation

**Plan:**
- **Marketing site:** Basic Droplet (£6/month, 1GB RAM)
- **Demo instance:** Standard Droplet (£12-24/month, 2-4GB RAM)

### Option 2: AWS Lightsail
**Cost:** £3.50-20/month

**Pros:**
- ✅ AWS ecosystem
- ✅ Cheap entry point
- ✅ Easy upgrade to full AWS

### Option 3: Linode/Vultr
**Cost:** £5-20/month

**Similar to DigitalOcean, slight price variations**

---

## 🚀 DEMO INSTANCE DEPLOYMENT

### Architecture:
```
demo.staffrotascotland.co.uk
├── Django application (your staff-rota-system)
├── PostgreSQL database
├── Redis cache
├── Nginx reverse proxy
├── SSL certificate (Let's Encrypt - FREE)
└── Automated backups
```

### Server Requirements (Minimum for Demo):
- **CPU:** 2 cores
- **RAM:** 4GB
- **Storage:** 25GB SSD
- **OS:** Ubuntu 22.04 LTS

### Deployment Steps:

#### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib \
  nginx redis-server certbot python3-certbot-nginx git

# Create deploy user
sudo useradd -m -s /bin/bash deploy
sudo usermod -aG sudo deploy
```

#### 2. Database Setup
```bash
# Create PostgreSQL database
sudo -u postgres psql

CREATE DATABASE staffrota_demo;
CREATE USER staffrota_demo WITH PASSWORD 'GENERATE_SECURE_PASSWORD';
ALTER ROLE staffrota_demo SET client_encoding TO 'utf8';
ALTER ROLE staffrota_demo SET default_transaction_isolation TO 'read committed';
ALTER ROLE staffrota_demo SET timezone TO 'Europe/London';
GRANT ALL PRIVILEGES ON DATABASE staffrota_demo TO staffrota_demo;
\q
```

#### 3. Application Deployment
```bash
# Clone repository
cd /home/deploy
git clone https://github.com/Dean-Sockalingum/staff-rota-system.git
cd staff-rota-system

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn  # Production WSGI server

# Create .env file for demo
cp .env.production .env
nano .env
```

**Demo .env Configuration:**
```bash
# Demo Instance Configuration
DEBUG=False
SECRET_KEY='your-generated-secret-key-from-.env.production'
ALLOWED_HOSTS=demo.staffrotascotland.co.uk

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=staffrota_demo
DB_USER=staffrota_demo
DB_PASSWORD='your-secure-password'
DB_HOST=localhost
DB_PORT=5432

# Redis Cache
REDIS_URL=redis://localhost:6379/1

# Email (for demo - use Gmail SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=demo@yourdomain.com
EMAIL_HOST_PASSWORD='app-specific-password'
DEFAULT_FROM_EMAIL=noreply@staffrotascotland.co.uk

# Demo-specific
DEMO_MODE=True  # Add this flag to identify demo instance
AUTO_RESET_DEMO=True  # Reset demo data nightly
```

#### 4. Initialize Application
```bash
# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load demo data (create this fixture)
python manage.py loaddata demo_data.json

# Collect static files
python manage.py collectstatic --noinput
```

#### 5. Gunicorn Setup
Create `/etc/systemd/system/staffrota-demo.service`:

```ini
[Unit]
Description=Staff Rota Demo Gunicorn
After=network.target

[Service]
User=deploy
Group=www-data
WorkingDirectory=/home/deploy/staff-rota-system
Environment="PATH=/home/deploy/staff-rota-system/venv/bin"
ExecStart=/home/deploy/staff-rota-system/venv/bin/gunicorn \
  --workers 3 \
  --bind unix:/home/deploy/staff-rota-system/staffrota.sock \
  rotasystems.wsgi:application

[Install]
WantedBy=multi-user.target
```

**Start service:**
```bash
sudo systemctl start staffrota-demo
sudo systemctl enable staffrota-demo
```

#### 6. Nginx Configuration
Create `/etc/nginx/sites-available/staffrota-demo`:

```nginx
server {
    listen 80;
    server_name demo.staffrotascotland.co.uk;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /home/deploy/staff-rota-system/staticfiles/;
    }

    location /media/ {
        alias /home/deploy/staff-rota-system/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/deploy/staff-rota-system/staffrota.sock;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
    }
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/staffrota-demo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 7. SSL Certificate (FREE)
```bash
sudo certbot --nginx -d demo.staffrotascotland.co.uk
```

Certbot will automatically:
- Obtain Let's Encrypt certificate
- Configure Nginx for HTTPS
- Set up auto-renewal

---

## 🎨 MARKETING SITE SETUP

### Option 1: Static Site (Recommended)
Use simple HTML/CSS or static generator:

**Tools:**
- **Hugo** (Fast, easy)
- **Jekyll** (GitHub Pages integration)
- **Plain HTML** (Maximum control)

**Host on:**
- GitHub Pages (FREE)
- Netlify (FREE tier)
- Vercel (FREE tier)

### Option 2: WordPress
If you need non-technical team members to update content.

**Cost:** £3-6/month (shared hosting)

### Marketing Site Content:

#### Homepage:
```
Hero Section:
- "AI-Powered Staff Scheduling for Scottish Care Services"
- "Reduce admin time by 89%. Save £500k+ annually."
- CTA: "Book a Demo" | "See Case Studies"

Feature Highlights:
- ML Forecasting (Prophet)
- Automated Scheduling
- Compliance Tracking
- Mobile App

Social Proof:
- "Trusted by 5 Glasgow care homes"
- "109,000+ shifts managed"
- "89% time savings validated"

CTA: "Try Free Demo" → demo.staffrotascotland.co.uk
```

#### Pages Structure:
```
/                      → Homepage
/features              → Detailed feature list
/case-studies          → Customer success stories
/pricing               → Implementation packages (Tier 2/3)
/demo                  → Link to demo.staffrotascotland.co.uk
/about                 → Your story, NHS alignment
/contact               → Contact form
/docs                  → Link to documentation
/blog                  → Future: Updates, best practices
```

---

## 📊 DEMO INSTANCE CONFIGURATION

### Demo Data Requirements:

Create realistic but anonymized data:

**5 Care Homes:**
1. Orchard Grove (reference from your test data)
2. Meadowburn
3. Hawthorn House
4. Riverside
5. Victoria Gardens

**User Accounts (for demo logins):**
```
Operational Manager: demo.om@staffrotascotland.co.uk / Demo2026!
Service Manager:     demo.sm@staffrotascotland.co.uk / Demo2026!
IDI Staff:           demo.idi@staffrotascotland.co.uk / Demo2026!
Head of Service:     demo.hos@staffrotascotland.co.uk / Demo2026!
Care Worker:         demo.staff@staffrotascotland.co.uk / Demo2026!
```

**Demo Data Characteristics:**
- 2-3 months of historical shifts
- Mix of day/night/twilight patterns
- Realistic leave requests
- Some compliance gaps (to demo alerts)
- ML forecasting with predictions visible

### Auto-Reset Script:
Create `reset_demo.py` to run nightly:

```python
#!/usr/bin/env python
"""
Reset demo instance to clean state nightly
Preserves demo user accounts, resets shifts to last 2 months
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from scheduling.models import Shift, LeaveRequest, ComplianceRecord

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Delete old data
        cutoff_date = timezone.now() - timedelta(days=60)
        Shift.objects.filter(date__lt=cutoff_date).delete()
        LeaveRequest.objects.filter(created_at__lt=cutoff_date).delete()
        ComplianceRecord.objects.filter(date__lt=cutoff_date).delete()
        
        # Reload demo fixture
        call_command('loaddata', 'demo_data.json')
        
        self.stdout.write(self.style.SUCCESS('Demo reset complete'))
```

**Cron job:**
```bash
0 2 * * * cd /home/deploy/staff-rota-system && venv/bin/python manage.py reset_demo
```

---

## 🔒 DEMO SECURITY CONSIDERATIONS

### Restrictions:
1. **Rate Limiting:** Max 100 requests/hour per IP
2. **No Email Sending:** Disable or use sandbox mode
3. **Read-Only Data:** Some features locked (can't delete care homes)
4. **Session Timeout:** 30 minutes of inactivity
5. **CAPTCHA:** On login page to prevent bot abuse

### Demo Banner:
Add prominent banner on demo site:

```html
<div class="demo-banner">
  ⚠️ This is a demo instance. Data resets nightly. 
  <a href="/contact">Contact us</a> for production deployment.
</div>
```

---

## 💰 COST SUMMARY

### Initial Setup (One-Time):
| Item | Cost |
|------|------|
| Domain registration (.co.uk) | £10-15 |
| SSL certificate (Let's Encrypt) | FREE |
| **Total Initial** | **£10-15** |

### Monthly Recurring:
| Item | Cost |
|------|------|
| Demo server (DigitalOcean 4GB) | £24 |
| Marketing site (GitHub Pages) | FREE |
| Domain renewal (annual ÷ 12) | £1.25 |
| Backups (DigitalOcean) | £4.80 |
| **Total Monthly** | **£30** |

### Annual Total: £360-375

**ROI:** If demo generates 1 HSCP contract (£85k), ROI = 23,333%

---

## 📈 DEMO ANALYTICS SETUP

### Recommended Tools:

#### 1. Google Analytics 4 (FREE)
Track:
- Visitors to marketing site
- Demo logins
- Feature usage in demo
- Geographic distribution

#### 2. Hotjar (FREE tier)
- Heatmaps showing where users click
- Session recordings
- User feedback surveys

#### 3. Custom Django Analytics
Add to demo instance:

```python
# Track feature usage
from django.db import models

class DemoUsageLog(models.Model):
    session_id = models.CharField(max_length=100)
    feature = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    user_type = models.CharField(max_length=50)  # OM, SM, etc.
    
    class Meta:
        db_table = 'demo_usage_log'
```

**Track metrics:**
- Which features get used most
- Average session duration
- Conversion rate (demo → contact form)

---

## 🎯 SUCCESS METRICS

### Demo Effectiveness KPIs:

**Engagement:**
- Average session duration > 10 minutes (indicates serious evaluation)
- Pages per session > 5
- Return visitors > 20%

**Conversion:**
- Demo → Contact form: Target 5-10%
- Contact → Sales call: Target 50%
- Sales call → Pilot: Target 30%

**Feature Interest:**
- ML forecasting views (high value feature)
- Report generation usage
- Mobile app testing

---

## 🚀 LAUNCH CHECKLIST

### Pre-Launch (Week 1):
- [ ] Register domain
- [ ] Set up hosting account
- [ ] Deploy demo instance
- [ ] Create demo data fixture
- [ ] Test all user roles
- [ ] Set up SSL certificate
- [ ] Configure auto-reset script
- [ ] Add demo banner/disclaimers

### Marketing Site (Week 2):
- [ ] Build marketing pages
- [ ] Write feature descriptions
- [ ] Create demo video walkthrough
- [ ] Add contact form
- [ ] Set up Google Analytics
- [ ] Test mobile responsiveness

### Content (Week 3):
- [ ] Write 1-2 case studies (from pilot)
- [ ] Create pricing page (Tier 2/3 packages)
- [ ] Screenshot gallery
- [ ] FAQ section
- [ ] Documentation links

### Launch (Week 4):
- [ ] Final testing
- [ ] Soft launch to test users
- [ ] Monitor analytics
- [ ] Fix any issues
- [ ] Public announcement

---

## 📞 DEMO SUPPORT STRATEGY

### Guided Demo Option:
Offer 30-minute Zoom walkthrough for serious prospects:

**Email Template:**
```
Subject: Interested in Our Demo?

Hi [Name],

Thanks for trying our demo! Would you like a guided 30-minute 
walkthrough where we:

✓ Customize demo to your care home setup
✓ Show advanced features (ML forecasting, automation)
✓ Answer your specific questions
✓ Discuss implementation timeline

Book a time: [Calendly link]

Best regards,
Dean
```

### Self-Service Resources:
- Video tutorials (5-10 minutes each)
- Interactive tooltips in demo
- Help icon with contextual guidance
- Download sample reports

---

## 🔄 MAINTENANCE PLAN

### Daily:
- Auto-reset demo data (2 AM cron job)
- Check server health (uptime monitoring)

### Weekly:
- Review analytics
- Check for errors in logs
- Update demo data if needed

### Monthly:
- Security updates
- Dependency updates
- Backup verification
- Performance review

### Quarterly:
- Add new features to demo
- Update screenshots/videos
- Refresh case studies
- Review hosting costs

---

## 🎬 IMMEDIATE ACTION PLAN

### This Week:
1. **Register domain:** staffrotascotland.co.uk (1 hour)
2. **Set up DigitalOcean account:** Use £200 free credit (1 hour)
3. **Deploy demo instance:** Follow steps above (4-6 hours)

### Next Week:
4. **Create demo data fixture:** Based on your existing test data (4 hours)
5. **Build simple marketing page:** Use HTML template or Hugo (6 hours)
6. **Test demo thoroughly:** All roles, features (4 hours)

### Week 3:
7. **Create demo video:** Screen recording with voiceover (6 hours)
8. **Write first case study:** From pilot customer (4 hours)
9. **Set up analytics:** Google Analytics + Hotjar (2 hours)

**Total Time Investment:** ~30-35 hours over 3 weeks

**Total Cost:** £360/year + your time

**Expected ROI:** 1 HSCP contract = £85,000 (23,611% ROI)

---

## 📝 NEXT STEPS

1. **Decision:** Approve £360/year budget for demo infrastructure
2. **Action:** Register staffrotascotland.co.uk this week
3. **Technical:** Deploy demo instance (use existing .env.production as template)
4. **Content:** Prepare pilot approach materials (next document)

**Ready to proceed?** Start with domain registration while I prepare the pilot proposal templates.
