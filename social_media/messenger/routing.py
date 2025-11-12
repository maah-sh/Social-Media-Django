from django.urls import re_path

from messenger import consumers

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<conversation_id>\w+)/$", consumers.ChatConsumer.as_asgi()),
    re_path(r"ws/chat/with/(?P<username>\w+)/$", consumers.PrivateChatConsumer.as_asgi()),
    re_path(r"ws/chats/$", consumers.ChatListConsumer.as_asgi()),
]