from django.urls import path
from . import views

urlpatterns = [
    path('chats/', views.UserChatsList.as_view()),
    path('chat-messages/<int:pk>/', views.ChatMessagesList.as_view()),
]