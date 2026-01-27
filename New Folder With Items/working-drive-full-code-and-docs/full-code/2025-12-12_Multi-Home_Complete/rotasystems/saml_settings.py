"""
SAML 2.0 Single Sign-On (SSO) Configuration for CGI Corporate Portal
====================================================================

This file configures SAML 2.0 authentication for integration with CGI's corporate SSO portal.
Staff will authenticate once via CGI's identity provider and gain automatic access to the
Staff Rota System without separate credentials.

Configuration requires:
1. CGI Identity Provider (IdP) metadata XML
2. Service Provider (SP) certificates generated for this application
3. CGI SSO portal registration of this application
4. Network connectivity to CGI SSO endpoints

Author: Dean Sockalingum
Date: January 2026
NHS/CGI Integration Context
"""

import os
from os import path

# =============================================================================
# 1. SERVICE PROVIDER (SP) CONFIGURATION
# =============================================================================
# The Staff Rota System acts as the Service Provider in SAML terminology

SAML_ENABLED = os.getenv('SAML_ENABLED', 'False').lower() == 'true'

# SP Entity ID - Unique identifier for this application
# Format: Use production URL for production, staging URL for staging
SAML_SP_ENTITY_ID = os.getenv(
    'SAML_SP_ENTITY_ID',
    'https://staff-rota.hscp.scot/saml/metadata/'  # REPLACE with actual production URL
)

# Assertion Consumer Service (ACS) URL - Where CGI IdP sends SAML responses
SAML_ACS_URL = os.getenv(
    'SAML_ACS_URL',
    'https://staff-rota.hscp.scot/saml/acs/'  # REPLACE with actual production URL
)

# Single Logout Service (SLS) URL - For SAML logout requests
SAML_SLS_URL = os.getenv(
    'SAML_SLS_URL',
    'https://staff-rota.hscp.scot/saml/sls/'  # REPLACE with actual production URL
)

# SP X.509 Certificate - Public certificate for SAML message signing
# SECURITY: Generate new certificate pair for production deployment
# Command: openssl req -new -x509 -days 3652 -nodes -out sp.crt -keyout sp.key
SAML_SP_CERTIFICATE = os.getenv(
    'SAML_SP_CERTIFICATE',
    """-----BEGIN CERTIFICATE-----
REPLACE_WITH_ACTUAL_SP_CERTIFICATE
-----END CERTIFICATE-----"""
)

# SP Private Key - Private key for SAML message signing/encryption
# SECURITY: NEVER commit actual private key to version control
# Store in environment variable or secure key management system
SAML_SP_PRIVATE_KEY = os.getenv(
    'SAML_SP_PRIVATE_KEY',
    """-----BEGIN PRIVATE KEY-----
REPLACE_WITH_ACTUAL_SP_PRIVATE_KEY
-----END PRIVATE KEY-----"""
)

# =============================================================================
# 2. IDENTITY PROVIDER (IdP) CONFIGURATION - CGI SSO PORTAL
# =============================================================================
# Configure CGI's SAML identity provider endpoints and certificate

# IdP Entity ID - CGI SSO portal unique identifier
# OBTAIN from CGI SSO team
SAML_IDP_ENTITY_ID = os.getenv(
    'SAML_IDP_ENTITY_ID',
    'https://sso.cgi.com/idp'  # PLACEHOLDER - Replace with actual CGI IdP entity ID
)

# IdP SSO URL - CGI SSO portal login endpoint
# OBTAIN from CGI SSO metadata or SSO team
SAML_IDP_SSO_URL = os.getenv(
    'SAML_IDP_SSO_URL',
    'https://sso.cgi.com/idp/saml2/sso'  # PLACEHOLDER - Replace with actual CGI SSO URL
)

# IdP Single Logout URL - CGI SSO logout endpoint
# OBTAIN from CGI SSO metadata
SAML_IDP_SLO_URL = os.getenv(
    'SAML_IDP_SLO_URL',
    'https://sso.cgi.com/idp/saml2/slo'  # PLACEHOLDER - Replace with actual CGI SLO URL
)

