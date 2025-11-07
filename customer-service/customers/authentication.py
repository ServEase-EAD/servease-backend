"""
Custom authentication classes for customer service
Validates JWT tokens and integrates with authentication service
"""

import jwt
import requests
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions


class CustomerUser:
    """
    Custom user class to represent authenticated customers.
    Contains user data from JWT token payload.
    """

    def __init__(self, user_data):
        self.id = user_data.get('user_id')
        self.user_id = user_data.get('user_id')
        self.email = user_data.get('email', '')
        self.first_name = user_data.get('first_name', '')
        self.last_name = user_data.get('last_name', '')
        self.user_role = user_data.get('user_role', 'customer')
        self.is_active = user_data.get('is_active', True)
        self.is_authenticated = True
        self.is_anonymous = False
        self.is_staff = False
        self.is_superuser = False

    def __str__(self):
        return f"CustomerUser({self.email}, id={self.user_id})"

    def is_customer(self):
        return self.user_role == 'customer'

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class CustomerJWTAuthentication(BaseAuthentication):
    """
    Custom JWT authentication for customer service.
    Validates tokens issued by authentication service and creates CustomerUser instances.

    This authentication class:
    1. Extracts JWT token from Authorization header
    2. Decodes and validates token using shared SECRET_KEY
    3. Ensures user_role is 'customer'
    4. Creates CustomerUser object with token payload data
    """

    def authenticate(self, request):
        """
        Returns a two-tuple of `CustomerUser` and token if valid.
        Returns None if no token provided (allowing other authentication methods).
        Raises AuthenticationFailed for invalid tokens.
        """
        # Get the Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None

        if not auth_header.startswith('Bearer '):
            return None

        # Extract the token
        token = auth_header.split(' ')[1]

        try:
            # Decode and validate the token using Django settings
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )

            # Extract user information from token
            user_id = payload.get('user_id')
            if not user_id:
                raise exceptions.AuthenticationFailed('Token missing user_id')

            email = payload.get('email', '')
            first_name = payload.get('first_name', '')
            last_name = payload.get('last_name', '')
            user_role = payload.get('user_role', 'customer')

            # Allow customers, admins, and employees to access customer service
            # Admins and employees need access for inter-service calls and management
            if user_role not in ['customer', 'admin', 'employee']:
                raise exceptions.PermissionDenied(
                    'Access denied. '
                    f'Your role ({user_role}) is not authorized.'
                )

            # Create custom user object with token data
            user_data = {
                'user_id': user_id,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'user_role': user_role,
                'is_active': True
            }

            user = CustomerUser(user_data)
            return user, token

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError as e:
            raise exceptions.AuthenticationFailed(f'Invalid token: {str(e)}')
        except Exception as e:
            raise exceptions.AuthenticationFailed(
                f'Authentication failed: {str(e)}')


def get_user_data_from_auth_service(user_id):
    """
    Fetch user data from authentication service by user_id.

    Args:
        user_id: UUID of the user in authentication service

    Returns:
        dict: User data including email, name, phone, etc.
        None: If request fails or user not found
    """
    try:
        auth_service_url = getattr(
            settings, 'AUTH_SERVICE_URL', 'http://localhost:8001')

        # Call auth service user detail endpoint
        response = requests.get(
            f'{auth_service_url}/api/auth/admin/users/{user_id}/',
            timeout=5
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(
                f"Failed to fetch user data from auth service: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching user data from auth service: {e}")
        return None


def validate_token_with_auth_service(token):
    """
    Verify JWT token with authentication service.

    Args:
        token: JWT token string

    Returns:
        dict: User data if token is valid
        None: If token is invalid

    Note: This is an alternative to local JWT decoding.
    Use this when you need to verify token validity with the auth service.
    """
    try:
        auth_service_url = getattr(
            settings, 'AUTH_SERVICE_URL', 'http://localhost:8001')

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        # Call auth service token validation endpoint
        response = requests.post(
            f'{auth_service_url}/api/auth/validate-token/',
            headers=headers,
            timeout=5
        )

        if response.status_code == 200:
            return response.json()
        else:
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error verifying token with auth service: {e}")
        return None
