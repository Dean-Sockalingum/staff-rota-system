"""
Task 48: Two-Factor Authentication Middleware
Enforces 2FA for managers and administrators
"""
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django_otp import user_has_device
from django.conf import settings


class TwoFactorAuthMiddleware:
    """
    Middleware to enforce 2FA for managers and admins
    Redirects to 2FA setup if required but not enabled
    Redirects to 2FA verification if not verified in session
    """
    
    # URLs that don't require 2FA verification (allow access)
    EXEMPT_URLS = [
        '/login/',
        '/logout/',
        '/2fa/setup/',
        '/2fa/verify/',
        '/2fa/disable/',
        '/2fa/regenerate-backup-codes/',
        '/api/2fa/status/',
        '/static/',
        '/media/',
        '/offline/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip if user not authenticated
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        # Skip if URL is exempt
        path = request.path
        if any(path.startswith(exempt) for exempt in self.EXEMPT_URLS):
            return self.get_response(request)
        
        # Check if user requires 2FA
        requires_2fa = self._user_requires_2fa(request.user)
        
        if requires_2fa:
            # Check if user has 2FA enabled
            has_2fa = user_has_device(request.user)
            
            if not has_2fa:
                # Require user to set up 2FA
                messages.warning(
                    request,
                    "As a manager/admin, you must enable Two-Factor Authentication for enhanced security."
                )
                return redirect('scheduling:two_factor_setup')
            
            # Check if user is verified in this session
            is_verified = request.user.is_verified() if hasattr(request.user, 'is_verified') else False
            
            if not is_verified:
                # Store intended URL for redirect after verification
                request.session['next_after_2fa'] = request.path
                return redirect('scheduling:two_factor_verify')
        
        return self.get_response(request)
    
    def _user_requires_2fa(self, user):
        """
        Determine if user is required to have 2FA enabled
        Returns True for staff, superusers, and managers
        """
        # Staff and superusers always require 2FA
        if user.is_staff or user.is_superuser:
            return True
        
        # Check if user has manager role
        try:
            if hasattr(user, 'staff_profile'):
                profile = user.staff_profile
                if profile.role and 'Manager' in profile.role.name:
                    return True
        except:
            pass
        
        return False
