"""
SAML 2.0 Single Sign-On (SSO) Views for CGI Integration
========================================================

This module provides Django views for SAML authentication flows:
- SSO Login: Initiate SAML login with CGI IdP
- Assertion Consumer Service (ACS): Process SAML responses from CGI
- Single Logout (SLO): Logout from both application and CGI SSO
- Metadata: Provide SP metadata for CGI SSO portal registration

Author: Dean Sockalingum
Date: January 2026
NHS/CGI Integration Context
"""

import logging
from typing import Optional

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect, render
from django.urls import reverse
from django.conf import settings

from rotasystems.saml_backend import get_saml_auth, SAMLBackend

logger = logging.getLogger('saml')


@require_http_methods(["GET"])
def saml_login(request):
    """
    Initiate SAML SSO login with CGI Identity Provider.
    
    This view redirects the user to CGI's SSO portal for authentication.
    After successful login, CGI will POST the SAML response to our ACS endpoint.
    
    URL: /saml/login/
    Method: GET
    """
    try:
        # Initialize SAML auth
        auth = get_saml_auth(request)
        
        # Get return URL from query parameter or default to home
        return_to = request.GET.get('next', '/')
        
        # Store return URL in session for retrieval after authentication
        request.session['saml_return_to'] = return_to
        
        logger.info(f"Initiating SAML login, will return to: {return_to}")
        
        # Generate SAML AuthnRequest and redirect to CGI IdP
        return HttpResponseRedirect(auth.login(return_to=return_to))
        
    except Exception as e:
        logger.error(f"SAML login initiation failed: {e}", exc_info=True)
        return HttpResponseServerError("Failed to initiate SAML login. Please contact support.")


@csrf_exempt  # SAML POST comes from external IdP, can't include CSRF token
@require_http_methods(["POST"])
def saml_acs(request):
    """
    Assertion Consumer Service (ACS) - Process SAML response from CGI IdP.
    
    This view receives the SAML assertion from CGI after successful authentication,
    validates it, extracts user attributes, and creates/updates the Django user.
    
    URL: /saml/acs/
    Method: POST (from CGI IdP)
    """
    try:
        # Initialize SAML auth
        auth = get_saml_auth(request)
        
        # Process SAML response
        auth.process_response()
        
        # Get errors from SAML processing
        errors = auth.get_errors()
        
        if errors:
            error_reason = auth.get_last_error_reason()
            logger.error(f"SAML ACS errors: {errors}, reason: {error_reason}")
            return render(request, 'saml/error.html', {
                'errors': errors,
                'error_reason': error_reason,
            }, status=400)
        
        # Check if user is authenticated
        if not auth.is_authenticated():
            logger.warning("SAML ACS: User not authenticated after processing response")
            return HttpResponse("Authentication failed", status=401)
        
        # Authenticate user with our custom SAML backend
        backend = SAMLBackend()
        user = backend.authenticate(request, saml_authentication=auth)
        
        if not user:
            logger.error("Failed to authenticate user from SAML assertion")
            return HttpResponse("Failed to create user from SAML data", status=500)
        
        # Log the user into Django session
        login(request, user, backend='rotasystems.saml_backend.SAMLBackend')
        
        # Store SAML session info for Single Logout
        request.session['saml_name_id'] = auth.get_nameid()
        request.session['saml_name_id_format'] = auth.get_nameid_format()
        request.session['saml_name_id_nq'] = auth.get_nameid_nq()
        request.session['saml_name_id_spnq'] = auth.get_nameid_spnq()
        request.session['saml_session_index'] = auth.get_session_index()
        
        logger.info(f"SAML ACS: User authenticated successfully: {user.username}")
        
        # Get return URL from session or RelayState
        return_to = request.session.pop('saml_return_to', None)
        if not return_to:
            return_to = auth.redirect_to() or '/'
        
        return HttpResponseRedirect(return_to)
        
    except Exception as e:
        logger.error(f"SAML ACS processing failed: {e}", exc_info=True)
        return HttpResponseServerError("SAML authentication processing failed. Please contact support.")


