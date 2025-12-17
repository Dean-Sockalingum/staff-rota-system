"""
View decorators for permission and access control in the multi-home system.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models_multi_home import CareHome


def require_permission_level(required_level):
    """
    Decorator to require a specific permission level for a view.
    
    Usage:
        @require_permission_level('FULL')
        def my_view(request):
            ...
    
    Levels:
        - FULL: SM/OM - Full access (approvals, rota management, all data)
        - MOST: SSCW - Most access (view schedules, team data, submit requests)
        - LIMITED: Staff - Limited access (view own info, submit requests only)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if not request.user.has_permission_level(required_level):
                messages.error(
                    request, 
                    f"You need {required_level} access level to view this page."
                )
                raise PermissionDenied
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_home_access(home_param='care_home'):
    """
    Decorator to verify user can access the requested care home.
    
    Usage:
        @require_home_access()  # Uses 'care_home' GET parameter
        def my_view(request):
            ...
        
        @require_home_access('home_slug')  # Uses 'home_slug' URL parameter
        def my_view(request, home_slug=None):
            ...
    
    Senior management team can access all homes.
    Regular staff can only access their assigned home.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Get home identifier from GET params or URL kwargs
            home_identifier = request.GET.get(home_param) or kwargs.get(home_param)
            
            if not home_identifier:
                # No home specified - allow senior management, redirect others to their home
                if request.user.role and request.user.role.is_senior_management_team:
                    return view_func(request, *args, **kwargs)
                elif request.user.assigned_care_home:
                    messages.info(
                        request,
                        f"You have been redirected to your home: {request.user.assigned_care_home.display_name}"
                    )
                    # Add home parameter and redirect
                    from django.http import QueryDict
                    query_params = request.GET.copy()
                    query_params[home_param] = request.user.assigned_care_home.name
                    return redirect(f"{request.path}?{query_params.urlencode()}")
                else:
                    messages.error(request, "You are not assigned to a care home.")
                    raise PermissionDenied
            
            # Verify access to specified home
            try:
                care_home = CareHome.objects.get(name=home_identifier)
            except CareHome.DoesNotExist:
                messages.error(request, f"Care home '{home_identifier}' not found.")
                raise PermissionDenied
            
            if not request.user.can_access_home(care_home):
                messages.error(
                    request,
                    f"You do not have access to {care_home.display_name}."
                )
                raise PermissionDenied
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_role(allowed_roles):
    """
    Decorator to require user has one of the specified roles.
    
    Usage:
        @require_role(['OPERATIONS_MANAGER', 'SSCW'])
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if not request.user.role or request.user.role.name not in allowed_roles:
                messages.error(
                    request,
                    "You do not have the required role to access this page."
                )
                raise PermissionDenied
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_management():
    """
    Decorator to require user is in management (any management role).
    
    Usage:
        @require_management()
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if not (request.user.role and request.user.role.is_management):
                messages.error(request, "Management access required.")
                raise PermissionDenied
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_senior_management():
    """
    Decorator to require user is on senior management team.
    
    Usage:
        @require_senior_management()
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if not (request.user.role and request.user.role.is_senior_management_team):
                messages.error(
                    request,
                    "Senior management team access required."
                )
                raise PermissionDenied
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
