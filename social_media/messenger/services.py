from django.db.models import Q
from django.db.transaction import atomic
from .models import Conversation, ConversationType, PrivateConversation, Message


class MessageService:

    def __init__(self, conversation, sender ,content):
        self.conversation = conversation
        self.sender = sender
        self.content = content

    @atomic
    def create_message(self):
        Message.objects.create(
            conversation=self.conversation,
            sender=self.sender,
            content=self.content
        )
        self.conversation.last_message_content = self.content
        self.conversation.save()


class PrivateChatService:

    def __init__(self, first_user, second_user):
        self.first_user = first_user
        self.second_user = second_user

    @atomic
    def create_conversation(self):
        conversation = Conversation.objects.create(
            type=ConversationType.PRIVATE,
            created_by=self.first_user
        )
        PrivateConversation.objects.create(
            conversation=conversation,
            starter_user=self.first_user,
            other_user=self.second_user
        )
        conversation.participants.add(self.first_user)
        conversation.participants.add(self.second_user)

        return conversation

    def get_conversation(self):
        try:
            private_conversation = PrivateConversation.objects.get(
                Q(starter_user=self.first_user, other_user=self.second_user) |
                Q(starter_user=self.second_user, other_user=self.first_user)
            )
            return private_conversation.conversation
        except PrivateConversation.DoesNotExist:
            return None
