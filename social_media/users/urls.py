from django.urls import path
from users import views

urlpatterns = [
    path('profile/edit/', views.ProfileUpdate.as_view()),
    path('profile/<str:username>/', views.ProfileRetrieve.as_view()),
]