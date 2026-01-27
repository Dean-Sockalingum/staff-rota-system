# Cloudflare DNS Setup Guide

## Step 1: Create Cloudflare Account
1. Go to https://dash.cloudflare.com/sign-up
2. Sign up with your email
3. Verify email

## Step 2: Add Your Domain to Cloudflare
1. Click "Add a Site"
2. Enter: `therota.co.uk`
3. Select FREE plan
4. Click "Continue"

## Step 3: Review DNS Records
Cloudflare will scan your current DNS. You should see:
- A record: demo.therota.co.uk → 159.65.18.80
- A record: therota.co.uk → 159.65.18.80 (if exists)

If not shown, add them manually:
- Type: A
- Name: demo
- IPv4 address: 159.65.18.80
- Proxy status: Proxied (orange cloud) ✅
- TTL: Auto

Repeat for root domain:
- Type: A
- Name: @
- IPv4 address: 159.65.18.80
- Proxy status: Proxied (orange cloud) ✅
- TTL: Auto

## Step 4: Update Nameservers
Cloudflare will provide nameservers like:
```
adam.ns.cloudflare.com
roxy.ns.cloudflare.com
```

Go to your domain registrar (where you bought therota.co.uk):
1. Find "Nameservers" or "DNS Management"
2. Replace existing nameservers with Cloudflare's nameservers
3. Save changes

## Step 5: Configure Cloudflare Settings

### SSL/TLS Settings
1. Go to SSL/TLS tab
2. Set encryption mode to: **Full (strict)**
3. Enable "Always Use HTTPS"

### Security Settings
1. Go to Security → Settings
2. Security Level: Medium
3. Enable "Browser Integrity Check"

### Speed Settings
1. Go to Speed → Optimization
2. Enable "Auto Minify" for HTML, CSS, JS
3. Enable "Brotli"

## Step 6: Update Django Settings

Add to /home/staff-rota-system/rotasystems/settings.py:

```python
# Cloudflare Configuration
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Trust Cloudflare IPs
ALLOWED_HOSTS = ['demo.therota.co.uk', 'therota.co.uk', 'localhost']
```

## Step 7: Verify Setup
Wait 5-10 minutes for DNS propagation, then test:

```bash
# Check DNS is pointing to Cloudflare
dig demo.therota.co.uk

# Test HTTPS
curl -I https://demo.therota.co.uk
```

You should see Cloudflare in the response headers.

## Step 8: Wait for Activation
Cloudflare will email you when nameservers are updated (can take 24 hours max, usually 5 minutes).

## Benefits After Setup
✅ Better reputation (Cloudflare IPs instead of DigitalOcean)
✅ DDoS protection
✅ CDN/faster loading
✅ SSL managed by Cloudflare
✅ Less likely to be blocked by NCSC

## Notes
- Your site continues running on DigitalOcean
- Django app doesn't change
- Database stays the same
- Only DNS routing changes
