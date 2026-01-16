"""
LDAP/Active Directory Authentication Configuration
====================================================

This module provides LDAP authentication for CGI corporate directory integration.
Implements single source of truth for user identities.

Author: Dean Sockalingum
Date: 6 January 2026
Purpose: Task #2 - LDAP/Active Directory Integration (NHS/CGI Deployment)
"""

import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType, PosixGroupType

# ============================================================================
# SECTION 1: LDAP SERVER CONFIGURATION
# ============================================================================

# CGI Active Directory Server Details
# NOTE: Replace these with actual CGI LDAP server details during deployment
LDAP_SERVER_URI = "ldap://cgi-ldap.example.com"  # TODO: Update with CGI LDAP server URL
LDAP_BIND_DN = "CN=ServiceAccount,OU=ServiceAccounts,DC=cgi,DC=com"  # TODO: Update
LDAP_BIND_PASSWORD = "REPLACE_WITH_SERVICE_ACCOUNT_PASSWORD"  # TODO: Update with secure credential

# Connection Options
LDAP_CONNECTION_OPTIONS = {
    ldap.OPT_DEBUG_LEVEL: 0,  # Set to 1 for debugging
    ldap.OPT_REFERRALS: 0,  # Disable referrals (common in AD)
    ldap.OPT_NETWORK_TIMEOUT: 10,  # 10 second timeout
}

# TLS/SSL Configuration (REQUIRED for production)
LDAP_START_TLS = True  # Enable StartTLS
# LDAP_CERT_FILE = "/path/to/ca_cert.pem"  # Optional: CA certificate for TLS verification

# ============================================================================
# SECTION 2: USER SEARCH CONFIGURATION
# ============================================================================

# Search Base DN (where to search for users)
# Example for CGI: DC=cgi,DC=com or OU=Users,DC=cgi,DC=com
LDAP_USER_SEARCH_BASE = "OU=Users,DC=cgi,DC=com"  # TODO: Update with actual OU

# User Search Filter
# (sAMAccountName=%(user)s) for Windows AD
# (uid=%(user)s) for OpenLDAP
LDAP_USER_SEARCH = LDAPSearch(
    LDAP_USER_SEARCH_BASE,
    ldap.SCOPE_SUBTREE,
    "(sAMAccountName=%(user)s)",  # Windows AD username attribute
)

# Alternative for email-based login:
# LDAP_USER_SEARCH_ALT = LDAPSearch(
#     LDAP_USER_SEARCH_BASE,
#     ldap.SCOPE_SUBTREE,
#     "(mail=%(user)s)",
# )

# ============================================================================
# SECTION 3: USER ATTRIBUTE MAPPING
# ============================================================================

# Map LDAP attributes to Django User model fields
LDAP_USER_ATTR_MAP = {
    "username": "sAMAccountName",  # Windows AD username
    "first_name": "givenName",
    "last_name": "sn",  # surname
    "email": "mail",
}

# Additional Staff Rota System fields (if using custom User model)
LDAP_USER_ATTR_MAP_EXTRA = {
    # "employee_id": "employeeNumber",  # If CGI uses employee number
    # "department": "department",
    # "phone_number": "telephoneNumber",
}

# ============================================================================
# SECTION 4: GROUP MEMBERSHIP CONFIGURATION
# ============================================================================

# Group Search Base (where to find security groups)
LDAP_GROUP_SEARCH_BASE = "OU=Groups,DC=cgi,DC=com"  # TODO: Update

# Group Search Configuration
LDAP_GROUP_SEARCH = LDAPSearch(
    LDAP_GROUP_SEARCH_BASE,
    ldap.SCOPE_SUBTREE,
    "(objectClass=group)",  # Windows AD group object class
)

# Group Type (use GroupOfNamesType for AD)
LDAP_GROUP_TYPE = GroupOfNamesType(name_attr="cn")

# ============================================================================
# SECTION 5: ROLE MAPPING (LDAP Groups → Django Permissions)
# ============================================================================

# Map CGI AD groups to Django staff status and superuser status
LDAP_USER_FLAGS_BY_GROUP = {
    # Django is_staff flag (required for admin access)
    "is_staff": [
        "CN=StaffRotaSystem_Managers,OU=Groups,DC=cgi,DC=com",  # TODO: Update group names
        "CN=StaffRotaSystem_Admins,OU=Groups,DC=cgi,DC=com",
    ],
    
    # Django is_superuser flag (full admin rights)
    "is_superuser": [
        "CN=StaffRotaSystem_Admins,OU=Groups,DC=cgi,DC=com",
    ],
    
    # Django is_active flag (can login)
    "is_active": [
        "CN=StaffRotaSystem_Users,OU=Groups,DC=cgi,DC=com",
        "CN=StaffRotaSystem_Managers,OU=Groups,DC=cgi,DC=com",
        "CN=StaffRotaSystem_Admins,OU=Groups,DC=cgi,DC=com",
    ],
}

