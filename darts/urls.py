from django.urls import path
from . import views


urlpatterns = [
    path('', views.home_view, name='home'),
    path('create/', views.GameCreateView.as_view(), name='game_create'),
    path('delete/<str:uuid>/', views.GameDeleteView.as_view(), name='game_delete'),
    path('play/<str:uuid>/', views.play_game_view, name='play'),
    path('reset/<str:uuid>/', views.reset_game_view, name='reset'),
]