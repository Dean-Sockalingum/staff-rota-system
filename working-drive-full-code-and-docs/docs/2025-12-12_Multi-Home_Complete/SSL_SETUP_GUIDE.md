# SSL/TLS Configuration Guide
**Document:** Production HTTPS Setup  
**Date:** January 6, 2026  
**Status:** Implementation Ready

---

## Overview

This guide covers SSL/TLS certificate setup for secure HTTPS access to the Staff Rota System in production environments.

## Options

### Option 1: Let's Encrypt (Recommended - FREE)

**Advantages:**
- Free, automated, renewable certificates
- Trusted by all major browsers
- Easy renewal with Certbot
- No cost for multi-domain certificates

**Requirements:**
- Domain name pointing to server
- Port 80 and 443 accessible
- Root/sudo access to server

**Setup Steps:**

1. **Install Certbot**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install certbot python3-certbot-nginx

# macOS
brew install certbot
```

2. **Obtain Certificate**
```bash
# For Nginx (recommended)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# For standalone (if not using Nginx)
sudo certbot certonly --standalone -d yourdomain.com
```

3. **Update Django Settings**

Create `staff_rota_system/settings_production.py`:
```python
from .settings import *

# Security Settings
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com', 'your-server-ip']

# HTTPS/SSL Configuration
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HSTS Settings (enable after confirming HTTPS works)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Certificate paths (for Let's Encrypt)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

4. **Configure Nginx as Reverse Proxy**

Create `/etc/nginx/sites-available/staff-rota`:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Certificate paths (Certbot will configure these)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL Configuration (Mozilla Intermediate)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/letsencrypt/live/yourdomain.com/chain.pem;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Static files
    location /static/ {
        alias /path/to/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /path/to/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete/media/;
        expires 30d;
    }
    
    # Proxy to Django
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Client body size (for file uploads)
    client_max_body_size 10M;
}
```

5. **Enable and Test Configuration**
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/staff-rota /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

# Check SSL certificate
sudo certbot certificates
```

6. **Set Up Auto-Renewal**
```bash
# Test renewal
sudo certbot renew --dry-run

# Certbot auto-renewal is configured via systemd timer
sudo systemctl status certbot.timer

# Manual renewal (if needed)
sudo certbot renew
```

7. **Run Django with Production Settings**
```bash
cd /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete

# Using Gunicorn (recommended for production)
pip3 install gunicorn

gunicorn staff_rota_system.wsgi:application \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --access-logfile /var/log/gunicorn/access.log \
    --error-logfile /var/log/gunicorn/error.log \
    --env DJANGO_SETTINGS_MODULE=staff_rota_system.settings_production
```

8. **Create Systemd Service for Auto-Start**

Create `/etc/systemd/system/staff-rota.service`:
```ini
[Unit]
Description=Staff Rota Django Application
After=network.target

[Service]
Type=notify
User=your-username
Group=www-data
WorkingDirectory=/path/to/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
Environment="DJANGO_SETTINGS_MODULE=staff_rota_system.settings_production"
ExecStart=/usr/local/bin/gunicorn staff_rota_system.wsgi:application \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --access-logfile /var/log/gunicorn/access.log \
    --error-logfile /var/log/gunicorn/error.log
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable staff-rota
sudo systemctl start staff-rota
sudo systemctl status staff-rota
```

---

### Option 2: Commercial SSL Certificate (Paid)

**Use Cases:**
- Extended validation (EV) certificates
- Organization validation (OV) certificates
- Wildcard certificates for subdomains
- Longer validity periods (if available)

**Providers:**
- **DigiCert:** $218/year (OV), $595/year (EV)
- **Sectigo:** $73/year (OV), $149/year (EV)
- **GoDaddy:** $79/year (OV), $299/year (EV)

**Setup Steps:**

1. **Generate CSR (Certificate Signing Request)**
```bash
# Create private key
openssl genrsa -out yourdomain.key 2048

# Generate CSR
openssl req -new -key yourdomain.key -out yourdomain.csr

# Answer prompts:
# - Country: GB
# - State: Scotland
# - City: Glasgow
# - Organization: Your Care Home Group
# - Common Name: yourdomain.com
```

2. **Purchase Certificate**
- Submit CSR to certificate authority
- Complete domain validation (email, DNS, or file upload)
- Download certificate bundle (certificate + intermediate + root)

3. **Install Certificate**
```bash
# Copy files to secure location
sudo mkdir -p /etc/ssl/certs
sudo mkdir -p /etc/ssl/private

sudo cp yourdomain.crt /etc/ssl/certs/
sudo cp yourdomain.key /etc/ssl/private/
sudo cp ca-bundle.crt /etc/ssl/certs/

# Set permissions
sudo chmod 644 /etc/ssl/certs/yourdomain.crt
sudo chmod 644 /etc/ssl/certs/ca-bundle.crt
sudo chmod 600 /etc/ssl/private/yourdomain.key
```