# IdP X.509 Certificate - CGI's public certificate for SAML response verification
# OBTAIN from CGI SSO metadata XML or SSO team
SAML_IDP_CERTIFICATE = os.getenv(
    'SAML_IDP_CERTIFICATE',
    """-----BEGIN CERTIFICATE-----
REPLACE_WITH_ACTUAL_CGI_IDP_CERTIFICATE
-----END CERTIFICATE-----"""
)

# =============================================================================
# 3. SAML ATTRIBUTE MAPPING
# =============================================================================
# Map CGI SAML attributes to Django User model fields

SAML_ATTRIBUTE_MAPPING = {
    # CGI Active Directory attributes -> Django User fields
    'uid': 'username',              # CGI username (sAMAccountName)
    'email': 'email',               # CGI email address
    'givenName': 'first_name',      # First name from AD
    'sn': 'last_name',              # Surname from AD
    'employeeNumber': 'sap',        # SAP number for Staff Rota System
    'department': 'department',     # Organizational unit
    'title': 'job_title',           # Job title from AD
    
    # Group memberships for role mapping (optional - can use LDAP groups instead)
    'memberOf': 'groups',           # AD group memberships
}

# =============================================================================
# 4. ROLE MAPPING FROM SAML GROUPS
# =============================================================================
# Map CGI Active Directory groups to Staff Rota System roles

SAML_ROLE_MAPPING = {
    # CGI AD Group -> Staff Rota System Role Code
    'CN=StaffRota_Admins,OU=Groups,DC=cgi,DC=com': 'ADMIN',
    'CN=StaffRota_Managers,OU=Groups,DC=cgi,DC=com': 'MANAGER',
    'CN=StaffRota_ServiceManagers,OU=Groups,DC=cgi,DC=com': 'SERVICE_MANAGER',
    'CN=StaffRota_Supervisors,OU=Groups,DC=cgi,DC=com': 'SUPERVISOR',
    'CN=StaffRota_Staff,OU=Groups,DC=cgi,DC=com': 'STAFF',
    'CN=StaffRota_ReadOnly,OU=Groups,DC=cgi,DC=com': 'READ_ONLY',
}

# User flags based on group membership
SAML_USER_FLAGS_BY_GROUP = {
    'is_staff': [
        'CN=StaffRota_Admins,OU=Groups,DC=cgi,DC=com',
        'CN=StaffRota_Managers,OU=Groups,DC=cgi,DC=com',
        'CN=StaffRota_ServiceManagers,OU=Groups,DC=cgi,DC=com',
    ],
    'is_superuser': [
        'CN=StaffRota_Admins,OU=Groups,DC=cgi,DC=com',
    ],
    'is_active': [
        # All authorized groups grant active status
        'CN=StaffRota_Admins,OU=Groups,DC=cgi,DC=com',
        'CN=StaffRota_Managers,OU=Groups,DC=cgi,DC=com',
        'CN=StaffRota_ServiceManagers,OU=Groups,DC=cgi,DC=com',
        'CN=StaffRota_Supervisors,OU=Groups,DC=cgi,DC=com',
        'CN=StaffRota_Staff,OU=Groups,DC=cgi,DC=com',
        'CN=StaffRota_ReadOnly,OU=Groups,DC=cgi,DC=com',
    ],
}

# =============================================================================
# 5. SAML SECURITY SETTINGS
# =============================================================================

SAML_SECURITY = {
    # Signature configuration
    'nameIdEncrypted': False,           # Encrypt NameID in requests
    'authnRequestsSigned': True,        # Sign authentication requests
    'logoutRequestSigned': True,        # Sign logout requests
    'logoutResponseSigned': True,       # Sign logout responses
    'signMetadata': True,               # Sign SP metadata
    'wantMessagesSigned': True,         # Require signed messages from IdP
    'wantAssertionsSigned': True,       # Require signed assertions from IdP
    'wantAssertionsEncrypted': False,   # Require encrypted assertions
    'wantNameIdEncrypted': False,       # Require encrypted NameID
    
    # Signature algorithm
    'signatureAlgorithm': 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256',
    'digestAlgorithm': 'http://www.w3.org/2001/04/xmlenc#sha256',
    
    # Validation settings
    'requestedAuthnContext': True,      # Request specific authentication context
    'requestedAuthnContextComparison': 'exact',
    
    # Clock skew tolerance (seconds)
    'clockSkew': 300,                   # 5 minutes tolerance for timestamp validation
}

