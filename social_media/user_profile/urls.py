from django.urls import path
from user_profile import views

urlpatterns = [
    path('edit/', views.ProfileUpdate.as_view()),
]