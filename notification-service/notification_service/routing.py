from django.urls import re_path
from notifications import consumers

websocket_urlpatterns = [
    # WebSocket route for a specific user to receive notifications
    re_path(r'ws/notifications/(?P<user_id>\w+)/$', consumers.NotificationConsumer.as_asgi()),
]