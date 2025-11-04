"""
Custom Authentication for Admin Service
Admin service doesn't have its own user database, so we validate tokens
and extract user info without querying the database
"""
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth.models import AnonymousUser


class JWTTokenAuthentication(BaseAuthentication):
    """
    Custom JWT authentication that doesn't require database user lookup.
    Validates the token and returns user info from token payload.
    """
    
    def authenticate(self, request):
        # Get the authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            return None
        
        # Extract token
        token_string = auth_header.split(' ')[1]
        
        try:
            # Validate token
            token = AccessToken(token_string)
            
            # Create a simple user object from token payload
            user = TokenUser(token)
            
            return (user, token)
            
        except (TokenError, InvalidToken) as e:
            raise AuthenticationFailed(f'Invalid token: {str(e)}')


class TokenUser:
    """
    A simple user object created from JWT token payload.
    Does not require database access.
    """
    
    def __init__(self, token):
        self.token = token
        self.id = token.get('user_id')
        self.email = token.get('email', '')
        self.user_role = token.get('user_role', '')
        self.first_name = token.get('first_name', '')
        self.last_name = token.get('last_name', '')
        self.is_authenticated = True
        self.is_active = True
    
    @property
    def is_anonymous(self):
        return False
    
    def __str__(self):
        return f'{self.email} ({self.user_role})'
