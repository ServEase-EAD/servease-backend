"""
URL configuration for employee_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_auth(request):
    """Test endpoint to verify JWT authentication works"""
    return Response({
        'message': 'Authentication successful!',
        'user_id': request.user.user_id if hasattr(request.user, 'user_id') else None,
        'auth_header': request.META.get('HTTP_AUTHORIZATION', 'No auth header'),
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/employees/', include('employees.urls')),           # Employee profiles
    path('api/v1/employees/timelogs/', include('timelogs.urls')),    # Time logs (employee-centric)
    path('api/v1/test-auth/', test_auth),                           # Test authentication
    
    # Health check
    path('health/', lambda request: JsonResponse({'status': 'healthy'})),
]
