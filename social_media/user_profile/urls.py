from django.urls import path
from user_profile import views

urlpatterns = [
    path('edit/', views.ProfileUpdate.as_view()),
    path('<str:username>/', views.ProfileRetrieve.as_view()),
]