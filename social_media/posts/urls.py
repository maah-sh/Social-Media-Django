from django.urls import path
from . import views

urlpatterns = [
    path('user-posts/', views.UserPostsList.as_view()),
    path('published-posts/', views.PublishedPostsList.as_view()),
    path('post/', views.PostCreate.as_view()),
    path('post/<int:pk>/', views.PostRetrieveUpdateDestroy.as_view()),
]