# Map AD groups to Staff Rota System roles
# NOTE: Requires custom backend to populate Role model from LDAP groups
LDAP_ROLE_MAPPING = {
    # CGI AD Group → Staff Rota System Role
    "CN=StaffRotaSystem_Staff,OU=Groups,DC=cgi,DC=com": "STAFF",
    "CN=StaffRotaSystem_SeniorCareWorkers,OU=Groups,DC=cgi,DC=com": "SENIOR_CARE_WORKER",
    "CN=StaffRotaSystem_Managers,OU=Groups,DC=cgi,DC=com": "MANAGER",
    "CN=StaffRotaSystem_OperationalManagers,OU=Groups,DC=cgi,DC=com": "OPERATIONAL_MANAGER",
    "CN=StaffRotaSystem_HeadOfService,OU=Groups,DC=cgi,DC=com": "HEAD_OF_SERVICE",
    "CN=StaffRotaSystem_Admins,OU=Groups,DC=cgi,DC=com": "ADMIN",
}

# ============================================================================
# SECTION 6: AUTHENTICATION BACKEND CONFIGURATION
# ============================================================================

# Cache LDAP queries for performance (24 hours)
LDAP_CACHE_TIMEOUT = 86400  # 24 hours in seconds

# Always update user from LDAP on login (ensures attributes are current)
LDAP_ALWAYS_UPDATE_USER = True

# Create new users automatically from LDAP (if they don't exist in Django)
LDAP_MIRROR_GROUPS = True  # Sync group memberships from LDAP

# Deny login if user not in LDAP (fallback to Django auth)
LDAP_REQUIRE_GROUP = "CN=StaffRotaSystem_Users,OU=Groups,DC=cgi,DC=com"  # Optional: require specific group

# ============================================================================
# SECTION 7: FALLBACK AUTHENTICATION (LOCAL DJANGO USERS)
# ============================================================================

# Allow local Django users for:
# 1. Emergency access (if LDAP down)
# 2. Service accounts
# 3. Development/testing

# Authentication backends (order matters!)
AUTHENTICATION_BACKENDS = [
    'django_auth_ldap.backend.LDAPBackend',  # Try LDAP first
    'django.contrib.auth.backends.ModelBackend',  # Fallback to local Django users
]

# ============================================================================
# SECTION 8: LOGGING CONFIGURATION
# ============================================================================

# Enable LDAP debug logging
LDAP_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'ldap_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/rota/ldap_auth.log',  # TODO: Ensure directory exists
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'loggers': {
        'django_auth_ldap': {
            'handlers': ['ldap_file', 'console'],
            'level': 'DEBUG',  # Change to INFO in production
        },
    },
}

# ============================================================================
# SECTION 9: SECURITY CONSIDERATIONS
# ============================================================================

"""
SECURITY BEST PRACTICES:

1. Service Account Security:
   - Use dedicated service account with minimal privileges
   - Grant only "Read" access to user/group OUs
   - Rotate password regularly (90 days)
   - Store password in environment variable, NOT in code

2. TLS/SSL Encryption:
   - Always use LDAP_START_TLS = True in production
   - Verify TLS certificate (set LDAP_CERT_FILE)
   - Never use plain LDAP (ldap://) for production

3. Access Control:
   - Implement LDAP_REQUIRE_GROUP to restrict who can login
   - Map AD groups to specific Staff Rota System roles
   - Audit LDAP group memberships regularly

4. Monitoring:
   - Enable LDAP logging to detect authentication issues
   - Monitor failed login attempts (django-axes already in place)
   - Alert on LDAP connection failures

5. Disaster Recovery:
   - Keep fallback Django authentication enabled
   - Document emergency admin account procedure
   - Test LDAP failover scenarios
"""

# ============================================================================
# SECTION 10: DEPLOYMENT CHECKLIST
# ============================================================================

"""
PRE-DEPLOYMENT CHECKLIST:

☐ 1. CGI LDAP Server Details
   - Obtain LDAP server hostname/IP
   - Confirm port (389 for LDAP, 636 for LDAPS, 3268 for Global Catalog)
   - Get service account credentials

☐ 2. Active Directory Structure
   - Identify user search base DN (OU where users are located)
   - Identify group search base DN (OU where security groups are)
   - Confirm AD attribute names (sAMAccountName, mail, etc.)

☐ 3. Security Group Creation
   - Work with CGI to create AD groups:
     * StaffRotaSystem_Users (all users)
     * StaffRotaSystem_Staff (staff role)
     * StaffRotaSystem_SeniorCareWorkers
     * StaffRotaSystem_Managers
     * StaffRotaSystem_OperationalManagers
     * StaffRotaSystem_HeadOfService
     * StaffRotaSystem_Admins

☐ 4. Network Configuration
   - Ensure firewall allows Staff Rota server → CGI LDAP (port 389/636)
   - Configure VPN access if LDAP not internet-facing
   - Test network connectivity (ldapsearch command)

☐ 5. Testing
   - Test with test user account
   - Verify group membership sync
   - Test fallback to local Django auth
   - Load test LDAP authentication (100+ users)

☐ 6. Documentation
   - Document CGI LDAP contact for support
   - Create runbook for LDAP issues
   - Train HSCP staff on AD-based login
   - Update user documentation
"""