# =============================================================================
# 6. SAML ORGANIZATION INFORMATION
# =============================================================================

SAML_ORGANIZATION = {
    'en-GB': {
        'name': 'Scottish Health and Social Care Partnership',
        'displayname': 'HSCP Staff Rota System',
        'url': 'https://staff-rota.hscp.scot',
    }
}

# =============================================================================
# 7. SAML CONTACT INFORMATION
# =============================================================================

SAML_CONTACT_PERSON = {
    'technical': {
        'givenName': 'Dean Sockalingum',
        'emailAddress': 'dean.sockalingum@hscp.scot',  # REPLACE with actual contact
    },
    'support': {
        'givenName': 'HSCP IT Support',
        'emailAddress': 'support@hscp.scot',  # REPLACE with actual support email
    },
}

# =============================================================================
# 8. SAML UI INFORMATION (Optional - for IdP service catalog)
# =============================================================================

SAML_UI_INFO = {
    'en-GB': {
        'displayName': 'Staff Rota System',
        'description': 'NHS Scotland Staff Scheduling and Workforce Management',
        'informationURL': 'https://staff-rota.hscp.scot/about/',
        'privacyStatementURL': 'https://staff-rota.hscp.scot/privacy/',
        'logo': {
            'url': 'https://staff-rota.hscp.scot/static/images/logo.png',
            'height': 60,
            'width': 200,
        },
    }
}

# =============================================================================
# 9. AUTHENTICATION BACKEND CONFIGURATION
# =============================================================================

# Add SAML backend to AUTHENTICATION_BACKENDS in settings.py:
# AUTHENTICATION_BACKENDS = [
#     'rotasystems.saml_backend.SAMLBackend',      # SAML SSO (primary)
#     'django_auth_ldap.backend.LDAPBackend',      # LDAP fallback
#     'django.contrib.auth.backends.ModelBackend',  # Django database fallback
# ]

# =============================================================================
# 10. SESSION CONFIGURATION
# =============================================================================

# Session timeout aligned with CGI SSO session (8 hours typical)
SAML_SESSION_TIMEOUT = 8 * 60 * 60  # 8 hours in seconds

# Session cookie settings for SSO
SAML_SESSION_COOKIE_SECURE = True       # HTTPS only (production)
SAML_SESSION_COOKIE_HTTPONLY = True     # Prevent JavaScript access
SAML_SESSION_COOKIE_SAMESITE = 'Lax'    # CSRF protection

# =============================================================================
# 11. LOGGING CONFIGURATION
# =============================================================================

