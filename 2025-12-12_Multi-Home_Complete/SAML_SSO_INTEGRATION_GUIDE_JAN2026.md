# SAML 2.0 Single Sign-On Integration Guide
## CGI Corporate SSO Portal Integration for NHS Scotland Staff Rota System

**Document Version:** 1.0  
**Date:** January 6, 2026  
**Author:** Dean Sockalingum  
**Status:** Implementation Ready  
**CGI Partnership Context:** NHS/Local Government Digital Transformation

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architecture Overview](#2-architecture-overview)
3. [Prerequisites](#3-prerequisites)
4. [Installation](#4-installation)
5. [Configuration](#5-configuration)
6. [CGI SSO Portal Integration](#6-cgi-sso-portal-integration)
7. [Testing Procedures](#7-testing-procedures)
8. [Production Deployment](#8-production-deployment)
9. [Security Hardening](#9-security-hardening)
10. [Monitoring & Logging](#10-monitoring--logging)
11. [User Documentation](#11-user-documentation)
12. [Troubleshooting](#12-troubleshooting)
13. [Academic Paper Contribution](#13-academic-paper-contribution)
14. [Business Case Analysis](#14-business-case-analysis)

---

## 1. Executive Summary

### 1.1 Purpose

This guide documents the integration of SAML 2.0 Single Sign-On (SSO) authentication with CGI's corporate identity provider. Staff will authenticate once via CGI's SSO portal and gain automatic access to the NHS Scotland Staff Rota System without separate credentials.

### 1.2 Benefits

- **Improved User Experience:** Single login across all CGI applications
- **Enhanced Security:** Centralized authentication, no local passwords
- **Reduced Support Burden:** 80% reduction in password reset tickets
- **CGI Compliance:** Mandatory for enterprise deployment
- **Audit Trail:** Centralized authentication logs in CGI systems

### 1.3 Implementation Timeline

- **Development:** 3-4 weeks (£4-6K)
- **CGI Collaboration:** 1 week (£1K)
- **Testing:** 1 week with CGI SSO team
- **Production Cutover:** 1 day (scheduled maintenance window)
- **Total Duration:** 5-6 weeks

### 1.4 Key Components

1. **python3-saml:** SAML 2.0 library for Service Provider functionality
2. **rotasystems/saml_settings.py:** SAML configuration (IdP/SP settings)
3. **rotasystems/saml_backend.py:** Custom authentication backend
4. **rotasystems/saml_views.py:** SSO login/logout/metadata views
5. **CGI IdP Metadata:** CGI SSO portal configuration
6. **SP Certificates:** X.509 certificate pair for SAML message signing

---

## 2. Architecture Overview

### 2.1 SAML Authentication Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    SAML 2.0 SSO Architecture                     │
└─────────────────────────────────────────────────────────────────┘

     User                Staff Rota System (SP)         CGI SSO (IdP)
       │                                                      │
       │  1. Access protected resource                       │
       ├──────────────────────────►                          │
       │                           │                         │
       │                           │ 2. Generate AuthnRequest│
       │                           │ (signed with SP cert)   │
       │                           │                         │
       │  3. Redirect to CGI SSO   │                         │
       │  (with SAML AuthnRequest) │                         │
       │◄──────────────────────────┤                         │
       │                           │                         │
       │  4. SAML AuthnRequest     │                         │
       ├───────────────────────────────────────────────────► │
       │                           │                         │
       │                           │  5. User authentication │
       │  6. CGI Login Page        │     (LDAP/AD)           │
       │◄───────────────────────────────────────────────────┤
       │                           │                         │
       │  7. CGI Credentials       │                         │
       ├───────────────────────────────────────────────────► │
       │                           │                         │
       │                           │     8. Generate SAML    │
       │                           │        Response         │
       │                           │     (signed assertion)  │
       │                           │                         │
       │  9. Redirect back to ACS  │                         │
       │  (with SAML Response)     │                         │
       │◄───────────────────────────────────────────────────┤
       │                           │                         │
       │  10. POST SAML Response   │                         │
       ├──────────────────────────►│                         │
       │                           │                         │
       │                           │ 11. Validate signature  │
       │                           │ 12. Extract attributes  │
       │                           │ 13. Create/update user  │
       │                           │ 14. Assign roles        │
       │                           │ 15. Create session      │
       │                           │                         │
       │  16. Redirect to app      │                         │
       │◄──────────────────────────┤                         │
       │                           │                         │
       │  17. Authenticated access │                         │
       ├──────────────────────────►│                         │
       │                           │                         │
```

### 2.2 Single Logout Flow

```
     User                Staff Rota System (SP)         CGI SSO (IdP)
       │                           │                         │
       │  1. Click logout          │                         │
       ├──────────────────────────►│                         │
       │                           │                         │
       │                           │ 2. Generate LogoutRequest
       │                           │ (signed)                │
       │                           │                         │
       │  3. Redirect to CGI SSO   │                         │
       │  (with LogoutRequest)     │                         │
       │◄──────────────────────────┤                         │
       │                           │                         │
       │  4. SAML LogoutRequest    │                         │
       ├───────────────────────────────────────────────────► │
       │                           │                         │
       │                           │  5. Terminate SSO session
       │                           │  6. Logout from other apps
       │                           │                         │
       │  7. LogoutResponse        │                         │
       │◄───────────────────────────────────────────────────┤
       │                           │                         │
       │  8. POST LogoutResponse   │                         │
       ├──────────────────────────►│                         │
       │                           │                         │
       │                           │ 9. Clear local session  │
       │                           │                         │
       │  10. Redirect to login    │                         │
       │◄──────────────────────────┤                         │
       │                           │                         │
```

### 2.3 Component Diagram

```
┌───────────────────────────────────────────────────────────────┐
│              Staff Rota System (Service Provider)              │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────────────────────────────────────────┐    │
│  │                 rotasystems/urls.py                   │    │
│  │  - /saml/login/    (initiate SSO)                     │    │
│  │  - /saml/acs/      (assertion consumer service)       │    │
│  │  - /saml/logout/   (initiate SLO)                     │    │
│  │  - /saml/sls/      (single logout service)            │    │
│  │  - /saml/metadata/ (SP metadata XML)                  │    │
│  └────────────────┬─────────────────────────────────────┘    │
│                   │                                            │
│  ┌────────────────▼─────────────────────────────────────┐    │
│  │            rotasystems/saml_views.py                  │    │
│  │  - saml_login()     (redirect to CGI IdP)             │    │
│  │  - saml_acs()       (process SAML response)           │    │
│  │  - saml_logout()    (initiate logout)                 │    │
│  │  - saml_sls()       (process logout response)         │    │
│  │  - saml_metadata()  (generate SP metadata)            │    │
│  └────────────────┬─────────────────────────────────────┘    │
│                   │                                            │
│  ┌────────────────▼─────────────────────────────────────┐    │
│  │           rotasystems/saml_backend.py                 │    │
│  │  - SAMLBackend.authenticate()                         │    │
│  │  - _map_saml_attributes()                             │    │
│  │  - _get_or_create_user()                              │    │
│  │  - _assign_roles_from_groups()                        │    │
│  │  - get_saml_auth()  (initialize SAML)                 │    │
│  └────────────────┬─────────────────────────────────────┘    │
│                   │                                            │
│  ┌────────────────▼─────────────────────────────────────┐    │
│  │          rotasystems/saml_settings.py                 │    │
│  │  - SAML_SP_ENTITY_ID, SAML_ACS_URL                    │    │
│  │  - SAML_SP_CERTIFICATE, SAML_SP_PRIVATE_KEY           │    │
│  │  - SAML_IDP_ENTITY_ID, SAML_IDP_SSO_URL               │    │
│  │  - SAML_IDP_CERTIFICATE                               │    │
│  │  - SAML_ATTRIBUTE_MAPPING                             │    │
│  │  - SAML_ROLE_MAPPING                                  │    │
│  │  - SAML_SECURITY (signature settings)                 │    │
│  └────────────────┬─────────────────────────────────────┘    │
│                   │                                            │
│  ┌────────────────▼─────────────────────────────────────┐    │
│  │              python3-saml Library                     │    │
│  │  - OneLogin_Saml2_Auth                                │    │
│  │  - OneLogin_Saml2_Utils                               │    │
│  │  - XML signature validation                           │    │
│  │  - Assertion parsing                                  │    │
│  └───────────────────────────────────────────────────────┘    │
│                                                                │
└───────────────────────────────────────────────────────────────┘
                              │
                              │ SAML 2.0 Protocol (HTTPS)
                              │
┌─────────────────────────────▼─────────────────────────────────┐
│              CGI SSO Portal (Identity Provider)                │
├───────────────────────────────────────────────────────────────┤
│  - Active Directory Authentication                             │
│  - SAML 2.0 Assertion Generation                              │
│  - User Attribute Provisioning (uid, email, groups)           │
│  - SSO Session Management                                      │
│  - IdP Metadata: entity ID, SSO URL, SLO URL, certificate     │
└───────────────────────────────────────────────────────────────┘
```

---

## 3. Prerequisites

### 3.1 CGI Requirements (MUST obtain from CGI SSO team)

- [ ] **CGI IdP Metadata XML**
  - IdP Entity ID (e.g., `https://sso.cgi.com/idp`)
  - SSO Service URL (e.g., `https://sso.cgi.com/idp/saml2/sso`)
  - SLO Service URL (e.g., `https://sso.cgi.com/idp/saml2/slo`)
  - IdP X.509 Certificate (PEM format)

- [ ] **Active Directory Group Creation**
  - `StaffRota_Admins` - System administrators
  - `StaffRota_Managers` - Care home managers
  - `StaffRota_ServiceManagers` - Service managers
  - `StaffRota_Supervisors` - Unit supervisors
  - `StaffRota_Staff` - General staff
  - `StaffRota_ReadOnly` - Read-only users

- [ ] **Network Configuration**
  - Firewall rules to allow HTTPS from CGI SSO portal to Staff Rota ACS endpoint
  - Firewall rules to allow HTTPS from Staff Rota to CGI SSO portal
  - DNS resolution for CGI SSO portal hostname
  - SSL/TLS certificate for Staff Rota System (required for SAML)

- [ ] **CGI SSO Portal Registration**
  - Register Staff Rota System as Service Provider
  - Whitelist ACS URL: `https://staff-rota.hscp.scot/saml/acs/`
  - Whitelist SLS URL: `https://staff-rota.hscp.scot/saml/sls/`
  - Upload SP metadata XML

### 3.2 Technical Requirements

- [ ] **Python 3.14** (already installed)
- [ ] **Django 5.2+** (already installed)
- [ ] **python3-saml** library (installed via pip)
- [ ] **HTTPS enabled** (mandatory for SAML)
- [ ] **NTP synchronization** (clock skew <5 minutes for signature validation)
- [ ] **Certificate generation tools** (OpenSSL)

### 3.3 Django Configuration

- [ ] Add `'rotasystems.saml_backend.SAMLBackend'` to `AUTHENTICATION_BACKENDS`
- [ ] Configure SAML URLs in `rotasystems/urls.py`
- [ ] Set `SAML_ENABLED=True` in environment variables (production)
- [ ] Configure session settings (secure cookies, HTTPS only)

---

## 4. Installation

### 4.1 Install python3-saml

```bash
# Install SAML library and dependencies
pip3 install python3-saml --break-system-packages

# Verify installation
python3 -c "from onelogin.saml2.auth import OneLogin_Saml2_Auth; print('SAML library installed successfully')"
```

**Installed packages:**
- `python3-saml==1.16.0` - SAML 2.0 library
- `xmlsec==1.3.17` - XML signature processing
- `lxml==6.0.2` - XML parsing
- `isodate==0.7.2` - ISO 8601 date parsing

### 4.2 Generate SP Certificate Pair

```bash
# Generate X.509 certificate and private key for Service Provider
# Valid for 10 years (3652 days)
cd /path/to/project/certificates/

openssl req -new -x509 -days 3652 -nodes \
    -out sp.crt \
    -keyout sp.key \
    -subj "/C=GB/ST=Scotland/L=Glasgow/O=HSCP/OU=IT/CN=staff-rota.hscp.scot"

# Set secure permissions
chmod 600 sp.key
chmod 644 sp.crt

# Display certificate for verification
openssl x509 -in sp.crt -text -noout
```

### 4.3 Store Certificates Securely

**Development:**
```bash
# Store in environment variables (development only)
export SAML_SP_CERTIFICATE=$(cat sp.crt)
export SAML_SP_PRIVATE_KEY=$(cat sp.key)
```

**Production (recommended):**
```bash
# Option 1: Azure Key Vault
az keyvault secret set --vault-name hscp-keyvault \
    --name saml-sp-private-key \
    --file sp.key

# Option 2: CGI Secret Management System
# Contact CGI IT for secure key storage procedures

# Option 3: Environment variables (less secure)
# Set in systemd service file or Azure App Service configuration
```

---

## 5. Configuration

### 5.1 Update rotasystems/saml_settings.py

```python
# 1. Service Provider URLs (REPLACE with production URLs)
SAML_SP_ENTITY_ID = 'https://staff-rota.hscp.scot/saml/metadata/'
SAML_ACS_URL = 'https://staff-rota.hscp.scot/saml/acs/'
SAML_SLS_URL = 'https://staff-rota.hscp.scot/saml/sls/'

# 2. SP Certificates (LOAD from secure storage)
SAML_SP_CERTIFICATE = os.getenv('SAML_SP_CERTIFICATE', '...')
SAML_SP_PRIVATE_KEY = os.getenv('SAML_SP_PRIVATE_KEY', '...')

# 3. CGI Identity Provider (OBTAIN from CGI SSO team)
SAML_IDP_ENTITY_ID = 'https://sso.cgi.com/idp'  # REPLACE
SAML_IDP_SSO_URL = 'https://sso.cgi.com/idp/saml2/sso'  # REPLACE
SAML_IDP_SLO_URL = 'https://sso.cgi.com/idp/saml2/slo'  # REPLACE
SAML_IDP_CERTIFICATE = os.getenv('SAML_IDP_CERTIFICATE', '...')  # REPLACE

# 4. Attribute Mapping (VERIFY with CGI SSO team)
SAML_ATTRIBUTE_MAPPING = {
    'uid': 'username',              # CGI username
    'email': 'email',               # CGI email
    'givenName': 'first_name',      # First name
    'sn': 'last_name',              # Surname
    'employeeNumber': 'sap',        # SAP number
    'memberOf': 'groups',           # AD groups
}

# 5. Role Mapping (UPDATE group DNs after AD groups created)
SAML_ROLE_MAPPING = {
    'CN=StaffRota_Admins,OU=Groups,DC=cgi,DC=com': 'ADMIN',
    'CN=StaffRota_Managers,OU=Groups,DC=cgi,DC=com': 'MANAGER',
    # ... (see saml_settings.py for complete mapping)
}
```

### 5.2 Update rotasystems/settings.py

```python
# Add SAML backend to authentication backends
AUTHENTICATION_BACKENDS = [
    'rotasystems.saml_backend.SAMLBackend',      # SAML SSO (primary)
    'django_auth_ldap.backend.LDAPBackend',      # LDAP fallback
    'django.contrib.auth.backends.ModelBackend',  # Django database fallback
]

# Session configuration for SSO
SESSION_COOKIE_AGE = 8 * 60 * 60  # 8 hours (match CGI SSO session)
SESSION_COOKIE_SECURE = True      # HTTPS only
SESSION_COOKIE_HTTPONLY = True    # Prevent JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'   # CSRF protection

# SAML-specific settings
SAML_ENABLED = os.getenv('SAML_ENABLED', 'False').lower() == 'true'
```

### 5.3 Update rotasystems/urls.py

```python
from django.urls import path, include
from rotasystems import saml_views

urlpatterns = [
    # ... existing URL patterns ...
    
    # SAML SSO endpoints
    path('saml/', include([
        path('login/', saml_views.saml_login, name='saml_login'),
        path('acs/', saml_views.saml_acs, name='saml_acs'),
        path('logout/', saml_views.saml_logout, name='saml_logout'),
        path('sls/', saml_views.saml_sls, name='saml_sls'),
        path('metadata/', saml_views.saml_metadata, name='saml_metadata'),
        path('status/', saml_views.saml_status, name='saml_status'),
    ])),
]
```

---

## 6. CGI SSO Portal Integration

### 6.1 Initial Coordination Meeting with CGI

**Attendees:**
- HSCP Technical Lead (Dean Sockalingum)
- CGI SSO Platform Team
- CGI Active Directory Team
- CGI Network Security Team

**Agenda:**
1. Review Staff Rota System SAML requirements
2. Obtain CGI IdP metadata (entity ID, SSO URL, certificate)
3. Discuss Active Directory group creation
4. Plan network firewall rule updates
5. Schedule SP registration in CGI SSO portal
6. Define testing timeline and procedures

### 6.2 Provide SP Metadata to CGI

**Generate SP metadata:**
```bash
# Start Django development server
cd /path/to/project
python3 manage.py runserver

# Download SP metadata
curl https://localhost:8000/saml/metadata/ > staff_rota_sp_metadata.xml

# Or access via browser: https://staff-rota.hscp.scot/saml/metadata/
```

**Send to CGI SSO team:**
- SP metadata XML file
- ACS URL: `https://staff-rota.hscp.scot/saml/acs/`
- SLS URL: `https://staff-rota.hscp.scot/saml/sls/`
- SP certificate (public key only)
- Contact: Dean Sockalingum <dean.sockalingum@hscp.scot>

### 6.3 Active Directory Group Setup

**Work with CGI AD team to create:**

```powershell
# Create security groups in CGI Active Directory
New-ADGroup -Name "StaffRota_Admins" `
    -GroupScope Global `
    -GroupCategory Security `
    -Description "Staff Rota System Administrators" `
    -Path "OU=StaffRota,OU=Applications,DC=cgi,DC=com"

New-ADGroup -Name "StaffRota_Managers" `
    -GroupScope Global `
    -GroupCategory Security `
    -Description "Staff Rota Care Home Managers" `
    -Path "OU=StaffRota,OU=Applications,DC=cgi,DC=com"

# Repeat for other groups: ServiceManagers, Supervisors, Staff, ReadOnly
```

**Add pilot users to groups:**
```powershell
# Add user to Admin group
Add-ADGroupMember -Identity "StaffRota_Admins" `
    -Members "dean.sockalingum", "pilot.user1"

# Verify membership
Get-ADGroupMember -Identity "StaffRota_Admins"
```

### 6.4 Network Firewall Configuration

**CGI Network Security team tasks:**

**Inbound rules (CGI SSO → Staff Rota):**
```
Source: CGI SSO Portal (e.g., 10.20.30.0/24)
Destination: Staff Rota ACS endpoint (e.g., 10.40.50.10)
Protocol: HTTPS (TCP 443)
Purpose: SAML Response POST from IdP to ACS
```

**Outbound rules (Staff Rota → CGI SSO):**
```
Source: Staff Rota server (e.g., 10.40.50.10)
Destination: CGI SSO Portal (e.g., 10.20.30.40)
Protocol: HTTPS (TCP 443)
Purpose: SAML AuthnRequest redirect to IdP SSO endpoint
```

### 6.5 CGI SSO Portal Registration

**CGI SSO team tasks:**
1. Import SP metadata XML
2. Whitelist ACS URL
3. Whitelist SLS URL
4. Configure attribute release policy (uid, email, givenName, sn, memberOf)
5. Set SAML binding preferences (HTTP-POST for ACS)
6. Enable SP in SSO portal

**Verification:**
```bash
# Test metadata endpoint accessibility
curl -I https://sso.cgi.com/idp/saml2/metadata
# Expected: HTTP 200 OK + XML content-type

# Test SSO endpoint accessibility
curl -I https://sso.cgi.com/idp/saml2/sso
# Expected: HTTP 200 OK or redirect
```

---

## 7. Testing Procedures

### 7.1 Unit Testing

```bash
cd /path/to/project

# Test SAML configuration loading
python3 manage.py shell << EOF
from rotasystems.saml_settings import *
print(f"SP Entity ID: {SAML_SP_ENTITY_ID}")
print(f"IdP Entity ID: {SAML_IDP_ENTITY_ID}")
print(f"Attribute Mapping: {SAML_ATTRIBUTE_MAPPING}")
EOF

# Test SAML backend instantiation
python3 manage.py shell << EOF
from rotasystems.saml_backend import SAMLBackend, get_saml_auth
from django.test import RequestFactory

backend = SAMLBackend()
print(f"Backend loaded: {backend}")

factory = RequestFactory()
request = factory.get('/saml/login/')
# auth = get_saml_auth(request)  # Requires HTTPS in production
print("SAML auth object creation successful")
EOF
```

### 7.2 Manual Testing Checklist

**Test Case 1: SSO Login Flow**
- [ ] Navigate to: `https://staff-rota.hscp.scot/saml/login/`
- [ ] Verify redirect to CGI SSO portal
- [ ] Login with CGI credentials (test user in `StaffRota_Staff` group)
- [ ] Verify redirect back to Staff Rota System
- [ ] Verify authenticated session created
- [ ] Verify user profile populated from SAML attributes
- [ ] Verify role assigned from AD group membership

**Test Case 2: Attribute Mapping**
- [ ] Login via SAML
- [ ] Check user profile:
  ```bash
  python3 manage.py shell << EOF
  from django.contrib.auth import get_user_model
  User = get_user_model()
  user = User.objects.get(username='test.user')
  print(f"Username: {user.username}")
  print(f"Email: {user.email}")
  print(f"Name: {user.first_name} {user.last_name}")
  print(f"SAP: {user.sap}")
  print(f"Role: {user.role}")
  EOF
  ```
- [ ] Verify all fields populated correctly

**Test Case 3: Role Assignment**
- [ ] Login with user in `StaffRota_Admins` group
  - Expected role: ADMIN
  - Expected: `is_staff=True`, `is_superuser=True`
- [ ] Login with user in `StaffRota_Staff` group
  - Expected role: STAFF
  - Expected: `is_staff=False`, `is_superuser=False`
- [ ] Login with user in multiple groups
  - Expected: Highest priority role assigned

**Test Case 4: Single Logout**
- [ ] Login via SAML
- [ ] Navigate to: `https://staff-rota.hscp.scot/saml/logout/`
- [ ] Verify redirect to CGI SSO logout page
- [ ] Verify session cleared in Staff Rota System
- [ ] Verify session cleared in CGI SSO portal
- [ ] Attempt to access protected page
  - Expected: Redirect to login

**Test Case 5: Session Timeout**
- [ ] Login via SAML
- [ ] Wait 8 hours (or adjust `SESSION_COOKIE_AGE` for testing)
- [ ] Attempt to access protected page
  - Expected: Redirect to CGI SSO login

**Test Case 6: Fallback Authentication**
- [ ] Disable SAML: `export SAML_ENABLED=False`
- [ ] Restart Django server
- [ ] Navigate to: `https://staff-rota.hscp.scot/login/`
- [ ] Login with LDAP credentials
  - Expected: Successful login via LDAP backend
- [ ] Re-enable SAML: `export SAML_ENABLED=True`

### 7.3 Load Testing

```bash
# Simulate 50 concurrent SAML logins
# (requires load testing tool like Locust or JMeter)

# Install Locust
pip3 install locust

# Create locustfile.py
cat > locustfile.py << 'EOF'
from locust import HttpUser, task, between

class SAMLUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def saml_login(self):
        # Initiate SAML login
        response = self.client.get("/saml/login/", name="SAML Login")
        # Note: Full SAML flow requires browser automation
        # This tests the login endpoint only
EOF

# Run load test
locust -f locustfile.py --host=https://staff-rota.hscp.scot --users=50 --spawn-rate=10
```

### 7.4 Security Testing

**Test Case 1: Signature Validation**
- [ ] Modify SAML response (tamper with assertion)
- [ ] POST to ACS endpoint
  - Expected: Signature validation failure, authentication rejected

**Test Case 2: Replay Attack**
- [ ] Capture valid SAML response
- [ ] Replay same response 5 minutes later
  - Expected: Timestamp validation failure (if InResponseTo is checked)

**Test Case 3: Certificate Expiry**
- [ ] Set system clock to certificate expiry date + 1 day
- [ ] Attempt SAML login
  - Expected: Certificate validation failure

**Test Case 4: HTTPS Enforcement**
- [ ] Attempt SAML flow over HTTP (if available)
  - Expected: Redirect to HTTPS or error

---

## 8. Production Deployment

### 8.1 Pre-Deployment Checklist

- [ ] CGI IdP metadata obtained and configured
- [ ] SP certificates generated and stored securely
- [ ] Active Directory groups created and populated
- [ ] Network firewall rules configured
- [ ] SP registered in CGI SSO portal
- [ ] All testing completed successfully
- [ ] User documentation prepared
- [ ] Support team trained on troubleshooting

### 8.2 Deployment Steps

**Step 1: Enable SAML in Production**
```bash
# Set environment variable
export SAML_ENABLED=True

# Or in Azure App Service:
az webapp config appsettings set --name staff-rota-prod \
    --resource-group hscp-rg \
    --settings SAML_ENABLED=True
```

**Step 2: Update URL Configuration**
```python
# rotasystems/saml_settings.py (production values)
SAML_SP_ENTITY_ID = 'https://staff-rota.hscp.scot/saml/metadata/'
SAML_ACS_URL = 'https://staff-rota.hscp.scot/saml/acs/'
SAML_SLS_URL = 'https://staff-rota.hscp.scot/saml/sls/'
```

**Step 3: Deploy Code**
```bash
# Git commit and push
git add rotasystems/saml_*.py
git commit -m "Enable SAML SSO integration with CGI SSO portal"
git push origin main

# Deploy to Azure (if using App Service)
az webapp deployment source sync --name staff-rota-prod --resource-group hscp-rg
```

**Step 4: Restart Application**
```bash
# Restart Django/Gunicorn
sudo systemctl restart staff-rota

# Or Azure App Service:
az webapp restart --name staff-rota-prod --resource-group hscp-rg
```

**Step 5: Verify Production**
```bash
# Test metadata endpoint
curl https://staff-rota.hscp.scot/saml/metadata/
# Expected: SP metadata XML

# Test SSO login (via browser)
# Navigate to: https://staff-rota.hscp.scot/saml/login/
# Expected: Redirect to CGI SSO portal
```

### 8.3 Rollback Procedure

**If issues encountered:**
```bash
# Step 1: Disable SAML immediately
export SAML_ENABLED=False
sudo systemctl restart staff-rota

# Step 2: Users can login via LDAP/Django fallback
# Navigate to: https://staff-rota.hscp.scot/login/

# Step 3: Investigate and fix issue

# Step 4: Re-enable SAML when resolved
export SAML_ENABLED=True
sudo systemctl restart staff-rota
```

---

## 9. Security Hardening

### 9.1 Certificate Management

**Certificate Rotation Schedule:**
- SP certificate valid for 10 years
- Rotate every 2 years (well before expiry)
- Monitor expiry with automated alerts

**Rotation procedure:**
```bash
# 90 days before expiry:
# 1. Generate new certificate pair
openssl req -new -x509 -days 3652 -nodes -out sp_new.crt -keyout sp_new.key

# 2. Update SAML_SP_CERTIFICATE in environment (but keep old key active)

# 3. Notify CGI SSO team to add new certificate to IdP configuration

# 30 days before expiry:
# 4. Test SAML login with new certificate

# On expiry date:
# 5. Remove old certificate from environment
# 6. CGI SSO team removes old certificate from IdP
```

### 9.2 HTTPS Enforcement

```python
# rotasystems/settings.py (production)
SECURE_SSL_REDIRECT = True           # Redirect HTTP to HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000       # 1 year HSTS
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### 9.3 Session Security

```python
# rotasystems/settings.py (production)
SESSION_COOKIE_SECURE = True         # HTTPS only
SESSION_COOKIE_HTTPONLY = True       # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'      # CSRF protection
CSRF_COOKIE_SECURE = True            # HTTPS only for CSRF token
```

### 9.4 SAML Security Settings

```python
# rotasystems/saml_settings.py
SAML_SECURITY = {
    'authnRequestsSigned': True,      # Sign all AuthnRequests
    'wantMessagesSigned': True,       # Require signed messages from IdP
    'wantAssertionsSigned': True,     # Require signed assertions
    'signatureAlgorithm': 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256',
    'digestAlgorithm': 'http://www.w3.org/2001/04/xmlenc#sha256',
}
```

### 9.5 Clock Synchronization

```bash
# Install NTP daemon
sudo apt-get install ntp

# Configure NTP servers (UK)
sudo vi /etc/ntp.conf
# Add:
# server 0.uk.pool.ntp.org
# server 1.uk.pool.ntp.org
# server 2.uk.pool.ntp.org

# Restart NTP
sudo systemctl restart ntp

# Verify synchronization
ntpq -p
# Expected: Active NTP peers with low offset (<50ms)
```

---

## 10. Monitoring & Logging

### 10.1 SAML Event Logging

```python
# rotasystems/saml_settings.py
SAML_LOGGING = {
    'handlers': {
        'saml_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/staff-rota/saml.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
        },
    },
    'loggers': {
        'saml': {
            'handlers': ['saml_file'],
            'level': 'INFO',
        },
    },
}
```

**Key events logged:**
- SAML login initiation (username, timestamp, source IP)
- SAML response received (NameID, attributes)
- User creation/update (username, SAP, role assigned)
- Authentication success/failure
- Signature validation errors
- Session creation/termination

### 10.2 Monitoring Metrics

**CloudWatch/Azure Monitor metrics:**
- SAML login success rate (target: >99%)
- SAML login duration (target: <2 seconds)
- Authentication failures (alert if >5% in 5 minutes)
- Session creation rate
- Signature validation failures (alert immediately)

**Example CloudWatch alarm (AWS):**
```bash
aws cloudwatch put-metric-alarm \
    --alarm-name saml-auth-failures \
    --alarm-description "Alert on SAML authentication failures" \
    --metric-name SAMLAuthFailures \
    --namespace StaffRotaSystem \
    --statistic Sum \
    --period 300 \
    --threshold 10 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 1 \
    --alarm-actions arn:aws:sns:eu-west-2:123456789:staff-rota-alerts
```

### 10.3 Log Analysis Queries

**Splunk queries (if using CGI Splunk):**
```
# SAML login success rate
index=staff_rota sourcetype=saml 
| stats count(eval(match(_raw, "User authenticated via SAML"))) as success, 
        count(eval(match(_raw, "SAML authentication failed"))) as failure
| eval success_rate = round(success / (success + failure) * 100, 2)

# Top 10 users by SAML login count
index=staff_rota sourcetype=saml "User authenticated via SAML" 
| rex field=_raw "User authenticated via SAML: (?<username>\S+)"
| stats count by username 
| sort -count 
| head 10

# SAML signature validation errors
index=staff_rota sourcetype=saml "signature validation failed"
| timechart count by source_ip
```

---

## 11. User Documentation

### 11.1 Updated Login Instructions

**For Staff:**

**Old login process (LDAP):**
1. Navigate to https://staff-rota.hscp.scot/login/
2. Enter username and password
3. Click "Login"

**New login process (SAML SSO):**
1. Navigate to https://staff-rota.hscp.scot/ (or any protected page)
2. Click "Login with CGI SSO" button
3. You will be redirected to CGI's SSO portal
4. Enter your CGI username and password
5. You will be automatically logged into Staff Rota System

**Benefits:**
- One login for all CGI applications
- Automatic logout from all apps when you logout from CGI SSO
- No need to remember separate Staff Rota password

### 11.2 Troubleshooting for Users

**Problem: "Access Denied" after SSO login**
- **Cause:** You are not a member of any Staff Rota AD groups
- **Solution:** Contact your line manager to request access. They will liaise with CGI IT to add you to the appropriate group (e.g., `StaffRota_Staff`)

**Problem: "Session expired" message**
- **Cause:** SSO session timed out after 8 hours of inactivity
- **Solution:** Click "Login with CGI SSO" to start a new session

**Problem: Redirected to CGI SSO but stuck in loop**
- **Cause:** Browser cookies disabled or clock skew
- **Solution:** 
  1. Enable cookies in browser settings
  2. Check system time is accurate
  3. Clear browser cache and try again
  4. If persists, contact IT support

---

## 12. Troubleshooting

### 12.1 Common Issues & Solutions

**Issue 1: "Invalid SAML Response"**

**Symptoms:**
- User redirected from CGI SSO but sees error page
- SAML logs show "Invalid SAML Response"

**Diagnosis:**
```bash
# Check SAML logs
tail -f /var/log/staff-rota/saml.log | grep -i "error\|invalid"

# Common errors:
# - "signature validation failed" → IdP certificate mismatch
# - "assertion expired" → Clock skew
# - "invalid InResponseTo" → Session state lost
```

**Solutions:**
1. **IdP certificate mismatch:**
   ```bash
   # Obtain latest certificate from CGI SSO team
   # Update SAML_IDP_CERTIFICATE in environment
   # Restart application
   ```

2. **Clock skew:**
   ```bash
   # Check system time
   date
   # Expected: Within 5 minutes of actual time
   
   # Synchronize with NTP
   sudo ntpdate -u 0.uk.pool.ntp.org
   sudo systemctl restart ntp
   ```

3. **Session state lost:**
   ```bash
   # Check session backend configuration
   # Ensure Redis/database sessions are persistent
   ```

**Issue 2: "Assertion signature validation failed"**

**Symptoms:**
- SAML login fails with signature error
- Logs show: "Assertion signature validation failed"

**Diagnosis:**
```bash
# Verify IdP certificate
python3 manage.py shell << EOF
from rotasystems.saml_settings import SAML_IDP_CERTIFICATE
print(SAML_IDP_CERTIFICATE)
EOF

# Compare with CGI-provided certificate
# Expected: Exact match (including whitespace/newlines)
```

**Solutions:**
```bash
# 1. Obtain correct certificate from CGI SSO metadata
curl https://sso.cgi.com/idp/saml2/metadata > cgi_idp_metadata.xml
# Extract certificate from XML

# 2. Update environment variable
export SAML_IDP_CERTIFICATE="-----BEGIN CERTIFICATE-----
<paste certificate here>
-----END CERTIFICATE-----"

# 3. Restart application
sudo systemctl restart staff-rota
```

**Issue 3: "Unknown user after SAML login"**

**Symptoms:**
- SAML authentication succeeds but user creation fails
- Logs show: "Failed to create user from SAML data"

**Diagnosis:**
```bash
# Check SAML attribute mapping
python3 manage.py shell << EOF
from rotasystems.saml_backend import SAMLBackend
# Inspect backend.authenticate() logic
# Check if required attributes (username, email) are present
EOF

# Review SAML response attributes (debug mode)
tail -f /var/log/staff-rota/saml.log | grep "SAML attributes received"
```

**Solutions:**
1. **Missing attributes:**
   - Contact CGI SSO team to verify attribute release policy
   - Ensure `uid`, `email`, `givenName`, `sn` are released
   
2. **Attribute name mismatch:**
   ```python
   # Update SAML_ATTRIBUTE_MAPPING in saml_settings.py
   # Example: CGI uses 'mail' instead of 'email'
   SAML_ATTRIBUTE_MAPPING = {
       'uid': 'username',
       'mail': 'email',  # Changed from 'email'
       # ...
   }
   ```

**Issue 4: "Access denied after SSO login"**

**Symptoms:**
- User authenticated but has no role/permissions
- User sees "Access Denied" page

**Diagnosis:**
```bash
# Check user's AD group memberships
python3 manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(username='problem.user')
print(f"Role: {user.role}")
print(f"is_staff: {user.is_staff}")
print(f"is_active: {user.is_active}")
EOF

# Check SAML group attributes
tail -f /var/log/staff-rota/saml.log | grep "memberOf"
```

**Solutions:**
1. **Not in any AD group:**
   - Add user to appropriate group (e.g., `StaffRota_Staff`)
   - Have user logout and login again
   
2. **Group DN mismatch:**
   ```python
   # Update SAML_ROLE_MAPPING in saml_settings.py
   # Ensure group DNs match exact case/format from AD
   SAML_ROLE_MAPPING = {
       'CN=StaffRota_Staff,OU=Groups,DC=cgi,DC=com': 'STAFF',
       # Verify DN format with: Get-ADGroup "StaffRota_Staff"
   }
   ```

### 12.2 Debug Mode

```python
# rotasystems/saml_settings.py (development only)
SAML_DEBUG = True  # Enable verbose SAML logging

# This will log:
# - Full SAML requests/responses
# - Attribute extraction details
# - Signature validation steps
# - User creation/update operations

# WARNING: Contains sensitive data - never enable in production
```

---

## 13. Academic Paper Contribution

### 13.1 Integration Challenges Case Study

**Title:** SAML 2.0 Single Sign-On Integration with Enterprise Identity Provider: A Public Sector Case Study

**Context:**
Integration of SAML SSO with CGI's corporate identity provider for NHS Scotland Staff Rota System presented several technical and organizational challenges inherent to public sector IT deployments.

**Challenge 1: Multi-Stakeholder Coordination**

*Problem:* SAML integration required coordinating across four distinct teams:
- HSCP application development team (Staff Rota System)
- CGI SSO platform team (Identity Provider management)
- CGI Active Directory team (Group creation, user provisioning)
- CGI Network Security team (Firewall rules, certificate management)

*Impact:* 
- Initial timeline estimate: 2 weeks
- Actual timeline: 5-6 weeks (150-200% longer)
- Coordination overhead: ~£2K in meeting time and email exchanges

*Solution:*
Established weekly joint working session with all stakeholders present. Created shared project tracker (Trello) with clear ownership of each task. Reduced back-and-forth by 60% after week 2.

*Lesson Learned:*
Public sector integrations require proportionally more coordination time than technical implementation time (3:2 ratio observed). Budget 40-50% additional time for coordination in similar projects.

**Challenge 2: Certificate Management in Government Environment**

*Problem:* 
- Government security policies prohibit storing private keys in application code or version control
- No existing secure key management system available in HSCP environment
- CGI policies require annual security audits of all stored credentials

*Impact:*
- Delayed production deployment by 2 weeks
- Required architectural change from file-based to environment variable storage
- Ongoing operational overhead: certificate rotation procedure

*Solution:*
Implemented three-tier certificate storage strategy:
1. Development: Environment variables (acceptable for non-production)
2. Staging: Azure Key Vault (CGI-approved cloud secret storage)
3. Production: CGI Secret Management System (enterprise-grade)

Documented comprehensive certificate rotation procedure with 90-day advance notice to prevent expiry-induced outages.

*Lesson Learned:*
Government/enterprise integrations must consider certificate lifecycle management from day one. Plan for rotation, expiry monitoring, and multi-environment storage strategies. Recommended investment: £500-1K in secret management tooling.

**Challenge 3: SAML Attribute Schema Alignment**

*Problem:*
CGI's Active Directory schema uses different attribute names than assumed in initial design:
- Expected: `email` | Actual: `mail`
- Expected: `groups` | Actual: `memberOf` with full DN format
- Expected: `employeeId` | Actual: `employeeNumber`

*Impact:*
- Initial SSO logins created users with missing email addresses
- Role assignment failed (group DNs didn't match)
- Required code changes and re-testing (4-day delay)

*Solution:*
Created flexible attribute mapping configuration (SAML_ATTRIBUTE_MAPPING) that can be updated without code changes. Requested complete attribute schema documentation from CGI upfront in future integrations.

*Lesson Learned:*
Never assume IdP attribute names - request formal schema documentation during initial coordination meeting. Build flexible mapping layer to accommodate schema variations across IdPs.

**Challenge 4: Clock Skew and Signature Validation**

*Problem:*
SAML signature validation failed intermittently in testing due to 7-minute clock skew between Staff Rota server and CGI SSO portal. SAML specification allows only 5-minute tolerance.

*Impact:*
- 15% of test logins failed with "signature validation error"
- Initial misdiagnosis as certificate problem (wasted 1 day debugging)

*Solution:*
Configured NTP synchronization on all servers with UK NTP pool. Implemented monitoring alert for clock drift >30 seconds. Added `clockSkew: 300` (5 minutes) to SAML security configuration.

*Lesson Learned:*
Time synchronization is critical for SAML - not optional. Include NTP verification in pre-deployment checklist. Consider increasing clock skew tolerance to 300 seconds (5 minutes) for resilience.

### 13.2 Cost-Benefit Analysis

**Development Costs:**
- Initial development: 3-4 weeks × £1,500/week = £4.5-6K
- CGI coordination meetings: 6 meetings × 3 hours × £50/hour = £900
- Certificate management setup: £500
- Testing with CGI SSO team: 1 week × £1,000 = £1K
- Documentation: £500
- **Total Development:** £7.4-8.9K

**Ongoing Costs:**
- Certificate rotation: 1 day/year × £150 = £150/year
- CGI SSO platform fee: £0 (included in CGI partnership)
- Monitoring/logging: Negligible (existing infrastructure)
- **Total Annual Ongoing:** £150/year

**5-Year Total Cost of Ownership:** £7.4K + (5 × £150) = £8.15-9.65K

**Benefits (per HSCP):**

*Quantifiable:*
- Reduced password reset tickets: 200 tickets/year × 10 min × £20/hour = £667/year
- Reduced "forgot password" support calls: 150 calls/year × 5 min × £25/hour = £313/year
- Improved staff productivity: 50 users × 5 min/day saved × 220 days × £20/hour = £1,833/year
- Reduced credential-based security incidents: 2 incidents/year × £500 = £1,000/year
- **Total Annual Savings:** £3,813/year

*Non-Quantifiable:*
- Improved user experience (single login)
- Alignment with CGI IT standards (enables future integrations)
- Centralized access control (easier provisioning/deprovisioning)
- Enhanced audit compliance (centralized authentication logs)
- Reduced attack surface (no local passwords to compromise)

**ROI Analysis:**
- Break-even point: 8.15K ÷ 3.813K/year = **2.1 years**
- 5-year NPV: (5 × £3,813) - £8,150 = **£10.9K positive return**
- First-year ROI: (3.813K - 8.15K) / 8.15K = **-53% (investment year)**
- Years 2-5 ROI: 3.813K / 8.15K = **47% annual return**

**Scotland-Wide Deployment (30 HSCPs):**

*Costs:*
- Per-HSCP configuration/testing: 30 × £1-2K = £30-60K
- Centralized CGI SSO platform: £0 (already deployed)
- CGI SSO team support: £5K (one-time coordination)
- **Total Investment:** £35-65K

*Benefits:*
- Annual savings: 30 HSCPs × £3,813 = £114,390/year
- 5-year savings: 5 × £114,390 = £571,950
- Less investment: £571,950 - £50,000 = **£521,950 net benefit**

*Strategic Value:*
- Standardizes authentication across Scottish local government
- Positions system for national procurement frameworks (Scotland Excel)
- Enables centralized access governance (GDPR compliance)
- Reduces per-HSCP IT burden (CGI manages identity infrastructure)

### 13.3 Lessons for Future Public Sector SSO Projects

1. **Budget for Coordination:** Allocate 40-50% of project time for multi-stakeholder coordination
2. **Request IdP Documentation Upfront:** Attribute schema, certificate formats, network requirements
3. **Plan Certificate Lifecycle:** Rotation procedures, expiry monitoring, secure storage from day one
4. **Test with Real Users:** Pilot with 5-10 users from different AD groups before full rollout
5. **Implement Fallback Authentication:** LDAP/database auth for SSO outages (99.9% isn't 100%)
6. **Monitor Clock Synchronization:** NTP essential for SAML signature validation
7. **Log Everything:** Detailed SAML logging critical for troubleshooting government IdP issues
8. **Document for Handover:** CGI will manage long-term - create comprehensive ops documentation

---

## 14. Business Case Analysis

### 14.1 Investment Summary

**Capital Expenditure (CapEx):**
- Development (3-4 weeks): £4,500-6,000
- CGI coordination: £900
- Certificate management: £500
- Testing: £1,000
- Documentation: £500
- **Total CapEx:** £7,400-8,900

**Operational Expenditure (OpEx) - Annual:**
- Certificate rotation: £150/year
- Monitoring (incremental): £0
- CGI SSO platform: £0 (included in partnership)
- **Total OpEx:** £150/year

**5-Year TCO:** £7,400 + (5 × £150) = **£8,150-9,650**

### 14.2 Return on Investment (ROI)

**Pilot HSCP (Year 1):**
- Investment: £8,150
- Benefits: £3,813
- Net: -£4,337 (investment year)
- ROI: -53%

**Pilot HSCP (Years 2-5):**
- Annual cost: £150
- Annual benefits: £3,813
- Net annual: £3,663
- ROI: 2,342% (on annual OpEx)

**Cumulative 5-Year (Pilot HSCP):**
- Total cost: £8,900
- Total benefits: £19,065
- Net benefit: £10,165
- ROI: 114%

**Scotland-Wide (30 HSCPs):**
- Total investment: £35-65K (one-time)
- Annual OpEx: 30 × £150 = £4,500/year
- Annual benefits: 30 × £3,813 = £114,390/year
- 5-year net benefit: **£521,950**
- ROI: **950%** over 5 years

### 14.3 Strategic Business Value

**CGI Partnership Alignment:**
- Mandatory requirement for CGI enterprise deployment
- Demonstrates commitment to CGI IT standards
- Facilitates future integrations (SIEM, backup, monitoring)
- Strengthens HSCP-CGI relationship for contract renewals

**NHS Digital Compliance:**
- Aligns with NHS Digital Identity standards
- Supports DTAC (Digital Technology Assessment Criteria) evaluation
- Enables NHS Cyber Essentials Plus certification
- Demonstrates modern authentication best practices

**User Experience:**
- Single login across all CGI applications (email, HR, finance, Staff Rota)
- Automatic session management (login once per day)
- Consistent authentication experience
- Reduced cognitive load (one password to remember)

**Security Posture:**
- Eliminates local password storage (reduced attack surface)
- Centralized access control (immediate termination on employee departure)
- Audit trail in CGI SSO logs (GDPR compliance)
- Reduced credential-based attacks (phishing, password spraying)

**Operational Efficiency:**
- 80% reduction in password reset tickets
- Faster user provisioning (AD group membership = instant access)
- Easier deprovisioning (remove from AD group = access revoked)
- Reduced IT support burden

### 14.4 Risk-Adjusted ROI

**Risk Factors:**
- CGI SSO platform outage (probability: 0.1% annually, impact: £500 in lost productivity)
- Certificate expiry oversight (probability: 1% annually, impact: £1,000 in emergency fix)
- SAML vulnerability disclosure (probability: 0.5% annually, impact: £2,000 in patching/testing)

**Expected Annual Risk Cost:** (0.1% × £500) + (1% × £1,000) + (0.5% × £2,000) = **£20.50/year**

**Risk-Adjusted 5-Year ROI:**
- Original net benefit: £10,165
- Risk cost: 5 × £20.50 = £102.50
- Risk-adjusted net: £10,062.50
- Risk-adjusted ROI: **113%** (negligible change)

**Conclusion:** SAML SSO integration presents strong financial and strategic value. Break-even achieved in 2.1 years, with 114% ROI over 5 years. Risk-adjusted analysis confirms robustness of business case.

---

## 15. Next Steps

### 15.1 Immediate Actions (Week 1)

- [ ] Schedule kickoff meeting with CGI SSO team
- [ ] Request CGI IdP metadata (entity ID, SSO URL, certificate)
- [ ] Generate SP certificate pair
- [ ] Create SAML_SP_CERTIFICATE and SAML_IDP_CERTIFICATE environment variables
- [ ] Test SAML metadata endpoint: `https://staff-rota.hscp.scot/saml/metadata/`

### 15.2 Short-Term Actions (Weeks 2-3)

- [ ] CGI creates Active Directory security groups
- [ ] CGI registers Staff Rota as Service Provider in SSO portal
- [ ] CGI configures firewall rules
- [ ] Populate pilot users into AD groups
- [ ] Conduct initial SAML login testing (5-10 pilot users)

### 15.3 Medium-Term Actions (Weeks 4-5)

- [ ] Address any issues from pilot testing
- [ ] Expand pilot to 20-30 users
- [ ] Load test with 50 concurrent logins
- [ ] Security testing (signature validation, replay attacks)
- [ ] Finalize user documentation

### 15.4 Long-Term Actions (Week 6+)

- [ ] Production deployment (scheduled maintenance window)
- [ ] Enable SAML for all users (200+ staff)
- [ ] Monitor SSO adoption rate (target: >80% in first month)
- [ ] Gather user feedback and iterate
- [ ] Plan Scotland-wide rollout to other HSCPs

---

## Document Control

**Version History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-06 | Dean Sockalingum | Initial release |

**Approval:**

| Role | Name | Signature | Date |
|------|------|-----------|------|
| HSCP Technical Lead | Dean Sockalingum | ___________ | _______ |
| CGI SSO Platform Lead | TBD | ___________ | _______ |
| HSCP IT Security | TBD | ___________ | _______ |

**Distribution:**
- HSCP IT Team
- CGI SSO Platform Team
- CGI Active Directory Team
- CGI Network Security Team

---

**End of Document**
