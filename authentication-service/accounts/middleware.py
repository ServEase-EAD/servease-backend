"""
JWT Authentication Middleware for microservices
This middleware validates JWT tokens and attaches the user to the request
"""
import jwt
from django.conf import settings
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .models import CustomUser


class JWTAuthenticationMiddleware:
    """
    Middleware to validate JWT tokens from Authorization header
    and attach user to request object for all views
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Paths that don't require authentication
        self.exempt_paths = [
            '/api/v1/auth/register/',
            '/api/v1/auth/login/',
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
                user_id = access_token.get('user_id')
                
                # Get user from database
                try:
                    user = CustomUser.objects.get(id=user_id)
                    if not user.is_active:
                        return JsonResponse(
                            {'error': 'User account is inactive'},
                            status=401
                        )
                    request.user = user
                    request.auth = access_token
                except CustomUser.DoesNotExist:
                    return JsonResponse(
                        {'error': 'User not found'},
                        status=401
                    )
                    
            except (InvalidToken, TokenError) as e:
                return JsonResponse(
                    {'error': 'Invalid or expired token', 'detail': str(e)},
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