4. **Update Nginx Configuration**
```nginx
ssl_certificate /etc/ssl/certs/yourdomain.crt;
ssl_certificate_key /etc/ssl/private/yourdomain.key;
ssl_trusted_certificate /etc/ssl/certs/ca-bundle.crt;
```

---

## Testing

### 1. SSL Certificate Validation
```bash
# Check certificate details
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Verify certificate chain
openssl s_client -connect yourdomain.com:443 -showcerts

# Check expiration
echo | openssl s_client -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates
```

### 2. Online SSL Test Tools
- **SSL Labs:** https://www.ssllabs.com/ssltest/
  - Target: A+ rating
  - Check for protocol support, cipher strength, certificate validity
  
- **SecurityHeaders.com:** https://securityheaders.com/
  - Target: A rating
  - Verify HSTS, CSP, X-Frame-Options headers

### 3. Browser Testing
- Chrome: Lock icon in address bar, click for certificate details
- Firefox: Lock icon → More Information → View Certificate
- Safari: Lock icon → Show Certificate

### 4. Django Security Check
```bash
cd /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
python3 manage.py check --deploy --settings=staff_rota_system.settings_production
```

Expected output: No issues found (or only warnings about SECURE_HSTS_SECONDS if not enabled yet)

---

## Troubleshooting

### Issue: Certificate Not Trusted

**Symptoms:** Browser shows "Not Secure" warning

**Solutions:**
1. Check certificate chain is complete (intermediate + root certificates)
2. Verify certificate matches domain name (check Common Name and SANs)
3. Clear browser cache and hard refresh (Cmd+Shift+R)
4. Check certificate hasn't expired: `openssl x509 -in cert.pem -noout -dates`

### Issue: Mixed Content Warnings

**Symptoms:** Some resources load over HTTP instead of HTTPS

**Solutions:**
1. Check all static file URLs use HTTPS or protocol-relative URLs
2. Update `SECURE_SSL_REDIRECT = True` in settings
3. Add `<meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests">` to base template
4. Audit templates for hardcoded http:// URLs

### Issue: Infinite Redirect Loop

**Symptoms:** Browser shows "Too many redirects" error

**Solutions:**
1. Check `SECURE_PROXY_SSL_HEADER` is set correctly
2. Verify Nginx is passing `X-Forwarded-Proto` header
3. Temporarily disable `SECURE_SSL_REDIRECT` to debug
4. Check for conflicting redirect rules in Nginx

### Issue: Certificate Renewal Fails

**Symptoms:** Certbot renewal fails with error

**Solutions:**
```bash
# Check Certbot logs
sudo tail -f /var/log/letsencrypt/letsencrypt.log

# Verify DNS is pointing to server
nslookup yourdomain.com

# Check ports 80 and 443 are open
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443

# Manual renewal with verbose output
sudo certbot renew --dry-run --verbose
```

---

## Security Hardening

### 1. Enable HTTP Strict Transport Security (HSTS)

After confirming HTTPS works, enable HSTS to prevent downgrade attacks:

```python
# settings_production.py
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

**⚠️ Warning:** HSTS is irreversible for the specified duration. Test thoroughly before enabling!

### 2. Certificate Transparency Monitoring

Monitor certificate issuance for your domain:
- **crt.sh:** https://crt.sh/?q=yourdomain.com
- **Facebook CT Monitor:** https://developers.facebook.com/tools/ct/
- Set up alerts for unexpected certificate issuance

### 3. CAA DNS Records

Restrict which Certificate Authorities can issue certificates for your domain:

```bash
# Add CAA record to DNS
yourdomain.com. IN CAA 0 issue "letsencrypt.org"
yourdomain.com. IN CAA 0 issuewild "letsencrypt.org"
yourdomain.com. IN CAA 0 iodef "mailto:security@yourdomain.com"
```

### 4. OCSP Stapling

Enable OCSP stapling in Nginx (already in configuration above):
```nginx
ssl_stapling on;
ssl_stapling_verify on;
ssl_trusted_certificate /etc/letsencrypt/live/yourdomain.com/chain.pem;
```

Verify with:
```bash
openssl s_client -connect yourdomain.com:443 -status -servername yourdomain.com
```

---

## Monitoring

### 1. Certificate Expiration Alerts

Set up automated monitoring:

**Create monitoring script** `/usr/local/bin/check-ssl-expiry.sh`:
```bash
#!/bin/bash
DOMAIN="yourdomain.com"
EXPIRY_DATE=$(echo | openssl s_client -connect $DOMAIN:443 -servername $DOMAIN 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2)
EXPIRY_EPOCH=$(date -d "$EXPIRY_DATE" +%s)
NOW_EPOCH=$(date +%s)
DAYS_LEFT=$(( ($EXPIRY_EPOCH - $NOW_EPOCH) / 86400 ))

if [ $DAYS_LEFT -lt 30 ]; then
    echo "SSL certificate for $DOMAIN expires in $DAYS_LEFT days!"
    # Send email alert (configure mail command)
    echo "SSL certificate expires in $DAYS_LEFT days" | mail -s "SSL Alert: $DOMAIN" admin@yourdomain.com
fi
```

**Schedule daily check**:
```bash
# Add to crontab
sudo crontab -e

# Add line:
0 9 * * * /usr/local/bin/check-ssl-expiry.sh
```

### 2. SSL Labs Monitoring

Sign up for SSL Labs monitoring: https://www.ssllabs.com/ssltest/
- Get email alerts for rating changes
- Weekly re-scans
- Track configuration changes

---

## Checklist

### Pre-Production
- [ ] Domain name registered and DNS configured
- [ ] Ports 80 and 443 accessible from internet
- [ ] Firewall rules configured (ufw/iptables)
- [ ] Nginx installed and tested
- [ ] Gunicorn installed and tested
- [ ] SSL certificate obtained (Let's Encrypt or commercial)

### Configuration
- [ ] `settings_production.py` created with SSL settings
- [ ] Nginx configuration updated with SSL paths
- [ ] Static files collected: `python3 manage.py collectstatic`
- [ ] Database migrations applied: `python3 manage.py migrate`
- [ ] Systemd service created and enabled

### Testing
- [ ] HTTPS accessible: `https://yourdomain.com`
- [ ] HTTP redirects to HTTPS
- [ ] Static files load correctly
- [ ] Django admin accessible
- [ ] Staff Rota System login works
- [ ] SSL Labs rating: A or A+
- [ ] SecurityHeaders rating: A
- [ ] No mixed content warnings
- [ ] Certificate expiration > 30 days

### Security
- [ ] `DEBUG = False` in production
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] HSTS enabled (after testing HTTPS)
- [ ] Security headers configured
- [ ] OCSP stapling enabled
- [ ] CAA DNS records configured
- [ ] Certificate monitoring set up

### Monitoring
- [ ] Certificate expiration alerts configured
- [ ] SSL Labs monitoring enabled
- [ ] Nginx access/error logs monitored
- [ ] Django error logging configured (Sentry)
- [ ] Uptime monitoring configured

---

## Cost Summary

### Let's Encrypt (FREE)
- **Certificate Cost:** £0/year
- **Renewal:** Automatic (every 90 days)
- **Total Annual Cost:** £0

### Commercial Certificate
- **Domain Validation (DV):** £10-50/year
- **Organization Validation (OV):** £73-218/year
- **Extended Validation (EV):** £149-595/year
- **Wildcard:** £100-300/year

### Server Infrastructure (if needed)
- **VPS (2GB RAM, 2 CPU):** £10-20/month (£120-240/year)
- **Domain Registration:** £10-15/year
- **Total:** £130-255/year (using Let's Encrypt)

**Recommendation:** Use Let's Encrypt for production deployment. Zero cost, automated renewals, and trusted by all browsers.

---

## Next Steps

1. **Domain Setup** (if not done):
   - Register domain or use existing
   - Point DNS A record to server IP
   - Wait for DNS propagation (up to 48 hours)

2. **Server Preparation**:
   - Install Nginx: `sudo apt install nginx`
   - Install Certbot: `sudo apt install certbot python3-certbot-nginx`
   - Configure firewall: `sudo ufw allow 80,443/tcp`

3. **Certificate Installation**:
   - Run Certbot: `sudo certbot --nginx -d yourdomain.com`
   - Test auto-renewal: `sudo certbot renew --dry-run`

4. **Django Configuration**:
   - Create `settings_production.py`
   - Update `ALLOWED_HOSTS`
   - Enable SSL security settings

5. **Deployment**:
   - Set up Gunicorn service
   - Configure Nginx reverse proxy
   - Test HTTPS access

6. **Validation**:
   - SSL Labs test (target: A+)
   - SecurityHeaders test (target: A)
   - Django security check
   - User acceptance testing

**Estimated Time:** 2-4 hours (first-time setup)  
**Difficulty:** Moderate (requires command-line familiarity)

---

**Document Status:** Ready for Implementation  
**Last Updated:** January 6, 2026  
**Reviewed By:** Production Team  
**Next Review:** Before pilot deployment
