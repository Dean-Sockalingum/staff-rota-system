"""
Custom SAML Authentication Backend for CGI SSO Integration
===========================================================

This backend handles SAML 2.0 authentication with CGI's corporate SSO portal.
It processes SAML assertions, maps attributes to Django User model, and assigns
roles based on Active Directory group memberships.

Author: Dean Sockalingum
Date: January 2026
NHS/CGI Integration Context
"""

import logging
from typing import Optional, Dict, List, Any

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.conf import settings

from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils

logger = logging.getLogger('saml')

User = get_user_model()


class SAMLBackend(BaseBackend):
    """
    Custom SAML 2.0 authentication backend for CGI SSO integration.
    
    This backend:
    1. Validates SAML assertions from CGI IdP
    2. Extracts user attributes from SAML response
    3. Creates or updates Django User from SAML attributes
    4. Maps AD groups to Staff Rota System roles
    5. Assigns appropriate permissions based on group membership
    """
    
    def authenticate(self, request, saml_authentication=None):
        """
        Authenticate user via SAML assertion.
        
        Args:
            request: Django HttpRequest object
            saml_authentication: OneLogin_Saml2_Auth instance with validated assertion
            
        Returns:
            User instance if authentication successful, None otherwise
        """
        if not saml_authentication:
            logger.debug("No SAML authentication object provided")
            return None
            
        if not saml_authentication.is_authenticated():
            logger.warning("SAML authentication failed - user not authenticated")
            return None
            
        # Extract attributes from SAML assertion
        attributes = saml_authentication.get_attributes()
        nameid = saml_authentication.get_nameid()
        
        logger.info(f"SAML authentication successful for NameID: {nameid}")
        logger.debug(f"SAML attributes received: {list(attributes.keys())}")
        
        # Map SAML attributes to user fields
        user_data = self._map_saml_attributes(attributes, nameid)
        
        if not user_data:
            logger.error("Failed to map SAML attributes to user data")
            return None
            
        # Get or create user
        user = self._get_or_create_user(user_data)
        
        if not user:
            logger.error(f"Failed to get or create user for: {user_data.get('username')}")
            return None
            
        # Update user attributes from SAML
        self._update_user_attributes(user, user_data)
        
        # Map AD groups to roles
        groups = attributes.get('memberOf', [])
        self._assign_roles_from_groups(user, groups)
        
        # Set user flags based on group membership
        self._set_user_flags_from_groups(user, groups)
        
        user.save()
        
        logger.info(f"User authenticated via SAML: {user.username} (SAP: {user.sap})")
        return user
    
    def _map_saml_attributes(self, attributes: Dict[str, List[str]], nameid: str) -> Optional[Dict[str, Any]]:
        """
        Map SAML attributes to Django User model fields.
        
        Args:
            attributes: SAML attributes dictionary from IdP
            nameid: SAML NameID (typically username)
            
        Returns:
            Dictionary of user field values, or None if mapping fails
        """
        from rotasystems.saml_settings import SAML_ATTRIBUTE_MAPPING
        
        user_data = {}
        
        # Map NameID to username if not in attributes
        user_data['username'] = nameid
        
        # Map each SAML attribute to User model field
        for saml_attr, user_field in SAML_ATTRIBUTE_MAPPING.items():
            if saml_attr in attributes:
                # SAML attributes are always lists - take first value
                value = attributes[saml_attr][0] if attributes[saml_attr] else None
                
                if value:
                    user_data[user_field] = value
                    logger.debug(f"Mapped {saml_attr} -> {user_field}: {value}")
        
        # Validate required fields
        required_fields = ['username', 'email']
        missing_fields = [field for field in required_fields if field not in user_data]
        
        if missing_fields:
            logger.error(f"Missing required SAML attributes: {missing_fields}")
            return None
            
        return user_data
    
    def _get_or_create_user(self, user_data: Dict[str, Any]) -> Optional[User]:
        """
        Get existing user or create new user from SAML data.
        
        Args:
            user_data: Dictionary of user field values
            
        Returns:
            User instance or None if creation fails
        """
        username = user_data.get('username')
        email = user_data.get('email')
        sap = user_data.get('sap')
        
        # Try to find user by username
        try:
            user = User.objects.get(username=username)
            logger.debug(f"Found existing user: {username}")
            return user
        except User.DoesNotExist:
            pass
        
        # Try to find user by SAP number (if provided)
        if sap:
            try:
                user = User.objects.get(sap=sap)
                logger.info(f"Found existing user by SAP: {sap} (updating username to {username})")
                user.username = username  # Update username to match SAML
                return user
            except User.DoesNotExist:
                pass
        
        # Try to find user by email
        try:
            user = User.objects.get(email=email)
            logger.info(f"Found existing user by email: {email} (updating username to {username})")
            user.username = username  # Update username to match SAML
            return user
        except User.DoesNotExist:
            pass
        
        # Create new user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
            )
            logger.info(f"Created new user from SAML: {username}")
            return user
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return None
    
    def _update_user_attributes(self, user: User, user_data: Dict[str, Any]) -> None:
        """
        Update user attributes from SAML data.
        
        Args:
            user: User instance to update
            user_data: Dictionary of user field values
        """
        # Update standard User model fields
        user.email = user_data.get('email', user.email)
        user.first_name = user_data.get('first_name', user.first_name)
        user.last_name = user_data.get('last_name', user.last_name)
        
        # Update Staff Rota System specific fields
        if 'sap' in user_data:
            user.sap = user_data['sap']
        
        if 'department' in user_data:
            user.department = user_data['department']
        
        if 'job_title' in user_data:
            user.job_title = user_data['job_title']
        
        logger.debug(f"Updated user attributes: {user.username}")
    
    def _assign_roles_from_groups(self, user: User, groups: List[str]) -> None:
        """
        Assign Staff Rota System role based on AD group membership.
        
        Args:
            user: User instance
            groups: List of AD group DNs from SAML
        """
        from rotasystems.saml_settings import SAML_ROLE_MAPPING
        from scheduling.models import Role
        
        # Find highest priority role from group memberships
        assigned_role = None
        role_priority = {
            'ADMIN': 1,
            'SERVICE_MANAGER': 2,
            'MANAGER': 3,
            'SUPERVISOR': 4,
            'STAFF': 5,
            'READ_ONLY': 6,
        }
        
        highest_priority = 999
        
        for group_dn in groups:
            if group_dn in SAML_ROLE_MAPPING:
                role_code = SAML_ROLE_MAPPING[group_dn]
                priority = role_priority.get(role_code, 999)
                
                if priority < highest_priority:
                    highest_priority = priority
                    assigned_role = role_code
                    logger.debug(f"Found role mapping: {group_dn} -> {role_code}")
        
        if assigned_role:
            try:
                role = Role.objects.get(code=assigned_role)
                user.role = role
                logger.info(f"Assigned role to user {user.username}: {assigned_role}")
            except Role.DoesNotExist:
                logger.error(f"Role not found: {assigned_role}")
        else:
            logger.warning(f"No role mapping found for user {user.username} groups: {groups}")
    
    def _set_user_flags_from_groups(self, user: User, groups: List[str]) -> None:
        """
        Set Django user flags (is_staff, is_superuser, is_active) based on AD groups.
        
        Args:
            user: User instance
            groups: List of AD group DNs from SAML
        """
        from rotasystems.saml_settings import SAML_USER_FLAGS_BY_GROUP
        
        # Check is_staff
        is_staff_groups = SAML_USER_FLAGS_BY_GROUP.get('is_staff', [])
        user.is_staff = any(group in is_staff_groups for group in groups)
        
        # Check is_superuser
        is_superuser_groups = SAML_USER_FLAGS_BY_GROUP.get('is_superuser', [])
        user.is_superuser = any(group in is_superuser_groups for group in groups)
        
        # Check is_active
        is_active_groups = SAML_USER_FLAGS_BY_GROUP.get('is_active', [])
        user.is_active = any(group in is_active_groups for group in groups)
        
        logger.debug(f"Set user flags: is_staff={user.is_staff}, is_superuser={user.is_superuser}, is_active={user.is_active}")
    
    def get_user(self, user_id):
        """
        Get user by ID for session authentication.
        
        Args:
            user_id: User primary key
            
        Returns:
            User instance or None
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


def prepare_django_request(request):
    """
    Prepare Django request for python3-saml library.
    
    The python3-saml library expects a specific request format.
    This function converts Django's HttpRequest to the expected format.
    
    Args:
        request: Django HttpRequest object
        
    Returns:
        Dictionary in python3-saml expected format
    """
    # Get server protocol (http or https)
    if request.is_secure():
        protocol = 'https'
    else:
        protocol = 'http'
    
    # Build request data
    result = {
        'https': 'on' if request.is_secure() else 'off',
        'http_host': request.META['HTTP_HOST'],
        'script_name': request.META.get('PATH_INFO', ''),
        'server_port': request.META['SERVER_PORT'],
        'get_data': request.GET.copy(),
        'post_data': request.POST.copy(),
    }
    
    return result


def get_saml_auth(request):
    """
    Initialize SAML authentication object with CGI IdP configuration.
    
    Args:
        request: Django HttpRequest object
        
    Returns:
        OneLogin_Saml2_Auth instance configured for CGI SSO
    """
    from rotasystems.saml_settings import (
        SAML_SP_ENTITY_ID, SAML_ACS_URL, SAML_SLS_URL,
        SAML_SP_CERTIFICATE, SAML_SP_PRIVATE_KEY,
        SAML_IDP_ENTITY_ID, SAML_IDP_SSO_URL, SAML_IDP_SLO_URL,
        SAML_IDP_CERTIFICATE, SAML_SECURITY, SAML_ORGANIZATION,
        SAML_CONTACT_PERSON
    )
    
    # Build SAML configuration
    saml_settings = {
        'strict': True,
        'debug': settings.DEBUG,
        'sp': {
            'entityId': SAML_SP_ENTITY_ID,
            'assertionConsumerService': {
                'url': SAML_ACS_URL,
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST'
            },
            'singleLogoutService': {
                'url': SAML_SLS_URL,
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
            },
            'NameIDFormat': 'urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified',
            'x509cert': SAML_SP_CERTIFICATE,
            'privateKey': SAML_SP_PRIVATE_KEY,
        },
        'idp': {
            'entityId': SAML_IDP_ENTITY_ID,
            'singleSignOnService': {
                'url': SAML_IDP_SSO_URL,
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
            },
            'singleLogoutService': {
                'url': SAML_IDP_SLO_URL,
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
            },
            'x509cert': SAML_IDP_CERTIFICATE,
        },
        'security': SAML_SECURITY,
        'organization': SAML_ORGANIZATION,
        'contactPerson': SAML_CONTACT_PERSON,
    }
    
    # Prepare request for python3-saml
    req = prepare_django_request(request)
    
    # Create SAML auth object
    auth = OneLogin_Saml2_Auth(req, saml_settings)
    
    return auth
