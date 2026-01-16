# NCSC Domain Unblock Request

## Issue
Domain `demo.therota.co.uk` and `therota.co.uk` are being blocked by NCSC Protective DNS service as a false positive.

## Domain Details
- **Domain:** demo.therota.co.uk, therota.co.uk
- **IP Address:** 159.65.18.80
- **Purpose:** NHS Staff Rota Management System Demo
- **Owner:** Dean Sockalingum
- **Organization:** NHS/Local Government

## Business Justification
This is a legitimate business application for NHS staff scheduling and rota management. The domain is required for:
- Senior management demonstrations
- Staff access to shift schedules
- Operational workforce planning
- Compliance with NHS workforce management requirements

## Technical Details
- Hosted on: DigitalOcean
- SSL Certificate: Let's Encrypt (valid)
- Framework: Django (Python web framework)
- Security: CSRF protection, HTTPS only, secure authentication
- No malicious content or activities

## Actions Required

### 1. Submit NCSC Review Request
**URL:** https://www.ncsc.gov.uk/information/secure-dns

**Email Template:**
```
To: NCSC Protective DNS Team
Subject: False Positive - Domain Unblock Request: demo.therota.co.uk

Dear NCSC Team,

I am writing to request a review and unblocking of the following domains that are currently flagged by NCSC Protective DNS:

Domains: demo.therota.co.uk, therota.co.uk
IP Address: 159.65.18.80

These domains host a legitimate NHS Staff Rota Management System for healthcare workforce planning. The blocking appears to be a false positive, likely due to the new domain registration.

Application Details:
- Purpose: NHS staff scheduling and workforce management
- Security: HTTPS with valid SSL, CSRF protection, secure authentication
- Framework: Django (industry-standard secure framework)
- Hosting: DigitalOcean UK

The site contains no malicious content and is used solely for internal NHS workforce management. The blocking is preventing legitimate business operations and senior management demonstrations.

Please review and whitelist these domains.

Contact Details:
[Your name]
[Your organization]
[Your email]
[Your phone]

Thank you,
Dean Sockalingum
```

### 2. Report False Positive to Cloudflare
**URL:** https://radar.cloudflare.com/scan

Submit both domains for security scan to prove they're clean.

### 3. Contact Your IT Department
```
Subject: Domain Whitelist Request - Legitimate Business System

Dear IT Support,

Please whitelist the following domains which are currently blocked by NCSC Protective DNS:

Domains: demo.therota.co.uk, therota.co.uk
Purpose: NHS Staff Rota Management System
Owner: [Your department]

These domains host our internal staff scheduling system and are required for business operations. The NCSC blocking appears to be a false positive on a newly registered domain.

The application uses industry-standard security (HTTPS, Django framework) and contains no malicious content.

Please whitelist these domains to allow staff access.

Thank you.
```

### 4. Alternative: Change DNS Provider (Temporary)
If unblocking takes too long, we can:
- Move DNS to Cloudflare (better reputation management)
- Add security headers to improve reputation
- Register with Google Safe Browsing

## Timeline
- IT Whitelist: 1-2 business days
- NCSC Review: 5-10 business days
- DNS Provider Change: Immediate

## Immediate Solution
For urgent demonstrations: Use local installation on laptop (http://127.0.0.1:8001)
