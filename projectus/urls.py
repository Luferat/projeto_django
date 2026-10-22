from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('view/<int:id>/', views.post_view, name='post_view'),
]