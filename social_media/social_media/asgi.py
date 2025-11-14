"""
ASGI config for social_media project.
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django_channels_jwt.middleware import JwtAuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_media.settings')

django_asgi_app = get_asgi_application()

from messenger.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
                JwtAuthMiddlewareStack(URLRouter(websocket_urlpatterns))
            ),
})