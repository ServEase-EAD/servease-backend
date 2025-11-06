"""
Shared JWT Authentication Middleware for other microservices
This middleware validates JWT tokens without requiring direct database access
to the authentication service's user table
"""
import jwt
from django.conf import settings
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class JWTAuthenticationMiddleware:
    """
    Middleware to validate JWT tokens from Authorization header
    Extracts user information from the token claims
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Paths that don't require authentication
        self.exempt_paths = [
            '/admin/',
            '/health/',
        ]
    
    def __call__(self, request):
        # Check if path is exempt from authentication
        if self._is_exempt_path(request.path):
            return self.get_response(request)
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            try:
                # Validate and decode token
                access_token = AccessToken(token)
                
                # Extract user information from token claims
                user_data = {
                    'id': access_token.get('user_id'),
                    'email': access_token.get('email'),
                    'user_role': access_token.get('user_role'),
                    'first_name': access_token.get('first_name'),
                    'last_name': access_token.get('last_name'),
                }
                
                # Attach user data to request
                request.user_data = user_data
                request.auth = access_token
                
            except (InvalidToken, TokenError) as e:
                return JsonResponse(
                    {'error': 'Invalid or expired token', 'detail': str(e)},
                    status=401
                )
        else:
            # No token provided for non-exempt path
            return JsonResponse(
                {'error': 'Authentication required'},
                status=401
            )
        
        response = self.get_response(request)
        return response
    
    def _is_exempt_path(self, path):
        """Check if the path is exempt from authentication"""
        for exempt_path in self.exempt_paths:
            if path.startswith(exempt_path):
                return True
        return False


class SecurityHeadersMiddleware:
    """
    Middleware to add security headers to all responses
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response


def require_role(*allowed_roles):
    """
    Decorator to check if user has required role
    Usage: @require_role('admin', 'employee')
    """
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            user_data = getattr(request, 'user_data', None)
            if not user_data:
                return JsonResponse(
                    {'error': 'Authentication required'},
                    status=401
                )
            
            user_role = user_data.get('user_role')
            if user_role not in allowed_roles:
                return JsonResponse(
                    {'error': 'Permission denied. Insufficient privileges.'},
                    status=403
                )
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator
