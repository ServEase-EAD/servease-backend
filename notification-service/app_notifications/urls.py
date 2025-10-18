from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import NotificationViewSet

router = DefaultRouter()
# Register the viewset to handle all standard API routes
router.register(r'', NotificationViewSet, basename='notification')

urlpatterns = [
    # This includes all standard CRUD routes and custom actions
    path('', include(router.urls)),
]

# This provides the following API endpoints:
# GET /api/v1/notifications/                   - List all (or filtered) notifications
# POST /api/v1/notifications/                  - Create a new notification
# GET /api/v1/notifications/{id}/              - Retrieve a notification
# POST /api/v1/notifications/{id}/mark_as_read/ - Mark specific notification as read
# POST /api/v1/notifications/mark_all_as_read/ - Mark all notifications as read