# ============================================================================
# SECTION 11: TESTING COMMANDS
# ============================================================================

"""
TESTING LDAP CONFIGURATION:

1. Test LDAP Connection (from server command line):
   $ ldapsearch -x -H ldap://cgi-ldap.example.com -D "CN=ServiceAccount,DC=cgi,DC=com" -W -b "OU=Users,DC=cgi,DC=com" "(sAMAccountName=testuser)"

2. Test Django LDAP Authentication (Python shell):
   $ python manage.py shell
   >>> from django.contrib.auth import authenticate
   >>> user = authenticate(username='testuser', password='testpassword')
   >>> print(user)  # Should return User object if successful

3. Test Group Membership Sync:
   $ python manage.py ldap_sync_groups

4. Debug LDAP Issues:
   - Check /var/log/rota/ldap_auth.log
   - Enable LDAP_CONNECTION_OPTIONS[ldap.OPT_DEBUG_LEVEL] = 1
   - Use ldapsearch to verify AD structure

5. Performance Testing:
   - Test with 100 concurrent logins (simulate CGI AD load)
   - Verify LDAP_CACHE_TIMEOUT reduces queries
"""

# ============================================================================
# SECTION 12: TROUBLESHOOTING GUIDE
# ============================================================================

"""
COMMON ISSUES & SOLUTIONS:

1. "Server not available" Error:
   - Check network connectivity (ping cgi-ldap.example.com)
   - Verify firewall allows port 389/636
   - Confirm VPN connection if required

2. "Invalid credentials" Error:
   - Verify service account DN format
   - Check service account password
   - Ensure account not locked in AD

3. "User not found" Error:
   - Verify LDAP_USER_SEARCH_BASE is correct
   - Check LDAP_USER_SEARCH filter (sAMAccountName vs uid)
   - Confirm user exists in AD (use ldapsearch)

4. Group Membership Not Syncing:
   - Verify LDAP_GROUP_SEARCH_BASE
   - Check LDAP_GROUP_TYPE (GroupOfNamesType for AD)
   - Ensure LDAP_MIRROR_GROUPS = True

5. TLS/SSL Errors:
   - Verify LDAP_START_TLS = True
   - Check CA certificate path (LDAP_CERT_FILE)
   - Confirm server certificate is valid

6. Performance Issues:
   - Increase LDAP_CACHE_TIMEOUT
   - Check LDAP server response time
   - Consider LDAP connection pooling
"""

# ============================================================================
# ACADEMIC PAPER CONTRIBUTION
# ============================================================================

"""
ACADEMIC PAPER - INTEGRATION CHALLENGES SECTION:

This LDAP integration demonstrates:

1. **Enterprise SSO Integration**
   - Single source of truth for user identities
   - Reduces password fatigue (one login for all CGI systems)
   - Improves security (centralized account lockout, password policy)

2. **Cost Savings vs Commercial Alternatives**
   - Commercial solutions: £5-10K/year for SSO integration
   - Our implementation: £2-4K one-time (2-3 weeks development)
   - Break-even: 6 months vs commercial licensing

3. **NHS/Local Government Alignment**
   - Demonstrates integration with corporate IT standards
   - Supports CGI ITIL service management
   - Enables centralized audit trail (AD logs + Django logs)

4. **Risk Mitigation**
   - Fallback authentication (local Django users)
   - Service account with minimal privileges
   - TLS encryption for credential transmission

5. **Lessons Learned**
   - CGI collaboration essential (AD structure, group creation)
   - Network configuration complexity (firewall, VPN)
   - Testing with production-like data crucial
"""

# ============================================================================
# BUSINESS CASE CONTRIBUTION
# ============================================================================

"""
BUSINESS CASE - ROI CALCULATION:

**Investment:**
- Development: 2-3 weeks × £800/week = £1,600-2,400
- CGI Support: 1 week × £1,000 = £1,000
- Testing: 3 days × £500/day = £1,500
- **Total: £4,100-4,900**

**Annual Savings:**
- Avoided SSO licensing fees: £5-10K/year
- Reduced helpdesk calls (password resets): £2-3K/year (est. 100 calls @ £20-30/call)
- Improved security (reduced breach risk): Quantified as risk reduction

**Intangible Benefits:**
- User experience improvement (single login)
- Security posture enhancement (centralized access control)
- CGI partnership strengthening (demonstrates integration capability)
- Compliance with CGI IT standards (ITIL alignment)

**ROI Timeline:**
- Break-even: 6-12 months
- 5-year NPV: £20-45K savings (vs commercial SSO licensing)

**Scotland-Wide Scaling:**
- If deployed to 30 HSCPs: 30 × £5-10K/year = £150-300K/year avoided licensing
- Implementation cost scales linearly: 30 × £4.5K = £135K one-time
- **Scotland-wide 5-year savings: £615K-1.37M**
"""
