from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination, CursorPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serilizers import ConversationSerializer, MessageSerializer
from .models import Conversation
from .permissions import IsParticipant



class UserChatsList(generics.ListAPIView):
    serializer_class = ConversationSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination


    def get_queryset(self):
        return self.request.user.conversations.order_by('-updated_at')


class ChatMessagesList(generics.ListAPIView):
    serializer_class = MessageSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsParticipant]
    pagination_class = CursorPagination

    def get_queryset(self):
        self.paginator.page_size = 3
        self.paginator.ordering = '-created_at'
        conversation = get_object_or_404(Conversation, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, conversation)
        return conversation.messages