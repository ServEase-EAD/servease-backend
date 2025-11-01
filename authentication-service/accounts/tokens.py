"""
Custom JWT Token classes for ServEase Authentication
Includes additional user information in token payload
"""

from rest_framework_simplejwt.tokens import RefreshToken


class CustomRefreshToken(RefreshToken):
    """Custom refresh token that includes additional user data in payload"""

    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)

        # Add custom claims to the token payload
        token['email'] = user.email
        token['user_role'] = user.user_role
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name

        return token


class CustomAccessToken(RefreshToken.access_token_class):
    """Custom access token that includes additional user data in payload"""

    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)

        # Add custom claims to the token payload
        token['email'] = user.email
        token['user_role'] = user.user_role
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name

        return token
