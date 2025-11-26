from django.db.models.signals import post_save
from django.dispatch import receiver
from messenger.models import Message


@receiver(post_save, sender=Message, dispatch_uid='conversation_last_message')
def set_conversation_last_message(sender, instance, created, **kwargs):
    conversation = instance.conversation
    if created or (instance.pk == conversation.messages.latest('created_at').pk):
        conversation.last_message_content = instance.content
        conversation.save()