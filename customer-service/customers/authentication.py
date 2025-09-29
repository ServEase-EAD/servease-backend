"""
Custom authentication classes for customer service
Handles JWT token validation and customer-specific authentication
"""

import jwt
import requests
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.contrib.auth.models import AnonymousUser
from .models import Customer


class CustomerUser:
    """
    Custom user class to represent authenticated customers
    """

    def __init__(self, user_data):
        self.id = user_data.get('user_id')
        self.user_id = user_data.get('user_id')
        self.email = user_data.get('email', '')
        self.user_role = user_data.get('user_role', 'customer')
        self.is_authenticated = True
        self.is_anonymous = False
        self.is_staff = False
        self.is_superuser = False

    def __str__(self):
        return f"CustomerUser({self.email})"

    def is_customer(self):
        return self.user_role == 'customer'


class CustomerJWTAuthentication(BaseAuthentication):
    """
    Custom JWT authentication for customer service
    Validates tokens and creates CustomerUser instances
    """

    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if a valid signature has been
        supplied using JWT-based authentication. Otherwise returns `None`.
        """
        # Get the Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        # Extract the token
        token = auth_header.split(' ')[1]

        try:
            # Decode and validate the token using Django settings
            from django.conf import settings
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )

            # Extract user information from token
            user_id = payload.get('user_id')
            email = payload.get('email', '')
            user_role = payload.get('user_role', 'customer')

            # Only allow customers to access customer service
            if user_role != 'customer':
                raise exceptions.PermissionDenied(
                    'Only customers can access this service')

            # Create custom user object with token data
            user_data = {
                'user_id': user_id,
                'email': email,
                'user_role': user_role
            }

            user = CustomerUser(user_data)
            return user, token

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')
        except Exception as e:
            raise exceptions.AuthenticationFailed(
                f'Authentication failed: {str(e)}')


def verify_token_with_auth_service(token):
    """
    Verify JWT token with authentication service
    Returns user data if token is valid
    """
    try:
        auth_service_url = settings.AUTH_SERVICE_URL
        headers = {
            'Content-Type': 'application/json'
        }

        data = {
            'token': token
        }

        # Call auth service to verify token and get user data
        response = requests.post(
            f'{auth_service_url}/api/auth/validate-token/',
            headers=headers,
            json=data,
            timeout=10
        )

        if response.status_code == 200:
            return response.json()
        else:
            return None

    except Exception as e:
        print(f"Error verifying token with auth service: {e}")
        return None
