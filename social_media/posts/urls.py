from django.urls import path
from . import views

urlpatterns = [
    path('user-posts/', views.UserPostsList.as_view()),
    path('published-posts/', views.PublishedPostsList.as_view()),
    path('post/', views.PostCreate.as_view()),
    path('post/<int:pk>/', views.PostRetrieveUpdateDestroy.as_view()),
    path('comment/', views.CommentCreate.as_view()),
    path('comment/<int:pk>/', views.CommentRetrieveUpdateDestroy.as_view()),
    path('post/comments/<int:pk>/', views.PostComments.as_view()),
]