@require_http_methods(["GET"])
def saml_logout(request):
    """
    Initiate SAML Single Logout (SLO).
    
    This view logs the user out of the application and sends a logout request
    to CGI SSO portal to terminate the SSO session.
    
    URL: /saml/logout/
    Method: GET
    """
    try:
        # Initialize SAML auth
        auth = get_saml_auth(request)
        
        # Get SAML session info
        name_id = request.session.get('saml_name_id')
        session_index = request.session.get('saml_session_index')
        name_id_format = request.session.get('saml_name_id_format')
        name_id_nq = request.session.get('saml_name_id_nq')
        name_id_spnq = request.session.get('saml_name_id_spnq')
        
        # Log out from Django session
        username = request.user.username if request.user.is_authenticated else 'unknown'
        logout(request)
        
        logger.info(f"User logged out: {username}")
        
        # If we have SAML session info, initiate SLO with CGI IdP
        if name_id:
            return HttpResponseRedirect(auth.logout(
                name_id=name_id,
                session_index=session_index,
                nq=name_id_nq,
                name_id_format=name_id_format,
                spnq=name_id_spnq
            ))
        else:
            # No SAML session (user may have used LDAP/Django auth fallback)
            return redirect('login')
            
    except Exception as e:
        logger.error(f"SAML logout failed: {e}", exc_info=True)
        # Still log out locally even if SAML logout fails
        logout(request)
        return redirect('login')


@csrf_exempt  # SAML POST comes from external IdP
@require_http_methods(["GET", "POST"])
def saml_sls(request):
    """
    Single Logout Service (SLS) - Process logout requests/responses from CGI IdP.
    
    This view handles:
    1. Logout requests initiated by CGI (user logged out from another app)
    2. Logout responses from CGI (acknowledgment of our logout request)
    
    URL: /saml/sls/
    Method: GET or POST (from CGI IdP)
    """
    try:
        # Initialize SAML auth
        auth = get_saml_auth(request)
        
        # Determine if this is a logout request or response
        request_id = request.session.get('saml_logout_request_id')
        
        # Process SLO
        def logout_callback():
            """Callback to clear Django session after SAML logout"""
            logout(request)
        
        url = auth.process_slo(
            request_id=request_id,
            delete_session_cb=logout_callback
        )
        
        errors = auth.get_errors()
        
        if errors:
            logger.error(f"SAML SLS errors: {errors}")
            logout(request)  # Force logout even if SLO has errors
            return redirect('login')
        
        # Redirect to URL from SLO or login page
        if url:
            return HttpResponseRedirect(url)
        else:
            return redirect('login')
            
    except Exception as e:
        logger.error(f"SAML SLS processing failed: {e}", exc_info=True)
        logout(request)  # Force logout
        return redirect('login')


@require_http_methods(["GET"])
def saml_metadata(request):
    """
    Provide SAML Service Provider (SP) metadata.
    
    This view generates and returns the SP metadata XML that CGI SSO team
    will use to register this application in their SSO portal.
    
    URL: /saml/metadata/
    Method: GET
    Returns: XML metadata document
    """
    try:
        # Initialize SAML auth
        auth = get_saml_auth(request)
        
        # Generate metadata XML
        settings_obj = auth.get_settings()
        metadata = settings_obj.get_sp_metadata()
        
        # Validate metadata
        errors = settings_obj.validate_metadata(metadata)
        
        if errors:
            logger.error(f"SAML metadata validation errors: {errors}")
            return HttpResponse(
                f"Error generating metadata: {', '.join(errors)}",
                content_type='text/plain',
                status=500
            )
        
        logger.info("SAML metadata requested")
        
        return HttpResponse(
            metadata,
            content_type='text/xml'
        )
        
    except Exception as e:
        logger.error(f"SAML metadata generation failed: {e}", exc_info=True)
        return HttpResponseServerError("Failed to generate SAML metadata")


@require_http_methods(["GET"])
def saml_status(request):
    """
    SAML configuration status page (for administrators).
    
    Shows current SAML configuration and connectivity status with CGI IdP.
    
    URL: /saml/status/
    Method: GET
    Requires: is_staff permission
    """
    if not request.user.is_staff:
        return HttpResponse("Access denied", status=403)
    
    try:
        from rotasystems.saml_settings import (
            SAML_ENABLED, SAML_SP_ENTITY_ID, SAML_IDP_ENTITY_ID,
            SAML_IDP_SSO_URL, SAML_ACS_URL
        )
        
        # Check if SAML is enabled
        if not SAML_ENABLED:
            status_message = "SAML SSO is DISABLED"
            status_class = "warning"
        else:
            status_message = "SAML SSO is ENABLED"
            status_class = "success"
        
        context = {
            'saml_enabled': SAML_ENABLED,
            'status_message': status_message,
            'status_class': status_class,
            'sp_entity_id': SAML_SP_ENTITY_ID,
            'idp_entity_id': SAML_IDP_ENTITY_ID,
            'idp_sso_url': SAML_IDP_SSO_URL,
            'acs_url': SAML_ACS_URL,
        }
        
        return render(request, 'saml/status.html', context)
        
    except Exception as e:
        logger.error(f"Failed to load SAML status: {e}", exc_info=True)
        return HttpResponseServerError("Failed to load SAML status")
