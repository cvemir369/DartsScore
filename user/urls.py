from django.urls import path

from . import views


urlpatterns = [
    path('players/', views.PlayerListView.as_view(), name='players'),
    path('players/create/', views.PlayerCreateView.as_view(), name='players_create'),
    path('players/update/<int:pk>/', views.PlayerUpdateView.as_view(), name='players_update'),
    path('players/delete/<int:pk>/', views.PlayerDeleteView.as_view(), name='players_delete'),
]
