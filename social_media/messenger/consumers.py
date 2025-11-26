import json

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from django.db.models import Q
from .models import Conversation, Message, PrivateConversation, ConversationType
from django.contrib.auth.models import User
from .services import PrivateChatService, MessageService


class ChatConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conversation = None
        self.conversation_group_name = None

    async def connect(self):
        conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.conversation_group_name = f"conversation_{conversation_id}"
        try:
            self.conversation = await Conversation.objects.aget(pk=conversation_id)
            await self.channel_layer.group_add(self.conversation_group_name, self.channel_name)
            await self.accept()
        except Conversation.DoesNotExist:
            await self.close()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.conversation_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        content = text_data_json['content']
        message_service = MessageService(conversation=self.conversation, sender=self.scope["user"], content=content)
        await database_sync_to_async(message_service.create_message)()
        await self.channel_layer.group_send(self.conversation_group_name,{"type": "send.message", "message": content})
        async for participant in self.conversation.participants.all():
            await self.channel_layer.group_send(f"chat_list_{participant.pk}", {"type": "chat.list.update"})

    async def send_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))


class PrivateChatConsumer(ChatConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.private_chat_service = None

    async def connect(self):
        recipient_username = self.scope['url_route']['kwargs']['username']
        try:
            recipient_user = await User.objects.aget(username=recipient_username)
            self.private_chat_service = PrivateChatService(first_user=self.scope["user"], second_user=recipient_user)
            self.conversation = await database_sync_to_async(self.private_chat_service.get_conversation)()
            if self.conversation:
                self.conversation_group_name = f"conversation_{self.conversation.pk}"
                await self.channel_layer.group_add(self.conversation_group_name, self.channel_name)
            await self.accept()
        except User.DoesNotExist:
            await self.close()

    async def disconnect(self, code):
        if self.conversation:
            await super().disconnect(code)

    async def receive(self, text_data):
        if self.conversation is None:
            self.conversation = await database_sync_to_async(self.private_chat_service.create_conversation)()
            self.conversation_group_name = f"conversation_{self.conversation.pk}"
            await self.channel_layer.group_add(self.conversation_group_name, self.channel_name)

        await super().receive(text_data)


class ChatListConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_list_group_name = None

    async def connect(self):
        self.chat_list_group_name = f"chat_list_{self.scope["user"].pk}"
        await self.channel_layer.group_add(self.chat_list_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.chat_list_group_name, self.channel_name)

    async def chat_list_update(self, event):
        await self.send(text_data=json.dumps({"details":"New message in list of chats"}))


