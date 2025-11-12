from django.db import models
from django.conf import settings


class ConvertionType(models.TextChoices):
    PRIVATE = 'private'
    GROUP = 'group'

class Conversation(models.Model):
    conversation_type = models.CharField(max_length=10, choices=ConvertionType, default=ConvertionType.PRIVATE)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
    last_message_content = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
