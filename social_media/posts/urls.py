from django.urls import path
from . import views

urlpatterns = [
    path('user-posts/', views.UserPostsList.as_view()),
    path('published-posts/', views.PublishedPostsList.as_view()),
    path('post/', views.PostCreate.as_view()),
    path('post/<int:pk>/', views.PostRetrieveUpdateDestroy.as_view()),
    path('add-comment/', views.CommentCreate.as_view()),
    path('edit-comment/<int:pk>/', views.CommentUpdate.as_view()),
    path('delete-comment/<int:pk>/', views.CommentDestroy.as_view()),
]