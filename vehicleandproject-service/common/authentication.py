# common/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions
import jwt
from django.conf import settings

class StatelessJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        try:
            # Decode token manually (no DB lookup)
            payload = jwt.decode(
                raw_token,
                settings.SIMPLE_JWT['SIGNING_KEY'],
                algorithms=["HS256"]
            )
            
            # Create a lightweight user object (not from DB)
            user = type("UserObject", (), {
                "id": payload.get("user_id"),
                "user_role": payload.get("user_role", None),
                "email": payload.get("email", ""),
                "is_authenticated": True
            })()
            
            return (user, raw_token)
        
        except Exception as e:
            raise exceptions.AuthenticationFailed("Invalid token")
