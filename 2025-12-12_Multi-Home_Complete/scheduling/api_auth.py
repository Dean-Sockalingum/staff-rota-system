"""
Integration API Authentication and Rate Limiting
================================================

Middleware and utilities for API authentication and rate limiting.

Created: 30 December 2025
Task 41: Integration APIs
"""

from django.http import JsonResponse
from django.utils import timezone
from functools import wraps
import time

from .models_integrations import APIClient, APIToken, APIRateLimit, APIRequestLog


class APIAuthenticationMiddleware:
    """
    Middleware to authenticate API requests using API keys or tokens.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Only process API requests
        if not request.path.startswith('/api/v1/integration/'):
            return self.get_response(request)
        
        # Skip authentication for documentation endpoints
        if request.path.endswith('/docs') or request.path.endswith('/schema'):
            return self.get_response(request)
        
        # Extract authentication credentials
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        api_key = request.META.get('HTTP_X_API_KEY', '')
        
        client = None
        
        # Try API key authentication
        if api_key:
            try:
                client = APIClient.objects.get(
                    api_key=api_key,
                    is_active=True,
                    status='ACTIVE'
                )
            except APIClient.DoesNotExist:
                return JsonResponse({
                    'error': 'Invalid API key',
                    'code': 'INVALID_API_KEY'
                }, status=401)
        
        # Try Bearer token authentication
        elif auth_header.startswith('Bearer '):
            token_value = auth_header.split(' ')[1]
            try:
                token = APIToken.objects.select_related('client').get(
                    token=token_value,
                    is_active=True
                )
                
                if not token.is_valid():
                    return JsonResponse({
                        'error': 'Token expired',
                        'code': 'TOKEN_EXPIRED'
                    }, status=401)
                
                client = token.client
                token.last_used_at = timezone.now()
                token.use_count += 1
                token.save()
                
            except APIToken.DoesNotExist:
                return JsonResponse({
                    'error': 'Invalid token',
                    'code': 'INVALID_TOKEN'
                }, status=401)
        
        else:
            return JsonResponse({
                'error': 'Authentication required',
                'code': 'AUTH_REQUIRED',
                'message': 'Provide API key via X-API-Key header or Bearer token'
            }, status=401)
        
        # Check IP whitelist
        if client.ip_whitelist:
            client_ip = self.get_client_ip(request)
            if client_ip not in client.ip_whitelist:
                return JsonResponse({
                    'error': 'IP address not whitelisted',
                    'code': 'IP_NOT_ALLOWED',
                    'ip': client_ip
                }, status=403)
        
        # Check allowed endpoints
        if client.allowed_endpoints:
            endpoint = request.path.replace('/api/v1/integration/', '')
            if not any(endpoint.startswith(pattern) for pattern in client.allowed_endpoints):
                return JsonResponse({
                    'error': 'Endpoint not allowed',
                    'code': 'ENDPOINT_NOT_ALLOWED',
                    'endpoint': endpoint
                }, status=403)
        
        # Check allowed methods
        if client.allowed_methods:
            if request.method not in client.allowed_methods:
                return JsonResponse({
                    'error': 'Method not allowed',
                    'code': 'METHOD_NOT_ALLOWED',
                    'method': request.method
                }, status=405)
        
        # Attach client to request
        request.api_client = client
        
        return self.get_response(request)
    
    def get_client_ip(self, request):
        """Extract client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class APIRateLimitMiddleware:
    """
    Middleware to enforce rate limiting on API requests.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Only process API requests
        if not request.path.startswith('/api/v1/integration/'):
            return self.get_response(request)
        
        # Skip rate limiting for unauthenticated requests (handled by auth middleware)
        if not hasattr(request, 'api_client'):
            return self.get_response(request)
        
        client = request.api_client
        endpoint = request.path.replace('/api/v1/integration/', '')
        
        # Check rate limits for different windows
        for window_type in ['MINUTE', 'HOUR', 'DAY']:
            allowed, rate_limit = APIRateLimit.check_rate_limit(
                client, window_type, endpoint
            )
            
            if not allowed:
                # Determine when rate limit resets
                if window_type == 'MINUTE':
                    reset_seconds = 60 - timezone.now().second
                    limit = client.rate_limit_per_minute
                elif window_type == 'HOUR':
                    reset_seconds = (60 - timezone.now().minute) * 60
                    limit = client.rate_limit_per_hour
                else:  # DAY
                    now = timezone.now()
                    tomorrow = now.replace(hour=0, minute=0, second=0) + timezone.timedelta(days=1)
                    reset_seconds = int((tomorrow - now).total_seconds())
                    limit = client.rate_limit_per_day
                
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'code': 'RATE_LIMIT_EXCEEDED',
                    'window': window_type.lower(),
                    'limit': limit,
                    'current': rate_limit.request_count,
                    'reset_in_seconds': reset_seconds
                }, status=429)
        
        return self.get_response(request)


class APILoggingMiddleware:
    """
    Middleware to log all API requests.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Only log API requests
        if not request.path.startswith('/api/v1/integration/'):
            return self.get_response(request)
        
        # Start timer
        start_time = time.time()
        
        # Process request
        response = self.get_response(request)
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR', '0.0.0.0')
        
        # Extract request body (for POST/PUT)
        request_body = {}
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                if hasattr(request, 'data'):
                    request_body = request.data
                elif request.body:
                    import json
                    request_body = json.loads(request.body)
            except:
                request_body = {}
        
        # Log request
        log_data = {
            'endpoint': request.path,
            'method': request.method,
            'query_params': dict(request.GET),
            'request_body': request_body,
            'ip_address': ip_address,
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500],
            'status_code': response.status_code,
            'response_time_ms': response_time_ms,
            'response_size': len(response.content) if hasattr(response, 'content') else 0,
        }
        
        # Add client if authenticated
        if hasattr(request, 'api_client'):
            log_data['client'] = request.api_client
            
            # Update client statistics
            request.api_client.increment_request_count(
                success=(200 <= response.status_code < 300)
            )
        
        # Create log entry (async to not slow down response)
        try:
            APIRequestLog.objects.create(**log_data)
        except Exception as e:
            # Don't fail request if logging fails
            print(f"Failed to log API request: {e}")
        
        # Add rate limit headers
        if hasattr(request, 'api_client'):
            response['X-RateLimit-Limit-Minute'] = request.api_client.rate_limit_per_minute
            response['X-RateLimit-Limit-Hour'] = request.api_client.rate_limit_per_hour
            response['X-RateLimit-Limit-Day'] = request.api_client.rate_limit_per_day
        
        return response


def require_api_scope(*required_scopes):
    """
    Decorator to require specific API scopes.
    
    Usage:
        @require_api_scope('staff:read', 'shifts:read')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            # Check if request has API client
            if not hasattr(request, 'api_client'):
                return JsonResponse({
                    'error': 'Authentication required',
                    'code': 'AUTH_REQUIRED'
                }, status=401)
            
            # If using token, check scopes
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header.startswith('Bearer '):
                token_value = auth_header.split(' ')[1]
                try:
                    token = APIToken.objects.get(token=token_value)
                    token_scopes = set(token.scope)
                    
                    # Check if token has all required scopes
                    if not all(scope in token_scopes for scope in required_scopes):
                        return JsonResponse({
                            'error': 'Insufficient permissions',
                            'code': 'INSUFFICIENT_SCOPE',
                            'required_scopes': required_scopes,
                            'token_scopes': list(token_scopes)
                        }, status=403)
                except APIToken.DoesNotExist:
                    pass
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator
