# projectus\urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('view/<int:id>/', views.post_view, name='post_view'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('password-reset/', views.password_reset, name='password_reset'),
    path('password-reset/<str:username>/', views.password_reset_confirm, name='password_reset_confirm'),
]
