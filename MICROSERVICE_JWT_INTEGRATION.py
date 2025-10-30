"""
Example: How to add JWT authentication to other microservices

This example shows how to integrate the JWT authentication middleware
into other services like customer-service, employee-service, etc.
"""

# 1. Copy the shared middleware file to your service
# From: backend/shared/jwt_middleware.py
# To: your-service/shared/jwt_middleware.py

# 2. Update settings.py
# In your-service/your_service/settings.py

# Add to MIDDLEWARE (after existing middleware)
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Add these two lines
    'shared.jwt_middleware.JWTAuthenticationMiddleware',
    'shared.jwt_middleware.SecurityHeadersMiddleware',
]

# Ensure you have JWT settings (copy from authentication-service)
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# 3. Update requirements.txt
# Add these if not present:
"""
djangorestframework-simplejwt==5.3.0
PyJWT==2.8.0
"""

# 4. Example views using JWT authentication

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from shared.jwt_middleware import require_role
import json


# Example 1: Protected view - requires authentication
@require_http_methods(["GET"])
def get_user_data(request):
    """
    View accessible by any authenticated user
    """
    user_data = request.user_data
    return JsonResponse({
        'user_id': user_data['id'],
        'email': user_data['email'],
        'role': user_data['user_role'],
        'name': f"{user_data['first_name']} {user_data['last_name']}"
    })


# Example 2: Admin-only view
@require_role('admin')
@require_http_methods(["GET"])
def admin_dashboard(request):
    """
    View accessible only by admins
    """
    user_data = request.user_data
    return JsonResponse({
        'message': 'Welcome to admin dashboard',
        'admin': user_data['email']
    })


# Example 3: Employee or Admin view
@require_role('employee', 'admin')
@require_http_methods(["POST"])
def create_appointment(request):
    """
    View accessible by employees and admins
    """
    user_data = request.user_data
    data = json.loads(request.body)
    
    # Create appointment logic here
    
    return JsonResponse({
        'message': 'Appointment created',
        'created_by': user_data['email'],
        'creator_role': user_data['user_role']
    })


# Example 4: Customer-only view
@require_role('customer')
@require_http_methods(["GET"])
def customer_orders(request):
    """
    View accessible only by customers
    """
    user_data = request.user_data
    customer_id = user_data['id']
    
    # Get orders for this customer
    
    return JsonResponse({
        'customer_id': customer_id,
        'orders': []  # Your orders logic here
    })


# Example 5: Using Django REST Framework views
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_view_example(request):
    """
    DRF view with JWT authentication
    Note: Middleware attaches user_data to request
    """
    user_data = request.user_data
    
    return Response({
        'message': 'Authenticated request',
        'user': {
            'id': user_data['id'],
            'email': user_data['email'],
            'role': user_data['user_role']
        }
    })


# Example 6: Class-based view with role checking
from django.views import View
from django.utils.decorators import method_decorator


class CustomerProfileView(View):
    """
    Class-based view requiring customer role
    """
    
    @method_decorator(require_role('customer'))
    def get(self, request):
        user_data = request.user_data
        return JsonResponse({
            'profile': {
                'id': user_data['id'],
                'email': user_data['email'],
                'name': f"{user_data['first_name']} {user_data['last_name']}"
            }
        })
    
    @method_decorator(require_role('customer'))
    def put(self, request):
        user_data = request.user_data
        data = json.loads(request.body)
        
        # Update profile logic
        
        return JsonResponse({
            'message': 'Profile updated',
            'user_id': user_data['id']
        })


# 5. URL patterns example

from django.urls import path

urlpatterns = [
    path('api/v1/user/', get_user_data, name='user_data'),
    path('api/v1/admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('api/v1/appointments/', create_appointment, name='create_appointment'),
    path('api/v1/customer/orders/', customer_orders, name='customer_orders'),
    path('api/v1/customer/profile/', CustomerProfileView.as_view(), name='customer_profile'),
]


# 6. Testing your endpoints

"""
# Test with curl
curl -X GET http://localhost:8002/api/v1/user/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Test admin endpoint
curl -X GET http://localhost:8002/api/v1/admin/dashboard/ \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN"

# Test without token (should get 401)
curl -X GET http://localhost:8002/api/v1/user/

# Test with invalid token (should get 401)
curl -X GET http://localhost:8002/api/v1/user/ \
  -H "Authorization: Bearer invalid_token"
"""


# 7. Error handling example

@require_http_methods(["GET"])
def safe_view(request):
    """
    View with proper error handling
    """
    try:
        user_data = getattr(request, 'user_data', None)
        
        if not user_data:
            return JsonResponse(
                {'error': 'Authentication required'},
                status=401
            )
        
        # Your logic here
        
        return JsonResponse({
            'message': 'Success',
            'user': user_data['email']
        })
        
    except Exception as e:
        return JsonResponse(
            {'error': str(e)},
            status=500
        )


# 8. Middleware configuration options

"""
# In jwt_middleware.py, you can customize exempt paths:

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Customize these for your service
        self.exempt_paths = [
            '/admin/',
            '/health/',
            '/api/v1/public/',  # Add public endpoints here
        ]
"""


# 9. Advanced: Custom role checking

def check_user_role(user_data, allowed_roles):
    """
    Helper function to check if user has allowed role
    """
    return user_data.get('user_role') in allowed_roles


def custom_role_check(request, allowed_roles):
    """
    Custom role checking logic
    """
    user_data = getattr(request, 'user_data', None)
    
    if not user_data:
        return JsonResponse(
            {'error': 'Authentication required'},
            status=401
        )
    
    if not check_user_role(user_data, allowed_roles):
        return JsonResponse(
            {'error': 'Permission denied'},
            status=403
        )
    
    return None  # No error


# Example usage
@require_http_methods(["GET"])
def custom_protected_view(request):
    """
    View with custom role checking
    """
    error_response = custom_role_check(request, ['admin', 'employee'])
    if error_response:
        return error_response
    
    user_data = request.user_data
    
    return JsonResponse({
        'message': 'Access granted',
        'user': user_data['email']
    })


# 10. Migration checklist

"""
Checklist for migrating a service to use JWT authentication:

□ Copy jwt_middleware.py to your service
□ Update settings.py (add middleware)
□ Add JWT settings to settings.py
□ Install djangorestframework-simplejwt
□ Update views to use @require_role decorator
□ Remove old authentication logic
□ Update URL patterns if needed
□ Test all endpoints with JWT tokens
□ Test role-based access control
□ Update documentation
□ Deploy changes

Common issues:
- Missing SECRET_KEY: Ensure SECRET_KEY matches across services
- CORS errors: Update CORS settings in settings.py
- Token not found: Check Authorization header format
- Wrong role: Verify user role in JWT token at jwt.io
"""
