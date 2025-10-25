"""
ASGI config for notification_service project.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import notification_service.routing # Import the routing file you will create

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notification_service.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            notification_service.routing.websocket_urlpatterns
        )
    ),
})