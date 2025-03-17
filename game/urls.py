from django.urls import path
from . import views
from .views import monitor_game

urlpatterns = [
    path('', views.index, name='index'),
    path('monitor/', monitor_game, name='monitor_game'),
]
