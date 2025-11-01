from django.urls import re_path
from app_notifications import consumers

websocket_urlpatterns = [
    # WebSocket route for a specific user to receive notifications
    # Pattern supports UUIDs (includes hyphens)
    re_path(r'ws/notifications/(?P<user_id>[\w-]+)/$', consumers.NotificationConsumer.as_asgi()),
]