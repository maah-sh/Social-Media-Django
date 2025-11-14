from django.db import models
from django.conf import settings


class ConversationType(models.TextChoices):
    PRIVATE = 'private'
    GROUP = 'group'

class Conversation(models.Model):
    type = models.CharField(max_length=10, choices=ConversationType, default=ConversationType.PRIVATE)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
    last_message_content = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='sent_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PrivateConversation(models.Model):
    conversation = models.OneToOneField(Conversation, on_delete=models.CASCADE, related_name='private')
    starter_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='+')
    other_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='+')


class GroupConversation(models.Model):
    conversation = models.OneToOneField(Conversation, on_delete=models.CASCADE, related_name='group')
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, related_name='owned_groups')
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='+')



