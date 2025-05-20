from django.urls import path
from . import views

urlpatterns = [
    path('<int:creator_id>/<int:game_id>/create-manage/', views.create_manage, name='create_manage'),
    path('<int:creator_id>/<int:pk>/monitor/', views.monitor, name='monitor'),
    path('<int:creator_id>/<int:game_id>/results/', views.results, name='results'),
    path('calculate-scores/<int:creator_id>/<int:game_id>/', views.calculate_scores, name='calculate_scores'),
]
