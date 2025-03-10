from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.get_user, name='get_user'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),

    path('games/', views.get_game, name='get_game'),
    path('games/create/', views.create_game, name='create_game'),
    path('games/<int:pk>/', views.game_detail, name='game_detail'),

    path('waypoints/', views.get_waypoint, name='get_waypoint'),
    path('waypoints/create/', views.create_waypoint, name='create_waypoint'),
    path('waypoints/<int:pk>/', views.waypoint_detail, name='waypoint_detail'),

    path('userlocations/', views.get_user_location, name='get_user_location'),
    path('userlocations/create/', views.create_user_location, name='create_user_location'),
    path('userlocations/<int:pk>/', views.user_location_detail, name='user_location_detail'),

    path('userdistances/', views.get_user_distance, name='get_user_distance'),
    path('userdistances/create/', views.create_user_distance, name='create_user_distance'),
    path('userdistances/<int:pk>/', views.user_distance_detail, name='user_distance_detail'),

    path('userscores/', views.get_user_score, name='get_user_score'),
    path('userscores/create/', views.create_user_score, name='create_user_score'),
    path('userscores/<int:pk>/', views.user_score_detail, name='user_score_detail'),
]
