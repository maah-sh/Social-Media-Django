import json

from asgiref.sync import sync_to_async, async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from django.db.models import Q
from .models import Conversation, Message, ConvertionType
from .serilizers import ConversationSerializer, MessageSerializer
from django.contrib.auth.models import User


class ChatConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_user = None
        self.conversation_id = None
        self.conversation_group_name = None
        self.conversation = None

    async def connect(self):
        self.auth_user = await User.objects.aget(username='testun')
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.conversation_group_name = f"conversation_{self.conversation_id}"

        try:
            self.conversation = await Conversation.objects.aget(pk=self.conversation_id)
            await self.channel_layer.group_add(self.conversation_group_name, self.channel_name)
            await self.accept()

        except Conversation.DoesNotExist:
            await self.close()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.conversation_group_name, self.channel_name)


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json['content']
        await Message.objects.acreate(conversation=self.conversation, sender=self.auth_user, content=message_content)
        self.conversation.last_message_content = message_content
        await self.conversation.asave()

        await self.channel_layer.group_send(
            self.conversation_group_name,
            {"type": "send.message", "message": message_content}
        )

        async for participant in self.conversation.participants.all():
            await self.channel_layer.group_send(f"chat_list_{participant.id}", {"type": "chat.list.update"})


    async def send_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))


class PrivateChatConsumer(ChatConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recipient_user = None

    async def connect(self):
        self.auth_user = await User.objects.aget(username='testun')
        recipient_username = self.scope['url_route']['kwargs']['username']
        try:
            self.recipient_user = await User.objects.aget(username=recipient_username)
            search_query = Conversation.objects.filter(
                Q(conversation_type=ConvertionType.PRIVATE) &
                (Q(created_by=self.auth_user, participants=self.recipient_user.pk) |
                Q(created_by=self.recipient_user, participants=self.auth_user.pk))
            )
            if await search_query.aexists():
                print('find')
                self.conversation = await search_query.aget()
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
            self.conversation = await Conversation.objects.acreate(
                conversation_type=ConvertionType.PRIVATE,
                created_by=self.auth_user
            )
            await self.conversation.participants.aadd(self.auth_user)
            await self.conversation.participants.aadd(self.recipient_user)
            self.conversation_group_name = f"conversation_{self.conversation_id}"
            await self.channel_layer.group_add(self.conversation_group_name, self.channel_name)

        await super().receive(text_data)



class ChatListConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_user = None
        self.chat_list_group_name = None

    def connect(self):
        self.auth_user = User.objects.get(username='testun')
        self.chat_list_group_name = f"chat_list_{self.auth_user.pk}"

        async_to_sync(self.channel_layer.group_add)(self.chat_list_group_name, self.channel_name)
        self.accept()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(self.chat_list_group_name, self.channel_name)


    def chat_list_update(self, event):
        chats = self.auth_user.conversations.all()
        serializer = ConversationSerializer(chats, many=True)
        self.send(text_data=json.dumps(serializer.data))


