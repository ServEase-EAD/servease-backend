"""
URL configuration for admin_service project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def health_check(request):
    """Health check endpoint for Kubernetes probes."""
    return JsonResponse({'status': 'healthy', 'service': 'admin'})


urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('api/v1/admin/', include('admin_api.urls')),
    # Health check endpoint for Kubernetes liveness/readiness probes
    path('health/', health_check, name='health-check'),
]