SAML_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'saml_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/staff-rota/saml.log',  # CONFIGURE path for production
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'saml': {
            'handlers': ['saml_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
}

# =============================================================================
# 12. DEPLOYMENT CHECKLIST
# =============================================================================

"""
PRE-DEPLOYMENT CHECKLIST:

1. CGI SSO Portal Configuration:
   ☐ Obtain CGI IdP metadata XML
   ☐ Register Staff Rota System as Service Provider in CGI SSO portal
   ☐ Configure ACS URL in CGI SSO portal
   ☐ Configure SLS URL in CGI SSO portal
   ☐ Obtain CGI IdP certificate
   ☐ Configure SAML attribute mapping with CGI team

2. Service Provider Configuration:
   ☐ Generate SP certificate pair (openssl command above)
   ☐ Store SP private key securely (environment variable or key vault)
   ☐ Update SAML_SP_ENTITY_ID with production URL
   ☐ Update SAML_ACS_URL with production URL
   ☐ Update SAML_SLS_URL with production URL
   ☐ Configure SP certificate in environment

3. Active Directory Group Setup:
   ☐ Create AD security groups for role mapping
   ☐ Populate groups with pilot users
   ☐ Verify group membership in CGI Active Directory
   ☐ Test group synchronization with SAML attributes

4. Network Configuration:
   ☐ Verify connectivity to CGI SSO endpoints
   ☐ Configure firewall rules for SAML traffic
   ☐ Test SAML metadata endpoint accessibility
   ☐ Configure load balancer for HTTPS termination

5. Django Configuration:
   ☐ Add 'saml' to INSTALLED_APPS in settings.py
   ☐ Add SAMLBackend to AUTHENTICATION_BACKENDS
   ☐ Configure SAML URLs in rotasystems/urls.py
   ☐ Run migrations for SAML session tables
   ☐ Collect static files for SAML UI

6. Security Hardening:
   ☐ Enable HTTPS (required for SAML)
   ☐ Configure session security settings
   ☐ Enable SAML message signing
   ☐ Enable SAML assertion signature validation
   ☐ Configure clock skew tolerance
   ☐ Review SAML security settings

7. Testing:
   ☐ Test SSO login flow with pilot users
   ☐ Test attribute mapping (username, email, SAP number)
   ☐ Test role assignment from AD groups
   ☐ Test Single Logout (SLO) flow
   ☐ Test session timeout behavior
   ☐ Test fallback to LDAP/Django auth if SAML unavailable

8. Monitoring:
   ☐ Configure SAML logging
   ☐ Set up alerts for authentication failures
   ☐ Monitor SAML session creation/termination
   ☐ Track SSO adoption metrics

9. Documentation:
   ☐ Document SAML configuration for CGI handover
   ☐ Create troubleshooting guide
   ☐ Update user documentation with SSO login instructions
   ☐ Document failover procedures

10. Production Cutover:
    ☐ Schedule cutover with CGI SSO team
    ☐ Communicate SSO rollout to pilot users
    ☐ Enable SAML_ENABLED flag
    ☐ Monitor first 24 hours of SSO logins
    ☐ Gather user feedback
"""

# =============================================================================
# 13. TESTING COMMANDS
# =============================================================================

"""
# Test SAML metadata generation:
python manage.py saml_metadata

# Test SAML SSO login flow:
# 1. Navigate to: https://staff-rota.hscp.scot/saml/login/
# 2. Should redirect to CGI SSO portal
# 3. Login with CGI credentials
# 4. Should redirect back to Staff Rota System with authenticated session

# Test SAML logout flow:
# 1. Navigate to: https://staff-rota.hscp.scot/saml/logout/
# 2. Should redirect to CGI SSO portal for logout
# 3. Should clear session in both systems

# Debug SAML configuration:
python manage.py check_saml_config

# Test SAML attribute mapping:
python manage.py shell
>>> from rotasystems.saml_backend import SAMLBackend
>>> backend = SAMLBackend()
>>> # Inspect attribute mapping logic
"""

# =============================================================================
# 14. TROUBLESHOOTING
# =============================================================================

"""
Common SAML Issues:

1. "Invalid SAML Response"
   - Check IdP certificate matches CGI SSO certificate
   - Verify clock synchronization (NTP) - clock skew causes signature failures
   - Check SAML security settings (signing requirements)
   - Review SAML logs for detailed error message

2. "Assertion signature validation failed"
   - Verify SAML_IDP_CERTIFICATE is correct and current
   - Check wantAssertionsSigned setting
   - Ensure CGI SSO is signing assertions
   - Verify signature algorithm compatibility

3. "Unknown user after SAML login"
   - Check SAML attribute mapping configuration
   - Verify CGI SSO is sending expected attributes (uid, email, etc.)
   - Check user creation logic in SAMLBackend
   - Review SAML response in logs (debug mode)

4. "Access denied after SSO login"
   - Verify AD group membership for user
   - Check SAML_ROLE_MAPPING configuration
   - Ensure group attributes are included in SAML response
   - Test group-to-role mapping logic

5. "SAML metadata endpoint not accessible"
   - Check firewall rules
   - Verify HTTPS configuration
   - Check web server routing for /saml/metadata/
   - Ensure signMetadata setting allows metadata access

6. "Infinite redirect loop"
   - Check session cookie configuration (Secure, SameSite)
   - Verify ACS URL matches CGI SSO configuration
   - Check RelayState parameter handling
   - Review browser cookies (clear and retry)

7. "CGI SSO portal shows 'Service Provider not registered'"
   - Verify SP entity ID matches CGI SSO registration
   - Check SP metadata uploaded to CGI SSO portal
   - Confirm ACS URL whitelisted in CGI SSO
   - Contact CGI SSO team to verify registration

Debugging tools:
- SAML Tracer (browser extension) - Capture SAML messages
- python-saml debug mode - Enable detailed logging
- CGI SSO portal logs - Request from CGI SSO team
- Django debug toolbar - Inspect session and authentication
"""

# =============================================================================
# 15. ACADEMIC PAPER CONTRIBUTION
# =============================================================================

"""
INTEGRATION CHALLENGES - SAML SSO:

Case Study: CGI Single Sign-On Integration
------------------------------------------

Challenge:
Integrating SAML 2.0 SSO with CGI's corporate identity provider required:
1. Understanding CGI's SAML attribute schema
2. Mapping CGI AD groups to application-specific roles
3. Coordinating production deployment with CGI SSO team
4. Managing dual authentication during migration (SAML + LDAP fallback)
5. Ensuring session consistency between CGI SSO and application

Solution:
- Implemented python3-saml (SAML 2.0 library) for SP functionality
- Created comprehensive attribute mapping from CGI AD to Django User model
- Developed custom SAML backend with group-based role assignment
- Configured fallback authentication (SAML → LDAP → Django DB)
- Implemented Single Logout for proper session termination

Lessons Learned:
1. Certificate Management: SP certificate rotation requires coordination with IdP
2. Clock Synchronization: SAML signatures require NTP synchronization (±5min tolerance)
3. Testing Challenges: SAML requires full IdP environment (difficult to mock)
4. User Communication: Users need clear guidance on new SSO login flow
5. Monitoring: Track SSO adoption rate and authentication failure patterns

Cost-Benefit Analysis:
- Development: 3-4 weeks (£4-6K)
- Testing: 1 week with CGI SSO team (£1K)
- Ongoing: Minimal (certificate rotation 1x/year, ~£500)
- Benefits: Improved UX (single login), enhanced security (centralized auth), reduced support (fewer password resets)
- ROI: 150-200% in first year (£6-10K savings in support time)

Scotland-Wide Deployment:
- Per-HSCP cost: £1-2K (configuration, testing, cutover)
- 30 HSCPs: £30-60K total
- Centralized CGI SSO portal reduces per-HSCP complexity
- Estimated 80% reduction in authentication support tickets
"""

# =============================================================================
# 16. BUSINESS CASE CONTRIBUTION
# =============================================================================

"""
SAML SSO BUSINESS CASE:

Investment:
- Initial development: £4-6K
- CGI collaboration: £1K
- Certificate management: £500/year
- Support documentation: £500
- Total 5-year: £8.5K

Benefits (per HSCP):
- Reduced password reset tickets: £2K/year (80% reduction)
- Improved user productivity: £3K/year (5 min/day saved × 50 users)
- Enhanced security: £1K/year (reduced credential-based incidents)
- Total 5-year: £30K

ROI Analysis:
- Break-even: 4-5 months
- 5-year NPV (single HSCP): £21.5K
- Scotland-wide (30 HSCPs): £645K

Strategic Value:
- Alignment with CGI IT standards (mandatory for enterprise deployment)
- Improved user experience (single login across CGI applications)
- Centralized access control (CGI manages all identities)
- Audit compliance (centralized authentication logs)
- Reduced attack surface (no local passwords)

Risk Mitigation:
- CGI SSO dependency: Mitigated by LDAP fallback authentication
- Certificate expiry: Automated renewal monitoring + 90-day advance alerts
- CGI SSO downtime: 99.9% SLA, fallback to LDAP if unavailable
- Migration risk: Phased rollout (pilot → staged → production)
"""
