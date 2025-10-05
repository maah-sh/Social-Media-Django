from django.urls import path
from users import views

urlpatterns = [
    path('register/', views.Register.as_view()),
    path('login/', views.Login.as_view()),
    path('logout/', views.Logout.as_view()),
    path('profile/edit/', views.ProfileUpdate.as_view()),
    path('profile/<str:username>/', views.ProfileRetrieve.as_view()),
]