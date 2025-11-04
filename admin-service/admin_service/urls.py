"""
URL configuration for admin_service project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('api/v1/admin/', include('admin_api.urls')),
]
